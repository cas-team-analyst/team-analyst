# Codebase Summary: Actuarial Loss Reserving Pipeline

## What This Is

A 7-step Python pipeline for actuarial loss reserve analysis. Given historical loss development triangles and expected loss inputs, it estimates ultimate losses and IBNR (Incurred But Not Reported) reserves using three actuarial methods: Chain Ladder (CL), Initial Expected (IE), and Bornhuetter-Ferguson (BF).

The pipeline is a **human-in-the-loop system**: steps 1–3 and 6–7 are fully automatic, while steps 4–5 require selections from either an agent (CL LDF selection) or the user (IE expected inputs).

---

## Pipeline Steps and Data Flow

```
data/canonical-triangles.xlsx
data/canonical-elrs.xlsx
         │
         ▼
[Step 1] 1-normalize.py          → output/prep/triangles.pkl
                                   output/data-processing/long.xlsx
                                   output/data-processing/triangles.xlsx
                                   output/data-processing/pre-method-triangle-diagnostics.xlsx
         │
         ▼
[Step 2] 2-extract-diagonal.py   → output/prep/diagonal.pkl
                                   output/prep/age_map.csv
         │
         ▼
[Step 3] 3-compute-ldfs.py       → output/prep/ldf_averages.csv
                                   output/prep/ldf_triangle.csv
         │
         ▼
[AGENT SELECTS CL LDFs]          → output/selections/cl_selections.json
         │
         ▼
[Step 4] 4-apply-cl-selections.py → output/chain-ladder/chain-ladder.xlsx
                                    output/chain-ladder/cl_cdfs.csv
                                    output/chain-ladder/cl_ultimates.csv
         │
         ▼
[USER PROVIDES IE INPUTS]         → data/canonical-elrs.xlsx (pre-loaded)
         │
         ▼
[Step 5] 5-apply-ie.py           → output/initial-expected/initial-expected.xlsx
                                   output/initial-expected/ie_ultimates.csv
         │
         ▼
[Step 6] 6-apply-bf.py           → output/bornhuetter-ferguson/bornhuetter-ferguson.xlsx
                                   output/bornhuetter-ferguson/bf_ultimates.csv
         │
         ▼
[Step 7] 7-combine-ultimates.py  → output/selected-ultimates/selected-ultimates.xlsx
                                   output/post-method/post-method-series-diagnostics.xlsx
                                   output/post-method/post-method-triangle-diagnostics.xlsx
                                   output/full-analysis.xlsx
```

---

## Step-by-Step Detail

### Step 1 — Normalize (`1-normalize.py`)

**Purpose:** Read raw wide-format triangle files and convert to a canonical long format.

**Input:**
- `data/canonical-triangles.xlsx` — one sheet per measure:
  - `Incurred` → Incurred Loss (dollars)
  - `Paid` → Paid Loss (dollars)
  - `Reported` → Reported Count (claims)
  - `Closed` → Closed Count (claims)
  - `Exposure` → Exposure (count)
- Rows = accident periods, columns = development ages (e.g. 12, 24, 36 … months)
- Configured via the `SOURCES` list at the top of the script

**Output (internal):**
- `output/prep/triangles.pkl` — long-format DataFrame (used by all downstream scripts)
- `output/prep/triangles.csv` — same, in CSV

**Output (Excel):**
- `output/data-processing/long.xlsx` — columns: Accident Period, Development Age, Measure, Value
- `output/data-processing/triangles.xlsx` — wide format, one sheet per measure
- `output/data-processing/pre-method-triangle-diagnostics.xlsx` — 11 diagnostic ratio triangles:
  - Incurred Severity, Incurred Loss Rate
  - Paid Severity, Paid Loss Rate, Paid-to-Incurred
  - Case Reserves
  - Reported Frequency, Closed Frequency, Closed-to-Reported
  - Open Counts, Average Open Case Reserve

**Selections made:** None (pure data transformation)

---

### Step 2 — Extract Diagonal (`2-extract-diagonal.py`)

**Purpose:** Extract the most recent (rightmost) observation per accident period per measure — the "latest diagonal" that is the starting point for all projections.

**Input:**
- `output/prep/triangles.pkl`

**Output:**
- `output/prep/diagonal.pkl` — one row per (period × measure): period, age, value, age_rank
- `output/prep/diagonal.csv`
- `output/prep/age_map.csv` — ordered list of age intervals (age, next_age, interval, age_index)

**Selections made:** None (deterministic — takes max age per group)

---

### Step 3 — Compute LDFs (`3-compute-ldfs.py`)

**Purpose:** Compute age-to-age development factors (LDFs) for every period × interval and summarize with statistical averages. This is the input the agent uses to make CL selections.

**Input:**
- `output/prep/triangles.pkl`

**Output:**
- `output/prep/ldf_triangle.csv` — per-period LDF for every interval (used to inspect individual factors)
- `output/prep/ldf_averages.csv` — summary statistics per (measure × interval):
  - `weighted_all`, `simple_all`, `excl_hi_lo_all` — full-history averages
  - `weighted_3yr`, `simple_3yr`, `excl_hi_lo_3yr` — 3-year averages
  - `weighted_5yr`, `simple_5yr`, `excl_hi_lo_5yr` — 5-year averages
  - `cv_3yr`, `cv_5yr` — coefficient of variation (volatility measure)
  - `slope_3yr`, `slope_5yr` — linear trend in recent LDFs (positive = rising)

**Selections made:** None (pure computation)

---

### Step 4 — Apply CL Selections (`4-apply-cl-selections.py`)

**Purpose:** Convert selected LDFs into CDFs and project ultimates for each accident period.

**Input:**
- `output/prep/triangles.pkl`
- `output/prep/diagonal.pkl`
- `output/selections/cl_selections.json` — **written by agent before this step runs**

**Formulas:**
```
CDF@tail   = selected tail LDF (the seed of the chain)
CDF@age    = selected LDF(age→next) × CDF@next  (built backward from tail)
CL Ultimate = Actual diagonal × CDF@current_age
IBNR        = Ultimate − Actual
Unpaid      = Ultimate − Paid diagonal (for loss measures)
           = Ultimate − Closed diagonal (for count measures)
```

**Tail factor:** The tail is an agent selection like any other interval. It is written to `cl_selections.json` as `"interval": "tail"` and is the starting point for the backward CDF chain — every interval's CDF is multiplied by it. The code defaults to `1.000` if the key is absent. Guidance: inspect the oldest interval's observed LDF to judge whether additional development beyond the triangle is expected.

**Output:**
- `output/chain-ladder/chain-ladder.xlsx` — one sheet per measure: Accident Period, Current Age, Actual, CDF, Ultimate, IBNR, Unpaid
- `output/chain-ladder/cl_cdfs.csv` — internal: CDF and % developed per (measure × age)
- `output/chain-ladder/cl_ultimates.csv` — internal: projected ultimates
- `output/inputs/cl_selections.json` — copy of agent selections for reference

---

### Step 5 — Apply Initial Expected (`5-apply-ie.py`)

**Purpose:** Compute expected ultimates from ELR × Exposure and Expected Frequency × Exposure.

**Input:**
- `output/prep/diagonal.pkl`
- `output/chain-ladder/cl_ultimates.csv`
- `data/canonical-elrs.xlsx` (sheet "ELR") — columns:
  - Accident Period
  - Expected Loss Ratio (e.g., 0.75 = 75% of exposure)
  - Expected Frequency (e.g., 1.35 claims per exposure unit)

**Formulas:**
```
IE Loss Ultimate  = Expected Loss Ratio × Exposure
IE Count Ultimate = Expected Frequency × Exposure
IBNR              = IE Ultimate − Actual
Unpaid            = IE Ultimate − Paid diagonal
```

**Output:**
- `output/initial-expected/initial-expected.xlsx` — two sheets:
  - **Loss**: Accident Period, Current Age, Exposure, Selected Loss Rate, Selected Loss
  - **Counts**: Accident Period, Current Age, Exposure, Selected Frequency, Selected Counts
- `output/initial-expected/ie_ultimates.csv` — internal: ultimates for all 4 measures per period
- `output/inputs/ie_inputs.json` — copy of computed IE inputs for reference

**Selections made:** None (script reads ELR file directly; the "selection" is what values are in the ELR file)

---

### Step 6 — Apply BF (`6-apply-bf.py`)

**Purpose:** Blend CL and IE using the BF credibility formula. Fully automatic.

**Input:**
- `output/prep/diagonal.pkl`
- `output/chain-ladder/cl_cdfs.csv` — provides % developed per (measure × age)
- `output/initial-expected/ie_ultimates.csv` — provides expected ultimates

**Formula:**
```
% developed   = 1 / CDF
% unreported  = 1 − % developed
BF Ultimate   = Actual + (1 − % developed) × IE Expected
IBNR          = (1 − % developed) × IE Expected
Unpaid        = BF Ultimate − Paid diagonal
```

BF naturally blends toward IE for immature periods (low % developed) and toward CL for mature periods (high % developed).

**Output:**
- `output/bornhuetter-ferguson/bornhuetter-ferguson.xlsx` — four sheets (Incurred, Paid, Reported, Closed): Accident Period, Current Age, Initial Expected, CDF, % Unreported/Unpaid, $ Unreported/Unpaid, Actual, Ultimate, IBNR, Unpaid
- `output/bornhuetter-ferguson/bf_ultimates.csv` — internal

**Selections made:** None (deterministic formula)

---

### Step 7 — Combine Ultimates (`7-combine-ultimates.py`)

**Purpose:** Merge CL, IE, and BF results into side-by-side comparison tables, compute post-method diagnostics, and build the master workbook.

**Input:**
- `output/prep/triangles.pkl`
- `output/prep/diagonal.pkl`
- `output/chain-ladder/cl_ultimates.csv`
- `output/initial-expected/ie_ultimates.csv`
- `output/bornhuetter-ferguson/bf_ultimates.csv`

**Default selection logic:** BF is selected as the default; falls back to CL, then IE if BF is unavailable.

**Output:**
- `output/selected-ultimates/selected-ultimates.xlsx` — two sheets (Loss, Counts) with columns: Accident Period, Current Age, Actual measures, CL/BF/IE ultimates, Selected Ultimate, IBNR, Unpaid
- `output/post-method/post-method-series-diagnostics.xlsx` — Ultimate Severity, Ultimate Loss Rate, Ultimate Frequency per accident period
- `output/post-method/post-method-triangle-diagnostics.xlsx` — X-to-Ultimate ratio triangles (Incurred, Paid, Reported, Closed) + Average IBNR and Average Unpaid triangles
- `output/full-analysis.xlsx` — all sheets from all output files combined into one master workbook

**Selections made:** Default = BF; user can override in `selected-ultimates.xlsx`

---

## Where Selections Are Made

| Step | Who Selects | What Is Selected | Format |
|------|-------------|------------------|--------|
| Step 4 (CL) | **Agent** | One LDF per (measure × interval) + one tail per measure | `output/selections/cl_selections.json` |
| Step 5 (IE) | **User / data file** | Expected Loss Ratio and Expected Frequency per accident period | `data/canonical-elrs.xlsx` |
| Step 7 (Final) | **Default = BF** (user can override) | Selected ultimate per period | `output/selected-ultimates/selected-ultimates.xlsx` |

---

## CL LDF Selection Criteria (Step 4 — Agent Decision)

The agent reads `ldf_averages.csv` and applies 8 criteria holistically:

1. **Outlier handling** — use `excl_hi_lo_*` when variability is high (high CV)
2. **Recency preference** — prefer 5-year and 3-year; use shorter windows when a clear trend exists
3. **Asymmetric conservatism** — slower to follow drops (>10% threshold), quicker to follow increases (>5% threshold)
4. **Bayesian anchoring** — anchor to prior selected LDF; blend explicitly when signals conflict
5. **Latest-point outlier exception** — if latest factor differs >15% from recent history, treat as outlier and rely on averages instead
6. **Trending** — if 3–4 consecutive factors move in one direction, begin moving the selection that way
7. **Sparse data** — fewer than ~50 claims/year or <$1M incurred/year → prefer longer-term averages
8. **Convergence override** — if 3yr, 5yr, and all-history align tightly and differ from prior → override the prior

Each selection is recorded with a `reasoning` field explaining which criteria drove the choice.

---

## Data Structures

### Long-format triangle (canonical internal format)
| Column | Type | Description |
|--------|------|-------------|
| period | ordered category | Accident period (e.g. 2015, 2016) |
| age | ordered category | Development age in months (e.g. 12, 24, 36) |
| measure | category | Incurred Loss, Paid Loss, Reported Count, Closed Count, Exposure |
| value | float | The observation |

### CL Selections JSON
```json
[
  {
    "measure": "Incurred Loss",
    "interval": "12-24",
    "selected_ldf": 1.8093,
    "reasoning": "Weighted 3-year average selected; low CV (0.012) indicates stable development."
  },
  {
    "measure": "Incurred Loss",
    "interval": "tail",
    "selected_ldf": 1.0000,
    "reasoning": "Oldest interval LDF is 1.005; tail set to 1.000 assuming no further development."
  }
]
```

### ELR File (IE inputs)
Sheet "ELR" with columns: Accident Period, Expected Loss Ratio, Expected Frequency

---

## Supporting Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Top-level pipeline reference: steps, output structure, troubleshooting |
| `methods/chain-ladder/METHOD.md` | Detailed CL selection criteria and reasoning guidance |
| `methods/initial-expected/METHOD.md` | IE input format and output description |
| `methods/bornhuetter-ferguson/METHOD.md` | BF formula and output explanation |
| `references/method-reference.md` | Conceptual definitions: LDF, CDF, % developed, tail; method comparison table |
| `canonical-data/` | Reference outputs for validating the pipeline against known-good results |
