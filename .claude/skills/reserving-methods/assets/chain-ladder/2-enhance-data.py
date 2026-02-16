"""
goal: Add calculated columns needed for chain ladder. These should typically not be changed, they should work with the format of the data output by 1-prep-data.py.
contents:
    enhance_triangle_data(): Add calculated columns (prior_age, ldf, weight) to the long format triangle data.
"""

import pandas as pd
import numpy as np

# Replace when using this file in an actual project:
OUTPUT_PATH = "../test-output/"
METHOD_ID = "chainladder"


def enhance_triangle_data(df_long: pd.DataFrame) -> pd.DataFrame:
    """
    Enhance triangle data by adding prior_age, ldf, and weight columns.
    
    For each (period, measure, source) combination:
    - prior_age: The previous development age
    - ldf: Loss Development Factor (current value / prior value)
    - weight: Volume weight for the LDF (equals prior value)
    
    The first age for each group will have NA values for these columns.
    
    Args:
        df_long: Long format DataFrame with columns: period, age, value, measure, source
                 Should come from 1-data-prep.py output
    
    Returns:
        DataFrame with additional columns: prior_age, ldf, weight, interval
    """
    # Make a copy to avoid modifying original
    df_enhanced = df_long.copy()
    
    # Get the age categories to map previous age
    ages = df_enhanced['age'].cat.categories.tolist()
    
    # Sort by grouping keys and age to ensure proper order
    # Use categorical codes for age to ensure correct ordering
    df_enhanced['_age_sort'] = df_enhanced['age'].cat.codes
    df_enhanced = df_enhanced.sort_values(['measure', 'source', 'period', '_age_sort'])
    df_enhanced = df_enhanced.drop(columns=['_age_sort']).reset_index(drop=True)
    
    # Group by period, measure, and source
    grouping_cols = ['period', 'measure', 'source']
    
    # Within each group, shift age and value to get prior values
    df_enhanced['prior_age'] = df_enhanced.groupby(grouping_cols, observed=True)['age'].shift(1)
    df_enhanced['prior_value'] = df_enhanced.groupby(grouping_cols, observed=True)['value'].shift(1)
    
    # Calculate LDF: current value / prior value
    df_enhanced['ldf'] = df_enhanced['value'] / df_enhanced['prior_value'].replace(0, np.nan)
    
    # Weight is the prior value (used for volume-weighted averages)
    df_enhanced['weight'] = df_enhanced['prior_value']
    
    # Drop the temporary prior_value column
    df_enhanced = df_enhanced.drop(columns=['prior_value'])
    
    # Convert prior_age to categorical with same categories as age
    df_enhanced['prior_age'] = pd.Categorical(
        df_enhanced['prior_age'], 
        categories=ages, 
        ordered=True
    )
    
    # Create interval label for convenience (e.g., "12-24")
    df_enhanced['interval'] = df_enhanced.apply(
        lambda row: f"{row['prior_age']}-{row['age']}" if pd.notna(row['prior_age']) else None,
        axis=1
    )
    
    # Convert interval to categorical with proper ordering based on age sequence
    # Get all valid intervals in order by iterating through consecutive age pairs
    valid_intervals = []
    for i in range(len(ages) - 1):
        valid_intervals.append(f"{ages[i]}-{ages[i+1]}")
    
    df_enhanced['interval'] = pd.Categorical(
        df_enhanced['interval'],
        categories=valid_intervals,
        ordered=True
    )
    
    return df_enhanced


if __name__ == "__main__":
    """Test the enhance_triangle_data function."""
    # Read processed data from step 1
    input_file = OUTPUT_PATH + f"1_{METHOD_ID}_processed_data.parquet"
    df = pd.read_parquet(input_file)
    print(f"Loaded {len(df)} rows, {df['measure'].nunique()} measures, {df['source'].nunique()} sources")
    
    # Enhance the data
    df_enhanced = enhance_triangle_data(df)
    print(f"\nEnhanced data: {len(df_enhanced)} rows, {df_enhanced['ldf'].notna().sum()} with LDFs")
    
    # Display sample
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print("\nSample (first 10 rows with LDFs):")
    print(df_enhanced[df_enhanced['ldf'].notna()].head(10))
    
    # Round numeric columns to 4 decimal places
    numeric_cols = ['value', 'ldf', 'weight']
    for col in numeric_cols:
        if col in df_enhanced.columns:
            df_enhanced[col] = df_enhanced[col].round(4)
    
    # Save outputs
    df_enhanced.to_parquet(OUTPUT_PATH + f"2_{METHOD_ID}_enhanced_data.parquet", index=False)
    df_enhanced.to_csv(OUTPUT_PATH + f"2_{METHOD_ID}_enhanced_data.csv", index=False)
    print(f"\nSaved to: {OUTPUT_PATH}2_{METHOD_ID}_enhanced_data.[parquet|csv]")
    print("parquet preserves categorical types, CSV for inspection")

