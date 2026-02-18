#!/usr/bin/env python3
"""
Diagnostic script to analyze ledger output and identify amount duplication issues.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

def analyze_ledger_output(ledger_file: str):
    """Analyze ledger output to identify issues."""
    
    print(f"📊 Analyzing ledger output: {ledger_file}\n")
    
    # Read ledger output
    df = pd.read_excel(ledger_file, sheet_name=0)
    
    print(f"Total ledger entries: {len(df)}")
    print(f"Columns: {list(df.columns)}\n")
    
    # Check for amount column
    amount_col = None
    for col in ['amount', 'Amount', 'AMOUNT']:
        if col in df.columns:
            amount_col = col
            break
    
    if not amount_col:
        print("❌ Could not find amount column!")
        print(f"Available columns: {df.columns.tolist()}")
        return
    
    print(f"Using amount column: {amount_col}\n")
    
    # Total amount
    total_amount = df[amount_col].sum()
    print(f"📈 Total amount in ledger: {total_amount:,.2f}")
    
    # Group by source entry
    if 'source_entry_id' in df.columns or 'Source Entry ID' in df.columns:
        source_col = 'source_entry_id' if 'source_entry_id' in df.columns else 'Source Entry ID'
        
        # Count entries per source
        entries_per_source = df.groupby(source_col).size()
        amounts_per_source = df.groupby(source_col)[amount_col].sum()
        
        print(f"\n📋 Entries per source journal entry:")
        print(f"   Average: {entries_per_source.mean():.2f}")
        print(f"   Max: {entries_per_source.max()}")
        print(f"   Min: {entries_per_source.min()}")
        
        # Find sources with multiple entries
        multi_entry_sources = entries_per_source[entries_per_source > 1]
        if len(multi_entry_sources) > 0:
            print(f"\n⚠️  Found {len(multi_entry_sources)} source entries that generated multiple ledger entries:")
            print(f"   These may be causing amount duplication!\n")
            
            # Show top 10
            print("   Top 10 sources with most ledger entries:")
            for source_id, count in multi_entry_sources.head(10).items():
                total = amounts_per_source[source_id]
                print(f"      {source_id}: {count} ledger entries, total amount: {total:,.2f}")
            
            # Check if amounts are duplicated
            print(f"\n   Checking for amount duplication...")
            duplicated_amounts = 0
            for source_id in multi_entry_sources.head(20).index:
                source_df = df[df[source_col] == source_id]
                amounts = source_df[amount_col].tolist()
                # Check if all amounts are the same (duplication)
                if len(set(amounts)) == 1 and len(amounts) > 1:
                    duplicated_amounts += 1
                    if duplicated_amounts <= 5:
                        print(f"      ⚠️  {source_id}: {len(amounts)} entries all with amount {amounts[0]:,.2f}")
            
            if duplicated_amounts > 0:
                print(f"\n   ❌ Found {duplicated_amounts} source entries with duplicated amounts!")
                print(f"   This is the problem - each matching rule creates a ledger entry with the FULL amount.")
                print(f"   For double-entry bookkeeping, amounts should be split, not duplicated.\n")
    
    # Group by account
    if 'account_code' in df.columns or 'Account Code' in df.columns:
        account_col = 'account_code' if 'account_code' in df.columns else 'Account Code'
        account_totals = df.groupby(account_col)[amount_col].sum().sort_values(ascending=False)
        
        print(f"\n💰 Top 10 accounts by total amount:")
        for account, total in account_totals.head(10).items():
            print(f"   {account}: {total:,.2f}")
    
    # Sample entries
    print(f"\n📝 Sample ledger entries (first 5):")
    print(df.head(5).to_string())
    
    print(f"\n💡 Explanation:")
    print(f"   - Each journal entry can match multiple rules (e.g., CR and DR rules)")
    print(f"   - Currently, each matching rule creates a ledger entry with the FULL journal amount")
    print(f"   - This causes amounts to be duplicated/multiplied")
    print(f"   - For proper double-entry bookkeeping, amounts should be split between CR/DR")

if __name__ == '__main__':
    ledger_file = Path('output/ledger_output.xlsx')
    if not ledger_file.exists():
        ledger_file = Path('output/old_ledger_output.xlsx')
    
    if ledger_file.exists():
        analyze_ledger_output(str(ledger_file))
    else:
        print(f"❌ Could not find ledger output file in output/ directory")







