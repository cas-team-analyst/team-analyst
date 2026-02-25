---
name: ldfs-diagnostics
description: Calculate historical LDFs, average LDFs, and diagnostics from canonical triangle data produced by extract-canonical. Outputs are consumed by the ultimate-projections skill for LDF selection and ultimate loss projection.
---
# LDFs & Diagnostics Skill

This skill calculates historical link development factors (LDFs), LDF averages, and diagnostic metrics from a `{stem}-canonical.csv` file produced by the **extract-canonical** skill. All user interaction is handled by the agent following the instructions below; the Python scripts in `scripts/` are pure utility functions with no prompts.

The outputs of this skill feed directly into **ultimate-projections**, which uses them to select age-to-age LDFs and project ultimate losses.

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
from scripts.`1-calculate-ldfs` import calculate_historical_ldfs

result = calculate_historical_ldfs(
    canonical_path="path/to/{stem}-canonical.csv",
)
```

**Output file:** `{canonical_stem}-ldfs.csv` saved alongside the canonical CSV.

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
from scripts.`2-calculate-averages` import calculate_average_ldfs

result = calculate_average_ldfs(
    ldf_path="path/to/{stem}-canonical-ldfs.csv",   # result.output_path from Step 1
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

### Step 3 — Compute Diagnostics

Run all diagnostics defined in `assets/diagnostics-registry.yaml` that are supported by the available measures. Available measures are read automatically from the metadata JSON — no user input is required to determine which diagnostics to compute.

Only diagnostics whose required `inputs` are all present in `available_measures` are computed; the rest are silently skipped and returned in `result.skipped_diagnostics`.

#### Running the script

```python
from scripts.`3-diagnostics` import compute_diagnostics

result = compute_diagnostics(
    canonical_path="path/to/{stem}-canonical.csv",    # from extract-canonical Step 1
    metadata_path="path/to/{stem}-canonical-metadata.json",  # from extract-canonical Step 2
    # exposure={"2020": 1000, "2021": 1100, ...}  # optional; required for loss-rate/frequency diagnostics
)
```

**Output file:** `{canonical_stem}-diagnostics.csv` saved alongside the canonical CSV.

| Column             | Description                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `diagnostic_key` | Registry key, e.g.`paid_to_incurred`                                                                                      |
| `label`          | Human-readable label from registry, e.g.`"Paid / Incurred"`                                                               |
| `format`         | Display hint:`integer`, `percentage`, or `decimal`                                                                    |
| `origin_period`  | Accident / origin period label                                                                                              |
| `age_to`         | Development age label; the "to" bound for incremental diagnostics                                                           |
| `age_from`       | Predecessor development age — populated for incremental diagnostics, null for cumulative and for the first development age |
| `value`          | Computed value (`NaN` if inputs missing for that cell)                                                                    |

Rows are sorted by `(diagnostic_key, age_to, origin_period)`.

#### Exposure-based diagnostics

Diagnostics using the `safe_divide_exposure` recipe (e.g. `incurred_loss_rate`, `reported_frequency`) require an `exposure` argument — a dict or `pd.Series` mapping origin_period → exposure value. If exposure is not provided, these diagnostics are skipped. If the user has exposure data, ask them to supply it before calling the script.

#### After calling the script

If `result.skipped_diagnostics` is non-empty, report them grouped by reason:

> "The following diagnostics were skipped: **{label}** — {reason}. …"

Tell the user:

> "I've computed **{len(result.computed_diagnostics)}** diagnostic(s) — **{result.computed_diagnostics}** — and saved the results to **{result.output_path}**."

Store `result.output_path` as the active diagnostics file path for subsequent steps.

---

## Next Step

Once Steps 1–3 are complete, hand off to the **ultimate-projections** skill, passing the paths to:

- `{stem}-canonical-ldfs.csv`
- `{stem}-canonical-ldfs-averages.csv`
- `{stem}-canonical-diagnostics.csv`
