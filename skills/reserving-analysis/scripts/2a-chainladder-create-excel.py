# Creates a formatted Excel workbook that displays all the claims data, development factors,
# diagnostics, and calculated averages in an organized layout. Actuaries review this workbook and
# manually enter their selected factors based on the information presented.

"""
goal: Create Chain Ladder Selections.xlsx for actuarial LDF review and selection. This file should be manually edited by the actuary to make selections.

Sheet layout:
  - One main sheet per measure: loss triangle, LDF triangle, averages (no CV/slopes), selections
  - "Exposure": exposure triangle (if exposure data is available)
  - One CV & slopes sheet per measure: "{Measure} - CV & Slopes"
  - One sheet per diagnostic triangle: "Diag - {Name}" (shared across measures)

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 2a-chainladder-create-excel.py
"""

import sys
import pandas as pd
import xlsxwriter
from pathlib import Path

from modules import config
from modules.markdown_utils import df_to_markdown

# Paths from modules/config.py — override here if needed:
OUTPUT_PATH = config.PROCESSED_DATA
SELECTIONS_OUTPUT_PATH = config.SELECTIONS
METHOD_ID = "chainladder"
OUTPUT_FILE_NAME = "Chain Ladder Selections - LDFs.xlsx"

DIAG_SHEET_LABELS = {
    'reported_claims': 'REPORTED CLAIMS',
    'incurred_severity': 'INCURRED SEVERITY',
    'paid_severity': 'PAID SEVERITY',
    'paid_to_incurred': 'PAID TO INCURRED',
    'open_counts': 'OPEN COUNTS',
    'average_case_reserve': 'AVERAGE CASE RESERVE',
    'claim_closure_rate': 'CLAIM CLOSURE RATE',
    'incremental_incurred_severity': 'INCREMENTAL INCURRED SEVERITY',
    'incremental_paid_severity': 'INCREMENTAL PAID SEVERITY',
    'incremental_closure_rate': 'INCREMENTAL CLOSURE RATE',
}

DIAG_NUMBER_FORMATS = {
    'reported_claims': '#,##0',
    'incurred_severity': '#,##0',
    'paid_severity': '#,##0',
    'paid_to_incurred': '0.00%',
    'open_counts': '#,##0',
    'average_case_reserve': '#,##0',
    'claim_closure_rate': '0.00%',
    'incremental_incurred_severity': '#,##0',
    'incremental_paid_severity': '#,##0',
    'incremental_closure_rate': '0.00%',
}

def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter (A, B, C, etc.)"""
    result = ''
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result

def create_formats(wb):
    """Create all cell formats used in the workbook."""
    formats = {}
    
    # Subheader (column/row headers)
    formats['subheader'] = wb.add_format({
        'bold': True,
        'bg_color': '#D9D9D9',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    # Label (row labels in first column)
    formats['label'] = wb.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    # Data cells
    formats['data'] = wb.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter'
    })
    
    # Data with number format
    formats['data_num'] = wb.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '#,##0'
    })
    
    formats['data_ldf'] = wb.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '0.0000'
    })
    
    formats['data_pct'] = wb.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '0.00%'
    })
    
    # Selection fills
    formats['prior'] = wb.add_format({
        'bg_color': '#FFF2CC',
        'border': 1,
        'bold': True,
        'align': 'center'
    })
    
    formats['prior_data'] = wb.add_format({
        'bg_color': '#FFF2CC',
        'border': 1,
        'align': 'right',
        'num_format': '0.0000'
    })
    
    formats['prior_text'] = wb.add_format({
        'bg_color': '#FFF2CC',
        'border': 1,
        'align': 'left',
        'text_wrap': True
    })
    
    formats['selection'] = wb.add_format({
        'bg_color': '#E2EFDA',
        'border': 1,
        'bold': True,
        'align': 'center'
    })
    
    formats['selection_data'] = wb.add_format({
        'bg_color': '#E2EFDA',
        'border': 1,
        'align': 'right',
        'num_format': '0.0000'
    })
    
    formats['selection_text'] = wb.add_format({
        'bg_color': '#E2EFDA',
        'border': 1,
        'align': 'left',
        'text_wrap': True
    })
    
    formats['ai'] = wb.add_format({
        'bg_color': '#DDEBF7',
        'border': 1,
        'bold': True,
        'align': 'center'
    })
    
    formats['ai_data'] = wb.add_format({
        'bg_color': '#DDEBF7',
        'border': 1,
        'align': 'right',
        'num_format': '0.0000'
    })
    
    formats['ai_text'] = wb.add_format({
        'bg_color': '#DDEBF7',
        'border': 1,
        'align': 'left',
        'text_wrap': True
    })
    
    formats['user'] = wb.add_format({
        'bg_color': '#F4B084',
        'border': 1,
        'bold': True,
        'align': 'center'
    })
    
    formats['user_data'] = wb.add_format({
        'bg_color': '#F4B084',
        'border': 1,
        'align': 'right',
        'num_format': '0.0000'
    })
    
    formats['user_text'] = wb.add_format({
        'bg_color': '#F4B084',
        'border': 1,
        'align': 'left',
        'text_wrap': True
    })
    
    # Section header
    formats['section'] = wb.add_format({
        'bg_color': '#D9E1F2',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    return formats

def write_triangle(ws, start_row, title, row_labels, col_labels, data_dict, fmt, number_format="#,##0"):
    """Write a triangle to the worksheet starting at start_row (0-based)."""
    # Create format with specific number format
    data_fmt = fmt['wb'].add_format({
        'border': 1,
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
    return start_row + len(row_labels) + 2, data_start_row, data_end_row

def write_selections_section(ws, start_row, col_labels, fmt, prior_selections=None, measure=None):
    """Write selection rows for Rules-Based AI, Open-Ended AI, and User."""
    # Header row
    ws.write(start_row, 0, "", fmt['subheader'])
    for c_idx, col in enumerate(col_labels):
        ws.write(start_row, c_idx + 1, col, fmt['subheader'])
    start_row += 1
    
    # Prior selections if available
    if prior_selections is not None and measure is not None:
        measure_prior = prior_selections[prior_selections['measure'] == measure]
        if not measure_prior.empty:
            prior_dict = {}
            for _, row in measure_prior.iterrows():
                prior_dict[str(row['interval'])] = {
                    'selection': row['selection'],
                    'reasoning': row['reasoning']
                }
            
            # Prior Selection row
            ws.write(start_row, 0, "Prior Selection", fmt['prior'])
            for c_idx, col in enumerate(col_labels):
                if str(col) in prior_dict:
                    ws.write(start_row, c_idx + 1, prior_dict[str(col)]['selection'], fmt['prior_data'])
                else:
                    ws.write(start_row, c_idx + 1, "", fmt['prior_data'])
            start_row += 1
            
            # Prior Reasoning row
            ws.write(start_row, 0, "Prior Reasoning", fmt['prior'])
            for c_idx, col in enumerate(col_labels):
                if str(col) in prior_dict:
                    ws.write(start_row, c_idx + 1, prior_dict[str(col)]['reasoning'], fmt['prior_text'])
                else:
                    ws.write(start_row, c_idx + 1, "", fmt['prior_text'])
            start_row += 1
            
            start_row += 1  # Blank row
    
    # Rules-Based AI Selection
    ws.write(start_row, 0, "Rules-Based AI Selection", fmt['selection'])
    for c_idx in range(len(col_labels)):
        ws.write(start_row, c_idx + 1, "", fmt['selection_data'])
    start_row += 1
    
    # Rules-Based AI Reasoning
    ws.write(start_row, 0, "Rules-Based AI Reasoning", fmt['selection'])
    for c_idx in range(len(col_labels)):
        ws.write(start_row, c_idx + 1, "", fmt['selection_text'])
    start_row += 1
    
    start_row += 1  # Blank row
    
    # Open-Ended AI Selection
    ws.write(start_row, 0, "Open-Ended AI Selection", fmt['ai'])
    for c_idx in range(len(col_labels)):
        ws.write(start_row, c_idx + 1, "", fmt['ai_data'])
    start_row += 1
    
    # Open-Ended AI Reasoning
    ws.write(start_row, 0, "Open-Ended AI Reasoning", fmt['ai'])
    for c_idx in range(len(col_labels)):
        ws.write(start_row, c_idx + 1, "", fmt['ai_text'])
    start_row += 1
    
    start_row += 1  # Blank row
    
    # User Selection
    sel_row = start_row
    ws.write(start_row, 0, "User Selection", fmt['user'])
    for c_idx in range(len(col_labels)):
        ws.write(start_row, c_idx + 1, "", fmt['user_data'])
    start_row += 1
    
    # User Reasoning
    ws.write(start_row, 0, "User Reasoning", fmt['user'])
    for c_idx in range(len(col_labels)):
        ws.write(start_row, c_idx + 1, "", fmt['user_text'])
    start_row += 1
    
    return start_row, sel_row

_AVG_PERIOD_ORDER = ['all', '3yr', '5yr', '10yr']
_AVG_TYPE_ORDER = ['simple', 'weighted', 'exclude_high_low']

def _sort_avg_cols(cols):
    def key(col):
        normalized = col.replace('avg_', '')
        for p_idx, p in enumerate(_AVG_PERIOD_ORDER):
            for t_idx, t in enumerate(_AVG_TYPE_ORDER):
                if normalized == f"{t}_{p}":
                    return (p_idx, t_idx)
        return (99, 99)
    return sorted(cols, key=key)

def _avg_display_name(col):
    return col.replace('avg_exclude_high_low', 'exclude_high_low')

def atoa_formula(r, c, tri_data_start, ata_data_start):
    """Generate age-to-age formula (0-based indexing, but Excel formulas are 1-based)."""
    tri_row = tri_data_start + (r - ata_data_start) + 1  # +1 for Excel 1-based
    num_col = col_letter(c + 1)
    den_col = col_letter(c)
    return f"=IFERROR(IF({num_col}{tri_row}=\"\",\"\",{num_col}{tri_row}/{den_col}{tri_row}),\"\")"

def simple_avg_formula(col, row_range, ata_range):
    a, b = row_range
    ata_a, ata_b = ata_range
    # Convert to 1-based for Excel
    return f"=IFERROR(AVERAGE({col}{a+1}:{col}{b+1}),AVERAGE({col}{ata_a+1}:{col}{ata_b+1}))"

def weighted_avg_formula(col, ata_range, tri_range, all_ata_range, all_tri_range):
    ata_a, ata_b = ata_range
    tri_a, tri_b = tri_range
    # Convert to 1-based for Excel
    ata_ref = f"{col}{ata_a+1}:{col}{ata_b+1}"
    tri_ref = f"{col}{tri_a+1}:{col}{tri_b+1}"
    all_ata = f"{col}{all_ata_range[0]+1}:{col}{all_ata_range[1]+1}"
    all_tri = f"{col}{all_tri_range[0]+1}:{col}{all_tri_range[1]+1}"
    primary = f"SUMPRODUCT({ata_ref},{tri_ref})/SUMPRODUCT(({ata_ref}<>\"\")*{tri_ref})"
    fallback = f"SUMPRODUCT({all_ata},{all_tri})/SUMPRODUCT(({all_ata}<>\"\")*{all_tri})"
    return f"=IFERROR({primary},{fallback})"

def excl_hl_formula(col, row_range, ata_range):
    a, b = row_range
    ata_a, ata_b = ata_range
    # Convert to 1-based for Excel
    rng = f"{col}{a+1}:{col}{b+1}"
    all_rng = f"{col}{ata_a+1}:{col}{ata_b+1}"
    primary = f"TRIMMEAN({rng},2/COUNT({rng}))"
    fallback = f"AVERAGE({all_rng})"
    return f"=IFERROR({primary},{fallback})"

def build_main_sheet(ws, measure, df2, df4, fmt, df_prior=None):
    """Build the main LDF selection sheet for a measure."""
    df_m = df2[df2['measure'] == measure].copy()
    periods = df_m['period'].cat.categories.tolist()
    ages = [str(a) for a in df_m['age'].cat.categories.tolist()]
    intervals = [str(i) for i in df_m['interval'].dropna().cat.categories.tolist()]
    
    # 1. Loss Triangle
    loss_dict = {}
    for _, row in df_m.iterrows():
        loss_dict[(str(row['period']), str(row['age']))] = row['value']
    row_ptr, tri_start, tri_end = write_triangle(ws, 0, measure, periods, ages, loss_dict, fmt, "#,##0")
    
    # 2. Age-to-Age Factors (formulas)
    ata_start = row_ptr
    ws.write(ata_start, 0, "Period", fmt['subheader'])
    for c_idx, interval in enumerate(intervals):
        ws.write(ata_start, c_idx + 1, interval, fmt['subheader'])
    ata_start += 1
    
    # Write ATA formulas
    for r_idx, period in enumerate(periods):
        row = ata_start + r_idx
        ws.write(row, 0, period, fmt['label'])
        for c_idx in range(len(intervals)):
            formula = atoa_formula(row, c_idx, tri_start, ata_start)
            ws.write_formula(row, c_idx + 1, formula, fmt['data_ldf'])
    
    ata_end = ata_start + len(periods) - 1
    row_ptr = ata_end + 2
    
    # 3. Averages (formulas)
    df_avg = df4[df4['measure'] == measure].copy()
    raw_avg_cols = [col for col in df_avg.columns 
                    if col not in ['measure', 'interval'] 
                    and not col.startswith('cv_') 
                    and not col.startswith('slope_')]
    avg_cols = _sort_avg_cols(raw_avg_cols)
    display_cols = [_avg_display_name(c) for c in avg_cols]
    intervals_with_tail = intervals + ["Tail"]
    
    avg_start = row_ptr
    ws.write(avg_start, 0, "Metric", fmt['subheader'])
    for c_idx, interval in enumerate(intervals_with_tail):
        ws.write(avg_start, c_idx + 1, interval, fmt['subheader'])
    avg_start += 1
    
    # Map periods to ranges
    all_ata_rng = (ata_start, ata_end)
    all_tri_rng = (tri_start, tri_end)
    n_periods = len(periods)
    
    def get_ranges(n):
        if n >= n_periods:
            return all_ata_rng, all_tri_rng
        return (ata_end - n + 1, ata_end), (tri_end - n + 1, tri_end)
    
    # Write average formulas
    for r_idx, display in enumerate(display_cols):
        row = avg_start + r_idx
        ws.write(row, 0, display, fmt['label'])
        
        for c_idx in range(len(intervals)):
            col = col_letter(c_idx + 1)
            
            if "all" in display:
                ata_rng, tri_rng = all_ata_rng, all_tri_rng
            elif "3yr" in display:
                ata_rng, tri_rng = get_ranges(3)
            elif "5yr" in display:
                ata_rng, tri_rng = get_ranges(5)
            elif "10yr" in display:
                ata_rng, tri_rng = get_ranges(10)
            else:
                ata_rng, tri_rng = all_ata_rng, all_tri_rng
            
            if "simple" in display:
                formula = simple_avg_formula(col, ata_rng, all_ata_rng)
            elif "weighted" in display:
                formula = weighted_avg_formula(col, ata_rng, tri_rng, all_ata_rng, all_tri_rng)
            elif "exclude_high_low" in display:
                formula = excl_hl_formula(col, ata_rng, all_ata_rng)
            else:
                formula = ""
            
            if formula:
                ws.write_formula(row, c_idx + 1, formula, fmt['data_ldf'])
        
        # Tail column - write value from df4
        tail_val = None
        metric_col = [c for c in avg_cols if _avg_display_name(c) == display]
        if metric_col:
            val_row = df_avg[df_avg['interval'] == 'Tail']
            if not val_row.empty and metric_col[0] in val_row.columns:
                tail_val = val_row[metric_col[0]].iloc[0]
        
        if tail_val is not None and pd.notna(tail_val):
            ws.write(row, len(intervals) + 1, tail_val, fmt['data_ldf'])
    
    avg_end = avg_start + len(display_cols) - 1
    row_ptr = avg_end + 2
    
    # 4. Selections
    row_ptr, sel_row = write_selections_section(ws, row_ptr, intervals, fmt, prior_selections=df_prior, measure=measure)
    
    # Set column widths
    ws.set_column(0, 0, 22)
    for c_idx in range(1, max(len(ages), len(intervals_with_tail)) + 1):
        ws.set_column(c_idx, c_idx, 12)
    
    return {
        "tri_start": tri_start,
        "tri_end": tri_end,
        "ata_start": ata_start,
        "ata_end": ata_end,
        "sel_row": sel_row
    }

def build_exposure_sheet(ws, df2, fmt):
    """Build exposure sheet displaying exposure as simple 2-column table."""
    exp_sub = df2[(df2['measure'] == 'Exposure') & df2['value'].notna()].copy()
    if exp_sub.empty:
        return
    
    # Take the latest value per period
    exp_sub['age_num'] = pd.to_numeric(exp_sub['age'].astype(str), errors='coerce')
    exp_simple = exp_sub.sort_values('age_num').groupby('period', observed=True).last().reset_index()
    
    # Write headers
    ws.write(0, 0, "Period", fmt['subheader'])
    ws.write(0, 1, "Exposure", fmt['subheader'])
    
    # Write data
    for r_idx, (_, row) in enumerate(exp_simple.iterrows()):
        ws.write(r_idx + 1, 0, str(row['period']), fmt['label'])
        ws.write(r_idx + 1, 1, row['value'], fmt['data_num'])
    
    ws.set_column(0, 0, 22)
    ws.set_column(1, 1, 18)

def build_combined_diagnostics_sheet(ws, diagnostic_cols, df2, df3, fmt):
    """Build combined diagnostics sheet with all diagnostic triangles stacked vertically."""
    first_measure = df2['measure'].cat.categories[0]
    df_m = df2[df2['measure'] == first_measure].copy()
    periods = df_m['period'].cat.categories.tolist()
    ages = [str(a) for a in df_m['age'].cat.categories.tolist()]
    
    # Build period to row mapping for formula references (1-based for Excel)
    period_to_row = {str(p): idx + 2 for idx, p in enumerate(periods)}  # +2 because row 1 is header (0-based row 0)
    
    row_ptr = 0
    
    for diag_col in diagnostic_cols:
        # Skip reported_claims - it's redundant
        if diag_col == 'reported_claims':
            continue
        
        number_format = DIAG_NUMBER_FORMATS.get(diag_col, "0.0000")
        
        # Create format with specific number format
        diag_data_fmt = fmt['wb'].add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': number_format
        })
        
        # Write section title
        label = DIAG_SHEET_LABELS.get(diag_col, diag_col.replace('_', ' ').upper())
        ws.merge_range(row_ptr, 0, row_ptr, len(ages), label, fmt['section'])
        row_ptr += 1
        
        # Write header row
        ws.write(row_ptr, 0, "Period", fmt['subheader'])
        for c_idx, age in enumerate(ages):
            ws.write(row_ptr, c_idx + 1, age, fmt['subheader'])
        row_ptr += 1
        
        # Write data rows
        if diag_col == 'incurred_severity':
            for period in periods:
                ws.write(row_ptr, 0, str(period), fmt['label'])
                source_row = period_to_row[str(period)]
                for c_idx, age in enumerate(ages):
                    col_l = col_letter(c_idx + 1)
                    formula = f"=IFERROR('Incurred Loss'!{col_l}{source_row}/'Reported Count'!{col_l}{source_row},\"\")"
                    ws.write_formula(row_ptr, c_idx + 1, formula, diag_data_fmt)
                row_ptr += 1
        elif diag_col == 'paid_severity':
            for period in periods:
                ws.write(row_ptr, 0, str(period), fmt['label'])
                source_row = period_to_row[str(period)]
                for c_idx, age in enumerate(ages):
                    col_l = col_letter(c_idx + 1)
                    formula = f"=IFERROR('Paid Loss'!{col_l}{source_row}/'Reported Count'!{col_l}{source_row},\"\")"
                    ws.write_formula(row_ptr, c_idx + 1, formula, diag_data_fmt)
                row_ptr += 1
        elif diag_col == 'paid_to_incurred':
            for period in periods:
                ws.write(row_ptr, 0, str(period), fmt['label'])
                source_row = period_to_row[str(period)]
                for c_idx, age in enumerate(ages):
                    col_l = col_letter(c_idx + 1)
                    formula = f"=IFERROR('Paid Loss'!{col_l}{source_row}/'Incurred Loss'!{col_l}{source_row},\"\")"
                    ws.write_formula(row_ptr, c_idx + 1, formula, diag_data_fmt)
                row_ptr += 1
        elif diag_col == 'incremental_incurred_severity':
            for period in periods:
                ws.write(row_ptr, 0, str(period), fmt['label'])
                source_row = period_to_row[str(period)]
                for c_idx, age in enumerate(ages):
                    col_l = col_letter(c_idx + 1)
                    if c_idx == 0:  # First age column
                        formula = f"=IFERROR('Incurred Loss'!{col_l}{source_row}/'Reported Count'!{col_l}{source_row},\"\")"
                    else:  # Incremental
                        prev_col_l = col_letter(c_idx)
                        formula = f"=IFERROR(('Incurred Loss'!{col_l}{source_row}-'Incurred Loss'!{prev_col_l}{source_row})/('Reported Count'!{col_l}{source_row}-'Reported Count'!{prev_col_l}{source_row}),\"\")"
                    ws.write_formula(row_ptr, c_idx + 1, formula, diag_data_fmt)
                row_ptr += 1
        else:
            # Build data dict from df3
            diag_dict = {}
            for _, row in df3.iterrows():
                if diag_col in row and pd.notna(row[diag_col]):
                    diag_dict[(str(row['period']), str(row['age']))] = row[diag_col]
            
            for period in periods:
                ws.write(row_ptr, 0, str(period), fmt['label'])
                for c_idx, age in enumerate(ages):
                    val = diag_dict.get((str(period), age))
                    if val is not None:
                        ws.write(row_ptr, c_idx + 1, val, diag_data_fmt)
                row_ptr += 1
        
        # Add spacing between sections
        row_ptr += 1
    
    ws.set_column(0, 0, 22)
    for c_idx in range(1, len(ages) + 1):
        ws.set_column(c_idx, c_idx, 12)

def build_combined_cv_slopes_sheet(ws, measures, df2, df4, fmt):
    """Build combined CV & Slopes sheet with formulas AND cached values from df4."""
    row_ptr = 0
    
    # LDF data is in rows 28-51 (24 periods) in each measure sheet (1-based Excel rows)
    # In 0-based indexing: rows 27-50
    ldf_start_row_0based = 27
    ldf_end_row_0based = 50
    ldf_start_row_excel = 28  # 1-based for Excel formulas
    ldf_end_row_excel = 51    # 1-based for Excel formulas
    total_periods = ldf_end_row_excel - ldf_start_row_excel + 1
    
    for measure in measures:
        df_m = df2[df2['measure'] == measure].copy()
        intervals = [str(i) for i in df_m['interval'].dropna().cat.categories.tolist()]
        intervals_with_tail = intervals + ["Tail"]
        
        # Map intervals to column letters in the measure sheet
        interval_to_col = {}
        for idx, interval in enumerate(intervals):
            interval_to_col[interval] = col_letter(idx + 1)  # +1 because col 0 is "Period"
        
        # Write section title
        ws.merge_range(row_ptr, 0, row_ptr, len(intervals_with_tail), measure.upper(), fmt['section'])
        row_ptr += 1
        
        # Write header row
        ws.write(row_ptr, 0, "Metric", fmt['subheader'])
        for c_idx, interval in enumerate(intervals_with_tail):
            ws.write(row_ptr, c_idx + 1, interval, fmt['subheader'])
        row_ptr += 1
        
        # Define metrics
        metrics = ['cv_3yr', 'cv_5yr', 'cv_10yr', 'slope_3yr', 'slope_5yr', 'slope_10yr']
        
        # Get cached values from df4
        df_avg = df4[df4['measure'] == measure].copy()
        
        # Write data rows with formulas AND cached values
        for metric in metrics:
            ws.write(row_ptr, 0, metric, fmt['label'])
            
            # Determine number of periods for this metric
            if '3yr' in metric:
                n_periods = 3
            elif '5yr' in metric:
                n_periods = 5
            elif '10yr' in metric:
                n_periods = 10
            else:
                n_periods = total_periods
            
            # Calculate start row for the range (Excel 1-based)
            range_start_row_excel = ldf_end_row_excel - n_periods + 1
            
            for c_idx, interval in enumerate(intervals_with_tail):
                if interval == "Tail":
                    # Tail column - write value from df4 (no formula)
                    val_row = df_avg[df_avg['interval'] == interval]
                    if not val_row.empty and metric in val_row.columns:
                        val = val_row[metric].iloc[0]
                        if pd.notna(val):
                            ws.write(row_ptr, c_idx + 1, val, fmt['data_ldf'])
                else:
                    # Regular interval - write formula WITH cached value
                    col_l = interval_to_col.get(interval)
                    if col_l:
                        # Get cached value from df4
                        val_row = df_avg[df_avg['interval'] == interval]
                        cached_value = None
                        if not val_row.empty and metric in val_row.columns:
                            val = val_row[metric].iloc[0]
                            if pd.notna(val):
                                cached_value = val
                        
                        # Generate formula
                        if metric.startswith('cv_'):
                            formula = f"=IFERROR(STDEV.S('{measure}'!{col_l}{range_start_row_excel}:{col_l}{ldf_end_row_excel})/AVERAGE('{measure}'!{col_l}{range_start_row_excel}:{col_l}{ldf_end_row_excel}),\"\")"
                        elif metric.startswith('slope_'):
                            x_array = ",".join(str(i) for i in range(1, n_periods + 1))
                            formula = f"=IFERROR(SLOPE('{measure}'!{col_l}{range_start_row_excel}:{col_l}{ldf_end_row_excel},{{{x_array}}}),\"\")"
                        else:
                            formula = None
                        
                        # Write formula with cached value
                        if formula:
                            if cached_value is not None:
                                ws.write_formula(row_ptr, c_idx + 1, formula, fmt['data_ldf'], cached_value)
                            else:
                                ws.write_formula(row_ptr, c_idx + 1, formula, fmt['data_ldf'])
            
            row_ptr += 1
        
        # Add spacing between sections
        row_ptr += 1
    
    ws.set_column(0, 0, 22)
    if measures:
        first_measure = measures[0]
        df_m = df2[df2['measure'] == first_measure].copy()
        intervals = [str(i) for i in df_m['interval'].dropna().cat.categories.tolist()]
        intervals_with_tail = intervals + ["Tail"]
        for c_idx in range(1, len(intervals_with_tail) + 1):
            ws.set_column(c_idx, c_idx, 12)

def export_md_data(measures, df2, df3, df4, exp_md):
    """Export markdown context files for subagents."""
    for measure in measures:
        safe_name = measure.lower().replace(' ', '_')
        md_path = Path(SELECTIONS_OUTPUT_PATH) / f"chainladder-context-{safe_name}.md"
        
        tri_sub = df2[(df2['measure'] == measure) & df2['value'].notna()]
        if not tri_sub.empty:
            tri_piv = tri_sub.pivot(index='period', columns='age', values='value')
            tri_md = df_to_markdown(tri_piv, index=True)
        else:
            tri_md = "No data\n"
        
        diag_md = df_to_markdown(df3, index=False)
        avg_md = df_to_markdown(df4[df4['measure'] == measure], index=False)
        
        md_content = f"# Chain Ladder Context: {measure}\n\n"
        md_content += "## Table of Contents\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Triangle](#triangle)\n"
        md_content += "- [Diagnostics](#diagnostics)\n"
        md_content += "- [Averages](#averages)\n\n"
        md_content += "## Exposure\n" + exp_md + "\n"
        md_content += "## Triangle\n" + tri_md + "\n"
        md_content += "## Diagnostics\n" + diag_md + "\n"
        md_content += "## Averages\n" + avg_md + "\n"
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"Exported MD: {md_path}")

def main():
    output_file = SELECTIONS_OUTPUT_PATH + OUTPUT_FILE_NAME
    if Path(output_file).exists():
        raise FileExistsError(
            f"Output file already exists: {output_file}\n"
            "Delete or rename the file before re-running to avoid overwriting manual edits."
        )
    
    df2 = pd.read_parquet(OUTPUT_PATH + "2_enhanced.parquet")
    df3 = pd.read_parquet(OUTPUT_PATH + "3_diagnostics.parquet")
    df4 = pd.read_parquet(OUTPUT_PATH + "4_ldf_averages.parquet")
    
    print(f"Loaded data: {len(df2)} enhanced rows, {len(df3)} diagnostic rows, {len(df4)} average rows")
    
    prior_selections_path = Path(OUTPUT_PATH) / "../prior-selections.csv"
    df_prior = None
    if prior_selections_path.exists():
        df_prior = pd.read_csv(prior_selections_path)
        print(f"Loaded {len(df_prior)} prior selections")
    else:
        print("No prior selections found (optional)")
    
    for col in df3.columns:
        if col not in ['period', 'age']:
            if ('rate' in col.lower() or 'ratio' in col.lower() or 'to_' in col.lower()):
                if df3[col].dropna().abs().max() <= 2.0:
                    df3[col] = df3[col].astype(float)
    
    # Create workbook
    wb = xlsxwriter.Workbook(output_file)
    fmt = create_formats(wb)
    fmt['wb'] = wb  # Store workbook reference for creating additional formats
    
    raw_measures = df2['measure'].cat.categories.tolist()
    
    exp_sub = df2[(df2['measure'] == 'Exposure') & df2['value'].notna()]
    if not exp_sub.empty:
        exp_simple = exp_sub.groupby('period', observed=True).agg({'value': 'last'}).reset_index()
        exp_simple.columns = ['Period', 'Exposure']
        exp_md = df_to_markdown(exp_simple, index=False)
    else:
        exp_md = "No Exposure data\n"
    
    measures = [m for m in raw_measures if m != 'Exposure']
    
    diagnostic_cols = [col for col in df3.columns if col not in ['period', 'age']]
    
    layout_infos = {}
    
    for measure in measures:
        ws = wb.add_worksheet(measure[:31])
        layout_infos[measure] = build_main_sheet(ws, measure, df2, df4, fmt, df_prior=df_prior)
        print(f"Built main sheet: {measure[:31]}")
    
    # Add exposure sheet if exposure data is available
    if not exp_sub.empty:
        ws = wb.add_worksheet("Exposure")
        build_exposure_sheet(ws, df2, fmt)
        print("Built Exposure sheet")
    
    # Add combined Diagnostics sheet
    if diagnostic_cols:
        ws = wb.add_worksheet("Diagnostics")
        build_combined_diagnostics_sheet(ws, diagnostic_cols, df2, df3, fmt)
        print("Built combined Diagnostics sheet")
    
    # Add combined CV & Slopes sheet
    ws = wb.add_worksheet("CV & Slopes")
    build_combined_cv_slopes_sheet(ws, measures, df2, df4, fmt)
    print("Built combined CV & Slopes sheet")
    
    wb.close()
    print(f"\nSaved: {output_file}")
    print("  CV & Slope formulas now display immediately (cached values included)")
    
    export_md_data(measures, df2, df3, df4, exp_md)

if __name__ == "__main__":
    main()
