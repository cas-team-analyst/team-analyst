# Creates a formatted Excel workbook displaying projected ultimate indications from multiple
# reserving methods (Chain Ladder, Bornhuetter-Ferguson, etc.) alongside prior selections.
# Actuaries review this workbook and manually enter their selected ultimate values and reasoning.

"""
goal: Create Ultimates.xlsx for actuarial review and selection of ultimate losses by period.

Each sheet (one per measure) contains:
  - Period and current maturity information
  - Actual reported losses
  - Initial expected ultimate
  - Indicated ultimates from Chain Ladder, BF, and other methods
  - Prior selections and reasoning (when available)
  - Blank selection rows for actuary input

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 5a-ultimates-create-excel.py
"""

import json
import pandas as pd
import numpy as np
import xlsxwriter
import pathlib

from modules import config
from modules.xl_styles import create_xlsxwriter_formats, COLORS
from modules.xl_utils import build_column_map
from modules.markdown_utils import df_to_markdown


def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter (A, B, C...)."""
    result = ""
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result

# Paths from modules/config.py — override here if needed:
INPUT_ULTIMATES  = config.ULTIMATES + "projected-ultimates.parquet"
INPUT_TRIANGLES = config.PROCESSED_DATA + "triangles.parquet"
PRIOR_SELECTIONS_RB = config.SELECTIONS + "ultimates-prior.json"             # Optional, priority 1 — set to prior cycle's selected ultimates
PRIOR_SELECTIONS_OE = config.SELECTIONS + "ultimates-prior-oe.json"          # Optional, priority 2 — fallback prior
OUTPUT_FILE      = config.SELECTIONS + "Ultimates.xlsx"
SELECTIONS_OUTPUT_PATH = config.SELECTIONS


def export_md_data(df_ult, exp_md):
    import pathlib
    # Subagents should use these markdown files as canonical context.
    # Workbook contains hard-coded values from source data.
    
    # Export Loss category (Incurred + Paid)
    loss_measures = ['Incurred Loss', 'Paid Loss']
    loss_data = []
    for measure in loss_measures:
        df_m = df_ult[df_ult['measure'] == measure].copy()
        if not df_m.empty:
            loss_data.append((measure, df_m))
    
    if loss_data:
        md_path = pathlib.Path(SELECTIONS_OUTPUT_PATH) / "ultimates-context-loss.md"
        md_content = "# Ultimates Context: Loss\n\n"
        md_content += "## Table of Contents\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Projected Ultimates](#projected-ultimates)\n\n"
        md_content += "## Exposure\n" + exp_md + "\n"
        md_content += "## Projected Ultimates\n\n"
        
        for measure, df_m in loss_data:
            df_m = df_m.drop(columns=['measure'], errors='ignore')
            md_content += f"### {measure}\n\n"
            md_content += df_to_markdown(df_m, index=False) + "\n\n"
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"  Exported MD: {md_path}")
    
    # Export Count category (Reported + Closed, skip Closed if no actual data)
    count_measures = ['Reported Count', 'Closed Count']
    count_data = []
    for measure in count_measures:
        df_m = df_ult[df_ult['measure'] == measure].copy()
        # Skip Closed Count if no actual data exists
        if not df_m.empty:
            if measure == 'Closed Count' and not df_m['actual'].notna().any():
                continue  # Skip closed count with no actual data
            count_data.append((measure, df_m))
    
    if count_data:
        md_path = pathlib.Path(SELECTIONS_OUTPUT_PATH) / "ultimates-context-count.md"
        md_content = "# Ultimates Context: Count\n\n"
        md_content += "## Table of Contents\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Projected Ultimates](#projected-ultimates)\n\n"
        md_content += "## Exposure\n" + exp_md + "\n"
        md_content += "## Projected Ultimates\n\n"
        
        for measure, df_m in count_data:
            df_m = df_m.drop(columns=['measure'], errors='ignore')
            md_content += f"### {measure}\n\n"
            md_content += df_to_markdown(df_m, index=False) + "\n\n"
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"  Exported MD: {md_path}")



def format_loss_sheet(wb, ws, df_ult, df_prior):
    """
    Format the Loss sheet with Incurred and Paid columns combined.
    
    Args:
        wb: xlsxwriter workbook object (for creating formats)
        ws: xlsxwriter worksheet object
        df_ult: DataFrame with projected ultimates for all measures
        df_prior: DataFrame with prior selections (or None if no prior selections)
    """
    # Get data for both loss measures
    df_incurred = df_ult[df_ult['measure'] == 'Incurred Loss'].copy() if 'Incurred Loss' in df_ult['measure'].values else pd.DataFrame()
    df_paid = df_ult[df_ult['measure'] == 'Paid Loss'].copy() if 'Paid Loss' in df_ult['measure'].values else pd.DataFrame()
    
    if df_incurred.empty and df_paid.empty:
        return
    
    # Merge on period to get one row per period
    if not df_incurred.empty and not df_paid.empty:
        df_combined = df_incurred[['period', 'current_age', 'actual']].copy()
        df_combined.rename(columns={'actual': 'incurred_actual'}, inplace=True)
        df_paid_subset = df_paid[['period', 'actual', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].copy()
        df_paid_subset.rename(columns={'actual': 'paid_actual', 'ultimate_ie': 'paid_ie', 'ultimate_cl': 'paid_cl', 'ultimate_bf': 'paid_bf'}, inplace=True)
        df_combined = df_combined.merge(df_paid_subset, on='period', how='outer')
        df_combined.rename(columns={'incurred_actual': 'incurred', 'paid_actual': 'paid'}, inplace=True)
        
        # Add incurred ultimates
        df_combined = df_combined.merge(
            df_incurred[['period', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].rename(columns={'ultimate_ie': 'incurred_ie', 'ultimate_cl': 'incurred_cl', 'ultimate_bf': 'incurred_bf'}),
            on='period', how='left'
        )
    elif not df_incurred.empty:
        df_combined = df_incurred[['period', 'current_age', 'actual', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].copy()
        df_combined.rename(columns={'actual': 'incurred', 'ultimate_ie': 'incurred_ie', 'ultimate_cl': 'incurred_cl', 'ultimate_bf': 'incurred_bf'}, inplace=True)
        df_combined['paid'] = None
        df_combined['paid_ie'] = None
        df_combined['paid_cl'] = None
        df_combined['paid_bf'] = None
    else:  # only paid
        df_combined = df_paid[['period', 'current_age', 'actual', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].copy()
        df_combined.rename(columns={'actual': 'paid', 'ultimate_ie': 'paid_ie', 'ultimate_cl': 'paid_cl', 'ultimate_bf': 'paid_bf'}, inplace=True)
        df_combined['incurred'] = None
        df_combined['incurred_ie'] = None
        df_combined['incurred_cl'] = None
        df_combined['incurred_bf'] = None
    
    # Check if we have prior data for Losses
    has_prior_data = df_prior is not None and 'Losses' in df_prior.get('category', df_prior.get('measure', pd.Series())).values
    
    # Get formats
    fmt = create_xlsxwriter_formats(wb)
    
    # Write headers - conditionally include Prior columns
    headers = [
        "Accident Period", "Current Age", "Incurred", "Paid",
        "Incurred CL", "Paid CL", "Incurred IE", "Paid IE", "Incurred BF", "Paid BF"
    ]
    if has_prior_data:
        headers.extend(["Prior Selection", "Prior Reasoning"])
    headers.extend([
        "Rules-Based AI Selection", "Rules-Based AI Reasoning",
        "Open-Ended AI Selection", "Open-Ended AI Reasoning",
        "User Selection", "User Reasoning"
    ])
    
    for c_idx, header in enumerate(headers):
        ws.write(0, c_idx, header, fmt['header'])
        ws.set_column(c_idx, c_idx, 18)
    
    # Build column map from headers list (xlsxwriter is write-only, cannot read back)
    col_map = {header: idx for idx, header in enumerate(headers)}
    
    # Set wider widths for reasoning columns
    if has_prior_data:
        prior_reason_col = col_map["Prior Reasoning"]
        ws.set_column(prior_reason_col, prior_reason_col, 30)
    rb_reason_col = col_map["Rules-Based AI Reasoning"]
    oe_reason_col = col_map["Open-Ended AI Reasoning"]
    user_reason_col = col_map["User Reasoning"]
    ws.set_column(rb_reason_col, rb_reason_col, 30)
    ws.set_column(oe_reason_col, oe_reason_col, 30)
    ws.set_column(user_reason_col, user_reason_col, 40)
    
    # Create dict of prior
    prior_dict = {}
    if has_prior_data:
        mp = df_prior[df_prior.get('category', df_prior.get('measure')) == 'Losses']
        for _, r in mp.iterrows():
            prior_dict[str(r['period'])] = {"sel": r.get('selection', r.get('selected_ultimate')), "reason": r.get('reasoning', '')}
    
    # Write rows (0-based indexing, starting at row 1)
    for r_idx, (_, row) in enumerate(df_combined.iterrows(), start=1):
        period = row['period']  # Keep original type
        
        # Period - write as number if numeric to avoid Excel warnings
        if isinstance(period, (int, float, np.integer, np.floating)):
            ws.write_number(r_idx, 0, period, fmt['label'])
        else:
            ws.write(r_idx, 0, str(period), fmt['label'])
        
        val_age = row.get('current_age')
        if pd.isna(val_age):
            ws.write_blank(r_idx, 1, None, fmt['label'])
        elif isinstance(val_age, (int, float, np.integer, np.floating)):
            ws.write_number(r_idx, 1, val_age, fmt['label'])
        else:
            ws.write(r_idx, 1, str(val_age), fmt['label'])
        
        # Values (incurred, paid, CL, IE, BF)
        for col_offset, col_name in enumerate(['incurred', 'paid', 'incurred_cl', 'paid_cl', 'incurred_ie', 'paid_ie', 'incurred_bf', 'paid_bf']):
            val = row.get(col_name)
            if pd.isna(val): val = ""
            ws.write(r_idx, 2 + col_offset, val, fmt['data'])
        
        # Prior (only if prior data available)
        if has_prior_data:
            prior_sel = prior_dict.get(period, {}).get("sel", "")
            prior_reason = prior_dict.get(period, {}).get("reason", "")
            
            ws.write(r_idx, col_map["Prior Selection"], prior_sel, fmt['prior'])
            ws.write(r_idx, col_map["Prior Reasoning"], prior_reason, fmt['prior'])
        
        # Rules-Based AI Selection (yellow fill - will be populated by 5b script)
        ws.write(r_idx, col_map["Rules-Based AI Selection"], "", fmt['selection'])
        ws.write(r_idx, col_map["Rules-Based AI Reasoning"], "", fmt['selection'])
        
        # Open-Ended AI Selection (purple fill - will be populated by 5b script)
        ws.write(r_idx, col_map["Open-Ended AI Selection"], "", fmt['ai'])
        ws.write(r_idx, col_map["Open-Ended AI Reasoning"], "", fmt['ai'])
        
        # User Selection (blank - actuary input)
        ws.write(r_idx, col_map["User Selection"], "", fmt['user'])
        ws.write(r_idx, col_map["User Reasoning"], "", fmt['user'])


def format_count_sheet(wb, ws, df_ult, df_prior):
    """
    Format the Count sheet with Reported and Closed columns combined.
    Closed columns are omitted if no closed count data is present.
    
    Args:
        wb: xlsxwriter workbook object (for creating formats)
        ws: xlsxwriter worksheet object
        df_ult: DataFrame with projected ultimates for all measures
        df_prior: DataFrame with prior selections (or None if no prior selections)
    """
    # Get data for both count measures
    df_reported = df_ult[df_ult['measure'] == 'Reported Count'].copy() if 'Reported Count' in df_ult['measure'].values else pd.DataFrame()
    df_closed = df_ult[df_ult['measure'] == 'Closed Count'].copy() if 'Closed Count' in df_ult['measure'].values else pd.DataFrame()
    
    if df_reported.empty and df_closed.empty:
        return
    
    # Determine if we have closed count data (any non-null actual values)
    has_closed = not df_closed.empty and df_closed['actual'].notna().any()
    
    # Merge on period to get one row per period
    if not df_reported.empty and has_closed:
        df_combined = df_reported[['period', 'current_age', 'actual']].copy()
        df_combined.rename(columns={'actual': 'reported_actual'}, inplace=True)
        df_closed_subset = df_closed[['period', 'actual', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].copy()
        df_closed_subset.rename(columns={'actual': 'closed_actual', 'ultimate_ie': 'closed_ie', 'ultimate_cl': 'closed_cl', 'ultimate_bf': 'closed_bf'}, inplace=True)
        df_combined = df_combined.merge(df_closed_subset, on='period', how='outer')
        df_combined.rename(columns={'reported_actual': 'reported', 'closed_actual': 'closed'}, inplace=True)
        
        # Add reported ultimates
        df_combined = df_combined.merge(
            df_reported[['period', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].rename(columns={'ultimate_ie': 'reported_ie', 'ultimate_cl': 'reported_cl', 'ultimate_bf': 'reported_bf'}),
            on='period', how='left'
        )
    elif not df_reported.empty:
        # Only reported count - no closed columns needed
        df_combined = df_reported[['period', 'current_age', 'actual', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].copy()
        df_combined.rename(columns={'actual': 'reported', 'ultimate_ie': 'reported_ie', 'ultimate_cl': 'reported_cl', 'ultimate_bf': 'reported_bf'}, inplace=True)
    else:  # only closed
        df_combined = df_closed[['period', 'current_age', 'actual', 'ultimate_ie', 'ultimate_cl', 'ultimate_bf']].copy()
        df_combined.rename(columns={'actual': 'closed', 'ultimate_ie': 'closed_ie', 'ultimate_cl': 'closed_cl', 'ultimate_bf': 'closed_bf'}, inplace=True)
    
    # Check if we have prior data for Counts
    has_prior_data = df_prior is not None and 'Counts' in df_prior.get('category', df_prior.get('measure', pd.Series())).values
    
    # Get formats
    fmt = create_xlsxwriter_formats(wb)
    
    # Build headers based on whether closed count exists and whether we have prior data
    if has_closed:
        headers = [
            "Accident Period", "Current Age", "Reported", "Closed",
            "Reported CL", "Closed CL", "Reported IE", "Closed IE", "Reported BF", "Closed BF"
        ]
        data_columns = ['reported', 'closed', 'reported_cl', 'closed_cl', 'reported_ie', 'closed_ie', 'reported_bf', 'closed_bf']
    else:
        headers = [
            "Accident Period", "Current Age", "Reported",
            "Reported CL", "Reported IE", "Reported BF"
        ]
        data_columns = ['reported', 'reported_cl', 'reported_ie', 'reported_bf']
    
    # Conditionally add Prior columns
    if has_prior_data:
        headers.extend(["Prior Selection", "Prior Reasoning"])
    
    headers.extend([
        "Rules-Based AI Selection", "Rules-Based AI Reasoning",
        "Open-Ended AI Selection", "Open-Ended AI Reasoning",
        "User Selection", "User Reasoning"
    ])
    
    for c_idx, header in enumerate(headers):
        ws.write(0, c_idx, header, fmt['header'])
        ws.set_column(c_idx, c_idx, 18)
    
    # Build column map from headers list (xlsxwriter is write-only, cannot read back)
    col_map = {header: idx for idx, header in enumerate(headers)}
    
    # Set wider widths for reasoning columns
    if has_prior_data:
        prior_reason_col = col_map["Prior Reasoning"]
        ws.set_column(prior_reason_col, prior_reason_col, 30)
    rb_reason_col = col_map["Rules-Based AI Reasoning"]
    oe_reason_col = col_map["Open-Ended AI Reasoning"]
    user_reason_col = col_map["User Reasoning"]
    ws.set_column(rb_reason_col, rb_reason_col, 30)
    ws.set_column(oe_reason_col, oe_reason_col, 30)
    ws.set_column(user_reason_col, user_reason_col, 40)
    
    # Create dict of prior
    prior_dict = {}
    if has_prior_data:
        mp = df_prior[df_prior.get('category', df_prior.get('measure')) == 'Counts']
        for _, r in mp.iterrows():
            prior_dict[str(r['period'])] = {"sel": r.get('selection', r.get('selected_ultimate')), "reason": r.get('reasoning', '')}
    
    # Write rows (0-based indexing, starting at row 1)
    for r_idx, (_, row) in enumerate(df_combined.iterrows(), start=1):
        period = row['period']  # Keep original type
        
        # Period - write as number if numeric to avoid Excel warnings
        if isinstance(period, (int, float, np.integer, np.floating)):
            ws.write_number(r_idx, 0, period, fmt['label'])
        else:
            ws.write(r_idx, 0, str(period), fmt['label'])
        
        val_age = row.get('current_age')
        if pd.isna(val_age):
            ws.write_blank(r_idx, 1, None, fmt['label'])
        elif isinstance(val_age, (int, float, np.integer, np.floating)):
            ws.write_number(r_idx, 1, val_age, fmt['label'])
        else:
            ws.write(r_idx, 1, str(val_age), fmt['label'])
        
        # Data values (reported, closed, IE, CL, BF - dynamically based on what's available)
        for col_offset, col_name in enumerate(data_columns):
            val = row.get(col_name)
            if pd.isna(val): val = ""
            ws.write(r_idx, 2 + col_offset, val, fmt['data'])
        
        # Prior (only if prior data available)
        if has_prior_data:
            prior_sel = prior_dict.get(period, {}).get("sel", "")
            prior_reason = prior_dict.get(period, {}).get("reason", "")
            
            ws.write(r_idx, col_map["Prior Selection"], prior_sel, fmt['prior'])
            ws.write(r_idx, col_map["Prior Reasoning"], prior_reason, fmt['prior'])
        
        # Rules-Based AI Selection (yellow fill - will be populated by 5b script)
        ws.write(r_idx, col_map["Rules-Based AI Selection"], "", fmt['selection'])
        ws.write(r_idx, col_map["Rules-Based AI Reasoning"], "", fmt['selection'])
        
        # Open-Ended AI Selection (purple fill - will be populated by 5b script)
        ws.write(r_idx, col_map["Open-Ended AI Selection"], "", fmt['ai'])
        ws.write(r_idx, col_map["Open-Ended AI Reasoning"], "", fmt['ai'])
        
        # User Selection (blank - actuary input)
        ws.write(r_idx, col_map["User Selection"], "", fmt['user'])
        ws.write(r_idx, col_map["User Reasoning"], "", fmt['user'])




def main():
    """Create ultimates selection Excel file from projected ultimates."""
    print("Creating Ultimates.xlsx...")
    
    try:
        df_ult = pd.read_parquet(INPUT_ULTIMATES)
        print(f"Loaded ultimates from {INPUT_ULTIMATES}")
    except Exception as e:
        print(f"Error loading ultimates: {e}")
        exit(1)

    # Guard: warn if CL ultimates are missing for any loss measure — selector will fall
    # back to IE for every AY if this context is used before 2f has run successfully.
    for _m in ['Incurred Loss', 'Paid Loss']:
        if _m not in df_ult['measure'].values:
            continue
        _df_m = df_ult[df_ult['measure'] == _m]
        if 'ultimate_cl' not in _df_m.columns or _df_m['ultimate_cl'].isna().all():
            print(f"\nWARNING: ultimate_cl is all NaN for '{_m}'. "
                  f"Run 2f-chainladder-ultimates.py before this script — "
                  f"otherwise the ultimates selector will treat CL as unavailable for every AY.\n")

    df_prior = None
    # Try loading prior selections - prioritize rules-based, fall back to open-ended
    prior_loaded = False
    try:
        if pathlib.Path(PRIOR_SELECTIONS_RB).exists():
            with open(PRIOR_SELECTIONS_RB, 'r') as f:
                prior_data = json.load(f)
            df_prior = pd.DataFrame(prior_data)
            print(f"Loaded prior selections from {PRIOR_SELECTIONS_RB} (rules-based)")
            prior_loaded = True
    except Exception as e:
        print(f"  Could not load rules-based prior selections: {e}")
    
    if not prior_loaded:
        try:
            if pathlib.Path(PRIOR_SELECTIONS_OE).exists():
                with open(PRIOR_SELECTIONS_OE, 'r') as f:
                    prior_data = json.load(f)
                df_prior = pd.DataFrame(prior_data)
                print(f"Loaded prior selections from {PRIOR_SELECTIONS_OE} (open-ended)")
        except Exception as e:
            print(f"  No prior selections found: {e}")

    wb = xlsxwriter.Workbook(OUTPUT_FILE, {
        'use_future_functions': True,
        'nan_inf_to_errors': True
    })
    
    # Create Losses sheet (Incurred + Paid)
    has_loss = any(m in df_ult['measure'].values for m in ['Incurred Loss', 'Paid Loss'])
    if has_loss:
        ws = wb.add_worksheet('Losses')
        format_loss_sheet(wb, ws, df_ult, df_prior)
        print(f"  Created sheet for Losses (Incurred + Paid)")
    
    # Create Counts sheet (Reported + Closed)
    has_count = any(m in df_ult['measure'].values for m in ['Reported Count', 'Closed Count'])
    if has_count:
        ws = wb.add_worksheet('Counts')
        format_count_sheet(wb, ws, df_ult, df_prior)
        print(f"  Created sheet for Counts (Reported + Closed)")
    
    out_dir = pathlib.Path(OUTPUT_FILE).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    wb.close()
    print(f"\nSaved: {OUTPUT_FILE}")
    
    exp_md = "No Exposure data\n"
    try:
        tri_df = pd.read_parquet(INPUT_TRIANGLES)
        exp_sub = tri_df[(tri_df['measure'] == 'Exposure') & tri_df['value'].notna()]
        if not exp_sub.empty:
            # Format Exposure as simple 2-column table (period, value)
            # Exposure doesn't develop over age, so we take the last value per period
            exp_simple = exp_sub.groupby('period', observed=True).agg({'value': 'last'}).reset_index()
            exp_simple.columns = ['Period', 'Exposure']
            exp_md = df_to_markdown(exp_simple, index=False)
    except Exception:
        pass
        
    export_md_data(df_ult, exp_md)


if __name__ == "__main__":
    main()
