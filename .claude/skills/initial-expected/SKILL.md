---
name: initial-expected
description: Calculate ultimates using the initial expected method, relying on chain ladder ultimates from chain-ladder and selected trends from trend-selections.
---
# Initial Expected Skill

This skill computes initial expected loss ratios and (optionally) frequencies per origin period, then derives averages across rolling time windows. It follows the **trend-selections** skill in the reserving workflow.

**Prerequisites:**
- `{stem}-chain-ladder-ultimates.csv` — chain-ladder ultimates (from chain-ladder)
- `{stem}-canonical.csv` — canonical long-format data, for exposure (from extract-canonical)
- `{stem}-trend-selections.json` — selected annual trend factors (from trend-selections)

---

## Instructions

### Step 1 — Select Periods, Average Types, and Measure Weights

> **This step is performed entirely by the LLM and the user. No Python script is called.**

Before calculating initial expected values, ask the user which periods and average types to use as the basis for those calculations, and how to weight multiple chain-ladder ultimates where more than one is available.

Ask the user **two questions**, separately, waiting for each answer before asking the next:

1. **Time periods** — which averaging windows to use:

   > "Which time periods would you like to use when calculating initial expected loss ratio options? Available options: **3-year**, **4-year**, **5-year**, and/or **all-year**. You can select multiple."

2. **Average types** — which types of averages to use:

   > "Which average types would you like to use? Available options: **straight** (simple mean), **olympic** (straight mean dropping the single highest and lowest), and/or **weighted** (volume-weighted mean). You can select multiple."

If both **paid losses** and **incurred losses** chain ladder ultimates are available, also ask:

3. **Loss measure weighting** — how to blend the two ultimates for the ELR calculation:

   > "For the initial expected loss ratio calculation, how would you like to weight the paid loss chain ladder ultimate vs. the incurred loss chain ladder ultimate? Enter a weight for paid (e.g. 0.50 for 50/50, 0.00 for incurred only, 1.00 for paid only)."

   If only one loss measure is available, default to 100% weight on that measure (no question needed).

If count measures (reported counts and/or closed counts) are present in the data, also ask:

4. **Frequency — time periods and average types** — use the same options, but ask separately for the frequency selection:

   > "The same period and average-type choices will also be used for initial expected **frequency** options. Would you like to use the same selections as above for frequency, or different ones?"

   If the user wants different selections for frequency, ask questions 1 and 2 again specifically for frequency.

If both **reported counts** and **closed counts** chain ladder ultimates are available, also ask:

5. **Count measure weighting** — how to blend the two count ultimates for the frequency calculation:

   > "For the initial expected frequency calculation, how would you like to weight the reported counts chain ladder ultimate vs. the closed counts chain ladder ultimate? Enter a weight for reported counts (e.g. 0.50 for 50/50, 0.00 for closed only, 1.00 for reported only)."

   If only one count measure is available, default to 100% weight on that measure (no question needed).

#### Storing the selections

Record the resulting selections as:

```
elr_periods:        [e.g. "3_year", "5_year", "all_year"]
elr_avg_types:      [e.g. "straight", "weighted"]
elr_paid_weight:    0.50   # weight on paid loss CL ultimate; 1 - elr_paid_weight = incurred weight
                           # defaults to 1.0 (paid only) or 0.0 (incurred only) when only one is available
freq_periods:       [e.g. "all_year"]          # only if count measures are present
freq_avg_types:     [e.g. "straight", "olympic", "weighted"]  # only if count measures are present
freq_rptd_weight:   0.50   # weight on reported counts CL ultimate; 1 - freq_rptd_weight = closed weight
                           # defaults to 1.0 (reported only) or 0.0 (closed only) when only one is available
                           # only if count measures are present
```

---

### Step 2 — Compute Initial Expected Values Per Origin Period

#### Running the script

```python
from scripts.`1-initial-expected` import compute_initial_expected

result = compute_initial_expected(
    ultimates_path="path/to/{stem}-chain-ladder-ultimates.csv",  # from ultimate-projections Step 2
    trend_selections_path="path/to/{stem}-trend-selections.json",  # from trend-selections Step 2
    canonical_path="path/to/{stem}-canonical.csv",                  # for exposure
    elr_paid_weight=0.50,      # from Step 1 — weight on paid loss CL ultimate (omit if only one loss measure)
    freq_rptd_weight=0.50,     # from Step 1 — weight on reported counts CL ultimate (omit if only one count measure or no counts)
)
```

**Output file:** `{stem}-initial-expected.csv` saved alongside the ultimates CSV.

| Column | Description |
|---|---|
| `measure_type` | `"loss_ratio"` or `"frequency"` |
| `origin_period` | Accident / origin period label |
| `blended_ult` | Weighted average of CL ultimates (loss measures for loss_ratio rows; count measures for frequency rows) |
| `exposure` | Exposure for this origin period (from canonical diagonal) |
| `trend_step` | Number of years from this origin period to the most recent one (most recent = 0) |
| `severity_trend` | Compounded severity annual factor ^ `trend_step` (loss_ratio rows; null for frequency rows; 1.0 when no count measures present) |
| `frequency_trend` | Compounded frequency (or loss_ratio) annual factor ^ `trend_step` |
| `exposure_trend` | Compounded exposure annual factor ^ `trend_step` |
| `initial_value` | Computed initial ELR or initial frequency |

Rows are sorted by `(measure_type, origin_period)` — all loss_ratio rows first, then frequency rows.

**Trend compounding:** each annual trend factor is raised to the power of `trend_step`, where `trend_step = n_origin_periods − 1 − rank` (rank 0 = most recent). For example, with an annual severity trend of 1.05: most recent period → 1.05⁰ = 1.0000; one year older → 1.05¹ = 1.0500; two years older → 1.05² = 1.1025.

**Formulas applied:**
- **Initial ELR:** `blended_ult × severity_trend × frequency_trend / (exposure × exposure_trend)`
- **Initial frequency:** `blended_ult × frequency_trend / (exposure × exposure_trend)`

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g. measures not found in ultimates, missing exposure for specific periods, or defaulted trend factors.

Tell the user:
> "I've computed initial expected **{result.measure_types}** for all origin periods and saved the results to **{result.output_path}**."

Present the results as a table per measure type (origin periods as rows, columns: `blended_ult`, `initial_value`).

Store `result.output_path` for use in Step 3.

---

### Step 3 — Calculate Initial Expected Averages

#### Running the script

```python
from scripts.`2-initial-expected-averages` import compute_initial_expected_averages

result = compute_initial_expected_averages(
    initial_expected_path="path/to/{stem}-initial-expected.csv",   # from Step 2
    elr_periods=["3_year", "all_year"],                            # from Step 1 user selections
    elr_avg_types=["straight", "weighted"],                        # from Step 1 user selections
    freq_periods=["all_year"],          # from Step 1 user selections — only if frequency rows present
    freq_avg_types=["straight", "weighted"],  # from Step 1 user selections — only if frequency rows present
)
```

**Output file:** `{stem}-initial-expected-averages.csv` saved alongside the initial-expected CSV.

| Column | Description |
|---|---|
| `measure_type` | `"loss_ratio"` or `"frequency"` |
| `period` | Rolling window: `3_year`, `4_year`, `5_year`, `all_year` |
| `avg_type` | Average type: `straight`, `olympic`, `weighted` |
| `n_available` | Total origin period observations available |
| `n_requested` | Window size requested (null for `all_year`) |
| `n_used` | Actual n used — capped at `n_available` when fewer obs exist |
| `average` | Computed average initial expected value (6 decimal places) |

Rows are sorted by `(measure_type, period, avg_type)` — all loss_ratio rows first, then frequency rows.

**Average types:**
- **Straight** — simple arithmetic mean of the most recent N `initial_value`s
- **Olympic** — straight mean after dropping the single highest and single lowest value (requires ≥ 3 obs; falls back to straight if fewer)
- **Weighted** — exposure-weighted mean: `Σ(initial_value × exposure) / Σ(exposure)` for the selected origin periods

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g. olympic fallbacks due to insufficient observations, or missing measure types.

Tell the user:
> "I've calculated **{result.measure_types}** initial expected averages and saved the results to **{result.output_path}**."

Present the results as a table per measure type (rows: `period × avg_type`, column: `average`).

Store `result.output_path` for use in Step 4.

---

### Step 4 — Select Initial Expected Values

> **This step is performed entirely by the LLM and the user. No Python script is called.**

For each applicable measure type (`loss_ratio` and/or `frequency`), review the computed averages from Step 3 and select a single initial expected value.

#### Selection process (per measure type)

1. **Review the computed averages** across all period × average-type combinations from Step 3.
2. **Identify any outlier or anomalous averages** — consider whether very old or very recent periods produce systematically high or low values that may distort the selection.
3. **Select the most appropriate average** as the initial expected value, along with a brief rationale explaining the chosen period and average type.

Present proposed selections to the user in a table per measure type:

```
Measure type: loss_ratio

| Period    | Avg Type | n_used | Average  |
|-----------|----------|--------|----------|
| 3_year    | straight | 3      | 0.623400 |
| 3_year    | weighted | 3      | 0.618200 |
| all_year  | straight | 7      | 0.641000 |
| all_year  | weighted | 7      | 0.635500 |

→ Selected: 0.6234  (3-year straight; recent periods reflect current conditions)
```

Ask the user to confirm or override each selection before recording.

#### After selections are confirmed

Save confirmed selections to **`{stem}-initial-expected-selections.json`** alongside the other output files:

```json
{
  "loss_ratio": {
    "computed_averages": {
      "3_year-straight": 0.623400,
      "3_year-weighted": 0.618200,
      "all_year-straight": 0.641000,
      "all_year-weighted": 0.635500
    },
    "selected_average": 0.6234,
    "basis": "3-year straight",
    "rationale": "Recent periods reflect current conditions; stable loss experience"
  },
  "frequency": {
    "computed_averages": {
      "all_year-straight": 0.042100,
      "all_year-weighted": 0.041800
    },
    "selected_average": 0.0421,
    "basis": "all-year straight",
    "rationale": "Sufficient history available; no material trend in frequency"
  }
}
```

- `computed_averages` — dict of `"{period}-{avg_type}": average` from Step 3. Only include the period/type combinations calculated for this measure type.
- `selected_average` — confirmed selection (float, 4 decimal places)
- `basis` — which period and average type was selected (e.g. `"3-year straight"`, `"all-year weighted"`)
- `rationale` — brief free-text explanation of the selection basis

Omit the `"frequency"` key entirely if no frequency rows were computed in Step 2.

Store `{stem}-initial-expected-selections.json` path for use in Step 5.

---

### Step 5 — Compute Initial Expected Ultimates

#### Running the script

```python
from scripts.`3-initial-expected-ultimates` import compute_ie_ultimates

result = compute_ie_ultimates(
    initial_expected_path="path/to/{stem}-initial-expected.csv",          # from Step 2
    ie_selections_path="path/to/{stem}-initial-expected-selections.json", # from Step 4
)
```

**Output file:** `{stem}-initial-expected-ultimates.csv` saved alongside the initial-expected CSV.

| Column | Description |
|---|---|
| `measure_type` | `"loss_ratio"` or `"frequency"` |
| `origin_period` | Accident / origin period label |
| `selected_ie_value` | Selected initial expected ELR or frequency from Step 4 |
| `exposure` | Exposure for this origin period (from Step 2) |
| `severity_trend` | Compounded severity factor for this period (loss_ratio rows; null for frequency rows; 1.0 when no counts present) |
| `frequency_trend` | Compounded frequency (or loss_ratio) factor for this period |
| `exposure_trend` | Compounded exposure factor for this period |
| `ie_ultimate` | Computed initial expected ultimate (losses or counts) |

Rows are sorted by `(measure_type, origin_period)` — all loss_ratio rows first, then frequency rows.

**Formulas applied:**

When count measures are present:
- **IE loss ultimate:** `selected_elr × exposure × exposure_trend / (severity_trend × frequency_trend)`
- **IE count ultimate:** `selected_frequency × exposure × exposure_trend / frequency_trend`

When count measures are not present:
- **IE loss ultimate:** `selected_elr × exposure × exposure_trend / frequency_trend`
  *(the `frequency_trend` column holds the compounded loss_ratio trend in this case)*

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g. missing trend factors, zero denominators, or skipped origin periods.

Tell the user:
> "I've computed initial expected ultimates for **{result.measure_types}** and saved the results to **{result.output_path}**."

Present the results as a table per measure type (origin periods as rows, columns: `selected_ie_value`, `exposure`, `ie_ultimate`).

Store `result.output_path` for use in subsequent reserving steps (e.g. Bornhuetter-Ferguson).
