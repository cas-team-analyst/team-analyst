---
name: chain-ladder-ldf-selector
description: Selects loss development factors (LDF) for the chain-ladder reserving method
model: opus
maxTurns: 1
---

Use the logic below to make selections for loss development factors (LDFs) for the chain-ladder reserving method. Do not write a script to make selections (the logic is too diverse to capture in a script), instead you will receive the applicable data as text, then read the selection method logic reference, and finally choose an average or a weighted average of available averages. 

Return JSON with your selection and your logic like "{selection: 1.6573, reasoning: 'Selected 5-year volume-weighted average excluding high/low because CV was 0.12, indicating moderate variability, and the latest diagonal was not an outlier.'}".


# Master Selection Logic Reference

This is our starting point for capturing logic when making actuarial selections. 

Actuaries often have slightly different strategies, so ideally this is combined with a personal strategy, but in the absence of that strategy this can be used alone.

## Chain Ladder LDF Selection Logic

This is our starting point for capturing logic when selecting age-to-age factors in the chain ladder method. It applies to both paid and incurred development triangles.

Actuaries often have slightly different strategies, so ideally this is combined with a personal strategy, but in the absence of that strategy this can be used alone.

### The Core Selection Criteria

#### 1. Outlier Handling (Exclude High/Low)

Where there is significant variability in a particular age-to-age column, use averages that exclude the high and low values. This reduces the influence of extreme LDFs that may not reflect typical development.

- **Trigger:** Use excluding-high/low averages when the coefficient of variation (CV) of a column's age-to-age factors exceeds **0.10** (i.e., standard deviation > 10% of the mean LDF).
- **Mild variability (CV 0.10–0.20):** Exclude only the single highest and lowest LDFs, then average the remainder.
- **High variability (CV > 0.20):** Exclude the top and bottom **two** LDFs if you have 7+ data points. If fewer than 7 points, exclude one each and flag the column as low-credibility.
- **Identifying the outlier cause:** Before excluding, check whether the outlier AY corresponds to a known event (large loss, reserve study, portfolio change). If it does, the exclusion is justified and should be documented. If the cause is unknown, still exclude but note it for investigation.
- **Never exclude more than 30%** of available data points in a single column. If that much data looks anomalous, the "outliers" may actually be the new pattern — see Criterion 6 (Trending).
- **Interaction with recency:** If the outlier is the most recent diagonal, see Criterion 5 (Latest-Point Outlier Exception) before excluding.

#### 2. Recency Preference

More recent age-to-age factors are preferable to longer-term averages because they better reflect current conditions — newer claims handling philosophies, technology, and operational practices. In large triangles, avoid all-years averages entirely, as older LDFs may represent materially different environments (different adjuster philosophies, pre-technology era, etc.).

- **Default averaging window:** 5-year volume-weighted average.
- **Use 3-year average when:**
  - Diagnostics show a clear regime change in the last 3 years (e.g., closure rate shift >5pp, case reserve philosophy change >15%).
  - A known operational change occurred (new TPA, new claims system, new reserving guidelines) and pre-change development patterns are no longer representative.
  - The 3-year and 5-year LDF averages diverge by more than **3%** — the divergence itself signals that older data is pulling in a different direction.
- **Use 7-year or all-year average when:**
  - Annual claim counts are below **50** per accident year (see Criterion 7, Sparse Data).
  - The line is long-tail (e.g., WC, umbrella, med mal) and development ages are 60+ months — longer windows smooth LDF volatility at thin maturities.
  - All recent averages (3-year, 5-year) have high variability (CV > 0.15) and no clear trend — the additional data adds stability without introducing bias.
- **Never use all-year averages** when the triangle spans more than 10 years, unless claim counts are very thin. Development patterns from a decade ago are almost certainly non-representative.
- **Volume-weighted vs. simple average:** Default to volume-weighted. Switch to simple average only when a single large AY dominates the volume (>40% of total column exposure) and you want to prevent it from dictating the LDF selection.

#### 3. Asymmetric Conservatism

Actuaries lean conservative (better to over-estimate reserves than under-estimate). When LDFs are trending downward, be slower to react. When LDFs are trending upward, respond faster.

- **Upward movement (data suggests higher LDF than current selection):**
  - If the preferred average exceeds the prior selected LDF by **>3%:** Move **60–80%** of the distance toward the data.
  - If the preferred average exceeds the prior by **>10%:** Move **80–100%** of the distance. At this level the data is strongly signaling.
  - Always cross-check with the diagnostic framework before making large upward moves — confirm the signal is real (e.g., paid and incurred triangles both showing higher factors).
- **Downward movement (data suggests lower LDF than current selection):**
  - If the preferred average is below the prior by **3–10%:** Move only **30–50%** of the distance. Wait for another study to confirm before fully committing.
  - If the preferred average is below the prior by **>10%:** Move **50–70%** of the distance. Even with a strong downward signal, retain some conservatism.
  - Exception: If the downward movement is supported by **converged averages** (Criterion 8) and **paid-to-incurred diagnostics** confirm reserve redundancy, move the full distance.
- **Rationale for asymmetry:** Under-reserving creates solvency risk and regulatory exposure. Over-reserving ties up capital but is correctable. The cost of the two errors is not symmetric.
- **Maturity adjustment:** Asymmetric conservatism should be **strongest at early maturities** (12–36 months) where uncertainty is highest, and can be **relaxed at late maturities** (60+ months) where development is more predictable and over-reserving has real capital cost.

#### 4. Bayesian Anchoring to Prior Selection

Use the prior selected LDF (if available) as an anchor to avoid wild swings between studies. The latest diagonal point is new information, but how much you move off the prior depends on how consistent that new point is with recent history.

- **Prior is within ±2% of the preferred average:** Stay with the prior. The new data confirms it.
- **Preferred average is 2–5% above the prior:**
  - Check whether the latest 2–3 diagonals are all above the prior, or just the most recent one.
  - If multiple diagonals confirm: raise the selection by **50–75%** of the gap.
  - If only the latest diagonal is high: raise by **25–40%** of the gap (may be noise).
- **Preferred average is 2–5% below the prior:**
  - Apply asymmetric conservatism: lower by only **25–50%** of the gap.
  - Require confirmation from the next study before moving further.
- **Preferred average is >5% different from the prior:** This is a material move. Before adjusting:
  - Confirm with at least two diagnostics (e.g., severity trend + closure rate).
  - Check whether a structural change explains the shift (operational, legal, portfolio).
  - If confirmed, move per the asymmetric conservatism rules above.
  - If not confirmed, hold closer to the prior and document the flag.
- **Explicit weighting approach (optional):** When uncertainty is high, blend: `Selected LDF = (W × Prior) + ((1 − W) × Preferred Average)` where W = 0.4–0.6 depending on confidence in the new data. Lower W (less prior weight) when diagnostics strongly support the new level.
- **When to abandon the prior entirely:** See Criterion 8 (Convergence Override). Also abandon if the prior was itself a placeholder or low-confidence selection from a prior study.

#### 5. Latest-Point Outlier Exception *(Override of Bayesian)*

If the latest diagonal LDF is very different from the past 5–10 points, treat it as a likely outlier caused by unusual single-claim development. Do not give it outsized weight; instead rely on the averages and the prior.

- **Definition of "very different":** The latest age-to-age factor deviates from the column's 5-year average by more than **1.5 standard deviations** or **>15%**, whichever threshold is reached first.
- **Before excluding, check for cause:**
  - Run the incremental diagnostics (`incremental_incurred_severity`, `paid_severity_incr`, `incremental_closure_rate`) for that development interval.
  - If `paid_severity_incr` also spikes by >15% → likely a real large loss, not a reserving artifact. Consider capping its influence rather than fully excluding.
  - If `paid_severity_incr` is normal but `incremental_incurred_severity` spikes → case reserve posting. Exclude from incurred LDF average; rely on the paid triangle's LDFs for that column.
  - If `incremental_closure_rate` is abnormal → settlement timing distortion. The development may emerge in the next interval rather than being permanently higher/lower.
- **If confirmed as outlier:**
  - Exclude from the averaging window for that column.
  - Select based on the remaining averages and the prior.
  - Document the exclusion and the dollar impact on ultimates.
- **If ambiguous (could be real):**
  - Include in the average but use a **blended selection** (Criterion 4 weighting approach) that limits its pull.
  - Flag for monitoring at the next study. If the next diagonal confirms the level, reclassify as a trend rather than an outlier.
- **Consecutive outliers:** If the latest **two** diagonal LDFs are both >15% away from prior history in the same direction, this is no longer an outlier — it's a potential regime change. Shift to Criterion 6 (Trending).

#### 6. Trending

If the most recent 3–4 age-to-age factors are trending consistently in one direction relative to earlier points, a new development level may be emerging. Do not move the full distance in one step, but begin moving in that direction.

- **Identifying a trend vs. noise:**
  - A trend requires **3+ consecutive LDFs** moving in the same direction relative to the long-term average, OR a statistically significant slope (p < 0.10 on a simple linear regression of the column's LDFs over time).
  - A single high or low point followed by a return to normal is **not** a trend. Two consecutive points in the same direction are suggestive but not confirmatory.
- **Quantifying the trend:**
  - Compute the 3-year average and the 5-year average for the column. If the 3-year is more than **3%** different from the 5-year, a trend is likely present.
  - Compute the annualized rate of change across the last 3–4 diagonals.
- **Responding to a confirmed trend:**
  - **Mild trend (3-yr vs. 5-yr divergence of 3–5%):** Weight the 3-year average at **60%** and the 5-year at **40%** in your LDF selection.
  - **Strong trend (divergence >5%):** Weight the 3-year average at **75–100%**. The older data is no longer representative.
  - **Accelerating trend (each successive LDF further from the prior):** Consider whether the 3-year average itself is lagging. Use the latest 2-year average or apply an explicit trend factor to project forward.
- **Cross-check with diagnostics:** A trend in LDFs should be explainable by at least one diagnostic:
  - Rising LDFs + rising `incurred_severity` → severity inflation.
  - Rising LDFs + slowing `closure_rate` → payment delays stretching development.
  - Falling LDFs + rising `closure_rate` → faster settlement pulling development forward.
  - If no diagnostic supports the trend, treat it with skepticism — it may be noise that happens to be serially correlated.
- **Trend vs. level shift:** If the trend plateaus (last 2 LDFs are stable at the new level), stop trending and lock in the new level as your selection.

#### 7. Sparse Data

When data is thin, individual age-to-age factors are unreliable and selections should lean on stability over responsiveness.

- **Thresholds for "sparse":**
  - Fewer than **50 reported claims** per accident year at the relevant maturity.
  - Average incurred losses less than **$1M per AY** for accident years older than 24 months.
  - Fewer than **5 LDFs** available in a column (i.e., triangle has fewer than 5 complete AYs at that development age).
- **Adjustments for sparse data:**
  - **Widen the averaging window:** Use 7-year or all-year averages rather than 3- or 5-year.
  - **Increase prior anchoring:** Weight the prior selection more heavily (60–70%) relative to the current data.
  - **Reduce sensitivity to trends:** Require 4+ consecutive points (rather than 3) to confirm a trend. Sparse data trends are often noise.
  - **Lean on paid over incurred:** With fewer claims, individual large case reserve changes have outsized impact on incurred LDFs. Paid triangle LDFs are more stable in sparse books.
  - **Consider external benchmarks:** If the book is very small (<25 claims per AY), industry development patterns or sister-company triangles may be more credible than the entity's own. Blend internal and external LDFs.
- **Interaction with outlier handling:** In sparse columns, excluding high/low may remove too much data. If exclusion leaves fewer than **4 data points**, use the full dataset and instead apply a trimmed mean (cap extreme LDFs at the 10th/90th percentile rather than excluding).

#### 8. Convergence Override

If all the LDF averages (3-year, 5-year, 7-year, all-year, excluding-high/low) are in a tight range and are collectively and materially different from the prior selection, override the prior and select from those converged averages. The data has spoken clearly enough to move.

- **Definition of convergence:** All standard averages fall within a **±2%** band of each other.
- **Definition of "materially different from prior":** The center of the converged band differs from the prior by more than **3%**.
- **Action:**
  - Select at or near the **midpoint of the converged band**.
  - No need to apply asymmetric conservatism or Bayesian anchoring — convergence across all averaging methods is the strongest possible signal.
  - Document that convergence override was applied and note the prior vs. new selection.
- **Partial convergence:** If most averages converge but one is an outlier (e.g., all-year average is different because of very old data), ignore the non-converging average and assess convergence among the rest.
- **Convergence pointing downward:** Even in this case, move the full distance. Convergence is the one scenario that overrides asymmetric conservatism. The reasoning: every reasonable cut of the data agrees, making it highly unlikely the prior is correct.

#### 9. Maturity-Dependent Behavior

The relative importance of each criterion shifts as you move across the triangle from early to late development ages.

- **Early maturities (12–36 months):**
  - LDFs are large and volatile. Small percentage changes in the factor translate to large dollar swings in ultimate estimates.
  - **Emphasize:** Asymmetric conservatism (Criterion 3), diagnostics cross-checks, and Bayesian anchoring.
  - **De-emphasize:** Outlier exclusion (variance is naturally high at early ages — many LDFs that look like outliers are normal).
  - **Averaging window:** 5-year volume-weighted preferred. Avoid 3-year unless a clear regime change is documented.
  - **Triangle preference:** Incurred triangle LDFs are typically more stable than paid at early ages (paid is lumpy due to settlement timing). But if `average_case_reserve` diagnostics flag case reserving changes, give more credence to paid triangle LDFs.
- **Mid maturities (36–72 months):**
  - LDFs are moderate and most diagnostics are at their most informative.
  - **Emphasize:** Trending (Criterion 6) and convergence (Criterion 8). This is where persistent shifts become visible.
  - **Averaging window:** 5-year default; 3-year if trending is confirmed.
  - **Triangle preference:** Paid and incurred LDFs should be producing similar indications. If they diverge by >5%, use diagnostics to determine which triangle's factors are more reliable.
- **Late maturities (72+ months):**
  - LDFs are close to 1.000. Small absolute changes matter for tail adequacy.
  - **Emphasize:** Sparse data handling (Criterion 7), open count monitoring, tail factor adequacy.
  - **De-emphasize:** Recency preference (there may not be enough recent data at late ages to form a credible recent average).
  - **Averaging window:** All-year or longest available, unless a structural break is documented.
  - **Tail factor:** If selected LDFs at the last observable maturity still show development >1.005, a tail factor is needed. Use benchmark patterns, inverse power curve fit, or McClenahan method — do not simply select 1.000 unless supported by `open_counts` and `closure_rate` diagnostics showing near-complete runoff.

#### 10. Paid vs. Incurred Triangle Consistency

When developing both paid and incurred triangles, comparing LDF selections across the two provides an important cross-check on the reasonableness of each set of factors.

- **Expected behavior:** At early maturities, incurred LDFs are typically lower than paid LDFs (case reserves front-load incurred recognition). At later maturities, the two should converge.
- **Divergence > 5% at any maturity — investigate:**
  - Check `paid_to_incurred` ratio at that maturity. If it's moving away from the historical benchmark, one triangle is developing abnormally.
  - Check `average_case_reserve`. If case reserves are changing materially, incurred LDFs are being distorted — trust the paid triangle's factors at that column.
  - Check `paid_severity_incr`. If paid increments are erratic (large lump-sum settlements), the paid triangle's LDFs are noisy — trust the incurred triangle's factors at that column.
- **When selecting from one triangle to inform the other:**
  - If incurred LDFs at a column are clearly distorted by case reserving, select the incurred LDF by reference to the paid LDF at that column plus an expected case reserve emergence margin.
  - If paid LDFs at a column are distorted by large-loss settlements, select the paid LDF by reference to the incurred LDF minus the expected case reserve release at that age.
- **Document the cross-check.** Note where the two triangles agree (confirming the selection) and where they disagree (and which you gave more weight to and why).

#### 11. Negative or Sub-1.000 Development

Occasionally, age-to-age factors will be less than 1.000 (negative incremental development). This requires special handling.

- **At early maturities (12–36 months):** Sub-1.000 LDFs are almost always anomalous. They typically indicate reserve takedowns, salvage/subrogation recoveries, or data corrections. **Do not select a sub-1.000 LDF** at early ages. Select at minimum 1.000 or use the prior.
- **At mid maturities (36–72 months):** Sub-1.000 incurred LDFs can occur legitimately from favorable case reserve development. Investigate:
  - If `paid_severity` is still increasing → the favorable incurred development is just case reserve releases. Select the incurred LDF at minimum 1.000 and use the paid triangle's factor for that column as the primary indication.
  - If `paid_severity` is also flat or declining → genuine favorable. Consider selecting slightly below 1.000, but never more than **0.995** without strong multi-year confirmation.
- **At late maturities (72+ months):** Mild negative development (0.995–1.000) is plausible for well-reserved books experiencing salvage, subrogation, or final reserve closures. Select based on the sustained average, not a single point.
- **For paid triangles:** Sub-1.000 paid LDFs should **never** be selected. They indicate data issues (negative payments, corrections, or recoveries booked against prior periods). Investigate and correct the data, or select 1.000.

#### 12. Large Loss Handling

Large individual claims can distort age-to-age factors, especially in low-frequency lines.

- **Identification:** A claim is "large" if it represents more than **10%** of the total column's incremental development, or if removing it would change the column's LDF by more than **5%**.
- **When a large loss distorts a column:**
  - Compute the LDF **with and without** the large loss.
  - If the difference is >5%, use the excluding-large-loss LDF as your primary indication and add back a **large loss load** based on long-term expected large loss frequency and severity.
  - This is preferable to simply including the loss (which overstates development) or excluding it (which understates it).
- **Interaction with diagnostics:** A spike in `paid_severity_incr` or `incremental_incurred_severity` that is traceable to a single claim is a large loss signal. Cross-check with `reported_counts` — if counts are normal but severity spikes, it's a large loss, not a frequency change.
- **Lines most affected:** Excess/umbrella, commercial auto liability, D&O, professional liability. For these lines, consider developing triangles net of large losses as a standard practice and loading separately.

#### 13. Calendar Year Effects

Diagonal patterns in the triangle can reveal calendar-year influences (e.g., a reserve study, legislative change, or inflation spike) that affect all AYs simultaneously and distort multiple LDF columns at once.

- **Detection:** If the latest diagonal's LDFs are consistently high (or low) across **3+ development columns**, a calendar-year effect is likely. Individual column analysis would misattribute this as multiple independent trends.
- **Common causes:** Bulk reserve reviews, changes in claim staff or philosophy, legal environment shifts (tort reform, social inflation), economic inflation.
- **Handling:**
  - Identify which diagonals are affected.
  - If the effect is **one-time** (e.g., a single reserve study): exclude that diagonal from all column averages and rely on surrounding diagonals.
  - If the effect is **ongoing** (e.g., social inflation): treat as a trend (Criterion 6) across columns. Weight recent diagonals more heavily in all columns simultaneously.
- **Cross-check:** `average_case_reserve` changing uniformly across AYs in the same calendar period is the strongest signal of a calendar-year reserving action.

#### 14. Tail Factor Selection

The tail factor extends development beyond the last observable age-to-age interval. It is the most judgment-intensive LDF in the chain and deserves its own criterion.

- **When a tail is needed:** If the LDF at the last observable maturity is **>1.005** on incurred or **>1.010** on paid, residual development exists and a tail factor must be selected.
- **When a tail of 1.000 is defensible:** `open_counts` at the last maturity are <**2%** of reported counts, `claim_closure_rate` exceeds **97%**, and the last 3 observable LDFs are all within **0.002** of 1.000.
- **Methods for selecting the tail:**
  - **Extrapolation of decay:** Fit an exponential or inverse power curve to the last 3–5 observable LDFs and extrapolate. This assumes the rate of development decay continues.
  - **Industry/benchmark comparison:** Compare your triangle's development at the last observable age to an industry benchmark. If industry shows X% remaining development beyond that age, apply it as a starting point.
  - **Incurred vs. paid tail relationship:** The paid tail should almost always be **≥** the incurred tail. If your paid tail is lower, something is inconsistent — paid takes longer to run off than incurred.
- **Diagnostic checks on tail adequacy:**
  - If `open_counts` at the last maturity are higher than historical norms by >10%, the tail should be **increased** by +0.005–0.015.
  - If `average_case_reserve` on remaining open claims is rising at late maturities, there is unrealized development. Increase the incurred tail.
  - If `paid_to_incurred` at the last maturity is below historical benchmarks, paid has further to run. Increase the paid tail.
- **Minimum tail guidance:** For long-tail casualty lines, rarely select a tail below **1.010** on paid or **1.005** on incurred unless the triangle extends to 120+ months with very strong closure diagnostics.

#### 15. Documentation and Audit Trail

Every LDF selection should be traceable. This is not optional — it protects the actuary, supports peer review, and enables consistency across studies.

- **For each development column, record:**
  - The selected LDF and the averaging method used (e.g., "5-year volume-weighted excluding high/low").
  - Which criteria from this framework were applied and which were considered but not triggered.
  - Any diagnostic flags that influenced the selection (reference the diagnostic by name and threshold).
  - The prior selected LDF and the reason for any change (or the reason for holding).
  - The dollar impact on ultimate losses of the selection change vs. holding the prior.
- **Flag columns where judgment overrode the framework.** This is acceptable — actuarial judgment is essential — but should be explicit rather than implicit.
- **Version the selections.** If the analysis is run multiple times (preliminary, peer review, final), track how selections evolved and why.

### Decision Hierarchy

When multiple criteria point in different directions, resolve conflicts using this priority order:

1. **Convergence Override (Criterion 8):** If all LDF averages agree, follow them regardless of other criteria.
2. **Diagnostic-confirmed trend (Criterion 6 + diagnostics):** A trend supported by multiple diagnostics takes priority over the prior.
3. **Bayesian anchoring (Criterion 4):** In the absence of convergence or confirmed trends, anchor to the prior.
4. **Asymmetric conservatism (Criterion 3):** Applies as a modifier to any movement — upward moves are larger, downward moves are dampened.
5. **Sparse data caution (Criterion 7):** When data is thin, all movements are dampened and windows are widened, overriding recency preference.
6. **Latest-point outlier (Criterion 5):** An identified outlier is excluded before any averaging or trending logic is applied.

### Quick-Reference Thresholds

| Parameter | Threshold | Action |
|---|---|---|
| Column CV | > 0.10 | Use excluding-high/low LDF averages |
| Column CV | > 0.20 | Exclude top and bottom 2 LDFs (if 7+ points) |
| 3yr vs. 5yr LDF divergence | > 3% | Trend likely; weight 3-year more heavily |
| 3yr vs. 5yr LDF divergence | > 5% | Strong trend; use 3-year at 75–100% weight |
| Latest LDF vs. 5yr avg | > 1.5σ or > 15% | Potential outlier; investigate before including |
| All LDF averages within | ± 2% of each other | Convergence; override prior if >3% different |
| Prior vs. preferred avg | < 2% | Hold the prior |
| Prior vs. preferred avg | 2–5% higher | Raise 50–75% of gap (25–50% if only latest diagonal) |
| Prior vs. preferred avg | 2–5% lower | Lower 25–50% of gap |
| Prior vs. preferred avg | > 5% | Material move; require diagnostic confirmation |
| Claim count per AY | < 50 | Sparse data; widen window, increase prior weight |
| Incurred per AY | < $1M (at 24+ months) | Sparse data; widen window |
| Data points in column | < 5 | Sparse; use all-year, increase prior anchoring |
| Single claim impact on column LDF | > 5% | Large loss; develop ex-large and load separately |
| Paid vs. incurred LDF divergence | > 5% at same maturity | Investigate; use diagnostics to determine which triangle is more reliable |
| Sub-1.000 LDF at early maturity | Any | Do not select; use 1.000 or prior |
| Sub-1.000 LDF (incurred, mid-maturity) | Sustained | May select ≥ 0.995 if confirmed by paid triangle |
| Sub-1.000 LDF (paid, any maturity) | Any | Never select; data issue — investigate |
| Last observable LDF | > 1.005 (incurred) / > 1.010 (paid) | Tail factor required |
| Open counts at last maturity | < 2% of reported | Tail of 1.000 may be defensible |
| Diagonal LDFs high/low across 3+ columns | Consistent direction | Calendar year effect; investigate cause |

---

## Diagnostic-Driven Adjustments

### Philosophy

Start with a baseline LDF selection (e.g., volume-weighted average of recent 5 years). Then use each diagnostic to decide whether to **adjust up**, **adjust down**, or **hold**. Cutoffs below are illustrative anchors — calibrate to your book.


### 1. `reported_counts`

**Purpose:** Detects volume shifts that affect credibility and pattern stability.

- Compare the latest diagonal's reported count to the trailing 5-year average at the same maturity.
  - **±10% change:** No action. Normal volatility.
  - **>+10% increase:** Emerging frequency trend or portfolio growth.
    - If growth is from new business or a coverage expansion, **select LDFs from more recent years** (3-yr weighted) — older patterns may not apply.
    - If growth is from a surge in low-severity claims (e.g., CAT), consider **lowering severity-weighted LDFs** at early maturities.
  - **>−10% decrease:** Shrinking book or tighter claim reporting.
    - Lower volume → less credibility. **Widen the averaging window** (use all-year average or Bornhuetter-Ferguson blend).
  - **>±25% swing:** Treat the year as a potential outlier.
    - Examine whether to **exclude that accident year** from the LDF average entirely, or cap its weight.


### 2. `incurred_severity` (cumulative)

**Purpose:** Tracks whether ultimate cost-per-claim is stable, trending, or distorted by case reserving changes.

- Compute the year-over-year trend in cumulative incurred severity at each maturity.
  - **Trend < +2% p.a.:** Stable. Use standard LDF selection.
  - **Trend +2% to +5% p.a.:** Moderate inflation or severity drift.
    - **Increase selected LDFs by ~1–2%** at immature ages (12–36 months) to anticipate continued emergence.
    - Cross-check with `paid_severity` — if paid is flat but incurred is rising, it's likely a case reserve strengthening, not true severity.
  - **Trend > +5% p.a.:** Significant shift.
    - **Weight recent 3 years heavily** in LDF averaging.
    - Consider applying an explicit severity trend to your selections.
    - If driven by a single AY, evaluate excluding or capping.
  - **Declining trend:** Possible reserve takedowns or improving mix.
    - Don't blindly lower LDFs — check `average_case_reserve` to confirm it's real.


### 3. `paid_severity` (cumulative)

**Purpose:** Shows actual cash outflow per claim. Less subject to reserving judgment than incurred.

- Compare cumulative paid severity at each maturity to the 5-year corridor (min/max range).
  - **Within corridor:** Confirms LDF selection is reasonable. No adjustment.
  - **Above corridor by >10%:** Payment acceleration or severity inflation.
    - **Increase paid LDFs at that maturity by the excess percentage** (e.g., 12% above corridor → bump LDF by ~0.01–0.02 at that age).
    - Especially important at early ages (12–24 months) where it signals larger claims settling faster.
  - **Below corridor by >10%:** Payment delays or mix shift toward smaller claims.
    - **Increase LDFs at later maturities** — the development is being pushed out, not eliminated.
    - Check `claim_closure_rate` to confirm slowdown.
  - **Divergence from incurred severity (paid growing faster):** Case reserves may be redundant. Consider selecting closer to the **paid chain ladder** indication.


### 4. `paid_to_incurred` (cumulative)

**Purpose:** Single most important adequacy check. Measures how "real" the incurred estimate is.

- Establish a benchmark paid-to-incurred ratio at each maturity from mature AYs.
  - **Ratio within ±5pp of benchmark:** Case reserves are consistent. Standard selections apply.
  - **Ratio >5pp below benchmark (i.e., less paid than expected):**
    - Case reserves are **potentially deficient** if claims aren't actually settling slower.
    - Check `open_counts` and `closure_rate`:
      - If closure is normal → reserves are likely adequate, just slower payout. **Hold LDFs.**
      - If closure is also slow → true delay. **Increase later-age LDFs** (push development right).
    - If `average_case_reserve` is flat or declining → case reserves may be too low. **Increase incurred LDFs by 2–5%** at affected maturities.
  - **Ratio >5pp above benchmark (more paid than expected):**
    - Claims settling faster or case reserves being released.
    - **Lower later-age incurred LDFs** — less development remaining.
    - But verify with `open_counts` — if many claims remain open, the fast payment may be partial and more is coming.


### 5. `open_counts`

**Purpose:** Quantifies residual exposure to future development.

- Compare open count at each maturity to the historical average at the same maturity.
  - **Within ±10%:** Normal. Standard LDF selection.
  - **>10% higher than expected:**
    - More claims still developing → **select LDFs at the higher end of the range** (e.g., use high-weighted or excluding-low average).
    - At late maturities (60+ months): consider adding **+0.005–0.015 to the tail factor**.
  - **>10% lower than expected:**
    - Claims resolving faster → **select LDFs at the lower end** or weight recent years that reflect this pattern.
  - **>25% deviation:** Strong signal.
    - Investigate cause (litigation backlog, claim handling changes, new TPA).
    - May warrant a **structural break** — exclude pre-change years from LDF averaging.


### 6. `average_case_reserve`

**Purpose:** Detects case reserving philosophy changes that distort incurred triangles.

- Track the year-over-year change in average case reserve per open claim at each maturity.
  - **Change < ±5%:** Stable reserving. Incurred LDFs are reliable.
  - **Increase of 5–15%:** Moderate case strengthening.
    - This inflates incurred development artificially. The incurred LDF from that column will be **biased high**.
    - **Dampen the incurred LDF selection** — weight it toward the paid indication or exclude the strengthened year.
  - **Increase > 15%:** Major case strengthening event.
    - **Do not use that column's incurred LDFs** as-is. Rely on paid chain ladder or BF method at that maturity.
  - **Decrease of 5–15%:** Reserve releases or a shift to faster settlements.
    - Incurred LDFs will look artificially low. **Select LDFs higher than the observed incurred pattern** or rely on paid.
  - **Key cross-check:** If `average_case_reserve` rises but `paid_severity` is flat → it's purely a reserving action. Discount it from incurred selections.


### 7. `claim_closure_rate` (cumulative)

**Purpose:** Measures what percentage of reported claims have closed by each maturity.

- Compare to the historical benchmark closure rate at each development age.
  - **Within ±3pp:** Normal. Hold LDF selections.
  - **>3pp slower closure:**
    - Development is being stretched. Remaining LDFs should be **selected higher**.
    - Rule of thumb: **for every 5pp slowdown in closure rate at age X, increase the LDF at age X by ~0.5–1.5%** (more for long-tail lines).
    - Check if this is a temporary effect (e.g., court closures) or structural.
  - **>3pp faster closure:**
    - Development is accelerating. LDFs at later maturities can be **lowered**.
    - But verify that fast closures aren't **low-value nuisance claim** closures masking slow large-claim settlement. Check `paid_severity` concurrently.


### 8. `incremental_incurred_severity`

**Purpose:** Isolates the marginal severity emerging in each development interval. Best diagnostic for detecting diagonal distortions.

- For each development column, compare the latest diagonal's incremental incurred severity to the 5-year average for that column.
  - **Within ±10%:** Normal. No adjustment to that column's LDF.
  - **>+10% above average:**
    - Either true severity emergence or a case reserve bulk strengthening.
    - Cross-check `paid_severity_incr`:
      - If paid increment is also up → **real severity. Select that column's LDF at the higher end.**
      - If paid increment is flat → **case reserving change. Dampen or exclude that diagonal from incurred LDF averaging.**
  - **>−10% below average:**
    - Possible favorable development or thinning claim activity.
    - Cross-check `incremental_closure_rate`:
      - If closures are normal → legitimate favorable. **Select LDF at lower end.**
      - If closures are also low → claims are just dormant. **Do not lower LDFs** — the development is deferred, not gone.
  - **Single AY outlier >25%:** Likely a large loss or reserve posting.
    - **Exclude that AY from the column average** or cap its influence.


### 9. `paid_severity_incr` (incremental)

**Purpose:** Shows the actual marginal dollars paid per claim in each interval. Most objective diagnostic — hardest to manipulate.

- For each development column, compare the latest diagonal to the historical average.
  - **Within ±10%:** Confirms the LDF for that column. No adjustment.
  - **>+10% above:**
    - Large settlements or accelerated payments in that interval.
    - **Increase the paid LDF for that column** unless it's clearly a one-time large loss (check claim count).
    - If driven by 1–2 large claims in a low-frequency line, **exclude or limit** rather than re-select.
  - **>−10% below:**
    - Slower payment activity.
    - **Do not decrease the overall LDF** — instead, **shift the expected development to later columns** (increase LDFs at the next 1–2 maturities).
  - **Persistent trend across multiple diagonals (3+ years):** Structural change in payment speed.
    - **Re-anchor your LDF selection to only the years exhibiting the new pattern.**


### 10. `incremental_closure_rate`

**Purpose:** How many claims close in each development interval — the tempo of resolution.

- For each development column, compare to the historical average incremental closure rate.
  - **Within ±2pp:** Normal. Hold LDFs.
  - **>2pp faster:**
    - Claims resolving quicker in that interval.
    - **Lower the LDF for that column slightly** (the development that would have emerged later is pulling forward).
    - But **increase scrutiny at the next column** — verify development isn't just being reclassified.
  - **>2pp slower:**
    - Claims lingering longer.
    - **Increase LDFs for that column and the next 1–2 columns** — the development hasn't disappeared, it's been pushed out.
    - Key check: if `paid_severity_incr` is also low → confirmed delay → **select at the upper range of historical LDFs for affected columns.**
  - **Persistent slowdown across 3+ diagonals:** Systemic change (e.g., litigation environment, claim staffing).
    - **Extend the tail factor** and **re-weight LDF selections toward more recent diagonals** that reflect the new regime.


### Decision Matrix Summary

| Signal | Primary Action | Cross-Check With |
|---|---|---|
| Rising incurred severity | Load early LDFs upward | `paid_severity` (real or reserve?) |
| Paid-to-incurred below benchmark | Increase incurred LDFs or shift to paid CL | `open_counts`, `closure_rate` |
| High open counts at late ages | Increase tail factor | `closure_rate`, `average_case_reserve` |
| Case reserve spike | Dampen incurred LDFs; lean on paid | `paid_severity`, `incremental_incurred_severity` |
| Slow closure rate | Increase LDFs at affected + subsequent ages | `paid_severity_incr`, `open_counts` |
| Incremental paid spike | Increase paid LDF at that age or exclude outlier | `reported_counts` (is it one big claim?) |
| Count surge/drop >25% | Adjust credibility weighting of that AY | All severity metrics (mix shift?) |


### Application Sequence

1. **Set baseline:** Volume-weighted 5-year average LDF at each maturity.
2. **Screen diagnostics:** Flag any metric outside its threshold at each maturity.
3. **Cross-check flagged metrics:** Use the pairings above to distinguish real shifts from noise.
4. **Adjust selections:** Apply directional and magnitude adjustments per the rules above.
5. **Reasonability test:** Ensure resulting ultimates are consistent across paid, incurred, and BF methods. If diagnostic-adjusted selections cause >10% divergence between methods, re-examine the most aggressive adjustment.
6. **Document:** Record which diagnostics triggered which adjustments for audit trail.

---

## Additional Considerations

### Volume-Weighted Averages — Use with Caution
Volume-weighting is not always superior. When a small number of accident years dominate the volume (e.g., a few particularly high-volume years), volume-weighted averages can overweight those years and distort selections. In those cases, simple averages may be more appropriate.


