"""
Helpers for validating pipeline output against reference Veritas China Account book files.

Extract yearly report numbers from:
1. Our pipeline output (unified report: Account Summary by Year sheet)
2. Reference Excel files (one per year) - either Ledger-style (CR/DR/Net by account)
   or 报表小结FY-style (category name -> single amount per row).

Compare with tolerance and report differences.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


# Default column mapping for our "Account Summary (by Year)" sheet
OUR_SHEET = "Account Summary (by Year)"
OUR_HEADER_ROW = 3  # 1-based; row 4 in Excel
OUR_COLUMNS = {
    "year": 1,       # A=1
    "ledger_id": 2,
    "account_code": 3,
    "account_name": 4,
    "cr": 5,
    "dr": 6,
    "net": 7,
    "entry_count": 8,
}


def get_yearly_numbers_from_pipeline_output(
    report_path: Path,
    year: int,
) -> dict[str, dict[str, float]]:
    """
    Read our unified report (ledger_output.xlsx) and return yearly numbers for the given year.

    Args:
        report_path: Path to ledger_output.xlsx (unified report).
        year: Year to filter (e.g. 2024).

    Returns:
        Dict keyed by ledger_id (str): {"cr": float, "dr": float, "net": float}.
        Skips the TOTAL row. Uses Ledger ID as key for comparison with reference.
    """
    if not report_path.exists():
        return {}

    df = pd.read_excel(
        report_path,
        sheet_name=OUR_SHEET,
        header=OUR_HEADER_ROW - 1,  # 0-based: row 3 in Excel = index 2
    )
    # Normalize column names (might be "Year", "Ledger ID", etc.)
    df = df.rename(columns=lambda c: str(c).strip() if pd.notna(c) else "")
    # Filter by year (first column is Year)
    if "Year" in df.columns:
        df_year = df[df["Year"] == year].copy()
    else:
        df_year = df[df.iloc[:, 0].astype(str).str.strip() == str(year)].copy()

    # Skip TOTAL row
    df_year = df_year[df_year.iloc[:, 1].astype(str).str.strip().str.upper() != "TOTAL"]

    result: dict[str, dict[str, float]] = {}
    ledger_col = "Ledger ID" if "Ledger ID" in df_year.columns else df_year.columns[OUR_COLUMNS["ledger_id"] - 1]
    cr_col = "CR Amount" if "CR Amount" in df_year.columns else df_year.columns[OUR_COLUMNS["cr"] - 1]
    dr_col = "DR Amount" if "DR Amount" in df_year.columns else df_year.columns[OUR_COLUMNS["dr"] - 1]
    net_col = "Net Amount" if "Net Amount" in df_year.columns else df_year.columns[OUR_COLUMNS["net"] - 1]

    for _, row in df_year.iterrows():
        lid = row.get(ledger_col)
        if pd.isna(lid):
            continue
        key = str(int(lid)) if isinstance(lid, (int, float)) else str(lid).strip()
        result[key] = {
            "cr": float(row.get(cr_col, 0) or 0),
            "dr": float(row.get(dr_col, 0) or 0),
            "net": float(row.get(net_col, 0) or 0),
        }
    return result


def get_ours_by_account_name(report_path: Path, year: int) -> dict[str, dict[str, float]]:
    """
    Same as get_yearly_numbers_from_pipeline_output but keyed by Account Name
    for comparison with 报表小结FY (category-name keyed).
    """
    if not report_path.exists():
        return {}
    df = pd.read_excel(report_path, sheet_name=OUR_SHEET, header=OUR_HEADER_ROW - 1)
    df = df.rename(columns=lambda c: str(c).strip() if pd.notna(c) else "")
    if "Year" not in df.columns:
        return {}
    df_year = df[df["Year"] == year].copy()
    df_year = df_year[df_year.iloc[:, 1].astype(str).str.strip().str.upper() != "TOTAL"]
    result: dict[str, dict[str, float]] = {}
    name_col = "Account Name" if "Account Name" in df_year.columns else df_year.columns[3]
    cr_col = "CR Amount" if "CR Amount" in df_year.columns else df_year.columns[4]
    dr_col = "DR Amount" if "DR Amount" in df_year.columns else df_year.columns[5]
    net_col = "Net Amount" if "Net Amount" in df_year.columns else df_year.columns[6]
    for _, row in df_year.iterrows():
        name = row.get(name_col)
        if pd.isna(name) or not str(name).strip():
            continue
        key = str(name).strip()
        result[key] = {
            "cr": float(row.get(cr_col, 0) or 0),
            "dr": float(row.get(dr_col, 0) or 0),
            "net": float(row.get(net_col, 0) or 0),
        }
    return result


# Sheet name and row/column layout for Veritas 报表小结FY (yearly summary by category)
REFERENCE_SUMMARY_FY_SHEET = "报表小结FY"
# Map our account name -> list of reference row labels to try (reference uses 讲师组委工资, we use 组委工资; 投资收入 vs 投资收益).
# Salary/wage (8月工资) is an expense: match to 组委工资 (expense account), NOT 银行存款 (asset). Signs: expense = negative net, income = positive net.
REFERENCE_NAME_ALIASES = {
    "组委工资": ["组委工资", "讲师组委工资", "讲师工资", "8月工资", "a-1-2 8月工资", "工资"],
    "捐赠收入": ["捐赠收入"],
    "投资收益": ["投资收入", "投资收益"],
    "投资收入": ["投资收入", "投资收益"],
    "运营费用": ["运营费用", "业务活动费用", "组织管理费用"],
}


def _parse_amount(val: Any) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    s = str(val).strip().replace(",", "").replace("¥", "").replace("￥", "")
    m = re.search(r"-?[\d.]+", s)
    return float(m.group(0)) if m else 0.0


def get_yearly_numbers_from_reference_summary_fy(
    reference_path: Path,
    year_label: str = "2024Q1-Q3",
    sheet_name: str = REFERENCE_SUMMARY_FY_SHEET,
) -> dict[str, float]:
    """
    Read reference 报表小结FY sheet: first column = category name, one column = amounts.
    Returns dict[category_name_stripped] = net amount (single number per row).
    """
    if not reference_path.exists():
        return {}
    df = pd.read_excel(reference_path, sheet_name=sheet_name, header=None)
    # Find column that matches year_label (e.g. 2024Q1-Q3, 2024FY)
    col_idx = None
    for c in range(min(12, df.shape[1])):
        for r in range(min(3, df.shape[0])):
            v = df.iloc[r, c]
            if pd.notna(v) and year_label in str(v):
                col_idx = c
                break
        if col_idx is not None:
            break
    if col_idx is None:
        col_idx = 3  # default 2024Q1-Q3 often in col 3
    result: dict[str, float] = {}
    for r in range(1, len(df)):
        label = df.iloc[r, 0]
        if pd.isna(label) or not str(label).strip():
            continue
        name = str(label).strip()
        if name in ("项目名称", "nan", "备注"):
            continue
        result[name] = _parse_amount(df.iloc[r, col_idx])
    return result


def compare_yearly_by_name(
    ours_by_name: dict[str, dict[str, float]],
    reference_net_by_name: dict[str, float],
    tolerance: float = 0.01,
    name_aliases: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    """
    Compare our output (keyed by account name) to reference 报表小结FY (category -> net).
    reference_net_by_name: category name -> single net amount.
    name_aliases: map our name -> list of possible reference names (e.g. 组委工资 -> [组委工资, 讲师组委工资]).
    """
    aliases = name_aliases or REFERENCE_NAME_ALIASES
    diffs: list[dict[str, Any]] = []
    for our_name, our_vals in ours_by_name.items():
        our_net = our_vals.get("net", 0)
        ref_names = [our_name]
        for ref_cat, ref_list in aliases.items():
            if our_name in ref_list or our_name == ref_cat:
                ref_names = [ref_cat] + ref_list
                break
        ref_net = None
        for n in ref_names:
            if n in reference_net_by_name:
                ref_net = reference_net_by_name[n]
                break
        if ref_net is None:
            diffs.append({"account": our_name, "field": "net", "ours": our_net, "reference": None, "message": "Category not in reference (or add alias)"})
            continue
        if abs(our_net - ref_net) > tolerance:
            diffs.append({"account": our_name, "field": "net", "ours": our_net, "reference": ref_net, "diff": our_net - ref_net, "message": f"net: ours={our_net}, ref={ref_net}"})
    for ref_name in reference_net_by_name:
        if ref_name in ("项目名称", "备注", "nan", ""):
            continue
        if not any(ref_name in aliases.get(our_name, [our_name]) or ref_name == our_name for our_name in ours_by_name):
            if abs(reference_net_by_name[ref_name]) > tolerance:
                diffs.append({"account": ref_name, "field": "net", "ours": None, "reference": reference_net_by_name[ref_name], "message": "In reference only (no matching our category)"})
    return diffs


def get_yearly_numbers_from_reference(
    reference_path: Path,
    column_map: dict[str, str | int] | None = None,
    sheet_name: str | int = 0,
) -> dict[str, dict[str, float]]:
    """
    Read reference Veritas China Account book Excel and return per-account CR/DR/Net.

    Args:
        reference_path: Path to reference Excel (e.g. 2024Veritas China Account book.xlsx).
        column_map: Optional mapping: {"account": "Ledger ID" or 0, "cr": "CR" or 1, "dr": "DR", "net": "Net"}.
                    If None, tries to auto-detect columns by common names (CR Amount, DR Amount, Net, etc.).
        sheet_name: Sheet to read (0 = first sheet, or name).

    Returns:
        Dict keyed by account/ledger id: {"cr": float, "dr": float, "net": float}.
    """
    if not reference_path.exists():
        return {}

    df = pd.read_excel(reference_path, sheet_name=sheet_name, header=0)
    df = df.rename(columns=lambda c: str(c).strip())

    # Resolve column names or indices
    def find_col(candidates: list[str]) -> str | None:
        for c in candidates:
            for col in df.columns:
                if c.lower() in str(col).lower():
                    return col
        return None

    if column_map:
        account_col = column_map.get("account")
        cr_col = column_map.get("cr")
        dr_col = column_map.get("dr")
        net_col = column_map.get("net")
        if isinstance(account_col, int):
            account_col = df.columns[account_col] if account_col < len(df.columns) else None
        if isinstance(cr_col, int):
            cr_col = df.columns[cr_col] if cr_col < len(df.columns) else None
        if isinstance(dr_col, int):
            dr_col = df.columns[dr_col] if dr_col < len(df.columns) else None
        if isinstance(net_col, int):
            net_col = df.columns[net_col] if net_col < len(df.columns) else None
    else:
        account_col = find_col(["Ledger ID", "Ledger ID", "Account", "账户", "Code", "科目代码"])
        cr_col = find_col(["CR Amount", "CR", "Credit", "贷方"])
        dr_col = find_col(["DR Amount", "DR", "Debit", "借方"])
        net_col = find_col(["Net Amount", "Net", "余额", "Balance"])

    if not account_col:
        # Fallback: first column as account
        account_col = df.columns[0]
    if not cr_col:
        cr_col = None
    if not dr_col:
        dr_col = None
    if not net_col:
        net_col = None

    result: dict[str, dict[str, float]] = {}
    for _, row in df.iterrows():
        try:
            key = row[account_col]
        except KeyError:
            continue
        if pd.isna(key):
            continue
        key = str(key).strip()
        if not key or key.upper() in ("TOTAL", "NAN", ""):
            continue
        try:
            key = str(int(float(key)))
        except (ValueError, TypeError):
            pass
        def _val(col: str | None) -> float:
            if not col or col not in row.index:
                return 0.0
            v = row[col]
            if pd.isna(v):
                return 0.0
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0

        result[key] = {"cr": _val(cr_col), "dr": _val(dr_col), "net": _val(net_col)}
    return result


def compare_yearly(
    ours: dict[str, dict[str, float]],
    reference: dict[str, dict[str, float]],
    tolerance: float = 0.01,
    fields: tuple[str, ...] = ("cr", "dr", "net"),
) -> list[dict[str, Any]]:
    """
    Compare our yearly numbers to reference. Returns list of differences.

    Each item: {"account": str, "field": str, "ours": float, "reference": float, "diff": float, "message": str}.
    """
    diffs: list[dict[str, Any]] = []
    all_accounts = set(ours) | set(reference)

    for account in sorted(all_accounts):
        o = ours.get(account, {"cr": 0, "dr": 0, "net": 0})
        r = reference.get(account, {"cr": 0, "dr": 0, "net": 0})
        if account not in reference:
            diffs.append({
                "account": account,
                "field": "all",
                "ours": sum(o[f] for f in fields),
                "reference": None,
                "diff": None,
                "message": "In our output only (not in reference)",
            })
            continue
        if account not in ours:
            diffs.append({
                "account": account,
                "field": "all",
                "ours": None,
                "reference": sum(r[f] for f in fields),
                "diff": None,
                "message": "In reference only (missing in our output)",
            })
            continue
        for field in fields:
            a_val = o.get(field, 0)
            b_val = r.get(field, 0)
            diff = abs(a_val - b_val)
            if diff > tolerance:
                diffs.append({
                    "account": account,
                    "field": field,
                    "ours": a_val,
                    "reference": b_val,
                    "diff": a_val - b_val,
                    "message": f"{field.upper()}: ours={a_val}, ref={b_val}, diff={a_val - b_val}",
                })
    return diffs
