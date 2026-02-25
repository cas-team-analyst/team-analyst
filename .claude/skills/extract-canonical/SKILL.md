---
name: extract-canonical
description: convert validated data to canonical long format, store metadata, and perform basic ldf and diagnostic calculations
---
# Extract Canonical Skill

This skill provides a standardized approach to converting validated actuarial data into canonical long format, storing metadata, and performing basic LDF and diagnostic calculations. All user interaction is handled by the agent following the instructions below; the Python scripts in `assets/` are pure utility functions with no prompts.

## Instructions

### Step 1 — Extract Canonical Format

Run the appropriate substep based on the data format confirmed in validate-data Step 2. Both produce an identical four-column CSV:

| Column | Description |
|---|---|
| `origin_period` | Accident / origin period label |
| `development_age` | Development period / evaluation date label |
| `measure` | `paid_losses`, `incurred_losses`, `reported_counts`, `closed_counts` |
| `value` | Numeric value (unpopulated cells excluded; loss run cells are summed across claims) |

---

#### 1a — Triangle

*Run when the user confirmed **triangle** format in validate-data Step 2.*

Use the **original input file** if cumulative, or the **`-cumulative` file** from validate-data Step 6 if incremental.

```python
from assets.`1a-extract-triangle` import extract_canonical_from_triangles

# resolved_tabs: measure → tab mapping confirmed in validate-data Step 7a
result = extract_canonical_from_triangles(
    file_path="path/to/triangles-cumulative.xlsx",
    resolved_tabs={"incurred_losses": "Incurred", "paid_losses": "Paid"},
)
```

---

#### 1b — Loss Run

*Run when the user confirmed **loss run** format in validate-data Step 2.*

Use the column mapping resolved during validate-data Step 5 (`results.measure_columns.resolved`, `results.origin_period.selected_column`, `results.eval_date.selected_column`).

```python
from assets.`1b-extract-loss-run` import extract_canonical_from_loss_run

# origin_col / eval_col / resolved_columns: resolved during validate-data Step 5
result = extract_canonical_from_loss_run(
    df=df,
    origin_col="Accident_Year",
    eval_col="Eval_Date",
    resolved_columns={"paid_losses": "Paid_Loss", "incurred_losses": "Incurred_Loss"},
    source_file_path="path/to/lossrun.xlsx",
)
```

---

#### After either substep

The output CSV is saved alongside the source file with `-canonical` appended to the stem (e.g. `triangles-cumulative.xlsx` → `triangles-canonical.csv`).

If `result.failed_measures` is non-empty, report each failure and ask the user whether to fix the source data or skip that measure.

Tell the user:
> "I've extracted your data into canonical long format and saved the result to **{result.output_path}**. I'll use this file for all remaining analysis steps."

Store `result.output_path` as the active canonical file path for subsequent steps.

---

### Step 2 — Store Metadata

Before calling the script, gather the following from the user — ask each question separately, waiting for the answer before proceeding to the next, in this order:

1. **Valuation date** — the as-of date the data was extracted (e.g. "2024-12-31")
2. **Line of business** — e.g. "Workers Compensation", "General Liability", "Auto Liability"
3. **Specific coverage** *(if applicable)* — e.g. "Medical Only", "Excess", or "N/A" if not applicable
4. **Loss currency** — e.g. "USD", "GBP", "EUR"

Once you have the user's answers, call `store_metadata()`:

```python
from assets.`2-store-metadata` import store_metadata

result = store_metadata(
    canonical_path=canonical_path,          # result.output_path from Step 1
    loss_currency="USD",                    # from user
    valuation_date="2024-12-31",            # from user
    line_of_business="Workers Compensation",# from user
    data_source_format="triangle",          # "triangle" or "loss_run" — known from Step 1
    specific_coverage="Medical Only",       # from user; None if not applicable
    notes=None,                             # optional free text
)
```

The metadata JSON is saved alongside the canonical CSV with `-metadata` appended to the stem:
> e.g. `triangles-canonical.csv` → `triangles-canonical-metadata.json`

**Valuation date check:** If `result.valuation_date_check["consistent"]` is `False`, surface the message to the user and ask them to confirm or correct the valuation date before proceeding.

**Metadata fields stored:**

| Field | Source | Description |
|---|---|---|
| `loss_currency` | user | ISO 4217 code or free text |
| `valuation_date` | user | As-of date for the data |
| `line_of_business` | user | Line of business |
| `specific_coverage` | user | Sub-coverage, or null |
| `data_source_format` | agent | `"triangle"` or `"loss_run"` |
| `notes` | user | Optional free text |
| `origin_period_start` | data | Earliest origin period label |
| `origin_period_end` | data | Latest origin period label |
| `origin_period_count` | data | Number of distinct origin periods |
| `origin_period_interval` | data | Inferred interval: `annual`, `quarterly`, `semi-annual`, `biennial`, `irregular`, etc. |
| `origin_periods` | data | Full sorted list of origin period labels |
| `development_age_start` | data | Earliest development age label |
| `development_age_end` | data | Latest development age label |
| `development_age_count` | data | Number of distinct development ages |
| `development_age_interval` | data | Inferred interval between dev ages: `annual`, `quarterly`, etc. |
| `development_ages` | data | Full sorted list of development age labels |
| `available_measures` | data | List of measure keys present in the canonical file |
| `total_populated_cells` | data | Total non-null rows in the canonical CSV |
| `per_measure_stats` | data | `{count, min, max, mean, total}` per measure |
| `valuation_date_check` | data | `{consistent, expected, message}` — validates supplied date against `Dec 31 of oldest AY + max_dev_age months` |
| `source_canonical_path` | data | Absolute path to the canonical CSV |
| `created_at` | data | ISO 8601 UTC timestamp of metadata creation |

Store `result.output_path` as the active metadata path for subsequent steps.

---

### Step 3 — Extract Diagonal

Extract the latest diagonal from the canonical CSV: for each `(origin_period, measure)` pair, keep only the row whose `development_age` is the most mature (maximum). This is the starting point for all loss development projections.

```python
from assets.`3-extract-diagonal` import extract_diagonal

result = extract_diagonal(
    canonical_path=canonical_path,   # result.output_path from Step 1
)
```

**Output file:** `{canonical_stem}-diagonal.csv` saved alongside the canonical CSV.

**Output columns** (same schema as the canonical CSV, one row per origin period per measure):

| Column | Description |
|---|---|
| `origin_period` | Accident/origin period label |
| `development_age` | Most mature development age for that origin period |
| `measure` | Measure name (e.g. `paid`, `incurred`) |
| `value` | Value at the most mature development age |

Rows are sorted by `(measure, origin_period)` ascending.

**After calling the script**, confirm to the user:
> "I've extracted the latest diagonal for **{result.measures}** and saved it to **{result.output_path}**."

Store `result.output_path` as the active diagonal path for subsequent steps.
