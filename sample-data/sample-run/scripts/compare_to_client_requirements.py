"""Compare current implementation to client requirements."""
import pandas as pd

print("=" * 70)
print("PRE-METHOD DIAGNOSTICS")
print("=" * 70)

df = pd.read_excel('../Analysis.xlsx', sheet_name='Pre-Method Diagnostics', header=None)
sections = []
for idx, row in df.iterrows():
    val = row[0]
    if pd.notna(val) and isinstance(val, str):
        if any(x in val.upper() for x in ['SEVERITY', 'INCURRED', 'PAID', 'CASE', 'OPEN', 'CLOSURE', 'LOSS', 'FREQUENCY']):
            sections.append(val)

print("\nCurrent layout (stacked vertically):")
for i, s in enumerate(sections, 1):
    print(f"  {i}. {s}")

print("\nClient wants (paired side-by-side):")
print("  1. Incurred Severity | Paid Severity")
print("  2. Case Reserves | Paid-to-Incurred")
print("  3. Average Open Case Reserves | Open Counts")
print("  4. Closure Rate | Incremental Closure Rate")
print("  5. Incurred Loss Rate | Paid Loss Rate")
print("  6. Reported Frequency | Closed Frequency")

print("\n" + "=" * 70)
print("POST-METHOD DIAGNOSTICS")
print("=" * 70)

df = pd.read_excel('../Analysis.xlsx', sheet_name='Post-Method Diagnostics', header=None)
sections = []
for idx, row in df.iterrows():
    val = row[0]
    if pd.notna(val) and isinstance(val, str):
        if any(x in val.upper() for x in ['TO-ULTIMATE', 'IBNR', 'UNPAID']):
            sections.append(val)

print("\nCurrent layout (stacked vertically):")
for i, s in enumerate(sections, 1):
    print(f"  {i}. {s}")

print("\nClient wants (paired side-by-side):")
print("  1. Incurred-to-Ultimate | Paid-to-Ultimate")
print("  2. Reported-to-Ultimate | Closed-to-Ultimate")
print("  3. Average IBNR | Average Unpaid")

print("\n" + "=" * 70)
print("FORMULA ISSUES")
print("=" * 70)
print("\nAverage IBNR:")
print("  Current:  (ultimate loss - incurred loss) / 1")
print("  Client:   (ultimate loss - incurred loss) / (ultimate counts - closed counts)")
print("\nAverage Unpaid:")
print("  Current:  (ultimate loss - paid loss) / 1")
print("  Client:   (ultimate loss - paid loss) / (ultimate counts - closed counts)")
