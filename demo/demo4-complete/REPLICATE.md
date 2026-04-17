This file contains steps to replicate results.

## Files Required

| File | Location | Notes |
|---|---|---|
| canonical-triangles.xlsx | raw-data/ | Triangle data: Incurred, Paid, Reported, Closed, Exposure sheets. AYs 2015–2024, ages 12–120. |
| canonical-elrs.xlsx | raw-data/ | Expected Loss Rates and Expected Frequency by accident year 2015–2024. |

## Scripts (run from scripts/ directory)

| Script | Purpose |
|---|---|
| 1a-prep-data.py | Read raw data, resolve formula-based AY labels, output canonical parquet/CSV |
| 1b-enhance-data.py | Add derived columns (LDFs, etc.) |
| 1c-diagnostics.py | Compute diagnostics |
| 1d-averages-qa.py | Compute LDF averages for QA |
| 2a-chainladder-create-excel.py | Create Chain Ladder Selections workbook |
| 2b-chainladder-update-selections.py | Write AI/rule-based LDF selections into workbook |
| 2c-chainladder-ultimates.py | Project ultimates via Chain Ladder |
| 3-ie-ultimates.py | Project ultimates via Initial Expected |
| 4-bf-ultimates.py | Project ultimates via Bornhuetter-Ferguson |
| 5a-ultimates-create-excel.py | Create Ultimates selections workbook |
| 5b-ultimates-update-selections.py | Write AI ultimate selections into workbook |
| 6-create-complete-analysis.py | Compile complete analysis output |
| 7-tech-review.py | Run technical review checks |

## Manual Edits

*(None yet — will be logged here as they occur)*
