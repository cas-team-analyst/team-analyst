## Data Validation — Please Review

I've processed your raw data into the canonical triangle format. Please
confirm the summary below looks correct before I continue.

### 1. Measures Loaded

| Measure | # Records | AY Range | Dev Ages (months) | Min Value | Max Value |
|---|---|---|---|---|---|
| [measure 1] | [n] | [YYYY–YYYY] | [min–max] | [min] | [max] |
| ... | | | | | |

**Total records:** [N] across [K] measures.

### 2. Sample Rows

First 3 and last 3 rows of the processed triangle table (all measures combined):

| measure | accident_year | dev_age | value |
|---|---|---|---|
| ... | ... | ... | ... |

### 3. Spot-Check: One Full Triangle

Showing [Paid Loss] (cumulative) as a sanity check on shape and magnitude:

| AY \ Dev | 12 | 24 | 36 | ... | [ultimate age] |
|---|---|---|---|---|---|
| 2015 | ... | ... | ... | ... | ... |
| 2016 | ... | ... | ... | ... | |
| ... | | | | | |

### 4. Adjustments Made to `1a-prep-data.py`

- [Bullet each customization — column renames, source-specific parsing, outlier handling, etc.]
- If no changes were made, say: "No adjustments required — data matched the expected format."

### 5. Confirmation Needed

Please reply with one of:
- **"Looks good"** — I'll continue to LDF averages and diagnostics.
- **"Fix <issue>"** — describe what's wrong and I'll address it before moving on.
