from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

from modules.xl_styles import DATA_FONT, THIN_BORDER, style_header
from modules.xl_utils import _safe, _to_py


def _data_cell(cell, value, num_fmt=None):
    """Write a styled data cell with border and alignment."""
    value = _to_py(_safe(value))
    cell.value     = value
    cell.font      = DATA_FONT
    cell.border    = THIN_BORDER
    cell.alignment = Alignment(
        horizontal="right" if isinstance(value, (int, float)) else "left",
        vertical="center",
    )
    if num_fmt and value is not None and isinstance(value, (int, float)):
        cell.number_format = num_fmt


def _write_title_and_headers(ws, title, headers, col_width=18):
    """
    Write a title row (row 1) and a styled header row (row 2).
    Returns 3 — the first data row.
    This format matches script 7's read_with_title() convention.
    """
    title_cell = ws.cell(1, 1, title)
    style_header(title_cell, "header")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.row_dimensions[1].height = 20

    for c, text in enumerate(headers, 1):
        cell = ws.cell(2, c, text)
        style_header(cell, "subheader")
        ws.column_dimensions[get_column_letter(c)].width = col_width

    ws.freeze_panes = "A3"
    return 3


def _write_headers(ws, headers, col_width=18):
    """
    Write a single styled header row (row 1), no title row.
    Returns 2 — the first data row.
    Matches script 7's read_no_title() convention ("Sel - " sheets).
    """
    for c, text in enumerate(headers, 1):
        cell = ws.cell(1, c, text)
        style_header(cell, "subheader")
        ws.column_dimensions[get_column_letter(c)].width = col_width

    ws.freeze_panes = "A2"
    return 2


# ==============================================================================
# xlsxwriter functions (for formula-driven Excel workbooks)
# ==============================================================================

def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter (A, B, C, etc.)."""
    result = ''
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result


def write_triangle_xlsxwriter(ws, start_row, row_labels, col_labels, data_dict, fmt, number_format="#,##0"):
    """
    Write a triangle to xlsxwriter worksheet starting at start_row (0-based).
    
    Args:
        ws: xlsxwriter worksheet
        start_row: Starting row (0-based)
        row_labels: List of row labels (e.g., periods/accident years)
        col_labels: List of column labels (e.g., ages/development periods)
        data_dict: Dict mapping (str(row_label), str(col_label)) -> value
        fmt: Format dict from create_xlsxwriter_formats()
        number_format: Excel number format string for data cells
    
    Returns:
        (next_row, data_start_row, data_end_row) tuple
    """
    # Create format with specific number format
    data_fmt = fmt['wb'].add_format({
        'align': 'right',
        'valign': 'vcenter',
        'num_format': number_format
    })
    
    # Write header row
    ws.write(start_row, 0, "Period", fmt['subheader'])
    for c_idx, col in enumerate(col_labels):
        ws.write(start_row, c_idx + 1, col, fmt['subheader'])
    
    # Write data rows
    data_start_row = start_row + 1
    for r_idx, row_label in enumerate(row_labels):
        row = data_start_row + r_idx
        ws.write(row, 0, row_label, fmt['label'])
        for c_idx, col in enumerate(col_labels):
            val = data_dict.get((str(row_label), str(col)))
            if val is not None:
                ws.write(row, c_idx + 1, val, data_fmt)
    
    data_end_row = data_start_row + len(row_labels) - 1
    next_row = start_row + len(row_labels) + 2  # +1 for header, +1 for blank row after
    
    return next_row, data_start_row, data_end_row
