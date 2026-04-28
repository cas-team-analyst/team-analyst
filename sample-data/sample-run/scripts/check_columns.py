import pandas as pd

def col_letter(col_idx):
    """Convert 0-based column index to Excel column letter"""
    result = ''
    while col_idx >= 0:
        result = chr(col_idx % 26 + ord('A')) + result
        col_idx = col_idx // 26 - 1
    return result

df = pd.read_parquet('../processed-data/2_enhanced.parquet')
df_inc = df[df['measure'] == 'Incurred Loss']
intervals = [str(i) for i in df_inc['interval'].dropna().cat.categories.tolist()]

print('Interval to Column mapping in Excel:')
for idx, intv in enumerate(intervals):
    col_letter_val = col_letter(idx + 1)  # +1 because col 0 is "Period"
    print(f'  Interval {intv:10s} -> Column {col_letter_val} (index {idx+1})')

print(f'\nInterval 23-35 is at position: {intervals.index("23-35")}')
print(f'Maps to column: {col_letter(intervals.index("23-35") + 1)}')
