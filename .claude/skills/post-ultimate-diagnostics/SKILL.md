---
name: pre-ultimate-diagnostics
description: Calculate pre-ultimate diagnostics from canonical triangle data produced by extract-canonical. Outputs are consumed by downstream modeling skills.
---
# Pre-Ultimate Diagnostics Skill

This skill calculates diagnostic metrics from a `{stem}-canonical.csv` file produced by the **extract-canonical** skill. All user interaction is handled by the agent following the instructions below; the Python scripts in `scripts/` are pure utility functions with no prompts.

The output feeds into downstream modeling skills, such as **chain-ladder** or **ultimate-projections**.

---

## Instructions

### Step 1 — Compute Diagnostics

Run all diagnostics defined in `assets/pre-ultimate-diagnostics-registry.yaml` that are supported by the available measures. Available measures are read automatically from the metadata JSON — no user input is required to determine which diagnostics to compute.

Only diagnostics whose required `inputs` are all present in `available_measures` are computed; the rest are silently skipped and returned in `result.skipped_diagnostics`.

#### Running the script

```python
from scripts.`1-pre-ultimate-diagnostics` import compute_diagnostics

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

Once diagnostics are complete, hand off to the next appropriate skill (e.g. **chain-ladder**), passing the path to:

- `{stem}-pre-ultimate-diagnostics.csv`
