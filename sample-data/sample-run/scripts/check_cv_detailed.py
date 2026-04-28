import pandas as pd
import numpy as np

# What the Excel formula is doing
ldf_start_row_excel = 28
ldf_end_row_excel = 51
n_periods = 3
range_start_row_excel = ldf_end_row_excel - n_periods + 1

print(f'Excel CV_3yr formula uses range: rows {range_start_row_excel}-{ldf_end_row_excel}')
print(f'That is row {range_start_row_excel} to row {ldf_end_row_excel} (inclusive)')
print(f'Which are period indices {range_start_row_excel - ldf_start_row_excel} to {ldf_end_row_excel - ldf_start_row_excel} (0-based)')

# Load data and check
df = pd.read_parquet('../processed-data/2_enhanced.parquet')
periods = sorted(df['period'].unique())

period_idx_start = range_start_row_excel - ldf_start_row_excel
period_idx_end = ldf_end_row_excel - ldf_start_row_excel

print(f'\nPeriods that would be: {periods[period_idx_start:period_idx_end+1]}')

# Now check what LDF values exist in those rows for interval 23-35
df_inc = df[(df['measure'] == 'Incurred Loss') & (df['interval'] == '23-35')]

print(f'\nLDF values in those Excel formula rows for interval 23-35:')
for idx in range(period_idx_start, period_idx_end + 1):
    p = periods[idx]
    val = df_inc[df_inc['period'] == p]['ldf'].values
    if len(val) > 0 and pd.notna(val[0]):
        print(f'  Row {ldf_start_row_excel + idx}, Period {p}: {val[0]:.4f}')
    else:
        print(f'  Row {ldf_start_row_excel + idx}, Period {p}: (blank)')

# Simulate STDEV.S/AVERAGE behavior (ignores blanks)
ldfs = []
for idx in range(period_idx_start, period_idx_end + 1):
    p = periods[idx]
    val = df_inc[df_inc['period'] == p]['ldf'].values
    if len(val) > 0 and pd.notna(val[0]):
        ldfs.append(val[0])

if len(ldfs) > 1:
    print(f'\nExcel would calculate CV from {len(ldfs)} non-blank cells:')
    print(f'  Values: {ldfs}')
    print(f'  STDEV.S: {np.std(ldfs, ddof=1):.4f}')
    print(f'  AVERAGE: {np.mean(ldfs):.4f}')
    print(f'  CV: {np.std(ldfs, ddof=1)/np.mean(ldfs):.4f}')
elif len(ldfs) == 1:
    print(f'\nExcel has only 1 non-blank cell, STDEV.S would return #DIV/0! error')
else:
    print(f'\nExcel has no data in range')

# Now check what the Python script calculated and cached
df4 = pd.read_parquet('../processed-data/4_ldf_averages.parquet')
cached_cv = df4[(df4['measure'] == 'Incurred Loss') & (df4['interval'] == '23-35')]['cv_3yr'].values[0]
print(f'\nCached value from df4 (Python .tail(3)): {cached_cv:.4f}')
