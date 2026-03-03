---
name: trend-selections
description: Calculate and select trends to be used for initial expected methods. Requires chain-ladder ultimates produced by the chain-ladder skill as inputs.
---
# Trend Selections Skill

This skill fits annual trend lines for frequency, severity, loss ratio, and exposure from chain-ladder ultimates, then guides the LLM and user through selecting a single annual trend factor per component. The outputs then feed into **initial-expected** for the initial expected loss ratio and frequency calculations.

**Prerequisites — files produced by extract-canonical:**
- `{stem}-canonical.csv` — canonical long-format data (for exposure)

**Prerequisites — files produced by ldfs-diagnostics:**
- `{stem}-canonical-diagnostics.csv` — diagnostic metrics from ldfs-diagnostics (for selection review)

**Prerequisites — files produced by chain-ladder:**
- `{stem}-chain-ladder-ultimates.csv` — chain-ladder ultimate losses per measure and origin period

---

## Instructions

### Step 1 — Calculate Trend Rates

Calculate trends for exposure and loss ratio if only loss measures are present (no counts). Calculate trends for exposure, severity, and frequency if count measures and loss measures are present. Trend factors will be selected in Step 2.

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
from scripts.`1-calculate-trends` import calculate_trends

result = calculate_trends(
    ultimates_path="path/to/{stem}-chain-ladder-ultimates.csv",  # from ultimate-projections Step 2
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

Present the results as a table per component (periods as rows, columns: `n_used`, `annual_trend_factor`, `r_squared`).

Store `result.output_path` for use in Step 2.

---

### Step 2 — Select Trend Factors

> **This step is performed entirely by the LLM and the user. No Python script is called.**

For each applicable component, review the fitted trend rates from Step 1 and select a single annual trend factor.

#### Reference material

Before making selections, read:
- `assets/Trending Procedures in Property_Casualty Insurance.pdf` — the authoritative guide on trending methodology, data requirements, and selection criteria

Key inputs:
- `{stem}-trends.csv` — fitted trend rates from Step 1 per component and period
- `{stem}-canonical-diagnostics.csv` — from ldfs-diagnostics; review incremental severity and frequency metrics for outlier years or pattern shifts

#### Selection process (per component)

1. **Review the fitted rates** across all time-period windows.
2. **Review relevant diagnostics** — check for shifts (e.g. legislative change, mix change, large-loss distortion, exposure base change) that may warrant de-weighting older periods.
3. **Apply the guidance in the Trending Procedures reference** to select the most appropriate window and trend rate.
4. **Record the selected factor** as a single factor, along with a brief rationale.

For any component that the user manually overrode in Step 1, record that value directly without re-selection.

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

- `computed_factors` — dict of `"{period}": annual_trend_factor` from Step 1, or `null` if manually overridden
- `selected_factor` — `selected_annual_trend_factor` rounded to 3 decimal places
- `basis` — which fitted window was chosen, or `"Manual override"`

> **Hand off to the initial-expected skill** after completing Step 2. Pass the paths to:
> - `{stem}-chain-ladder-ultimates.csv` — chain-ladder ultimates (from ultimate-projections Step 2)
> - `{stem}-canonical.csv` — canonical data (for exposure)
> - `{stem}-trend-selections.json` — selected trend factors (Step 2 output)
>
> The initial-expected skill will compute per-period initial expected values and averages, producing `{stem}-initial-expected.csv` and `{stem}-initial-expected-averages.csv`.

