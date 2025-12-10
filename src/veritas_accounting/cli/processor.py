"""Processing pipeline for veritas-accounting CLI."""

from pathlib import Path
from typing import Optional

import click

from veritas_accounting.audit.trail import AuditTrail
from veritas_accounting.config.settings import AppConfig
from veritas_accounting.excel.journal_reader import JournalEntryReader
from veritas_accounting.excel.rule_reader import MappingRuleReader
from veritas_accounting.models.account_loader import AccountHierarchyLoader
from veritas_accounting.reporting.error_report import ErrorReportGenerator
from veritas_accounting.reporting.ledger_output import LedgerOutputGenerator
from veritas_accounting.reporting.quarterly_report import QuarterlyReportGenerator
from veritas_accounting.rules.applicator import RuleApplicator
from veritas_accounting.transformation.aggregator import QuarterlyAggregator
from veritas_accounting.transformation.journal_to_ledger import JournalToLedgerTransformer
from veritas_accounting.validation.error_detector import ErrorDetector
from veritas_accounting.validation.input_validator import JournalEntryValidator
from veritas_accounting.validation.pipeline import InputValidationPipeline
from veritas_accounting.validation.validation_results import ValidationResultsViewer
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
            if journal_errors:
                results["errors"].extend(journal_errors)
                return results

            click.echo(f"   ✓ Read {len(journal_entries)} journal entries")

            # Step 2: Read mapping rules
            click.echo("📋 Reading mapping rules...")
            rules, rule_errors = self._read_mapping_rules()
            if rule_errors:
                results["errors"].extend(rule_errors)
                return results

            click.echo(f"   ✓ Loaded {len(rules)} mapping rules")

            # Step 3: Read account hierarchy (optional)
            account_hierarchy = None
            if self.config.input.account_hierarchy_file:
                click.echo("📊 Reading account hierarchy...")
                account_hierarchy = self._read_account_hierarchy()
                click.echo(f"   ✓ Loaded account hierarchy")

            # Step 4: Validate input
            click.echo("✅ Validating input data...")
            validation_pipeline = InputValidationPipeline(account_hierarchy)
            validation_result = validation_pipeline.validate_inputs(journal_entries, rules)
            
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
            
            transformer = JournalToLedgerTransformer(rules, account_hierarchy)
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

            # Step 6: Generate reports
            click.echo("📊 Generating reports...")
            output_dir = Path(self.config.output.directory)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate ledger output
            ledger_path = output_dir / self.config.output.ledger_file
            ledger_generator = LedgerOutputGenerator(account_hierarchy)
            ledger_generator.generate(ledger_entries, ledger_path)
            results["output_files"].append(str(ledger_path))
            click.echo(f"   ✓ Generated ledger output: {ledger_path}")

            # Generate quarterly report
            quarterly_path = output_dir / self.config.output.quarterly_report_file
            quarterly_generator = QuarterlyReportGenerator(account_hierarchy)
            quarterly_generator.generate(ledger_entries, quarterly_path)
            results["output_files"].append(str(quarterly_path))
            click.echo(f"   ✓ Generated quarterly report: {quarterly_path}")

            # Generate error report
            validation_viewer = ValidationResultsViewer()
            validation_summary = validation_viewer.generate_summary(
                error_detector,
                len(journal_entries),
                len(journal_entries) - len(validation_result.errors),
            )

            error_report_path = output_dir / self.config.output.error_report_file
            error_report_generator = ErrorReportGenerator()
            error_report_generator.generate_report(
                error_report_path,
                error_detector,
                audit_trail=self.audit_trail,
                validation_summary=validation_summary,
                original_entries=journal_entries,
            )
            results["output_files"].append(str(error_report_path))
            click.echo(f"   ✓ Generated error report: {error_report_path}")

            # Export audit trail
            from veritas_accounting.audit.exporter import AuditTrailExporter
            audit_trail_path = output_dir / self.config.output.audit_trail_file
            exporter = AuditTrailExporter(self.audit_trail)
            exporter.export_to_excel(audit_trail_path)
            results["output_files"].append(str(audit_trail_path))
            click.echo(f"   ✓ Exported audit trail: {audit_trail_path}")

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

    def _read_journal_entries(self) -> tuple[list, list[str]]:
        """
        Read journal entries from Excel file.

        Returns:
            Tuple of (journal_entries, errors)
        """
        try:
            reader = JournalEntryReader()
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

        try:
            reader = MappingRuleReader()
            rules, errors = reader.read_rules(rules_file)
            error_messages = [str(e) for e in errors]
            return rules, error_messages
        except Exception as e:
            return [], [f"Failed to read mapping rules: {e}"]

    def _read_account_hierarchy(self):
        """
        Read account hierarchy from Excel file.

        Returns:
            AccountHierarchy object or None
        """
        if not self.config.input.account_hierarchy_file:
            return None

        try:
            loader = AccountHierarchyLoader()
            return loader.load_from_excel(self.config.input.account_hierarchy_file)
        except Exception as e:
            click.echo(f"   ⚠️  Warning: Failed to load account hierarchy: {e}")
            return None
