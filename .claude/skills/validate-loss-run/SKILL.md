---
name: validate-loss-run
description:
  Third step of the actuarial reserving pipeline; validates the loss run data. Use when the master PROGRESS.md shows Step 2 "identify-format" complete, data format from step 2 "identify-format" is "loss run" in master PROGRESS.md, and Step 3 "validate-data" is pending.
---

### Sub-step 1. Identify Available Data Elements

**Scan for measures first, then confirm with the user.**

Call `identify_loss_run_fields()` with the confirmed format and file path:

```python
from scripts.`1-identify-loss-run-fields` import identify_loss_run_fields

loss_run_fields = identify_loss_run_fields(sheets)
```

`loss_run_fields.column_matches` shows which columns matched each measure.
Present the mapping:

> I found the following fields based on column names:
>
> - **claim ID** → `{loss_run_fields.column_matches["claim_id"]}`
> - **accident date** → `{loss_run_fields.column_matches["accident_date"]}`
> - **closed date** → `{loss_run_fields.column_matches["closed_date"]}`
> - **origin period** → `{loss_run_fields.column_matches["origin_period"]}`
> - **eval date** → `{loss_run_fields.column_matches["eval_date"]}`
> - **dev age** → `{loss_run_fields.column_matches["dev_age"]}`
> - **incurred losses** → `{loss_run_fields.column_matches["incurred_losses"]}`
> - **paid losses** → `{loss_run_fields.column_matches["paid_losses"]}`
> - **case reserve** → `{loss_run_fields.column_matches["case_reserve"]}`
> - **reported count** → `{loss_run_fields.column_matches["reported_count"]}`
> - **closed count** → `{loss_run_fields.column_matches["closed_count"]}`
> - **open count** → `{loss_run_fields.column_matches["open_count"]}`
> - **claim status** → `{loss_run_fields.column_matches["claim_status"]}`

- **If the user confirms** the column matches → record the mapping as the working column mapping for later steps; do not proceed to Sub-step 2 until the user has explicitly confirmed (e.g. "yes", "looks good", "confirmed").
- **If the user does not confirm** → ask the user to correct the column matches (e.g. which column to use for a measure, or to name a column not matched). Record each correction in the working column mapping (measure key → chosen column name).

---

### Sub-step 2. Identify Empty Fields

**"Identify" here means:** the user provides the column name to use for that measure (or chooses from the list of sheet columns). Record each choice in the working column mapping (measure key → column name).

- **If claim ID has no matches (empty)** → tell the user they must provide the claim ID column before proceeding. Ask the user to choose from the sheet columns (loss_run_fields.columns) for **claim ID**. Record the chosen column in the working mapping.
- **If every field in the set has no matches (all empty)** for any of the following sets → tell the user they must identify at least one field in the set before proceeding. Ask the user to choose from the sheet columns (loss_run_fields.columns) for at least one field in that set, one set at a time:
  - (**accident date**, **origin period**)
  - (**eval date**, **dev age**)
  - (**incurred losses**, **paid losses**, **reported count**, **closed count**)

---

### Sub-step 3. Identify Ambiguous Fields

Only apply this sub-step when a field has **more than one** matching column. Ask one field at a time (or one set of fields at a time); record each user choice in the working column mapping.

**Fields that allow "sum all matches" or "select one match":** If any of these have more than one match, tell the user they must indicate whether to "sum all matches" or "select one match" for that field. Then ask the user how to handle each such field, one field at a time:
- **incurred losses**
- **paid losses**
- **case reserve**

**Fields that require "select one match":** If any of these have more than one match, tell the user they must select one of the matches. Ask the user which match they want to use, one field at a time:
- **claim ID**
- **origin period**
- **eval date**
- **dev age**
- **reported count**
- **closed count**
- **open count**
- **claim status**

Record each user choice in the working mapping.

---

### Sub-step 4. Identify Potentially Conflicting Fields

Only apply each bullet when **every field in that set has at least one match (all non-empty)**. Record the user's choices in the working column mapping; drop the non-selected measures from the mapping for downstream use.

**Single-choice sets (user picks exactly one field from each set):** If the set is all non-empty, tell the user they must select one field to use from that set. Ask which single field they want to use:
- (**accident date**, **origin period**)
- (**eval date**, **dev age**)
- (**closed date**, **claim status**, **closed count**)

**Two-choice sets (user picks exactly two fields from each set):** If the set is all non-empty, tell the user they must select two fields to use from that set. Ask which two fields they want to use:
- (**incurred losses**, **paid losses**, **case reserve**)
- (**reported count**, **closed count**, **open count**)

Record each user choice in the working mapping.

---

### Sub-step 2. Validate Loss Run

```python
from scripts.`4a-validate-loss-run` import validate_loss_run, build_summary_statistics

results = validate_loss_run(df, selected_measures=confirmed_measures)
```

#### 5a — Structural checks (resolve before continuing)

| Check | Field | Failure condition | Action |
|---|---|---|---|
| **1. Claim ID** | `results.claim_id.found` | `False` | List all columns; ask user to identify claim ID column. |
| **2. Origin period** | `results.origin_period.found` | `False` | Ask user to identify origin period column. |
| **3. Origin format** | `results.origin_format.is_consistent` | `False` | Show `detected_formats` and `unrecognised_values`; ask about mixed formats. |
| **4. Measure columns** | `results.measure_columns.missing` | Non-empty | Name missing measures; ask user to map columns. |
| | `results.measure_columns.ambiguous` | Non-empty dict | Show candidates; ask user to confirm. |
| **5. Numeric measures** | `results.numeric_measures.is_convertible` | Any `False` | Show up to 5 `problem_values`; ask to exclude or fix. |
| **6. Eval date** | `results.eval_date.found` | `False` | Ask user to identify evaluation date column. |
| **7. Duplicates** | `results.duplicates.duplicate_count` | > 0 | Show up to 10 examples; ask to deduplicate or investigate. |

#### 5b — Isolated anomalies (flag and let user decide)

Inspect `results.isolated_issues` and flag:
- **Fully-null measure rows**: list indices, ask whether to exclude.
- **High-null columns**: name column and null %; ask if expected.
- **Negative values**: name columns and rows; ask if valid (recoveries) or errors.
- **Incurred < paid**: list rows; ask if legitimate (salvage/subrogation) or data error.

#### 5c — Summary confirmation

```python
summary = build_summary_statistics(
    df,
    claim_col=results.claim_id.selected_column,
    origin_col=results.origin_period.selected_column,
    eval_col=results.eval_date.selected_column,
    resolved_columns=results.measure_columns.resolved,
)
```

Present total rows, unique claims, origin periods, eval dates, and per-measure min/max/mean/% null. Ask for confirmation before closing.
--
