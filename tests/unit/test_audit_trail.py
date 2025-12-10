"""Unit tests for audit trail tracking."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.audit.trail import AppliedRule, AuditTrail, TransformationRecord
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.rules.applicator import RuleApplicationResult
from veritas_accounting.models.rule import MappingRule


@pytest.fixture
def sample_journal_entry():
    """Create a sample journal entry for testing."""
    return JournalEntry(
        entry_id="JE-001",
        year=2024,
        description="Test entry",
        old_type="OL",
        amount=Decimal("1000.00"),
        date=datetime(2024, 1, 15),
    )


@pytest.fixture
def sample_rule():
    """Create a sample mapping rule for testing."""
    return MappingRule(
        rule_id="R-001",
        condition="old_type == 'OL'",
        account_code="A1",
        priority=1,
    )


@pytest.fixture
def sample_ledger_entry(sample_journal_entry, sample_rule):
    """Create a sample ledger entry for testing."""
    return LedgerEntry(
        entry_id="LE-001",
        account_code="A1",
        account_path="Level1/Level2/Level3/Level4",
        amount=Decimal("1000.00"),
        date=datetime(2024, 1, 15),
        description="Test entry",
        source_entry_id=sample_journal_entry.entry_id,
        rule_applied=sample_rule.rule_id,
        quarter=1,
        year=2024,
    )


@pytest.fixture
def sample_rule_application_result(sample_journal_entry, sample_rule, sample_ledger_entry):
    """Create a sample rule application result for testing."""
    return RuleApplicationResult(
        ledger_entries=[sample_ledger_entry],
        applied_rules=[sample_rule],
        no_match=False,
        entry_id=sample_journal_entry.entry_id,
    )


@pytest.fixture
def audit_trail():
    """Create an audit trail for testing."""
    return AuditTrail(
        user="test_user",
        system_version="1.0.0",
        rule_version="v1",
    )


class TestAuditTrail:
    """Test cases for AuditTrail class."""

    def test_initialization(self):
        """Test audit trail initialization."""
        trail = AuditTrail()
        assert trail.records == []
        assert trail.user is None
        assert trail.system_version is None
        assert trail.rule_version is None

    def test_initialization_with_metadata(self):
        """Test audit trail initialization with metadata."""
        trail = AuditTrail(
            user="user1",
            system_version="1.0.0",
            rule_version="v1",
        )
        assert trail.user == "user1"
        assert trail.system_version == "1.0.0"
        assert trail.rule_version == "v1"

    def test_start_end_timing(self, audit_trail):
        """Test start and end timing."""
        audit_trail.start()
        assert audit_trail._start_time is not None

        audit_trail.end()
        assert audit_trail._end_time is not None
        assert audit_trail._end_time >= audit_trail._start_time

    def test_record_transformation(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test recording a single transformation."""
        record = audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )

        assert isinstance(record, TransformationRecord)
        assert record.entry_id == sample_journal_entry.entry_id
        assert record.source_entry == sample_journal_entry
        assert len(record.applied_rules) == 1
        assert len(record.generated_entries) == 1
        assert not record.no_match
        assert len(audit_trail.records) == 1

    def test_record_transformation_no_match(
        self, audit_trail, sample_journal_entry
    ):
        """Test recording a transformation with no match."""
        no_match_result = RuleApplicationResult(
            ledger_entries=[],
            applied_rules=[],
            no_match=True,
            entry_id=sample_journal_entry.entry_id,
        )

        record = audit_trail.record_transformation(
            sample_journal_entry, no_match_result
        )

        assert record.no_match
        assert len(record.applied_rules) == 0
        assert len(record.generated_entries) == 0

    def test_record_batch_transformation(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test recording batch transformations."""
        entries = [sample_journal_entry]
        results = [sample_rule_application_result]

        records = audit_trail.record_batch_transformation(entries, results)

        assert len(records) == 1
        assert len(audit_trail.records) == 1

    def test_record_batch_transformation_mismatch(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test batch transformation with mismatched lengths."""
        entries = [sample_journal_entry]
        results = [sample_rule_application_result, sample_rule_application_result]

        with pytest.raises(ValueError, match="must have the same length"):
            audit_trail.record_batch_transformation(entries, results)

    def test_get_record_by_entry_id(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test getting record by entry ID."""
        audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )

        record = audit_trail.get_record_by_entry_id(sample_journal_entry.entry_id)
        assert record is not None
        assert record.entry_id == sample_journal_entry.entry_id

        # Non-existent entry
        assert audit_trail.get_record_by_entry_id("NONEXISTENT") is None

    def test_get_records_by_rule_id(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test getting records by rule ID."""
        audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )

        records = audit_trail.get_records_by_rule_id("R-001")
        assert len(records) == 1

        # Non-existent rule
        assert len(audit_trail.get_records_by_rule_id("NONEXISTENT")) == 0

    def test_get_all_ledger_entries(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test getting all ledger entries."""
        audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )

        ledger_entries = audit_trail.get_all_ledger_entries()
        assert len(ledger_entries) == 1
        assert ledger_entries[0].entry_id == "LE-001"

    def test_get_unmatched_entries(
        self, audit_trail, sample_journal_entry
    ):
        """Test getting unmatched entries."""
        no_match_result = RuleApplicationResult(
            ledger_entries=[],
            applied_rules=[],
            no_match=True,
            entry_id=sample_journal_entry.entry_id,
        )

        audit_trail.record_transformation(sample_journal_entry, no_match_result)

        unmatched = audit_trail.get_unmatched_entries()
        assert len(unmatched) == 1
        assert unmatched[0].entry_id == sample_journal_entry.entry_id

    def test_get_summary(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test getting summary statistics."""
        audit_trail.start()
        audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )
        audit_trail.end()

        summary = audit_trail.get_summary()

        assert summary["total_transformations"] == 1
        assert summary["matched_entries"] == 1
        assert summary["unmatched_entries"] == 0
        assert summary["total_ledger_entries"] == 1
        assert summary["unique_rules_applied"] == 1
        assert summary["user"] == "test_user"
        assert summary["system_version"] == "1.0.0"
        assert summary["rule_version"] == "v1"
        assert summary["start_time"] is not None
        assert summary["end_time"] is not None
        assert summary["duration_seconds"] is not None

    def test_to_dict(
        self, audit_trail, sample_journal_entry, sample_rule_application_result
    ):
        """Test converting audit trail to dictionary."""
        audit_trail.start()
        audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )
        audit_trail.end()

        data = audit_trail.to_dict()

        assert "metadata" in data
        assert "summary" in data
        assert "transformations" in data
        assert len(data["transformations"]) == 1

    def test_clear(self, audit_trail, sample_journal_entry, sample_rule_application_result):
        """Test clearing audit trail."""
        audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )
        assert len(audit_trail.records) == 1

        audit_trail.clear()
        assert len(audit_trail.records) == 0
        assert audit_trail._start_time is None
        assert audit_trail._end_time is None


class TestTransformationRecord:
    """Test cases for TransformationRecord class."""

    def test_to_dict(self, sample_journal_entry, sample_rule_application_result):
        """Test converting transformation record to dictionary."""
        audit_trail = AuditTrail()
        record = audit_trail.record_transformation(
            sample_journal_entry, sample_rule_application_result
        )

        data = record.to_dict()

        assert data["entry_id"] == sample_journal_entry.entry_id
        assert "timestamp" in data
        assert "source_entry" in data
        assert "applied_rules" in data
        assert "generated_entries" in data
        assert data["no_match"] is False
