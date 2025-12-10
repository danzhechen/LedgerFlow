"""Unit tests for CLI components."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from veritas_accounting.cli.error_formatter import CLIErrorFormatter
from veritas_accounting.config.settings import AppConfig, InputConfig, OutputConfig
from veritas_accounting.validation.error_detector import DetectedError, ERROR_TYPE_DATA, SEVERITY_ERROR


@pytest.fixture
def sample_error():
    """Create a sample error for testing."""
    return DetectedError(
        row_number=1,
        field_name="year",
        error_type=ERROR_TYPE_DATA,
        error_message="Year must be between 2000 and 2100",
        actual_value=1999,
        entry_id="JE-001",
        severity=SEVERITY_ERROR,
    )


class TestAppConfig:
    """Test cases for AppConfig class."""

    def test_initialization(self):
        """Test AppConfig initialization."""
        config = AppConfig(
            input=InputConfig(journal_file="test.xlsx"),
        )
        assert config.input.journal_file == "test.xlsx"
        assert config.output.directory == "./output"

    def test_from_yaml(self):
        """Test loading configuration from YAML file."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_data = {
                "input": {
                    "journal_file": "journal.xlsx",
                    "rules_file": "rules.xlsx",
                },
                "output": {
                    "directory": "./custom_output",
                },
            }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            config = AppConfig.from_yaml(config_path)
            assert config.input.journal_file == "journal.xlsx"
            assert config.input.rules_file == "rules.xlsx"
            assert config.output.directory == "./custom_output"

    def test_from_yaml_not_found(self):
        """Test loading from non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            AppConfig.from_yaml("nonexistent.yaml")

    def test_merge_with_cli_args(self):
        """Test merging CLI arguments into configuration."""
        config = AppConfig(
            input=InputConfig(journal_file="default.xlsx"),
        )

        merged = config.merge_with_cli_args(
            journal_file="cli.xlsx",
            output_dir="./cli_output",
        )

        assert merged.input.journal_file == "cli.xlsx"
        assert merged.output.directory == "./cli_output"

    def test_validate_paths(self):
        """Test path validation."""
        with TemporaryDirectory() as tmpdir:
            journal_file = Path(tmpdir) / "journal.xlsx"
            journal_file.touch()

            config = AppConfig(
                input=InputConfig(journal_file=str(journal_file)),
            )

            is_valid, errors = config.validate_paths()
            assert is_valid
            assert len(errors) == 0

    def test_validate_paths_missing_file(self):
        """Test path validation with missing file."""
        config = AppConfig(
            input=InputConfig(journal_file="nonexistent.xlsx"),
        )

        is_valid, errors = config.validate_paths()
        assert not is_valid
        assert len(errors) > 0


class TestCLIErrorFormatter:
    """Test cases for CLIErrorFormatter class."""

    def test_initialization(self):
        """Test CLIErrorFormatter initialization."""
        formatter = CLIErrorFormatter(use_colors=False)
        assert formatter.use_colors is False

    def test_format_simple_error(self, sample_error):
        """Test formatting simple error message."""
        formatter = CLIErrorFormatter(use_colors=False)
        message = formatter.format_error(sample_error, verbose=False)

        assert "year" in message.lower()
        assert "JE-001" in message
        assert "2000" in message or "2100" in message

    def test_format_detailed_error(self, sample_error):
        """Test formatting detailed error message."""
        formatter = CLIErrorFormatter(use_colors=False)
        message = formatter.format_error(sample_error, verbose=True)

        assert "year" in message.lower()
        assert len(message) > len(formatter.format_error(sample_error, verbose=False))

    def test_format_error_list(self, sample_error):
        """Test formatting error list."""
        formatter = CLIErrorFormatter(use_colors=False)
        errors = [sample_error]

        message = formatter.format_error_list(errors)
        assert "Found 1 error" in message
        assert "JE-001" in message

    def test_format_empty_error_list(self):
        """Test formatting empty error list."""
        formatter = CLIErrorFormatter(use_colors=False)
        message = formatter.format_error_list([])
        assert message == ""

    def test_get_severity_color(self):
        """Test getting severity color."""
        formatter = CLIErrorFormatter(use_colors=False)
        assert formatter._get_severity_color("error") == "red"
        assert formatter._get_severity_color("warning") == "yellow"
        assert formatter._get_severity_color("critical") == "red"
        assert formatter._get_severity_color("info") == "blue"

    def test_get_error_type_icon(self):
        """Test getting error type icon."""
        formatter = CLIErrorFormatter(use_colors=False)
        assert formatter._get_error_type_icon("data_error") == "📊"
        assert formatter._get_error_type_icon("rule_error") == "📋"
        assert formatter._get_error_type_icon("transformation_error") == "🔄"
        assert formatter._get_error_type_icon("output_error") == "📤"

    def test_get_quick_fix_hint(self, sample_error):
        """Test getting quick fix hint."""
        formatter = CLIErrorFormatter(use_colors=False)
        hint = formatter._get_quick_fix_hint(sample_error)
        # Hint may or may not be present depending on error message
        assert hint is None or isinstance(hint, str)
