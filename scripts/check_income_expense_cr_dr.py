#!/usr/bin/env python3
"""
Check that 收入 (4xxx) and 支出 (5xxx) accounts have correct CR/DR assignment.

For correct 期末−期初 = 收入−支出:
- 收入 accounts should typically have CR > DR (net positive).
- 支出 accounts should typically have DR > CR (net negative).

If you see 收入 with DR > CR or 支出 with CR > DR, the mapping rules may have
CR/DR swapped for that account. Fix the rules file (journal_to_ledger or
账目分类明细_ledger_rules), not the report.

Usage:
  python scripts/check_income_expense_cr_dr.py --sheet 2023
  python scripts/check_income_expense_cr_dr.py --sheet 2024 --year 2024
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import click
from veritas_accounting.config.settings import AppConfig, InputConfig, OutputConfig, ValidationConfig
from veritas_accounting.models.account_loader import AccountHierarchyLoader
from veritas_accounting.transformation.aggregator import QuarterlyAggregator
@click.command()
@click.option("--sheet", default="2023", help="Journal sheet name (e.g. 2023, 2024)")
@click.option("--journal", "-i", type=click.Path(exists=True), default="examples/journal_entry_2020_2024.xlsx")
@click.option("--rules", "-r", type=click.Path(exists=True), default="账目分类明细_ledger_rules.xlsx")
@click.option("--hierarchy", "-a", type=click.Path(exists=True), default="账目分类明细.xlsx")
def main(sheet: str, journal: str, rules: str, hierarchy: str) -> None:
    config = AppConfig(
        input=InputConfig(
            journal_file=journal,
            rules_file=rules,
            account_hierarchy_file=hierarchy,
        ),
        output=OutputConfig(directory="output/_check"),
        validation=ValidationConfig(level="strict", auto_fix_enabled=False),
        sheet_name=sheet,
    )
    from veritas_accounting.excel.journal_reader import JournalEntryReader
    from veritas_accounting.excel.rule_reader import MappingRuleReader
    from veritas_accounting.transformation.journal_to_ledger import JournalToLedgerTransformer

    journal_entries, _ = JournalEntryReader(sheet_name=sheet).read_journal_entries(config.input.journal_file)
    if not journal_entries:
        click.echo(f"No journal entries for sheet {sheet!r}")
        return
    rule_reader = MappingRuleReader()
    path = Path(config.input.rules_file)
    hierarchy_path = Path(config.input.account_hierarchy_file or "")
    use_jtl = path.exists() and hierarchy_path.exists() and path.resolve() == hierarchy_path.resolve()
    if use_jtl:
        try:
            loaded_rules, _ = rule_reader.read_rules_from_journal_to_ledger(config.input.rules_file)
        except Exception:
            loaded_rules, _ = rule_reader.read_rules(config.input.rules_file)
    else:
        loaded_rules, _ = rule_reader.read_rules(config.input.rules_file)
    hierarchy_obj = AccountHierarchyLoader().load_from_excel(config.input.account_hierarchy_file, "ledger_new")
    transformer = JournalToLedgerTransformer(loaded_rules, hierarchy_obj)
    ledger_entries, _ = transformer.transform(journal_entries)

    aggregator = QuarterlyAggregator(hierarchy_obj)
    aggs = aggregator.aggregate(ledger_entries)

    # Group by account and sum over all quarters
    from collections import defaultdict
    from decimal import Decimal

    by_account: dict[str, dict] = defaultdict(lambda: {"cr": Decimal("0"), "dr": Decimal("0"), "name": "", "first": ""})
    for a in aggs:
        acc = hierarchy_obj.get_account(a.account_code) or hierarchy_obj.get_account_by_name(a.account_code)
        if not acc or not acc.code.strip():
            continue
        first = acc.code.strip()[0]
        if first not in ("4", "5"):
            continue
        key = a.account_code
        by_account[key]["cr"] += a.cr_amount
        by_account[key]["dr"] += a.dr_amount
        by_account[key]["name"] = acc.name
        by_account[key]["first"] = first

    click.echo(f"Sheet: {sheet} | Ledger entries: {len(ledger_entries)}\n")
    click.echo("收入 (4xxx) and 支出 (5xxx) accounts — CR/DR totals (all quarters):")
    click.echo("-" * 70)
    for code in sorted(by_account.keys(), key=lambda c: (by_account[c]["first"], c)):
        d = by_account[code]
        cr, dr = float(d["cr"]), float(d["dr"])
        net = cr - dr
        typ = "收入" if d["first"] == "4" else "支出"
        ok = (d["first"] == "4" and cr >= dr) or (d["first"] == "5" and dr >= cr)
        flag = "" if ok else "  ⚠️  check CR/DR in rules"
        click.echo(f"  {code} {d['name']} ({typ}): CR={cr:>12,.2f}  DR={dr:>12,.2f}  Net={net:>12,.2f}{flag}")
    click.echo("-" * 70)
    raw_sum = sum(float(by_account[k]["cr"]) - float(by_account[k]["dr"]) for k in by_account)
    click.echo(f"  Result (收入−支出) raw sum = {raw_sum:,.2f}")
    click.echo("\nIf 小结 期末−期初 has the opposite sign, fix mapping rules: 收入=CR, 支出=DR.")


if __name__ == "__main__":
    main()
