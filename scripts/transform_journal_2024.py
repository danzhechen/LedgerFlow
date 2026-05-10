#!/usr/bin/env python3
"""
Transform journal_2024.xlsx to LedgerFlow format.

This script converts the Chinese column format to the standard LedgerFlow format:
- Maps Chinese columns to English
- Combines 收入/支出 into amount column
- Extracts year from date
- Creates entry_id from ID
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def transform_journal_2024(input_path, output_path=None):
    """
    Transform journal_2024.xlsx to LedgerFlow format.
    
    Args:
        input_path: Path to journal_2024.xlsx
        output_path: Path to save transformed file (default: input_path with _transformed suffix)
    """
    print(f"📖 Reading {input_path}...")
    df = pd.read_excel(input_path)
    
    print(f"   Original shape: {df.shape}")
    print(f"   Original columns: {list(df.columns)}")
    
    # Filter out rows without ID (summary rows)
    df = df[df['ID'].notna()].copy()
    print(f"   Rows with ID: {len(df)}")
    
    # Create transformed dataframe
    transformed = pd.DataFrame()
    
    # Map entry_id from ID
    transformed['entry_id'] = df['ID'].astype(str)
    
    # Map old_type from Type with Chinese to OL/CR/DR mapping
    type_mapping = {
        # Already correct
        'OL': 'OL',
        'OL-D': 'OL',
        'OL-奖学金': 'OL',
        'OL-工资': 'OL',
        'OL-讲师工资': 'OL',
        'OL押金': 'OL',
        # Income/Credit types
        '工资': 'CR',
        '组委工资': 'CR',
        '书院工资': 'CR',
        '运营': 'CR',
        '书院运营': 'CR',
        '捐赠收入': 'CR',
        '结息': 'CR',
        # Expense/Debit types
        '书院学费': 'DR',
        '书院报销': 'DR',
        '书院': 'DR',
        '书院住宿': 'DR',
        '书院场地': 'DR',
        '研讨屋': 'DR',
        '聚餐': 'DR',
        '播客': 'DR',
        # Special types - map 余利宝 to OL for now (can be customized)
        '余利宝': 'OL',
        '余利宝收益发放': 'OL',
        '支付宝自动转入余利宝': 'OL',
        '余利宝转出到支付宝': 'OL',
        '对公->支付宝': 'OL',
        'to支付宝': 'OL',
        # Default fallback
        '/': 'OL',
        '？': 'OL',
        '换汇-3000刀': 'OL',
    }
    
    transformed['old_type'] = df['Type'].astype(str).map(type_mapping).fillna('OL')
    
    # Map description from 摘要 - ensure it's never empty (required field)
    transformed['description'] = df['摘要'].fillna('无描述').astype(str)
    # Replace empty strings with default
    transformed['description'] = transformed['description'].replace('', '无描述')
    
    # Map date from 日期
    transformed['date'] = pd.to_datetime(df['日期'], errors='coerce')
    
    # Extract year from date
    transformed['year'] = transformed['date'].dt.year
    
    # Combine 收入 and 支出 into amount
    # Income (收入) = positive, Expense (支出) = negative
    income = df['收入'].fillna(0)
    expense = df['支出'].fillna(0)
    transformed['amount'] = income - expense
    
    # Add optional quarter if date is available
    transformed['quarter'] = transformed['date'].dt.quarter
    
    # Add optional notes (combine multiple fields)
    notes_parts = []
    if '领款人' in df.columns:
        notes_parts.append(df['领款人'].fillna('').astype(str))
    if '对方账户' in df.columns:
        notes_parts.append(df['对方账户'].fillna('').astype(str))
    
    if notes_parts:
        transformed['notes'] = notes_parts[0] if len(notes_parts) == 1 else (
            notes_parts[0] + ' | ' + notes_parts[1]
        )
    else:
        transformed['notes'] = ''
    
    # Clean up: remove rows with invalid dates or amounts
    initial_count = len(transformed)
    transformed = transformed[
        transformed['date'].notna() & 
        transformed['amount'].notna() &
        (transformed['amount'] != 0)
    ].copy()
    
    removed_count = initial_count - len(transformed)
    if removed_count > 0:
        print(f"   ⚠️  Removed {removed_count} rows with invalid dates or zero amounts")
    
    # Reorder columns to match expected format
    column_order = ['entry_id', 'year', 'description', 'old_type', 'amount', 'date', 'quarter', 'notes']
    transformed = transformed[[col for col in column_order if col in transformed.columns]]
    
    # Format date for Excel
    transformed['date'] = transformed['date'].dt.date
    
    print(f"\n✅ Transformation complete!")
    print(f"   Final shape: {transformed.shape}")
    print(f"   Final columns: {list(transformed.columns)}")
    
    # Show sample
    print(f"\n📝 Sample transformed data:")
    print(transformed.head(5).to_string())
    
    # Statistics
    print(f"\n📊 Statistics:")
    print(f"   - Total entries: {len(transformed)}")
    print(f"   - Year range: {transformed['year'].min()} - {transformed['year'].max()}")
    print(f"   - Amount range: {transformed['amount'].min():.2f} - {transformed['amount'].max():.2f}")
    print(f"   - Type distribution:")
    type_counts = transformed['old_type'].value_counts().head(10)
    for type_val, count in type_counts.items():
        print(f"     - {type_val}: {count}")
    
    # Save to file
    if output_path is None:
        input_file = Path(input_path)
        output_path = input_file.parent / f"{input_file.stem}_transformed{input_file.suffix}"
    
    print(f"\n💾 Saving to {output_path}...")
    transformed.to_excel(output_path, index=False)
    print(f"   ✅ Saved {len(transformed)} entries")
    
    return transformed, output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/transform_journal_2024.py <path/to/raw_journal_2024.xlsx>")
        print("  (Raw-format workbook is not shipped in the repo; keep yours local.)")
        sys.exit(1)
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    try:
        transformed_df, output_file = transform_journal_2024(input_file)
        print(f"\n🎉 Success! Transformed file saved to: {output_file}")
        print(f"\n💡 Next steps:")
        print(f"   1. Review the transformed file: {output_file}")
        print(f"   2. Update mapping rules if needed (Chinese Type values)")
        print(f"   3. Run: ledgerflow process --input {output_file} --rules examples/mapping_rules_sample.xlsx")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)









