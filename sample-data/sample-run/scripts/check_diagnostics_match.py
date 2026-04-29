"""Verify diagnostic columns match between selection sheets and Post-Method Diagnostics."""
import pandas as pd

loss = pd.read_excel('../Analysis.xlsx', sheet_name='Loss Selection')
count = pd.read_excel('../Analysis.xlsx', sheet_name='Count Selection')
post = pd.read_excel('../Analysis.xlsx', sheet_name='Post-Method Diagnostics')

print('Period 2001 comparison:')
print(f'  Loss Selection - Ultimate Loss Rate:  {loss.iloc[0]["Ultimate Loss Rate"]:.6f}')
print(f'  Post-Method    - Ultimate Loss Rate:  {post.iloc[0]["Ultimate Loss Rate"]:.6f}')
print()
print(f'  Count Selection - Ultimate Severity:   {count.iloc[0]["Ultimate Severity"]:.6f}')
print(f'  Post-Method     - Ultimate Severity:   {post.iloc[0]["Ultimate Severity"]:.6f}')
print()
print(f'  Count Selection - Ultimate Frequency:  {count.iloc[0]["Ultimate Frequency"]:.9f}')
print(f'  Post-Method     - Ultimate Frequency:  {post.iloc[0]["Ultimate Frequency"]:.9f}')
print()
print('✓ All values match!' if (
    abs(loss.iloc[0]["Ultimate Loss Rate"] - post.iloc[0]["Ultimate Loss Rate"]) < 0.000001 and
    abs(count.iloc[0]["Ultimate Severity"] - post.iloc[0]["Ultimate Severity"]) < 0.000001 and
    abs(count.iloc[0]["Ultimate Frequency"] - post.iloc[0]["Ultimate Frequency"]) < 0.000001
) else '✗ Values do not match')
