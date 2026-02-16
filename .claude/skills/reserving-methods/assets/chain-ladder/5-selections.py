"""
goal: Make initial LDF selections based on calculated averages and QA metrics.
contents:
    make_selections(): Create Conservative, Best Estimate, Optimistic, and Final Recommendation scenarios.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Replace when using this file in an actual project:
OUTPUT_PATH = "../test-output/"
METHOD_ID = "chainladder"


def make_selections(df_summary: pd.DataFrame, overrides_path: str = None) -> pd.DataFrame:
    """
    Make LDF selections based on calculated averages and QA metrics.
    
    Args:
        df_summary: DataFrame from step 4 with columns:
                   measure, interval, weighted_all, simple_all, medial_all,
                   weighted_3yr, simple_3yr, medial_3yr, weighted_5yr, simple_5yr, medial_5yr,
                   cv, slope
        overrides_path: Optional path to JSON file with overrides. JSON must be a list of objects
                       with the following structure:
                       [
                           {
                               "measure": "Closed Count",
                               "interval": "Dev Pd 1-Dev Pd 2",
                               "average_type": "weighted_all",
                               "value": 1.6300,
                               "reasoning": "OVERRIDE: Using all-year weighted due to management judgment"
                           },
                           ...
                       ]
                       Required keys: measure, interval, average_type, value, reasoning
                       These will replace Final Recommendation selections for matching measure+interval
    
    Returns:
        DataFrame with columns: measure, scenario, interval, average_type, value, reasoning
        Scenarios include: Conservative, Best Estimate, Optimistic, Final Recommendation
    """
    
    # Load and validate overrides if provided
    overrides_df = None
    if overrides_path is not None:
        overrides_path_obj = Path(overrides_path)
        
        if not overrides_path_obj.exists():
            raise FileNotFoundError(f"Overrides file not found: {overrides_path}")
        
        # Read JSON file
        with open(overrides_path_obj, 'r') as f:
            overrides_data = json.load(f)
        
        # Validate JSON structure
        if not isinstance(overrides_data, list):
            raise ValueError("Overrides JSON must be a list of objects")
        
        if len(overrides_data) > 0:
            required_keys = {'measure', 'interval', 'average_type', 'value', 'reasoning'}
            for i, override in enumerate(overrides_data):
                if not isinstance(override, dict):
                    raise ValueError(f"Override at index {i} must be an object/dict")
                
                missing_keys = required_keys - set(override.keys())
                if missing_keys:
                    raise ValueError(f"Override at index {i} missing required keys: {missing_keys}")
            
            # Convert to DataFrame
            overrides_df = pd.DataFrame(overrides_data)

    
    # Map average type names to column names
    avg_type_map = {
        'weighted_3yr': 'weighted_3yr',
        'weighted_5yr': 'weighted_5yr',
        'weighted_all': 'weighted_all',
        'simple_3yr': 'simple_3yr',
        'simple_5yr': 'simple_5yr',
        'simple_all': 'simple_all',
        'medial_3yr': 'medial_3yr',
        'medial_5yr': 'medial_5yr',
        'medial_all': 'medial_all'
    }
    
    selections = []
    
    for _, row in df_summary.iterrows():
        measure = row['measure']
        interval = row['interval']
        cv = row['cv']
        slope = row['slope']
        
        # Conservative: Prefer weighted averages or longer periods
        if cv < 0.05:  # Low volatility
            avg_type = 'weighted_3yr'
            reasoning = f'Low volatility (CV={cv:.3f}) supports recent trend analysis'
        elif cv < 0.10:
            avg_type = 'weighted_5yr'
            reasoning = f'Moderate volatility (CV={cv:.3f}) requires longer-term perspective'
        else:
            avg_type = 'weighted_all'
            reasoning = f'High volatility (CV={cv:.3f}) requires full data for stability'
        
        selections.append({
            'measure': measure,
            'scenario': 'Conservative',
            'interval': interval,
            'average_type': avg_type,
            'value': row[avg_type],
            'reasoning': reasoning
        })
        
        # Best Estimate: Balanced approach
        if cv < 0.08:
            if abs(slope) < 0.01:
                avg_type = 'simple_5yr'
                reasoning = f'Stable pattern (CV={cv:.3f}, slope={slope:.4f}) indicates consistent development'
            else:
                trend_desc = "declining" if slope < 0 else "increasing"
                avg_type = 'simple_5yr'
                reasoning = f'Stable with {trend_desc} trend (CV={cv:.3f}, slope={slope:.4f})'
        else:
            avg_type = 'simple_all'
            reasoning = f'Variable pattern (CV={cv:.3f}) benefits from full historical perspective'
        
        selections.append({
            'measure': measure,
            'scenario': 'Best Estimate',
            'interval': interval,
            'average_type': avg_type,
            'value': row[avg_type],
            'reasoning': reasoning
        })
        
        # Optimistic: Recent trends
        if slope < -0.01:  # Significant decreasing trend
            avg_type = 'simple_3yr'
            reasoning = f'Strong declining trend (slope={slope:.4f}) suggests continued improvement'
        elif slope < 0:  # Mild decreasing trend
            avg_type = 'simple_3yr'
            reasoning = f'Mild declining trend (slope={slope:.4f}) supports recent experience'
        elif cv < 0.06:  # Stable, no strong trend
            avg_type = 'simple_5yr'
            reasoning = f'Stable development (CV={cv:.3f}) with no adverse trends'
        else:
            avg_type = 'simple_5yr'
            reasoning = f'Recent experience (CV={cv:.3f}) may reflect improved conditions'
        
        selections.append({
            'measure': measure,
            'scenario': 'Optimistic',
            'interval': interval,
            'average_type': avg_type,
            'value': row[avg_type],
            'reasoning': reasoning
        })
        
        # Final Recommendation: Intelligent selection based on combined metrics
        if cv < 0.05 and abs(slope) < 0.005:  # Very stable, no trend
            avg_type = 'simple_5yr'
            reasoning = f'RECOMMENDED: Very stable pattern (CV={cv:.3f}, slope={slope:.4f}) supports balanced 5-year average'
        elif cv < 0.05 and slope < -0.005:  # Stable with improving trend
            avg_type = 'simple_3yr'
            reasoning = f'RECOMMENDED: Stable with improving trend (CV={cv:.3f}, slope={slope:.4f}) - recent experience preferred'
        elif cv < 0.05 and slope > 0.005:  # Stable with worsening trend
            avg_type = 'weighted_5yr'
            reasoning = f'RECOMMENDED: Stable with adverse trend (CV={cv:.3f}, slope={slope:.4f}) - weighted average dampens recent increases'
        elif cv < 0.08:  # Moderate volatility
            avg_type = 'simple_5yr'
            reasoning = f'RECOMMENDED: Moderate volatility (CV={cv:.3f}) balanced with 5-year perspective'
        elif cv < 0.12:  # High volatility  
            avg_type = 'weighted_all'
            reasoning = f'RECOMMENDED: High volatility (CV={cv:.3f}) requires full data span with volume weighting for stability'
        else:  # Very high volatility
            avg_type = 'simple_all'
            reasoning = f'RECOMMENDED: Very high volatility (CV={cv:.3f}) requires full historical perspective for stability'
        
        selections.append({
            'measure': measure,
            'scenario': 'Final Recommendation',
            'interval': interval,
            'average_type': avg_type,
            'value': row[avg_type],
            'reasoning': reasoning
        })
    
    # Create DataFrame
    df_selections = pd.DataFrame(selections)
    
    # Preserve categorical types
    df_selections['measure'] = pd.Categorical(
        df_selections['measure'], 
        categories=df_summary['measure'].cat.categories
    )
    df_selections['scenario'] = pd.Categorical(
        df_selections['scenario'],
        categories=['Conservative', 'Best Estimate', 'Optimistic', 'Final Recommendation'],
        ordered=True
    )
    df_selections['interval'] = pd.Categorical(
        df_selections['interval'],
        categories=df_summary['interval'].cat.categories,
        ordered=True
    )
    
    # Apply overrides to Final Recommendation scenario
    if overrides_df is not None and len(overrides_df) > 0:
        # Temporarily convert average_type to string to allow new values
        df_selections['average_type'] = df_selections['average_type'].astype(str)
        
        for _, override in overrides_df.iterrows():
            # Find matching rows in Final Recommendation scenario
            mask = (
                (df_selections['measure'] == override['measure']) &
                (df_selections['interval'] == override['interval']) &
                (df_selections['scenario'] == 'Final Recommendation')
            )
            
            # Update with override values
            if mask.any():
                df_selections.loc[mask, 'average_type'] = str(override['average_type'])
                df_selections.loc[mask, 'value'] = float(override['value'])
                df_selections.loc[mask, 'reasoning'] = str(override['reasoning'])
    
    # Convert average_type to categorical (after overrides)
    df_selections['average_type'] = df_selections['average_type'].astype('category')
    
    # Round value column to 4 decimal places
    df_selections['value'] = df_selections['value'].round(4)
    
    return df_selections


if __name__ == "__main__":
    """Test the make_selections function."""
    # Read summary data from step 4
    input_file = OUTPUT_PATH + f"4_{METHOD_ID}_ldf_summary.parquet"
    df_summary = pd.read_parquet(input_file)
    print(f"Loaded {len(df_summary)} summary rows")
    print(f"Measures: {df_summary['measure'].unique().tolist()}")
    
    # Make selections
    df_selections = make_selections(df_summary)
    print(f"\nCreated {len(df_selections)} selection rows")
    print(f"Scenarios: {df_selections['scenario'].unique().tolist()}")
    
    # Display sample selections for first measure
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 80)
    pd.set_option('display.float_format', '{:.4f}'.format)
    
    first_measure = df_selections['measure'].unique()[0]
    print(f"\nSelections for {first_measure}:")
    measure_selections = df_selections[df_selections['measure'] == first_measure]
    
    for scenario in df_selections['scenario'].unique():
        scenario_data = measure_selections[measure_selections['scenario'] == scenario]
        print(f"\n  {scenario}:")
        for _, row in scenario_data.iterrows():
            print(f"    {row['interval']}: {row['average_type']} = {row['value']:.4f}")
            print(f"      → {row['reasoning']}")
    
    # Save output - parquet preserves categorical types, CSV for inspection
    df_selections.to_parquet(OUTPUT_PATH + f"5_{METHOD_ID}_selections.parquet", index=False)
    df_selections.to_csv(OUTPUT_PATH + f"5_{METHOD_ID}_selections.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}5_{METHOD_ID}_selections.[parquet|csv]")
    
