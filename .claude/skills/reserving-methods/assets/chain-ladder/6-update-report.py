"""
goal: Update report.html with data from the Chain Ladder pipeline.
contents:
    update_report(): Reads parquet files from pipeline and populates report.html template for each measure.
"""

import pandas as pd
import json
import re
import shutil
from pathlib import Path

# Replace when using this file in an actual project:
OUTPUT_PATH = "../test-output/"
TEMPLATE_PATH = "report.html"

METHOD_ID = "chainladder"


def update_report(
    processed_data_path: str = None,
    ldf_summary_path: str = None,
    selections_path: str = None,
    output_dir: str = None,
    template_path: str = None
) -> list:
    """
    Update report.html with data from the Chain Ladder pipeline.
    
    Args:
        processed_data_path: Path to step 1 output (processed triangle data in long format)
        ldf_summary_path: Path to step 4 output (LDF summary with averages and QA metrics)
        selections_path: Path to step 5 output (selections by scenario)
        output_dir: Directory to save the generated HTML reports
        template_path: Path to the report.html template
    
    Returns:
        List of paths to generated HTML files (one per measure)
    """
    # Use defaults if not provided
    processed_data_path = processed_data_path or OUTPUT_PATH + f"1_{METHOD_ID}_processed_data.parquet"
    ldf_summary_path = ldf_summary_path or OUTPUT_PATH + f"4_{METHOD_ID}_ldf_summary.parquet"
    selections_path = selections_path or OUTPUT_PATH + f"5_{METHOD_ID}_selections.parquet"
    output_dir = output_dir or OUTPUT_PATH + "reports/"
    template_path = template_path or TEMPLATE_PATH
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print(f"Loading data from pipeline...")
    df_processed = pd.read_parquet(processed_data_path)
    df_summary = pd.read_parquet(ldf_summary_path)
    df_selections = pd.read_parquet(selections_path)
    
    print(f"  Processed data: {len(df_processed)} rows")
    print(f"  LDF summary: {len(df_summary)} rows")
    print(f"  Selections: {len(df_selections)} rows")
    print(f"  Measures: {df_processed['measure'].unique().tolist()}")
    
    # Generate one report per measure
    generated_files = []
    
    for measure in df_processed['measure'].cat.categories:
        print(f"\nGenerating report for: {measure}")
        
        # Filter data for this measure
        df_measure = df_processed[df_processed['measure'] == measure]
        df_selections_measure = df_selections[df_selections['measure'] == measure]
        df_summary_measure = df_summary[df_summary['measure'] == measure]
        
        # Convert long format triangle to wide format
        triangle_wide = df_measure.pivot_table(
            index='period',
            columns='age',
            values='value',
            aggfunc='first',
            observed=True
        )
        
        # Prepare data for HTML template
        periods = [str(p) for p in triangle_wide.index.tolist()]
        ages = [str(a) for a in triangle_wide.columns.tolist()]
        
        # Convert triangle data to list of lists
        data = []
        for period in triangle_wide.index:
            row = []
            for age in triangle_wide.columns:
                val = triangle_wide.at[period, age]
                row.append(None if pd.isna(val) else float(val))
            data.append(row)
        
        # Prepare selections by scenario
        scenarios = []
        for scenario_label in df_selections_measure['scenario'].cat.categories:
            scenario_df = df_selections_measure[
                df_selections_measure['scenario'] == scenario_label
            ].sort_values('interval')
            
            selections = []
            for _, row in scenario_df.iterrows():
                selection = {
                    'averageType': row['average_type'],
                    'reasoning': row['reasoning']
                }
                selections.append(selection)
            
            scenarios.append({
                'label': scenario_label,
                'selections': selections
            })
        
        # Prepare diagnostics (CV and slope)
        diagnostics = []
        for _, row in df_summary_measure.sort_values('interval').iterrows():
            diagnostics.append({
                'interval': row['interval'],
                'cv': None if pd.isna(row['cv']) else float(row['cv']),
                'slope': None if pd.isna(row['slope']) else float(row['slope'])
            })
        
        # Create source data object
        source_data = {
            'triangleName': measure,
            'developmentTriangle': {
                'periods': periods,
                'ages': ages,
                'data': data
            },
            'diagnostics': diagnostics,
            'selections': {
                'scenarios': scenarios
            }
        }
        
        # Copy template and update with data
        measure_filename = measure.lower().replace(' ', '_')
        html_output_path = output_path / f"{measure_filename}_report.html"
        
        shutil.copy(template_path, html_output_path)
        
        # Read template
        with open(html_output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Calculate relative path from output location to static folder
        # Output is in: .claude/skills/reserving-methods/assets/test-output/reports/
        # Static is at root, so we need to go up to root then into static/
        html_output_abs = html_output_path.resolve()
        
        # Find the project root (where static/ folder is)
        current = html_output_abs.parent
        levels_up = 0  # Count how many parent directories we traverse
        max_levels = 15  # Safety limit
        
        while levels_up < max_levels:
            if (current / 'static').exists():
                # Found the root with static folder
                break
            current = current.parent
            levels_up += 1
        
        # Build relative path (from the HTML file in reports/, we need levels_up '../')
        relative_static_path = '../' * levels_up + 'static/'
        
        # Replace absolute /static/ paths with relative paths
        html_content = html_content.replace('href="/static/', f'href="{relative_static_path}')
        html_content = html_content.replace('src="/static/', f'src="{relative_static_path}')
        
        # Update title with measure name
        title_pattern = r'<title>.*?</title>'
        title_replacement = f'<title>{measure} | Chain Ladder Report</title>'
        html_content = re.sub(title_pattern, title_replacement, html_content)
        
        # Replace sourceData object
        source_data_js = json.dumps(source_data, indent=12)
        pattern = r'const sourceData = \{[\s\S]*?\n        \};'
        replacement = f'const sourceData = {source_data_js};'
        html_content = re.sub(pattern, replacement, html_content)
        
        # Write updated HTML
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        generated_files.append(str(html_output_path))
        print(f"  Created: {html_output_path}")
        print(f"    Periods: {len(periods)} ({periods[0]} - {periods[-1]})")
        print(f"    Ages: {len(ages)} ({ages[0]} - {ages[-1]})")
        print(f"    Scenarios: {len(scenarios)}")
    
    return generated_files


if __name__ == "__main__":
    """Generate HTML reports from pipeline data."""
    print("="*80)
    print("Chain Ladder Report Generation")
    print("="*80)
    
    generated_files = update_report()
    
    print("\n" + "="*80)
    print(f"Successfully generated {len(generated_files)} report(s):")
    for file in generated_files:
        print(f"  - {file}")
    
    print("\nTo view the reports:")
    print("  1. Open the HTML files in a web browser")
    print("  2. Or serve them with: python -m http.server 8000")
    print("  3. Then navigate to: http://localhost:8000/")
    print("="*80)
