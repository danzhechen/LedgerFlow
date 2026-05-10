#!/usr/bin/env python3
"""
Generate rules from OLD types in the mapping file.

This script generates rules that match against OLD types (which is what
the journal entries actually have), not NEW types.

Also maps old account codes to new account hierarchy codes.
"""

import pandas as pd
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from veritas_accounting.models.account_loader import AccountHierarchyLoader

def map_account_code(old_code: str, hierarchy) -> str:
    """
    Map old account code to new account hierarchy code.
    
    Args:
        old_code: Old account code/name from mapping file
        hierarchy: AccountHierarchy object
        
    Returns:
        New account code or original if not found
    """
    if not old_code or pd.isna(old_code):
        return old_code
    
    old_code_str = str(old_code).strip()
    
    # Try exact code match
    account = hierarchy.get_account(old_code_str)
    if account:
        return account.code
    
    # Try exact name match
    account = hierarchy.get_account_by_name(old_code_str)
    if account:
        return account.code
    
    # Try partial name matching (common patterns)
    for acc in hierarchy.get_all_accounts():
        # Check if old code contains account name or vice versa
        if acc.name in old_code_str or old_code_str in acc.name:
            return acc.code
    
    # Common mappings based on patterns in old codes
    mapping_patterns = [
        # Bank/Deposit accounts
        (['银行存款', '銀行存款', '1002'], '银行存款'),
        (['其他货币资金', '其他貨幣資金', '1009'], '其他货币资金'),
        # Income accounts
        (['收入OL', 'OL收入', '4301'], '收入OL'),
        (['收入SC', 'SC收入', '4201'], '收入SC'),
        (['捐赠收入', '捐贈收入', '4101'], '捐赠收入'),
        (['投资收益', '投資收益', '4601'], '投资收益'),
        # Expense accounts
        (['支出OL讲师', 'OL讲师工资', '讲师工资', '5401', '5501', 'core讲师工资'], '支出OL讲师'),
        (['支出OL组委', '组委工资', '5601'], '支出OL组委'),
        (['支出SC运营', 'SC运营', '5001', '5101', '业务活动成本'], '支出SC运营'),
        (['支出SC讲师'], '支出SC讲师'),
        (['支出SC组委'], '支出SC组委'),
        (['支出内容运营', '内容运营'], '支出内容运营'),
        (['管理费用', '管理費用', '5201'], '管理费用'),
        (['社群维护'], '社群维护'),
        (['宣传推广'], '宣传推广'),
        # Payable accounts
        (['应付OL押金', 'OL押金', '2301'], '应付OL押金'),
        (['应付OL奖助', 'OL奖助', '2302'], '应付OL奖助'),
        (['应付SC押金', 'SC押金', '2201'], '应付SC押金'),
        (['应付SC奖助', 'SC奖助', '2202'], '应付SC奖助'),
        (['应付税款', '应交税金', '2206', '2209', '其他应付款', '其他應付款'], '应付税款'),
        # Other
        (['短期借款', '2101'], '短期借款'),
        (['权益变动'], '权益变动'),
    ]
    
    for patterns, target_name in mapping_patterns:
        if any(pattern in old_code_str for pattern in patterns):
            account = hierarchy.get_account_by_name(target_name)
            if account:
                return account.code
    
    # If no match found, return original (will cause validation error but that's OK)
    return old_code_str


def generate_rules_from_old_types(input_path, output_path=None, hierarchy_file=None):
    """
    Generate rules from OLD section of mapping file.
    
    Args:
        input_path: Path to mapping file (账目分类明细.xlsx)
        output_path: Output path for rules file
        hierarchy_file: Path to account hierarchy file (for code mapping)
    """
    print(f"📖 Reading {input_path}...")
    df = pd.read_excel(input_path, sheet_name='journal_to_ledger')
    
    print(f"   Original shape: {df.shape}")
    
    # Load account hierarchy for code mapping
    hierarchy = None
    if hierarchy_file:
        try:
            loader = AccountHierarchyLoader()
            hierarchy = loader.load_from_excel(hierarchy_file, sheet_name='ledger_new')
            print(f"   ✓ Loaded account hierarchy ({len(hierarchy.get_all_accounts())} accounts)")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not load account hierarchy: {e}")
            print(f"      Rules will use original account codes (may cause validation errors)")
    
    # Column structure:
    # OLD section: columns 0-3 (year, type, cr_ledger, dr_ledger)
    # NEW section: columns 4-6 (type, cr_ledger, dr_ledger)
    
    # Get column names
    col_names = df.columns.tolist()
    
    # OLD section columns
    old_year_col = col_names[0]      # OLD: year
    old_type_col = col_names[1]      # OLD: type
    old_cr_col = col_names[2]        # OLD: cr_ledger
    old_dr_col = col_names[3]        # OLD: dr_ledger
    
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
        
        # Skip if no OLD type
        if not old_type or pd.isna(old_type):
            continue
        
        # Skip if no ledger mapping
        if not old_cr and not old_dr:
            continue
        
        # Use OLD type for matching (this is what journal entries have)
        matching_type = str(old_type).strip()
        
        # Create rule for CR (credit) side
        if old_cr and pd.notna(old_cr) and str(old_cr).strip() and str(old_cr) != 'nan':
            # Match against OLD type (what journal entries actually have)
            # Don't add year condition - let rules match across all years
            # (Year-specific rules can be added later if needed)
            condition = f'old_type == "{matching_type}"'
            
            # Map account code to hierarchy code
            mapped_cr = map_account_code(old_cr, hierarchy) if hierarchy else str(old_cr).strip()
            
            rules.append({
                'rule_id': f'R-{rule_id_counter:03d}-CR',
                'condition': condition,
                'account_code': mapped_cr,
                'priority': 10,
                'old_type': matching_type,
                'new_type': matching_type,
                'description': f'Map {matching_type} to {mapped_cr} (CR)',
                'generates_multiple': False,
                'ledger_type': 'CR'
            })
            rule_id_counter += 1
        
        # Create rule for DR (debit) side
        if old_dr and pd.notna(old_dr) and str(old_dr).strip() and str(old_dr) != 'nan':
            # Match against OLD type (what journal entries actually have)
            # Don't add year condition - let rules match across all years
            condition = f'old_type == "{matching_type}"'
            
            # Map account code to hierarchy code
            mapped_dr = map_account_code(old_dr, hierarchy) if hierarchy else str(old_dr).strip()
            
            rules.append({
                'rule_id': f'R-{rule_id_counter:03d}-DR',
                'condition': condition,
                'account_code': mapped_dr,
                'priority': 10,
                'old_type': matching_type,
                'new_type': matching_type,
                'description': f'Map {matching_type} to {mapped_dr} (DR)',
                'generates_multiple': False,
                'ledger_type': 'DR'
            })
            rule_id_counter += 1
    
    # Create DataFrame
    rules_df = pd.DataFrame(rules)
    
    print(f"\n✅ Generated {len(rules)} mapping rules from OLD types")
    print(f"   Rules match against OLD types (what journal entries actually have)")
    print(f"\n📝 Sample rules:")
    print(rules_df.head(10).to_string())
    
    # Save
    if output_path is None:
        input_file = Path(input_path)
        output_path = input_file.parent / f"{input_file.stem}_old_type_rules.xlsx"
    
    print(f"\n💾 Saving to {output_path}...")
    rules_df.to_excel(output_path, index=False)
    print(f"   ✅ Saved {len(rules)} rules")
    
    return rules_df, output_path

if __name__ == '__main__':
    input_file = Path('账目分类明细.xlsx')
    hierarchy_file = input_file  # Same file contains hierarchy
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        exit(1)
    
    try:
        rules_df, output_file = generate_rules_from_old_types(input_file, hierarchy_file=hierarchy_file)
        print(f"\n🎉 Success! Rules saved to: {output_file}")
        print(f"\n💡 Now use this rules file:")
        print(f"   veritas-accounting process --input examples/journal_entry_sample.xlsx --rules {output_file}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
