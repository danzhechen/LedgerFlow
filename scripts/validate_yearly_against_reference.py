#!/usr/bin/env python3
"""
Run the pipeline on journal_entry_2020_2024.xlsx (per-year sheets) and validate
yearly report numbers against reference Veritas China Account book files.

Usage:
  # Reference files in a directory (named by year: 2020.xlsx, 2021.xlsx, ... or full names)
  python scripts/validate_yearly_against_reference.py \\
    --journal examples/journal_entry_2020_2024.xlsx \\
    --rules 账目分类明细_ledger_rules.xlsx \\
    --account-hierarchy 账目分类明细.xlsx \\
    --output ./output \\
    --reference-dir /path/to/reference_books

  # Or specify each reference file
  python scripts/validate_yearly_against_reference.py ... \\
    --reference-2020 "/Users/.../2020Veritas China Account book.xlsx" \\
    --reference-2021 "/Users/.../2021Veritas China Account book.xlsx" \\
    ...

Environment:
  REFERENCE_2020, REFERENCE_2021, ... can be used instead of --reference-YYYY.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add scripts dir so we can import yearly_validation_helpers
_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import click

from yearly_validation_helpers import (
    compare_yearly,
    compare_yearly_by_name,
    get_ours_by_account_name,
    get_yearly_numbers_from_pipeline_output,
    get_yearly_numbers_from_reference,
    get_yearly_numbers_from_reference_summary_fy,
)


def _run_multi_sheet_pipeline(
    journal_file: str,
    rules_file: str,
    account_hierarchy_file: str | None,
    output_dir: str,
) -> bool:
    """Run process_multi_sheet for 2020–2024 sheets. Returns True if all succeeded."""
    from veritas_accounting.cli.processor import ProcessingPipeline
    from veritas_accounting.config.settings import AppConfig, InputConfig, OutputConfig, ValidationConfig

    sheets = ["2020", "2021", "2022", "2023", "2024"]
    base = Path(output_dir)
    all_ok = True
    for sheet_name in sheets:
        out = base / sheet_name
        out.mkdir(parents=True, exist_ok=True)
        config = AppConfig(
            input=InputConfig(
                journal_file=journal_file,
                rules_file=rules_file,
                account_hierarchy_file=account_hierarchy_file or "",
            ),
            output=OutputConfig(directory=str(out)),
            validation=ValidationConfig(level="strict", auto_fix_enabled=False),
            sheet_name=sheet_name,
        )
        pipeline = ProcessingPipeline(config)
        result = pipeline.process()
        if not result.get("success"):
            click.echo(f"  ❌ Sheet {sheet_name} failed: {result.get('errors', [])}", err=True)
            all_ok = False
        else:
            click.echo(f"  ✓ Sheet {sheet_name} -> {out}")
    return all_ok


@click.command()
@click.option("--journal", "-j", required=True, type=click.Path(exists=True), help="Journal Excel (multi-sheet 2020–2024)")
@click.option("--rules", "-r", required=True, type=click.Path(exists=True), help="Mapping rules Excel")
@click.option("--account-hierarchy", "-a", type=click.Path(exists=True), default=None, help="Account hierarchy Excel")
@click.option("--output", "-o", type=click.Path(), default="./output", help="Base output directory")
@click.option(
    "--reference-dir",
    type=click.Path(exists=True),
    default=None,
    help="Directory containing reference files 2020.xlsx … 2024.xlsx or full names",
)
@click.option("--reference-2020", type=click.Path(exists=True), default=None, help="Path to 2020 reference account book")
@click.option("--reference-2021", type=click.Path(exists=True), default=None, help="Path to 2021 reference account book")
@click.option("--reference-2022", type=click.Path(exists=True), default=None, help="Path to 2022 reference account book")
@click.option("--reference-2023", type=click.Path(exists=True), default=None, help="Path to 2023 reference account book")
@click.option("--reference-2024", type=click.Path(exists=True), default=None, help="Path to 2024 reference account book")
@click.option("--tolerance", "-t", type=float, default=0.01, help="Numeric tolerance for amount comparison")
@click.option("--run-pipeline/--no-run-pipeline", default=True, help="Run pipeline first (default: yes)")
@click.option(
    "--reference-format",
    type=click.Choice(["ledger", "summary_fy"], case_sensitive=False),
    default="summary_fy",
    help="Reference format: summary_fy = 报表小结FY sheet (category -> net); ledger = per-account CR/DR/Net",
)
@click.option(
    "--year-label",
    default=None,
    help="Single column label for all years (overrides per-year labels). If unset, 2024 uses 2024Q1-Q3 (no Q4 data), others use year number.",
)
@click.option(
    "--year-labels",
    default=None,
    help='Per-year column labels, e.g. "2020:2020,2021:2021,2022:2022,2023:2023,2024:2024Q1-Q3"',
)
def main(
    journal: str,
    rules: str,
    account_hierarchy: str | None,
    output: str,
    reference_dir: str | None,
    reference_2020: str | None,
    reference_2021: str | None,
    reference_2022: str | None,
    reference_2023: str | None,
    reference_2024: str | None,
    tolerance: float,
    run_pipeline: bool,
    reference_format: str,
    year_label: str | None,
    year_labels: str | None,
) -> None:
    """Validate pipeline yearly output against reference account books."""
    years = [2020, 2021, 2022, 2023, 2024]
    ref_paths: dict[int, Path] = {}
    ref_opts = {
        2020: reference_2020 or os.environ.get("REFERENCE_2020"),
        2021: reference_2021 or os.environ.get("REFERENCE_2021"),
        2022: reference_2022 or os.environ.get("REFERENCE_2022"),
        2023: reference_2023 or os.environ.get("REFERENCE_2023"),
        2024: reference_2024 or os.environ.get("REFERENCE_2024"),
    }
    if reference_dir:
        ref_dir = Path(reference_dir)
        for y in years:
            # Try exact name then 2024Veritas China Account book (1).xlsx style
            for name in [f"{y}.xlsx", f"{y}Veritas China Account book.xlsx", f"{y}Veritas China Account book (1).xlsx"]:
                p = ref_dir / name
                if p.exists():
                    ref_paths[y] = p
                    break
    for y in years:
        if ref_opts[y]:
            ref_paths[y] = Path(ref_opts[y])

    # Per-year column label for reference 报表小结FY (2024 has no Q4 → use 2024Q1-Q3 only)
    year_label_map: dict[int, str] = {}
    if year_labels:
        for part in year_labels.split(","):
            part = part.strip()
            if ":" in part:
                ystr, label = part.split(":", 1)
                try:
                    year_label_map[int(ystr.strip())] = label.strip()
                except ValueError:
                    pass
    if year_label:
        # Single label for all years
        year_label_map = {y: year_label for y in years}
    if not year_label_map:
        year_label_map = {2024: "2024Q1-Q3"}
        for y in (2020, 2021, 2022, 2023):
            year_label_map.setdefault(y, str(y))

    if run_pipeline:
        click.echo("Running pipeline (multi-sheet 2020–2024)...")
        ok = _run_multi_sheet_pipeline(journal, rules, account_hierarchy or "", output)
        if not ok:
            click.echo("Pipeline had failures; continuing with validation for successful sheets.", err=True)
    else:
        click.echo("Skipping pipeline (--no-run-pipeline).")

    base = Path(output)
    ledger_file = "ledger_output.xlsx"
    total_diffs: list[tuple[int, list]] = []
    for year in years:
        our_report = base / str(year) / ledger_file
        ref_path = ref_paths.get(year)
        if not ref_path or not ref_path.exists():
            click.echo(f"  ⚠ {year}: No reference file (skip validation)")
            continue
        if reference_format == "summary_fy":
            ours_by_name = get_ours_by_account_name(our_report, year)
            ref_col = year_label_map.get(year, str(year))
            reference_net = get_yearly_numbers_from_reference_summary_fy(ref_path, year_label=ref_col)
            if not reference_net:
                click.echo(f"  ⚠ {year}: Reference 报表小结FY empty or sheet not found: {ref_path}")
                continue
            diffs = compare_yearly_by_name(ours_by_name, reference_net, tolerance=tolerance)
            n_categories = len(ours_by_name)
        else:
            ours = get_yearly_numbers_from_pipeline_output(our_report, year)
            reference = get_yearly_numbers_from_reference(ref_path)
            if not reference:
                click.echo(f"  ⚠ {year}: Reference file empty or unreadable: {ref_path}")
                continue
            diffs = compare_yearly(ours, reference, tolerance=tolerance)
            n_categories = len(ours)
        total_diffs.append((year, diffs))
        if not diffs:
            click.echo(f"  ✓ {year}: All yearly numbers match reference ({n_categories} categories)")
        else:
            click.echo(f"  ❌ {year}: {len(diffs)} difference(s)")
            for d in diffs[:15]:
                click.echo(f"      {d.get('account')} | {d.get('message', d)}")
            if len(diffs) > 15:
                click.echo(f"      ... and {len(diffs) - 15} more")

    if any(d for _, d in total_diffs):
        sys.exit(1)
    click.echo("All yearly validations passed.")


if __name__ == "__main__":
    main()
