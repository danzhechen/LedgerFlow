#!/usr/bin/env python3
"""
Process all sheets from a multi-sheet Excel file.

This script processes each sheet in the Excel file separately and saves
outputs to separate directories for each sheet.
"""

import sys
from pathlib import Path

import click
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from veritas_accounting.cli.processor import ProcessingPipeline
from veritas_accounting.config.settings import AppConfig


def get_sheet_names(excel_file: str) -> list[str]:
    """Get all sheet names from an Excel file."""
    try:
        xl = pd.ExcelFile(excel_file)
        return xl.sheet_names
    except Exception as e:
        raise click.ClickException(f"Failed to read Excel file: {e}")


def process_sheet(
    excel_file: str,
    sheet_name: str,
    rules_file: str | None,
    account_hierarchy_file: str | None,
    base_output_dir: str,
    validation_level: str | None = None,
    auto_fix: bool = False,
) -> dict[str, any]:
    """
    Process a single sheet from the Excel file.

    Args:
        excel_file: Path to Excel file
        sheet_name: Name of the sheet to process
        rules_file: Path to mapping rules file
        account_hierarchy_file: Path to account hierarchy file
        base_output_dir: Base output directory (will create subdirectory for sheet)
        validation_level: Validation level ('strict' or 'lenient')
        auto_fix: Enable auto-fix

    Returns:
        Dictionary with processing results
    """
    # Create output directory for this sheet
    output_dir = Path(base_output_dir) / sheet_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create config for this sheet
    from veritas_accounting.config.settings import InputConfig, OutputConfig, ValidationConfig
    
    config = AppConfig(
        input=InputConfig(
            journal_file=excel_file,
            rules_file=rules_file,
            account_hierarchy_file=account_hierarchy_file,
        ),
        output=OutputConfig(directory=str(output_dir)),
        validation=ValidationConfig(
            level=validation_level or "strict",
            auto_fix_enabled=auto_fix,
        ),
        sheet_name=sheet_name,
    )

    # Process this sheet
    pipeline = ProcessingPipeline(config)
    results = pipeline.process()

    return results


@click.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, path_type=str),
    help="Path to multi-sheet Excel file",
)
@click.option(
    "--rules",
    "-r",
    type=click.Path(exists=True, path_type=str),
    help="Path to mapping rules Excel file",
)
@click.option(
    "--account-hierarchy",
    "-a",
    type=click.Path(exists=True, path_type=str),
    help="Path to account hierarchy Excel file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=str),
    default="./output",
    help="Base output directory (default: ./output)",
)
@click.option(
    "--validation-level",
    type=click.Choice(["strict", "lenient"], case_sensitive=False),
    help="Validation level: 'strict' or 'lenient'",
)
@click.option(
    "--auto-fix",
    is_flag=True,
    help="Enable auto-fix suggestions",
)
@click.option(
    "--sheet",
    "-s",
    multiple=True,
    help="Specific sheets to process (can specify multiple times). If not specified, processes all sheets.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    input: str,
    rules: str | None,
    account_hierarchy: str | None,
    output: str,
    validation_level: str | None,
    auto_fix: bool,
    sheet: tuple[str, ...],
    verbose: bool,
) -> None:
    """
    Process all sheets from a multi-sheet Excel file.

    Each sheet is processed separately and outputs are saved to separate
    subdirectories under the output directory.

    Example:
        python process_multi_sheet.py -i journal.xlsx -r rules.xlsx -o ./output
    """
    try:
        # Get all sheet names
        all_sheets = get_sheet_names(input)
        
        # Determine which sheets to process
        if sheet:
            sheets_to_process = list(sheet)
            # Validate sheet names
            invalid_sheets = [s for s in sheets_to_process if s not in all_sheets]
            if invalid_sheets:
                click.echo(f"❌ Invalid sheet names: {', '.join(invalid_sheets)}", err=True)
                click.echo(f"Available sheets: {', '.join(all_sheets)}", err=True)
                sys.exit(1)
        else:
            sheets_to_process = all_sheets

        click.echo(f"📊 Found {len(all_sheets)} sheets: {', '.join(all_sheets)}")
        click.echo(f"🔄 Processing {len(sheets_to_process)} sheet(s)...")
        click.echo()

        # Process each sheet
        results_summary = {}
        base_output_path = Path(output)
        
        for idx, sheet_name in enumerate(sheets_to_process, 1):
            click.echo(f"{'='*60}")
            click.echo(f"Processing sheet {idx}/{len(sheets_to_process)}: {sheet_name}")
            click.echo(f"{'='*60}")
            
            try:
                results = process_sheet(
                    excel_file=input,
                    sheet_name=sheet_name,
                    rules_file=rules,
                    account_hierarchy_file=account_hierarchy,
                    base_output_dir=output,
                    validation_level=validation_level,
                    auto_fix=auto_fix,
                )
                
                results_summary[sheet_name] = results
                
                if results["success"]:
                    stats = results.get("statistics", {})
                    click.echo(f"\n✅ Sheet '{sheet_name}' processed successfully!")
                    click.echo(f"   • Journal entries: {stats.get('journal_entries', 0)}")
                    click.echo(f"   • Ledger entries: {stats.get('ledger_entries', 0)}")
                    click.echo(f"   • Output directory: {base_output_path / sheet_name}")
                else:
                    click.echo(f"\n❌ Sheet '{sheet_name}' processing failed!")
                    if results.get("errors"):
                        for error in results["errors"][:5]:  # Show first 5 errors
                            click.echo(f"   • {error}")
            except Exception as e:
                click.echo(f"\n❌ Error processing sheet '{sheet_name}': {e}", err=True)
                if verbose:
                    import traceback
                    traceback.print_exc()
                results_summary[sheet_name] = {"success": False, "errors": [str(e)]}
            
            click.echo()

        # Print summary
        click.echo(f"{'='*60}")
        click.echo("📊 Processing Summary")
        click.echo(f"{'='*60}")
        
        successful = sum(1 for r in results_summary.values() if r.get("success", False))
        failed = len(results_summary) - successful
        
        click.echo(f"Total sheets processed: {len(sheets_to_process)}")
        click.echo(f"✅ Successful: {successful}")
        if failed > 0:
            click.echo(f"❌ Failed: {failed}")
        
        click.echo()
        click.echo(f"📁 Output files saved to: {base_output_path.absolute()}")
        click.echo(f"   Each sheet has its own subdirectory:")
        for sheet_name in sheets_to_process:
            status = "✅" if results_summary[sheet_name].get("success", False) else "❌"
            click.echo(f"   {status} {sheet_name}/ -> {base_output_path / sheet_name}")

    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
