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
import numpy as np
import xlsxwriter
from pathlib import Path

from modules import config
from modules.markdown_utils import df_to_markdown
from modules.xl_styles import create_xlsxwriter_formats
from modules.xl_writers import col_letter, write_triangle_xlsxwriter
from modules.average_names import pretty_average_name
from modules.diagnostics_sheet import (
    DIAG_SHEET_LABELS,
    DIAG_NUMBER_FORMATS,
    build_combined_diagnostics_sheet,
)

# Paths from modules/config.py — override here if needed:
OUTPUT_PATH = config.PROCESSED_DATA
SELECTIONS_OUTPUT_PATH = config.SELECTIONS
METHOD_ID = "chainladder"
OUTPUT_FILE_NAME = "Chain Ladder Selections - LDFs.xlsx"

def write_selections_section(ws, start_row, col_labels, fmt, prior_selections=None, measure=None):
    """Write selection rows for Rules-Based AI, Open-Ended AI, and User."""
    # Header row
    ws.write(start_row, 0, "", fmt['subheader_left'])
    for c_idx, col in enumerate(col_labels):
        ws.write(start_row, c_idx + 1, col, fmt['subheader_right'])
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
    """Map average column names to prettier display names."""
    return pretty_average_name(col)

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
    row_ptr, tri_start, tri_end = write_triangle_xlsxwriter(ws, 0, periods, ages, loss_dict, fmt, "#,##0")
    
    # 2. Age-to-Age Factors (direct values from df2)
    ata_start = row_ptr
    ws.write(ata_start, 0, "Age-to-Age Factors", fmt['subheader_left'])
    for c_idx, interval in enumerate(intervals):
        ws.write(ata_start, c_idx + 1, interval, fmt['subheader_right'])
    ata_start += 1
    
    # Build LDF lookup dict from df_m
    ldf_dict = {}
    for _, row_data in df_m[df_m['ldf'].notna()].iterrows():
        key = (str(row_data['period']), str(row_data['interval']))
        ldf_dict[key] = row_data['ldf']
    
    # Write ATA values directly
    for r_idx, period in enumerate(periods):
        row = ata_start + r_idx
        ws.write(row, 0, period, fmt['label'])
        for c_idx, interval in enumerate(intervals):
            # Write LDF value directly from data
            ldf_val = ldf_dict.get((str(period), interval))
            if ldf_val is not None and pd.notna(ldf_val):
                ws.write(row, c_idx + 1, ldf_val, fmt['data_ldf'])
    
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
    ws.write(avg_start, 0, "Metric", fmt['subheader_left'])
    for c_idx, interval in enumerate(intervals_with_tail):
        ws.write(avg_start, c_idx + 1, interval, fmt['subheader_right'])
    avg_start += 1
    
    # Write average values directly from df4
    for r_idx, display in enumerate(display_cols):
        row = avg_start + r_idx
        ws.write(row, 0, display, fmt['label'])
        
        # Find the corresponding column in avg_cols
        metric_col = [c for c in avg_cols if _avg_display_name(c) == display]
        
        for c_idx, interval in enumerate(intervals):
            # Get value from df4
            if metric_col:
                val_row = df_avg[df_avg['interval'] == interval]
                if not val_row.empty and metric_col[0] in val_row.columns:
                    val = val_row[metric_col[0]].iloc[0]
                    if pd.notna(val):
                        ws.write(row, c_idx + 1, val, fmt['data_ldf'])
        
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
    ws.write(0, 0, "Period", fmt['subheader_left'])
    ws.write(0, 1, "Exposure", fmt['subheader_right'])
    
    # Write data
    for r_idx, (_, row) in enumerate(exp_simple.iterrows()):
        period = row['period']
        # Write period as number if numeric (try converting strings)
        if isinstance(period, (int, float, np.integer, np.floating)):
            ws.write_number(r_idx + 1, 0, float(period), fmt['label'])
        else:
            try:
                ws.write_number(r_idx + 1, 0, float(period), fmt['label'])
            except (ValueError, TypeError):
                ws.write(r_idx + 1, 0, str(period), fmt['label'])
        ws.write(r_idx + 1, 1, row['value'], fmt['data_num'])
    
    ws.set_column(0, 0, 22)
    ws.set_column(1, 1, 18)

def export_md_data(measures, df2, df3, df4, exp_md, prior_selections=None):
    """Export markdown context files for subagents."""
    for measure in measures:
        safe_name = measure.lower().replace(' ', '_')
        md_path = Path(SELECTIONS_OUTPUT_PATH) / f"chainladder-context-{safe_name}.md"
        
        # Triangle data
        tri_sub = df2[(df2['measure'] == measure) & df2['value'].notna()]
        if not tri_sub.empty:
            tri_piv = tri_sub.pivot(index='period', columns='age', values='value')
            tri_piv = tri_piv.round(0)
            tri_md = df_to_markdown(tri_piv, index=True)
        else:
            tri_md = "No data\n"
        
        # LDF (age-to-age factors) triangle
        ldf_sub = df2[(df2['measure'] == measure) & df2['ldf'].notna()]
        if not ldf_sub.empty:
            ldf_piv = ldf_sub.pivot(index='period', columns='interval', values='ldf')
            ldf_md = df_to_markdown(ldf_piv, index=True)
        else:
            ldf_md = "No data\n"
        
        # Diagnostics - create separate triangle for each diagnostic metric
        diagnostic_cols = [col for col in df3.columns if col not in ['period', 'age']]
        diagnostics_sections = ""
        for diag_col in diagnostic_cols:
            diag_sub = df3[['period', 'age', diag_col]].copy()
            # Filter out rows where age is NaN
            diag_sub = diag_sub[diag_sub['age'].notna()]
            if not diag_sub.empty and diag_sub[diag_col].notna().any():
                diag_piv = diag_sub.pivot(index='period', columns='age', values=diag_col)
                diag_label = DIAG_SHEET_LABELS.get(diag_col, diag_col.replace('_', ' ').title())
                diagnostics_sections += f"### {diag_label}\n"
                diagnostics_sections += df_to_markdown(diag_piv, index=True) + "\n"
        
        if not diagnostics_sections:
            diagnostics_sections = "No data\n"
        
        # Averages - exclude 'measure' column and transpose so intervals are columns
        avg_sub = df4[df4['measure'] == measure].copy()
        if not avg_sub.empty:
            avg_sub = avg_sub.drop(columns=['measure'])
            # Set interval as index, then transpose
            avg_sub = avg_sub.set_index('interval').T
            avg_md = df_to_markdown(avg_sub, index=True)
        else:
            avg_md = "No data\n"
        
        # Prior selections section
        prior_md = ""
        if prior_selections is not None:
            prior_m = prior_selections[prior_selections['measure'] == measure]
            if not prior_m.empty:
                prior_md = "## Prior Selections\n\n"
                prior_md += "| Interval | LDF | Reasoning |\n"
                prior_md += "|---|---|---|\n"
                for _, row in prior_m.iterrows():
                    reasoning = str(row.get('reasoning', ''))
                    truncated = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
                    prior_md += f"| {row['interval']} | {row['selection']:.4f} | {truncated} |\n"
                prior_md += "\n"
        
        if not prior_md:
            prior_md = "## Prior Selections\n\nNo prior LDF selections found for this analysis.\n\n"
        
        # Build markdown content
        md_content = f"# Chain Ladder Context: {measure}\n\n"
        md_content += "## Table of Contents\n"
        if prior_md:
            md_content += "- [Prior Selections](#prior-selections)\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Triangle](#triangle)\n"
        md_content += "- [Age-to-Age Factors](#age-to-age-factors)\n"
        md_content += "- [Diagnostics](#diagnostics)\n"
        md_content += "- [Averages](#averages)\n\n"
        if prior_md:
            md_content += prior_md
        md_content += "## Exposure\n" + exp_md + "\n"
        md_content += "## Triangle\n" + tri_md + "\n"
        md_content += "## Age-to-Age Factors\n" + ldf_md + "\n"
        md_content += "## Diagnostics\n" + diagnostics_sections + "\n"
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
    
    # Create workbook - LET and STDEV.S are now standard Excel 365 functions
    wb = xlsxwriter.Workbook(output_file)
    fmt = create_xlsxwriter_formats(wb)
    fmt['wb'] = wb  # Store workbook reference for creating additional formats
    
    raw_measures = df2['measure'].cat.categories.tolist()
    
    exp_sub = df2[(df2['measure'] == 'Exposure') & df2['value'].notna()]
    if not exp_sub.empty:
        exp_simple = exp_sub.groupby('period', observed=True).agg({'value': 'last'}).reset_index()
        exp_simple.columns = ['Period', 'Exposure']
        exp_simple['Exposure'] = exp_simple['Exposure'].round(0)
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
    
    # TODO: Add combined CV & Slopes sheet (function needs to be implemented)
    # ws = wb.add_worksheet("CV & Slopes")
    # build_combined_cv_slopes_sheet(ws, measures, df2, df4, fmt)
    # print("Built combined CV & Slopes sheet")
    
    wb.close()
    print(f"\nSaved: {output_file}")
    print("  All values hard-coded from source data (no formulas)")
    
    export_md_data(measures, df2, df3, df4, exp_md, df_prior)

if __name__ == "__main__":
    main()
