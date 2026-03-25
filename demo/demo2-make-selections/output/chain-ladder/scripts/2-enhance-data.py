"""
goal: Add calculated columns needed for chain ladder (prior_age, ldf, weight, interval).

usage: Run from project root:
    .venv/Scripts/Activate.ps1; python demo/demo2-make-selections/output/chain-ladder/scripts/2-enhance-data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = str(SCRIPT_DIR / "../data/") + "/"
METHOD_ID = "chainladder"


def enhance_triangle_data(df_long: pd.DataFrame) -> pd.DataFrame:
    """
    Enhance triangle data by adding prior_age, ldf, weight, and interval columns.

    For each (period, measure, source) combination:
    - prior_age: The previous development age
    - ldf: Loss Development Factor (current value / prior value)
    - weight: Volume weight for the LDF (equals prior value)
    - interval: Label like "15-27" for age-to-age step

    The first age for each group will have NA values for prior_age, ldf, weight.
    """
    df_enhanced = df_long.copy()
    ages = df_enhanced['age'].cat.categories.tolist()

    df_enhanced['_age_sort'] = df_enhanced['age'].cat.codes
    df_enhanced = df_enhanced.sort_values(['measure', 'source', 'period', '_age_sort'])
    df_enhanced = df_enhanced.drop(columns=['_age_sort']).reset_index(drop=True)

    grouping_cols = ['period', 'measure', 'source']
    df_enhanced['prior_age'] = df_enhanced.groupby(grouping_cols, observed=True)['age'].shift(1)
    df_enhanced['prior_value'] = df_enhanced.groupby(grouping_cols, observed=True)['value'].shift(1)
    df_enhanced['ldf'] = df_enhanced['value'] / df_enhanced['prior_value'].replace(0, np.nan)
    df_enhanced['weight'] = df_enhanced['prior_value']
    df_enhanced = df_enhanced.drop(columns=['prior_value'])

    df_enhanced['prior_age'] = pd.Categorical(df_enhanced['prior_age'], categories=ages, ordered=True)

    df_enhanced['interval'] = df_enhanced.apply(
        lambda row: f"{row['prior_age']}-{row['age']}" if pd.notna(row['prior_age']) else None,
        axis=1
    )

    valid_intervals = [f"{ages[i]}-{ages[i+1]}" for i in range(len(ages) - 1)]
    df_enhanced['interval'] = pd.Categorical(
        df_enhanced['interval'], categories=valid_intervals, ordered=True
    )

    return df_enhanced


if __name__ == "__main__":
    input_file = OUTPUT_PATH + f"1_{METHOD_ID}_prepped.parquet"
    df = pd.read_parquet(input_file)
    print(f"Loaded {len(df)} rows, {df['measure'].nunique()} measures, {df['source'].nunique()} sources")

    df_enhanced = enhance_triangle_data(df)
    print(f"Enhanced data: {len(df_enhanced)} rows, {df_enhanced['ldf'].notna().sum()} with LDFs")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print("\nSample (first 5 rows with LDFs):")
    print(df_enhanced[df_enhanced['ldf'].notna()].head(5).to_string())

    numeric_cols = ['value', 'ldf', 'weight']
    for col in numeric_cols:
        if col in df_enhanced.columns:
            df_enhanced[col] = df_enhanced[col].round(4)

    df_enhanced.to_parquet(OUTPUT_PATH + f"2_{METHOD_ID}_enhanced.parquet", index=False)
    df_enhanced.to_csv(OUTPUT_PATH + f"2_{METHOD_ID}_enhanced.csv", index=False)
    print(f"\nSaved: {OUTPUT_PATH}2_{METHOD_ID}_enhanced.[parquet|csv]")
