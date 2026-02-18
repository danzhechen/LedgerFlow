#!/usr/bin/env python3
"""
Convert 账目分类明细.xlsx to LedgerFlow mapping rules format.

Your file has:
- OLD column: year, type (old_type)
- NEW column: type, cr_ledger, dr_ledger
- Mapping from old types to new ledger accounts

This script converts it to LedgerFlow format:
- rule_id, condition, account_code, priority, old_type, description
"""

import pandas as pd
import sys
from pathlib import Path

def convert_mapping_file(input_path, output_path=None):
    """
    Convert 账目分类明细.xlsx to LedgerFlow mapping rules format.
    """
    print(f"📖 Reading {input_path}...")
    df = pd.read_excel(input_path, header=0)
    
    print(f"   Original shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    # The file structure:
    # Row 0: Headers (year, type, cr_ledger, dr_ledger, type, cr_ledger, dr_ledger, description, ...)
    # Row 1+: Data rows
    
    # Column structure:
    # OLD section: columns 0-3 (year, type, cr_ledger, dr_ledger)
    # NEW section: columns 4-6 (type, cr_ledger, dr_ledger)
    # Additional: column 7+ (description, etc.)
    
    # Get column names
    col_names = df.columns.tolist()
    
    # OLD section columns (indices 0-3)
    old_year_col = col_names[0]      # OLD: year
    old_type_col = col_names[1]      # OLD: type
    old_cr_col = col_names[2]        # OLD: cr_ledger
    old_dr_col = col_names[3]        # OLD: dr_ledger
    
    # NEW section columns (indices 4-6)
    new_type_col = col_names[4]      # NEW: type
    new_cr_col = col_names[5]        # NEW: cr_ledger
    new_dr_col = col_names[6]        # NEW: dr_ledger
    
    print(f"\n   Detected columns:")
    print(f"   OLD section: {old_year_col}, {old_type_col}, {old_cr_col}, {old_dr_col}")
    print(f"   NEW section: {new_type_col}, {new_cr_col}, {new_dr_col}")
    
    # Skip header row (row 0), process from row 1
    data_df = df.iloc[1:].copy()
    
    # Create mapping rules
    rules = []
    rule_id_counter = 1
    
    for idx, row in data_df.iterrows():
        # Skip completely empty rows
        if row.isna().all():
            continue
        
        # Extract OLD section data
        old_year = row[old_year_col] if pd.notna(row[old_year_col]) else None
        old_type = row[old_type_col] if pd.notna(row[old_type_col]) else None
        old_cr = row[old_cr_col] if pd.notna(row[old_cr_col]) else None
        old_dr = row[old_dr_col] if pd.notna(row[old_dr_col]) else None
        
        # Extract NEW section data
        new_type = row[new_type_col] if pd.notna(row[new_type_col]) else None
        new_cr = row[new_cr_col] if pd.notna(row[new_cr_col]) else None
        new_dr = row[new_dr_col] if pd.notna(row[new_dr_col]) else None
        
        # Use NEW section if available, otherwise use OLD section
        cr_ledger = new_cr if new_cr else old_cr
        dr_ledger = new_dr if new_dr else old_dr
        type_val = new_type if new_type else old_type
        
        # Skip if no NEW type (we only care about NEW section now)
        if not new_type or pd.isna(new_type):
            continue
        
        # Skip if no ledger mapping in NEW section
        if not new_cr and not new_dr:
            continue
        
        # Use NEW type for matching (journal entries will have NEW types in old_type column)
        matching_type = str(new_type).strip()
        
        # Create rule for CR (credit) side
        if cr_ledger and pd.notna(cr_ledger) and str(cr_ledger).strip() and str(cr_ledger) != 'nan':
            condition_parts = []
            # Match against NEW type (journal entries use NEW types as old_type)
            condition_parts.append(f'old_type == "{matching_type}"')
            # No year conditions - assume all entries are after 2025
            
            condition = ' and '.join(condition_parts)
            
            rules.append({
                'rule_id': f'R-{rule_id_counter:03d}-CR',
                'condition': condition,
                'account_code': str(cr_ledger).strip(),
                'priority': 10,
                'old_type': matching_type,  # Store NEW type as old_type for reference
                'new_type': matching_type,
                'description': f'Map {matching_type} to {cr_ledger} (CR)',
                'generates_multiple': False,
                'ledger_type': 'CR'  # Track CR/DR
            })
            rule_id_counter += 1
        
        # Create rule for DR (debit) side
        if dr_ledger and pd.notna(dr_ledger) and str(dr_ledger).strip() and str(dr_ledger) != 'nan':
            condition_parts = []
            # Match against NEW type (journal entries use NEW types as old_type)
            condition_parts.append(f'old_type == "{matching_type}"')
            # No year conditions - assume all entries are after 2025
            
            condition = ' and '.join(condition_parts)
            
            rules.append({
                'rule_id': f'R-{rule_id_counter:03d}-DR',
                'condition': condition,
                'account_code': str(dr_ledger).strip(),
                'priority': 10,
                'old_type': matching_type,  # Store NEW type as old_type for reference
                'new_type': matching_type,
                'description': f'Map {matching_type} to {dr_ledger} (DR)',
                'generates_multiple': False,
                'ledger_type': 'DR'  # Track CR/DR
            })
            rule_id_counter += 1
    
    # Create DataFrame
    rules_df = pd.DataFrame(rules)
    
    print(f"\n✅ Converted {len(rules)} mapping rules (NEW section only)")
    print(f"   Rules match against NEW types (used as old_type in journal entries)")
    print(f"\n📝 Sample rules:")
    print(rules_df.head(10).to_string())
    
    # Save
    if output_path is None:
        input_file = Path(input_path)
        output_path = input_file.parent / f"{input_file.stem}_ledger_rules.xlsx"
    
    print(f"\n💾 Saving to {output_path}...")
    rules_df.to_excel(output_path, index=False)
    print(f"   ✅ Saved {len(rules)} rules")
    
    return rules_df, output_path

if __name__ == '__main__':
    input_file = Path('账目分类明细.xlsx')
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    try:
        rules_df, output_file = convert_mapping_file(input_file)
        print(f"\n🎉 Success! Converted mapping rules saved to: {output_file}")
        print(f"\n💡 Now you can use:")
        print(f"   veritas-accounting process --input examples/test_journal_new.xlsx --rules {output_file} --output ./output")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
