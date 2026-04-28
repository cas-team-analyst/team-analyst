import pandas as pd
import numpy as np

df = pd.read_parquet('../processed-data/2_enhanced.parquet')
periods = sorted(df['period'].unique())

print(f'Total periods: {len(periods)}')
print(f'Last 3 periods in sheet: {periods[-3:]}')

df_inc = df[(df['measure'] == 'Incurred Loss') & (df['interval'] == '23-35')]

print(f'\nLDF values for last 3 periods (Excel rows 49-51):')
for p in periods[-3:]:
    val = df_inc[df_inc['period'] == p]['ldf'].values
    if len(val) > 0 and pd.notna(val[0]):
        print(f'  {p}: {val[0]:.4f}')
    else:
        print(f'  {p}: (no data)')

# Check what Excel STDEV.S/AVERAGE would calculate (ignores blanks)
ldfs_in_range = []
for p in periods[-3:]:
    val = df_inc[df_inc['period'] == p]['ldf'].values
    if len(val) > 0 and pd.notna(val[0]):
        ldfs_in_range.append(val[0])

if ldfs_in_range:
    print(f'\nExcel formula would use these {len(ldfs_in_range)} non-blank values:')
    print(f'  Values: {ldfs_in_range}')
    if len(ldfs_in_range) > 1:
        print(f'  Mean: {np.mean(ldfs_in_range):.4f}')
        print(f'  Stdev: {np.std(ldfs_in_range, ddof=1):.4f}')
        print(f'  CV: {np.std(ldfs_in_range, ddof=1)/np.mean(ldfs_in_range):.4f}')

# Now check what Python calculates (last 3 with data)
df_inc_with_data = df_inc[df_inc['ldf'].notna()].sort_values('period')
ldfs_last3 = df_inc_with_data['ldf'].tail(3).values
print(f'\nPython .tail(3) uses:')
print(f'  Periods: {df_inc_with_data["period"].tail(3).values}')
print(f'  Values: {ldfs_last3}')
print(f'  Mean: {np.mean(ldfs_last3):.4f}')
print(f'  Stdev: {np.std(ldfs_last3, ddof=1):.4f}')
print(f'  CV: {np.std(ldfs_last3, ddof=1)/np.mean(ldfs_last3):.4f}')
