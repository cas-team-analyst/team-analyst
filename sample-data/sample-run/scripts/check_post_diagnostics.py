"""Quick check of Post-Method Diagnostics sheet structure."""
import pandas as pd

wb = pd.ExcelFile('../Analysis.xlsx')
print("Available sheets:", wb.sheet_names)
print()

df = pd.read_excel('../Analysis.xlsx', sheet_name='Post-Method Diagnostics', header=None)

# Find section headers
print("Post-Method Diagnostics sections:")
for idx, row in df.iterrows():
    val = row[0]
    if pd.notna(val) and isinstance(val, str):
        if any(x in val.upper() for x in ['SERIES', 'TO-ULTIMATE', 'IBNR', 'UNPAID']):
            print(f"  Row {idx+1}: {val}")

print()
print("Series diagnostics data (first 5 periods):")
df_series = pd.read_excel('../Analysis.xlsx', sheet_name='Post-Method Diagnostics', 
                          skiprows=1, nrows=5)
print(df_series)

print()
print("First triangle diagnostic (Incurred-to-Ultimate) sample:")
# Find the row with INCURRED-TO-ULTIMATE
inc_row = None
for idx, row in df.iterrows():
    if pd.notna(row[0]) and 'INCURRED-TO-ULTIMATE' in str(row[0]):
        inc_row = idx
        break

if inc_row:
    # Read next few rows
    print(df.iloc[inc_row:inc_row+6, :6].to_string())
