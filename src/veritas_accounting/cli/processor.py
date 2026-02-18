"""Processing pipeline for veritas-accounting CLI."""

from pathlib import Path
from typing import Optional

import click
import pandas as pd

from veritas_accounting.audit.trail import AuditTrail
from veritas_accounting.config.settings import AppConfig
from veritas_accounting.excel.journal_reader import JournalEntryReader
from veritas_accounting.excel.rule_reader import MappingRuleReader
from veritas_accounting.models.account_loader import AccountHierarchyLoader
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.reporting.unified_report import UnifiedReportGenerator
from veritas_accounting.rules.applicator import RuleApplicator
from veritas_accounting.transformation.aggregator import QuarterlyAggregator
from veritas_accounting.transformation.journal_to_ledger import JournalToLedgerTransformer
from veritas_accounting.validation.error_detector import ErrorDetector
from veritas_accounting.validation.input_validator import JournalEntryValidator
from veritas_accounting.validation.pipeline import InputValidationPipeline
from veritas_accounting.utils.exceptions import ExcelIOError, TransformationError


class ProcessingPipeline:
    """
    Complete processing pipeline for accounting automation.

    Orchestrates the full workflow: input → validation → transformation → output.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize processing pipeline.

        Args:
            config: Application configuration
        """
        self.config = config
        self._rules_from_journal_to_ledger = False
        self.audit_trail = AuditTrail(
            user=config.processing.model_dump().get("user"),
            system_version="0.1.0",
            rule_version=None,  # Can be set from rules file metadata
        )

    def process(self) -> dict[str, any]:
        """
        Execute the complete processing pipeline.

        Returns:
            Dictionary with processing results and statistics

        Raises:
            ExcelIOError: If file I/O fails
            TransformationError: If transformation fails
        """
        results = {
            "success": False,
            "errors": [],
            "warnings": [],
            "output_files": [],
        }

        try:
            # Step 1: Read input files
            click.echo("📖 Reading journal entries...")
            journal_entries, journal_errors = self._read_journal_entries()
            if journal_errors and len(journal_entries) == 0:
                # Only fail if we have errors AND no valid entries at all
                results["errors"].extend(journal_errors)
                return results
            elif journal_errors:
                # Log warnings for row-level errors but continue with valid entries
                results["warnings"].extend(journal_errors[:10])  # Show first 10 warnings
                if len(journal_errors) > 10:
                    click.echo(f"   ⚠️  {len(journal_errors)} rows had errors (showing first 10)")

            click.echo(f"   ✓ Read {len(journal_entries)} journal entries")

            # Step 2: Read mapping rules (before type mapping so we know if rules are from journal_to_ledger)
            click.echo("📋 Reading mapping rules...")
            rules, rule_errors = self._read_mapping_rules()
            if rule_errors:
                results["warnings"].extend(rule_errors)
            click.echo(f"   ✓ Loaded {len(rules)} mapping rules")

            # When rules are from journal_to_ledger we match on raw type + 摘要, so skip type mapping.
            # Otherwise apply OLD→NEW type mapping from 账目分类明细.xlsx "journal" sheet.
            if not getattr(self, "_rules_from_journal_to_ledger", False):
                type_mapping = self._load_type_mapping()
                if type_mapping:
                    journal_entries = self._apply_type_mapping(journal_entries, type_mapping)
                    click.echo(f"   ✓ Applied type mapping from account hierarchy file ({len(type_mapping)} mappings)")

            # Step 3: Read account hierarchy (optional)
            account_hierarchy = None
            if self.config.input.account_hierarchy_file:
                click.echo("📊 Reading account hierarchy...")
                account_hierarchy = self._read_account_hierarchy()
                if account_hierarchy:
                    account_count = len(account_hierarchy.get_all_accounts())
                    click.echo(f"   ✓ Loaded account hierarchy ({account_count} accounts)")
                    # Debug: Show sample accounts
                    sample_accounts = account_hierarchy.get_all_accounts()[:3]
                    for acc in sample_accounts:
                        click.echo(f"      Sample: Code={acc.code}, Name={acc.name}")
                else:
                    click.echo(f"   ⚠️  Warning: Account hierarchy is None (may have failed to load)")

            # Step 4: Validate input
            click.echo("✅ Validating input data...")
            validation_pipeline = InputValidationPipeline(account_hierarchy)
            validation_result = validation_pipeline.validate_inputs(journal_entries, rules)
            
            # Use validated rules (rules that passed validation)
            # Note: Account code validation errors are non-blocking, so most rules should pass
            validated_rules = validation_result.valid_mapping_rules if hasattr(validation_result, 'valid_mapping_rules') else rules
            if len(validated_rules) != len(rules):
                click.echo(f"   ⚠️  {len(rules) - len(validated_rules)} rules filtered out during validation (using {len(validated_rules)} rules)")
            else:
                click.echo(f"   ✓ Using {len(validated_rules)} validated rules")
            
            error_detector = ErrorDetector()
            error_detector.add_validation_result(
                validation_result.errors,
                validation_result.warnings,
                error_category="data_error",
            )

            if validation_result.errors:
                click.echo(f"   ⚠️  Found {len(validation_result.errors)} validation errors")
                # Show first few errors
                from veritas_accounting.cli.error_formatter import CLIErrorFormatter
                formatter = CLIErrorFormatter()
                error_list = error_detector.get_all_errors()[:5]  # Show first 5
                if error_list:
                    click.echo(formatter.format_error_list(error_list, max_display=5))
            else:
                click.echo("   ✓ Input validation passed")

            # Step 5: Transform journal entries to ledger entries
            click.echo("🔄 Applying mapping rules and transforming entries...")
            self.audit_trail.start()
            
            # Use validated rules (rules that passed non-blocking validation)
            transformer = JournalToLedgerTransformer(validated_rules, account_hierarchy)
            ledger_entries, unmatched_entries = transformer.transform(journal_entries)

            # Record transformations in audit trail
            results_batch = transformer.applicator.apply_rules_batch(
                journal_entries, account_hierarchy
            )
            self.audit_trail.record_batch_transformation(journal_entries, results_batch)
            self.audit_trail.end()

            click.echo(f"   ✓ Generated {len(ledger_entries)} ledger entries")
            if unmatched_entries:
                click.echo(f"   ⚠️  {len(unmatched_entries)} entries had no matching rules")

            # Step 6: Generate unified report (single workbook: Ledger, Account Summary, Quarterly Report, Audit & Review)
            click.echo("📊 Generating report...")
            output_dir = Path(self.config.output.directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            report_path = output_dir / self.config.output.ledger_file
            unified_generator = UnifiedReportGenerator(account_hierarchy)
            unified_generator.generate(
                ledger_entries=ledger_entries,
                journal_entries=journal_entries,
                audit_trail=self.audit_trail,
                error_detector=error_detector,
                output_path=report_path,
            )
            results["output_files"].append(str(report_path))
            click.echo(f"   ✓ Generated report: {report_path}")

            results["success"] = True
            results["statistics"] = {
                "journal_entries": len(journal_entries),
                "ledger_entries": len(ledger_entries),
                "rules_applied": len(rules),
                "unmatched_entries": len(unmatched_entries),
                "validation_errors": len(validation_result.errors),
                "validation_warnings": len(validation_result.warnings),
            }

            click.echo("\n✅ Processing complete!")
            click.echo(f"📁 Output files saved to: {output_dir.absolute()}")

            return results

        except Exception as e:
            results["errors"].append(str(e))
            click.echo(f"\n❌ Error during processing: {e}", err=True)
            return results

    # Removed process_dual_ledger method - dual ledger support removed
    # All entries now use new ledger rules only

    def _read_journal_entries(self) -> tuple[list, list[str]]:
        """
        Read journal entries from Excel file.

        Returns:
            Tuple of (journal_entries, errors)
        """
        try:
            # Check if sheet_name is specified in config (for multi-sheet processing)
            sheet_name = getattr(self.config, 'sheet_name', None)
            reader = JournalEntryReader(sheet_name=sheet_name)
            entries, errors = reader.read_journal_entries(self.config.input.journal_file)
            error_messages = [str(e) for e in errors]
            return entries, error_messages
        except Exception as e:
            return [], [f"Failed to read journal entries: {e}"]

    def _read_mapping_rules(self) -> tuple[list, list[str]]:
        """
        Read mapping rules from Excel file.

        Returns:
            Tuple of (rules, errors)
        """
        rules_file = self.config.input.rules_file
        if not rules_file:
            return [], ["No rules file specified in configuration"]

        return self._read_mapping_rules_from_file(rules_file)

    def _read_mapping_rules_from_file(self, rules_file: str) -> tuple[list, list[str]]:
        """
        Read mapping rules from a specific Excel file.

        When the file is 账目分类明细.xlsx (or same as account_hierarchy_file), loads from
        sheet "journal_to_ledger" so 账目分类明细 is the single source of truth. Otherwise
        uses the standard rules sheet (e.g. 账目分类明细_ledger_rules.xlsx).

        Returns:
            Tuple of (rules, errors). Sets self._rules_from_journal_to_ledger if loaded from that sheet.
        """
        try:
            reader = MappingRuleReader()
            path = Path(rules_file)
            hierarchy_file = (self.config.input.account_hierarchy_file or "").strip()
            use_jtl = path.exists() and hierarchy_file and Path(hierarchy_file).resolve() == path.resolve()
            if use_jtl:
                try:
                    rules, errors = reader.read_rules_from_journal_to_ledger(rules_file)
                    if rules:
                        self._rules_from_journal_to_ledger = True
                        error_messages = [str(e) for e in errors]
                        return rules, error_messages
                except Exception:
                    pass
            self._rules_from_journal_to_ledger = False
            rules, errors = reader.read_rules(rules_file)
            error_messages = [str(e) for e in errors]
            return rules, error_messages
        except Exception as e:
            return [], [f"Failed to read mapping rules from {rules_file}: {e}"]

    def _read_account_hierarchy(self):
        """
        Read account hierarchy from Excel file.
        
        Tries to load from 'ledger_new' sheet first (which contains 4-digit ledger IDs),
        falls back to first sheet if 'ledger_new' doesn't exist.

        Returns:
            AccountHierarchy object or None
        """
        if not self.config.input.account_hierarchy_file:
            return None

        try:
            loader = AccountHierarchyLoader()
            # Try to load from 'ledger_new' sheet first (contains 4-digit ledger IDs)
            try:
                hierarchy = loader.load_from_excel(self.config.input.account_hierarchy_file, sheet_name="ledger_new")
                # Verify it loaded successfully
                if hierarchy and len(hierarchy.get_all_accounts()) > 0:
                    return hierarchy
                else:
                    click.echo(f"   ⚠️  Warning: ledger_new sheet loaded but has no accounts, trying first sheet...")
            except Exception as e1:
                # Log the specific error for ledger_new
                click.echo(f"   ⚠️  Warning: Failed to load from 'ledger_new' sheet: {e1}")
                # Fall back to first sheet if 'ledger_new' doesn't exist or fails
                try:
                    return loader.load_from_excel(self.config.input.account_hierarchy_file)
                except Exception as e2:
                    click.echo(f"   ⚠️  Warning: Failed to load from first sheet: {e2}")
                    raise e2
        except Exception as e:
            click.echo(f"   ⚠️  Warning: Failed to load account hierarchy: {e}")
            return None

    def _load_type_mapping(self) -> Optional[dict[tuple[int, str], str]]:
        """
        Load (year, old_type) -> new_type from account hierarchy Excel if it has a "journal" sheet
        (e.g. 账目分类明细.xlsx). This maps raw journal Type values to rule old_type values.
        Returns None if file missing or sheet not present.
        """
        path = self.config.input.account_hierarchy_file
        if not path or not Path(path).exists():
            return None
        try:
            xl = pd.ExcelFile(path)
            if "journal" not in xl.sheet_names:
                return None
            df = pd.read_excel(path, sheet_name="journal")
            # Columns: OLD (year), Unnamed 1 (摘要), Unnamed 2 (old type), NEW (new type)
            year_col = "OLD"
            old_type_col = None
            new_type_col = "NEW"
            for c in df.columns:
                if str(c).strip() in ("Unnamed: 2", "type", "类型"):
                    old_type_col = c
                    break
            if old_type_col is None and len(df.columns) >= 3:
                old_type_col = df.columns[2]
            if year_col not in df.columns or new_type_col not in df.columns or old_type_col is None:
                return None
            mapping: dict[tuple[int, str], str] = {}
            for _, row in df.iterrows():
                try:
                    y = row.get(year_col)
                    if pd.isna(y):
                        continue
                    year_val = int(float(y)) if isinstance(y, (int, float)) else int(y)
                    if year_val < 2000 or year_val > 2100:
                        continue
                    old_t = row.get(old_type_col)
                    new_t = row.get(new_type_col)
                    if pd.isna(old_t) or pd.isna(new_t):
                        continue
                    old_str = str(old_t).strip()
                    new_str = str(new_t).strip()
                    if not old_str:
                        continue
                    mapping[(year_val, old_str)] = new_str
                except (ValueError, TypeError):
                    continue
            return mapping if mapping else None
        except Exception:
            return None

    def _apply_type_mapping(
        self,
        journal_entries: list[JournalEntry],
        type_mapping: dict[tuple[int, str], str],
    ) -> list[JournalEntry]:
        """
        Replace each entry's old_type with mapped value.
        If (year, old_type) is not in the map, try (year-1, old_type) down to 2020
        so e.g. 2024 entries can use 2022/2023 mappings when the journal sheet has no 2024 rows.
        """
        result: list[JournalEntry] = []
        for entry in journal_entries:
            raw = entry.old_type.strip()
            key = (entry.year, raw)
            new_type = type_mapping.get(key)
            if new_type is None:
                for y in range(entry.year - 1, 2019, -1):
                    new_type = type_mapping.get((y, raw))
                    if new_type is not None:
                        break
            if new_type is None:
                new_type = entry.old_type
            if new_type != entry.old_type:
                result.append(entry.model_copy(update={"old_type": new_type}))
            else:
                result.append(entry)
        return result






