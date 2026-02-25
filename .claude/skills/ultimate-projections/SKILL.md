---
name: ultimate-projections
description: Select age-to-age LDFs and tail factors from averages calculated by ldfs-diagnostics, then apply development methods (chain-ladder, BF, etc.) to project ultimate losses. Requires the output files produced by ldfs-diagnostics as inputs.
---
# Ultimate Projections Skill

This skill picks up from the outputs of the **ldfs-diagnostics** skill and performs LDF selection, tail factor selection, and ultimate loss projection. All user interaction is handled by the agent following the instructions below.

**Prerequisites — files produced by ldfs-diagnostics:**
- `{stem}-canonical-ldfs.csv` — historical LDFs per interval and origin period (Step 1 output)
- `{stem}-canonical-ldfs-averages.csv` — computed averages by period and type (Step 2 output)
- `{stem}-canonical-diagnostics.csv` — diagnostic metrics (Step 3 output)

---

## Instructions

### Step 1 — Select Age-to-Age LDFs and Tail Factors

> **This step is performed entirely by the LLM and the user. No Python script is called.**

For each available triangle measure, select:
1. A **selected LDF** for every age-to-age interval (`age_from` → `age_to`)
2. A **tail factor** to apply beyond the last observed development age

#### Reference material

Before making selections, read:
- `assets/LDF and Method Selection Reference.pdf` (in the **ldfs-diagnostics** skill assets) — the authoritative guide for selection methodology and criteria

Key inputs to inform selections:
- `{stem}-canonical-ldfs.csv` — historical LDFs per interval and origin period
- `{stem}-canonical-ldfs-averages.csv` — straight, olympic, and weighted averages across time periods
- `{stem}-canonical-diagnostics.csv` — diagnostics such as `paid_to_incurred`, `closure_rate`, average case reserves, severity trends

#### Selection process (per measure)

For each measure and each age-to-age interval (`age_from` → `age_to`):

1. **Review the historical LDF column** from the ldfs-diagnostics Step 1 output — note the range, stability, and direction of individual LDFs across origin periods.
2. **Review the averages** from ldfs-diagnostics Step 2 — compare straight, olympic, and weighted averages across the available time periods (all-year, 3-year, 5-year, etc.).
3. **Review relevant diagnostics** from ldfs-diagnostics Step 3 — use metrics such as:
   - `paid_to_incurred` — to judge how settled claims are; immature periods may warrant more conservative selections
   - `incremental_closure_rate` — high closure activity in recent periods may indicate a shift in development pattern
   - `incurred_severity_incr` / `paid_severity_incr` — unexpected severity spikes can signal outlier years to de-weight
   - `average_case_reserves` — significant changes may signal case reserving philosophy shifts
4. **Apply the guidance in the LDF and Method Selection Reference** to pick the most appropriate average type and time period for each interval.
5. **Record the selected LDF** as a single value per interval per measure, along with a brief rationale.

For the **tail factor**:
- Default to `1.000` unless the triangle is clearly immature at the oldest observed age.
- Consult the Selection Reference for guidance on tail fitting approaches.

#### Output format

Present selections to the user in a table per measure, e.g.:

```
Measure: paid_losses

| age_from | age_to | selected_ldf | rationale                                      |
|----------|--------|-------------|------------------------------------------------|
| 12       | 24     | 1.312       | 3-yr weighted; stable pattern, high volume     |
| 24       | 36     | 1.087       | All-yr straight; no outliers, steady closure   |
| 36       | 48     | 1.031       | Olympic; one outlier dropped                   |
| 48       | 60     | 1.012       | All-yr straight; very stable                   |
| Tail     |        | 1.005       | Small residual based on benchmark              |
```

Ask the user to confirm or override any selections before proceeding to projection steps.

#### After selections are confirmed

Save confirmed selections to **`{stem}-ldf-selections.json`** in the same directory as the original input file. The file structure is:

```json
{
  "paid_losses": {
    "intervals": [
      {
        "age_from": "12",
        "age_to": "24",
        "computed_ldfs": {
          "all_year-straight": 1.312,
          "all_year-weighted": 1.308,
          "3_year-straight": 1.321,
          "3_year-weighted": 1.317
        },
        "selected_ldf": 1.312,
        "rationale": "3-yr weighted; stable pattern, high volume"
      },
      {
        "age_from": "24",
        "age_to": "36",
        "computed_ldfs": {
          "all_year-straight": 1.087,
          "all_year-weighted": 1.085,
          "3_year-straight": 1.088,
          "3_year-weighted": 1.084
        },
        "selected_ldf": 1.087,
        "rationale": "All-yr straight; no outliers, steady closure"
      }
    ],
    "tail": {
      "selected_ldf": 1.005,
      "rationale": "Small residual based on benchmark"
    }
  }
}
```

- `computed_ldfs` — a dictionary of computed average LDFs from the ldfs-diagnostics Step 2 output for that interval. Keys are `"{period}-{avg_type}"` (e.g. `"all_year-straight"`, `"3_year-weighted"`), matching the `period` and `avg_type` column values in the averages CSV. Only the period/type combinations calculated in ldfs-diagnostics Step 2 are included.
- `selected_ldf` — confirmed selection (float, 3 decimal places)
- `rationale` — brief free-text explanation of the selection basis

Store `{stem}-ldf-selections.json` path for use in subsequent projection steps.

---

### Step 2 — Project Chain Ladder Ultimates

#### Running the script

```python
from scripts.`1-cl-ultimates` import project_cl_ultimates

result = project_cl_ultimates(
    ldf_selections_path="path/to/{stem}-ldf-selections.json",       # from Step 1
    diagonal_path="path/to/{stem}-canonical-diagonal.csv",           # from extract-canonical Step 3
)
```

**Output file:** `{ldf_selections_stem}-ultimates.csv` saved alongside `ldf-selections.json`.

| Column | Description |
|---|---|
| `measure` | Triangle / measure name |
| `origin_period` | Accident / origin period label |
| `latest_age` | Development age from the diagonal |
| `current_value` | Projected-from value (diagonal value for this measure) |
| `cdf` | Cumulative development factor from `latest_age` to ultimate |
| `ultimate` | `current_value × cdf` |

#### After calling the script

If `result.warnings` is non-empty, report them to the user — e.g. measures with no diagonal data, ages without a CDF, or missing paid/incurred companion values.

Tell the user:
> "I've projected ultimate losses for **{result.measures}** and saved the results to **{result.output_path}**."

Present results as a summary table per measure (origin periods as rows, columns: current_value, cdf, ultimate).

### Step 3 — Calculate Trend Rates

Calculate trends for exposure and loss ratio if only loss measures are present (no counts). Calculate trends for exposure, severity, and frequency if count measures and loss measures are present. Trend factors will be selected in Step 4.

- If only loss measures are present (no counts), calculate **loss ratio** and **exposure** trends only.
- If count measures (reported counts and/or closed counts) are also present, calculate **exposure**, **severity**, and **frequency** trends.

#### User inputs

Ask the user three questions before running the script:

1. **Manual overrides** — ask if they would like to manually specify a trend factor for any component, skipping the fitted calculation:

   > "Would you like to manually set the trend factor for any of the following components, rather than fitting it from the data? If so, which one(s) and what value(s)? Components: **loss ratio** and **exposure** (if only loss measures are present); **exposure**, **severity** and **frequency** (if count measures and loss measures are present)."

   Record any manual entries and exclude those components from the script calculation.

2. **Measure basis** — ask which measures to use (only ask if multiple options are available in the canonical data):

   > "Which loss measure would you like to use for severity trends? Options: **incurred losses**, **paid losses**. (Default: incurred losses.)"

   > "Which count measure would you like to use for frequency trends and as the severity denominator? Note that the same selection will be used for both frequency trends and the severity denominator. Options: **reported counts**, **closed counts**. (Default: reported counts.)"

   Skip these questions if the corresponding measure type has only one option in the canonical data, or if all components were manually overridden.

3. **Time periods** — ask which rolling windows to use when fitting trend lines:

   > "Which time-period windows would you like to use for fitting trend lines? Available options: **3-year**, **4-year**, **5-year**, **all-year**. You can select multiple."

   Skip this question if all components were manually overridden.

#### Running the script

```python
from scripts.`3-calculate-trends` import calculate_trends

result = calculate_trends(
    ultimates_path="path/to/{stem}-ldf-selections-ultimates.csv",  # from Step 2
    canonical_path="path/to/{stem}-canonical.csv",                  # for exposure
    periods=[3, 5, "all_year"],                                     # from user — any subset of [3, 4, 5, "all_year"]
    loss_measure="incurred_losses",                                  # from user — "incurred_losses" or "paid_losses"
    count_measure="reported_counts",                                 # from user — "reported_counts" or "closed_counts"
)
```

**Output file:** `{stem}-trends.csv` saved alongside the ultimates CSV.

| Column | Description |
|---|---|
| `component` | `frequency`, `severity`, `loss_ratio`, or `exposure` |
| `period` | Time-period window: `3_year`, `4_year`, `5_year`, `all_year` |
| `n_available` | Total origin period observations available |
| `n_requested` | Window size requested (null for `all_year`) |
| `n_used` | Actual n used — capped at `n_available` when fewer obs exist |
| `annual_trend_factor` | Fitted annual trend rate as a factor (e.g. `1.05` for +5%) |
| `r_squared` | R² of the least-squares fit |

Rows are sorted by `(component, period)`.

**Trend series used per component:**
- **Frequency** — `{count_measure}_ultimate / exposure` per origin period (only if count measures present)
- **Severity** — `{loss_measure}_ultimate / {count_measure}_ultimate` per origin period (only if count measures present)
- **Loss ratio** — `{loss_measure}_ultimate / exposure` per origin period (fallback when count measures are absent)
- **Exposure** — read directly from `{stem}-canonical.csv` at the latest diagonal for each origin period

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g. components skipped due to missing measures, or windows capped due to limited data.

Tell the user:

> "I've fitted trend rates for **{result.components}** across periods **{result.periods_used}** and saved the results to **{result.output_path}**."

Present the results as a table per component (periods as rows, columns: `n_used`, `annual_trend_pct`, `r_squared`).

Store `result.output_path` for use in Step 4.

---

### Step 4 — Select Trend Factors

> **This step is performed entirely by the LLM and the user. No Python script is called.**

For each applicable component, review the fitted trend rates from Step 3 and select a single annual trend factor.

#### Reference material

Before making selections, read:
- `assets/Trending Procedures in Property_Casualty Insurance.pdf` (in the **ultimate-projections** skill assets) — the authoritative guide on trending methodology, data requirements, and selection criteria

Key inputs:
- `{stem}-trends.csv` — fitted trend rates from Step 3 per component and period
- `{stem}-canonical-diagnostics.csv` — from ldfs-diagnostics Step 3; review incremental severity and frequency metrics for outlier years or pattern shifts

#### Selection process (per component)

1. **Review the fitted rates** across all time-period windows.
2. **Review relevant diagnostics** — check for shifts (e.g. legislative change, mix change, large-loss distortion, exposure base change) that may warrant de-weighting older periods.
3. **Apply the guidance in the Trending Procedures reference** to select the most appropriate window and trend rate.
4. **Record the selected factor** as a single factor, along with a brief rationale.

For any component that the user manually overrode in Step 3, record that value directly without re-selection.

#### Output format

Present selections to the user in a single table:

```
| Component | Selected Factor | Basis                      | Rationale                                      |
|-----------|------------------|----------------------------|------------------------------------------------|
| Frequency | 0.980            | 3-yr fit (r²=0.85)         | Declining frequency, last 3 yrs; stable        |
| Severity  | 1.050            | 5-yr fit (r²=0.92)         | Consistent upward trend; no large-loss distort |
| Exposure  | 1.000            | Manual override            | Stable payroll base; no material trend evident |
```

Ask the user to confirm or override before recording.

#### After selections are confirmed

Save confirmed selections to **`{stem}-trend-selections.json`** alongside the other selection files:

```json
{
  "frequency": {
    "computed_factors": {
      "3_year": 0.98,
      "5_year": 0.982,
      "all_year": 0.985
    },
    "selected_factor": 0.980,
    "basis": "3-yr fit (r²=0.85)",
    "rationale": "Declining frequency, last 3 yrs; stable"
  },
  "severity": {
    "computed_factors": {
      "3_year": 1.050,
      "5_year": 1.048
    },
    "selected_factor": 1.050,
    "basis": "5-yr fit (r²=0.92)",
    "rationale": "Consistent upward trend; no large-loss distortion"
  },
  "exposure": {
    "computed_factors": null,
    "selected_factor": 1.000,
    "basis": "Manual override",
    "rationale": "Stable payroll base; no material trend evident"
  }
}
```

- `computed_factors` — dict of `"{period}": annual_trend_factor` from Step 3, or `null` if manually overridden
- `selected_factor` — `selected_annual_trend_factor` rounded to 3 decimal places
- `basis` — which fitted window was chosen, or `"Manual override"`
