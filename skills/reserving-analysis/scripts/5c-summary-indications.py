"""
Script 5c: Generate Summary of Indications

Reads Ultimates.xlsx (with user or AI selections), calculates total reserves by category,
and outputs summary for PROGRESS.md and REPORT.md Section 2.

Usage (run from scripts/ directory):
    cd scripts/
    python 5c-summary-indications.py

Inputs:
    ../selections/Ultimates.xlsx          - Selected ultimates (User Selection → Rules-Based AI)
    ../ultimates/projected-ultimates.parquet - Projected ultimates with actual values
    ../processed-data/1_triangles.parquet    - Triangle data (for paid/case reserves calculation)

Outputs:
    ../selections/summary-indications.json   - JSON file with totals by category
    Printed table to console for copy/paste into PROGRESS.md and REPORT.md
"""

import json
import pandas as pd
import pathlib

from modules import config
from modules.analysis_loaders import (
    MEASURE_TO_CATEGORY,
    load_selections,
    get_exposure,
)

# Paths
INPUT_ULTIMATES_EXCEL = config.SELECTIONS + "Ultimates.xlsx"
INPUT_ULTIMATES_PARQUET = config.ULTIMATES + "projected-ultimates.parquet"
INPUT_TRIANGLES = config.PROCESSED_DATA + "1_triangles.parquet"
OUTPUT_JSON = config.SELECTIONS + "summary-indications.json"


def calculate_case_reserves(triangles_path, df_ult, sel_lookup):
    """
    Calculate case reserves by category.
    Case reserves = Incurred actual - Paid actual (for Loss)
    For counts, case reserves are not applicable (N/A).
    
    Returns dict: {category: case_reserves}
    """
    # Load triangles to get diagonal values
    if not pathlib.Path(triangles_path).exists():
        print(f"  Warning: {triangles_path} not found - cannot calculate case reserves")
        return {}
    
    tri = pd.read_parquet(triangles_path)
    tri['period'] = tri['period'].astype(str)
    tri['measure'] = tri['measure'].astype(str)
    
    # Get diagonal (latest) values for each measure
    tri['age_num'] = pd.to_numeric(tri['age'].astype(str), errors='coerce')
    diagonal = tri.sort_values('age_num').groupby(['period', 'measure']).last()['value'].to_dict()
    
    # Calculate case reserves for Loss category
    case_reserves = {}
    
    # Loss: sum(Incurred actual - Paid actual) across all periods
    loss_case = 0
    for period in df_ult[df_ult['measure'] == 'Incurred Loss']['period'].unique():
        inc_actual = diagonal.get((period, 'Incurred Loss'), 0)
        paid_actual = diagonal.get((period, 'Paid Loss'), 0)
        loss_case += (inc_actual - paid_actual)
    
    case_reserves['Losses'] = loss_case
    case_reserves['Counts'] = None  # N/A for counts
    
    return case_reserves


def main():
    """Generate summary of indications."""
    print("Generating Summary of Indications...\n")
    
    # Load selections from Ultimates.xlsx
    print(f"Reading {INPUT_ULTIMATES_EXCEL}")
    sel_lookup = load_selections(INPUT_ULTIMATES_EXCEL)
    
    if not sel_lookup:
        print("ERROR: No selections found in Ultimates.xlsx")
        print("Run ultimate selector agents and/or populate User Selection column first.")
        return
    
    # Load projected ultimates
    print(f"Reading {INPUT_ULTIMATES_PARQUET}")
    df_ult = pd.read_parquet(INPUT_ULTIMATES_PARQUET)
    df_ult['period'] = df_ult['period'].astype(str)
    df_ult['measure'] = df_ult['measure'].astype(str)
    
    # Calculate case reserves
    case_reserves = calculate_case_reserves(INPUT_TRIANGLES, df_ult, sel_lookup)
    
    # Build summary by category
    summary = {}
    
    for category in ['Losses', 'Counts']:
        # Find measures for this category
        measures = [m for m, cat in MEASURE_TO_CATEGORY.items() if cat == category]
        
        # Determine primary measure for selections and display
        if category == 'Losses':
            primary_measure = 'Incurred Loss'  # Selections are for Incurred
            paid_measure = 'Paid Loss'         # But "Paid to Date" shows Paid actual
            display_name = 'Loss'
        else:
            primary_measure = 'Reported Count'
            paid_measure = None
            display_name = 'Count'
        
        # Filter to primary measure for selections
        df_cat = df_ult[df_ult['measure'] == primary_measure].copy()
        
        if df_cat.empty:
            print(f"  Warning: No data for {primary_measure}")
            continue
        
        # Get selected ultimates for this category (based on primary measure)
        total_primary_actual = 0  # Incurred or Reported
        total_ultimate = 0
        
        for _, row in df_cat.iterrows():
            period = row['period']
            actual = row['actual']
            
            # Get selected ultimate from lookup
            sel_key = (category, period)
            selected_ult = sel_lookup.get(sel_key)
            
            if selected_ult is not None and pd.notna(actual):
                total_primary_actual += actual
                total_ultimate += selected_ult
        
        # For Loss: also get Paid actual for "Paid to Date" display
        total_paid_actual = 0
        if paid_measure:
            df_paid = df_ult[df_ult['measure'] == paid_measure].copy()
            for _, row in df_paid.iterrows():
                if pd.notna(row['actual']):
                    total_paid_actual += row['actual']
        else:
            total_paid_actual = total_primary_actual  # For Counts, same as primary
        
        # Calculate IBNR (Ultimate - Primary Actual, where Primary = Incurred or Reported)
        total_ibnr = total_ultimate - total_primary_actual
        
        # Get case reserves
        case_res = case_reserves.get(category)
        
        # Calculate total unpaid
        # For Loss: Total Unpaid = Ultimate - Paid = Case Reserves + IBNR
        # For Count: Total Unpaid ≈ IBNR (no case reserves concept)
        if case_res is not None:
            total_unpaid = total_ultimate - total_paid_actual  # Should equal case_res + IBNR
        else:
            total_unpaid = total_ibnr
        
        summary[display_name] = {
            'paid_or_reported_actual': round(total_paid_actual, 2),  # Paid for Loss, Reported for Count
            'primary_actual': round(total_primary_actual, 2),  # Incurred for Loss, Reported for Count
            'case_reserves': round(case_res, 2) if case_res is not None else None,
            'ibnr': round(total_ibnr, 2),
            'total_unpaid': round(total_unpaid, 2),
            'selected_ultimate': round(total_ultimate, 2),
            'primary_measure': primary_measure,
            'category_sheet': category,
        }
    
    # Save to JSON
    output_path = pathlib.Path(OUTPUT_JSON)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Saved summary to {OUTPUT_JSON}\n")
    
    # Print formatted table for PROGRESS.md
    print("=" * 80)
    print("COPY THIS TO PROGRESS.MD (Headline Indications section):")
    print("=" * 80)
    print()
    print("| Metric | Loss | Count |")
    print("|---|---|---|")
    
    if 'Loss' in summary and 'Count' in summary:
        loss = summary['Loss']
        count = summary['Count']
        
        # Format values
        loss_paid = f"${loss['paid_or_reported_actual']:,.0f}"
        count_reported = f"{count['paid_or_reported_actual']:,.0f}"
        
        loss_case = f"${loss['case_reserves']:,.0f}" if loss['case_reserves'] is not None else "—"
        count_case = "—"
        
        loss_ibnr = f"${loss['ibnr']:,.0f}"
        count_ibnr = f"{count['ibnr']:,.0f}" if abs(count['ibnr']) >= 0.5 else "~(1)"
        
        loss_unpaid = f"${loss['total_unpaid']:,.0f}"
        count_unpaid = f"{count['total_unpaid']:,.0f}" if abs(count['total_unpaid']) >= 0.5 else "~(1)"
        
        loss_ult = f"${loss['selected_ultimate']:,.0f}"
        count_ult = f"~{count['selected_ultimate']:,.0f}"
        
        print(f"| Paid / Reported to Date | {loss_paid} | {count_reported} |")
        print(f"| Case Reserves | {loss_case} | {count_case} |")
        print(f"| IBNR | {loss_ibnr} | {count_ibnr} |")
        print(f"| **Total Unpaid** | **{loss_unpaid}** | **{count_unpaid}** |")
        print(f"| **Selected Ultimate** | **{loss_ult}** | **{count_ult}** |")
        
        if abs(count['ibnr']) < 0.5:
            print()
            print("*(1) Count IBNR rounds to zero — reported counts essentially fully developed.*")
    
    print()
    print("=" * 80)
    print("COPY THIS TO REPORT.MD (Section 2 Summary of Indications):")
    print("=" * 80)
    print()
    print("| Segment | Paid to Date | Case Reserves | IBNR | Total Unpaid | Ultimate |")
    print("|---|---|---|---|---|---|")
    
    if 'Loss' in summary and 'Count' in summary:
        loss = summary['Loss']
        count = summary['Count']
        
        # Format values
        loss_paid = f"${loss['paid_or_reported_actual']:,.0f}"
        count_reported = f"{count['paid_or_reported_actual']:,.0f}"
        
        loss_case = f"${loss['case_reserves']:,.0f}" if loss['case_reserves'] is not None else "—"
        count_case = "—"
        
        loss_ibnr = f"${loss['ibnr']:,.0f}"
        count_ibnr = f"{count['ibnr']:,.0f}" if abs(count['ibnr']) >= 0.5 else "(1)"
        
        loss_unpaid = f"${loss['total_unpaid']:,.0f}"
        count_unpaid = f"{count['total_unpaid']:,.0f}" if abs(count['total_unpaid']) >= 0.5 else "(1)"
        
        loss_ult = f"${loss['selected_ultimate']:,.0f}"
        count_ult = f"~{count['selected_ultimate']:,.0f}"
        
        print(f"| Loss (WC) | {loss_paid} | {loss_case} | {loss_ibnr} | {loss_unpaid} | {loss_ult} |")
        print(f"| Count (Reported) | {count_reported} | {count_case} | {count_ibnr} | {count_unpaid} | {count_ult} |")
        
        if abs(count['ibnr']) < 0.5:
            print()
            print("*(1) Count IBNR rounds to zero — reported counts essentially fully developed.*")
    
    print()
    print("=" * 80)
    print(f"\n✓ Summary generation complete!")
    print(f"  JSON saved to: {OUTPUT_JSON}")
    print(f"  Tables printed above for copy/paste to PROGRESS.md and REPORT.md")
    

if __name__ == "__main__":
    main()
