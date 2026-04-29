# Tail Cutoff Refactor Plan

> **Key Simplification:** No separate cutoff field or column. LDF selections array naturally stops at cutoff. Last interval's reasoning explains why. Scripts infer cutoff by parsing last interval ("72-84" → 84). Cleaner data model, less code, no extra UI elements.

## Progress Checklist

### Planning & Design
- [x] Document current workflow
- [x] Design new architecture (simplified cutoff model)
- [x] Identify files to modify
- [x] Resolve open questions (all resolved!)

### Phase 1: LDF Selector Changes
- [x] Update selector-chain-ladder-ldf-ai-rules-based.agent.md (add cutoff criteria, explain cutoff requirement + format)
- [x] Update selector-chain-ladder-ldf-ai-open-ended.agent.md (explain cutoff requirement + format)
- [ ] Test: Verify selections stop at different intervals with cutoff reasoning
- [ ] Test: Verify last+1 interval has cutoff-only reasoning (no selection)

### Phase 2: Tail Curve Fitting
- [ ] Add helper: `infer_cutoff_from_selections()` to modules
- [ ] Update 2c-tail-methods-diagnostics.py (infer cutoff, fit on selected LDFs)
- [ ] Test: Verify scenarios have fitted_ldfs and final_cdf
- [ ] Test: Verify curves fitted only on selected LDFs (not all observed)

### Phase 3: Tail Selector & Excel
- [ ] Update selector-tail-factor-ai-rules-based.agent.md (remove cutoff selection)
- [ ] Update selector-tail-factor-ai-open-ended.agent.md (remove cutoff selection)
- [ ] Update 2d-tail-create-excel.py (new structure with fitted LDFs)
- [ ] Update 2e-tail-update-selections.py (new JSON format)
- [ ] Test: Verify tail Excel shows method + fitted_ldfs

### Phase 4: Ultimates Calculation
- [ ] Update 2f-chainladder-ultimates.py (use selected + fitted LDFs)
- [ ] Test: Verify CDFs match expected values
- [ ] Test: Compare ultimates to baseline (document differences)

### Phase 5: Analysis Display
- [ ] Update 6-analysis-create-excel.py (show fitted LDFs with special formatting)
- [ ] Test: Verify visual distinction between selected and fitted LDFs
- [ ] Test: Verify cutoff marker displays correctly

---

## Executive Summary

**Current Flow:**
1. LDF selectors → pick LDFs for all intervals (12-24, 24-36, ..., 96-108, etc.)
2. Tail selectors → pick cutoff age + tail curve method + tail factor

**New Flow:**
1. LDF selectors → pick LDFs up to cutoff (array naturally stops at cutoff, last interval reasoning explains why)
2. Tail selectors → pick **only the curve method** (Bondy, exp_dev_quick, etc.)
3. Tail curve fitting → fit curve **only on selected LDFs** after cutoff
4. Tail curve → calculate **fitted LDFs** for ages after cutoff + **final CDF** at ultimate age
5. Analysis → show where LDFs come from (selected vs tail curve) + use tail curve LDFs to fill gaps and populate starting CDF so the others can be back-filled.

**Key Simplification:**
- **No separate cutoff field** — cutoff inferred from last interval in selections array (saves code, cleaner data model)
- **No Cutoff column in Excel** — selections just stop where they stop (natural visual difference between methods)
- Last interval's reasoning explains cutoff choice ("Last LDF. Cutoff at 84: CV=0.08, monotonic...")
- Scripts use helper `infer_cutoff_from_selections()` to parse last selected interval when needed

---

## Rationale

**Why select cutoff with LDFs?**
- CV, slope, monotonicity, and other cutoff criteria are already in LDF selector context
- Cutoff selection is part of LDF selection logic (when to stop trusting observed factors)
- Each selection method (rules-based/open-ended/user) may choose different cutoffs
- Separating cutoff from LDF selection creates unnecessary two-step process

**Why tail selector should only pick method?**
- Tail selector's job: evaluate curve fit diagnostics (R², LOO, residuals, gap) and choose best curve
- Cutoff already determined by LDF selector → tail selector doesn't re-decide "where to start"
- Tail selector still needs all ATA factors as context (to assess fit quality vs observed data)

**Why fit curves only on selected LDFs?**
- Selected LDFs represent actuary's judgment of credible pattern
- Fitting on all observed LDFs may include outliers/noise that LDF selector already rejected
- Tail curve should extend the **selected pattern**, not the raw observed pattern

**Why calculate final CDF from curve?**
- Standard actuarial practice: tail curve determines CDF at ultimate age (beyond last observed age)
- Different curves have different methods for this (see ken-tail-factor examples)
- Each curve method (exp_dev, double_exp, mcclenahan, etc.) has a way to calculate infinite-horizon CDF

---

## Architecture Changes

### 1. LDF Selector Output Format

**Current:**
```json
[
  {"interval": "12-24", "selection": 1.6573, "reasoning": "..."},
  {"interval": "24-36", "selection": 1.2341, "reasoning": "..."},
  ...
]
```

**New:**
```json
[
  {"interval": "12-24", "selection": 1.6573, "reasoning": "Weighted 3yr average most credible..."},
  {"interval": "24-36", "selection": 1.2341, "reasoning": "Geometric average balances..."},
  ...
  {"interval": "228-240", "selection": 1.0051, "reasoning": "Last credible LDF: CV=0.09, within historical range..."},
  {"interval": "240-252", "reasoning": "CUTOFF at 240 months: is_monotone_from_here=True, CV beyond this point >0.15, 5 intervals remaining for tail curve fit. Rejected 252+ due to high variance."}
]
```

**Notes:**
- Array includes last selected interval + one more interval (unselected) with cutoff reasoning
- **Last selected interval** (e.g., "228-240") has `selection` value + reasoning about that specific LDF
- **Next interval** (e.g., "240-252") has NO `selection` (or null/omitted) + reasoning explaining why cutoff is here
- **Cutoff age inferred from last selected interval**: "228-240" → cutoff = 240 months
- Each method (rules-based/open-ended/user) can have different cutoff (different stopping points)
- **No separate cutoff field needed** — data structure itself shows where selections stop

---

### 2. Tail Selector Input Format

**Current input:**
- Selected LDFs only (from LDF excel)
- Tail scenarios with diagnostics

**New input:**
- **All age-to-age factors** (from 2_enhanced.parquet) for fit quality assessment
- Selected LDFs (from LDF excel) to know which factors to fit curve on
- Selected cutoff age (from LDF selections)
- Average/min/max/slope/CV of ATA factors (restated for context)
- Tail scenarios with diagnostics (R², LOO, gap, etc.)

**Context markdown additions:**
```markdown
## Age-to-Age Factors (All Observed)

| Period | 12-24 | 24-36 | 36-48 | 48-60 | 60-72 | 72-84 | 84-96 | 96-108 |
|--------|-------|-------|-------|-------|-------|-------|-------|--------|
| 2016   | 1.823 | 1.456 | 1.234 | 1.123 | 1.067 | 1.034 | 1.018 | 1.009  |
| 2017   | 1.798 | 1.442 | 1.229 | 1.118 | 1.063 | 1.031 | 1.015 | 1.007  |
| ...    | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...    |

## Selected LDFs and Cutoff

**Cutoff Age:** 84 months
**Cutoff Reasoning:** Selected 84 as cutoff: CV=0.08, monotonic from here, 5 factors remaining for curve fit.

| Interval | Selected LDF | Method |
|----------|--------------|--------|
| 12-24    | 1.8093       | Rules-Based AI |
| 24-36    | 1.4489       | Rules-Based AI |
| ...      | ...          | ...    |
| 72-84    | 1.0323       | Rules-Based AI (last before tail) |

## ATA Factor Statistics (for fit quality assessment)

|                     | 84-96  | 96-108 | 108-120 | 120-132 | ... |
|---------------------|--------|--------|---------|---------|-----|
| Min                 | 1.012  | 1.005  | 1.002   | 1.001   | ... |
| Max                 | 1.021  | 1.012  | 1.008   | 1.004   | ... |
| All Years Avg       | 1.0165 | 1.0081 | 1.0048  | 1.0024  | ... |
| All Yrs Excl Hi/Lo  | 1.0164 | 1.0080 | 1.0047  | 1.0023  | ... |
| Weighted All        | 1.0167 | 1.0083 | 1.0050  | 1.0025  | ... |
| Wtd Excl Hi/Lo      | 1.0166 | 1.0082 | 1.0049  | 1.0024  | ... |
| CV                  | 0.045  | 0.038  | 0.042   | 0.051   | ... |
| Slope               | -0.02  | -0.01  | -0.008  | -0.005  | ... |

**Note:** Fitted tail curve values should ideally stay within [min, max] range of observed ATA factors.

## Tail Scenarios

(Rest of existing tail scenario content...)
```

---

### 3. Tail Selector Output Format

**Current:**
```json
[
  {
    "measure": "Incurred Loss",
    "cutoff_age": 84,
    "tail_factor": 1.0230,
    "method": "exp_dev_quick",
    "reasoning": "..."
  }
]
```

**New:**
```json
[
  {
    "measure": "Incurred Loss",
    "method": "exp_dev_quick",
    "method_params": {"D": 0.0156, "r": 0.842},
    "fitted_ldfs": {
      "84-96": 1.0167,
      "96-108": 1.0084,
      "108-120": 1.0042,
      "120-Ult": 1.0000
    },
    "final_cdf_at_cutoff": 1.0230,
    "reasoning": "exp_dev_quick selected: R²=0.91, LOO_std=0.0015, no gap (fitted@84=1.0167 vs selected=1.0150, delta=0.0017<0.005). Curve fitted on 5 selected LDFs from cutoff age 84. Final CDF at 84=1.0230."
  }
]
```

**Notes:**
- `method` = curve type chosen (exp_dev_quick, double_exp, mcclenahan, etc.)
- `method_params` = curve parameters (for reproducibility/validation)
- `fitted_ldfs` = LDFs calculated by curve for ages after cutoff
- `final_cdf_at_cutoff` = CDF at cutoff age (used as "tail factor" in current system)
- No `cutoff_age` field (comes from LDF selections now)

---

### 4. Chain Ladder Excel Changes

**LDF Selection Workbook (Chain Ladder Selections - LDFs.xlsx):**

**Current columns:** `12-24 | 24-36 | 36-48 | ... | 96-108 | Tail`

**New columns:** Same — `12-24 | 24-36 | 36-48 | ... | 96-108 | Tail` (no changes needed!)

**Row structure (per measure sheet):**
```
Age-to-Age Factors
  Period | 12-24 | 24-36 | ... | 72-84 | 84-96 | 96-108 | ...
  2016   | 1.823 | 1.456 | ... | 1.034 | 1.018 | 1.009  | ...
  ...

Averages
  Wtd 3yr  | 1.809 | 1.449 | ... | 1.032 | 1.016 | 1.008 | ...
  Wtd 5yr  | 1.811 | 1.451 | ... | 1.033 | 1.017 | 1.009 | ...
  ...

LDF Selections
  Rules-Based AI Selection   | 1.809 | 1.449 | ... | 1.032 | (blank) | (blank) | (formula from Tail wb)
  Rules-Based AI Reasoning   | ...   | ...   | ... | "Last LDF. Cutoff: CV=0.08..." | (blank) | (blank) | (formula)
  
  Open-Ended AI Selection    | 1.805 | 1.445 | ... | (blank) | (blank) | (blank) | (formula from Tail wb)
  Open-Ended AI Reasoning    | ...   | ...   | ... | "Last LDF. Cutoff at 72..." | (blank) | (blank) | (formula)
  
  User Selection             | (blank) | (blank) | ... | (blank) | (blank) | (blank) | (blank)
  User Reasoning             | ...   | ...   | ... | ...   | ...   | ...   | ...
```

**Notes:**
- **Cutoff inferred from where selections stop** — no separate column needed
- Rules-Based row stops at 72-84 (implicitly cutoff = 84)
- Open-Ended row stops at 60-72 (implicitly cutoff = 72)
- Different methods have different numbers of populated cells (different cutoffs)
- Last interval's reasoning cell explains cutoff choice
- Tail column still exists, references Tail workbook (curve method selections)
- **Simpler than before**: no extra Cutoff column, data structure itself shows cutoff

**Tail Selection Workbook (Chain Ladder Selections - Tail.xlsx):**

Current structure:
```
Selected LDFs (from CL Excel)
Tail Scenarios (all methods × starting ages)
Tail Factor Selection
  Label | Cutoff Age | Tail Factor | Method | Reasoning
  User  | ...        | ...         | ...    | ...
  RB AI | ...        | ...         | ...    | ...
```
(from CL Excel) — stops at cutoff
  Interval | 12-24 | ... | 72-84 | 84-96 | 96-108 | Cutoff Reasoning
  Rules-Based | 1.809 | ... | 1.032 | (blank) | (blank) | "Cutoff at 84: CV=0.08..."
  Open-Ended  | 1.805 | ... | (blank) | (blank) | (blank) | "Cutoff at 72: ..."
  User        | ...   | ... | ...   | (blank) | (blank) | Reasoning
  Rules-Based | 1.809 | ... | 1.032 | 84 | (pulled from CL Excel)
  Open-Ended  | 1.805 | ... | 1.030 | 72 | (pulled from CL Excel)
  User        | ...   | ... | ...   | ... | (pulled from CL Excel)

All Age-to-Age Factors (observed data)
  Period | 12-24 | 24-36 | ... | 84-96 | 96-108 | ...
  2016   | 1.823 | 1.456 | ... | 1.018 | 1.009  | ...

ATA Statistics (min/max for fit validation)
                    | 84-96  | 96-108 | 108-120 | 120-132 | ...
  Min               | 1.012  | 1.005  | 1.002   | 1.001   | ...
  Max               | 1.021  | 1.012  | 1.008   | 1.004   | ...
  All Years Avg     | 1.0165 | 1.0081 | 1.0048  | 1.0024  | ...
  All Yrs Excl Hi/Lo| 1.0164 | 1.0080 | 1.0047  | 1.0023  | ...
  Weighted All      | 1.0167 | 1.0083 | 1.0050  | 1.0025  | ...
  Wtd Excl Hi/Lo    | 1.0166 | 1.0082 | 1.0049  | 1.0024  | ...
  CV                | 0.045  | 0.038  | 0.042   | 0.051   | ...
  Slope             | -0.02  | -0.01  | -0.008  | -0.005  | ...

Tail Scenarios (fitted on selected LDFs only)
  Method | Starting Age | R² | LOO | Gap | Fitted LDFs | Final CDF | ...
  exp_dev_quick | 84 | 0.91 | 0.0015 | False | {...} | 1.0230 | ...

Curve Method Selection
  Label | Method | Params | Fitted LDFs | Final CDF | Reasoning
  User  | ...    | ...    | {...}       | ...       | ...
  RB AI | exp_dev_quick | D=0.0156,r=0.842 | {...} | 1.0230 | ...
  OE AI | ...    | ...    | {...}       | ...       | ...
```

---

### 5. Script Changes
**None!** Existing column structure works fine.
- Selectors will just populate fewer columns when they have earlier cutoffs
- Script already handles variable-length selection arrays

**No changes needed:**
- Triangle display
- Averages display
- CV/Slope sheets
- Column structure (selections naturally stop where data stops)ed:**
- Triangle display
- Averages display
- CV/Slope sheets

---

#### 2b-chainladder-update-selections.py (LDF selection updater)
****Minimal changes** — JSON is still an array of selections
- Script populates cells for intervals present in JSON (stops naturally when array ends)
- Last interval's reasoning contains cutoff explanation (script treats like any other reasoning)
- **No parsing needed** — script doesn't need to know cutoff age explicitly
- Excel shows cutoff implicitly (where selections stop)

**Logic:**
```python
selections = json.load(f)  # Array of {interval, selection, reasoning}
for sel in selections:
    write_to_excel(sel['interval'], sel['selection'], sel['reasoning'])
# Automatically stops at last interval in array
selections = data.get('selections', [])
  ```

---
from LDF Excel (all three rows: User/RB/OE)
- **Infer cutoff age** from last interval in each selection row:
  ```python
  # Find last populated interval cell in row
  last_interval = find_last_interval_with_value(row)
  cutoff_age = parse_interval_end(last_interval)  # "72-84" → 84
  ```
- For each measure+method combination:
  - Use inferred cutoff age (not all possible starting ages)
  - Extract selected LDFs from start through cutoff (not all observed LDFs)
  - Fit curve on **selected LDFs only**
  - Calculate fitted LDFs for ages beyond cutoff (84-96, 96-108, ..., until development negligible)
  - Calculate final CDF at cutoff age using curve's infinite-horizon formula
  - Store fitted_ldfs dict and final_cdf in scenario output
- Remove "starting_age" loop (use inferreds beyond cutoff (84-96, 96-108, ..., until development negligible)
  - Calculate final CDF at cutoff age using curve's infinite-horizon formula
  - Store fitted_ldfs dict and final_cdf in scenario output
- Remove "starting_age" loop (use cutoff from LDF selections instead)
- Add ATA factor statistics (min/max/avg) to scenario output for validation

**New scenario output columns:**
```
measure | method | cutoff_age | fitted_ldfs | final_cdf | method_params | r_squared | loo_std | gap_flag | ...
```

**Curve-specific CDF calculations:**
See `examples/ken-tail-factor/tail-factor/p01_tail_math.py` for examples:
- **exp_dev_quick**: sum first K terms, then geometric series for remainder
- **exp_dev_product**: product until dev < 1e-6
- **double_exp**: numefrom LDF Excel (all three rows)
- **Infer cutoff** from last populated interval in each row (same logic as 2c)
- Display selected LDFs (stops at cutoff naturally — just copy intervals from CL Excel)
- Add "Cutoff Reasoning" column showing last interval's reasoning from CL Excel
- Add "All Age-to-Age Factors" section (all observed ATA data)
- Add "ATA Statistics" section (min/max/avg/CV/slope per interval)
- Update scenario table to show fitted_ldfs and final_cdf (not just single tail_factor)
- Update selection area columns:
  ```
  Label | Method | Method Params | Fitted LDFs | Final CDF | Reasoning
  ```
- No separate "Cutoff Age" column needed (inferred from where LDF selections stopws)
- Display selected LDFs + cutoff in new section at top
- Add "All Age-to-Age Factors" section (all observed ATA data)
- Add "ATA Statistics" section (min/max/avg/CV/slope per interval)
- Update scenario table to show fitted_ldfs and final_cdf (not just single tail_factor)
- Update selection area columns:
  ```
  Label | Method | Method Params | Fitted LDFs | Final CDF | Reasoning
  ```
- Remove "Cutoff Age" column (comes from LDF selections now)

**MD context export:**
- Include all ATA factors
- Include selected LDFs + cutoff
- Include ATA statistics
- Include scenarios with fitted_ldfs and final_cdf

---

#### 2e-tail-update-selections.py
**Changes:**
- Read new JSON formatfrom LDF Excel (prioritize User > RB > OE)
- **Infer cutoff** from last interval in selected row: `parse_interval_end(last_interval)`
- Read tail selections (method + fitted_ldfs + final_cdf) from Tail Excel
- Build CDF using:
  - Selected LDFs up to cutoff age
  - Fitted LDFs from tail curve after cutoff age
  - Final CDF at cutoff age as anchor
- Track which LDFs come from selection vs tail curve (for Analysis display)

**CDF building logic:**
```python
# Read selections and infer cutoff
selections = read_ldf_selections(excel, measure)  # [{interval, ldf}, ...]
last_interval = selections[-1]['interval']  # "72-84"
cutoff_age = int(last_interval.split('-')[1])  # 84

# Get fitted LDFs from tail
fitted_ldfs = tail_data['fitted_ldfs']  # {"84-96": 1.0167, ...}

# Build CDF
ages = [12, 24, 36, 48, 60, 72, 84, 96, 108, ...]
cdf_at_cutoff = tail_data['final_cdf']  # e.g., 1.0230
cdfs = {cutoff_age: cdf_at_cutoff}

# Work backwards through selected LDFs
for sel in reversed(selections):
    start, end = parse_interval(sel['interval'])
    cdfs[start] = sel['ldf'] * cdfs[end]

# Work forwards through fitted LDFs (for display/validation only)
for interval, ldf in sorted(fitted_ldfs.items()):
    start, end = parse_interval(interval)
    if start >= cutoff_age:
        cdfs[start] = ldf * cdfs[end]
        continue
    interval = f"{age}-{age+12}"
    ldf = selected_ldfs.get(interval, 1.0)
    cdfs[age] = ldf * cdfs[age + 12]

# Work forwards through fitted LDFs (for display/validation only)
for interval, ldf in sorted(fitted_ldfs.items()):
    # Parse interval to get ages
    start, end = parse_interval(interval)
    if start >= cutoff_age:
        cdfs[start] = cdfs.get(end, 1.0) * ldf
```

---

#### 6-analysis-create-excel.py
**Changes:**
- Read LDF selections + cutoff from LDF Excel
- Read tail selections (fitted_ldfs) from Tail Excel
- In Analysis triangle sheets:
  - Show selected LDFs up to cutoff (normal cells)
  - Show fitted LDFs after cutoff (different formatting/color to distinguish)
  - Add visual marker (border/color/note) at cutoff age column
  - CDF row shows full chain (selected LDFs × fitted LDFs × final CDF)
- Update `add_tail_to_triangle_ws` function:
  - Instead of deleting columns beyond cutoff, keep them
  - Populate them with fitted LDFs from tail curve
  - Format differently (e.g., italic, different color) to show they're from curve not selection
  - Add column header notes: "84-96*" where * indicates "from tail curve"

**Visual distinction example:**
```
LDF Selections
  Selected       | 1.809 | 1.449 | ... | 1.032 | 1.017* | 1.008* | CDF
  Reasoning      | ...   | ...   | ... | Last  | Tail   | Tail   | 1.023
                                         ↑ cutoff
```

---

### 6. Selector Agent Changes

#### selector-chain-ladder-ldf-ai-rules-based.agent.md
**Changes:**
- Add new section: "Cutoff Age Selection"
- Cutoff criteria (move from tail selector):
  - Monotonic from cutoff onward
  - CV at cutoff < 0.15 (prefer < 0.10)
  - No slope sign changes from cutoff onward
  - At least 3-5 factors remaining after cutoff for curve fit
  - Type-specific minimums (Paid/Closed: ≥60, Incurred/Reported: ≥48)
- **Output format**: Array stops at cutoff interval (no separate cutoff field)
- **Last interval reasoning** must explain cutoff choice

**Prompt addition:**
```markdown
## Cutoff Age Selection

After selecting LDFs for each interval, you must also determine where to stop (the cutoff age).

**Your task:**
- Select LDFs for intervals where observed factors are credible
- Stop at the interval where tail curve should begin
- **Output format**: Array of selections that stops at the cutoff interval
- Last interval's reasoning must explain **why** it's the cutoff

**Cutoff criteria:**
1. **Monotonic decay** from cutoff onward (`is_monotone_from_cutoff = True`)
2. **Low variance** at cutoff (CV < 0.15, prefer < 0.10)
3. **No structural breaks** from cutoff onward (slope_sign_changes = 0)
4. **Sufficient tail factors** for curve fit (≥ 3-5 intervals remaining after cutoff)
5. **Type-specific minimum:**
   - Paid Loss / Closed Count: ≥ 60 months
   - Incurred Loss / Reported Count: ≥ 48 months

**Example output:**
```json
[
  {"interval": "12-24", "selection": 1.6573, "reasoning": "Weighted 3yr average: most credible balance of recent trend and stability"},
  {"interval": "24-36", "selection": 1.2341, "reasoning": "Geometric average: CV=0.05, minimal volatility"},
  ...
  {"interval": "72-84", "selection": 1.0150, "reasoning": "Last credible LDF: CV=0.08, monotonic, stable pattern"},
  {"interval": "84-96", "reasoning": "CUTOFF at 84 months: is_monotone_from_here=True, CV beyond=0.08, slope_sign_changes=0, 5 factors remaining for curve fit. Rejected 96+ due to CV>0.15 and non-monotonic pattern."}
]
```

**Important:** 
- Last selected interval (e.g., "72-84") has normal LDF reasoning
- Next interval (e.g., "84-96") has NO selection value, only cutoff reasoning
- Array stops after cutoff reasoning interval
```

---

#### selector-chain-ladder-ldf-ai-open-ended.agent.md
**Changes:**
- Explain requirement to select cutoff (using professional judgment, not rigid rules)
- **Output format**: Last selected interval + one more interval with cutoff reasoning only
- Emphasize holistic assessment of where credible pattern ends and tail curve should begin
- No specific criteria checklist (that's for rules-based) - use actuarial judgment

**Prompt guidance:**
```markdown
## Cutoff Selection

You must determine where to stop selecting LDFs and let the tail curve take over.

**Output format:**
- Last selected interval: has `selection` value + reasoning about that LDF
- Next interval: NO selection value, only reasoning explaining cutoff choice

**Use professional judgment to assess:**
- Where observed pattern becomes too unstable for credible selection
- Where data volume/credibility diminishes significantly  
- Where tail curve fitting would be more appropriate than direct selection
- Balance between observed data and extrapolation needs

**Example:**
```json
[
  ...
  {"interval": "72-84", "selection": 1.015, "reasoning": "Last credible observation: reasonable CV, stable pattern"},
  {"interval": "84-96", "reasoning": "Cutoff at 84: Beyond this point, sparse data and high variance make tail curve more reliable than direct factor selection."}
]
```
```

---

#### selector-tail-factor-ai-rules-based.agent.md
**Changes:**
- Remove "Starting Point Selection" section (cutoff now from LDF selections)
- Remove cutoff_age from output (comes from LDF selections)
- Add fitted_ldfs and final_cdf to output
- Input now includes all ATA factors + selected LDFs + cutoff age
- Update "Fit Diagnostics" section:
  - Fitted values should stay within [min, max] of observed ATA factors
  - Curves fitted on selected LDFs only (not all observed)
- Update "Gap Rule":
  - Gap measured between fitted curve at cutoff vs last selected LDF at cutoff
  - `abs(fitted_at_cutoff - selected_at_cutoff) > 0.005` → reject
- Add section: "Final CDF Calculation"
  - Each method must calculate CDF at cutoff age (infinite-horizon development)
  - Document formula used (exp_dev: geometric series, double_exp: numerical integration, etc.)

**Prompt changes:**
```markdown
## Input Data

You will receive:
1. **All observed age-to-age factors** (for fit quality assessment)
2. **Selected LDFs** from LDF Excel (Rules-Based AI / Open-Ended AI / User)
3. **Selected cutoff age** from LDF selections
4. **ATA statistics** (min, max, avg, CV, slope per interval)
5. **Tail scenarios** with fitted LDFs and final CDF per method

## Task

For each measure:
1. Read selected LDFs and cutoff age (use Rules-Based if User not present)
2. Evaluate curve fit quality (R², LOO, residuals, gap)
3. Validate fitted LDFs stay within [min, max] of observed ATA factors
4. Select best method based on diagnostics
5. Return method + method_params + fitted_ldfs + final_cdf

## Output Format

```json
[
  {
    "measure": "Incurred Loss",
    "method": "exp_dev_quick",
    "method_params": {"D": 0.0156, "r": 0.842},
    "fitted_ldfs": {
      "84-96": 1.0167,
      "96-108": 1.0084,
      "108-120": 1.0042
    },
    "final_cdf_at_cutoff": 1.0230,
    "reasoning": "..."
  }
]
```

## Gap Rule (Updated)

**Gap** = `abs(fitted_ldf_at_cutoff - last_selected_ldf)` where:
- `fitted_ldf_at_cutoff` = first LDF from fitted curve (e.g., fitted value for 84-96 interval)
- `last_selected_ldf` = last LDF in selected sequence (e.g., selected LDF for 72-84)

If gap > 0.005, **reject this method** (disconnected from selected pattern).

## Fitted LDF Validation

Fitted LDFs should stay within [min, max] range of observed ATA factors. If fitted LDF falls outside observed range by >10%, flag as "extrapolation risk" in reasoning.
```

---

#### selector-tail-factor-ai-open-ended.agent.md
**Changes:**
- Same as rules-based (remove cutoff selection, update output format)

---

### 7. Testing Strategy

#### Unit tests (if test framework exists):
1. Test LDF selector output format parsing
2. Test tail selector output format parsing
3. Test CDF building with mixed selected + fitted LDFs
4. Test curve CDF calculations (exp_dev, double_exp, etc.)

#### Integration tests (sample-data/sample-run):
1. Run full workflow with new structure
2. Verify LDF Excel has Cutoff column populated correctly
3. Verify Tail Excel shows fitted LDFs (not just single tail factor)
4. Verify Analysis Excel distinguishes selected vs fitted LDFs
5. Verify ultimates match (CDF calc using new structure)

#### Validation checks:
1. Cutoff ages should vary by method (RB vs OE vs User)
2. Fitted LDFs should extend beyond cutoff (84-96, 96-108, ...)
3. Final CDF should match product of selected LDFs × fitted LDFs
4. Gap rule should reject curves that disconnect from selected pattern
5. Each measure should have different cutoff (Paid > Incurred > Reported Count)

---

## Edge Cases to Handle

1. **User overrides cutoff in LDF Excel but not in Tail Excel:**
   - Tail Excel reads cutoff from LDF Excel (handles automatically)

2. **Different selection methods have different cutoffs:**
   - Each row in Tail Excel fits curves using that row's cutoff from LDF Excel
   - Analysis uses User > RB > OE priority for both LDF and tail selections

3. **Cutoff age = last observable age (no tail curve needed):**
   - Tail selector returns method="none", fitted_ldfs={}, final_cdf=1.0
   - Analysis treats as "no tail" scenario

4. **Curve fit fails at selected cutoff:**
   - Tail selector returns error/warning in reasoning
   - Falls back to Bondy or modified_bondy
   - Document in reasoning: "Curve fits failed; using Bondy (last selected LDF)"

5. **Fitted LDF falls outside observed [min, max]:**
   - Flag in tail selector reasoning: "Extrapolation risk: fitted 84-96=1.022 exceeds observed max=1.018"
   - Actuary can review and override if needed

6. **No selected LDFs after cutoff (cutoff = last observable age):**
   - Valid scenario (mature triangle, no tail development)
   - Tail selector returns final_cdf = last_selected_ldf or 1.0

---

## Backwards Compatibility

- Breaking change — old JSON files will not work
- Migration: Re-run selectors on existing data
- Save backup of old Excel files before re-running 2a-2f

---

## Documentation Updates

1. **PROGRESS.md**: Update Step 4 and Step 5 descriptions
2. **SKILL.md** (reserving-analysis): Update workflow description
3. **Selector agent docs**: Update all four selector .agent.md files
4. **METHOD.md** (chain-ladder): Update JSON format examples
5. **CODEBASE-SUMMARY.md**: Update script descriptions

---

## Key Files to Modify
6 files — one less than before!):
1. ~~`skills/reserving-analysis/scripts/2a-chainladder-create-excel.py`~~ **(NO CHANGES NEEDED!)**
2. `skills/reserving-analysis/scripts/2b-chainladder-update-selections.py` **(minimal changes)**
3. `skills/reserving-analysis/scripts/2c-tail-methods-diagnostics.py`
4. `skills/reserving-analysis/scripts/2d-tail-create-excel.py`
5. `skills/reserving-analysis/scripts/2e-tail-update-selections.py`
6. `skills/reserving-analysis/scripts/2f-chainladder-ultimates.py`
7. `skills/reserving-analysis/scripts/6-analysis-create-excel.py`

### Helper Functions (new):
- Add `infer_cutoff_from_selections()` to `modules/` (see Architecture Changes section 1 for implementation)

### Scripts (6 files):
1. ~~`skills/reserving-analysis/scripts/2a-chainladder-create-excel.py`~~ **(NO CHANGES)**
2. `skills/reserving-analysis/scripts/2b-chainladder-update-selections.py` **(minimal)**
3. `skills/reserving-analysis/scripts/2c-tail-methods-diagnostics.py`
4. `skills/reserving-analysis/scripts/2d-tail-create-excel.py`
5. `skills/reserving-analysis/scripts/2e-tail-update-selections.py`
6. `skills/reserving-analysis/scripts/2f-chainladder-ultimates.py`
7. `skills/reserving-analysis/scripts/6-analysis-create-excel.py`

### Agents (4 files):
1. `skills/reserving-analysis/agents/selector-chain-ladder-ldf-ai-rules-based.agent.md`
2. `skills/reserving-analysis/agents/selector-chain-ladder-ldf-ai-open-ended.agent.md`
3. `skills/reserving-analysis/agents/selector-tail-factor-ai-rules-based.agent.md`
4. `skills/reserving-analysis/agents/selector-tail-factor-ai-open-ended.agent.md`

### Workflow (2 files):
1. `skills/reserving-analysis/assets/PROGRESS.md`
2. `sample-data/sample-run/PROGRESS.md`

### Documentation (optional):
1. `examples/methods/chain-ladder/METHOD.md`
2. `examples/CODEBASE-SUMMARY.md`

---

## Risks and Mitigations

### Risk: Selectors pick bad cutoffs
**Mitigation:**
- User can override in Excel
- Show cutoff reasoning prominently
- Validate cutoff meets minimum criteria (monotonic, low CV, etc.)

### Risk: Fitted LDFs diverge from observed
**Mitigation:**
- Show min/max of observed ATA factors in Tail Excel
- Tail selector validates fitted values stay within range
- Flag extrapolation risk in reasoning

### Risk: Final CDF calculation errors
**Mitigation:**
- Use established formulas from ken-tail-factor examples
- Unit test each curve's CDF calculation
- Compare to current system results (should match when same cutoff/method)

### Risk: Breaking existing analyses
**Mitigation:**
- Clear migration path (re-run selectors)
- Document changes prominently
- Version the workflow (old = v1, new = v2)

---

---

## Next Steps

1. Review with stakeholders (all design questions resolved)
2. **Start Phase 1** implementation (see Progress Checklist)
3. Test thoroughly between phases
4. Document deviations from plan
