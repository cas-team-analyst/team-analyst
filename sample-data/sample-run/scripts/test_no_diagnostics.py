from openpyxl import load_workbook

wb = load_workbook('../Analysis.xlsx')
sheets = [ws.title for ws in wb.worksheets]

print('All sheets:')
for s in sheets:
    print(f'  {s}')

print(f'\nTotal sheets: {len(sheets)}')
print(f'Summary Diagnostics exists: {"Summary Diagnostics" in sheets}')

wb.close()
