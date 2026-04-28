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
import numpy as np
import xlsxwriter
from pathlib import Path

from modules import config
from modules.xl_styles import create_xlsxwriter_formats, COLORS
from modules.markdown_utils import df_to_markdown

# Paths
TAIL_SCENARIOS_PATH = config.PROCESSED_DATA + "tail-scenarios.parquet"
ENHANCED_PATH = config.PROCESSED_DATA + "2_enhanced.parquet"
DIAGNOSTICS_PATH = config.PROCESSED_DATA + "3_diagnostics.parquet"
SELECTIONS_OUTPUT_PATH = config.SELECTIONS
OUTPUT_FILE_NAME = "Chain Ladder Selections - Tail.xlsx"

# Colors for scenario comparison rows (xlsxwriter format)
SCENARIO_COLORS = {
    'green': '#C6E0B4',   # good scenario
    'yellow': '#FFE699',  # marginal scenario
    'red': '#F4B084'      # poor scenario
}

# Triangle type expectations (for banner notes)
TRIANGLE_TYPE_NOTES = {
    'Paid Loss': 'Paid loss tails typically longer than incurred',
    'Incurred Loss': 'Incurred loss tails typically shorter than paid',
    'Closed Count': 'Closure tails similar to paid loss',
    'Reported Count': 'Reported count tails similar to incurred loss',
}


def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter (A, B, C, etc.)"""
    result = ''
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result


def get_type_note(measure):
    """Return type-specific note for measure banner."""
    for key, note in TRIANGLE_TYPE_NOTES.items():
        if key.lower() in measure.lower():
            return note
    return ''


def write_section_header(ws, row, col_span, title, fmt, level="section"):
    """Write a section header spanning multiple columns."""
    format_key = {'header': 'header', 'section': 'section', 'subheader': 'subheader'}.get(level, 'section')
    header_fmt = fmt.get(format_key, fmt['section'])
    
    ws.merge_range(row, 0, row, col_span - 1, title, header_fmt)
    return row + 1


def write_banner_section(ws, start_row, measure, df_enhanced, df_diagnostics, fmt):
    """Section A: Triangle Type Banner with measure name and key stats."""
    # Create header format if needed
    if 'header' not in fmt:
        fmt['header'] = fmt['wb'].add_format({
            'bold': True,
            'bg_color': '#' + COLORS['header_blue'],
            'font_color': 'FFFFFF',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
    
    row = write_section_header(ws, start_row, 12, measure, fmt, "header")
    
    type_note = get_type_note(measure)
    if type_note:
        note_fmt = fmt['wb'].add_format({'italic': True, 'font_size': 9})
        ws.merge_range(row, 0, row, 11, type_note, note_fmt)
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
        
        label_fmt = fmt['wb'].add_format({'bold': True, 'font_size': 9, 'align': 'right'})
        value_fmt = fmt['wb'].add_format({'font_size': 9, 'align': 'left'})
        
        for i, (label, value) in enumerate(zip(stats_labels, stats_values)):
            col = i * 3
            ws.write(row, col, label, label_fmt)
            ws.write(row, col + 1, value, value_fmt)
        
        row += 1
    
    return row + 1


def write_observed_factors_section(ws, start_row, measure, df_enhanced, fmt):
    """Section B: Observed Factors Table (triangle + formulas for avg + CV with cached values)."""
    df_m = df_enhanced[df_enhanced['measure'] == measure].copy()
    if df_m.empty:
        return start_row
    
    periods = sorted(df_m['period'].unique())
    if hasattr(df_m['age'], 'cat'):
        ages = [a for a in df_m['age'].cat.categories if a in df_m['age'].values and pd.notna(a)]
    else:
        ages = sorted([a for a in df_m['age'].unique() if pd.notna(a)], key=lambda x: int(str(x)))
    
    row = write_section_header(ws, start_row, len(ages) + 1, "Observed Age-to-Age Factors", fmt, "section")
    
    # Header row
    ws.write(row, 0, "Accident Year", fmt['subheader'])
    
    for c_idx, age in enumerate(ages, start=1):
        # Write age as number if numeric to avoid Excel "number formatted as text" warnings
        if isinstance(age, (int, float, np.integer, np.floating)):
            ws.write_number(row, c_idx, age, fmt['subheader'])
        else:
            ws.write(row, c_idx, age, fmt['subheader'])
    row += 1
    
    # Build factor dict from source data
    factor_dict = {}
    for _, r in df_m[df_m['ldf'].notna()].iterrows():
        key = (str(r['period']), r['age'])
        factor_dict[key] = r['ldf']
    
    data_start_row = row
    for period in periods:
        # Write period as number if numeric to avoid Excel warnings
        if isinstance(period, (int, float, np.integer, np.floating)):
            ws.write_number(row, 0, period, fmt['label'])
        else:
            ws.write(row, 0, period, fmt['label'])
        
        for c_idx, age in enumerate(ages, start=1):
            val = factor_dict.get((str(period), age))
            if val is not None:
                ws.write(row, c_idx, val, fmt['data_ldf'])
            else:
                ws.write(row, c_idx, '', fmt['data'])
        row += 1
    data_end_row = row - 1
    
    # Average row with formulas and cached values
    ws.write(row, 0, "Average", fmt['label'])
    for c_idx, age in enumerate(ages, start=1):
        col_ltr = col_letter(c_idx)
        formula = f"=IFERROR(AVERAGE({col_ltr}{data_start_row+1}:{col_ltr}{data_end_row+1}),\"\")"
        
        # Calculate cached value from dataframe
        age_ldfs = df_m[(df_m['age'] == age) & df_m['ldf'].notna()]['ldf']
        cached_value = age_ldfs.mean() if not age_ldfs.empty else None
        
        ws.write_formula(row, c_idx, formula, fmt['data_ldf'], cached_value)
    row += 1
    
    # CV row with formulas and cached values
    ws.write(row, 0, "CV", fmt['label'])
    for c_idx, age in enumerate(ages, start=1):
        col_ltr = col_letter(c_idx)
        formula = f"=IFERROR(STDEV.S({col_ltr}{data_start_row+1}:{col_ltr}{data_end_row+1})/AVERAGE({col_ltr}{data_start_row+1}:{col_ltr}{data_end_row+1}),\"\")"
        
        # Calculate cached value from dataframe
        age_ldfs = df_m[(df_m['age'] == age) & df_m['ldf'].notna()]['ldf']
        if not age_ldfs.empty and len(age_ldfs) > 1:
            avg = age_ldfs.mean()
            std = age_ldfs.std(ddof=1)
            cached_value = std / avg if avg != 0 else None
        else:
            cached_value = None
        
        ws.write_formula(row, c_idx, formula, fmt['data_ldf'], cached_value)
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
        return SCENARIO_COLORS['yellow']
    
    # Green: high quality scenario
    if (is_monotone and slope_breaks == 0 and 
        r_squared is not None and not pd.isna(r_squared) and r_squared > 0.85 and 
        not gap_flag and materiality_ok):
        return SCENARIO_COLORS['green']
    
    # Red: poor quality
    if (not is_monotone or slope_breaks > 0 or 
        (r_squared is not None and not pd.isna(r_squared) and r_squared < 0.70) or gap_flag):
        return SCENARIO_COLORS['red']
    
    # Yellow: marginal
    return SCENARIO_COLORS['yellow']


def write_scenario_comparison_section(ws, start_row, measure, df_scenarios, fmt):
    """Section C: Scenario Comparison Table with diagnostics."""
    df_m = df_scenarios[df_scenarios['measure'] == measure].copy()
    if df_m.empty:
        return start_row
    
    col_headers = [
        'Starting Age', 'Monotone', 'CV', 'Slope Breaks', 'Method', 'Params',
        'Tail Factor', 'R2', 'LOO Std Dev', 'Gap to Last', 'Gap Flag',
        '% of CDF', 'Materiality OK', '+10% Reserve Delta', '+20% Reserve Delta'
    ]
    
    row = write_section_header(ws, start_row, len(col_headers), "Scenario Comparison", fmt, "section")
    
    # Header row
    for c_idx, header in enumerate(col_headers):
        ws.write(row, c_idx, header, fmt['subheader'])
    row += 1
    
    # Sort scenarios by starting_age then method
    df_m = df_m.sort_values(['starting_age', 'method'])
    
    # Data rows
    for _, scenario in df_m.iterrows():
        row_color = get_scenario_color(scenario)
        row_fmt = fmt['wb'].add_format({
            'border': 1,
            'bg_color': row_color,
            'align': 'right',
            'valign': 'vcenter',
            'font_size': 9
        })
        row_fmt_text = fmt['wb'].add_format({
            'border': 1,
            'bg_color': row_color,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 9
        })
        
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
        
        for c_idx, val in enumerate(values):
            cell_fmt = row_fmt_text if c_idx in [4, 5] else row_fmt  # Method and Params are text
            
            # Number formatting
            if c_idx == 1:  # Starting Age
                num_fmt = fmt['wb'].add_format({
                    'border': 1,
                    'bg_color': row_color,
                    'align': 'right',
                    'num_format': '0'
                })
                ws.write(row, c_idx, val, num_fmt)
            elif c_idx == 3:  # CV
                if val is not None:
                    num_fmt = fmt['wb'].add_format({
                        'border': 1,
                        'bg_color': row_color,
                        'align': 'right',
                        'num_format': '0.0000'
                    })
                    ws.write(row, c_idx, val, num_fmt)
                else:
                    ws.write(row, c_idx, '', row_fmt)
            elif c_idx == 7:  # Tail Factor
                if val is not None:
                    num_fmt = fmt['wb'].add_format({
                        'border': 1,
                        'bg_color': row_color,
                        'align': 'right',
                        'num_format': '0.0000'
                    })
                    ws.write(row, c_idx, val, num_fmt)
                else:
                    ws.write(row, c_idx, '', row_fmt)
            elif c_idx in [8, 9, 10]:  # R2, LOO Std Dev, Gap
                if val is not None:
                    num_fmt = fmt['wb'].add_format({
                        'border': 1,
                        'bg_color': row_color,
                        'align': 'right',
                        'num_format': '0.0000'
                    })
                    ws.write(row, c_idx, val, num_fmt)
                else:
                    ws.write(row, c_idx, '', row_fmt)
            elif c_idx == 12:  # % of CDF
                if val is not None:
                    num_fmt = fmt['wb'].add_format({
                        'border': 1,
                        'bg_color': row_color,
                        'align': 'right',
                        'num_format': '0.00%'
                    })
                    ws.write(row, c_idx, val, num_fmt)
                else:
                    ws.write(row, c_idx, '', row_fmt)
            elif c_idx in [14, 15]:  # Reserve deltas
                if val is not None:
                    num_fmt = fmt['wb'].add_format({
                        'border': 1,
                        'bg_color': row_color,
                        'align': 'right',
                        'num_format': '#,##0'
                    })
                    ws.write(row, c_idx, val, num_fmt)
                else:
                    ws.write(row, c_idx, '', row_fmt)
            else:
                ws.write(row, c_idx, val, cell_fmt)
        
        row += 1
    
    return row + 1


def write_selection_section(ws, start_row, measure, fmt, prior_selections=None):
    """Section D: Selection Area (prior, rules-based AI, open-ended AI, user selection)."""
    row = write_section_header(ws, start_row, 6, "Tail Factor Selection", fmt, "section")
    
    headers = ['Label', 'Cutoff Age', 'Tail Factor', 'Method', 'Reasoning', 'Additional Notes']
    for c_idx, header in enumerate(headers):
        ws.write(row, c_idx, header, fmt['subheader'])
    row += 1
    
    # Prior selection row
    if prior_selections is not None:
        prior_m = prior_selections[prior_selections['measure'] == measure]
        if not prior_m.empty:
            prior_row_data = prior_m.iloc[0]
            values = [
                'Prior Selection',
                prior_row_data.get('cutoff_age', ''),
                prior_row_data.get('tail_factor', ''),
                prior_row_data.get('method', ''),
                prior_row_data.get('reasoning', ''),
                ''
            ]
            
            for c_idx, val in enumerate(values):
                if c_idx == 0:  # Label column
                    ws.write(row, c_idx, val, fmt['prior'])
                elif c_idx == 1 and val:  # Cutoff Age
                    num_fmt = fmt['wb'].add_format({
                        'bg_color': '#' + COLORS['prior_yellow'],
                        'border': 1,
                        'align': 'right',
                        'num_format': '0'
                    })
                    ws.write(row, c_idx, val, num_fmt)
                elif c_idx == 2 and val:  # Tail Factor
                    ws.write(row, c_idx, val, fmt['prior_data'])
                elif c_idx in [3, 4, 5]:  # Text columns
                    ws.write(row, c_idx, val, fmt['prior_text'])
                else:
                    ws.write(row, c_idx, val, fmt['prior'])
            
            prior_data_row = row + 1  # xlsxwriter is 0-based, formula needs 1-based
            user_data_row = row + 8  # Will be 7 rows down after all AI selections
            row += 1
            
            # Prior Delta row with formula
            ws.write(row, 0, "Prior Delta", fmt['prior'])
            for c_idx in range(1, 6):
                if c_idx == 2:  # Tail Factor delta formula with cached value
                    formula = f"=IFERROR(C{user_data_row}-C{prior_data_row}, \"\")"
                    # We don't know user selection yet, so no cached value (will show blank until user fills)
                    ws.write_formula(row, c_idx, formula, fmt['prior_data'], None)
                else:
                    ws.write(row, c_idx, '', fmt['prior'])
            
            # Add note in Reasoning column
            note_fmt = fmt['wb'].add_format({
                'bg_color': '#' + COLORS['prior_yellow'],
                'border': 1,
                'italic': True,
                'font_size': 8,
                'align': 'left'
            })
            ws.write(row, 4, "(current - prior)", note_fmt)
            row += 1
            
            row += 1  # Blank row
    
    # Rules-Based AI Selection row
    ws.write(row, 0, "Rules-Based AI Selection", fmt['selection'])
    for c_idx in range(1, 6):
        ws.write(row, c_idx, '', fmt['selection_text'])
    row += 1
    
    # Open-Ended AI Selection row
    ws.write(row, 0, "Open-Ended AI Selection", fmt['ai'])
    for c_idx in range(1, 6):
        ws.write(row, c_idx, '', fmt['ai_text'])
    row += 1
    
    row += 1  # Blank row
    
    # User Selection row
    ws.write(row, 0, "User Selection", fmt['user'])
    for c_idx in range(1, 6):
        ws.write(row, c_idx, '', fmt['user_text'])
    row += 1
    
    return row + 1



def build_measure_sheet(ws, measure, df_scenarios, df_enhanced, df_diagnostics, fmt, prior_selections=None):
    """Build complete sheet for one measure."""
    row = 1
    
    # Section A: Banner
    row = write_banner_section(ws, row, measure, df_enhanced, df_diagnostics, fmt)
    
    # Section B: Observed Factors
    row = write_observed_factors_section(ws, row, measure, df_enhanced, fmt)
    
    # Section C: Scenario Comparison
    row = write_scenario_comparison_section(ws, row, measure, df_scenarios, fmt)
    
    # Section D: Selection Area
    row = write_selection_section(ws, row, measure, fmt, prior_selections)
    
    # Column widths (xlsxwriter uses 0-based indexing for columns)
    ws.set_column(0, 0, 30)  # A: Label
    ws.set_column(1, 1, 12)  # B: Cutoff Age
    ws.set_column(2, 2, 12)  # C: Tail Factor
    ws.set_column(3, 3, 15)  # D: Method
    ws.set_column(4, 4, 25)  # E: Reasoning
    ws.set_column(5, 5, 30)  # F: Additional Notes



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
    
    # Create workbook with xlsxwriter
    wb = xlsxwriter.Workbook(output_file, {
        'use_future_functions': True,
        'nan_inf_to_errors': True  # Convert NaN/INF to Excel errors instead of failing
    })
    fmt = create_xlsxwriter_formats(wb)
    fmt['wb'] = wb  # Store reference for dynamic format creation
    
    raw_measures = sorted(df_scenarios['measure'].unique())
    
    exp_sub = df_enhanced[(df_enhanced['measure'] == 'Exposure') & df_enhanced['value'].notna()]
    if not exp_sub.empty:
        # Format Exposure as simple 2-column table (period, value)
        # Exposure doesn't develop over age, so we take the last value per period
        exp_simple = exp_sub.groupby('period', observed=True).agg({'value': 'last'}).reset_index()
        exp_simple.columns = ['Period', 'Exposure']
        exp_simple['Exposure'] = exp_simple['Exposure'].round(0)
        exp_md = df_to_markdown(exp_simple, index=False)
    else:
        exp_md = "No Exposure data\n"
        
    measures = [m for m in raw_measures if m != 'Exposure']
    
    print(f"\nCreating sheets for measures: {measures}")
    
    for measure in measures:
        # xlsxwriter sheet names limited to 31 chars
        ws = wb.add_worksheet(measure[:31])
        build_measure_sheet(ws, measure, df_scenarios, df_enhanced, df_diagnostics, fmt, df_prior)
        print(f"  Built sheet: {measure[:31]}")
    
    wb.close()
    export_md_data(measures, df_scenarios, df_enhanced, df_diagnostics, exp_md)
    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    main()
