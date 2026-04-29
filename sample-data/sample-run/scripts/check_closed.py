import pandas as pd

ult = pd.read_parquet('../ultimates/projected-ultimates.parquet')
cc = ult[ult['measure'] == 'Closed Count']

print('Closed Count data:')
print(cc[['period', 'actual', 'ultimate_cl']].head())
print(f'\nTotal rows: {len(cc)}')
print(f'Non-null actual: {cc["actual"].notna().sum()}')
print(f'All actual values: {cc["actual"].unique()}')
