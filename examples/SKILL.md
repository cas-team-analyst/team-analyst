---
name: actuarial-reserving
description: >
  Full actuarial loss reserving pipeline skill. Use when user asks
  to estimate unpaid loss reserves, IBNR, or ultimate losses from a triangle
  dataset. Covers chain-ladder (CL), initial-expected (IE), and
  Bornhuetter-Ferguson (BF) methods. Supports dollar losses and claim counts.
  Triggers on: loss reserving, IBNR, chain ladder, Bornhuetter-Ferguson,
  initial expected, unpaid losses, reserve analysis, development factors.
---

# Actuarial Loss Reserving Skill

## Overview

This skill runs a complete actuarial reserving pipeline using three methods:
- **Chain Ladder (CL)** — age-to-age development with agent-selected LDFs
- **Initial Expected (IE)** — user-provided expected ultimates
- **Bornhuetter-Ferguson (BF)** — credibility blend of CL and IE (fully automatic)

## Output Structure

All outputs are written to `output/` with this folder structure:

```
output/
  data-processing/
    long.xlsx                              ← long-format triangle (Accident Period, Dev Age, Measure, Value)
    triangles.xlsx                         ← wide-format, one sheet per measure
    pre-method-triangle-diagnostics.xlsx   ← severity, loss rate, frequency, case reserve ratios
  chain-ladder/
    chain-ladder.xlsx                      ← CL results (one sheet per measure)
    cl_cdfs.csv                            ← internal: CDFs and % developed
    cl_ultimates.csv                       ← internal: CL ultimates
  initial-expected/
    initial-expected.xlsx                  ← IE results (Loss + Counts sheets)
    ie_ultimates.csv                       ← internal
  bornhuetter-ferguson/
    bornhuetter-ferguson.xlsx              ← BF results (Incurred, Paid, Reported, Closed)
    bf_ultimates.csv                       ← internal
  post-method/
    post-method-series-diagnostics.xlsx    ← ultimate severity, loss rate, frequency
    post-method-triangle-diagnostics.xlsx  ← X-to-ultimate triangles + avg IBNR/Unpaid
  selected-ultimates/
    selected-ultimates.xlsx                ← CL/IE/BF side-by-side with selected (Loss + Counts)
  inputs/
    cl_selections.json                     ← copy of agent CL selections
    ie_inputs.json                         ← copy of IE inputs
  full-analysis.xlsx                       ← all sheets combined in one workbook
```

## Pipeline Steps

### Steps 1–3: Data Preparation (run once per project)

**Step 1 — Normalize triangles**
```bash
python scripts/1-normalize.py
```
- Reads wide-format Excel/CSV input triangles
- Writes `output/data-processing/long.xlsx`, `triangles.xlsx`, `pre-method-triangle-diagnostics.xlsx`
- Writes `output/prep/triangles.pkl` (internal, used by all downstream scripts)
- Configure the `SOURCES` list at the top of the script for your data file

**Step 2 — Extract diagonal**
```bash
python scripts/2-extract-diagonal.py
```
- Extracts the most recent observation per accident period
- Writes `output/prep/diagonal.pkl` and `age_map.csv`

**Step 3 — Compute LDFs**
```bash
python scripts/3-compute-ldfs.py
```
- Computes age-to-age factors and statistical averages
- Writes `output/prep/ldf_averages.csv` — the agent reads this to make CL selections

---

### Step 4: Chain Ladder — LDF Selection (agent makes selections)

Read `output/prep/ldf_averages.csv`. Columns:
- `measure` — triangle measure (e.g. "Incurred Loss", "Paid Loss")
- `interval` — development interval (e.g. "12-24", "96-108")
- `weighted_all`, `simple_all`, `excl_hi_lo_all` — full-history averages
- `weighted_3yr`, `simple_3yr`, `excl_hi_lo_3yr` — recent 3-year averages
- `weighted_5yr`, `simple_5yr`, `excl_hi_lo_5yr` — recent 5-year averages
- `cv_3yr`, `cv_5yr` — coefficient of variation (stability measure)
- `slope_3yr`, `slope_5yr` — trend in recent LDFs (positive = rising)

Chain-ladder LDF selection follows an **eight-criteria** methodology (plus **tail**). Criteria are weighed **together** with judgment; full rules, numeric thresholds, prior-anchor sourcing, volume-weighting cautions, and `reasoning` guidance are in [methods/chain-ladder/METHOD.md](methods/chain-ladder/METHOD.md).

**The eight criteria (summary):**  
(1) **Outlier handling** — use `excl_hi_lo_*` when variability is high.  
(2) **Recency preference** — favor 5-year and 3-year over all-history alone in large triangles; shorter windows when a clear trend appears.  
(3) **Asymmetric conservatism** — slower to follow down moves, quicker to follow up moves (see METHOD for % thresholds).  
(4) **Bayesian anchoring to prior** — anchor to prior selected LDF; blend with explicit weights when helpful.  
(5) **Latest-point outlier exception** — if the latest factor is extreme vs the last 5–10 points (see METHOD), do not overweight it; lean on averages and prior.  
(6) **Trending** — gradual moves toward a sustained 3–4 point direction; distinguish trend from one-off noise.  
(7) **Sparse data** — prefer longer averages (5-year, all-history) when volume is thin (see METHOD for claim/$ heuristics).  
(8) **Convergence override** — when 3-year, 5-year, and all-history align tightly and differ materially from prior, override the prior.

Prep outputs **3-year, 5-year, and all-history** averages only (no 7-year column); use `output/prep/ldf_triangle.csv` for per-period factors when comparing the latest diagonal to history or applying criteria 5–6.

Write selections to `output/selections/cl_selections.json`:
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

Required fields: `measure`, `interval`, `selected_ldf`, `reasoning`
- Include one entry per (measure × interval) — don't skip any intervals
- Include one `"tail"` entry per measure
- Measure names must match exactly as they appear in `ldf_averages.csv`

Then run:
```bash
python scripts/4-apply-cl-selections.py
```
Output: `output/chain-ladder/chain-ladder.xlsx`

---

### Step 5: Initial Expected — User Provides Inputs

Help the user provide expected ultimate inputs and write them to
`output/selections/ie_inputs.json`. Then run script 5 — no actuarial selections required.

**Style A — Direct expected ultimate:**
```json
[
  {"period": "2015", "measure": "Incurred Loss",   "expected_ultimate": 47483901.76},
  {"period": "2015", "measure": "Paid Loss",        "expected_ultimate": 47708943.93},
  {"period": "2015", "measure": "Reported Count",   "expected_ultimate": 4930},
  {"period": "2015", "measure": "Closed Count",     "expected_ultimate": 5029.62}
]
```

**Style B — Expected loss ratio x premium:**
```json
[
  {"period": "2015", "measure": "Incurred Loss", "elr": 0.72, "premium": 65955419.11}
]
```

Then run:
```bash
python scripts/5-apply-ie.py
```
Output: `output/initial-expected/initial-expected.xlsx`

---

### Steps 6–7: Bornhuetter-Ferguson + Final Outputs (fully automatic)

**Prerequisites:**
- `output/chain-ladder/cl_cdfs.csv` must exist (from script 4)
- `output/initial-expected/ie_ultimates.csv` must exist (from script 5)

```bash
python scripts/6-apply-bf.py
python scripts/7-combine-ultimates.py
```

**BF Formula:**
```
BF Ultimate  = Actual + (1 - % developed) x Expected
% developed  = 1 / CDF
% unreported = 1 - % developed
IBNR         = (1 - % developed) x Expected
Unpaid       = BF Ultimate - Paid diagonal
```

After running both scripts, present the IBNR summary to the user:
1. **BF vs CL** — BF gives more weight to IE for immature periods (low % developed)
2. **BF vs IE** — BF gives more weight to actual development for mature periods
3. **Selected ultimate** — the default selection is BF; the user can override in selected-ultimates.xlsx

Step 6 writes `output/bornhuetter-ferguson/bornhuetter-ferguson.xlsx`

Step 7 writes:
- `output/selected-ultimates/selected-ultimates.xlsx`
- `output/post-method/post-method-series-diagnostics.xlsx`
- `output/post-method/post-method-triangle-diagnostics.xlsx`
- `output/full-analysis.xlsx`

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `No module named 'polars'` | polars unavailable | All scripts use pandas + pickle — safe to ignore |
| `FileNotFoundError: output/prep/triangles.pkl` | Scripts run out of order | Run steps 1–3 first |
| `FileNotFoundError: output/selections/cl_selections.json` | CL selections not written | Complete Step 4 first |
| `KeyError` on measure name | Wrong measure name in selections | Check `ldf_averages.csv` for exact measure names |
| Period/age type error | Non-numeric labels | Scripts handle this automatically via `_try_int()` |
