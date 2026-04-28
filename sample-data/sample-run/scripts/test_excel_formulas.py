"""
Test what formula syntax Excel actually accepts for external workbook references.
Open this in Excel and manually inspect the formulas.
"""
import win32com.client
import time
import os

# Get absolute paths
base = os.path.abspath('..')
selections_path = os.path.join(base, 'selections', 'Chain Ladder Selections - LDFs.xlsx')
test_path = os.path.join(base, 'test-excel-refs.xlsx')

print(f"Creating test workbook: {test_path}")
print(f"Referencing: {selections_path}")

# Open Excel
xl = win32com.client.DispatchEx("Excel.Application")
xl.Visible = True
xl.DisplayAlerts = False

# Create new workbook
wb_test = xl.Workbooks.Add()
ws = wb_test.Sheets(1)

# First, open the selections workbook so we can reference it
wb_sel = xl.Workbooks.Open(selections_path)

# Method 1: Reference while both workbooks are open
ws.Cells(1, 1).Value = "Method 1: Both workbooks open"
ws.Cells(1, 2).Formula = "='[Chain Ladder Selections - LDFs.xlsx]Incurred Loss'!B3"

# Method 2: Use full path (for when source is closed)
ws.Cells(2, 1).Value = "Method 2: Full path with brackets"
ws.Cells(2, 2).Formula = f"='{selections_path}'!'Incurred Loss'!B3"

# Method 3: Relative path attempt
ws.Cells(3, 1).Value = "Method 3: Relative path, no brackets"
ws.Cells(3, 2).Formula = "='selections\\Chain Ladder Selections - LDFs.xlsx'!'Incurred Loss'!B3"

# Save test workbook
wb_test.SaveAs(test_path)

# Get the formulas as Excel wrote them
print("\nFormulas as written by Python:")
print(f"B1: {ws.Cells(1, 2).Formula}")
print(f"B2: {ws.Cells(2, 2).Formula}")
print(f"B3: {ws.Cells(3, 2).Formula}")

# Close selections workbook
wb_sel.Close(SaveChanges=False)

# Force recalculation
xl.CalculateFullRebuild()

# Check what formulas look like after recalculation
print("\nFormulas after closing selections workbook and recalculating:")
print(f"B1: {ws.Cells(1, 2).Formula}")
print(f"B1 value: {ws.Cells(1, 2).Value}")
print(f"B2: {ws.Cells(2, 2).Formula}")
print(f"B2 value: {ws.Cells(2, 2).Value}")
print(f"B3: {ws.Cells(3, 2).Formula}")
print(f"B3 value: {ws.Cells(3, 2).Value}")

# Save and close
wb_test.Save()
wb_test.Close()
xl.Quit()

print(f"\nTest workbook saved to: {test_path}")
print("Open it in Excel to see which formula syntax works!")
