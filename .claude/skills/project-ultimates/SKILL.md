    

    

---
name: Project Ultimates
description: reads ultimate projections from available reserving ultimate development methods, selects ultimate losses (and counts if count measures are available), and computes ultimate diagnostics
---
# Project Ultimates

This skill reads ultimate projections from available reserving ultimate development methods, selects ultimate losses (and counts if count measures are available), and computes ultimate diagnostics.

## Instructions

### Step 1 — Discover Available Method Ultimates

> **This step is performed entirely by the LLM. No Python script is called.**

Before selecting ultimate losses, determine which reserving methods have already been computed by reading their output files from disk.

#### Known output file patterns

Each reserving method skill writes one canonical ultimates file per run. Look for files matching the following name patterns in the directory where the user's data files reside (the same directory as `{stem}-canonical.csv`):

| Method               | File pattern                              | Produced by skill        |
| -------------------- | ----------------------------------------- | ------------------------ |
| Chain Ladder         | `{stem}-chain-ladder-ultimates.csv`     | `chain-ladder`         |
| Initial Expected     | `{stem}-initial-expected-ultimates.csv` | `initial-expected`     |
| Bornhuetter-Ferguson | `{stem}-bf-ultimates.csv`               | `bornhuetter-ferguson` |

#### Discovery process

1. **Ask the user** for the directory path where their reserving output files are located, if it is not already known from prior steps.
2. **List the files** in that directory.
3. **Identify which method files are present** by matching each filename against the patterns above, using the common `{stem}` prefix (e.g. `mydata` in `mydata-chain-ladder-ultimates.csv`).
4. **Read each identified file** to confirm it is non-empty and contains the expected columns (`measure`, `origin_period`, and an ultimate column — e.g. `ultimate`, `ie_ultimate`, or `bf_ultimate`).

#### After discovery

Report to the user which methods are available, for example:

> "I found ultimates from the following methods:
>
> - ✅ **Chain Ladder** — `{stem}-chain-ladder-ultimates.csv` (measures: paid_losses, incurred_losses)
> - ✅ **Initial Expected** — `{stem}-initial-expected-ultimates.csv` (measures: paid_losses, incurred_losses)
> - ✅ **Bornhuetter-Ferguson** — `{stem}-bf-ultimates.csv` (measures: paid_losses, incurred_losses)
> - ❌ **Initial Expected** — not found"

Note which **measures** (e.g. `paid_losses`, `incurred_losses`, `reported_counts`, `closed_counts`) are present across the discovered files — this determines which selections and diagnostics are possible in subsequent steps.

Store the discovered file paths and available measures for use in subsequent steps.

---

### Step 2 — Assemble Method Ultimates JSON

#### Running the script

```python
from scripts.`1-assemble-ultimates` import assemble_method_ultimates

result = assemble_method_ultimates(
    cl_ultimates_path="path/to/{stem}-chain-ladder-ultimates.csv",          # required (Step 1)
    ie_ultimates_path="path/to/{stem}-initial-expected-ultimates.csv",      # optional (Step 1)
    bf_ultimates_path="path/to/{stem}-bf-ultimates.csv",                    # optional (Step 1)
)
```

Pass only the file paths that were found in Step 1. Omit any optional arguments for methods that are not available.

**Output file:** `{stem}-method-ultimates.json` saved alongside the chain-ladder ultimates CSV.

#### Output JSON structure

```json
{
  "losses": {
    "paid_losses chain_ladder": {
      "file_path": "path/to/{stem}-chain-ladder-ultimates.csv",
      "origin_periods": {
        "AY 2019": {
          "current_value": 8450000.00,
          "ultimate":      9100000.00,
          "ibnr":          650000.00,
          "unpaid":        650000.00
        },
        "AY 2020": { "..." }
      }
    },
    "incurred_losses chain_ladder": { "..." },
    "paid_losses initial_expected": { "..." },
    "paid_losses bornhuetter_ferguson": { "..." }
  },
  "counts": {
    "reported_counts chain_ladder": { "..." },
    "closed_counts chain_ladder": { "..." }
  }
}
```

**Column definitions per origin period:**

| Field             | Description                                                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `current_value` | Latest diagonal value for this measure (paid, incurred, reported, or closed)                                                 |
| `ultimate`      | Projected ultimate for this method × measure                                                                                |
| `ibnr`          | `ultimate − incurred_losses` (or `− reported_counts` for count measures); `null` if incurred/reported is unavailable |
| `unpaid`        | `ultimate − paid_losses` (or `− closed_counts` for count measures); `null` if paid/closed is unavailable             |

**Notes:**

- The top-level keys `"losses"` and `"counts"` are only present when at least one measure of that type exists.
- Entry keys follow the pattern `"{measure}_{method}"`, e.g. `"paid_losses_chain_ladder"`, `"paid_losses_bornhuetter_ferguson"`.
- For `initial_expected` rows, `current_value` is sourced from the chain-ladder diagonal (same measure and origin period).
- All values are rounded to 2 decimal places.

#### After calling the script

If `result.warnings` is non-empty, report them concisely — e.g. missing companion diagonals for IBNR/unpaid, skipped measures, or missing files.

Tell the user:

> "I've assembled ultimates for **{n}** method × measure combinations and saved the results to **{result.output_path}**."

Present results as a summary table per category (losses / counts), with origin periods as rows and method × measure combinations as columns, showing the `ultimate` for each.

Store `result.output_path` for use in subsequent steps.

---

### Step 3 — Select Ultimate Losses and Counts

> **This step is performed entirely by the LLM and the user. No Python script is called.**

For each available category (`losses` and, if present, `counts`), select a final ultimate value for every origin period.

#### Reference material

Before making selections, read:

- `references/Method Selection Reference.pdf` — specifically the sections on selecting ultimate projections and weighing different methods (Chain Ladder, Bornhuetter-Ferguson, Expected Loss Ratio) at various stages of development.

Key inputs to inform selections:

- `{stem}-method-ultimates.json` — the structured JSON from Step 2 containing the projections, current values, IBNR, and unpaid for every method × measure combination.

#### Selection process

For each category (first losses, then counts if available), and for each origin period from oldest to newest:

1. **Review the available projections** for that origin period across all methods.
2. **Consider the maturity** of the origin period. The Selection Reference generally advises:
   - **Mature periods** (oldest years): Rely heavily on Chain Ladder (often Paid, sometimes Incurred) as claims are mostly settled.
   - **Intermediate periods**: Blend or use Bornhuetter-Ferguson (Paid or Incurred) to stabilize erratic Chain Ladder projections while still recognizing actual experience.
   - **Immature periods** (youngest years, e.g. current year): Lean toward Bornhuetter-Ferguson or Initial Expected methods, as the Chain Ladder leverage is too high and actual experience is sparse.
3. **Compare measure types** (e.g. Paid vs. Incurred). Large divergences between Paid and Incurred ultimates for the same method should be investigated or reconciled.
4. **Make a selection**: Choose a single ultimate value for the category/origin period. You may select exactly one of the computed methods, or optionally a weighted average (e.g., 50% Paid CL / 50% Incurred CL).
5. **Record a brief rationale** explaining why that method/value was chosen for that specific period (e.g., "Mature year; Paid CL selected as claims are 95% closed" or "Immature year; Incurred BF selected to stabilize high leverage factor").

#### Output format

Present proposed selections to the user in a table per category:

```
Category: losses

| Origin Period | Selected Ultimate | Basis                     | Rationale                                      |
|---------------|------------------|---------------------------|------------------------------------------------|
| AY 2018       | 8,050,000        | Paid CL                   | Highly mature; Paid and Incurred converge      |
| AY 2019       | 9,100,000        | Incurred CL               | Very mature, but Paid CL looks unusually low   |
| AY 2020       | 10,250,000       | Incurred BF               | Intermediate maturity; stabilizes CL jump      |
| AY 2021       | 11,800,000       | Initial Expected          | Very immature; actuals too sparse for CL/BF    |
```

Ask the user to confirm or override the selections for that category before proceeding to the next.

#### After selections are confirmed

Save all confirmed selections to **`{stem}-selected-ultimates.jso			n`** alongside the other output files.

JSON structure:

```json
{
  "losses": {
    "AY 2018": {
      "selected_ultimate": 8050000.0,
      "basis": "Paid CL",
      "rationale": "Highly mature; Paid and Incurred converge"
    },
    ...
  },
  "counts": {
    "AY 2018": {
      "selected_ultimate": 420.0,
      "basis": "Reported CL",
      "rationale": "Mature year, counts fully reported"
    },
    ...
  }
}
```

Store `{stem}-selected-ultimates.json` path for use in subsequent diagnostic steps.
