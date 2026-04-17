"""
POC: Inject Excel formulas into the 4 measure sheets of cl-selections-template.xlsx.

For each of Incurred Loss, Paid Loss, Reported Count, Closed Count:
  - Triangle (rows 3-12) stays hard-coded input data
  - Age-to-age factors (rows 16-24) become =next_age/current_age formulas
  - Averages (rows 29-40) become AVERAGE/SUMPRODUCT/TRIMMEAN formulas
  - Selection row 47 stays hard-coded (actuary input)
  - NEW rows 50-52: Cumulative Development Factors (backward chain of selections)
  - NEW rows 54-65: Projected Ultimates per period = latest-diagonal * CDF-at-age

All four sheets share the same layout (verified) so one parameterized routine works.

Reproducibility: this script always rebuilds the template from the demo4 source
file, so accidental edits to the template never poison subsequent runs. Run from
the scripts/ directory.
"""

import pathlib
import shutil
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

DEMO_ROOT = pathlib.Path(__file__).parent.parent / "demo" / "demo4-complete"
SOURCE_PATH = DEMO_ROOT / "selections" / "Chain Ladder Selections.xlsx"
TEMPLATE_PATH = DEMO_ROOT / "poc-output" / "templates" / "cl-selections-template.xlsx"

MEASURE_SHEETS = ["Incurred Loss", "Paid Loss", "Reported Count", "Closed Count"]

# Layout constants (shared across measure sheets)
TRI_ROW_START, TRI_ROW_END = 3, 12
ATA_ROW_START, ATA_ROW_END = 16, 24
ATA_COL_START, ATA_COL_END = 2, 10    # B..J
TRI_COL_START, TRI_COL_END = 2, 11    # B..K

ROW_SIMPLE_ALL = 29
ROW_WEIGHTED_ALL = 30
ROW_EXCL_ALL = 31
ROW_SIMPLE_3YR = 32
ROW_WEIGHTED_3YR = 33
ROW_EXCL_3YR = 34
ROW_SIMPLE_5YR = 35
ROW_WEIGHTED_5YR = 36
ROW_EXCL_5YR = 37
ROW_SIMPLE_10YR = 38
ROW_WEIGHTED_10YR = 39
ROW_EXCL_10YR = 40

ROW_SELECTION = 47

ROW_CDF_TITLE = 50
ROW_CDF_AGES = 51
ROW_CDF_VALUES = 52
ROW_ULT_TITLE = 54
ROW_ULT_HEADER = 55
ROW_ULT_START = 56

ATA_ALL_RANGE = (16, 24)
ATA_3YR_RANGE = (22, 24)
ATA_5YR_RANGE = (20, 24)
ATA_10YR_RANGE = (16, 24)

TRI_ALL_RANGE = (3, 11)
TRI_3YR_RANGE = (9, 11)
TRI_5YR_RANGE = (7, 11)
TRI_10YR_RANGE = (3, 11)


def col_letter(idx):
    return get_column_letter(idx)


def atoa_formula(r, c):
    tri_row = r - 13
    num_col = col_letter(c + 1)
    den_col = col_letter(c)
    return f"={num_col}{tri_row}/{den_col}{tri_row}"


def simple_avg_formula(col, row_range):
    a, b = row_range
    return f"=IFERROR(AVERAGE({col}{a}:{col}{b}),AVERAGE({col}16:{col}24))"


def weighted_avg_formula(col, ata_range, tri_range):
    ata_a, ata_b = ata_range
    tri_a, tri_b = tri_range
    ata_ref = f"{col}{ata_a}:{col}{ata_b}"
    tri_ref = f"{col}{tri_a}:{col}{tri_b}"
    all_ata = f"{col}16:{col}24"
    all_tri = f"{col}3:{col}11"
    primary = f"SUMPRODUCT({ata_ref},{tri_ref})/SUMPRODUCT(({ata_ref}<>\"\")*{tri_ref})"
    fallback = f"SUMPRODUCT({all_ata},{all_tri})/SUMPRODUCT(({all_ata}<>\"\")*{all_tri})"
    return f"=IFERROR({primary},{fallback})"


def excl_hl_formula(col, row_range):
    a, b = row_range
    rng = f"{col}{a}:{col}{b}"
    all_rng = f"{col}16:{col}24"
    primary = f"TRIMMEAN({rng},2/COUNT({rng}))"
    fallback = f"AVERAGE({all_rng})"
    return f"=IFERROR({primary},{fallback})"


def inject_sheet(ws):
    # Age-to-age (rows 16-24, cols B-J)
    for r in range(ATA_ROW_START, ATA_ROW_END + 1):
        max_c = 26 - r  # diagonal constraint: factor needs col c and c+1 in same tri row
        for c in range(ATA_COL_START, ATA_COL_END + 1):
            if c <= max_c:
                ws.cell(row=r, column=c).value = atoa_formula(r, c)
            else:
                ws.cell(row=r, column=c).value = None

    # Averages
    for c in range(ATA_COL_START, ATA_COL_END + 1):
        col = col_letter(c)
        ws.cell(row=ROW_SIMPLE_ALL,     column=c).value = simple_avg_formula(col, ATA_ALL_RANGE)
        ws.cell(row=ROW_WEIGHTED_ALL,   column=c).value = weighted_avg_formula(col, ATA_ALL_RANGE, TRI_ALL_RANGE)
        ws.cell(row=ROW_EXCL_ALL,       column=c).value = excl_hl_formula(col, ATA_ALL_RANGE)
        ws.cell(row=ROW_SIMPLE_3YR,     column=c).value = simple_avg_formula(col, ATA_3YR_RANGE)
        ws.cell(row=ROW_WEIGHTED_3YR,   column=c).value = weighted_avg_formula(col, ATA_3YR_RANGE, TRI_3YR_RANGE)
        ws.cell(row=ROW_EXCL_3YR,       column=c).value = excl_hl_formula(col, ATA_3YR_RANGE)
        ws.cell(row=ROW_SIMPLE_5YR,     column=c).value = simple_avg_formula(col, ATA_5YR_RANGE)
        ws.cell(row=ROW_WEIGHTED_5YR,   column=c).value = weighted_avg_formula(col, ATA_5YR_RANGE, TRI_5YR_RANGE)
        ws.cell(row=ROW_EXCL_5YR,       column=c).value = excl_hl_formula(col, ATA_5YR_RANGE)
        ws.cell(row=ROW_SIMPLE_10YR,    column=c).value = simple_avg_formula(col, ATA_10YR_RANGE)
        ws.cell(row=ROW_WEIGHTED_10YR,  column=c).value = weighted_avg_formula(col, ATA_10YR_RANGE, TRI_10YR_RANGE)
        ws.cell(row=ROW_EXCL_10YR,      column=c).value = excl_hl_formula(col, ATA_10YR_RANGE)

    # CDF section
    title_cell = ws.cell(row=ROW_CDF_TITLE, column=1, value="Cumulative Development Factors")
    title_cell.font = Font(bold=True, size=10)
    # Safe merge: unmerge if already merged
    merge_range = f"A{ROW_CDF_TITLE}:K{ROW_CDF_TITLE}"
    if merge_range not in [str(m) for m in ws.merged_cells.ranges]:
        ws.merge_cells(merge_range)

    ws.cell(row=ROW_CDF_AGES, column=1, value="Age").font = Font(bold=True, size=9)
    for c in range(TRI_COL_START, TRI_COL_END + 1):
        cell = ws.cell(row=ROW_CDF_AGES, column=c, value=f"=${col_letter(c)}$2")
        cell.font = Font(bold=True, size=9)

    ws.cell(row=ROW_CDF_VALUES, column=1, value="CDF").font = Font(bold=True, size=9)
    # K (age 120) = tail from K47
    cell = ws.cell(row=ROW_CDF_VALUES, column=11, value=f"=K{ROW_SELECTION}")
    cell.number_format = "0.0000"
    # J..B: selected LDF × CDF of next column
    for c in range(10, 1, -1):
        col = col_letter(c)
        next_col = col_letter(c + 1)
        cell = ws.cell(
            row=ROW_CDF_VALUES, column=c,
            value=f"={col}{ROW_SELECTION}*{next_col}{ROW_CDF_VALUES}"
        )
        cell.number_format = "0.0000"

    # Projected Ultimates section
    title_cell = ws.cell(row=ROW_ULT_TITLE, column=1, value="Projected Ultimates")
    title_cell.font = Font(bold=True, size=10)
    merge_range = f"A{ROW_ULT_TITLE}:F{ROW_ULT_TITLE}"
    if merge_range not in [str(m) for m in ws.merged_cells.ranges]:
        ws.merge_cells(merge_range)

    headers = ["Period", "Latest Age", "Latest Value", "CDF at Age", "Projected Ultimate", "IBNR"]
    for i, h in enumerate(headers, start=1):
        c = ws.cell(row=ROW_ULT_HEADER, column=i, value=h)
        c.font = Font(bold=True, size=9)
        c.alignment = Alignment(horizontal="center")

    for i, tri_row in enumerate(range(TRI_ROW_START, TRI_ROW_END + 1)):
        r = ROW_ULT_START + i
        ws.cell(row=r, column=1, value=f"=A{tri_row}")
        ws.cell(row=r, column=2, value=f"=LOOKUP(2,1/(B{tri_row}:K{tri_row}<>\"\"),$B$2:$K$2)")
        cell = ws.cell(row=r, column=3, value=f"=LOOKUP(2,1/(B{tri_row}:K{tri_row}<>\"\"),B{tri_row}:K{tri_row})")
        cell.number_format = "#,##0"
        cell = ws.cell(row=r, column=4, value=f"=HLOOKUP(B{r},$B${ROW_CDF_AGES}:$K${ROW_CDF_VALUES},2,FALSE)")
        cell.number_format = "0.0000"
        cell = ws.cell(row=r, column=5, value=f"=C{r}*D{r}")
        cell.number_format = "#,##0"
        cell = ws.cell(row=r, column=6, value=f"=E{r}-C{r}")
        cell.number_format = "#,##0"


def main():
    # Always rebuild from pristine source so prior Excel edits don't drift.
    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE_PATH, TEMPLATE_PATH)
    print(f"  Seeded template from {SOURCE_PATH.name}")

    wb = load_workbook(TEMPLATE_PATH)
    for sheet in MEASURE_SHEETS:
        if sheet not in wb.sheetnames:
            print(f"  Skipping {sheet!r} (not found)")
            continue
        ws = wb[sheet]
        inject_sheet(ws)
        print(f"  Injected formulas -> {sheet!r}")
    wb.save(TEMPLATE_PATH)
    print(f"\nSaved -> {TEMPLATE_PATH}")


if __name__ == "__main__":
    main()
