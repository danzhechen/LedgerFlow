"""Rule application logic for veritas-accounting."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.engine import RuleEvaluator
from veritas_accounting.utils.exceptions import RuleError

# Placeholder account for journal entries with no matching mapping rule.
# Creates a DR and CR pair so the ledger stays complete and the amount is visible for review.
UNMATCHED_ACCOUNT_CODE = "UNMATCHED"
UNMATCHED_ACCOUNT_PATH = "Unmatched (no mapping rule) / 待匹配"
NO_MATCH_RULE_ID = "NO_MATCH"


@dataclass
class RuleApplicationResult:
    """
    Result of applying rules to a journal entry.

    Contains the generated ledger entries and metadata about which rules were applied.
    """

    ledger_entries: list[LedgerEntry]
    applied_rules: list[MappingRule]
    no_match: bool
    entry_id: str


class RuleApplicator:
    """
    Applies mapping rules to journal entries.

    Evaluates rules against journal entries, handles priority, and generates ledger entries.
    """

    def __init__(self, rules: list[MappingRule]) -> None:
        """
        Initialize RuleApplicator with a list of rules.

        Args:
            rules: List of MappingRule objects to apply
        """
        self.rules = rules
        self.evaluator = RuleEvaluator()

        # Pre-compile all rules to catch syntax errors early
        compilation_errors = self.evaluator.compile_rules(rules)
        if compilation_errors:
            error_messages = "\n".join(
                f"  Rule {rule_id}: {error}"
                for rule_id, error in compilation_errors.items()
            )
            raise RuleError(
                f"Rule compilation errors:\n{error_messages}"
            )

        # Sort rules by priority (higher priority first)
        self._sorted_rules = sorted(
            self.rules, key=lambda r: r.priority, reverse=True
        )

    def apply_rules(
        self, entry: JournalEntry, account_hierarchy: Any = None
    ) -> RuleApplicationResult:
        """
        Apply rules to a journal entry (one-to-one mapping).

        For one-to-one mapping, we find the first matching rule set (CR + DR rules with same old_type)
        and create exactly one CR entry and one DR entry.

        Args:
            entry: JournalEntry to apply rules to
            account_hierarchy: AccountHierarchy object (optional, for validation)

        Returns:
            RuleApplicationResult containing:
            - ledger_entries: List of generated LedgerEntry objects (should be 2: one CR, one DR)
            - applied_rules: List of rules that matched and were applied
            - no_match: True if no rules matched
            - entry_id: Journal entry ID
        """
        matching_rules: list[MappingRule] = []

        # Evaluate all rules against the entry
        for rule in self._sorted_rules:
            matches, error = self.evaluator.evaluate(rule, entry)

            if error:
                # Log error but continue with other rules
                # In production, might want to collect these errors
                continue

            if matches:
                matching_rules.append(rule)

        # Handle no-match case: create DR/CR placeholder entries so the ledger is complete
        # and the amount is visible for review (Audit & Review sheet still flags no_match).
        if not matching_rules:
            placeholders = self._create_unmatched_placeholder_entries(entry)
            return RuleApplicationResult(
                ledger_entries=placeholders,
                applied_rules=[],
                no_match=True,
                entry_id=entry.entry_id,
            )

        # For one-to-one mapping: group rules by old_type and find CR/DR pair
        # We want to find the first matching old_type that has both CR and DR rules
        cr_rule = None
        dr_rule = None
        generic_rules = []  # Rules without ledger_type (backward compatibility)
        
        # Group matching rules by old_type (they should all have the same old_type)
        # Find the first set that has both CR and DR
        for rule in matching_rules:
            # Check if rule has ledger_type attribute (from convert_mapping_file)
            ledger_type = getattr(rule, 'ledger_type', None)
            if ledger_type == 'CR' and cr_rule is None:
                cr_rule = rule
            elif ledger_type == 'DR' and dr_rule is None:
                dr_rule = rule
            elif ledger_type is None:
                # Backward compatibility: rules without ledger_type
                generic_rules.append(rule)
            
            # If we found both, we're done (one-to-one mapping)
            if cr_rule and dr_rule:
                break
        
        # If we only found one type, that's okay too (some transactions might only have CR or DR)
        applied_rules = []
        if cr_rule:
            applied_rules.append(cr_rule)
        if dr_rule:
            applied_rules.append(dr_rule)
        
        # Backward compatibility: if no CR/DR rules but we have generic rules, use the first one
        if not applied_rules and generic_rules:
            applied_rules = [generic_rules[0]]  # Use first generic rule
        
        # If no rules to apply, return no match with placeholder entries
        if not applied_rules:
            placeholders = self._create_unmatched_placeholder_entries(entry)
            return RuleApplicationResult(
                ledger_entries=placeholders,
                applied_rules=[],
                no_match=True,
                entry_id=entry.entry_id,
            )

        # Generate ledger entries from matching rules (should be 1-2 entries: CR and/or DR)
        ledger_entries = self._generate_ledger_entries(
            entry, applied_rules, account_hierarchy
        )

        return RuleApplicationResult(
            ledger_entries=ledger_entries,
            applied_rules=applied_rules,
            no_match=False,
            entry_id=entry.entry_id,
        )

    def _create_unmatched_placeholder_entries(self, entry: JournalEntry) -> list[LedgerEntry]:
        """
        Create a DR and CR placeholder pair for an entry with no matching rule.
        Keeps the ledger complete (one debit, one credit per transaction) and makes
        the amount visible for review; no_match remains True for Audit & Review.
        """
        base_amount = abs(Decimal(entry.amount))
        quarter = self._get_quarter(entry.date)
        entry_year = entry.date.year
        dr_entry = LedgerEntry(
            entry_id=f"LE-{entry.entry_id}-{NO_MATCH_RULE_ID}-DR",
            account_code=UNMATCHED_ACCOUNT_CODE,
            account_path=UNMATCHED_ACCOUNT_PATH,
            amount=base_amount,
            date=entry.date,
            description=entry.description,
            source_entry_id=entry.entry_id,
            rule_applied=NO_MATCH_RULE_ID,
            quarter=quarter,
            year=entry_year,
            ledger_type="DR",
        )
        cr_entry = LedgerEntry(
            entry_id=f"LE-{entry.entry_id}-{NO_MATCH_RULE_ID}-CR",
            account_code=UNMATCHED_ACCOUNT_CODE,
            account_path=UNMATCHED_ACCOUNT_PATH,
            amount=base_amount,
            date=entry.date,
            description=entry.description,
            source_entry_id=entry.entry_id,
            rule_applied=NO_MATCH_RULE_ID,
            quarter=quarter,
            year=entry_year,
            ledger_type="CR",
        )
        return [dr_entry, cr_entry]

    def _generate_ledger_entries(
        self,
        entry: JournalEntry,
        rules: list[MappingRule],
        account_hierarchy: Any = None,
    ) -> list[LedgerEntry]:
        """
        Generate ledger entries from matching rules.

        Professional double-entry bookkeeping implementation:
        - Creates ledger entries with positive amounts and separate ledger_type (CR/DR)
        - The SIGN of journal entry amount determines direction:
          * amount >= 0: Use mapping as-is (CR rule → CR, DR rule → DR)
          * amount < 0: Flip sides (CR rule → DR, DR rule → CR) for reversals
        - Both entries use abs(amount) for stored value
        - Net effects calculated downstream as CR_amount - DR_amount
        - Ensures proper double-entry: every transaction has balanced CR/DR sides

        Args:
            entry: JournalEntry source
            rules: List of matching MappingRule objects (should be CR and/or DR rules)
            account_hierarchy: AccountHierarchy for validation (optional)

        Returns:
            List of generated LedgerEntry objects (typically 2: one CR, one DR)
        """
        ledger_entries: list[LedgerEntry] = []

        # Separate CR and DR rules
        cr_rule = None
        dr_rule = None
        generic_rules = []  # Rules without ledger_type (backward compatibility)
        
        for rule in rules:
            ledger_type = getattr(rule, 'ledger_type', None)
            if ledger_type == 'CR':
                cr_rule = rule
            elif ledger_type == 'DR':
                dr_rule = rule
            elif ledger_type is None:
                # Backward compatibility: rules without ledger_type
                generic_rules.append(rule)

        # Determine quarter from entry date
        quarter = self._get_quarter(entry.date)
        
        # Backward compatibility: if no CR/DR rules, use generic rules
        if not cr_rule and not dr_rule and generic_rules:
            # Use first generic rule as a DR entry (default behavior)
            generic_rule = generic_rules[0]
            dr_rule = generic_rule

        # For double-entry bookkeeping:
        # - We store all ledger entry amounts as positive values and use
        #   `ledger_type` to distinguish CR vs DR
        # - The SIGN of the original journal entry amount determines
        #   whether we use the mapping as-is or FLIP CR/DR:
        #     * entry.amount >= 0  → use mapping as-is
        #         - CR rule → credit side
        #         - DR rule → debit side
        #     * entry.amount < 0   → flip sides (reversal)
        #         - CR rule → debit side
        #         - DR rule → credit side
        #   This matches professional accounting workflows where a negative
        #   amount behaves like a reversal of the normal entry.
        #
        # - In all cases we use abs(entry.amount) for the stored amount;
        #   net effects are handled downstream (e.g. in QuarterlyAggregator)
        #   via CR - DR.
        #
        # - 押金 (deposit refund): When we pay other people back 押金 (e.g. OL-d),
        #   账目分类明细 uses opposite sides; we flip CR/DR so the ledger matches.
        from decimal import Decimal
        base_amount = abs(Decimal(entry.amount))
        is_normal_direction = entry.amount >= 0
        ot = (entry.old_type or "").strip()
        is_deposit_refund = "押金" in ot or "ol-d" in ot.lower()

        def _ledger_type_for(role: str) -> str:
            """
            Determine ledger_type ('CR' or 'DR') for a rule role,
            respecting the sign of the journal amount and 押金 flip.
            """
            if is_normal_direction:
                base = role
            else:
                base = "DR" if role == "CR" else "CR"
            # 押金: 账目分类明细 rules are written with opposite sides; flip once.
            if is_deposit_refund:
                base = "DR" if base == "CR" else "CR"
            return base
        
        # Create CR-side entry if CR rule exists
        if cr_rule:
            # Validate account code exists in hierarchy (if provided)
            if account_hierarchy:
                # Try lookup by code first, then by name (mapping rules might use names)
                account = account_hierarchy.get_account(cr_rule.account_code)
                if not account:
                    account = account_hierarchy.get_account_by_name(cr_rule.account_code)
                
                if account is None:
                    # Skip if account doesn't exist (but this shouldn't happen if validation passed)
                    pass
                else:
                    account_path = account.full_path
                    
                    cr_ledger_type = _ledger_type_for("CR")
                    entry_year = entry.date.year
                    cr_entry = LedgerEntry(
                        entry_id=f"LE-{entry.entry_id}-{cr_rule.rule_id}",
                        account_code=cr_rule.account_code,
                        account_path=account_path,
                        amount=base_amount,
                        date=entry.date,
                        description=entry.description,
                        source_entry_id=entry.entry_id,
                        rule_applied=cr_rule.rule_id,
                        quarter=quarter,
                        year=entry_year,
                        ledger_type=cr_ledger_type,
                    )
                    ledger_entries.append(cr_entry)
            else:
                # If no hierarchy provided, use account_code as path
                entry_year = entry.date.year
                cr_ledger_type = _ledger_type_for("CR")
                cr_entry = LedgerEntry(
                    entry_id=f"LE-{entry.entry_id}-{cr_rule.rule_id}",
                    account_code=cr_rule.account_code,
                    account_path=cr_rule.account_code,
                    amount=base_amount,
                    date=entry.date,
                    description=entry.description,
                    source_entry_id=entry.entry_id,
                    rule_applied=cr_rule.rule_id,
                    quarter=quarter,
                    year=entry_year,
                    ledger_type=cr_ledger_type,
                )
                ledger_entries.append(cr_entry)

        # Create DR-side entry if DR rule exists
        if dr_rule:
            # Validate account code exists in hierarchy (if provided)
            if account_hierarchy:
                # Try lookup by code first, then by name (mapping rules might use names)
                account = account_hierarchy.get_account(dr_rule.account_code)
                if not account:
                    account = account_hierarchy.get_account_by_name(dr_rule.account_code)
                
                if account is None:
                    # Skip if account doesn't exist (but this shouldn't happen if validation passed)
                    pass
                else:
                    account_path = account.full_path
                    
                    dr_ledger_type = _ledger_type_for("DR")
                    entry_year = entry.date.year
                    dr_entry = LedgerEntry(
                        entry_id=f"LE-{entry.entry_id}-{dr_rule.rule_id}",
                        account_code=dr_rule.account_code,
                        account_path=account_path,
                        amount=base_amount,
                        date=entry.date,
                        description=entry.description,
                        source_entry_id=entry.entry_id,
                        rule_applied=dr_rule.rule_id,
                        quarter=quarter,
                        year=entry_year,
                        ledger_type=dr_ledger_type,
                    )
                    ledger_entries.append(dr_entry)
            else:
                # If no hierarchy provided, use account_code as path
                entry_year = entry.date.year
                dr_ledger_type = _ledger_type_for("DR")
                dr_entry = LedgerEntry(
                    entry_id=f"LE-{entry.entry_id}-{dr_rule.rule_id}",
                    account_code=dr_rule.account_code,
                    account_path=dr_rule.account_code,
                    amount=base_amount,
                    date=entry.date,
                    description=entry.description,
                    source_entry_id=entry.entry_id,
                    rule_applied=dr_rule.rule_id,
                    quarter=quarter,
                    year=entry_year,
                    ledger_type=dr_ledger_type,
                )
                ledger_entries.append(dr_entry)

        return ledger_entries

    def _get_quarter(self, date: Any) -> int:
        """
        Get quarter (1-4) from a date.

        Args:
            date: datetime object

        Returns:
            Quarter number (1-4)
        """
        from datetime import datetime

        if isinstance(date, datetime):
            month = date.month
        else:
            # Try to extract month from other date types
            month = getattr(date, "month", 1)

        if month in (1, 2, 3):
            return 1
        elif month in (4, 5, 6):
            return 2
        elif month in (7, 8, 9):
            return 3
        else:
            return 4

    def apply_rules_batch(
        self, entries: list[JournalEntry], account_hierarchy: Any = None
    ) -> list[RuleApplicationResult]:
        """
        Apply rules to a batch of journal entries.

        Args:
            entries: List of JournalEntry objects
            account_hierarchy: AccountHierarchy object (optional)

        Returns:
            List of RuleApplicationResult objects, one per entry
        """
        results: list[RuleApplicationResult] = []

        for entry in entries:
            result = self.apply_rules(entry, account_hierarchy)
            results.append(result)

        return results






