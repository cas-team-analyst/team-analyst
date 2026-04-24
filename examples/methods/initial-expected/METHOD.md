---
name: initial-expected
description: >
  Initial expected (IE) loss method. Use when providing expected ultimate losses,
  expected loss ratios, or premium inputs for actuarial reserving.
---

# Initial Expected Method

## What You Do

Help the user provide expected ultimate inputs and write them to
`output/selections/ie_inputs.json`. Then run script 5 — no actuarial selections required.

```bash
python scripts/5-apply-ie.py
```
Output: `output/initial-expected/initial-expected.xlsx`

## Input Format

Create `output/selections/ie_inputs.json` using one of two styles:

**Style A — Direct expected ultimate:**
```json
[
  {"period": "2015", "measure": "Incurred Loss",   "expected_ultimate": 47483901.76},
  {"period": "2015", "measure": "Paid Loss",        "expected_ultimate": 47708943.93},
  {"period": "2015", "measure": "Reported Count",   "expected_ultimate": 4930},
  {"period": "2015", "measure": "Closed Count",     "expected_ultimate": 5029.62},
  ...
]
```

**Style B — Expected loss ratio × premium:**
```json
[
  {"period": "2015", "measure": "Incurred Loss", "elr": 0.72, "premium": 65955419.11},
  ...
]
```

## What the Output Shows

`output/initial-expected/initial-expected.xlsx` contains:
- **Loss sheet**: Accident Period, Current Age, Exposure, Selected Loss Rate, Selected Loss (IE ultimate for incurred loss)
- **Counts sheet**: Accident Period, Current Age, Exposure, Selected Frequency, Selected Counts (IE ultimate for reported count)

`ie_ultimates.csv` retains full internal detail for downstream BF (all measures per period).

No trend factor calculations are required at this stage.
