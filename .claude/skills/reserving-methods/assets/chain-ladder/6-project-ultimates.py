"""
goal: Calculate ultimate values using selected LDFs and CDFs.
contents:
    calculate_cdfs(): Calculate cumulative development factors from selected LDFs.
    project_ultimates(): Calculate projected ultimate values for each measure and scenario.
"""

import pandas as pd
import numpy as np
from typing import Dict

# Replace when using this file in an actual project:
OUTPUT_PATH = "../test-output/"
METHOD_ID = "chainladder"


def calculate_cdfs(selected_ldfs: Dict[str, float], tail_factor: float = 1.0) -> Dict[str, float]:
    """
    Calculate cumulative development factors from selected LDFs.
    
    CDFs are calculated from tail back to earliest age:
        CDF[age] = LDF[age] * CDF[next_age]
        CDF[ultimate] = tail_factor
    
    Args:
        selected_ldfs: Dict of interval -> LDF value (e.g., {'Dev Pd 1-Dev Pd 2': 1.5})
        tail_factor: Tail factor to apply at ultimate (default 1.0 = no tail)
    
    Returns:
        Dict of starting_age -> CDF value
    """
    # Extract ages from interval strings "age_from-age_to"
    ages = []
    ldfs_by_age = {}
    ultimate_age = None
    
    for interval, ldf in selected_ldfs.items():
        parts = str(interval).split('-')
        if len(parts) == 2:
            age_from = parts[0].strip()
            age_to = parts[1].strip()
            if age_from not in ages:
                ages.append(age_from)
            ldfs_by_age[age_from] = ldf
            ultimate_age = age_to
    
    if not ages:
        return {}
    
    # Calculate CDFs from tail backwards
    cdfs = {}
    max_age = ages[-1]
    
    # The CDF at the last age includes the tail
    if max_age not in ldfs_by_age:
        raise ValueError(f"Missing LDF for age {max_age}")
    cdfs[max_age] = ldfs_by_age[max_age] * tail_factor
    
    # Work backwards
    for i in range(len(ages) - 2, -1, -1):
        age = ages[i]
        next_age = ages[i + 1]
        if age not in ldfs_by_age:
            raise ValueError(f"Missing LDF for age {age}")
        cdfs[age] = ldfs_by_age[age] * cdfs[next_age]
    
    # Add CDF for the ultimate age (only tail factor applies)
    if ultimate_age and ultimate_age not in cdfs:
        cdfs[ultimate_age] = tail_factor
    
    return cdfs


def project_ultimates(
    df_processed: pd.DataFrame,
    df_selections: pd.DataFrame,
    tail_factor: float = 1.0
) -> pd.DataFrame:
    """
    Calculate projected ultimate values for each measure and scenario.
    
    Args:
        df_processed: Long format DataFrame from step 1 (period, age, value, measure)
        df_selections: DataFrame from step 5 (measure, scenario, interval, average_type, value)
        tail_factor: Tail factor to apply (default 1.0 = no tail)
    
    Returns:
        Long format DataFrame with columns:
        - measure: Type of measure
        - scenario: Selection scenario
        - period: Origin period
        - latest_age: Latest age with data for this period
        - current_value: Current value at latest age
        - cdf: Cumulative development factor applied
        - ultimate: Projected ultimate value
        - development: Ultimate - Current
    """
    results = []
    
    # Get unique measures and scenarios
    for measure in df_selections['measure'].cat.categories:
        measure_data = df_processed[df_processed['measure'] == measure]
        
        for scenario in df_selections['scenario'].cat.categories:
            scenario_selections = df_selections[
                (df_selections['measure'] == measure) &
                (df_selections['scenario'] == scenario)
            ].sort_values('interval')
            
            # Build selected LDFs dict
            selected_ldfs = {}
            for _, row in scenario_selections.iterrows():
                if pd.notna(row['value']):
                    selected_ldfs[row['interval']] = row['value']
            
            if not selected_ldfs:
                continue
            
            # Calculate CDFs
            cdfs = calculate_cdfs(selected_ldfs, tail_factor)
            
            # Get latest diagonal (most recent value for each period)
            for period in measure_data['period'].cat.categories:
                period_data = measure_data[measure_data['period'] == period]
                
                if len(period_data) == 0:
                    continue
                
                # Get the last age with data for this period
                period_data_sorted = period_data.sort_values('age')
                latest_row = period_data_sorted.iloc[-1]
                
                latest_age = str(latest_row['age'])
                current_value = latest_row['value']
                
                # Get CDF for this age
                if latest_age not in cdfs:
                    # This age might not have a CDF (e.g., if it's the ultimate age)
                    # Check if it's the ending age of the last interval
                    last_interval = scenario_selections.iloc[-1]['interval']
                    ending_age = last_interval.split('-')[1].strip()
                    if latest_age == ending_age:
                        cdf = tail_factor
                    else:
                        # No CDF available for this age, skip
                        continue
                else:
                    cdf = cdfs[latest_age]
                
                # Calculate ultimate
                ultimate = current_value * cdf
                development = ultimate - current_value
                
                results.append({
                    'measure': measure,
                    'scenario': scenario,
                    'period': period,
                    'latest_age': latest_age,
                    'current_value': round(current_value, 4),
                    'cdf': round(cdf, 4),
                    'ultimate': round(ultimate, 4),
                    'development': round(development, 4)
                })
    
    df_ultimates = pd.DataFrame(results)
    
    # Preserve categorical types
    if len(df_ultimates) > 0:
        df_ultimates['measure'] = pd.Categorical(
            df_ultimates['measure'],
            categories=df_selections['measure'].cat.categories
        )
        df_ultimates['scenario'] = pd.Categorical(
            df_ultimates['scenario'],
            categories=df_selections['scenario'].cat.categories,
            ordered=True
        )
        df_ultimates['period'] = pd.Categorical(
            df_ultimates['period'],
            categories=df_processed['period'].cat.categories,
            ordered=True
        )
    
    return df_ultimates


if __name__ == "__main__":
    """Test the project_ultimates function."""
    # Read data from previous steps
    input_file_processed = OUTPUT_PATH + f"1_{METHOD_ID}_processed_data.parquet"
    input_file_selections = OUTPUT_PATH + f"5_{METHOD_ID}_selections.parquet"
    
    df_processed = pd.read_parquet(input_file_processed)
    df_selections = pd.read_parquet(input_file_selections)
    
    print(f"Loaded {len(df_processed)} processed rows")
    print(f"Loaded {len(df_selections)} selection rows")
    print(f"Measures: {df_processed['measure'].unique().tolist()}")
    print(f"Scenarios: {df_selections['scenario'].unique().tolist()}")
    
    # Calculate ultimates
    df_ultimates = project_ultimates(df_processed, df_selections, tail_factor=1.0)
    print(f"\nCalculated {len(df_ultimates)} ultimate projections")
    
    # Display sample
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', '{:.4f}'.format)
    
    if len(df_ultimates) > 0:
        first_measure = df_ultimates['measure'].unique()[0]
        first_scenario = df_ultimates['scenario'].unique()[0]
        
        sample = df_ultimates[
            (df_ultimates['measure'] == first_measure) &
            (df_ultimates['scenario'] == first_scenario)
        ].head(10)
        
        print(f"\nSample ultimates for {first_measure} - {first_scenario}:")
        print(sample)
    
    # Save outputs
    df_ultimates.to_parquet(OUTPUT_PATH + f"6_{METHOD_ID}_ultimates.parquet", index=False)
    df_ultimates.to_csv(OUTPUT_PATH + f"6_{METHOD_ID}_ultimates.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}6_{METHOD_ID}_ultimates.[parquet|csv]")
    print("parquet preserves categorical types, CSV for inspection")
