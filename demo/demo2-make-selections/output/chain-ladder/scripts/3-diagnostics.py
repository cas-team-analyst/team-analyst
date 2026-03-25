"""
goal: Create diagnostics that will support LDF selection.

usage: Run from project root:
    .venv/Scripts/Activate.ps1; python demo/demo2-make-selections/output/chain-ladder/scripts/3-diagnostics.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = str(SCRIPT_DIR / "../data/") + "/"
METHOD_ID = "chainladder"


def calculate_diagnostics(df_enhanced: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate actuarial diagnostics to help with LDF selection decisions.

    Diagnostics include:
    - Severities (Incurred/Paid per claim)
    - Paid to Incurred ratios
    - Average Case Reserve
    - Open claim counts
    - Claim closure rate and incremental closure rate
    """
    base_data = df_enhanced[['period', 'age']].drop_duplicates().reset_index(drop=True)

    measure_dfs = {}
    for measure in df_enhanced['measure'].unique():
        measure_subset = df_enhanced[df_enhanced['measure'] == measure].copy()
        grouped = measure_subset.groupby(['period', 'age'], observed=True)['value'].first().reset_index()
        key = measure.lower().replace(' ', '_')
        measure_dfs[key] = grouped.rename(columns={'value': key})

    result_df = base_data.copy()

    for measure_key in ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']:
        if measure_key in measure_dfs:
            result_df = result_df.merge(measure_dfs[measure_key], on=['period', 'age'], how='left')

    if 'incurred_loss' in result_df.columns and 'reported_count' in result_df.columns:
        result_df['incurred_severity'] = np.where(
            result_df['incurred_loss'] == 0, 0,
            result_df['incurred_loss'] / result_df['reported_count'].replace(0, np.nan)
        )

    if 'paid_loss' in result_df.columns and 'closed_count' in result_df.columns:
        result_df['paid_severity'] = np.where(
            result_df['paid_loss'] == 0, 0,
            result_df['paid_loss'] / result_df['closed_count'].replace(0, np.nan)
        )

    if 'paid_loss' in result_df.columns and 'incurred_loss' in result_df.columns:
        result_df['paid_to_incurred'] = np.where(
            result_df['paid_loss'] == 0, 0,
            result_df['paid_loss'] / result_df['incurred_loss'].replace(0, np.nan)
        )

    if 'reported_count' in result_df.columns and 'closed_count' in result_df.columns:
        result_df['open_counts'] = result_df['reported_count'] - result_df['closed_count']

    if all(col in result_df.columns for col in ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']):
        reserves = result_df['incurred_loss'] - result_df['paid_loss']
        opens = result_df['reported_count'] - result_df['closed_count']
        result_df['average_case_reserve'] = np.where(
            reserves == 0, 0,
            reserves / opens.replace(0, np.nan)
        )

    if 'closed_count' in result_df.columns and 'reported_count' in result_df.columns:
        result_df['claim_closure_rate'] = np.where(
            result_df['closed_count'] == 0, 0,
            result_df['closed_count'] / result_df['reported_count'].replace(0, np.nan)
        )

    result_df = result_df.sort_values(['period', 'age']).reset_index(drop=True)

    available_measures = ['incurred_loss', 'paid_loss', 'reported_count', 'closed_count']
    for col in available_measures:
        if col in result_df.columns:
            result_df[f'{col}_incr'] = result_df.groupby('period', observed=True)[col].diff()
            result_df[f'{col}_incr'] = result_df[f'{col}_incr'].fillna(result_df[col])

    if 'incurred_loss_incr' in result_df.columns and 'reported_count_incr' in result_df.columns:
        result_df['incremental_incurred_severity'] = np.where(
            result_df['incurred_loss_incr'] == 0, 0,
            result_df['incurred_loss_incr'] / result_df['reported_count_incr'].replace(0, np.nan)
        )

    if 'paid_loss_incr' in result_df.columns and 'closed_count_incr' in result_df.columns:
        result_df['incremental_paid_severity'] = np.where(
            result_df['paid_loss_incr'] == 0, 0,
            result_df['paid_loss_incr'] / result_df['closed_count_incr'].replace(0, np.nan)
        )

    if 'closed_count_incr' in result_df.columns and 'reported_count_incr' in result_df.columns:
        result_df['incremental_closure_rate'] = np.where(
            result_df['closed_count_incr'] == 0, 0,
            result_df['closed_count_incr'] / result_df['reported_count_incr'].replace(0, np.nan)
        )

    temp_cols = [col for col in result_df.columns if col.endswith('_incr') and col not in [
        'incremental_incurred_severity', 'incremental_paid_severity', 'incremental_closure_rate'
    ]]
    result_df = result_df.drop(columns=temp_cols)

    if 'reported_count' in result_df.columns:
        result_df = result_df.rename(columns={'reported_count': 'reported_claims'})

    measure_cols = ['incurred_loss', 'paid_loss', 'closed_count']
    result_df = result_df.drop(columns=[col for col in measure_cols if col in result_df.columns])

    result_df['period'] = result_df['period'].astype('category')
    result_df['age'] = result_df['age'].astype('category')

    return result_df


if __name__ == "__main__":
    input_file = OUTPUT_PATH + f"2_{METHOD_ID}_enhanced.parquet"
    df = pd.read_parquet(input_file)
    print(f"Loaded {len(df)} rows, {df['measure'].nunique()} measures")

    diagnostics_df = calculate_diagnostics(df)
    diag_cols = [c for c in diagnostics_df.columns if c not in ['period', 'age']]
    print(f"Calculated {len(diag_cols)} diagnostic columns: {diag_cols}")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', lambda x: f'{x:.2f}')

    sample_cols = [col for col in ['incurred_severity', 'paid_severity', 'paid_to_incurred'] if col in diagnostics_df.columns]
    if sample_cols:
        print("\nSample diagnostics (first 10 rows with data):")
        print(diagnostics_df.dropna(subset=sample_cols, how='all').head(10).to_string())

    numeric_cols = diagnostics_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        diagnostics_df[col] = diagnostics_df[col].round(4)

    diagnostics_df.to_parquet(OUTPUT_PATH + f"3_{METHOD_ID}_diagnostics.parquet", index=False)
    diagnostics_df.to_csv(OUTPUT_PATH + f"3_{METHOD_ID}_diagnostics.csv", index=False)
    print(f"\nSaved: {OUTPUT_PATH}3_{METHOD_ID}_diagnostics.[parquet|csv]")
