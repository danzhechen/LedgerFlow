#!/usr/bin/env python3
"""
Create a Type mapping from Chinese types to OL/CR/DR format.

This analyzes the journal data and suggests mappings.
"""

import pandas as pd
from pathlib import Path

def analyze_type_mapping(journal_file):
    """Analyze Type values and suggest mappings."""
    df = pd.read_excel(journal_file)
    
    print("=" * 80)
    print("TYPE MAPPING ANALYSIS")
    print("=" * 80)
    
    type_counts = df['old_type'].value_counts()
    
    print(f"\n📊 Type Distribution ({len(type_counts)} unique types):")
    for type_val, count in type_counts.items():
        print(f"  - {type_val}: {count} entries")
    
    # Suggest mappings based on patterns
    print(f"\n💡 Suggested Mappings:")
    print(f"  (Based on common patterns)")
    
    suggestions = {
        'OL': ['OL', 'OL-D'],  # Already in correct format
        'CR': ['工资', '组委工资', '运营', '书院运营'],  # Income/credit types
        'DR': ['书院学费', '书院报销', '书院'],  # Expense/debit types
        '余利宝': ['余利宝', '余利宝收益发放', '支付宝自动转入余利宝', '余利宝转出到支付宝'],  # Special type
    }
    
    for target, sources in suggestions.items():
        found = [t for t in type_counts.index if t in sources]
        if found:
            print(f"\n  {target}:")
            for f in found:
                print(f"    - '{f}' ({type_counts[f]} entries)")
    
    # Create mapping dictionary
    type_mapping = {}
    for target, sources in suggestions.items():
        for source in sources:
            if source in type_counts.index:
                type_mapping[source] = target
    
    print(f"\n📝 Type Mapping Dictionary:")
    for source, target in sorted(type_mapping.items()):
        print(f"  '{source}' → '{target}'")
    
    return type_mapping

if __name__ == '__main__':
    journal_file = Path('examples/journal_2024_transformed.xlsx')
    
    if not journal_file.exists():
        print(f"❌ File not found: {journal_file}")
        print("   Run transform_journal_2024.py first!")
        exit(1)
    
    mapping = analyze_type_mapping(journal_file)
    
    print(f"\n💡 Next Steps:")
    print(f"  1. Review the suggested mappings above")
    print(f"  2. Update transform_journal_2024.py to apply type mapping")
    print(f"  3. Or create a separate mapping rules file for Chinese types")









