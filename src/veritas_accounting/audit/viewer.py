"""Transformation visibility viewer for veritas-accounting."""

from typing import Any

from veritas_accounting.audit.trail import AuditTrail, TransformationRecord
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule


class TransformationViewer:
    """
    Provides visibility into transformations.

    Displays transformations in multiple views: entry-by-entry, rule-by-rule,
    and summary views for easy review and verification.
    """

    def __init__(self, audit_trail: AuditTrail) -> None:
        """
        Initialize TransformationViewer.

        Args:
            audit_trail: AuditTrail with transformation records
        """
        self.audit_trail = audit_trail

    def view_by_entry(self, entry_id: str) -> dict[str, Any] | None:
        """
        View transformation for a specific journal entry.

        Args:
            entry_id: Journal entry ID to view

        Returns:
            Dictionary with transformation details, or None if not found
        """
        record = self.audit_trail.get_record_by_entry_id(entry_id)
        if not record:
            return None

        return {
            "entry_id": record.entry_id,
            "timestamp": record.timestamp.isoformat(),
            "source_entry": record.source_entry.model_dump(),
            "applied_rules": [
                {
                    "rule_id": rule.rule_id,
                    "condition": rule.condition,
                    "account_code": rule.account_code,
                    "description": rule.description,
                }
                for rule in record.applied_rules
            ],
            "generated_ledger_entries": [
                entry.model_dump() for entry in record.generated_entries
            ],
            "no_match": record.no_match,
            "transformation_path": self._build_transformation_path(record),
        }

    def view_by_rule(self, rule_id: str) -> dict[str, Any]:
        """
        View all transformations that used a specific rule.

        Args:
            rule_id: Rule ID to view

        Returns:
            Dictionary with rule usage details
        """
        records = self.audit_trail.get_records_by_rule_id(rule_id)

        # Collect all journal entries and ledger entries for this rule
        journal_entries = [record.source_entry for record in records]
        ledger_entries: list[LedgerEntry] = []
        for record in records:
            for entry in record.generated_entries:
                if entry.rule_applied == rule_id:
                    ledger_entries.append(entry)

        return {
            "rule_id": rule_id,
            "usage_count": len(records),
            "journal_entries": [entry.model_dump() for entry in journal_entries],
            "generated_ledger_entries": [entry.model_dump() for entry in ledger_entries],
            "total_amount": sum(float(entry.amount) for entry in ledger_entries),
        }

    def view_summary(self) -> dict[str, Any]:
        """
        View summary of all transformations.

        Returns:
            Dictionary with summary statistics and overview
        """
        summary = self.audit_trail.get_summary()

        # Additional statistics
        all_ledger_entries = self.audit_trail.get_all_ledger_entries()
        total_amount = sum(float(entry.amount) for entry in all_ledger_entries)

        # Rule usage statistics
        rule_usage: dict[str, int] = {}
        for record in self.audit_trail.records:
            for rule in record.applied_rules:
                rule_usage[rule.rule_id] = rule_usage.get(rule.rule_id, 0) + 1

        return {
            **summary,
            "total_amount": total_amount,
            "rule_usage": rule_usage,
            "average_ledger_entries_per_journal": (
                summary["total_ledger_entries"] / summary["total_transformations"]
                if summary["total_transformations"] > 0
                else 0
            ),
        }

    def get_comparison_view(self, entry_id: str) -> dict[str, Any] | None:
        """
        Get before/after comparison view for a transformation.

        Args:
            entry_id: Journal entry ID to compare

        Returns:
            Dictionary with original and transformed data side-by-side, or None if not found
        """
        record = self.audit_trail.get_record_by_entry_id(entry_id)
        if not record:
            return None

        return {
            "entry_id": entry_id,
            "original": {
                "entry_id": record.source_entry.entry_id,
                "year": record.source_entry.year,
                "description": record.source_entry.description,
                "old_type": record.source_entry.old_type,
                "amount": float(record.source_entry.amount),
                "date": record.source_entry.date.isoformat(),
                "quarter": record.source_entry.quarter,
                "notes": record.source_entry.notes,
            },
            "transformed": {
                "ledger_entries": [
                    {
                        "entry_id": entry.entry_id,
                        "account_code": entry.account_code,
                        "account_path": entry.account_path,
                        "amount": float(entry.amount),
                        "date": entry.date.isoformat(),
                        "description": entry.description,
                        "rule_applied": entry.rule_applied,
                        "quarter": entry.quarter,
                        "year": entry.year,
                    }
                    for entry in record.generated_entries
                ],
                "rules_applied": [
                    {
                        "rule_id": rule.rule_id,
                        "condition": rule.condition,
                        "account_code": rule.account_code,
                    }
                    for rule in record.applied_rules
                ],
            },
            "no_match": record.no_match,
        }

    def export_transformation_log(self) -> list[dict[str, Any]]:
        """
        Export transformation log for external review.

        Returns:
            List of dictionaries with all transformation details
        """
        return [record.to_dict() for record in self.audit_trail.records]

    def _build_transformation_path(self, record: TransformationRecord) -> str:
        """
        Build human-readable transformation path.

        Args:
            record: TransformationRecord to build path for

        Returns:
            String describing the transformation path
        """
        if record.no_match:
            return f"Journal Entry {record.entry_id} → No matching rules → No transformation"

        path_parts = [f"Journal Entry {record.entry_id}"]
        for rule in record.applied_rules:
            path_parts.append(f"→ Rule {rule.rule_id} ({rule.account_code})")
        path_parts.append(f"→ {len(record.generated_entries)} Ledger Entry(ies)")

        return " ".join(path_parts)

    def format_entry_view_console(self, entry_id: str) -> str:
        """
        Format entry view for console output.

        Args:
            entry_id: Journal entry ID to format

        Returns:
            Formatted string for console display
        """
        view = self.view_by_entry(entry_id)
        if not view:
            return f"No transformation found for entry ID: {entry_id}"

        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"Transformation for Entry: {entry_id}")
        lines.append(f"{'='*60}")

        # Source entry
        source = view["source_entry"]
        lines.append("\n📥 Source Journal Entry:")
        lines.append(f"  Description: {source['description']}")
        lines.append(f"  Type: {source['old_type']}")
        lines.append(f"  Amount: {source['amount']}")
        lines.append(f"  Date: {source['date']}")

        # Applied rules
        if view["applied_rules"]:
            lines.append("\n🔧 Applied Rules:")
            for rule in view["applied_rules"]:
                lines.append(f"  • Rule {rule['rule_id']}: {rule['condition']}")
                if rule.get("description"):
                    lines.append(f"    → {rule['description']}")
        else:
            lines.append("\n⚠️  No matching rules found")

        # Generated entries
        if view["generated_ledger_entries"]:
            lines.append("\n📤 Generated Ledger Entries:")
            for entry in view["generated_ledger_entries"]:
                lines.append(f"  • {entry['entry_id']}: {entry['account_code']} ({entry['account_path']})")
                lines.append(f"    Amount: {entry['amount']}, Rule: {entry['rule_applied']}")
        else:
            lines.append("\n⚠️  No ledger entries generated")

        lines.append(f"\n{'='*60}")

        return "\n".join(lines)








