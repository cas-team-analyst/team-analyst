---
name: bornhuetter-ferguson
description: >
  Bornhuetter-Ferguson (BF) reserving method. Use when applying the BF method,
  computing credibility-weighted ultimates, or completing the final reserving pipeline.
---

# Bornhuetter-Ferguson Method

## What You Do

Run scripts 6 and 7 in sequence — both are fully automatic. No actuarial selections needed.

**Prerequisites:**
- `output/chain-ladder/cl_cdfs.csv` must exist (from script 4)
- `output/initial-expected/ie_ultimates.csv` must exist (from script 5)

```bash
python scripts/6-apply-bf.py
python scripts/7-combine-ultimates.py
```

## Outputs Written

| File | Description |
|------|-------------|
| `output/bornhuetter-ferguson/bornhuetter-ferguson.xlsx` | BF ultimates per measure |
| `output/selected-ultimates/selected-ultimates.xlsx` | CL / IE / BF side-by-side + selected |
| `output/post-method/post-method-series-diagnostics.xlsx` | Ultimate severity, loss rate, frequency |
| `output/post-method/post-method-triangle-diagnostics.xlsx` | X-to-Ultimate triangles + avg IBNR/Unpaid |
| `output/full-analysis.xlsx` | Master workbook with all sheets combined |

## BF Formula

```
BF Ultimate  = Actual + (1 − % developed) × Expected
% developed  = 1 / CDF
% unreported = 1 − % developed
IBNR         = (1 − % developed) × Expected  [= $ unreported/unpaid]
Unpaid       = BF Ultimate − Paid diagonal
```

BF Ultimate is always between the IE and CL estimates (credibility blend).

## Explaining the Results

After running both scripts, present the IBNR summary to the user. Key points to cover:
1. **BF vs CL** — BF gives more weight to IE for immature periods (low % developed)
2. **BF vs IE** — BF gives more weight to actual development for mature periods
3. **Selected ultimate** — the default selection is BF; the user can override in selected-ultimates.xlsx
