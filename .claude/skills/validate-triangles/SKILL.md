---
name: validate-triangles
description:
  Third step of the actuarial reserving pipeline; validates the triangles data. Use when the master PROGRESS.md shows Step 2 "identify-format" complete, data format from step 2 "identify-format" is "triangle" in master PROGRESS.md, and Step 3 "validate-data" is pending.
---

### Sub-step 1. Select Triangles to Use

**Read from identify-format output, then confirm with the user.**

If there are multiple triangle tabs for a measure, present the list of triangle tabs for that measure and ask the user which to use:

> I found the following triangle tabs for {measure}:
>
> - **{tab_check_results.tabs_matching_triangle.{measure}}**
>
> Which triangle tab do you want to use for {measure}?

Only allow the user to select one triangle tab for each measure.

If there is only one triangle tab for a measure, use that tab automatically.

Store the triangle tab mapping in a dictionary called `selected_triangles`.

```python
selected_triangles = {
    "incurred_losses": {selected_incurred_losses_tab},
    "paid_losses": {selected_paid_losses_tab},
    "reported_counts": {selected_reported_counts_tab},
    "closed_counts": {selected_closed_counts_tab},
}
```

### Sub-step 2. Identify Triangle Format for Each Measure

Call `identify_triangle_format()` with the selected triangles:

```python
from scripts.`1-identify-triangle-format` import identify_triangle_format

triangle_formats = identify_triangle_format(sheets, selected_triangles)
```

Present the triangle format results to the user:
```python
for measure, triangle_format in triangle_formats.items():
    print(f"{measure}: {triangle_format.tab_name} has {triangle_format.negative_count} negative values and {triangle_format.pct_non_decreasing:.2%} of values are non-decreasing")
```

**Run detection first, then confirm with the user.**

Load the first available triangle tab and call `detect_triangle_type()`:

```python
import pandas as pd
from scripts.`4b1-convert-to-cumulative` import detect_triangle_type

# Load any one triangle tab to sample the data
sample_df = pd.read_excel("path/to/triangles.xlsx", sheet_name=0)
guess, confidence = detect_triangle_type(sample_df)
```

Present the guess:

> "I believe your triangles are **{cumulative / incremental}** ({confidence} confidence) — values {are / are not} consistently non-decreasing across development periods.
>
> Does that look right?"

- If the user confirms **cumulative** → skip conversion, proceed to Sub-step 7 using the original file.
- If the user confirms **incremental** (or corrects to incremental) → run conversion:

```python
from scripts.`4b1-convert-to-cumulative` import convert_to_cumulative

result = convert_to_cumulative(
    file_path="path/to/triangles.xlsx",
    resolved_tabs={"incurred_losses": "Incurred", "paid_losses": "Paid"},
)
```

Output saved with `-cumulative` appended (e.g. `triangles-cumulative.xlsx`). Report any `result.failed_tabs` and ask the user whether to fix the source data or skip that measure. Store `result.output_path` as the active file path for Sub-step 7.

---

### Sub-step 7. Validate Triangles

*Triangle format only. Use the cumulative file (original or converted).*

```python
from scripts.`4b2-validate-triangle` import validate_all_triangles, build_summary_statistics

tab_findings, results = validate_all_triangles(
    file_path="path/to/triangles-cumulative.xlsx",
    selected_measures=confirmed_measures,
    triangle_type="cumulative",
    resolved_tabs={"incurred_losses": "Incurred", "paid_losses": "Paid"},
)
```

#### 7a — Tab mapping

| Field | Failure | Action |
|---|---|---|
| `tab_findings.missing` | Non-empty | List tab names; ask user to identify correct one. |
| `tab_findings.ambiguous` | Non-empty | Show candidates; ask user to select. |

#### 7b — Structural checks per triangle (resolve before continuing)

| Check | Field | Failure | Action |
|---|---|---|---|
| **1. Origin column** | `origin_period_col.found_exactly_one` | `False` | Show `matched_columns`; ask user to identify. |
| **2. Dev period row** | `dev_period_row.header_appears_valid` | `False` | Ask user to confirm header row. |
| **3. Origin format** | `origin_format.is_consistent` | `False` | Show formats and unrecognised values. |
| **4. Top-left nulls** | `top_left_nulls.has_unexpected_nulls` | `True` | Show up to 10 cells; ask: interpolate by origin, by dev, or ignore. |
| **5. Period intervals** | `period_intervals.*_is_regular` | `False` | Show irregular intervals; ask if expected. |
| **6. Staircase** | `staircase.is_non_increasing` | `False` | Report violations; ask if later AY legitimately has more dev. |
| **7. Numeric values** | `numeric_values.n_non_numeric_cells` | > 0 | Show up to 20 examples; ask to fix or exclude. |
| **8. Duplicate periods** | `duplicate_origin/dev_periods` | Non-empty | Ask to merge or drop. |

#### 7c — Cross-triangle and anomaly checks

| Check | Field | Applicable when | Action |
|---|---|---|---|
| **9. Consistent periods** | `period_alignment.*_mismatches` | > 1 triangle | List mismatches; ask if expected or data error. Resolve before 10–11. |
| **10. Paid ≤ incurred** | `paid_vs_incurred.violations` | Both present | List up to 20 (origin, dev col) pairs where paid > incurred. |
| **11. Closed ≤ reported** | `closed_vs_reported.violations` | Both present | Same pattern for counts. |
| **12. No negative cumulatives** | `no_negative_cumul.violations` | Always | List triples; ask if recoveries or errors. |
| **13. Large incrementals** | `large_incrementals.violations` | Always | List (origin, dev col, % change) > 200%; ask if expected. |

#### 7d — Summary confirmation

```python
summary = build_summary_statistics(df, tab_name="Incurred", triangle_type="cumulative")
```

Present origin periods, dev periods, min/max/mean, % populated per triangle. Ask for confirmation before closing.

---

### Sub-step 8. Close Skill

Fill in all output fields in PROGRESS.md, then copy the completed **Master Closing Block** into the master `.claude/PROGRESS.md` → Step 2 Summary and mark Step 2 `[x]` in the master pipeline.