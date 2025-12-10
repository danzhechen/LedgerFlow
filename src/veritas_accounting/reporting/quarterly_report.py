"""Quarterly aggregation report generation for veritas-accounting."""

from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.transformation.aggregator import (
    QuarterlyAggregator,
    QuarterlyAggregation,
    HierarchicalTotals,
)
from veritas_accounting.utils.exceptions import ExcelIOError


class QuarterlyReportGenerator:
    """
    Generates quarterly aggregation reports in Excel format.

    Creates professional Excel files with quarterly totals, hierarchical summaries,
    and statistics ready for financial reporting.
    """

    # Color scheme
    COLOR_HEADER = "2C3E50"  # Dark blue-gray
    COLOR_TOTAL = "3498DB"  # Blue
    COLOR_QUARTER1 = "E74C3C"  # Red
    COLOR_QUARTER2 = "F39C12"  # Orange
    COLOR_QUARTER3 = "2ECC71"  # Green
    COLOR_QUARTER4 = "9B59B6"  # Purple

    def __init__(
        self, account_hierarchy: AccountHierarchy | None = None
    ) -> None:
        """
        Initialize QuarterlyReportGenerator.

        Args:
            account_hierarchy: AccountHierarchy object (optional, for hierarchical organization)
        """
        self.account_hierarchy = account_hierarchy
        self.aggregator = QuarterlyAggregator(account_hierarchy)

    def generate(
        self,
        ledger_entries: list[LedgerEntry],
        output_path: Path | str,
        include_charts: bool = True,
    ) -> None:
        """
        Generate quarterly aggregation report Excel file.

        Args:
            ledger_entries: List of LedgerEntry objects
            output_path: Path to output Excel file
            include_charts: Whether to include charts (default: True)

        Raises:
            ExcelIOError: If generation fails
        """
        output_path = Path(output_path)

        try:
            wb = Workbook()
            wb.remove(wb.active)  # Remove default sheet

            # Generate aggregations
            aggregations = self.aggregator.aggregate(ledger_entries)
            level_totals = self.aggregator.aggregate_by_level(ledger_entries)

            # Create sheets
            self._create_quarterly_totals_sheet(wb, aggregations)
            self._create_hierarchy_summary_sheet(wb, level_totals)
            self._create_statistics_sheet(wb, ledger_entries, aggregations)

            # Add charts if requested
            if include_charts:
                self._add_charts(wb, aggregations)

            # Save workbook
            output_path.parent.mkdir(parents=True, exist_ok=True)
            wb.save(output_path)

        except Exception as e:
            raise ExcelIOError(
                f"Failed to generate quarterly report: {output_path}. Error: {e}"
            ) from e

    def _create_quarterly_totals_sheet(
        self, wb: Workbook, aggregations: list[QuarterlyAggregation]
    ) -> None:
        """Create quarterly totals sheet."""
        ws = wb.create_sheet("Quarterly Totals", 0)

        # Title
        ws["A1"] = "Quarterly Aggregation Totals"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:G1")

        # Headers
        headers = [
            "Account Code",
            "Account Path",
            "Level",
            "Quarter",
            "Year",
            "Total Amount",
            "Entry Count",
        ]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color=self.COLOR_HEADER,
                end_color=self.COLOR_HEADER,
                fill_type="solid",
            )
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

        # Group by quarter and year for comparison
        by_quarter: dict[tuple[int, int], list[QuarterlyAggregation]] = {}
        for agg in aggregations:
            key = (agg.quarter, agg.year)
            if key not in by_quarter:
                by_quarter[key] = []
            by_quarter[key].append(agg)

        # Write data
        row = 4
        for (quarter, year), aggs in sorted(by_quarter.items()):
            # Quarter header
            quarter_label = f"Q{quarter} {year}"
            ws.cell(row=row, column=1, value=quarter_label)
            ws.cell(row=row, column=1).font = Font(bold=True, size=12)
            ws.merge_cells(f"A{row}:G{row}")
            row += 1

            # Quarter data
            for agg in sorted(aggs, key=lambda a: (a.level, a.account_code)):
                ws.cell(row=row, column=1, value=agg.account_code)
                ws.cell(row=row, column=2, value=agg.account_path)
                ws.cell(row=row, column=3, value=agg.level)
                ws.cell(row=row, column=4, value=agg.quarter)
                ws.cell(row=row, column=5, value=agg.year)
                ws.cell(row=row, column=6, value=float(agg.total_amount))
                ws.cell(row=row, column=7, value=agg.entry_count)

                # Format amount
                amount_cell = ws.cell(row=row, column=6)
                amount_cell.number_format = "#,##0.00"

                # Color code by quarter
                quarter_color = self._get_quarter_color(agg.quarter)
                if quarter_color:
                    for col in range(1, 8):
                        cell = ws.cell(row=row, column=col)
                        cell.fill = PatternFill(
                            start_color=quarter_color,
                            end_color=quarter_color,
                            fill_type="solid",
                        )

                row += 1

            # Quarter total
            quarter_total = sum(float(a.total_amount) for a in aggs)
            quarter_count = sum(a.entry_count for a in aggs)

            ws.cell(row=row, column=1, value=f"{quarter_label} TOTAL")
            ws.cell(row=row, column=1).font = Font(bold=True)
            ws.merge_cells(f"A{row}:E{row}")
            ws.cell(row=row, column=6, value=float(quarter_total))
            ws.cell(row=row, column=7, value=quarter_count)

            # Format total row
            for col in range(1, 8):
                cell = ws.cell(row=row, column=col)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color=self.COLOR_TOTAL,
                    end_color=self.COLOR_TOTAL,
                    fill_type="solid",
                )
                cell.font = Font(bold=True, color="FFFFFF")
                if col == 6:
                    cell.number_format = "#,##0.00"

            row += 2  # Space between quarters

        # Auto-adjust column widths
        column_widths = {
            "A": 15,  # Account Code
            "B": 40,  # Account Path
            "C": 8,   # Level
            "D": 8,   # Quarter
            "E": 8,   # Year
            "F": 18,  # Total Amount
            "G": 12,  # Entry Count
        }
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

        # Freeze top rows
        ws.freeze_panes = "A4"

        # Enable filters
        ws.auto_filter.ref = ws.dimensions

    def _create_hierarchy_summary_sheet(
        self, wb: Workbook, level_totals: dict[int, HierarchicalTotals]
    ) -> None:
        """Create hierarchy summary sheet."""
        ws = wb.create_sheet("Hierarchy Summary")

        # Title
        ws["A1"] = "Hierarchical Summary by Level"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:E1")

        if not level_totals:
            ws["A3"] = "No hierarchical totals available"
            return

        row = 3
        for level in [1, 2, 3, 4]:
            if level not in level_totals:
                continue

            totals = level_totals[level]

            # Level header
            ws[f"A{row}"] = f"Level {level} Summary"
            ws[f"A{row}"].font = Font(bold=True, size=12)
            ws.merge_cells(f"A{row}:E{row}")
            row += 1

            # Sub-headers
            headers = ["Account Code", "Account Path", "Total Amount", "Account Count"]
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(
                    start_color=self.COLOR_HEADER,
                    end_color=self.COLOR_HEADER,
                    fill_type="solid",
                )
            row += 1

            # Level data
            for agg in sorted(totals.accounts, key=lambda a: a.account_code):
                ws.cell(row=row, column=1, value=agg.account_code)
                ws.cell(row=row, column=2, value=agg.account_path)
                ws.cell(row=row, column=3, value=float(agg.total_amount))
                ws.cell(row=row, column=4, value=agg.entry_count)

                # Format amount
                amount_cell = ws.cell(row=row, column=3)
                amount_cell.number_format = "#,##0.00"

                row += 1

            # Level total
            ws.cell(row=row, column=1, value="TOTAL")
            ws.cell(row=row, column=1).font = Font(bold=True)
            ws.cell(row=row, column=2, value=f"Level {level} Total")
            ws.cell(row=row, column=3, value=float(totals.total_amount))
            ws.cell(row=row, column=4, value=totals.account_count)

            # Format total row
            for col in range(1, 5):
                cell = ws.cell(row=row, column=col)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color=self.COLOR_TOTAL,
                    end_color=self.COLOR_TOTAL,
                    fill_type="solid",
                )
                cell.font = Font(bold=True, color="FFFFFF")
                if col == 3:
                    cell.number_format = "#,##0.00"

            row += 2  # Space between levels

        # Auto-adjust column widths
        ws.column_dimensions["A"].width = 15
        ws.column_dimensions["B"].width = 40
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 15

    def _create_statistics_sheet(
        self,
        wb: Workbook,
        ledger_entries: list[LedgerEntry],
        aggregations: list[QuarterlyAggregation],
    ) -> None:
        """Create statistics sheet."""
        ws = wb.create_sheet("Statistics")

        # Title
        ws["A1"] = "Summary Statistics"
        ws["A1"].font = Font(bold=True, size=14)
        ws.merge_cells("A1:B1")

        # Calculate statistics
        total_entries = len(ledger_entries)
        total_amount = sum(float(e.amount) for e in ledger_entries)
        unique_accounts = len(set(e.account_code for e in ledger_entries))
        unique_quarters = len(
            set((e.quarter, e.year) for e in ledger_entries)
        )

        # Quarters breakdown
        quarters = {}
        for entry in ledger_entries:
            key = (entry.quarter, entry.year)
            if key not in quarters:
                quarters[key] = {"count": 0, "amount": 0.0}
            quarters[key]["count"] += 1
            quarters[key]["amount"] += float(entry.amount)

        # Write statistics
        row = 3
        stats = [
            ("Total Entries", total_entries),
            ("Total Amount", f"{total_amount:,.2f}"),
            ("Unique Accounts", unique_accounts),
            ("Unique Quarters", unique_quarters),
        ]

        for label, value in stats:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=1).font = Font(bold=True)
            ws.cell(row=row, column=2, value=value)
            row += 1

        # Quarters breakdown
        row += 1
        ws.cell(row=row, column=1, value="Quarter Breakdown")
        ws.cell(row=row, column=1).font = Font(bold=True, size=12)
        ws.merge_cells(f"A{row}:B{row}")
        row += 1

        headers = ["Quarter", "Entry Count", "Total Amount"]
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color=self.COLOR_HEADER,
                end_color=self.COLOR_HEADER,
                fill_type="solid",
            )
        row += 1

        for (quarter, year), data in sorted(quarters.items()):
            ws.cell(row=row, column=1, value=f"Q{quarter} {year}")
            ws.cell(row=row, column=2, value=data["count"])
            ws.cell(row=row, column=3, value=data["amount"])
            ws.cell(row=row, column=3).number_format = "#,##0.00"
            row += 1

        # Auto-adjust column widths
        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 18
        ws.column_dimensions["C"].width = 18

    def _add_charts(self, wb: Workbook, aggregations: list[QuarterlyAggregation]) -> None:
        """Add charts to the quarterly totals sheet."""
        ws = wb["Quarterly Totals"]

        # Create a simple bar chart for quarterly totals
        # This is a placeholder - actual chart implementation would require
        # more complex data organization
        # Charts can be added using openpyxl.chart module

    def _get_quarter_color(self, quarter: int) -> str | None:
        """
        Get color for quarter.

        Args:
            quarter: Quarter number (1-4)

        Returns:
            Color hex code or None
        """
        colors = {
            1: self.COLOR_QUARTER1,
            2: self.COLOR_QUARTER2,
            3: self.COLOR_QUARTER3,
            4: self.COLOR_QUARTER4,
        }
        return colors.get(quarter)
