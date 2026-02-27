---
name: bornhuetter-ferguson
description: uses cumulative development factors from chain-ladder and initial expected ultimates from initial-expected to compute bornhuetter-ferguson ultimates
---
# Bornhuetter-Ferguson Skill

This skill computes Bornhuetter-Ferguson (BF) ultimates per origin period. It combines the cumulative development factors (CDFs) from the **chain-ladder** skill with the initial expected ultimates from the **initial-expected** skill.

**Prerequisites:**
- `{stem}-chain-ladder-ultimates.csv` — chain-ladder ultimates including CDF and current diagonal values (from chain-ladder)
- `{stem}-initial-expected-ultimates.csv` — initial expected ultimates per origin period (from initial-expected)

---

## Instructions

### Step 1 — Compute Bornhuetter-Ferguson Ultimates

#### Running the script

```python
from scripts.`1-bf-ultimates` import compute_bf_ultimates

result = compute_bf_ultimates(
    cl_ultimates_path="path/to/{stem}-chain-ladder-ultimates.csv",       # from chain-ladder Step 1
    ie_ultimates_path="path/to/{stem}-initial-expected-ultimates.csv",   # from initial-expected Step 5
)
```

**Output file:** `{stem}-bf-ultimates.csv` saved alongside the chain-ladder ultimates CSV.

| Column | Description |
|---|---|
| `measure` | Triangle / measure name (e.g. `paid_losses`, `incurred_losses`, `reported_counts`, `closed_counts`) |
| `origin_period` | Accident / origin period label |
| `ie_ultimate` | Initial expected ultimate for this measure / origin period (from initial-expected) |
| `current_value` | Latest diagonal value for this measure / origin period (from chain-ladder) |
| `cdf` | Cumulative development factor to ultimate (from chain-ladder) |
| `percent_undeveloped` | `1 - 1/cdf` — the undeveloped weight applied to the IE ultimate |
| `bf_ultimate` | Computed BF ultimate: `ie_ultimate × (1 - 1/cdf) + current_value` |

Rows are sorted by measure (preserving the order from the chain-ladder file), then chronologically by origin period within each measure.

**Measure-to-IE-type mapping:**
- `paid_losses`, `incurred_losses` → uses the `loss_ratio` IE measure type
- `reported_counts`, `closed_counts` → uses the `frequency` IE measure type

Only measures present in both the chain-ladder ultimates and the initial-expected ultimates are included in the output. Measures with no matching IE type are skipped with a warning.

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g. missing IE ultimates for specific origin periods, invalid CDFs, or unrecognized measure names.

Tell the user:
> "I've computed Bornhuetter-Ferguson ultimates for **{result.measures}** and saved the results to **{result.output_path}**."

Present the results as a table per measure (origin periods as rows, columns: `current_value`, `cdf`, `percent_undeveloped`, `ie_ultimate`, `bf_ultimate`).
