# Creates a formatted Excel workbook for tail factor review and selection. Each measure gets its
# own sheet with observed data, scenario comparisons, and selection areas for actuarial judgment.

"""
goal: Create Chain Ladder Selections - Tail.xlsx for actuarial tail factor review and selection.
      This file should be manually edited by the actuary to make tail factor selections.

Sheet layout per measure:
  - Section A: Triangle Type Banner (measure name + key stats)
  - Section B: Observed Factors Table (AY x age triangle + weighted avg + CV)
  - Section C: Scenario Comparison Table (method x starting_age scenarios with diagnostics)
  - Section D: Selection Area (prior, rule-based, AI, final selection rows)

run-note: When copied to a project, run from the scripts/ directory:
    cd scripts/
    python 2d-tail-create-excel.py
"""

import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pathlib import Path

from modules import config
from modules.xl_styles import (
    SUBHEADER_FILL, SELECTION_FILL, PRIOR_FILL, AI_FILL, USER_FILL,
    SUBHEADER_FONT, LABEL_FONT, DATA_FONT,
    THIN_BORDER, style_header,
)
from modules.markdown_utils import df_to_markdown

# Paths
TAIL_SCENARIOS_PATH = config.PROCESSED_DATA + "tail-scenarios.parquet"
ENHANCED_PATH = config.PROCESSED_DATA + "2_enhanced.parquet"
DIAGNOSTICS_PATH = config.PROCESSED_DATA + "3_diagnostics.parquet"
SELECTIONS_OUTPUT_PATH = config.SELECTIONS
OUTPUT_FILE_NAME = "Chain Ladder Selections - Tail.xlsx"

# Colors for scenario comparison rows
GREEN_FILL = PatternFill("solid", fgColor="C6E0B4")   # good scenario
YELLOW_FILL = PatternFill("solid", fgColor="FFE699")  # marginal scenario
RED_FILL = PatternFill("solid", fgColor="F4B084")     # poor scenario

# Triangle type expectations (for banner notes)
TRIANGLE_TYPE_NOTES = {
    'Paid Loss': 'Paid loss tails typically longer than incurred',
    'Incurred Loss': 'Incurred loss tails typically shorter than paid',
    'Closed Count': 'Closure tails similar to paid loss',
    'Reported Count': 'Reported count tails similar to incurred loss',
}


def get_type_note(measure):
    """Return type-specific note for measure banner."""
    for key, note in TRIANGLE_TYPE_NOTES.items():
        if key.lower() in measure.lower():
            return note
    return ''


def write_section_header(ws, row, col_span, title, level="section"):
    """Write a section header spanning multiple columns."""
    cell = ws.cell(row=row, column=1, value=title)
    style_header(cell, level)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=col_span)
    return row + 1


def write_banner_section(ws, start_row, measure, df_enhanced, df_diagnostics):
    """Section A: Triangle Type Banner with measure name and key stats."""
    row = write_section_header(ws, start_row, 12, measure, "header")
    
    type_note = get_type_note(measure)
    if type_note:
        cell = ws.cell(row=row, column=1, value=type_note)
        cell.font = Font(italic=True, size=9)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=12)
        row += 1
    
    # Key stats row
    df_m = df_enhanced[df_enhanced['measure'] == measure].copy()
    if not df_m.empty:
        max_age = df_m['age'].max()
        n_ays = df_m['period'].nunique()
        
        # Get closure rate from diagnostics at last age if available (diagnostics are shared, no measure filter)
        closure_pct = None
        if 'claim_closure_rate' in df_diagnostics.columns:
            last_age_diag = df_diagnostics[df_diagnostics['age'] == max_age]
            if not last_age_diag.empty:
                closure_rate = last_age_diag['claim_closure_rate'].iloc[0]
                if pd.notna(closure_rate):
                    closure_pct = closure_rate * 100
        
        # Last observed avg LDF
        last_ldf = None
        if 'ldf' in df_m.columns:
            max_interval = df_m['interval'].max()
            last_ldfs = df_m[df_m['interval'] == max_interval]['ldf'].dropna()
            if not last_ldfs.empty:
                last_ldf = last_ldfs.mean()
        
        stats_labels = ['Max Observed Age:', 'Accident Years:', 'Closure % at Last Age:', 'Last Observed Avg LDF:']
        stats_values = [
            max_age,
            n_ays,
            f"{closure_pct:.1f}%" if closure_pct is not None else 'N/A',
            f"{last_ldf:.4f}" if last_ldf is not None else 'N/A'
        ]
        
        for i, (label, value) in enumerate(zip(stats_labels, stats_values)):
            col = i * 3 + 1
            label_cell = ws.cell(row=row, column=col, value=label)
            label_cell.font = LABEL_FONT
            label_cell.alignment = Alignment(horizontal="right")
            
            value_cell = ws.cell(row=row, column=col+1, value=value)
            value_cell.font = DATA_FONT
            value_cell.alignment = Alignment(horizontal="left")
        
        row += 1
    
    return row + 1


def write_observed_factors_section(ws, start_row, measure, df_enhanced):
    """Section B: Observed Factors Table (triangle + simple avg + CV)."""
    df_m = df_enhanced[df_enhanced['measure'] == measure].copy()
    if df_m.empty:
        return start_row
    
    periods = sorted(df_m['period'].unique())
    if hasattr(df_m['age'], 'cat'):
        ages = [a for a in df_m['age'].cat.categories if a in df_m['age'].values and pd.notna(a)]
    else:
        ages = sorted([a for a in df_m['age'].unique() if pd.notna(a)], key=lambda x: int(str(x)))
    
    row = write_section_header(ws, start_row, len(ages) + 1, "Observed Age-to-Age Factors", "section")
    
    ws.cell(row=row, column=1, value="Accident Year").border = THIN_BORDER
    ws.cell(row=row, column=1).font = SUBHEADER_FONT
    ws.cell(row=row, column=1).fill = SUBHEADER_FILL
    ws.cell(row=row, column=1).alignment = Alignment(horizontal="center")
    
    for c_idx, age in enumerate(ages, start=2):
        cell = ws.cell(row=row, column=c_idx, value=age)
        style_header(cell, "subheader")
    row += 1
    
    factor_dict = {}
    for _, r in df_m[df_m['ldf'].notna()].iterrows():
        key = (str(r['period']), r['age'])
        factor_dict[key] = r['ldf']
    
    data_start_row = row
    for period in periods:
        period_cell = ws.cell(row=row, column=1, value=period)
        period_cell.font = LABEL_FONT
        period_cell.alignment = Alignment(horizontal="left")
        period_cell.border = THIN_BORDER
        
        for c_idx, age in enumerate(ages, start=2):
            val = factor_dict.get((str(period), age))
            cell = ws.cell(row=row, column=c_idx, value=val)
            cell.font = DATA_FONT
            cell.alignment = Alignment(horizontal="right")
            cell.border = THIN_BORDER
            if val is not None:
                cell.number_format = "0.0000"
        row += 1
    data_end_row = row - 1
    
    avg_cell = ws.cell(row=row, column=1, value="Average")
    avg_cell.font = LABEL_FONT
    avg_cell.border = THIN_BORDER
    for c_idx, age in enumerate(ages, start=2):
        col_letter = get_column_letter(c_idx)
        rng = f"{col_letter}{data_start_row}:{col_letter}{data_end_row}"
        cell = ws.cell(row=row, column=c_idx, value=f"=IFERROR(AVERAGE({rng}),"")")
        cell.font = DATA_FONT
        cell.alignment = Alignment(horizontal="right")
        cell.border = THIN_BORDER
        cell.number_format = "0.0000"
    row += 1
    
    cv_cell = ws.cell(row=row, column=1, value="CV")
    cv_cell.font = LABEL_FONT
    cv_cell.border = THIN_BORDER
    for c_idx, age in enumerate(ages, start=2):
        col_letter = get_column_letter(c_idx)
        rng = f"{col_letter}{data_start_row}:{col_letter}{data_end_row}"
        cell = ws.cell(row=row, column=c_idx, value=f"=IFERROR(STDEV.S({rng})/AVERAGE({rng}),"")")
        cell.font = DATA_FONT
        cell.alignment = Alignment(horizontal="right")
        cell.border = THIN_BORDER
        cell.number_format = "0.0000"
    row += 1
    
    return row + 1


def get_scenario_color(row_data):
    """Determine row color based on scenario quality diagnostics."""
    # Green if: monotone AND no slope breaks AND good R² AND no gap AND materiality ok
    # Yellow: marginal (Bondy/Modified Bondy always yellow since no R²)
    # Red: poor quality
    
    # Helper to safely convert boolean (handles pandas NA)
    def safe_bool(val):
        if pd.isna(val):
            return False
        return bool(val)
    
    is_monotone = safe_bool(row_data.get('is_monotone_from_here', False))
    slope_breaks = row_data.get('slope_sign_changes', 999)
    if pd.isna(slope_breaks):
        slope_breaks = 999
    r_squared = row_data.get('r_squared')
    gap_flag = safe_bool(row_data.get('gap_flag', True))
    materiality_ok = safe_bool(row_data.get('materiality_ok', False))
    method = row_data.get('method', '')
    
    # Bondy variants have no R² - always yellow
    if 'bondy' in method.lower():
        return YELLOW_FILL
    
    # Green: high quality scenario
    if (is_monotone and slope_breaks == 0 and 
        r_squared is not None and not pd.isna(r_squared) and r_squared > 0.85 and 
        not gap_flag and materiality_ok):
        return GREEN_FILL
    
    # Red: poor quality
    if (not is_monotone or slope_breaks > 0 or 
        (r_squared is not None and not pd.isna(r_squared) and r_squared < 0.70) or gap_flag):
        return RED_FILL
    
    # Yellow: marginal
    return YELLOW_FILL


def write_scenario_comparison_section(ws, start_row, measure, df_scenarios):
    """Section C: Scenario Comparison Table with diagnostics."""
    df_m = df_scenarios[df_scenarios['measure'] == measure].copy()
    if df_m.empty:
        return start_row
    
    col_headers = [
        'Starting Age', 'Monotone', 'CV', 'Slope Breaks', 'Method', 'Params',
        'Tail Factor', 'R2', 'LOO Std Dev', 'Gap to Last', 'Gap Flag',
        '% of CDF', 'Materiality OK', '+10% Reserve Delta', '+20% Reserve Delta'
    ]
    
    row = write_section_header(ws, start_row, len(col_headers), "Scenario Comparison", "section")
    
    # Header row
    for c_idx, header in enumerate(col_headers, start=1):
        cell = ws.cell(row=row, column=c_idx, value=header)
        style_header(cell, "subheader")
    row += 1
    
    # Sort scenarios by starting_age then method
    df_m = df_m.sort_values(['starting_age', 'method'])
    
    # Data rows
    for _, scenario in df_m.iterrows():
        row_fill = get_scenario_color(scenario)
        
        # Helper to safely convert boolean columns (handles pandas NA)
        def safe_bool(val):
            if pd.isna(val):
                return False
            return bool(val)
        
        values = [
            scenario['starting_age'],
            'Y' if safe_bool(scenario.get('is_monotone_from_here', False)) else 'N',
            scenario.get('cv_at_starting_age'),
            scenario.get('slope_sign_changes', 0),
            scenario['method'],
            str(scenario.get('method_params', '')) if pd.notna(scenario.get('method_params')) else '',
            scenario['tail_factor'],
            scenario.get('r_squared'),
            scenario.get('loo_std_dev'),
            scenario.get('gap_to_last_observed'),
            'Y' if safe_bool(scenario.get('gap_flag', False)) else 'N',
            scenario.get('pct_of_cdf'),
            'Y' if safe_bool(scenario.get('materiality_ok', False)) else 'N',
            scenario.get('sensitivity_plus10_reserve_delta'),
            scenario.get('sensitivity_plus20_reserve_delta'),
        ]
        
        for c_idx, val in enumerate(values, start=1):
            cell = ws.cell(row=row, column=c_idx, value=val)
            cell.font = DATA_FONT
            cell.alignment = Alignment(horizontal="right" if isinstance(val, (int, float)) else "left")
            cell.border = THIN_BORDER
            cell.fill = row_fill
            
            # Number formatting
            if c_idx == 1:  # Starting Age
                cell.number_format = "0"
            elif c_idx == 3:  # CV
                if val is not None:
                    cell.number_format = "0.0000"
            elif c_idx == 7:  # Tail Factor
                if val is not None:
                    cell.number_format = "0.0000"
            elif c_idx in [8, 9, 10]:  # R2, LOO Std Dev, Gap
                if val is not None:
                    cell.number_format = "0.0000"
            elif c_idx == 12:  # % of CDF
                if val is not None:
                    cell.number_format = "0.00%"
            elif c_idx in [14, 15]:  # Reserve deltas
                if val is not None:
                    cell.number_format = "#,##0"
        
        row += 1
    
    return row + 1


def write_selection_section(ws, start_row, measure, prior_selections=None):
    """Section D: Selection Area (prior, rules-based AI, open-ended AI, user selection)."""
    row = write_section_header(ws, start_row, 6, "Tail Factor Selection", "section")
    
    headers = ['Label', 'Cutoff Age', 'Tail Factor', 'Method', 'Reasoning', 'Additional Notes']
    for c_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=c_idx, value=header)
        style_header(cell, "subheader")
    row += 1
    
    if prior_selections is not None:
        prior_m = prior_selections[prior_selections['measure'] == measure]
        if not prior_m.empty:
            prior_row = prior_m.iloc[0]
            values = [
                'Prior Selection',
                prior_row.get('cutoff_age', ''),
                prior_row.get('tail_factor', ''),
                prior_row.get('method', ''),
                prior_row.get('reasoning', ''),
                ''
            ]
            for c_idx, val in enumerate(values, start=1):
                cell = ws.cell(row=row, column=c_idx, value=val)
                cell.fill = PRIOR_FILL
                cell.border = THIN_BORDER
                cell.font = DATA_FONT
                cell.alignment = Alignment(horizontal="left", wrap_text=True)
                if c_idx in [2, 3] and val:
                    cell.number_format = "0.0000" if c_idx == 3 else "0"
            
            prior_data_row = row
            user_data_row = row + 7
            row += 1
            
            cell = ws.cell(row=row, column=1, value="Prior Delta")
            cell.fill = PRIOR_FILL
            cell.border = THIN_BORDER
            cell.font = LABEL_FONT
            for c_idx in range(2, 7):
                cell = ws.cell(row=row, column=c_idx, value='')
                cell.fill = PRIOR_FILL
                cell.border = THIN_BORDER
                if c_idx == 3:
                    cell.value = f"=IFERROR(C{user_data_row}-C{prior_data_row}, "")"
                    cell.number_format = "0.0000"
            ws.cell(row=row, column=5, value="(current - prior)").font = Font(italic=True, size=8)
            row += 1
            
            row += 1
    
    cell = ws.cell(row=row, column=1, value="Rules-Based AI Selection")
    style_header(cell, "selection")
    for c_idx in range(2, 7):
        cell = ws.cell(row=row, column=c_idx, value='')
        cell.fill = SELECTION_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="left", wrap_text=True)
    row += 1
    
    cell = ws.cell(row=row, column=1, value="Open-Ended AI Selection")
    style_header(cell, "ai")
    for c_idx in range(2, 7):
        cell = ws.cell(row=row, column=c_idx, value='')
        cell.fill = AI_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="left", wrap_text=True)
    row += 1
    
    row += 1
    
    cell = ws.cell(row=row, column=1, value="User Selection")
    style_header(cell, "user")
    for c_idx in range(2, 7):
        cell = ws.cell(row=row, column=c_idx, value='')
        cell.fill = USER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="left", wrap_text=True)
    row += 1
    
    return row + 1



def build_measure_sheet(ws, measure, df_scenarios, df_enhanced, df_diagnostics, prior_selections=None):
    """Build complete sheet for one measure."""
    row = 1
    
    # Section A: Banner
    row = write_banner_section(ws, row, measure, df_enhanced, df_diagnostics)
    
    # Section B: Observed Factors
    row = write_observed_factors_section(ws, row, measure, df_enhanced)
    
    # Section C: Scenario Comparison
    row = write_scenario_comparison_section(ws, row, measure, df_scenarios)
    
    # Section D: Selection Area
    row = write_selection_section(ws, row, measure, prior_selections)
    
    # Column widths
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 25
    ws.column_dimensions['F'].width = 30



def export_md_data(measures, df_scenarios, df_enhanced, df_diagnostics, exp_md):
    # Subagents should use these markdown files as canonical context.
    # The workbook can include formulas that are not recalculated in headless runs,
    # which makes direct Excel reads unreliable for selection inputs.
    for measure in measures:
        safe_name = measure.lower().replace(' ', '_')
        md_path = Path(SELECTIONS_OUTPUT_PATH) / f"tail-context-{safe_name}.md"
        
        scen_sub = df_scenarios[df_scenarios['measure'] == measure].drop(columns=['measure'], errors='ignore')
        scen_md = df_to_markdown(scen_sub, index=False)
        
        obs_sub = df_enhanced[df_enhanced['measure'] == measure][['period', 'age', 'ldf']].dropna()
        if not obs_sub.empty:
            obs_piv = obs_sub.pivot(index='period', columns='age', values='ldf')
            obs_md = df_to_markdown(obs_piv, index=True)
        else:
            obs_md = "No data\n"
            
        md_content = f"# Tail Context: {measure}\n\n"
        md_content += "## Table of Contents\n"
        md_content += "- [Exposure](#exposure)\n"
        md_content += "- [Scenarios](#scenarios)\n"
        md_content += "- [Observed Factors](#observed-factors)\n\n"
        md_content += "## Exposure\n" + exp_md + "\n"
        md_content += "## Scenarios\n" + scen_md + "\n"
        md_content += "## Observed Factors\n" + obs_md + "\n"
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        print(f"  Exported MD: {md_path}")

def main():
    """Create Tail Factor Selections Excel file."""
    output_file = SELECTIONS_OUTPUT_PATH + OUTPUT_FILE_NAME
    if Path(output_file).exists():
        raise FileExistsError(
            f"Output file already exists: {output_file}\n"
            "Delete or rename the file before re-running to avoid overwriting manual edits."
        )
    
    if not Path(TAIL_SCENARIOS_PATH).exists():
        raise FileNotFoundError(
            f"Tail scenarios file not found: {TAIL_SCENARIOS_PATH}\n"
            "Run 2c-tail-methods-diagnostics.py first to generate tail scenarios."
        )
    
    print("Loading data...")
    df_scenarios = pd.read_parquet(TAIL_SCENARIOS_PATH)
    df_enhanced = pd.read_parquet(ENHANCED_PATH)
    df_diagnostics = pd.read_parquet(DIAGNOSTICS_PATH)
    
    print(f"  {len(df_scenarios)} tail scenarios")
    print(f"  {len(df_enhanced)} enhanced rows")
    print(f"  {len(df_diagnostics)} diagnostic rows")
    
    # Load prior selections if available
    prior_selections_path = Path(config.SELECTIONS) / "tail-factor-prior.csv"
    df_prior = None
    if prior_selections_path.exists():
        df_prior = pd.read_csv(prior_selections_path)
        print(f"  {len(df_prior)} prior tail selections loaded")
    else:
        print("  No prior tail selections found (optional)")
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    
    raw_measures = sorted(df_scenarios['measure'].unique())
    
    exp_sub = df_enhanced[(df_enhanced['measure'] == 'Exposure') & df_enhanced['value'].notna()]
    if not exp_sub.empty:
        # Format Exposure as simple 2-column table (period, value)
        # Exposure doesn't develop over age, so we take the last value per period
        exp_simple = exp_sub.groupby('period', observed=True).agg({'value': 'last'}).reset_index()
        exp_simple.columns = ['Period', 'Exposure']
        exp_md = df_to_markdown(exp_simple, index=False)
    else:
        exp_md = "No Exposure data\n"
        
    measures = [m for m in raw_measures if m != 'Exposure']
    
    print(f"\nCreating sheets for measures: {measures}")
    
    for measure in measures:
        ws = wb.create_sheet(title=measure[:31])
        build_measure_sheet(ws, measure, df_scenarios, df_enhanced, df_diagnostics, df_prior)
        print(f"  Built sheet: {measure[:31]}")
    
    wb.save(output_file)
    export_md_data(measures, df_scenarios, df_enhanced, df_diagnostics, exp_md)
    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    main()
