"""Click command definitions for veritas-accounting CLI."""

import sys
from pathlib import Path

import click

from veritas_accounting.cli.processor import ProcessingPipeline
from veritas_accounting.config.settings import AppConfig, InputConfig
from veritas_accounting.utils.exceptions import ExcelIOError, ValidationError


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """
    veritas-accounting: Excel-native accounting automation.

    Transform journal entries through mapping rules to generate ledger reports
    with complete transparency and validation.
    """
    pass


@main.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, path_type=str),
    help="Path to journal entries Excel file (required)",
)
@click.option(
    "--rules",
    "-r",
    type=click.Path(exists=True, path_type=str),
    help="Path to mapping rules Excel file (optional, can be specified in config)",
)
@click.option(
    "--account-hierarchy",
    "-a",
    type=click.Path(exists=True, path_type=str),
    help="Path to account hierarchy Excel file (optional)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=str),
    default="./output",
    help="Output directory (default: ./output)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=str),
    help="Configuration file path (YAML format, optional)",
)
@click.option(
    "--validation-level",
    type=click.Choice(["strict", "lenient"], case_sensitive=False),
    help="Validation level: 'strict' or 'lenient' (default: strict)",
)
@click.option(
    "--auto-fix",
    is_flag=True,
    help="Enable auto-fix suggestions for validation errors",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def process(
    input: str,
    rules: str | None,
    account_hierarchy: str | None,
    output: str,
    config: str | None,
    validation_level: str | None,
    auto_fix: bool,
    verbose: bool,
) -> None:
    """
    Process journal entries through mapping rules to generate ledger output.

    This command performs the complete accounting automation workflow:
    1. Reads journal entries from Excel file
    2. Validates input data
    3. Applies mapping rules to transform entries
    4. Generates ledger output, quarterly reports, and error reports
    5. Exports audit trail for complete traceability

    Example:
        veritas-accounting process --input journal.xlsx --rules rules.xlsx --output ./output
    """
    try:
        # Load configuration
        app_config = _load_config(
            config_path=config,
            journal_file=input,
            rules_file=rules,
            account_hierarchy_file=account_hierarchy,
            output_dir=output,
            validation_level=validation_level,
            auto_fix_enabled=auto_fix,
        )

        # Validate configuration
        is_valid, errors = app_config.validate_paths()
        if not is_valid:
            click.echo("❌ Configuration errors:", err=True)
            for error in errors:
                click.echo(f"   • {error}", err=True)
            sys.exit(1)

        # Create and run processing pipeline
        pipeline = ProcessingPipeline(app_config)
        results = pipeline.process()

        # Check results
        if not results["success"]:
            if results["errors"]:
                click.echo("\n❌ Processing failed with errors:", err=True)
                for error in results["errors"]:
                    click.echo(f"   • {error}", err=True)
            sys.exit(1)

        # Show summary
        if "statistics" in results:
            stats = results["statistics"]
            click.echo("\n📊 Processing Summary:")
            click.echo(f"   • Journal entries processed: {stats['journal_entries']}")
            click.echo(f"   • Ledger entries generated: {stats['ledger_entries']}")
            click.echo(f"   • Rules applied: {stats['rules_applied']}")
            if stats["unmatched_entries"] > 0:
                click.echo(f"   • Unmatched entries: {stats['unmatched_entries']}")
            if stats["validation_errors"] > 0:
                click.echo(f"   • Validation errors: {stats['validation_errors']}")
            if stats["validation_warnings"] > 0:
                click.echo(f"   • Validation warnings: {stats['validation_warnings']}")

        sys.exit(0)

    except FileNotFoundError as e:
        click.echo(f"❌ File not found: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)
    except ExcelIOError as e:
        click.echo(f"❌ Excel I/O error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, path_type=str),
    help="Path to journal entries Excel file",
)
@click.option(
    "--rules",
    "-r",
    type=click.Path(exists=True, path_type=str),
    help="Path to mapping rules Excel file",
)
def validate(
    input: str,
    rules: str | None,
) -> None:
    """
    Validate input files and mapping rules without processing.

    Checks that:
    - Journal entries file is valid and readable
    - Mapping rules file is valid (if provided)
    - All required columns are present
    - Data types are correct
    - Business rules are satisfied

    Example:
        veritas-accounting validate --input journal.xlsx --rules rules.xlsx
    """
    try:
        click.echo("🔍 Validating input files...")

        # Validate journal entries
        from veritas_accounting.excel.journal_reader import JournalEntryReader
        reader = JournalEntryReader()
        entries, errors = reader.read_journal_entries(input)

        if errors:
            click.echo(f"❌ Found {len(errors)} validation errors in journal entries:")
            for error in errors[:10]:  # Show first 10 errors
                click.echo(f"   • {error}")
            if len(errors) > 10:
                click.echo(f"   ... and {len(errors) - 10} more errors")
            sys.exit(1)
        else:
            click.echo(f"✅ Journal entries file is valid ({len(entries)} entries)")

        # Validate rules if provided
        if rules:
            from veritas_accounting.excel.rule_reader import MappingRuleReader
            rule_reader = MappingRuleReader()
            rule_entries, rule_errors = rule_reader.read_rules(rules)

            if rule_errors:
                click.echo(f"❌ Found {len(rule_errors)} validation errors in mapping rules:")
                for error in rule_errors[:10]:  # Show first 10 errors
                    click.echo(f"   • {error}")
                if len(rule_errors) > 10:
                    click.echo(f"   ... and {len(rule_errors) - 10} more errors")
                sys.exit(1)
            else:
                click.echo(f"✅ Mapping rules file is valid ({len(rule_entries)} rules)")

        click.echo("\n✅ All input files are valid!")
        sys.exit(0)

    except FileNotFoundError as e:
        click.echo(f"❌ File not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)


def _load_config(
    config_path: str | None = None,
    journal_file: str | None = None,
    rules_file: str | None = None,
    account_hierarchy_file: str | None = None,
    output_dir: str | None = None,
    validation_level: str | None = None,
    auto_fix_enabled: bool = False,
) -> AppConfig:
    """
    Load configuration from multiple sources with proper priority.

    Priority order:
    1. Command-line arguments (highest)
    2. Configuration file (YAML)
    3. Environment variables
    4. Default values (lowest)

    Args:
        config_path: Path to configuration file
        journal_file: Journal file path from CLI
        rules_file: Rules file path from CLI
        account_hierarchy_file: Account hierarchy file path from CLI
        output_dir: Output directory from CLI
        validation_level: Validation level from CLI
        auto_fix_enabled: Auto-fix enabled from CLI

    Returns:
        AppConfig instance
    """
    # Start with defaults or environment variables
    try:
        config = AppConfig.from_env()
    except ValueError:
        # No environment variables set, use defaults
        if not journal_file:
            raise click.BadParameter(
                "Journal file is required. Provide --input or set VERITAS_JOURNAL_FILE environment variable."
            )
        config = AppConfig(
            input=InputConfig(journal_file=journal_file or ""),
        )

    # Override with config file if provided
    if config_path:
        file_config = AppConfig.from_yaml(config_path)
        # Merge: file config values override base config
        config_dict = config.model_dump()
        file_dict = file_config.model_dump()
        # Deep merge
        for key in ["input", "output", "validation", "processing"]:
            if key in file_dict:
                config_dict[key].update(file_dict[key])
        config = AppConfig(**config_dict)

    # Override with CLI arguments (highest priority)
    config = config.merge_with_cli_args(
        journal_file=journal_file,
        rules_file=rules_file,
        account_hierarchy_file=account_hierarchy_file,
        output_dir=output_dir,
        validation_level=validation_level,
        auto_fix_enabled=auto_fix_enabled if auto_fix_enabled else None,
    )

    return config


if __name__ == "__main__":
    main()
