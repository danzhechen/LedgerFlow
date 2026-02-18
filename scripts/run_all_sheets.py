#!/usr/bin/env python3
"""
Process all sheets from journal_entry_2020_2024.xlsx

Usage:
    python3 scripts/run_all_sheets.py [--rules RULES_FILE] [--account-hierarchy HIERARCHY_FILE]

This will process each sheet (2020, 2021, 2022, 2023, 2024) separately
and save outputs to separate directories:
    output/2020/
    output/2021/
    output/2022/
    output/2023/
    output/2024/
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Process all sheets using the CLI command."""
    script_dir = Path(__file__).parent.parent
    
    # Excel file with 5 sheets
    journal_file = script_dir / "examples" / "journal_entry_2020_2024.xlsx"
    
    if not journal_file.exists():
        print(f"❌ Error: Journal file not found: {journal_file}")
        sys.exit(1)
    
    # Get rules file (default or from args)
    rules_file = None
    account_hierarchy = None
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg == "--rules" and i + 1 < len(sys.argv):
                rules_file = sys.argv[i + 1]
            elif arg == "--account-hierarchy" and i + 1 < len(sys.argv):
                account_hierarchy = sys.argv[i + 1]
    
    if not rules_file:
        print("⚠️  Warning: No rules file specified. Using default location.")
        print("   Use --rules PATH to specify rules file")
        rules_file = "账目分类明细_ledger_rules.xlsx"  # Default
        if not Path(script_dir / rules_file).exists():
            print(f"   Default rules file not found: {rules_file}")
            print("   Please specify --rules PATH")
            sys.exit(1)
    
    # Sheet names
    sheets = ["2020", "2021", "2022", "2023", "2024"]
    
    print("=" * 60)
    print("Processing All Sheets from journal_entry_2020_2024.xlsx")
    print("=" * 60)
    print(f"Journal file: {journal_file}")
    print(f"Rules file: {rules_file}")
    if account_hierarchy:
        print(f"Account hierarchy: {account_hierarchy}")
    print(f"Output directories: output/2020/, output/2021/, etc.")
    print()
    
    # Process each sheet
    for sheet_name in sheets:
        print(f"{'=' * 60}")
        print(f"Processing sheet: {sheet_name}")
        print(f"{'=' * 60}")
        
        output_dir = script_dir / "output" / sheet_name
        
        # Build command
        cmd = [
            sys.executable,
            "-m", "veritas_accounting.cli.commands",
            "process",
            "--input", str(journal_file),
            "--rules", rules_file,
            "--output", str(output_dir),
        ]
        
        if account_hierarchy:
            cmd.extend(["--account-hierarchy", account_hierarchy])
        
        # Run command
        try:
            # For sheet processing, we need to modify the journal reader to use sheet_name
            # Since the CLI doesn't support sheet_name yet, we'll need to use the script
            print(f"Note: The current CLI processes only the first sheet.")
            print(f"      To process specific sheets, we need the process_multi_sheet.py script")
            print(f"      or modify the file to specify sheet names.")
            print()
            print(f"Alternative: Manually create separate Excel files for each year")
            print(f"            or use process_multi_sheet.py when dependencies are installed.")
            break  # Don't actually run for now
        except Exception as e:
            print(f"❌ Error processing sheet {sheet_name}: {e}")
            continue
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("To process all sheets, use: python3 scripts/process_multi_sheet.py")
    print("Make sure dependencies are installed: pip install -e .")

if __name__ == "__main__":
    main()
