---
name: validate-data
description: Load and validate actuarial data provided by the user to ensure it meets required formats and quality standards before performing actuarial analysis.
---
# Validate Data Skill

This skill provides a standardized approach to loading and validating actuarial data. All user interaction is handled by the agent following the instructions below; the Python scripts in `scripts/` are pure utility functions with no prompts.

## Instructions

### Step 1 — Load Data (`scripts/1-load-data.py`)

Ask the user:
> "Please provide the full path to your data file. Accepted formats: `.csv`, `.xlsx`, `.xlsm`, `.xls`"

Once you have the path, call `load_data()`:

```python
from scripts.`1-load-data` import load_data

df = load_data("path/to/file.xlsx", sheet_name="Sheet1")
```

If a `FileNotFoundError` or `ValueError` is raised, report the error to the user and ask them to provide a corrected path or file.

---

### Step 2 — Identify Format (`scripts/2-identify-data-format.py`)

Ask the user:
> "What format is your data in?
> 1 — **Loss Run**: long format, one row per claim per evaluation date
> 2 — **Triangle**: wide format, rows = origin periods, columns = development periods"

Once you have their answer, call `summarize()` with the appropriate format string, then display the result:

```python
from scripts.`2-identify-data-format` import summarize

summary = summarize(df, fmt="loss_run")  # or "triangle"
print(summary.report())
```

After displaying the report, ask the user:
> "Does this look correct? Should we continue?"

- If **yes** → proceed to the next validation step.
- If **no** → ask the user what looks wrong and return to Step 1 if needed.

---

### Step 3 — Check Format (`scripts/3-check-format.py`)

Run all five diagnostic tests against the loaded data and file path:

```python
from scripts.`3-check-format` import run_all_checks

results = run_all_checks(df, file_path="path/to/file.xlsx")
```

The tests return **raw facts only** — do not synthesize a conclusion or calculate a score. Use the findings to identify any discrepancies between what the user said their data format is and what the data actually shows. If one or more findings conflict with the stated format, surface them in plain language using the pattern below:

> "You indicated that **{fileName}** contains **{format}**, but:
> 1) {finding that conflicts} — _{brief factual observation}_
> 2) {finding that conflicts} — _{brief factual observation}_
> ...
> Are you sure you selected the correct file and format? I may not produce reasonable results if I cannot accurately parse your input."

Only report findings that **conflict** with the stated format. Do not report findings that are consistent with it. If all findings are consistent, proceed silently to Step 4.

#### Test descriptions and what each finding means

| Test | Field(s) | Loss-run signal | Triangle signal |
|---|---|---|---|
| **1. Column names** | `claim_id_columns` | Non-empty list (has claim/file/policy column) | Empty list |
| | `origin_period_columns` | Empty list | Non-empty list |
| | `dev_period_columns` | Empty list | Non-empty list |
| **2. Data shape** | `row_col_ratio` | > 5 (tall, many rows) | ≤ 3 (roughly square) |
| | `avg_records_per_claim` | > 1 (multiple evals per claim) | None (no claim column) |
| | `null_corner_pct` | Low (≈ 0%) | High (> 30%), staircase pattern |
| | `last_col_null_pct` | Low | High |
| **3. Tab count** | `tab_count` / `tab_names` | ≤ 2 tabs, named for claims/exposure | Often > 1, tabs named for data types |
| **4. Date columns** | `total_date_columns` | ≥ 2 date columns typical | 0–1 date columns |
| **5. Numeric density** | `numeric_ratio` | < 0.6 (mixed text, dates, numbers) | ≥ 0.8 (mostly numeric) |

---

### Step 4 — Identify Available Data Elements

Ask the user:
> "Which of the following data elements are present in your file? Select all that apply:
> 1 — Incurred Losses
> 2 — Paid Losses
> 3 — Reported Counts
> 4 — Closed Counts
> 5 — Exposure"

Record the user's selections. If **Exposure** is included, ask a follow-up:
> "Is the exposure data in **long format** (one column of exposure values, one row per origin period) or **wide/triangle format** (a separate triangle with origin periods as rows and development periods as columns)?"

Record the exposure format as either `"long"` or `"triangle"`. Store all selections for use in the validation step.

---

### Step 5 — Validate Loss Run (`scripts/4-validate-loss-run.py`)

*Run this step only when the user confirmed **loss run** format in Step 2.*

```python
from scripts.`4-validate-loss-run` import validate_loss_run, build_summary_statistics

# selected_measures: list of keys the user chose in Step 4
# valid keys: "incurred_losses", "paid_losses", "reported_counts", "closed_counts"
results = validate_loss_run(df, selected_measures=["incurred_losses", "paid_losses"])
```

The function runs eight checks and returns raw findings. Use them as follows:

#### 5a — Structural checks (report any failures immediately)

| Check | Field | Failure condition | What to tell the user |
|---|---|---|---|
| **1. Claim ID** | `results.claim_id.found` | `False` | No column matched a claim number pattern. List all columns and ask the user to identify the claim ID column. |
| **2. Origin period** | `results.origin_period.found` | `False` | No accident/origin period column found. Ask the user to identify it. |
| **3. Origin format** | `results.origin_format.is_consistent` | `False` | Show `detected_formats` and `unrecognised_values`. Ask whether the column contains mixed formats or needs cleaning. |
| **4. Measure columns** | `results.measure_columns.missing` | Non-empty list | Name the missing measures. Ask the user to identify which column maps to each. |
| | `results.measure_columns.ambiguous` | Non-empty dict | Name the ambiguous measures and their candidates. Ask the user to confirm which column to use. |
| **5. Numeric measures** | `results.numeric_measures.is_convertible` | Any `False` | Show the column name and up to 5 `problem_values`. Ask the user whether to exclude or fix those rows. |
| **6. Eval date** | `results.eval_date.found` | `False` | No evaluation date column found. Ask the user to identify it. |
| **7. Duplicates** | `results.duplicates.duplicate_count` | `> 0` | Report the count and show up to 10 `example_duplicates`. Ask the user whether to deduplicate by keeping the last record or to investigate further. |

If any structural check fails, pause here and resolve with the user before continuing.

#### 5b — Isolated anomalies (flag and let the user decide)

After structural checks pass, inspect `results.isolated_issues` and flag any of the following:

- **Fully-null measure rows** (`fully_null_measure_rows`): list the row indices and ask whether to exclude them.
- **High-null columns** (`high_null_columns`): name each column and its null %. Ask if that is expected or if the column should be excluded.
- **Negative values** (`negative_value_columns`, `negative_value_rows`): name the columns and row indices. Ask the user to confirm whether negatives are valid (e.g. recoveries) or should be treated as errors.
- **Incurred < paid** (`incurred_less_than_paid_rows`): list the row indices. Ask whether these are data errors or legitimate (e.g. salvage/subrogation).

For each anomaly, ask: *"Would you like to exclude these rows/columns, leave them as-is, or fix them manually before continuing?"*

#### 5c — Summary confirmation

Once all anomalies are resolved, build and present summary statistics:

```python
summary = build_summary_statistics(
    df,
    claim_col=results.claim_id.selected_column,
    origin_col=results.origin_period.selected_column,
    eval_col=results.eval_date.selected_column,
    resolved_columns=results.measure_columns.resolved,
)
```

Present the following to the user and ask for confirmation before proceeding:

- Total rows and unique claim count
- List of origin periods
- List of evaluation dates
- For each measure column: min, max, mean, and % null

> "Here is a summary of your loss run data. Please confirm this looks correct before I proceed:
> - **{n_rows}** total records covering **{n_unique_claims}** unique claims
> - **Origin periods**: {origin_periods}
> - **Evaluation dates**: {eval_dates}
> - **{measure}** ({column}): min={min}, max={max}, mean={mean}, {pct_null}% null
> - ...
> Does this look correct?"

---

### Step 6 — Convert Incremental Triangles to Cumulative (`scripts/4b1-convert-to-cumulative.py`)

*Run this step only when the user confirmed **triangle** format in Step 2.*

Ask the user:
> "Are your triangles **cumulative** (each cell = total to date) or **incremental** (each cell = activity in that development period only)?"

- If **cumulative** → skip this step and proceed to Step 7 using the original file.
- If **incremental** → run the conversion script below.

```python
from scripts.`4b1-convert-to-cumulative` import convert_to_cumulative

# resolved_tabs: agent's confirmed mapping from Step 7a tab-check
# (run the tab check described in 7a first, then pass the resolved mapping here)
result = convert_to_cumulative(
    file_path="path/to/triangles.xlsx",
    resolved_tabs={"incurred_losses": "Incurred", "paid_losses": "Paid"},
)
```

The function saves a new file to the same directory as the original, with `-cumulative` appended to the filename:
> e.g. `triangles.xlsx` → `triangles-cumulative.xlsx`

If any tabs failed to convert (`result.failed_tabs` is non-empty), report each failure and ask the user whether to fix the source data or skip that measure.

Tell the user:
> "I've converted your incremental triangles to cumulative form and saved the result to **{result.output_path}**. I'll use this file for all remaining validation checks."

Store `result.output_path` as the active file path for Step 7.

---

### Step 7 — Validate Triangle (`scripts/4b2-validate-triangle.py`)

*Uses the original file (if cumulative) or the `-cumulative` file produced in Step 6 (if incremental). All input DataFrames passed to this script must be in cumulative form.*

#### 7a — Tab mapping check (file-level)

```python
from scripts.`4b2-validate-triangle` import (
    validate_all_triangles, build_summary_statistics
)

# file_path: original file if cumulative; cumulative-converted file if incremental
# selected_measures: keys from Step 4 — "incurred_losses", "paid_losses", etc.
tab_findings, results = validate_all_triangles(
    file_path="path/to/triangles-cumulative.xlsx",
    selected_measures=["incurred_losses", "paid_losses"],
    triangle_type="cumulative",   # always "cumulative" at this point
    resolved_tabs={"incurred_losses": "Incurred", "paid_losses": "Paid"},
)
```

| Field | Failure condition | What to ask the user |
|---|---|---|
| `tab_findings.missing` | Non-empty | No tab matched measure. List all tab names and ask user to identify the correct one. |
| `tab_findings.ambiguous` | Non-empty | Multiple tabs matched. Show candidates and ask user to select. |

Resolve all tab mapping issues before proceeding to per-triangle checks.

#### 7b — Structural checks (per triangle, report failures immediately)

For each triangle in `results`:

| Check | Field | Failure condition | What to tell the user |
|---|---|---|---|
| **1. Origin column** | `origin_period_col.found_exactly_one` | `False` | Show `matched_columns`. Ask user to identify the origin period column. |
| **2. Dev period row** | `dev_period_row.header_appears_valid` | `False` | No dev period labels detected in column headers. Ask user to confirm the header row. |
| **3. Origin format** | `origin_format.is_consistent` | `False` | Show `detected_formats` and `unrecognised_values`. Ask if formats are mixed or need cleaning. |
| **4. Top-left nulls** | `top_left_nulls.has_unexpected_nulls` | `True` | Show up to 10 `unexpected_null_cells` (row index, column). Ask user how to handle: interpolate by origin period, interpolate by development period, or ignore in average calculations. |
| **5. Period intervals** | `period_intervals.origin_interval_is_regular` or `dev_interval_is_regular` | `False` | Show the irregular intervals. Ask if this is expected (e.g. mixed annual/quarterly) or a data issue. |
| **6. Staircase pattern** | `staircase.is_non_increasing` | `False` | Report `violations` (row indices and populated counts). Ask if a later origin period legitimately has more development than an earlier one. |
| **7. Numeric values** | `numeric_values.n_non_numeric_cells` | `> 0` | Show up to 20 `non_numeric_examples`. Ask user to fix or exclude those cells. |
| **8. Duplicate periods** | `duplicate_origin_periods` / `duplicate_dev_periods` | non-empty | Name the duplicates. Ask user whether to merge or drop. |

If any structural check fails, pause and resolve with the user before continuing.

#### 7c — Cross-triangle and anomaly checks (flag and let user decide)

| Check | Field | Applicable when | What to flag |
|---|---|---|---|
| **9. Consistent periods across triangles** | `period_alignment.origin_mismatches` / `period_alignment.dev_mismatches` | More than one triangle present | List any accident periods or development periods that appear in some triangles but not others. Ask the user whether the mismatch is expected (e.g. a newer triangle with an extra origin period) or a data error. **Resolve before running checks 10–11**, which assume all triangles share the same axes. |
| **10. Paid ≤ incurred** | `paid_vs_incurred.violations` | Both triangles present | List up to 20 `(origin period, dev column)` pairs where cumulative paid > incurred. |
| **11. Closed ≤ reported** | `closed_vs_reported.violations` | Both triangles present | Same pattern for counts. |
| **12. No negative cumulatives** | `no_negative_cumul.violations` | Always | List up to 20 `(origin, dev col, value)` triples. Ask if negative values are recoveries or data errors. |
| **13. Large incrementals** | `large_incrementals.violations` | Always | List `(origin, dev col, % change)` exceeding 200%. Ask if large swings are expected or errors. |

For each anomaly, ask:
> *"Would you like to exclude these rows/columns, leave them as-is, or fix them manually before continuing?"*

#### 7d — Summary confirmation

Once all anomalies are resolved, build and present summary statistics for each triangle:

```python
summary = build_summary_statistics(df, tab_name="Incurred", triangle_type="cumulative")
```

Present and ask for confirmation:

> "Here is a summary of your **{tab_name}** triangle ({triangle_type}). Please confirm before I proceed:
> - **{n_origin_periods}** origin periods: {origin_periods}
> - **{n_dev_periods}** development periods: {dev_periods}
> - Values: min={min}, max={max}, mean={mean}
> - **{pct_populated}%** of cells populated
> Does this look correct?"

---

## Data Format Reference

| Format       | Layout | Typical columns |
| ------------ | ------ | --------------- |
| **Loss Run** | Long — one row per claim per eval date | Claim No, Accident Date, Eval Date, Paid Loss, Incurred Loss, Status |
| **Triangle** | Wide — rows = origin periods, cols = dev periods | Org Pd 1…N as rows; Dev Pd 1…N as columns |
