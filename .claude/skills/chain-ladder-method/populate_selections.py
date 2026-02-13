"""
Populate Chain Ladder Selections HTML

Generates HTML selection reports from selections CSV files.
Triangle data is loaded from separate triangle CSV files.

Usage:
    python populate_selections.py --csv <path_to_selections.csv>
    
Examples:
    python populate_selections.py --csv output/selections/paid_losses_selections.csv
"""

import sys
from pathlib import Path
import argparse
import shutil
import pandas as pd
import json

# Add the chain-ladder-method skill folder to path
sys.path.append(str(Path(__file__).parent.parent.parent / '.claude/skills/chain-ladder-method'))


def setup_html_file(triangle_name):
    """Copy template for the triangle."""
    # Create sanitized filename from triangle name
    filename = triangle_name.lower().replace(' ', '_')
    html_path = Path(f'output/selections/{filename}_selections.html')
    
    # Ensure selections directory exists
    html_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy template (CSS paths are already absolute from root)
    template_path = Path('.claude/skills/chain-ladder-method/template_report.html')
    shutil.copy(template_path, html_path)
    
    return str(html_path)


def update_html_with_data(html_path, triangle_name, periods, ages, data, scenarios):
    """Update the HTML template with triangle and selection data."""
    import re
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Prepare the sourceData JavaScript object
    source_data = {
        'triangleName': triangle_name,
        'developmentTriangle': {
            'periods': periods,
            'ages': ages,
            'data': data
        },
        'selections': {
            'scenarios': scenarios
        }
    }
    
    # Convert to JavaScript
    source_data_js = json.dumps(source_data, indent=4)
    
    # Find and replace the sourceData object in the HTML
    pattern = r'const sourceData = \{[\s\S]*?\};'
    replacement = f'const sourceData = {source_data_js};'
    html_content = re.sub(pattern, replacement, html_content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def populate_from_csv(selections_csv_path: str) -> str:
    """
    Populate HTML report from selections CSV file.
    Automatically finds the matching triangle CSV in output/processed/.
    
    Args:
        selections_csv_path: Path to the selections CSV file
    
    Returns:
        Path to the created HTML file
    """
    selections_path = Path(selections_csv_path)
    
    if not selections_path.exists():
        raise FileNotFoundError(f"Selections file not found: {selections_path}")
    
    # Load selections CSV
    selections_df = pd.read_csv(selections_path)
    
    # Derive triangle name from filename
    filename_base = selections_path.stem.replace('_selections', '')
    triangle_name = filename_base.replace('_', ' ').title()
    
    # Find matching triangle CSV in output/processed/
    triangle_path = Path(f"output/processed/{filename_base}_triangle.csv")
    
    if not triangle_path.exists():
        raise FileNotFoundError(f"Triangle file not found: {triangle_path}")
    
    # Load triangle CSV
    triangle_df = pd.read_csv(triangle_path, index_col=0)
    
    print(f"\n{'='*60}")
    print(f"Populating HTML: {triangle_name}")
    print(f"{'='*60}\n")
    
    # Setup HTML file
    print("Setting up HTML file from template...")
    html_path = setup_html_file(triangle_name)
    print(f"CREATED: {html_path}\n")
    
    # Convert CSV data to JSON format for HTML template
    periods = [str(p) for p in triangle_df.index.tolist()]
    ages = [int(a) if isinstance(a, (int, float)) else a for a in triangle_df.columns.tolist()]
    
    # Convert triangle data to list of lists
    data = []
    for idx in triangle_df.index:
        row = []
        for col in triangle_df.columns:
            val = triangle_df.at[idx, col]
            row.append(None if pd.isna(val) else float(val))
        data.append(row)
    
    # Convert selections to JSON format
    scenarios = []
    for scenario_label in selections_df['Scenario'].unique():
        scenario_df = selections_df[selections_df['Scenario'] == scenario_label]
        selections = []
        for _, row in scenario_df.iterrows():
            selection = {'reasoning': row['Reasoning']}
            if pd.notna(row['ManualValue']) and row['ManualValue'] != '':
                selection['manualValue'] = float(row['ManualValue'])
            else:
                selection['averageType'] = row['AverageType']
            selections.append(selection)
        scenarios.append({'label': scenario_label, 'selections': selections})
    
    # Update HTML file
    update_html_with_data(html_path, triangle_name, periods, ages, data, scenarios)
    
    print(f"\nSUCCESSFULLY updated {html_path}")
    print(f"  Triangle: {triangle_name}")
    print(f"  Periods: {len(periods)} ({periods[0]} - {periods[-1]})")
    print(f"  Ages: {len(ages)} ({ages[0]} - {ages[-1]})")
    print(f"  Scenarios: {len(scenarios)}")
    
    print(f"\nHTML report populated successfully!")
    print(f"\nNext steps:")
    print(f"  1. Run: npx vite --port 5175")
    print(f"  2. Navigate to: http://localhost:5175/{html_path}")
    print(f"  3. Review selections and adjust CSV if needed\n")
    
    return html_path


def main():
    parser = argparse.ArgumentParser(description='Generate HTML report from selections and triangle data')
    parser.add_argument('--csv', required=True, help='Path to selections CSV file')
    
    args = parser.parse_args()
    
    try:
        html_path = populate_from_csv(args.csv)
        print(f"Success! Created: {html_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
