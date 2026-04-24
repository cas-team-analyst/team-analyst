---
name: chain-ladder
description: >
  Chain-ladder LDF selection step. Use when performing chain-ladder development,
  selecting age-to-age factors, or making LDF selections for actuarial reserving.
---

# Chain Ladder — LDF Selection

## What You Do

Read `output/prep/ldf_averages.csv` and select an age-to-age factor (LDF) for
each (measure × interval) combination. Use `output/prep/ldf_triangle.csv` when
you need per-period factors (e.g. latest diagonal vs history). Then write
`output/selections/cl_selections.json`.

Run script 4 after writing the JSON:
```bash
python scripts/4-apply-cl-selections.py
```
Output: `output/chain-ladder/chain-ladder.xlsx`

## Reading the LDF Averages

Open or read `output/prep/ldf_averages.csv`. Columns:
- `measure` — triangle measure (e.g. "Incurred Loss", "Paid Loss")
- `interval` — development interval (e.g. "12-24", "96-108")
- `weighted_all`, `simple_all`, `excl_hi_lo_all` — full-history averages
- `weighted_3yr`, `simple_3yr`, `excl_hi_lo_3yr` — recent 3-year averages
- `weighted_5yr`, `simple_5yr`, `excl_hi_lo_5yr` — recent 5-year averages
- `cv_3yr`, `cv_5yr` — coefficient of variation (stability measure)
- `slope_3yr`, `slope_5yr` — trend in recent LDFs (positive = rising)

This pipeline exposes **3-year, 5-year, and all-history** averages only (no separate 7-year column). When methodology refers to longer-term or “7-year” style preference, use **5-year** and **all-history** (`*_5yr`, `*_all`, `excl_hi_lo_*`) as the longer window.

## The Eight Core Selection Criteria

Apply these **together with judgment**; they often pull in different directions. Your `reasoning` field should cite the criteria that drove the choice.

### 1. Outlier handling (exclude high/low)

Where there is significant variability in a particular age-to-age column, use averages that exclude the high and low values (`excl_hi_lo_*`). This reduces the influence of extreme points that may not reflect typical development.

### 2. Recency preference

More recent averages are preferable to longer-term averages because they better reflect current conditions—claims handling, technology, and operations. In **large** triangles, **avoid relying on all-years averages alone**, as older points may reflect materially different environments. **Default toward 5-year** (and 3-year when appropriate); use **shorter** windows when there is a **clear trend** in recent data (`slope_3yr`, `slope_5yr`, and visual review of `ldf_triangle.csv`).

### 3. Asymmetric conservatism

Actuaries lean conservative. When development is **trending downward**, be slower to react—do not move the full distance immediately. When development is **trending upward**, respond faster and move more of the distance toward the higher level.

**Implemented thresholds (for guidance):** a drop of **more than 10%** → cautious/partial response; an increase of **more than 5%** → more responsive.

### 4. Bayesian anchoring to prior selection

Use the **prior selected LDF** as an anchor to avoid wild swings between studies. The latest diagonal point is new information, but how far you move from the prior depends on how consistent that new point is with recent history:

- If the latest point is **close to the prior** → generally stay near the prior.
- If the latest point is **higher** than the prior → raise the selection (magnitude depends on consistency of recent data).
- If the latest point is **lower** than the prior → lower the selection, but **more cautiously** (see asymmetric conservatism).

Sometimes explicit **weights** are appropriate (e.g. 50% prior / 50% preferred average).

**Prior LDFs in spreadsheets:** often provided as a row below the triangle, labeled “Prior LDFs” or “Prior Selection.” If your project does not supply them, state that in `reasoning` and rely more heavily on recent averages and stability metrics.

### 5. Latest-point outlier exception (override of Bayesian anchoring)

If the **latest diagonal** factor is very different from the past **5–10** points in that column (`ldf_triangle.csv`), treat it as a likely outlier from unusual single-claim development. **Threshold:** more than **15%** in development terms (compare **factor − 1** across points, or equivalent relative comparison). Do **not** give that point outsized weight; **rely on the averages and the prior** instead.

### 6. Trending

If the most recent **3–4** factors move consistently in one direction relative to earlier points, a new development level may be emerging. Do **not** move the full distance in one step, but **begin** moving in that direction—giving the **3-year** average meaningful weight is often reasonable. Distinguish a true trend from a one-time anomaly (see criterion 5 and operational judgment).

### 7. Sparse data

When data is thin—**fewer than ~50 claims per year**, or **average incurred losses below ~$1M per year** for accident years older than **2** years—prefer **longer-term** averages (5-year and all-history) over shorter-term **3-year** averages. Use the **count triangle** when available to assess volume.

### 8. Convergence override

If **3-year, 5-year, and all-history** averages (including `excl_hi_lo_*` where used) fall in a **tight band** and are **collectively and materially different** from the prior selection, **override the prior** and select from those converged averages—the current data has aligned enough to justify moving off the anchor.

## Additional Considerations

### Volume-weighted averages — use with caution

Volume-weighting is not always superior. When a **small number of accident years dominate** volume, weighted averages can overweight those years and distort selections. In those cases, **simple** or **exclude high/low** averages may be more appropriate.

### Diagnostic triangles (supplementary)

When available, **average case reserves**, **paid-to-incurred** ratios, and **claims closure** rates can flag anomalies not visible in raw development alone. Use them to support or challenge an LDF choice; they are **not** required by the scripts but strengthen judgment.

## Holistic Application

Weigh **multiple criteria in one conclusion**; no single rule always wins. When signals conflict (e.g. convergence vs. latest-point outlier), resolve with **actuarial judgment**, explain the tradeoff in `reasoning`, and prefer **stability and credibility** of the evidence over mechanical defaults.

## Selections JSON Format

Write to `output/selections/cl_selections.json`:
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
  },
  ...
]
```

Required fields: `measure`, `interval`, `selected_ldf`, `reasoning`
- Include one entry per (measure × interval) — don't skip any intervals
- Include one `"tail"` entry per measure
- Measure names must match exactly as they appear in `ldf_averages.csv`
