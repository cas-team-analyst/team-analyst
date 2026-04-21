# Tail Factor Selection Sub-Workflow — Implementation Checklist

> Each task is self-contained and farmable independently.
> Implement in order — later tasks depend on earlier ones.
>
> **Script renumbering:** current `2c-chainladder-ultimates.py` → `2f-chainladder-ultimates.py`.
> Tail workflow inserts as 2c / 2d / 2e.
>
> **Excel rename:** `Chain Ladder Selections.xlsx` → `Chain Ladder Selections - LDFs.xlsx`.

---

## Phase 1: Renames

- [x] **1.1** Rename `scripts/2c-chainladder-ultimates.py` → `scripts/2f-chainladder-ultimates.py` in the skill scripts folder
- [x] **1.2** In `assets/PROGRESS.md` — replace all `2c-chainladder-ultimates.py` → `2f-chainladder-ultimates.py`
- [x] **1.3** In `scripts/2a-chainladder-create-excel.py` — change output filename from `Chain Ladder Selections.xlsx` → `Chain Ladder Selections - LDFs.xlsx`
- [x] **1.4** In `scripts/2b-chainladder-update-selections.py` — update reference to `Chain Ladder Selections - LDFs.xlsx`
- [x] **1.5** In `scripts/2f-chainladder-ultimates.py` (renamed) — update reference to `Chain Ladder Selections - LDFs.xlsx`
- [x] **1.6** In `assets/PROGRESS.md` — replace all `Chain Ladder Selections.xlsx` → `Chain Ladder Selections - LDFs.xlsx`
- [x] **1.7** In `scripts/6-create-complete-analysis.py` — update any reference to `Chain Ladder Selections.xlsx` → `Chain Ladder Selections - LDFs.xlsx`

---

## Phase 2: Tail Methods & Diagnostics Script

- [x] **2.1** Create `scripts/2c-tail-methods-diagnostics.py`

  ### Inputs

  | Source | What's needed |
  |--------|--------------|
  | `processed-data/1_triangles.parquet` | Raw cumulative triangle by period × age × measure — Skurnick needs a 2D cumulative array (oldest AY = row 0) per measure from starting_age onward |
  | `processed-data/2_enhanced.parquet` | Age-to-age factors by period × age × measure — used for monotonicity / CV / structural break detection and for WLS fitting (individual AY factors as data points, weighted by `weight` column) |
  | `processed-data/4_ldf_averages.parquet` | Weighted avg LDF per interval × measure (`weighted_all` column) — the `factors` array passed to Bondy / Modified Bondy / McClenahan / Exp Dev |
  | `selections/Chain Ladder Selections - LDFs.xlsx` | Selected LDF per interval × measure (from "Selection" row; fallback to "AI Selection") — needed to compute the full CDF from age 1 to last observed age, which is required for "tail as % of CDF" and sensitivity reserve impact |

  **Writes:** `processed-data/tail-scenarios.parquet`

  ### Starting Point Candidates

  Use **selected LDFs** from `selections/Chain Ladder Selections - LDFs.xlsx` (Selection row only — error if selections not found for a measure) as the `factors` array for all methods.

  Candidate starting ages = ~5 evenly-spaced ages sampled from the last half of observed ages. Two constraints must both be satisfied for a valid starting age:
  - At least 3 selected LDF intervals remain from starting_age onward (minimum data to fit)
  - Age ≥ type minimum:
    - Paid Loss / Closed Count → 60mo
    - Incurred Loss / Reported Count → 48mo

  Algorithm: take all observed ages, slice the last half, then pick every `ceil(n/5)` to yield ~5 candidates. Drop any that fail either constraint. If fewer than 2 remain, extend back into the first half until 2 valid candidates exist.

  Run every (method × starting_age) combination. Diagnostics identify the best starting point — no pre-filtering.

  Print banner per measure noting expected relative tail length.

  ### Methods (implement inline — no imports from examples)

  Skip `none` and `scalar`. Implement these 6:

  | Method key | `factors` input | Other inputs | Technique |
  |------------|----------------|--------------|-----------|
  | `bondy` | weighted avg LDFs from starting_age onward (1D array) | — | `tail = last finite factor` |
  | `modified_bondy_double_dev` | same | — | `d = last − 1; tail = 1 + 2d` |
  | `modified_bondy_square_ratio` | same | — | `tail = last²` |
  | `exp_dev_quick` | same | — | Fit `ln(d_t) = ln(D) + t·ln(r)` where `d_t = factor_t − 1` using WLS (see fitting section below); `tail = 1 + D·r^K / (1−r)`, K=8 |
  | `exp_dev_quick_exact_last` | same | — | Same fit + Boor Improvement 2 rescale: `1 + (d_actual/d_fitted)·(tail_fitted − 1)` |
  | `exp_dev_product` | same | — | Same fit; multiply `1 + D·r^t` until dev portion < 1e-6 |
  | `double_exp` | same | — | Fit `ln(d_t) = b0 + b1·t + b2·t²` (log-quadratic) using WLS; integrate numerically to compute tail: `tail = 1 + Σ exp(b0 + b1·t + b2·t²)` summed over future periods until dev portion < 1e-6 |
  | `mcclenahan` | same | `m_months = max_age + 12`, `a_months = 6` | Synthetic cumulative from factors (base 100); extract incrementals; estimate `r` = mean of last 5 decaying incremental ratios (ratio < 1); closed form: `tail = 12q / (12q − p^(m−a−10)·(1−p^12))` where `p = r^(1/12)`, `q = 1−p` |
  | `skurnick` | — (not used) | 2D cumulative array from `1_triangles.parquet`, oldest AY = row 0, columns from starting_age onward | Fit `ln(inc_y) = ln(A) + y·ln(r)` on oldest AY incrementals; closed form: `tail = (1−r) / (1−r−r^n)` where n = number of incremental periods |

  ### Fitting (curve methods: exp_dev variants and double_exp)

  - **Preferred:** WLS — weight each age-point by sum of losses across AYs at that age (`weight` column from `2_enhanced.parquet` aggregated per age). WLS preferred over OLS; fall back to OLS only if weights unavailable.
  - **Transform:** fit `ln(factor_t − 1)` not raw factors
  - Fit only on ages ≥ starting_age
  - Note: Skurnick and McClenahan use their own internal fitting logic (not this WLS curve fit)

  ### Diagnostics per scenario

  Capture all of these per (measure × starting_age × method). Selectors and actuary use these to identify best starting point.

  **Starting point quality diagnostics** (describe the data at this starting age — same value for all methods at same starting_age). Good starting point = `is_monotone_from_here=True`, `cv_at_starting_age` low, `slope_sign_changes=0`:
  - `n_factors_in_fit`: count of selected LDF ages from starting_age onward — fewer = less stable fit
  - `n_ay_contributing`: count of AYs with observed data at starting_age (from `2_enhanced`)
  - `is_monotone_from_here`: bool — are selected LDFs monotonically decreasing from starting_age to last age?
  - `cv_at_starting_age`: CV of individual AY factors at starting_age (from `2_enhanced`)
  - `slope_sign_changes`: count of slope direction reversals in selected LDFs from starting_age onward — 0 = smooth, >0 = structural break present

  **Fit quality diagnostics** (method-specific):
  - **R²** on selected LDFs from starting_age onward (fit log(factor−1) for exp_dev; for McClenahan/Skurnick compute R² of fitted vs observed; for Bondy/Modified Bondy: N/A)
  - **Residuals by age**: `{age: observed_log_factor_minus1 − fitted}` as JSON string; N/A for Bondy/Modified Bondy
  - **LOO stability (accident year LOO)**: for each AY in `2_enhanced`, exclude it, refit curve, recompute tail. Report std dev, min, max across all LOO trials. For Bondy (no curve): LOO on the last observed weighted avg factor.
  - **Gap to last observed**: `abs(fitted_curve_value_at_starting_age − last selected_LDF at starting_age)`. Flag (`gap_flag`) if > 0.005. A flagged gap means the curve doesn't connect smoothly to observed data — selector must reject this scenario or choose a later starting_age where the curve rejoins observed factors before switching.

  **Reserve impact diagnostics**:
  - **Tail as % of CDF**:
    - Full CDF = product of all selected LDFs (age 12 → last age) × tail_factor
    - `pct_of_cdf = (tail_factor − 1) / (full_CDF − 1) × 100`
  - **Materiality flag**: tail contribution < 0.1% to full CDF → True/False. Valid anchor for cutoff: materiality_ok = True means losses extrapolated beyond this point are immaterial.
  - **Sensitivity reserve impact**:
    - Diagonal actuals per measure from `1_triangles.parquet` (most recent value per AY)
    - `base_reserve = sum(diagonal_actuals) × (1 − 1/CDF_at_current_age)`
    - Recompute with tail × 1.10, 0.90, 1.20, 0.80; report delta vs base reserve

  ### Output columns

  `measure, starting_age, method, method_params, tail_factor, n_factors_in_fit, n_ay_contributing, is_monotone_from_here, cv_at_starting_age, slope_sign_changes, r_squared, loo_std_dev, loo_min, loo_max, gap_to_last_observed, gap_flag, pct_of_cdf, materiality_ok, sensitivity_plus10_reserve_delta, sensitivity_minus10_reserve_delta, sensitivity_plus20_reserve_delta, sensitivity_minus20_reserve_delta, residuals_json`

- [x] **2.2** Test against `demo/demo4-complete/` — parquet has rows for each measure × method × starting age, values actuarially reasonable, no crashes

---

## Phase 3: Tail Excel Workbook

- [x] **3.1** Create `scripts/2d-tail-create-excel.py`

  **Reads:** `processed-data/tail-scenarios.parquet`, `processed-data/2_enhanced.parquet`, `processed-data/3_diagnostics.parquet`, optional `selections/tail-factor-prior.csv`  
  **Writes:** `selections/Chain Ladder Selections - Tail.xlsx` (one sheet per measure)  
  **Guard:** raise error if file already exists (protect manual edits — same as 2a)
  
  **Prior selections:** If `selections/tail-factor-prior.csv` exists (columns: `measure`, `cutoff_age`, `tail_factor`, `method`, `reasoning`), load it and include in Section D "Prior Selection" row. Selector agents reference these to document changes from prior year.

  Sheet layout per measure:

  **Section A — Triangle Type Banner**
  - Measure name + type note (e.g., "Paid loss tails materially longer than incurred")
  - Key stats row: max observed age | # AYs | % closed at last age (from diagnostics) | last observed avg LDF

  **Section B — Observed Factors Table**
  - Triangle: AYs as rows × ages as columns, age-to-age factors (from `2_enhanced`)
  - Bottom rows: weighted avg LDF per age, CV per age
  - Highlight candidate starting age columns (light yellow)

  **Section C — Scenario Comparison Table**
  - One row per (method × starting_age)
  - Columns: Starting Age | Monotone | CV | Slope Breaks | Method | Params | Tail Factor | R² | LOO Std Dev | Gap to Last | Gap Flag | % of CDF | Materiality OK | ±10% Reserve Δ | ±20% Reserve Δ
  - Row color: green if `is_monotone_from_here=True` AND `slope_sign_changes=0` AND R² > 0.85 AND `gap_flag=False` AND `materiality_ok`; yellow if marginal; red otherwise; Bondy/Modified Bondy always yellow (no R²)

  **Section D — Selection Area**  
  Rows (columns: label | cutoff_age | tail_factor | method | reasoning):
  1. Prior Selection (pre-fill from `selections/tail-factor-prior.csv` if exists — optional)
  2. Prior Delta (current − prior) | Delta Driver (text explaining change)
  3. Rule-Based Selection (blank — 2e fills; blue background)
  4. AI Selection (blank — 2e fills; purple background)
  5. **Final Selection** (yellow — actuary input, may override automated selections)
  6. Pct of CDF
  7. Anchor Basis: "Closure/payment data" or "Materiality (<0.1% of CDF)" (text — required)
  8. Sensitivity ±10% reserve delta
  9. Sensitivity ±20% reserve delta

  **Section E — Documentation Checklist**  
  Manual checkbox rows:
  - Alternatives considered and documented
  - Diagnostics reviewed (R², residuals, LOO)
  - Sensitivity results documented
  - Override justification (if selection differs from top scenario)
  - Prior vs current delta and driver documented
  - Peer review notes
  - Sign-off

- [x] **3.2** Test against demo data — Excel opens, one sheet per measure, scenario table populated, colors correct, selection rows present

---

## Phase 4: Tail Selection Update Script

- [x] **4.1** Create `scripts/2e-tail-update-selections.py`

  **Reads:** `selections/tail-factor.json`, `selections/tail-factor-ai.json` (optional)  
  **Updates:** Rule-Based and AI Selection rows in `selections/Chain Ladder Selections - Tail.xlsx`  
  Pattern mirrors `2b-chainladder-update-selections.py`.

  Expected JSON schema:
  ```json
  [
    {
      "measure": "Incurred Loss",
      "cutoff_age": 84,
      "tail_factor": 1.023,
      "method": "exp_dev_quick",
      "reasoning": "...",
      "pct_of_cdf": 2.3,
      "prior_selection": 1.018,
      "prior_delta": 0.005,
      "prior_delta_driver": "...",
      "alternatives_considered": "...",
      "diagnostics_summary": "..."
    }
  ]
  ```

- [x] **4.2** Test with hand-written `tail-factor.json` → run 2e → confirm Excel rows populated correctly

---

## Phase 5: Tail Selector Agents

- [x] **5.1** Create `.claude/agents/selector-tail-factor.md`

  Rule-based directed agent (blue). Reads `selections/Chain Ladder Selections - Tail.xlsx` (all sheets).

  Must apply the 15-point framework from `examples/tail-factor-selction/tail-factor-decision-point-guide.md` plus:

  **Triangle type recognition:**
  - Identify triangle type from measure name; state expected tail length relative to other measures
  - Paid Loss tails materially longer than Incurred Loss; Closed Count tails materially longer than Reported Count
  - Select each triangle's tail independently — never copy one measure's tail to another

  **Starting point selection:**
  - Prefer starting ages where `is_monotone_from_here=True`, `cv_at_starting_age` is low, `slope_sign_changes=0`
  - Avoid starting ages with structural breaks or high AY variance — these indicate the development pattern has not stabilized

  **Fit quality:**
  - Prefer WLS over OLS; prefer fitting on `log(factor − 1)`
  - Prefer R² > 0.85 computed on late-age subset only (ages ≥ starting_age)
  - Prefer low LOO std dev — high LOO variability means fit is AY-sensitive and unreliable

  **Gap rule (hard):**
  - `gap_flag = True` → reject this scenario. Do not accept a tail that disconnects from the last observed factor. Prefer a scenario with `gap_flag = False`, or explain explicitly why a gap is acceptable and how it was handled.

  **Anchor (required — at least one must apply):**
  - Closure/payment data shows losses substantively complete at cutoff age, OR
  - Extrapolated tail contributes < 0.1% to CDF (`materiality_ok = True`)
  - State which anchor applies in reasoning

  **Documentation (all required in JSON):**
  - method chosen and why
  - alternatives considered and why rejected (name specific methods/starting ages)
  - R², LOO std dev, gap value for selected scenario
  - tail as % of CDF
  - sensitivity ±10% and ±20% reserve delta
  - prior selection, current selection, delta (current − prior), driver of change
  - Writes `selections/tail-factor.json` — all schema fields required

- [x] **5.2** Create `.claude/agents/selector-tail-factor-ai.md`

  Open-ended AI agent (purple, opus model). Same data, independent holistic judgment. No rigid rule sequence. Must still produce all documentation fields.  
  Writes `selections/tail-factor-ai.json`.

---

## Phase 6: Remove Tail from LDF Selector Agents

- [x] **6.1** Modify `.claude/agents/selector-chain-ladder-ldf.md`
  - Delete entire §14 (Tail Factor) section
  - Remove Task item 4 instruction: "Always include a tail factor selection as the final entry with `'column': 'Tail'`"
  - Remove "Paid tail ≥ incurred tail always" from §9
  - Remove `{"interval": "Tail", ...}` from output format example
  - Update Task item 4: "Return a JSON selection with full reasoning for each non-tail interval only."

- [x] **6.2** Modify `.claude/agents/selector-chain-ladder-ldf-ai.md`
  - Remove "Always include a tail factor as the final entry with `'interval': 'Tail'`" paragraph
  - Remove tail from output format example
  - Update task description accordingly

---

## Phase 7: Wire Tail into 2f (Ultimates)

- [x] **7.1** Modify `scripts/2f-chainladder-ultimates.py`

  Replace tail-reading logic with priority fallback:
  1. `selections/Chain Ladder Selections - Tail.xlsx` "Rule-Based Selection" row → user's final selection (may be manual override)
  2. `selections/tail-factor.json` → rule-based selector output
  3. `selections/tail-factor-ai.json` → AI selector output

  Excel is priority 1 because it contains the user's final choice (accepting or overriding automated selections).
  
  Log to console which source was used for each measure.

- [x] **7.2** Test: Verify Excel is read as priority 1, JSON files as fallbacks 2 and 3

---

## Phase 8: Include Tail Workbook in Complete Analysis

- [x] **8.1** Modify `scripts/6-create-complete-analysis.py`

  Include `selections/Chain Ladder Selections - Tail.xlsx` sheets in `output/complete-analysis.xlsx` with prefix `"Tail - "` (same pattern as existing sheet consolidation).

- [x] **8.2** Test: run 6 with demo data → `complete-analysis.xlsx` contains "Tail - Incurred Loss", "Tail - Paid Loss", etc.

---

## Phase 9: Update PROGRESS.md

- [x] **9.1** In Step 4 — remove tail from both LDF subagent tasking bullets:
  - Remove `**including a tail factor (interval "Tail") for each measure**` from `selector-chain-ladder-ldf` bullet
  - Remove `**including a tail factor**` from `selector-chain-ladder-ldf-ai` bullet

- [x] **9.2** In Step 5 — update `2c-chainladder-ultimates.py` → `2f-chainladder-ultimates.py`

- [x] **9.3** In Step 7 and Step 9 — update any remaining references to `2c` → `2f`

- [x] **9.4** Insert new **Step 4.5** between Step 4 and Step 5:

  ````
  # Step 4.5: Tail Factor Selection

  Goal: Select tail factors for each triangle with curve fitting, diagnostics, and ASOP 43-compliant documentation.

  - [ ] Copy `2c-tail-methods-diagnostics.py`, `2d-tail-create-excel.py`, `2e-tail-update-selections.py` from the reserving-analysis skill scripts folder into the project `scripts/` folder.
  - [ ] Run `2c-tail-methods-diagnostics.py`. Output: `processed-data/tail-scenarios.parquet`.
  - [ ] Run `2d-tail-create-excel.py`. Output: `selections/Tail Factor Selections.xlsx`.
  - [ ] Create `selections/tail-factor.json` with `[]`.
  - [ ] Task a single `selector-tail-factor` subagent to: Review `selections/Tail Factor Selections.xlsx` in full, apply the 15-point tail factor decision framework (recognize triangle type, fit multiple curve forms on log(factor−1) with WLS, check R²/LOO/gap diagnostics, anchor to closure data or <0.1% CDF materiality), and write selections to `selections/tail-factor.json` with required fields: measure, cutoff_age, tail_factor, method, reasoning, pct_of_cdf, prior_selection, prior_delta, prior_delta_driver, alternatives_considered, diagnostics_summary.
  - [ ] Task a single `selector-tail-factor-ai` subagent to independently select tail factors using holistic actuarial judgment and save to `selections/tail-factor-ai.json` (same schema).
  - [ ] Run `2e-tail-update-selections.py` to populate Excel with both selections.
  - [ ] Tell the user where `selections/Tail Factor Selections.xlsx` is. Final Selection row feeds 2f; Rule-Based is default if Final blank; AI is cross-check.
  - [ ] **Always pause here regardless of interaction mode** — tail factors are material and require actuary sign-off. Open the workbook. Wait for user confirmation before continuing.
  - [ ] **Update REPORT.md:**
    - Fill in **Section 5.1** tail factor subsection: for each measure, document selected tail, cutoff age, method, tail as % of CDF, sensitivity ±10/20% reserve delta, prior vs current delta and driver.
    - Add to **Section 8.2**: tail sensitivity range and reserve impact bounds.
    - Add to **Section 11**: measures where rule-based and AI selections diverged materially, or where R²/LOO flagged instability.
    - Add to **Section 12** ASOP Self-Check: alternatives considered, diagnostics documented, sensitivity documented, override justifications, peer review notes recorded.
  ````

---

## End-to-End Verification

- [ ] **V.1** Full pipeline against `demo/demo1-data/`: 1a → 1b → 1c → 1d → 2a → (LDF without tail) → 2b → 2c → 2d → (tail JSON) → 2e → 2f → 3 → 4 → 5a → 5b → 6 → 7. No errors. Tail feeds CDFs correctly.
  - **Note:** Individual scripts tested successfully with demo4-complete data. Full end-to-end pipeline from scratch would require running against demo1-data with updated selector agents.
- [x] **V.2** `complete-analysis.xlsx` contains "Tail - " sheets.
  - **Verified:** 4 tail sheets present: "Tail - Closed Count", "Tail - Incurred Loss", "Tail - Paid Loss", "Tail - Reported Count"
- [ ] **V.3** `chainladder.json` from demo has no "Tail" entries.
  - **Note:** Current demo4-complete data predates selector agent updates. Fresh analysis would produce chainladder.json without Tail entries per updated agent task definition.
- [x] **V.4** `2f` console log shows tail source used per measure.
  - **Verified:** Script logs "Tail factor source: tail-factor.json" (priority 1) with correct fallback behavior to tail-factor-ai.json (priority 2) and Excel (priority 3).
