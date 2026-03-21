"""
goal: Write JSON data from the Chain Ladder pipeline.
contents:
    update_report(): Reads parquet files from pipeline and generates JSON data files for each measure.

run-note: This script must be run from its own directory for relative paths to work correctly.
    cd .claude/skills/reserving-methods/assets/chain-ladder
    python 7-write-json.py
"""

import pandas as pd
import json
from pathlib import Path

# Replace when using this file in an actual project:
INPUT_PATH = "../test-output/"
OUTPUT_PATH = "../test-output/"

METHOD_ID = "chainladder"


def update_report(
    processed_data_path: str = None,
    ldf_averages_path: str = None,
    selections_path: str = None,
    diagnostics_path: str = None,
    ultimates_path: str = None,
    output_dir: str = None
) -> list:
    """
    Write JSON data from the Chain Ladder pipeline.
    
    Args:
        processed_data_path: Path to step 1 output (processed triangle data in long format)
        ldf_averages_path: Path to step 4 output
        selections_path: Path to step 5 output (selections by scenario)
        diagnostics_path: Path to step 3 output (actuarial diagnostics)
        ultimates_path: Path to step 6 output (projected ultimates)
        output_dir: Directory to save the generated JSON data files
    
    Returns:
        List of paths to generated JSON files (one per measure)
    """
    # Use defaults if not provided
    processed_data_path = processed_data_path or INPUT_PATH + f"1_{METHOD_ID}_processed_data.parquet"
    ldf_averages_path = ldf_averages_path or INPUT_PATH + f"4_{METHOD_ID}_ldf_averages.parquet"
    selections_path = selections_path or INPUT_PATH + f"5_{METHOD_ID}_selections.parquet"
    diagnostics_path = diagnostics_path or INPUT_PATH + f"3_{METHOD_ID}_diagnostics.parquet"
    ultimates_path = ultimates_path or INPUT_PATH + f"6_{METHOD_ID}_ultimates.parquet"
    output_dir = output_dir or OUTPUT_PATH + "json/"
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print(f"Loading data from pipeline...")
    df_processed = pd.read_parquet(processed_data_path)
    df_summary = pd.read_parquet(ldf_averages_path)
    df_selections = pd.read_parquet(selections_path)
    df_diagnostics = pd.read_parquet(diagnostics_path)
    df_ultimates = pd.read_parquet(ultimates_path)
    
    print(f"  Processed data: {len(df_processed)} rows")
    print(f"  LDF summary: {len(df_summary)} rows")
    print(f"  Selections: {len(df_selections)} rows")
    print(f"  Diagnostics: {len(df_diagnostics)} rows")
    print(f"  Ultimates: {len(df_ultimates)} rows")
    print(f"  Measures: {df_processed['measure'].unique().tolist()}")
    
    # Generate one report per measure
    generated_files = []
    
    for measure in df_processed['measure'].cat.categories:
        print(f"\nGenerating report for: {measure}")
        
        # Filter data for this measure
        df_measure = df_processed[df_processed['measure'] == measure]
        df_ultimates_measure = df_ultimates[df_ultimates['measure'] == measure]
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
                    'value': None if pd.isna(row['value']) else float(row['value']),
                    'reasoning': row['reasoning']
                }
                selections.append(selection)
            
            scenarios.append({
                'label': scenario_label,
                'selections': selections
            })
        
        # Prepare QA metrics (CV and slope)
        qa_metrics = []
        for _, row in df_summary_measure.sort_values('interval').iterrows():
            qa_metrics.append({
                'interval': row['interval'],
                'cv': None if pd.isna(row['cv']) else float(row['cv']),
                'slope': None if pd.isna(row['slope']) else float(row['slope'])
            })
        
        # Create JSON data in long tabular format for AI agent access
        # Use column headers + data arrays (like CSV in JSON format)
        json_data = {
            'measure': measure,
            'triangleData': {
                'columns': ['period', 'age', 'value'],
                'data': []
            },
            'qaMetrics': {
                'columns': ['interval', 'cv', 'slope'],
                'data': []
            },
            'actuarialDiagnostics': {
                'columns': ['period', 'age', 'metric', 'value'],
                'data': []
            },
            'selections': {
                'columns': ['scenario', 'interval', 'average_type', 'value', 'reasoning'],
                'data': []
            },
            'ultimates': {
                'columns': ['scenario', 'period', 'latest_age', 'current_value', 'cdf', 'ultimate', 'development'],
                'data': []
            }
        }
        
        # Convert triangle to long format
        for i, period in enumerate(periods):
            for j, age in enumerate(ages):
                if data[i][j] is not None:
                    json_data['triangleData']['data'].append([period, age, round(data[i][j], 4)])
        
        # Convert QA metrics to array format
        for metric in qa_metrics:
            json_data['qaMetrics']['data'].append([
                metric['interval'],
                round(metric['cv'], 4),
                round(metric['slope'], 4)
            ])
        
        # Convert actuarial diagnostics to long format (directly from dataframe)
        diagnostic_cols = [
            'incurred_severity', 'paid_severity', 'paid_to_incurred',
            'case_reserves', 'open_counts', 'average_case_reserves',
            'cumulative_closure_rate', 'incurred_severity_incr',
            'paid_severity_incr', 'incremental_closure_rate'
        ]
        
        for _, row in df_diagnostics.iterrows():
            period = str(row['period'])
            age = str(row['age'])
            for metric_name in diagnostic_cols:
                if metric_name in row and pd.notna(row[metric_name]):
                    json_data['actuarialDiagnostics']['data'].append([
                        period,
                        age,
                        metric_name,
                        round(float(row[metric_name]), 4)
                    ])
        
        # Convert selections to long format
        for scenario in scenarios:
            scenario_label = scenario['label']
            for i, selection in enumerate(scenario['selections']):
                # Get interval from qa_metrics (they're in same order)
                interval = qa_metrics[i]['interval'] if i < len(qa_metrics) else f'Interval {i+1}'
                value = selection.get('value', None)
                json_data['selections']['data'].append([
                    scenario_label,
                    interval,
                    selection.get('averageType', ''),
                    round(value, 4) if value is not None else None,
                    selection.get('reasoning', '')
                ])
        
        # Convert ultimates to long format (directly from dataframe)
        for _, row in df_ultimates_measure.iterrows():
            json_data['ultimates']['data'].append([
                str(row['scenario']),
                str(row['period']),
                str(row['latest_age']),
                round(float(row['current_value']), 4) if pd.notna(row['current_value']) else None,
                round(float(row['cdf']), 4) if pd.notna(row['cdf']) else None,
                round(float(row['ultimate']), 4) if pd.notna(row['ultimate']) else None,
                round(float(row['development']), 4) if pd.notna(row['development']) else None
            ])
        
        
        # Save JSON data for AI agent access (no _data suffix)
        # Use compact format: one data row per line for easy scanning
        measure_filename = measure.lower().replace(' ', '_')
        json_output_path = output_path / f"{measure_filename}_report.json"
        
        with open(json_output_path, 'w', encoding='utf-8') as f:
            f.write('{\n')
            f.write(f'  "measure": {json.dumps(json_data["measure"])},\n')
            
            # Triangle data - columns + data array
            f.write('  "triangleData": {\n')
            f.write(f'    "columns": {json.dumps(json_data["triangleData"]["columns"])},\n')
            f.write('    "data": [\n')
            for i, row in enumerate(json_data['triangleData']['data']):
                comma = ',' if i < len(json_data['triangleData']['data']) - 1 else ''
                f.write(f'      {json.dumps(row, separators=(",", ": "))}{comma}\n')
            f.write('    ]\n')
            f.write('  },\n')
            
            # QA metrics - columns + data array
            f.write('  "qaMetrics": {\n')
            f.write(f'    "columns": {json.dumps(json_data["qaMetrics"]["columns"])},\n')
            f.write('    "data": [\n')
            for i, row in enumerate(json_data['qaMetrics']['data']):
                comma = ',' if i < len(json_data['qaMetrics']['data']) - 1 else ''
                f.write(f'      {json.dumps(row, separators=(",", ": "))}{comma}\n')
            f.write('    ]\n')
            f.write('  },\n')
            
            # Actuarial diagnostics - columns + data array
            f.write('  "actuarialDiagnostics": {\n')
            f.write(f'    "columns": {json.dumps(json_data["actuarialDiagnostics"]["columns"])},\n')
            f.write('    "data": [\n')
            for i, row in enumerate(json_data['actuarialDiagnostics']['data']):
                comma = ',' if i < len(json_data['actuarialDiagnostics']['data']) - 1 else ''
                f.write(f'      {json.dumps(row, separators=(",", ": "))}{comma}\n')
            f.write('    ]\n')
            f.write('  },\n')
            
            # Selections - columns + data array
            f.write('  "selections": {\n')
            f.write(f'    "columns": {json.dumps(json_data["selections"]["columns"])},\n')
            f.write('    "data": [\n')
            for i, row in enumerate(json_data['selections']['data']):
                comma = ',' if i < len(json_data['selections']['data']) - 1 else ''
                f.write(f'      {json.dumps(row, separators=(",", ": "))}{comma}\n')
            f.write('    ]\n')
            f.write('  },\n')
            
            # Ultimates - columns + data array
            f.write('  "ultimates": {\n')
            f.write(f'    "columns": {json.dumps(json_data["ultimates"]["columns"])},\n')
            f.write('    "data": [\n')
            for i, row in enumerate(json_data['ultimates']['data']):
                comma = ',' if i < len(json_data['ultimates']['data']) - 1 else ''
                f.write(f'      {json.dumps(row, separators=(",", ": "))}{comma}\n')
            f.write('    ]\n')
            f.write('  }\n')
            f.write('}\n')
        
        print(f"  Saved JSON: {json_output_path}")
        generated_files.append(str(json_output_path))
        print(f"    Periods: {len(periods)} ({periods[0]} - {periods[-1]})")
        print(f"    Ages: {len(ages)} ({ages[0]} - {ages[-1]})")
        print(f"    Scenarios: {len(scenarios)}")
    
    return generated_files


if __name__ == "__main__":
    """Generate JSON data files from pipeline data."""
    print("="*80)
    print("Chain Ladder JSON Generation")
    print("="*80)
    
    generated_files = update_report()
    
    print("\n" + "="*80)
    print(f"Successfully generated {len(generated_files)} JSON file(s):")
    for file in generated_files:
        print(f"  - {file}")
    print("="*80)
