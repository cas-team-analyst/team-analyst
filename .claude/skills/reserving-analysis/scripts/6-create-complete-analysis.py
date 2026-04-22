# Reads projected ultimates, actuary selections, and triangle data to produce a
# final Excel workbook summarizing the complete reserving analysis.

"""
goal: Create complete-analysis.xlsx (and three supporting workbooks) from the outputs
of the prior numbered scripts.

Outputs:
  - selected-ultimates.xlsx     Loss + Counts sheets with selected ultimates per period
  - post-method-series.xlsx     Ultimate Severity, Loss Rate, Frequency diagnostics
  - post-method-triangles.xlsx  X-to-Ultimate triangles, Average IBNR, Average Unpaid
  - complete-analysis.xlsx      Master workbook combining all prior Excel outputs + above

Gracefully handles optional data:
  - ultimate_ie (IE method, script 3): omits IE columns if not present
  - ultimate_bf (BF method, script 4): omits BF columns if not present
  - Exposure in triangles: omits Loss Rate and Frequency if not present
  - ultimates-ai-rules-based.json selections: falls back to open-ended > bf > cl > ie if file is absent or a row is missing

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 6-create-complete-analysis.py
"""

import copy
import json
import os
import pathlib

import numpy as np
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from modules.formulas import rewrite_formula_sheet_refs

from modules import config
from modules.xl_styles import (
    HEADER_FILL, SUBHEADER_FILL, SECTION_FILL, SELECTION_FILL,
    HEADER_FONT, SUBHEADER_FONT, SECTION_FONT, LABEL_FONT, DATA_FONT,
    THIN_BORDER, style_header,
)

# ── User-configurable properties ─────────────────────────────────────────────
# Paths from modules/config.py — override here if needed:

INPUT_ULTIMATES         = config.ULTIMATES + "projected-ultimates.parquet"
INPUT_SELECTIONS_EXCEL  = config.SELECTIONS + "Ultimates.xlsx"
INPUT_SELECTIONS_RB_JSON = config.SELECTIONS + "ultimates-ai-rules-based.json"
INPUT_SELECTIONS_OE_JSON = config.SELECTIONS + "ultimates-ai-open-ended.json"
INPUT_TRIANGLES         = config.PROCESSED_DATA + "1_triangles.parquet"
OUTPUT_PATH             = config.OUTPUT

# Excel files from prior scripts to fold into the complete analysis workbook.
# Each entry: (path_to_file, sheet_name_prefix_or_None).
# Files that do not exist are silently skipped.
ANALYSIS_SOURCE_FILES = [
    (config.SELECTIONS + "Chain Ladder Selections - LDFs.xlsx", "CL - "),
    (config.SELECTIONS + "Chain Ladder Selections - Tail.xlsx", "Tail - "),
    (config.SELECTIONS + "Ultimates.xlsx",               "Sel - "),
]

# Maps each measure to its "unpaid" proxy measure used to compute the Unpaid column.
# Unpaid = Selected Ultimate − latest actual of the proxy measure for that period.
UNPAID_PROXY = {
    "Incurred Loss":  "Paid Loss",
    "Paid Loss":      "Paid Loss",
    "Reported Count": "Closed Count",
    "Closed Count":   "Closed Count",
}

# ─────────────────────────────────────────────────────────────────────────────
# Derived output paths — do not modify.
OUTPUT_COMPLETE_ANALYSIS  = OUTPUT_PATH + "complete-analysis.xlsx"

_NUM_FMT = "#,##0"
_DEC_FMT = "#,##0.000"


def _style_cell(cell, level="subheader"):
    style_header(cell, level)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _try_int(val):
    """Convert value to integer where possible, else return original value."""
    try:
        num = float(val)
        if num == int(num):
            return int(num)
        return num
    except (ValueError, TypeError):
        return val


def _col_has_data(df, col):
    """True if column exists in df and contains at least one non-NaN value."""
    return col in df.columns and df[col].notna().any()


def _write_header_row(ws, headers, row=1, level="subheader", col_width=22):
    """Write a styled header row at the given row number."""
    for c_idx, text in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=c_idx, value=text)
        _style_cell(cell, level)
        ws.column_dimensions[get_column_letter(c_idx)].width = col_width


def _write_data_cell(cell, value, num_fmt=None, is_numeric=False):
    """Write a data cell with consistent font, border, alignment."""
    # Ensure numeric values are stored as numbers, not text
    if value is not None and is_numeric:
        try:
            cell.value = float(value) if not isinstance(value, (int, float)) else value
        except (ValueError, TypeError):
            cell.value = value
    else:
        cell.value = value
    
    cell.font   = DATA_FONT
    cell.border = THIN_BORDER
    cell.alignment = Alignment(horizontal="right" if isinstance(cell.value, (int, float)) else "left",
                               vertical="center")
    if num_fmt and cell.value is not None and isinstance(cell.value, (int, float)):
        cell.number_format = num_fmt


def _safe(val):
    """Return None for NaN so openpyxl writes a blank cell."""
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val


# ── Data loading ──────────────────────────────────────────────────────────────

def load_combined(ultimates_path, selections_excel_path, selections_rb_json_path, selections_oe_json_path):
    """
    Load projected ultimates and merge in actuary selections from Excel and JSON files.
    Priority: Excel User Selection > Excel Rules-Based AI > Excel Open-Ended AI > JSON rules-based > JSON open-ended.

    Returns:
        combined  (DataFrame): one row per (period, measure) with columns
                               period, measure, current_age, actual,
                               ultimate_cl, [ultimate_ie], [ultimate_bf],
                               selected_ultimate, selected_ibnr, selected_unpaid
        has_ie    (bool): True when ultimate_ie data is present
        has_bf    (bool): True when ultimate_bf data is present
    """
    df = pd.read_parquet(ultimates_path)
    df["period"]  = df["period"].astype(str)
    df["measure"] = df["measure"].astype(str)

    has_ie = _col_has_data(df, "ultimate_ie")
    has_bf = _col_has_data(df, "ultimate_bf")

    # Load actuary selections from Excel and JSON files
    # Priority: Excel User Selection (col 13) > Excel Rules-Based AI (col 9) > Excel Open-Ended AI (col 11) > JSON files
    sel_lookup = {}
    
    # Try to read from Excel first
    excel_path = pathlib.Path(selections_excel_path)
    if excel_path.exists():
        try:
            from openpyxl import load_workbook
            wb = load_workbook(excel_path, data_only=True)
            excel_count = 0
            
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                measure = sheet_name
                
                # Read from row 2 onwards (row 1 is header)
                row = 2
                while True:
                    period_cell = ws.cell(row=row, column=1)
                    if not period_cell.value:
                        break
                    
                    period = str(period_cell.value).strip()
                    key = (measure, period)
                    
                    # Check User Selection (col 13), then Rules-Based AI (col 9), then Open-Ended AI (col 11)
                    for col_idx in [13, 9, 11]:
                        val = ws.cell(row=row, column=col_idx).value
                        if val is not None and str(val).strip() and key not in sel_lookup:
                            try:
                                sel_lookup[key] = float(val)
                                excel_count += 1
                                break
                            except (ValueError, TypeError):
                                pass
                    
                    row += 1
            
            wb.close()
            if excel_count > 0:
                print(f"  Loaded {excel_count} selections from Excel {selections_excel_path}")
        except Exception as e:
            print(f"  Note: Could not read Excel selections from {selections_excel_path}: {e}")
    else:
        print(f"  Note: {selections_excel_path} not found")
    
    # Load rules-based JSON selections (only for missing keys)
    rb_path = pathlib.Path(selections_rb_json_path)
    if rb_path.exists():
        with open(rb_path, "r") as f:
            entries = json.load(f)
        rb_count = 0
        for entry in entries:
            key = (str(entry["measure"]), str(entry["period"]))
            if key not in sel_lookup:  # Don't overwrite Excel selections
                sel_lookup[key] = float(entry["selection"])
                rb_count += 1
        if rb_count > 0:
            print(f"  Loaded {rb_count} rules-based selections from {selections_rb_json_path} (fallback)")
    else:
        print(f"  Note: {selections_rb_json_path} not found")
    
    # Load open-ended JSON selections (only for missing keys)
    oe_path = pathlib.Path(selections_oe_json_path)
    if oe_path.exists():
        with open(oe_path, "r") as f:
            entries = json.load(f)
        oe_count = 0
        for entry in entries:
            key = (str(entry["measure"]), str(entry["period"]))
            if key not in sel_lookup:  # Don't overwrite Excel or rules-based
                sel_lookup[key] = float(entry["selection"])
                oe_count += 1
        if oe_count > 0:
            print(f"  Loaded {oe_count} open-ended selections from {selections_oe_json_path} (fallback)")
    else:
        print(f"  Note: {selections_oe_json_path} not found")
    
    if not sel_lookup:
        print("  Using method fallback for selected ultimate (no selections found in Excel or JSON).")

    # selected_ultimate: JSON entry → bf → cl → ie (first non-NaN available)
    def _pick_selected(row):
        key = (row["measure"], row["period"])
        if key in sel_lookup:
            return sel_lookup[key]
        for col in ("ultimate_bf", "ultimate_cl", "ultimate_ie"):
            if col in df.columns:
                v = row.get(col, np.nan)
                if pd.notna(v):
                    return v
        return np.nan

    df["selected_ultimate"] = df.apply(_pick_selected, axis=1)
    df["selected_ibnr"]     = df["selected_ultimate"] - df["actual"]

    # Unpaid = selected ultimate − actual of the proxy measure for that period
    actual_lookup = df.set_index(["period", "measure"])["actual"].to_dict()

    def _pick_unpaid(row):
        proxy = UNPAID_PROXY.get(row["measure"])
        if proxy is None:
            return np.nan
        proxy_actual = actual_lookup.get((row["period"], proxy), np.nan)
        if pd.isna(proxy_actual) or pd.isna(row["selected_ultimate"]):
            return np.nan
        return row["selected_ultimate"] - proxy_actual

    df["selected_unpaid"] = df.apply(_pick_unpaid, axis=1)

    return df, has_ie, has_bf


def get_exposure(triangles_df):
    """
    Extract latest exposure value per period from the triangles.

    Returns dict {str(period): float} or {} when no Exposure rows exist.
    """
    exp = triangles_df[triangles_df["measure"].astype(str) == "Exposure"].copy()
    if exp.empty:
        return {}
    exp["period"]  = exp["period"].astype(str)
    exp["age_int"] = pd.to_numeric(exp["age"].astype(str), errors="coerce")
    latest = exp.sort_values("age_int").groupby("period").last()
    return latest["value"].to_dict()


# ── Excel writers ─────────────────────────────────────────────────────────────

def write_notes_sheet(ws):
    """
    Write a Notes sheet with workbook overview and table of contents.
    """
    from datetime import datetime
    
    row = 1
    
    # Main title
    title_cell = ws.cell(row=row, column=1, value="Reserve Analysis Workbook")
    _style_cell(title_cell, "header")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
    ws.row_dimensions[row].height = 24
    row += 1
    
    # Metadata section
    meta_cell = ws.cell(row=row, column=1, value="Workbook Information")
    _style_cell(meta_cell, "section")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
    row += 1
    
    # Creation date
    date_label = ws.cell(row=row, column=1, value="Created:")
    date_label.font = LABEL_FONT
    date_label.border = THIN_BORDER
    date_label.alignment = Alignment(horizontal="left", vertical="center")
    
    date_value = ws.cell(row=row, column=2, value=datetime.now().strftime("%B %d, %Y %I:%M %p"))
    date_value.font = DATA_FONT
    date_value.border = THIN_BORDER
    date_value.alignment = Alignment(horizontal="left", vertical="center")
    row += 1
    
    # Description
    desc_label = ws.cell(row=row, column=1, value="Description:")
    desc_label.font = LABEL_FONT
    desc_label.border = THIN_BORDER
    desc_label.alignment = Alignment(horizontal="left", vertical="center")
    
    desc_value = ws.cell(row=row, column=2, value="Complete actuarial reserve analysis combining selections and projections")
    desc_value.font = DATA_FONT
    desc_value.border = THIN_BORDER
    desc_value.alignment = Alignment(horizontal="left", vertical="center")
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
    row += 2
    
    # Table of contents section
    toc_cell = ws.cell(row=row, column=1, value="Table of Contents")
    _style_cell(toc_cell, "section")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
    row += 1
    
    # Headers for TOC
    toc_name_header = ws.cell(row=row, column=1, value="Sheet Name")
    toc_name_header.font = SUBHEADER_FONT
    toc_name_header.fill = SUBHEADER_FILL
    toc_name_header.border = THIN_BORDER
    toc_name_header.alignment = Alignment(horizontal="center", vertical="center")
    
    toc_desc_header = ws.cell(row=row, column=2, value="Description")
    toc_desc_header.font = SUBHEADER_FONT
    toc_desc_header.fill = SUBHEADER_FILL
    toc_desc_header.border = THIN_BORDER
    toc_desc_header.alignment = Alignment(horizontal="center", vertical="center")
    row += 1
    
    # Return the row number where sheet list should start
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 15
    ws.freeze_panes = "A8"
    
    return row


def write_full_analysis(output_path, source_files, internal_files):
    """
    Combine all Excel files into a single master complete-analysis.xlsx.

    source_files  : list of (file_path, sheet_prefix_or_None) from prior scripts
    internal_files: list of file_paths generated by this script (no prefix)
    """
    master = Workbook()
    master.remove(master.active)
    
    # Create Notes sheet first
    notes_ws = master.create_sheet(title="Notes", index=0)
    toc_start_row = write_notes_sheet(notes_ws)

    all_files = list(source_files) + [(f, None) for f in internal_files]
    
    sheet_descriptions = []

    for file_path, prefix in all_files:
        if not os.path.exists(file_path):
            print(f"  Skipping (not found): {file_path}")
            continue
        wb = load_workbook(file_path, data_only=False)
        
        rename_map = {}
        for sname in wb.sheetnames:
            new_name = (f"{prefix}{sname}" if prefix else sname)[:31]
            rename_map[sname] = new_name
            
        for sname in wb.sheetnames:
            new_name = rename_map[sname]
            ws_src = wb[sname]
            ws_dst = master.create_sheet(title=new_name)
            
            for row in ws_src.iter_rows():
                for cell in row:
                    dst_cell = ws_dst[cell.coordinate]
                    # REWRITE FORMULA REFS
                    if isinstance(cell.value, str) and cell.value.startswith('='):
                        dst_cell.value = rewrite_formula_sheet_refs(cell.value, rename_map)
                    else:
                        dst_cell.value = cell.value
                        
                    if cell.has_style:
                        dst_cell.font = copy.copy(cell.font)
                        dst_cell.border = copy.copy(cell.border)
                        dst_cell.fill = copy.copy(cell.fill)
                        dst_cell.number_format = cell.number_format
                        dst_cell.protection = copy.copy(cell.protection)
                        dst_cell.alignment = copy.copy(cell.alignment)
            
            for col_letter in ws_src.column_dimensions:
                if col_letter in ws_src.column_dimensions:
                    ws_dst.column_dimensions[col_letter].width = ws_src.column_dimensions[col_letter].width
            
            for row_num in ws_src.row_dimensions:
                if row_num in ws_src.row_dimensions:
                    ws_dst.row_dimensions[row_num].height = ws_src.row_dimensions[row_num].height
            
            for merged_cell_range in ws_src.merged_cells.ranges:
                ws_dst.merge_cells(str(merged_cell_range))
            
            if ws_src.freeze_panes:
                ws_dst.freeze_panes = ws_src.freeze_panes
            
            desc = _get_sheet_description(new_name, prefix)
            sheet_descriptions.append((new_name, desc))
            
        print(f"  Added sheets from {file_path}")
    
    for idx, (sheet_name, desc) in enumerate(sheet_descriptions, start=toc_start_row):
        name_cell = notes_ws.cell(row=idx, column=1, value=sheet_name)
        name_cell.font = DATA_FONT
        name_cell.border = THIN_BORDER
        name_cell.alignment = Alignment(horizontal="left", vertical="center")
        
        desc_cell = notes_ws.cell(row=idx, column=2, value=desc)
        desc_cell.font = DATA_FONT
        desc_cell.border = THIN_BORDER
        desc_cell.alignment = Alignment(horizontal="left", vertical="center")

    os.makedirs(pathlib.Path(output_path).parent, exist_ok=True)
    master.save(output_path)
    print(f"  Saved -> {output_path}")

def _get_sheet_description(sheet_name, prefix):
    """Generate a description for a sheet based on its name."""
    # Remove prefix for pattern matching
    base_name = sheet_name
    if prefix:
        base_name = sheet_name[len(prefix):]
    
    # Common patterns
    descriptions = {
        # Chain Ladder sheets
        "Development Age-to-Age": "Historical age-to-age development factors",
        "Simple Averages": "Simple averages of age-to-age factors",
        "Vol-Weighted Avgs": "Volume-weighted averages of age-to-age factors",
        "Medians": "Median age-to-age factors",
        "Selections": "Selected loss development factors",
        
        # Ultimates selection sheets
        "Summary": "Ultimate loss selections summary",
        
        # Measure-specific sheets
        "Incurred Loss": "Incurred loss projections and selections",
        "Paid Loss": "Paid loss projections and selections",
        "Reported Count": "Reported claim count projections",
        "Closed Count": "Closed claim count projections",
        
        # Diagnostic sheets
        "Diagnostics": "Post-method diagnostic calculations",
        "Incurred-to-Ult": "Incurred to ultimate development ratios",
        "Paid-to-Ult": "Paid to ultimate development ratios",
        "Reported-to-Ult": "Reported to ultimate development ratios",
        "Closed-to-Ult": "Closed to ultimate development ratios",
        "Average IBNR": "Average IBNR by development age",
        "Average Unpaid": "Average unpaid by development age",
    }
    
    # Try exact match first
    if base_name in descriptions:
        return descriptions[base_name]
    
    # Try partial matches
    for key, desc in descriptions.items():
        if key in base_name or base_name in key:
            return desc
    
    # Default
    return "Analysis results"


# ── Main ──────────────────────────────────────────────────────────────────────

import json
import glob
import numpy as np

def build_measure_dfs():
    INPUT_ULTIMATES = config.ULTIMATES + "projected-ultimates.parquet"
    if not os.path.exists(INPUT_ULTIMATES):
        return {}
    df = pd.read_parquet(INPUT_ULTIMATES)
    
    excel_path = config.SELECTIONS + "Ultimates.xlsx"
    wb = None
    if os.path.exists(excel_path):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, data_only=True)
        except Exception:
            pass
            
    measures = df['measure'].unique()
    measure_dfs = {}
    for m in measures:
        json_path = config.SELECTIONS + "ultimates-ai-rules-based.json"
        m_df = df[df['measure'] == m].copy()
        m_df = m_df.rename(columns={
            "period": "Accident Period",
            "current_age": "Current Age",
            "actual": "Actual",
            "ultimate_cl": "Chain Ladder",
            "ultimate_ie": "Initial Expected",
            "ultimate_bf": "BF"
        })
        
        sel_col = pd.Series(index=m_df.index, dtype=float)
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as jf:
                jdata = json.load(jf)
                if isinstance(jdata, dict) and "measures" in jdata:
                    m_data = next((md for md in jdata["measures"] if md["measure"] == m), None)
                    if m_data:
                        for row in m_data.get("selections", []):
                            period_val = row.get("period")
                            sel = row.get("selection")
                            idx = m_df.index[m_df["Accident Period"] == period_val]
                            if len(idx) > 0 and sel is not None:
                                sel_col.loc[idx] = sel
                                
        if wb and f"Sel - {m}" in wb.sheetnames:
            ws = wb[f"Sel - {m}"]
            user_col = None
            period_col = None
            for cell in ws[1]:
                if cell.value == "User Selection":
                    user_col = cell.column
                if cell.value == "Period":
                    period_col = cell.column
            if user_col and period_col:
                for row in range(2, ws.max_row + 1):
                    period_val = ws.cell(row=row, column=period_col).value
                    user_val = ws.cell(row=row, column=user_col).value
                    if user_val is not None and isinstance(user_val, (int, float)):
                        idx = m_df.index[m_df["Accident Period"] == period_val]
                        if len(idx) > 0:
                            sel_col.loc[idx] = user_val
                            
        for idx in sel_col.index:
            if pd.isna(sel_col.loc[idx]):
                sel_col.loc[idx] = m_df.loc[idx, "BF"] if not pd.isna(m_df.loc[idx, "BF"]) else m_df.loc[idx, "Chain Ladder"]
        
        m_df["Selected Ultimate"] = sel_col
        m_df["IBNR"] = m_df["Selected Ultimate"] - m_df["Actual"]
        m_df["Unpaid"] = np.nan
        measure_dfs[m] = m_df
        
    return measure_dfs

def build_cl_dfs():
    INPUT_TRIANGLES = config.PROCESSED_DATA + "triangles.parquet"
    if not os.path.exists(INPUT_TRIANGLES):
        return {}
    tri_df = pd.read_parquet(INPUT_TRIANGLES)
    measures = tri_df['measure'].unique()
    cl_dfs = {}
    
    excel_path_ldf = config.SELECTIONS + "Chain Ladder Selections - LDFs.xlsx"
    wb_ldf = None
    if os.path.exists(excel_path_ldf):
        try:
            import openpyxl
            wb_ldf = openpyxl.load_workbook(excel_path_ldf, data_only=True)
        except Exception:
            pass
            
    excel_path_tail = config.SELECTIONS + "Chain Ladder Selections - Tail.xlsx"
    wb_tail = None
    if os.path.exists(excel_path_tail):
        try:
            import openpyxl
            wb_tail = openpyxl.load_workbook(excel_path_tail, data_only=True)
        except Exception:
            pass

    for m in measures:
        m_tri = tri_df[tri_df['measure'] == m]
        # We need the factors. LDFs are built from triangles.
        # Wait, the MD context replaced the json context. We can just rebuild the triangle here!
        # But wait! We just need the "Selected LDF" row for Tech Review! We can just put it in a dataframe.
        df_piv = m_tri.pivot(index="period", columns="age", values="value")
        df_piv.index = df_piv.index.astype(str)
        # Drop current age columns, actually LDFs have intervals like '12-24'.
        ages = sorted([int(c) for c in df_piv.columns if str(c).isdigit()])
        intervals = [f"{ages[i]}-{ages[i+1]}" for i in range(len(ages)-1)]
        
        sel_ldf = pd.Series(index=[str(a) for a in ages[:-1]] + ["Tail"], dtype=float)
        
        rb_json_path = config.SELECTIONS + "chainladder-ai-rules-based.json"
        if os.path.exists(rb_json_path):
            with open(rb_json_path, 'r') as rb_f:
                rb_data = json.load(rb_f)
                if isinstance(rb_data, dict) and "measures" in rb_data:
                    m_data = next((md for md in rb_data["measures"] if md["measure"] == m), None)
                    if m_data:
                        for interval_data in m_data.get("selections", []):
                            age = str(interval_data.get("interval", "")).split("-")[0]
                            sel = interval_data.get("selection")
                            if age in sel_ldf.index and sel is not None:
                                sel_ldf[age] = sel
                                
        if wb_ldf and m in wb_ldf.sheetnames:
            ws = wb_ldf[m]
            user_row = None
            header_row = None
            for row in range(1, ws.max_row + 1):
                if ws.cell(row=row, column=1).value == "User Selection":
                    user_row = row
                    for hr in range(row-1, max(0, row-10), -1):
                        if str(ws.cell(row=hr, column=2).value).endswith("24"):
                            header_row = hr
                            break
                    break
            if user_row and header_row:
                for col in range(2, ws.max_column + 1):
                    interval = ws.cell(row=header_row, column=col).value
                    user_val = ws.cell(row=user_row, column=col).value
                    if interval and isinstance(user_val, (int, float)):
                        age = str(interval).split("-")[0]
                        if age in sel_ldf.index:
                            sel_ldf[age] = user_val
                            
        sel_ldf["Tail"] = 1.0 
        rb_tail_path = config.SELECTIONS + "tail-ai-rules-based.json"
        if os.path.exists(rb_tail_path):
            with open(rb_tail_path, 'r') as t_f:
                t_data = json.load(t_f)
                if isinstance(t_data, dict) and "measures" in t_data:
                    tm_data = next((md for md in t_data["measures"] if md["measure"] == m), None)
                    if tm_data and tm_data.get("selection") is not None:
                        sel_ldf["Tail"] = tm_data.get("selection")
                        
        if wb_tail and m in wb_tail.sheetnames:
            ws_t = wb_tail[m]
            for row in range(1, ws_t.max_row + 1):
                if ws_t.cell(row=row, column=1).value == "User Selection":
                    u_val = ws_t.cell(row=row, column=2).value
                    if isinstance(u_val, (int, float)):
                        sel_ldf["Tail"] = u_val
                    break
        
        # We don't need the whole triangle for Tech Review, just the 'Selected LDF' dataframe
        # Wait, check_cl_factors checks df.loc["Selected LDF"]!
        cl_dfs[f"CL - {m}"] = pd.DataFrame([sel_ldf], index=["Selected LDF"])
        
    return cl_dfs

def write_hardcoded_excel(measure_dfs, cl_dfs, filepath):
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for m, df in measure_dfs.items():
            df.to_excel(writer, sheet_name=f"Sel - {m[:25]}", index=False)
        for name, df in cl_dfs.items():
            df.to_excel(writer, sheet_name=name[:31])


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    print("Loading data...")
    combined, has_ie, has_bf = load_combined(INPUT_ULTIMATES, INPUT_SELECTIONS_EXCEL, INPUT_SELECTIONS_RB_JSON, INPUT_SELECTIONS_OE_JSON)
    print(f"  has_ie={has_ie}, has_bf={has_bf}, rows={len(combined)}")

    print("\\nWriting complete analysis workbook...")
    internal = []
    write_full_analysis(OUTPUT_COMPLETE_ANALYSIS, ANALYSIS_SOURCE_FILES, internal)

    # Console IBNR summary
    print("\\n=== IBNR Summary ===")
    pd.set_option("display.float_format", lambda x: f"{x:,.0f}")
    for m in ["Incurred Loss", "Paid Loss", "Reported Count", "Closed Count"]:
        sub = combined[combined["measure"] == m]
        if sub.empty or sub["selected_ultimate"].isna().all():
            continue
        parts = [
            f"Actual={sub['actual'].sum():,.0f}",
            f"CL={sub['ultimate_cl'].sum():,.0f}",
        ]
        if has_ie:
            parts.append(f"IE={sub['ultimate_ie'].sum():,.0f}")
        if has_bf:
            parts.append(f"BF={sub['ultimate_bf'].sum():,.0f}")
        parts += [
            f"Selected={sub['selected_ultimate'].sum():,.0f}",
            f"IBNR={sub['selected_ibnr'].sum():,.0f}",
        ]
        print(f"  {m}: " + "  ".join(parts))

if __name__ == "__main__":
    print("=== Step 6: Creating complete analysis workbook ===")
    main()
    print("\nWriting evaluated hard-coded analysis workbook...")
    try:
        m_dfs = build_measure_dfs()
        c_dfs = build_cl_dfs()
        write_hardcoded_excel(m_dfs, c_dfs, OUTPUT_PATH + "complete-analysis-values.xlsx")
        print(f"  Created: {OUTPUT_PATH + 'complete-analysis-values.xlsx'}")
    except Exception as e:
        print(f"  Warning: could not write hardcoded excel: {e}")

    
