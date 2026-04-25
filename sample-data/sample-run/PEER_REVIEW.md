# Peer Review — Workers Compensation (Sample Run)

**Analysis folder:** `C:\Users\super\Documents\actuarial\cas-rfp\spec-only\team-analyst\sample-data\sample-run`
**Review date:** 2026-04-25
**Status:** Advisory — no selections were modified

**Files reviewed:**
- `output/Complete Analysis - Values Only.xlsx`
- `output/Tech Review.xlsx`
- `REPORT.md`
- `REPLICATE.md`

---

## Summary

This is a well-structured first-pass reserving analysis on CAS example Workers Compensation data (AYs 2001–2024, valued 12/31/2024) using Paid LDF, Incurred LDF, IE (fallback ELR), and BF methods. The workflow, documentation skeleton, and selection reasoning are generally sound. However, two arithmetic integrity issues in the Paid Loss selections require correction before this draft can be relied upon: the AY 2010 Paid selection is mathematically impossible from the stated method blend, and the AY 2023 Paid selection materially exceeds what the stated weights would produce. Beyond those, the paid tail factor selection (1.0039) appears too conservative relative to WC industry expectations and the incurred tail (1.0216), and several documentation sections remain as placeholders. The analysis should not be distributed or finalized until at least the arithmetic issues and documentation gaps are resolved.

---

## High-Priority Findings

| # | Finding | Section Reference | Approx. Dollar Impact |
|---|---|---|---|
| HP-1 | AY 2010 Paid selection (1,358,891) **above** CL (1,350,189) — arithmetically impossible from any blend of methods | §6.1, Tech Review §16 | ~$9K overstatement vs. max method; root cause unknown |
| HP-2 | AY 2023 Paid selection (2,440,248) does not reconcile to stated formula; implied effective weight is ~43% CL vs. stated 15% | §6.1 | ~$487K vs. stated-formula result of $1,954K |
| HP-3 | Paid tail (1.0039) < Incurred tail (1.0216) — unusual for WC; paid development should extend longer than incurred | §5.1, Reviewer Quick-Start | Aggregate paid reserve potentially understated; see Proposed Alternatives |
| HP-4 | Paid ultimate > Incurred ultimate for AYs 2017, 2021–2023 — $380K total excess | §6.1–6.2, Tech Review §5 | 4 AYs; largest discrepancy in AY 2023 ($244K) |
| HP-5 | Multiple documentation sections still contain placeholder text — report is not final-ready per ASOP 41 | §1.3, §4.3, §5.3–5.5, §8.1, §9, §10, §11 | Documentation only; no dollar impact |

---

## Detailed Findings

### Cross-Method Consistency

**Paid vs. Incurred development patterns.** Paid link ratios at early ages (11→23) consistently exceed incurred link ratios (paid avg 2.498 vs. incurred avg 1.744), which is normal for a WC book where indemnity payments develop over many years. At mid-to-late ages, paid and incurred factors converge appropriately. No systematic bias is present in the body of the triangles.

**Tail factor inversion.** The paid tail factor (1.0039, Bondy) is materially lower than the incurred tail (1.0216, double exponential). For a long-tail Workers Compensation line, paid development characteristically extends further than incurred (incurred IBNR reflects case reserve strengthening/weakening in addition to unreported claims, while paid claims must actually be paid out). A paid tail below incurred tail is an unusual result that warrants scrutiny. The open-ended selector's recommendation of 1.0472 for paid is more consistent with WC long-tail convention. The rules-based selection reasoning notes the cross-check was "deferred" but does not resolve the anomaly.

The incurred tail selection (1.0216, double exponential, age 203, R²=0.886) is well-supported by diagnostics and is not questioned.

**BF vs. development methods.** At mature ages (AYs 2001–2016), CL dominates both paid and incurred, which is appropriate given high pct_developed (87%–100%). At green ages (AYs 2019–2024), BF is weighted 55%–90%, consistent with the maturity profile. No systematic overstatement or understatement bias between BF and CL is evident once the IE anomalies (see below) are set aside.

**IE fallback ELR.** The IE method shows negative IBNR in multiple years (confirmed in AY 2005 paid IE = $1,712K vs. actual $2,242K, and AY 2007 paid IE = $2,850K vs. actual $4,791K). These negative-IBNR situations are correctly explained in REPORT.md as a known limitation of the 3-year rolling average fallback when actual losses in volatile years run above the average. The selections appropriately down-weight or exclude IE in those years. No corrective action is required, but the analyst may want to consider whether the IE fallback ELR is influencing BF results in green years (BF uses the same a priori as IE).

---

### Paid vs. Incurred Reasonability

**Four AYs where paid ultimate exceeds incurred ultimate:**

| AY | Paid Selected | Incurred Selected | Paid Excess |
|----|--------------|-------------------|-------------|
| 2017 | 1,509,432 | 1,483,500 | +25,932 |
| 2021 | 1,554,970 | 1,522,446 | +32,524 |
| 2022 | 1,346,415 | 1,268,262 | +78,153 |
| 2023 | 2,440,248 | 2,196,734 | +243,514 |
| **Total** | | | **+$380,123** |

For AYs 2017 and 2021, the differences are modest ($26K and $33K respectively) and may result from legitimate method weighting differences. However, for AYs 2022 and 2023 the amounts are material ($78K and $244K). Note that raw paid actual ≤ raw incurred actual at every cell across the entire triangle (confirmed by Tech Review §12 — all PASS), so the exceedances arise entirely from projection mechanics: the paid CL at these young ages is highly leveraged and receives more relative weight in the paid blend than in the incurred blend. Consider whether a pure BF selection (eliminating the paid CL component entirely for AYs 2022–2024) would be more defensible.

Note also that AY 2023's paid excess is materially inflated by the arithmetic issue in HP-2 above. Correcting the paid AY 2023 selection to the stated formula result (~$1,954K) would flip that year from an excess of +$244K to a deficit of −$243K, which is the more expected relationship.

---

### Recent Year Loss Ratio / Loss Rate Stability

The diagnostics sheet shows selected ultimate loss rates (per payroll dollar) ranging from 0.002 to 0.014 across AYs, with no obvious step change in recent years. AY 2007 stands out at 0.014 (vs. median ~0.004), consistent with the large-loss flag in REPORT.md. The most recent AYs (2022: 0.003, 2023: 0.004, 2024: 0.003) are in line with the broader distribution, suggesting the BF-heavy selections for green years are not introducing visible rate instability.

However, AY 2015 has an implied ultimate loss rate of 0.009 and severity of $11,719 — the second highest in the study period. The Incurred LDF selection for AY 2015 is $3,912K, driven solely by CL with a CDF of 1.1565 at only 86.5% developed. The selection reasoning notes a potential case adequacy concern ("negative IE IBNR of −$1.7M, indicating prior overstated"). You may want to consider whether the incurred CL at 119 months (86.5% developed) is being over-relied upon for a period with elevated severity relative to its cohort.

AY 2023 ultimate severity ($7,206) and loss rate (0.0045) are elevated relative to adjacent years (2022: $4,253, 2024: $5,648). This may simply reflect the large uncertainty in projecting a 23-month AY, but warrants a note for the next valuation to monitor.

---

### ASOP Compliance

**ASOP 23 (Data Quality).** The data review is documented in §3 and is broadly satisfactory for a sample analysis. The negative development cells in paid and incurred triangles are disclosed (§3.3). No reconciliation to an external source is possible given the sample nature of the data, and this is appropriately disclosed.

**ASOP 25 (Credibility).** The method weighting framework (14-criteria rules-based + maturity-based BF escalation) constitutes an implicit credibility procedure. The weights are generally reasonable and maturity-appropriate. However, the a priori ELR source is a fallback approximation with no back-test against an external benchmark. This is disclosed in §5.2 and §3.4. Consider adding a brief note in §4.2 or §5.2 characterizing the sensitivity of BF results to the a priori (i.e., "if ELR is overstated by 10%, the total BF IBNR changes by approximately $X").

**ASOP 36.** This is a draft, not a formal SAO. No opinion type, materiality standard, or RMAD assessment is included — appropriate for the current draft stage. If this progresses to a formal opinion, §8.1 (sensitivity to key assumptions) must be quantified and the paid/incurred selection rationale must be explicit.

**ASOP 41 (Communications).** Several material gaps remain (see HP-5 and Documentation Quality section below). Most critically: §1.3 Intended Internal Users still shows example text; §4.3 LAE Treatment is unfilled (WC has meaningful LAE exposure, and the analysis scope should clarify whether ALAE/ULAE is included or excluded); §10 Information Date is blank. The report is appropriately marked "Working Draft" and includes the required caveat — these gaps are acceptable at draft stage but must be resolved before the report is circulated.

**ASOP 43 (Unpaid Claim Estimates).** Methods are appropriate for the data. Multiple methods are applied per ASOP guidance. The intended measure (paid and incurred central estimates) is stated. The main ASOP 43 gap is §8.1 (sensitivity table is all placeholders) and the absence of an aggregate reasonableness check narrative — the report discusses individual segments but does not offer a top-down view comparing total selected ($48.7M paid / $50.7M incurred) to any external or prior benchmark.

---

### Diagnostic Consistency

**Tech Review summary (33 WARNs, 0 FAILs):** All structural, period-consistency, and CL integrity checks pass. The warnings fall into three categories:

1. **Expected for this data type.** Link ratio ceiling violations (96 for incurred, 107 for paid) are concentrated at the 11→23 interval, where WC cumulative development is characteristically steep. These are not selection problems; they reflect normal WC loss emergence. Similarly, 31 incurred triangle reversal warnings (negative link ratios at late ages) are documented and expected for a maturing WC book.

2. **Require investigation.** The Incurred-to-Ult triangle has 1 cell where the ratio exceeds 1.0, meaning current incurred diagonal is above selected incurred ultimate for that AY/age combination. This is arithmetically problematic — it should be identified and explained (likely a rounding artifact in the Average IBNR/Unpaid computation, but needs confirmation). The 207 cells where Average Unpaid < Average IBNR also warrant a structural check; for paid periods, IBNR = Unpaid by definition, so this pattern in a combined average suggests the averaging methodology may be mixing paid and incurred IBNR without proper adjustment.

3. **Selection quality flag.** The IBNR% non-monotone warning for Paid Loss (7 reversals, exceeds N/5=4 tolerance) is the most substantive selection-quality signal. IBNR% should generally decline with age — reversals mean certain more-mature AYs carry a higher IBNR% than less-mature ones, which can indicate over-projection at specific ages. The AY 2010 arithmetic error (HP-1) likely contributes at least one reversal here.

**LDF diagnostics.** The incurred average LDF non-increasing check has 4 reversals (a younger-age average LDF < an older-age average LDF). This suggests potential pattern instability at certain intervals. You may want to identify which intervals are reversing and verify that the selection framework adequately addresses them (e.g., via CV-based caution or convergence overrides).

---

### Documentation Quality

**REPORT.md completeness.** The following sections contain unfilled placeholder text and must be addressed before the document is circulated:

- §1.3 Intended Internal Users — still shows example text ("[e.g., Chief Actuary...]")
- §4.3 LAE Treatment — both DCC/ALAE and A&O/ULAE fields are blank
- §5.3 Trend Assumptions — no entries; clarify whether trend is implicitly assumed zero or not applicable for this sample analysis
- §5.4 Other Assumptions — rate change, case reserve adequacy, settlement pattern all blank
- §5.5 Assumption Rationale — placeholder
- §8.1 Sensitivity to Key Assumptions — all "[±]" and "[ ]" placeholders; given that tail and ELR sensitivity are flagged as key risks in §8.2, the quantitative sensitivity table is essential
- §9 Reliance on Others — placeholder (if truly none, state "None — no third-party data or analyses relied upon other than the CAS sample dataset")
- §10 Information Date — blank
- §11 Open Questions — still default numbered placeholders with no specific questions; the Reviewer Quick-Start (§0) identifies four specific items for scrutiny but these are not reflected in §11

**REPLICATE.md.** The replication log is well-structured and meets ASOP 41 documentation standards for the steps that were completed. The note "Manual Overrides: None" is explicitly stated for all three selection phases (LDF, Tail, Ultimates), which is clear and good practice.

**Version history.** Only v0.1 is recorded. If any changes are made in response to this review, a v0.2 entry should be added.

---

### Technical Review Diagnostics

**All checks passed with 0 failures** — no structural or arithmetic failures from the automated tech review script. Key warnings noted in the Diagnostic Consistency section above. The most actionable warnings for the analyst to resolve:

- §16 Selection Reasonableness: AY 2010 Paid outside method range (see HP-1)
- §5 Cross-Measure Consistency: Paid > Incurred for 4 AYs (see HP-4)
- §4 IBNR% non-monotone: Paid Loss has 7 reversals (exceeds tolerance); warrants review
- §7 Incurred-to-Ult: 1 cell > 1.0 — identify and resolve
- §8 Average Unpaid < Average IBNR: 207 cells — structural check recommended

---

## Proposed Alternatives

The following are reviewer suggestions only. The analyst's selections remain unchanged.

---

**Alternative 1 — AY 2010 Paid: Correct the selection arithmetic (HP-1)**

The selection of 1,358,891 exceeds the CL (the highest method at 1,350,189) by $8,702 and cannot be produced by any weighted blend of CL ($1,350,189), BF ($1,338,594), and IE ($1,134,301). The stated weights (70% CL / 20% BF / 10% IE) would produce:

> 0.70 × 1,350,189 + 0.20 × 1,338,594 + 0.10 × 1,134,301 = **$1,326,281**

Even if IE is excluded and weights are 80% CL / 20% BF:

> 0.80 × 1,350,189 + 0.20 × 1,338,594 = **$1,347,870**

The root cause may be a stale value in the selection file or a script-level rounding error. Recommend: re-examine the values in `selections/Ultimates.xlsx` and `ultimates/projected-ultimates.parquet` for AY 2010 Paid, identify where the discrepancy enters, correct the selection, and rerun `6-create-complete-analysis.py` and `7-tech-review.py`.

---

**Alternative 2 — AY 2023 Paid: Reconcile selection to stated formula (HP-2)**

The selection of 2,440,248 does not reconcile to the stated formula (15% CL + 75% BF + 10% IE = ~$1,954K, or even using CL for the IE term = ~$2,183K). The implied effective weight is approximately 43% CL / 57% BF — materially more CL-reliant than the stated 15%. At 23 months maturity with a CDF of 2.73×, 43% CL weight is difficult to defend. Recommend verifying the calculation, then either (a) correcting to the stated 15/75/10 formula (~$1,954K) or (b) documenting why a 43% CL weight is appropriate at this age. Under the corrected formula the paid AY 2023 selection would be approximately $1,954K, below the incurred BF selection of $2,197K — which is the expected relationship.

---

**Alternative 3 — Paid tail: Consider a higher factor in the 1.030–1.047 range (HP-3)**

The rules-based paid tail of 1.0039 is grounded in the Bondy method anchored to the last observed factor of 1.0039. The primary concern is that this approach leaves the tail factor equal to the last observed average factor, which may understate structural tail development that is not yet visible in the data. For reference:

| Method | Paid Tail | Notes |
|---|---|---|
| Rules-based (Bondy) | 1.0039 | Last observed factor; materiality anchor applied |
| Open-ended (exp_dev_quick_exact_last) | 1.0472 | Exponential extrapolation; R²=0.204 (low) |
| double_exp (age 203) | 1.031 | Better fit (R²=0.515 for comparable paid scenario) |
| Incurred tail (double_exp, age 203) | 1.0216 | For comparison |

The reviewer would suggest a paid tail in the range of 1.020–1.030 as a reasonable middle ground, reflecting: (a) WC convention that paid should exceed incurred, (b) the Bondy anchor being conservatively low, and (c) the open-ended exponential fit having low R² (0.204), which reduces confidence in the 1.0472 figure. A tail of 1.025, for example, would ensure paid tail > incurred tail (1.0216) while remaining materially below the open-ended selection. The analyst should document the final rationale explicitly given the wide selector divergence flagged in §11 and §0.

---

**Alternative 4 — AYs 2022–2024 Paid: Consider pure BF selections to eliminate paid > incurred anomaly (HP-4)**

For the three green AYs where paid ultimate exceeds incurred ultimate (excluding AY 2017 where the excess is modest), consider setting paid selections to pure BF or capping them at the incurred selection. At 35 months (2022), 23 months (2023), and 11 months (2024), paid CL development is inherently noisy, and blending in any CL weight for paid will tend to over-project relative to incurred. If the paid BF uses the same a priori as incurred BF and the same ELR, the paid BF should be below the incurred BF (since paid actual < incurred actual at the same age, and the unreported portion borne by BF is proportionally larger). 

For AY 2022, the paid BF indication ($1,256,767) is already below the incurred BF ($1,268,262), as expected. A pure paid BF selection of $1,257K (vs. current $1,346K) would be more internally consistent.

---

*End of Peer Review.*
