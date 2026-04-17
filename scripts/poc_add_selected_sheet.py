"""
POC addendum: Adds a 'Selected Ultimates - POC' sheet to the template workbook
that pulls values from the Closed Count projected-ultimates region via
intra-workbook cross-sheet formulas.

Proves: LDF edit on Closed Count -> CDF recalc -> Projected Ultimate recalc
-> cross-sheet IBNR recalc on Selected Ultimates sheet.
"""

import pathlib
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

TEMPLATE_PATH = (
    pathlib.Path(__file__).parent.parent
    / "demo" / "demo4-complete" / "poc-output" / "templates"
    / "cl-selections-template.xlsx"
)

SRC_SHEET = "Closed Count"
NEW_SHEET = "Selected Ultimates - POC"

# Projected Ultimates region in source sheet (from poc_inject_formulas.py)
SRC_ULT_START = 56       # row 56 = first period
SRC_ULT_END = 65         # row 65 = last period
SRC_PERIOD_COL = "A"
SRC_ACTUAL_COL = "C"     # Latest Value
SRC_ULT_COL = "E"        # Projected Ultimate


def build():
    wb = load_workbook(TEMPLATE_PATH)

    if NEW_SHEET in wb.sheetnames:
        del wb[NEW_SHEET]
    ws = wb.create_sheet(NEW_SHEET)

    # Title
    title = ws.cell(row=1, column=1, value="Selected Ultimates — Closed Count (POC)")
    title.font = Font(bold=True, size=12)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)

    # Headers
    headers = ["Accident Period", "Actual (Latest)", "Chain Ladder Ult", "Selected Ultimate", "IBNR"]
    for i, h in enumerate(headers, start=1):
        c = ws.cell(row=2, column=i, value=h)
        c.font = Font(bold=True, size=10)
        c.alignment = Alignment(horizontal="center")

    # Column widths
    for i, w in enumerate([18, 16, 18, 20, 14], start=1):
        ws.column_dimensions[ws.cell(row=2, column=i).column_letter].width = w

    ws.freeze_panes = "A3"

    # Data rows — cross-sheet references
    for i, src_row in enumerate(range(SRC_ULT_START, SRC_ULT_END + 1)):
        r = 3 + i

        # Period: pull from CL sheet
        ws.cell(row=r, column=1, value=f"='{SRC_SHEET}'!{SRC_PERIOD_COL}{src_row}")

        # Actual: pull from CL sheet Latest Value
        cell = ws.cell(row=r, column=2, value=f"='{SRC_SHEET}'!{SRC_ACTUAL_COL}{src_row}")
        cell.number_format = "#,##0"

        # Chain Ladder Ult: pull from CL sheet Projected Ultimate
        cell = ws.cell(row=r, column=3, value=f"='{SRC_SHEET}'!{SRC_ULT_COL}{src_row}")
        cell.number_format = "#,##0"

        # Selected Ultimate: defaults to CL; actuary can overwrite with typed number
        cell = ws.cell(row=r, column=4, value=f"=C{r}")
        cell.number_format = "#,##0"

        # IBNR = Selected - Actual
        cell = ws.cell(row=r, column=5, value=f"=D{r}-B{r}")
        cell.number_format = "#,##0"

    # Totals row
    total_row = 3 + (SRC_ULT_END - SRC_ULT_START + 1)
    ws.cell(row=total_row, column=1, value="Total").font = Font(bold=True)
    for col_letter, col_idx in [("B", 2), ("C", 3), ("D", 4), ("E", 5)]:
        cell = ws.cell(
            row=total_row, column=col_idx,
            value=f"=SUM({col_letter}3:{col_letter}{total_row - 1})"
        )
        cell.number_format = "#,##0"
        cell.font = Font(bold=True)

    wb.save(TEMPLATE_PATH)
    print(f"Added '{NEW_SHEET}' sheet -> {TEMPLATE_PATH}")


if __name__ == "__main__":
    build()
