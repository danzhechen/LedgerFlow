"""Configuration management for veritas-accounting."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class InputConfig(BaseModel):
    """Input file configuration."""

    journal_file: str = Field(
        ...,
        description="Path to journal entries Excel file",
    )
    rules_file: Optional[str] = Field(
        None,
        description="Path to mapping rules Excel file (optional)",
    )
    account_hierarchy_file: Optional[str] = Field(
        None,
        description="Path to account hierarchy Excel file (optional)",
    )

    @field_validator("journal_file", "rules_file", "account_hierarchy_file", mode="before")
    @classmethod
    def validate_file_path(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate file path format (existence check is done separately).

        Args:
            v: File path or None

        Returns:
            File path or None
        """
        # Just return the value - existence validation is done in validate_paths()
        return v


class OutputConfig(BaseModel):
    """Output configuration."""

    directory: str = Field(
        default="./output",
        description="Output directory path",
    )
    ledger_file: str = Field(
        default="ledger_output.xlsx",
        description="Ledger output file name",
    )
    quarterly_report_file: str = Field(
        default="quarterly_report.xlsx",
        description="Quarterly report file name",
    )
    error_report_file: str = Field(
        default="error_report.xlsx",
        description="Error report file name",
    )
    audit_trail_file: str = Field(
        default="audit_trail.xlsx",
        description="Audit trail export file name",
    )


class ValidationConfig(BaseModel):
    """Validation configuration."""

    level: str = Field(
        default="strict",
        description="Validation level: 'strict' or 'lenient'",
    )
    auto_fix_enabled: bool = Field(
        default=False,
        description="Enable auto-fix suggestions",
    )
    require_review: bool = Field(
        default=True,
        description="Require review for all errors",
    )

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """
        Validate validation level.

        Args:
            v: Validation level string

        Returns:
            Validation level string

        Raises:
            ValueError: If level is invalid
        """
        if v not in ["strict", "lenient"]:
            raise ValueError(f"Invalid validation level: {v}. Must be 'strict' or 'lenient'")
        return v


class ProcessingConfig(BaseModel):
    """Processing configuration."""

    parallel_processing: bool = Field(
        default=False,
        description="Enable parallel processing (future feature)",
    )
    chunk_size: Optional[int] = Field(
        None,
        description="Chunk size for batch processing",
    )


class AppConfig(BaseModel):
    """
    Main application configuration.

    Supports configuration from multiple sources with priority:
    1. Command-line arguments (highest)
    2. Configuration file (YAML/JSON)
    3. Environment variables
    4. Default values (lowest)
    """

    input: InputConfig
    output: OutputConfig = Field(default_factory=OutputConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    sheet_name: Optional[str] = Field(
        None,
        description="Specific sheet name to read from Excel file (for multi-sheet processing)",
    )

    @classmethod
    def from_yaml(cls, config_path: Path | str) -> "AppConfig":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            AppConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in configuration file: {e}") from e

        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """
        Create configuration from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            AppConfig instance
        """
        return cls(**data)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        Load configuration from environment variables.

        Returns:
            AppConfig instance with values from environment
        """
        # Build config from environment variables
        config_dict = {
            "input": {
                "journal_file": os.getenv("VERITAS_JOURNAL_FILE", ""),
                "rules_file": os.getenv("VERITAS_RULES_FILE"),
                "account_hierarchy_file": os.getenv("VERITAS_ACCOUNT_HIERARCHY_FILE"),
            },
            "output": {
                "directory": os.getenv("VERITAS_OUTPUT_DIR", "./output"),
                "ledger_file": os.getenv("VERITAS_LEDGER_FILE", "ledger_output.xlsx"),
                "quarterly_report_file": os.getenv(
                    "VERITAS_QUARTERLY_REPORT_FILE", "quarterly_report.xlsx"
                ),
                "error_report_file": os.getenv(
                    "VERITAS_ERROR_REPORT_FILE", "error_report.xlsx"
                ),
                "audit_trail_file": os.getenv(
                    "VERITAS_AUDIT_TRAIL_FILE", "audit_trail.xlsx"
                ),
            },
            "validation": {
                "level": os.getenv("VERITAS_VALIDATION_LEVEL", "strict"),
                "auto_fix_enabled": os.getenv("VERITAS_AUTO_FIX_ENABLED", "false").lower() == "true",
                "require_review": os.getenv("VERITAS_REQUIRE_REVIEW", "true").lower() == "true",
            },
            "processing": {
                "parallel_processing": os.getenv("VERITAS_PARALLEL_PROCESSING", "false").lower() == "true",
                "chunk_size": int(os.getenv("VERITAS_CHUNK_SIZE", "0")) or None,
            },
        }

        # Only create if journal_file is provided
        if not config_dict["input"]["journal_file"]:
            raise ValueError("VERITAS_JOURNAL_FILE environment variable is required")

        return cls(**config_dict)

    def merge_with_cli_args(
        self,
        journal_file: Optional[str] = None,
        rules_file: Optional[str] = None,
        account_hierarchy_file: Optional[str] = None,
        output_dir: Optional[str] = None,
        validation_level: Optional[str] = None,
        auto_fix_enabled: Optional[bool] = None,
    ) -> "AppConfig":
        """
        Merge CLI arguments into configuration (CLI args override config).

        Args:
            journal_file: Journal file path from CLI
            rules_file: Rules file path from CLI
            account_hierarchy_file: Account hierarchy file path from CLI
            output_dir: Output directory from CLI
            validation_level: Validation level from CLI
            auto_fix_enabled: Auto-fix enabled from CLI

        Returns:
            New AppConfig instance with merged values
        """
        config_dict = self.model_dump()

        # Merge CLI args (override config)
        if journal_file:
            config_dict["input"]["journal_file"] = journal_file
        if rules_file:
            config_dict["input"]["rules_file"] = rules_file
        if account_hierarchy_file:
            config_dict["input"]["account_hierarchy_file"] = account_hierarchy_file
        if output_dir:
            config_dict["output"]["directory"] = output_dir
        if validation_level:
            config_dict["validation"]["level"] = validation_level
        if auto_fix_enabled is not None:
            config_dict["validation"]["auto_fix_enabled"] = auto_fix_enabled

        return AppConfig(**config_dict)

    def validate_paths(self) -> tuple[bool, list[str]]:
        """
        Validate that all configured file paths exist.

        Returns:
            Tuple of (is_valid, errors) where:
            - is_valid: True if all paths are valid
            - errors: List of error messages
        """
        errors: list[str] = []

        # Validate input files
        if not Path(self.input.journal_file).exists():
            errors.append(f"Journal file not found: {self.input.journal_file}")

        if self.input.rules_file and not Path(self.input.rules_file).exists():
            errors.append(f"Rules file not found: {self.input.rules_file}")

        if (
            self.input.account_hierarchy_file
            and not Path(self.input.account_hierarchy_file).exists()
        ):
            errors.append(
                f"Account hierarchy file not found: {self.input.account_hierarchy_file}"
            )

        # Validate output directory (create if doesn't exist)
        output_path = Path(self.output.directory)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")

        return len(errors) == 0, errors








