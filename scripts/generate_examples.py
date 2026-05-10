#!/usr/bin/env python3
"""
Generate a synthetic journal workbook for demos (no real financial data).

Writes examples/journal_entry_sample.xlsx with year-named sheets 2020–2024.

Usage from repo root:
    python3 scripts/generate_examples.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / "examples" / "journal_entry_sample.xlsx"

    headers = ["entry_id", "year", "description", "old_type", "amount", "date", "quarter"]

    wb = Workbook()
    wb.remove(wb.active)

    samples_by_year: dict[int, list[tuple]] = {
        2020: [
            ("A-1-101", 2020, "Synthetic OL tuition receipt sample", "OL", 1200.0, date(2020, 1, 12), 1),
            ("I-1-22", 2020, "Synthetic bank interest sample", "结息", 8.55, date(2020, 3, 31), 1),
            ("B-2-7", 2020, "Synthetic expense reimbursement sample", "报销", -340.0, date(2020, 6, 18), 2),
            ("W-1-18", 2020, "Synthetic workshop fee sample", "Workshop-FEE", 880.0, date(2020, 9, 5), 3),
            ("A-3-44", 2020, "Synthetic deposit refund placeholder", "OL-D", -500.0, date(2020, 11, 2), 4),
            ("A-9-1", 2020, "Skipped internal transfer pattern (demo)", "余利宝", 100.0, date(2020, 7, 1), 3),
            ("A-9-2", 2020, "余利宝自动转入", "余利宝", 50.0, date(2020, 7, 2), 3),
            ("B-9-3", 2020, "Zero amount row (skipped in pipeline)", "转账", 0.0, date(2020, 8, 1), 3),
            ("A-9-4", 2020, "Missing type — empty cell (reader marks __MISSING_TYPE__)", None, 25.0, date(2020, 8, 15), 3),
            ("A-9-5", 2020, "Rare synthetic type for NO_MATCH exercise", "RareSynthTypeDemo", 99.0, date(2020, 12, 1), 4),
        ],
        2021: [
            ("A-1-14", 2021, "Synthetic OL row sample", "OL", 650.0, date(2021, 2, 10), 1),
            ("I-2-3", 2021, "Synthetic interest row", "结息", 12.1, date(2021, 5, 20), 2),
            ("B-3-11", 2021, "Synthetic bank fee sample", "收费", -15.0, date(2021, 8, 8), 3),
            ("W-2-9", 2021, "Synthetic workshop income sample", "workshop-fee", 420.0, date(2021, 10, 2), 4),
        ],
        2022: [
            ("A-1-7", 2022, "Synthetic comms expense placeholder", "通讯", -88.0, date(2022, 1, 25), 1),
            ("I-2-1", 2022, "Synthetic interest", "结息", 6.2, date(2022, 4, 30), 2),
            ("B-1-12", 2022, "Synthetic payroll placeholder", "工资", -3200.0, date(2022, 7, 15), 3),
            ("A-4-20", 2022, "Synthetic OL payment sample", "OL", 1500.0, date(2022, 11, 11), 4),
        ],
        2023: [
            ("A-2-11", 2023, "Synthetic OL sample", "OL", 900.0, date(2023, 3, 9), 1),
            ("I-1-5", 2023, "Synthetic interest sample", "结息", 4.4, date(2023, 6, 30), 2),
            ("W-1-7", 2023, "Synthetic transfer placeholder", "转账", -50.0, date(2023, 9, 21), 3),
        ],
        2024: [
            ("A-2-26", 2024, "Synthetic scholarship placeholder", "OL-奖学金", -200.0, date(2024, 1, 18), 1),
            ("B-3-90", 2024, "Synthetic admin server expense demo", "RareSynthAdminDemo", -750.0, date(2024, 4, 12), 2),
            ("I-3-4", 2024, "Synthetic interest", "余利宝收益发放", 3.3, date(2024, 7, 31), 3),
            ("A-4-28", 2024, "Synthetic gathering expense placeholder", "聚餐", -180.0, date(2024, 10, 5), 4),
        ],
    }

    for year in range(2020, 2025):
        ws = wb.create_sheet(str(year))
        ws.append(headers)
        for row in samples_by_year.get(year, []):
            ws.append(list(row))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
