"""Audit trail tracking for veritas-accounting."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.applicator import RuleApplicationResult


@dataclass
class AppliedRule:
    """Record of a rule that was applied during transformation."""

    rule_id: str
    condition: str
    account_code: str
    description: Optional[str] = None
    priority: int = 0
    generates_multiple: bool = False


@dataclass
class TransformationRecord:
    """
    Complete record of a single transformation.

    Tracks a journal entry transformation with all applied rules and generated ledger entries.
    """

    entry_id: str
    timestamp: datetime
    source_entry: JournalEntry
    applied_rules: list[AppliedRule] = field(default_factory=list)
    generated_entries: list[LedgerEntry] = field(default_factory=list)
    no_match: bool = False
    user: Optional[str] = None
    system_version: Optional[str] = None
    rule_version: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert transformation record to dictionary for export.

        Returns:
            Dictionary representation of the transformation record
        """
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "source_entry": self.source_entry.model_dump(),
            "applied_rules": [
                {
                    "rule_id": rule.rule_id,
                    "condition": rule.condition,
                    "account_code": rule.account_code,
                    "description": rule.description,
                    "priority": rule.priority,
                    "generates_multiple": rule.generates_multiple,
                }
                for rule in self.applied_rules
            ],
            "generated_entries": [entry.model_dump() for entry in self.generated_entries],
            "no_match": self.no_match,
            "user": self.user,
            "system_version": self.system_version,
            "rule_version": self.rule_version,
        }


class AuditTrail:
    """
    Audit trail tracker for all transformations.

    Tracks complete transformation history with source entries, applied rules,
    generated entries, and metadata for full traceability.
    """

    def __init__(
        self,
        user: Optional[str] = None,
        system_version: Optional[str] = None,
        rule_version: Optional[str] = None,
    ) -> None:
        """
        Initialize AuditTrail.

        Args:
            user: User who ran the transformation (optional)
            system_version: Version of the system (optional)
            rule_version: Version of the rules file (optional)
        """
        self.user = user
        self.system_version = system_version
        self.rule_version = rule_version
        self.records: list[TransformationRecord] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

    def start(self) -> None:
        """Mark the start of transformation processing."""
        self._start_time = datetime.now()

    def end(self) -> None:
        """Mark the end of transformation processing."""
        self._end_time = datetime.now()

    def record_transformation(
        self,
        source_entry: JournalEntry,
        result: RuleApplicationResult,
    ) -> TransformationRecord:
        """
        Record a single transformation.

        Args:
            source_entry: Source journal entry
            result: Rule application result with applied rules and generated entries

        Returns:
            TransformationRecord that was created
        """
        # Convert applied rules to AppliedRule objects
        applied_rules = [
            AppliedRule(
                rule_id=rule.rule_id,
                condition=rule.condition,
                account_code=rule.account_code,
                description=rule.description,
                priority=rule.priority,
                generates_multiple=rule.generates_multiple,
            )
            for rule in result.applied_rules
        ]

        # Create transformation record
        record = TransformationRecord(
            entry_id=source_entry.entry_id,
            timestamp=datetime.now(),
            source_entry=source_entry,
            applied_rules=applied_rules,
            generated_entries=result.ledger_entries,
            no_match=result.no_match,
            user=self.user,
            system_version=self.system_version,
            rule_version=self.rule_version,
        )

        self.records.append(record)
        return record

    def record_batch_transformation(
        self,
        source_entries: list[JournalEntry],
        results: list[RuleApplicationResult],
    ) -> list[TransformationRecord]:
        """
        Record a batch of transformations.

        Args:
            source_entries: List of source journal entries
            results: List of rule application results (one per entry)

        Returns:
            List of TransformationRecord objects created

        Raises:
            ValueError: If source_entries and results have different lengths
        """
        if len(source_entries) != len(results):
            raise ValueError(
                f"Source entries ({len(source_entries)}) and results "
                f"({len(results)}) must have the same length"
            )

        records: list[TransformationRecord] = []
        for entry, result in zip(source_entries, results, strict=True):
            record = self.record_transformation(entry, result)
            records.append(record)

        return records

    def get_record_by_entry_id(self, entry_id: str) -> Optional[TransformationRecord]:
        """
        Get transformation record for a specific entry ID.

        Args:
            entry_id: Journal entry ID to look up

        Returns:
            TransformationRecord if found, None otherwise
        """
        for record in self.records:
            if record.entry_id == entry_id:
                return record
        return None

    def get_records_by_rule_id(self, rule_id: str) -> list[TransformationRecord]:
        """
        Get all transformation records that used a specific rule.

        Args:
            rule_id: Rule ID to look up

        Returns:
            List of TransformationRecord objects that used this rule
        """
        matching_records: list[TransformationRecord] = []
        for record in self.records:
            if any(rule.rule_id == rule_id for rule in record.applied_rules):
                matching_records.append(record)
        return matching_records

    def get_all_ledger_entries(self) -> list[LedgerEntry]:
        """
        Get all ledger entries generated across all transformations.

        Returns:
            List of all LedgerEntry objects
        """
        all_entries: list[LedgerEntry] = []
        for record in self.records:
            all_entries.extend(record.generated_entries)
        return all_entries

    def get_unmatched_entries(self) -> list[JournalEntry]:
        """
        Get all journal entries that had no matching rules.

        Returns:
            List of JournalEntry objects that had no_match=True
        """
        unmatched: list[JournalEntry] = []
        for record in self.records:
            if record.no_match:
                unmatched.append(record.source_entry)
        return unmatched

    def get_summary(self) -> dict[str, Any]:
        """
        Get summary statistics of the audit trail.

        Returns:
            Dictionary with summary statistics
        """
        total_transformations = len(self.records)
        total_ledger_entries = sum(len(r.generated_entries) for r in self.records)
        unmatched_count = sum(1 for r in self.records if r.no_match)
        matched_count = total_transformations - unmatched_count

        # Count unique rules applied
        unique_rules = set()
        for record in self.records:
            for rule in record.applied_rules:
                unique_rules.add(rule.rule_id)

        return {
            "total_transformations": total_transformations,
            "matched_entries": matched_count,
            "unmatched_entries": unmatched_count,
            "total_ledger_entries": total_ledger_entries,
            "unique_rules_applied": len(unique_rules),
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "duration_seconds": (
                (self._end_time - self._start_time).total_seconds()
                if self._start_time and self._end_time
                else None
            ),
            "user": self.user,
            "system_version": self.system_version,
            "rule_version": self.rule_version,
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert entire audit trail to dictionary for export.

        Returns:
            Dictionary representation of the audit trail
        """
        return {
            "metadata": {
                "user": self.user,
                "system_version": self.system_version,
                "rule_version": self.rule_version,
                "start_time": self._start_time.isoformat() if self._start_time else None,
                "end_time": self._end_time.isoformat() if self._end_time else None,
            },
            "summary": self.get_summary(),
            "transformations": [record.to_dict() for record in self.records],
        }

    def clear(self) -> None:
        """Clear all records from the audit trail."""
        self.records.clear()
        self._start_time = None
        self._end_time = None
