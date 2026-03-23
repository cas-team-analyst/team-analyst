This file contains steps to replicate results.

## Data Files

| File | Size | Last Modified | Notes |
|------|------|---------------|-------|
| data/Triangle Examples 1.xlsx | — | — | WC paid/incurred triangles, AY 2001-2024 |

## Chain Ladder Scripts

Run each script from `output/chain-ladder/scripts/`:

```bash
cd output/chain-ladder/scripts
python 1-prep-data.py    # Read Excel triangles → processed_data.parquet/csv
python 2-enhance-data.py # Add LDFs, weights, intervals → enhanced_data.parquet/csv
python 3-diagnostics.py  # Paid-to-incurred ratios → diagnostics.parquet/csv
python 4-averages-qa.py  # LDF averages & CV/slope metrics → ldf_averages.parquet/csv
```

Output files are saved to `output/chain-ladder/processed/`.

```bash
python 5-create-selections-excel.py  # Build selections Excel -> output/selections/Chain Ladder Selections.xlsx
```
