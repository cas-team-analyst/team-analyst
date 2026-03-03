---
name: chain-ladder
description: Calculate historical and average LDFs, select age-to-age LDFs and tail factors, then apply cumulative development factors to project ultimate losses using the chain-ladder method. Requires the canonical data produced by extract-canonical and diagnostics from pre-ultimate-diagnostics.
---
# Chain Ladder Skill

This skill picks up from the outputs of the **extract-canonical** and **pre-ultimate-diagnostics** skills to perform LDF calculation, LDF selection, tail factor selection, and chain-ladder ultimate loss projection. All user interaction is handled by the agent following the instructions below.

**Prerequisites:**

- `{stem}-canonical.csv` — canonical triangle data for historical LDF calculation (from extract-canonical)
- `{stem}-pre-ultimate-diagnostics.csv` — diagnostic metrics (from pre-ultimate-diagnostics)

---

## Instructions

### Step 1 — Calculate Historical LDFs

For each available triangle (measure), compute historical link development factors (LDFs) for every (origin_period, development_age) age pair present in the canonical data.

A historical LDF for an (origin period, age) cell is:

```
LDF(origin_period, D) = value(origin_period, D_next) / value(origin_period, D)
```

where `D_next` is the next older development age in the sorted sequence. Only cells where both values are non-null and the denominator is non-zero are included.

#### Running the script

```python
from scripts.`1-historical-ldfs` import calculate_historical_ldfs

result = calculate_historical_ldfs(
    canonical_path="path/to/{stem}-canonical.csv",
)
```

**Output file:** `{stem}-ldfs.csv` saved alongside the canonical CSV.

| Column            | Description                                                        |
| ----------------- | ------------------------------------------------------------------ |
| `measure`       | Triangle / measure name (e.g.`paid_losses`, `incurred_losses`) |
| `origin_period` | Accident / origin period label                                     |
| `age_from`      | "From" age (younger)                                               |
| `age_to`        | "To" age (older / next)                                            |
| `value_from`    | Canonical value at `age_from`                                    |
| `value_to`      | Canonical value at `age_to`                                      |
| `ldf`           | `value_to / value_from`                                          |

Rows are sorted by `(measure, age_from, origin_period)`.

#### After calling the script

If `result.skipped_pairs` is non-empty, report the count of skipped cells grouped by reason (e.g. "zero denominator") and ask the user whether to review them before continuing.

Tell the user:

> "I've calculated historical LDFs for **{result.measures}** across **{len(result.development_age_pairs)}** development age interval(s) and saved the result to **{result.output_path}**. I'll use this file for all LDF averaging and selection steps."

Store `result.output_path` as the active LDF file path for subsequent steps.

---

### Step 2 — Calculate Average LDFs

Before calling the script, ask the user two questions **separately**, waiting for each answer before asking the next:

1. **Time periods** — which averaging windows would you like?

   > "Which time periods would you like to use for average LDF calculations? Available options: **3-year**, **4-year**, **5-year**, and/or **all-year**. You can select multiple."
   >
2. **Average types** — which types of averages would you like?

   > "Which types of averages would you like to compute? Available options: **straight** (simple mean), **olympic** (straight mean dropping the single highest and lowest), and/or **weighted** (volume-weighted mean). You can select multiple."
   >

The same period/type selections are applied to all available measures (triangles).

#### Running the script

```python
from scripts.`2-average-ldfs` import calculate_average_ldfs

result = calculate_average_ldfs(
    ldf_path="path/to/{stem}-ldfs.csv",   # result.output_path from Step 1
    periods=[3, 5, "all_year"],                      # from user — any subset of [3, 4, 5, "all_year"]
    avg_types=["straight", "weighted"],              # from user — any subset of ["straight", "olympic", "weighted"]
)
```

**Output file:** `{ldf_stem}-averages.csv` saved alongside the LDF CSV.

| Column          | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `measure`     | Triangle / measure name                                             |
| `age_from`    | "From" development age                                              |
| `age_to`      | "To" development age                                                |
| `period`      | Time-period window:`3_year`, `4_year`, `5_year`, `all_year` |
| `avg_type`    | Average type:`straight`, `olympic`, `weighted`                |
| `n_available` | Total LDF observations available for this interval                  |
| `n_requested` | Window size requested (null for `all_year`)                       |
| `n_used`      | Actual n used — capped at `n_available` when fewer obs exist     |
| `average_ldf` | Computed average (6 decimal places)                                 |

Rows are sorted by `(measure, age_from, period, avg_type)`.

**Automatic capping:** if the user selects, e.g., a 5-year average but a development interval has only 3 observations, the script uses those 3 observations rather than returning NaN. The `n_used` column records the actual count.

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g.:

> "Note: for the following intervals fewer observations were available than requested, so a shorter window was used: …"

Tell the user:

> "I've calculated **{result.avg_types_used}** averages for periods **{result.periods_used}** across all measures and saved the results to **{result.output_path}**."

Store `result.output_path` as the active averages file path for subsequent steps.

---

### Step 3 — Select Age-to-Age LDFs and Tail Factors

> **This step is performed entirely by the LLM and the user. No Python script is called.**

For each available triangle measure, select:

1. A **selected LDF** for every age-to-age interval (`age_from` → `age_to`)
2. A **tail factor** to apply beyond the last observed development age

#### Reference material

Before making selections, read:

- `references/LDF Selection Reference.pdf` — the authoritative guide for LDF selection methodology and criteria

Key inputs to inform selections:

- `{stem}-ldfs.csv` — historical LDFs per interval and origin period
- `{ldf_stem}-averages.csv` — straight, olympic, and weighted averages across time periods
- `{stem}-pre-ultimate-diagnostics.csv` — diagnostics such as `paid_to_incurred`, `closure_rate`, average case reserves, severity trends

#### Selection process (per measure)

For each measure and each age-to-age interval (`age_from` → `age_to`):

1. **Review the historical LDF column** from the Step 1 output — note the range, stability, and direction of individual LDFs across origin periods.
2. **Review the averages** from Step 2 — compare straight, olympic, and weighted averages across the available time periods (all-year, 3-year, 5-year, etc.).
3. **Review relevant diagnostics** from ldfs-diagnostics — use metrics such as:
   - `paid_to_incurred` — to judge how settled claims are; immature periods may warrant more conservative selections
   - `incremental_closure_rate` — high closure activity in recent periods may indicate a shift in development pattern
   - `incurred_severity_incr` / `paid_severity_incr` — unexpected severity spikes can signal outlier years to de-weight
   - `average_case_reserves` — significant changes may signal case reserving philosophy shifts
4. **Apply the guidance in the LDF Selection Reference** to pick the most appropriate average type and time period for each interval.
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

Save confirmed selections to **`{ldf_stem}-selections.json`** in the same directory as the original input file. The file structure is:

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

- `computed_ldfs` — a dictionary of computed average LDFs from the Step 2 output for that interval. Keys are `"{period}-{avg_type}"` (e.g. `"all_year-straight"`, `"3_year-weighted"`), matching the `period` and `avg_type` column values in the averages CSV. Only the period/type combinations calculated in Step 2 are included.
- `selected_ldf` — confirmed selection (float, 3 decimal places)
- `rationale` — brief free-text explanation of the selection basis

Store `{ldf_stem}-selections.json` path for use in subsequent projection steps.

---

### Step 4 — Project Chain Ladder Ultimates

#### Running the script

```python
from scripts.`3-cl-ultimates` import project_cl_ultimates

result = project_cl_ultimates(
    ldf_selections_path="path/to/{ldf_stem}-selections.json",       # from Step 1
    diagonal_path="path/to/{stem}-canonical-diagonal.csv",           # from extract-canonical Step 3
)
```

**Output file:** `chain-ladder-ultimates.csv` saved alongside `{ldf_stem}-selections.json`.

| Column            | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| `measure`       | Triangle / measure name                                       |
| `origin_period` | Accident / origin period label                                |
| `latest_age`    | Development age from the diagonal                             |
| `current_value` | Projected-from value (diagonal value for this measure)        |
| `cdf`           | Cumulative development factor from `latest_age` to ultimate |
| `ultimate`      | `current_value × cdf`                                      |

#### After calling the script

If `result.warnings` is non-empty, report them to the user — e.g. measures with no diagonal data, ages without a CDF, or missing paid/incurred companion values.

Tell the user:

> "I've projected ultimate losses for **{result.measures}** and saved the results to **{result.output_path}**."

Present results as a summary table per measure (origin periods as rows, columns: current_value, cdf, ultimate).

> **Hand off to the trend-selections skill**. Pass the paths to:
>
> - `{stem}-chain-ladder-ultimates.csv` — chain-ladder ultimates (Step 2 output)
> - `{stem}-canonical.csv` — canonical data (for exposure)
> - `{stem}-pre-ultimate-diagnostics.csv` — diagnostics (from pre-ultimate-diagnostics)
>
> The trend-selections skill will calculate and select trend factors, and produce `{stem}-trend-selections.json`.
