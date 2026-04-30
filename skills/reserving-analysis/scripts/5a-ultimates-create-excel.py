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
from modules.xl_writers import write_ultimates_sheet_xlw

# Paths from modules/config.py — override here if needed:
INPUT_ULTIMATES  = config.ULTIMATES + "projected-ultimates.parquet"
INPUT_TRIANGLES = config.PROCESSED_DATA + "1_triangles.parquet"  # Triangle data including Exposure measure
PRIOR_SELECTIONS_RB = config.SELECTIONS + "ultimates-prior.json"             # Optional, priority 1 — set to prior cycle's selected ultimates
PRIOR_SELECTIONS_OE = config.SELECTIONS + "ultimates-prior-oe.json"          # Optional, priority 2 — fallback prior
OUTPUT_FILE      = config.SELECTIONS + "Ultimates.xlsx"
SELECTIONS_OUTPUT_PATH = config.SELECTIONS


def export_md_data(df_ult, exp_md):
    import pathlib
    # Subagents should use these markdown files as canonical context.
    # Workbook contains hard-coded values from source data.
    # 
    # CRITICAL: Include ALL method columns (CL, IE, BF, and their IBNR) so selectors can:
    # - Compare method indications at each maturity level
    # - Evaluate IBNR magnitudes and patterns
    # - Apply maturity-based weighting rules
    # - Check reasonability (loss ratios, IELR, paid-to-incurred ratios)
    #
    # Round appropriately to reduce visual clutter while preserving precision:
    # - Dollar amounts: nearest whole number
    # - Percentages (pct_developed): 4 decimals (0.9999)
    # - CDFs: 4 decimals (1.0035)
    # - Loss ratios and diagnostics: 4 decimals
    
    def round_for_display(df_m):
        """Round numeric columns for markdown display."""
        df_display = df_m.copy()
        
        # Round dollar amounts to nearest whole number
        dollar_cols = ['actual', 'ultimate_cl', 'ibnr_cl', 'ultimate_ie', 'ibnr_ie', 'ultimate_bf', 'ibnr_bf']
        for col in dollar_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].round(0)
        
        # Round percentages and ratios to 4 decimals
        ratio_cols = ['pct_developed', 'cdf']
        for col in ratio_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].round(4)
        
        return df_display
    
    # Export Loss category (Incurred + Paid)
    loss_measures = ['Incurred Loss', 'Paid Loss']
    loss_data = []
    for measure in loss_measures:
        df_m = df_ult[df_ult['measure'] == measure].copy()
        if not df_m.empty:
            # Include ALL method columns for selector context
            cols_to_keep = ['period', 'current_age', 'actual', 'cdf', 'pct_developed',
                          'ultimate_cl', 'ibnr_cl', 'ultimate_ie', 'ibnr_ie', 
                          'ultimate_bf', 'ibnr_bf']
            available_cols = [c for c in cols_to_keep if c in df_m.columns]
            df_m = df_m[available_cols]
            df_m = round_for_display(df_m)
            loss_data.append((measure, df_m))
    
    if loss_data:
        md_path = pathlib.Path(SELECTIONS_OUTPUT_PATH) / "ultimates-context-loss.md"
        md_content = "# Ultimates Context: Loss\n\n"
        md_content += "## Table of Contents\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Projected Ultimates](#projected-ultimates)\n\n"
        md_content += "## Exposure\n\n" + exp_md + "\n"
        md_content += "## Projected Ultimates\n\n"
        
        for measure, df_m in loss_data:
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
            # Include ALL method columns for selector context
            cols_to_keep = ['period', 'current_age', 'actual', 'cdf', 'pct_developed',
                          'ultimate_cl', 'ibnr_cl', 'ultimate_ie', 'ibnr_ie', 
                          'ultimate_bf', 'ibnr_bf']
            available_cols = [c for c in cols_to_keep if c in df_m.columns]
            df_m = df_m[available_cols]
            df_m = round_for_display(df_m)
            count_data.append((measure, df_m))
    
    if count_data:
        md_path = pathlib.Path(SELECTIONS_OUTPUT_PATH) / "ultimates-context-count.md"
        md_content = "# Ultimates Context: Count\n\n"
        md_content += "## Table of Contents\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Projected Ultimates](#projected-ultimates)\n\n"
        md_content += "## Exposure\n\n" + exp_md + "\n"
        md_content += "## Projected Ultimates\n\n"
        
        for measure, df_m in count_data:
            md_content += f"### {measure}\n\n"
            md_content += df_to_markdown(df_m, index=False) + "\n\n"
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"  Exported MD: {md_path}")


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
    
    loss_measures = ['Incurred Loss', 'Paid Loss']
    has_loss = any(m in df_ult['measure'].values for m in loss_measures)
    if has_loss:
        ws = wb.add_worksheet('Losses')
        write_ultimates_sheet_xlw(wb, ws, df_ult, df_prior, 'Losses', loss_measures)
        print(f"  Created sheet for Losses (Incurred + Paid)")
    
    # Create Counts sheet (Reported + Closed)
    count_measures = ['Reported Count', 'Closed Count']
    has_count = any(m in df_ult['measure'].values for m in count_measures)
    if has_count:
        ws = wb.add_worksheet('Counts')
        write_ultimates_sheet_xlw(wb, ws, df_ult, df_prior, 'Counts', count_measures)
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
            exp_simple['value'] = exp_simple['value'].round(0)  # Round to whole numbers
            exp_simple.columns = ['period', 'exposure']
            exp_md = df_to_markdown(exp_simple, index=False)
    except Exception:
        pass
        
    export_md_data(df_ult, exp_md)


if __name__ == "__main__":
    main()
