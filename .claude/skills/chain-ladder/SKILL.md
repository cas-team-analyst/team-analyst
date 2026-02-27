---
name: chain-ladder
description: Select age-to-age LDFs and tail factors from averages calculated by ldfs-diagnostics, then apply cumulative development factors to project ultimate losses using the chain-ladder method. Requires the output files produced by ldfs-diagnostics as inputs.
---
# Chain Ladder Skill

This skill picks up from the outputs of the **ldfs-diagnostics** skill and performs LDF selection, tail factor selection, and chain-ladder ultimate loss projection. All user interaction is handled by the agent following the instructions below.

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

> **Hand off to the trend-selections skill**. Pass the paths to:
> - `{stem}-chain-ladder-ultimates.csv` — chain-ladder ultimates (Step 2 output)
> - `{stem}-canonical.csv` — canonical data (for exposure)
> - `{stem}-canonical-diagnostics.csv` — diagnostics (from ldfs-diagnostics Step 3)
>
> The trend-selections skill will calculate and select trend factors, and produce `{stem}-trend-selections.json`.
