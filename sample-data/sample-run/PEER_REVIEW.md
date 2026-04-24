# Peer Review — Workers' Compensation (Clerical) — Sample Test Data

**Analysis folder:** `C:\Users\super\Documents\actuarial\cas-rfp\spec-only\team-analyst\sample-data\sample-run`
**Review date:** 2026-04-24
**Status:** Advisory — no selections were modified

**Files reviewed:**
- `output/Complete Analysis - Values Only.xlsx`
- `output/Tech Review.xlsx`
- `REPORT.md`
- `REPLICATE.md`

---

## Summary

This is a well-structured first-pass analysis for a 24-accident-year WC (clerical) book. The paid loss results are internally sound — maturity-appropriate CL/BF blending, clean positive IBNR, and a sensible tail selection. The incurred loss results, however, contain a material defect: the incurred ultimate selector reported Incurred Chain Ladder as "unavailable" for AYs 2002–2024 and defaulted entirely to the IE fallback, producing selected ultimates that fall below the current incurred diagonal for nine accident years and aggregate paid-selected-exceeds-incurred-selected by $2.0M. Before this analysis can support any actuarial communication, the incurred CL data interface issue should be investigated and incurred selections should be rebuilt. Tail factor divergence on both paid and incurred also warrants analyst attention before finalizing.

---

## High-Priority Findings

| # | Finding | Section(s) | Materiality |
|---|---|---|---|
| H-1 | Incurred CL reported as "unavailable" by selector for 23 of 24 AYs despite values existing in workbook; all incurred selections default to IE | §6.2, §11 | **Critical** |
| H-2 | Incurred selected ultimate < current incurred diagonal for 9 AYs (IBNR < 0); worst cases AY 2007 (−$1.96M) and AY 2015 (−$1.71M) | §6.2, §7 | **Critical** |
| H-3 | Total paid selected ($48.0M) exceeds total incurred selected ($46.0M) by $2.0M; Paid > Incurred selected for 13 AYs including mature periods | §6, §7 | **High** |
| H-4 | Incurred tail factor: rules-based 1.0000 vs open-ended 1.0812 — range of 8 points; neither extreme well-supported in isolation | §5.1, §11 | **High** |
| H-5 | IE fallback ELR produces deeply unreliable ultimates for large-loss years (2007, 2015) where smoothed ELR is far below actual emergence | §5.2, §11 | **High** |

---

## Detailed Findings

### Cross-Method Consistency

**Paid LDF development pattern.** The paid triangle shows a well-behaved pattern. Age-to-age factors decline consistently with maturity; a few below-1.0 factors (AY 2013 at 59→71: 0.9974; AY 2001 at 71→83: 0.9904) are minor and consistent with reserve releases on old claims. The tech review flags 5 paid reversal cells — all within the N/5 tolerance threshold. No systematic bias detected in the paid chain ladder.

**Incurred LDF development pattern.** The incurred triangle is materially more volatile than paid. The tech review flags 31 link ratios below 1.0 (vs 5 for paid), consistent with incurred loss reserve movements and partial case reserve rundown. Notable sub-1.0 factors appear at AY 2006 (23→35: 0.8692) and AY 2009 (23→35: 0.9424) — suggesting adverse-then-favorable development, possibly from late-reported claims followed by closure. The incurred average LDF sequence also shows 4 age-reversals (younger age average < older age average), which the tech review flags. This signals that incurred development patterns may benefit from capping or exclusion of outlier years before re-running the selection.

**Incurred CL "unavailable" for all but AY 2001.** The incurred ultimate selector's reasoning text reads "CL unavailable (NaN)" for AYs 2002–2024, yet the workbook's `Sel - Incurred Loss` sheet contains non-null Chain Ladder ultimate values for most of those periods (e.g., AY 2011 at 167 months: CL = $2,048,920; AY 2010 at 179 months: CL = $1,338,019; AY 2008 at 203 months: CL = $1,427,506). This is the most consequential issue in the analysis: the selector was running blind to its primary method indication and compensated by applying IE exclusively. The reviewer would strongly encourage the analyst to debug this data interface issue before accepting any incurred selections.

**BF vs development method bias.** For Paid Loss, BF consistently exceeds CL at early maturities (e.g., AY 2024: BF $1,216,849 vs CL $2,602,723 — opposite direction, CL over-leveraged). The method weighting logic correctly addresses this by down-weighting CL at immature ages. For Incurred, BF values are not reported (all periods show BF unavailable in the selector), consistent with the IE/CL availability issue. Reviewer cannot evaluate BF bias for Incurred without corrected data.

---

### Paid vs Incurred Reasonability

**Total-level reversal.** Paid selected total ($48,024,170) exceeds incurred selected total ($46,003,887) by approximately $2.0M. For a WC book with active case reserves, incurred ultimates should ordinarily be at or above paid ultimates (since incurred includes case reserves in addition to paid losses). The reversal here is almost entirely a function of the IE fallback underestimating incurred ultimates for atypical accident years.

**Period-level: Incurred selected below current incurred diagonal.** The most critical manifestation of H-1 and H-2 is that the incurred selected ultimate is below the current incurred diagonal for the following accident years:

| AY | Age | Incurred Actual | Incurred Selected | Shortfall |
|---|---|---|---|---|
| 2005 | 239 | $2,242,149 | $1,712,285 | −$529,864 |
| 2007 | 215 | $4,810,775 | $2,850,338 | −$1,960,437 |
| 2010 | 179 | $1,277,672 | $1,134,301 | −$143,371 |
| 2011 | 167 | $1,916,082 | $1,542,649 | −$373,433 |
| 2014 | 131 | $1,389,604 | $1,227,804 | −$161,800 |
| 2015 | 119 | $3,382,963 | $1,669,813 | −$1,713,150 |
| 2018 | 83 | $2,395,448 | $2,215,023 | −$180,425 |
| 2019 | 71 | $2,599,883 | $2,259,324 | −$340,559 |
| 2023 | 23 | $1,651,757 | $978,226 | −$673,531 |

In no case should a selected ultimate fall below the current diagonal incurred — the minimum defensible incurred ultimate is the current diagonal itself. These selections represent an aggregate understatement of approximately $5.1M in incurred IBNR. AY 2007 and AY 2015 are individually material and should be prioritized for correction.

**Period-level: Paid selected > Incurred selected.** Beyond the nine negative-IBNR AYs, paid selected also exceeds incurred selected for AYs 2016, 2018, 2019, 2021, 2022, and 2024 where IBNR is positive but the ordering is reversed. For AY 2021 (47 months, early maturity), paid selected is $1,580,265 vs incurred selected $1,410,360 — a $170K reversal at a maturity where significant case reserves should still be open. Consider whether the IE-based incurred for these years is sufficiently conservative.

---

### Recent Year Stability

**Paid loss rate trend.** Using the Diagnostics sheet ultimate loss rates (per dollar of payroll), the paid book shows the following AY cohort pattern:

| Period | Avg Ultimate Loss Rate |
|---|---|
| 2005–2009 | 0.0064 |
| 2010–2014 | 0.0034 |
| 2015–2019 | 0.0055 |
| 2020–2024 | 0.0026 |

The 2020–2024 average of 0.0026 is the lowest of any five-year window and is roughly half the 2015–2019 rate. This could reflect genuine book improvement (favorable COVID-period claim activity, lower severity) or it could indicate that the BF a priori ELR applied to immature AYs is too conservative. Given that the fallback ELR is a three-year rolling average of *incurred* diagonal / payroll, it will reflect all prior period volatility with a lag — and for 2022–2024, the rolling average window includes 2019–2021 which contained elevated incurred periods. It is worth confirming whether the decline is directionally consistent with the analyst's pricing expectations or whether the BF a priori for 2022–2024 should be reviewed upward.

**Recent-year IBNR% pattern.** The paid IBNR% increases monotonically from mature to immature periods (AY 2001: 0.4%, AY 2024: 72.8%), as expected. The tech review confirms this passes at the N/5 tolerance with 4 reversals. Severity spikes in the diagnostics (11 periods with >25% YoY change) are worth monitoring in a live analysis but are typical of thin-data WC triangles.

---

### ASOP Compliance

**ASOP 43 (Unpaid Claim Estimates).**
The paid loss results satisfy ASOP 43's core requirements: multiple methods are used where applicable, method weighting is documented and maturity-appropriate, and uncertainty is discussed in §8. The incurred results do not: for 23 of 24 AYs, only one method (IE) is used due to the CL interface issue, and for nine of those AYs the resulting ultimates fall below current losses — an outcome that is mechanically inconsistent with the definition of an unpaid claim estimate. Per ASOP 43 §3.6, the estimate must represent a reasonable provision for unpaid claims; a negative IBNR does not satisfy this standard for periods that are not yet fully developed. The analysis, as currently stated in the report, appropriately flags this as a draft limitation — but correction is required before any final actuarial use.

**ASOP 25 (Credibility).**
The paid BF method uses the fallback ELR as its a priori complement. This is a reasonable approximation when no external ELR is available, and the report discloses it clearly. However, the fallback's three-year rolling average does not adequately differentiate between normal years and large-loss years (2007, 2015), causing the IE and BF indications to be severe underestimates for those periods. Consider whether applying the fallback to *paid* rather than *incurred* diagonal (which is more stable) would produce a better-calibrated a priori, or whether a longer rolling window (5-year) would smooth more reliably. The incurred IE selections inherit this same calibration issue with no CL cross-check due to the data interface defect.

**ASOP 23 (Data Quality).**
The data documentation in §3 is thorough and appropriate for test data. The absence of reconciliation to external financials is noted and justified. One minor observation: the reported count triangle contains fractional values (noted in §3.3 as "likely partial-year or weighted counts"), but the analysis treats them as integers throughout. For a live analysis, the actuary should confirm with the data provider whether fractional counts are intentional or a data formatting artifact.

**ASOP 41 (Actuarial Communications).**
REPORT.md is well-organized and covers most ASOP 41 requirements for a draft actuarial report. Two items to address before finalizing: (1) Section 1.3 (Intended Users) contains placeholder text — this should be populated with actual intended user(s) for any version distributed beyond the drafting team. (2) The ASOP self-check table in §12 references "ASOP 56 (Modeling)" but this standard governs actuarial models in the context of pricing and reserving models with specific computational components — its applicability to an AI-assisted selection process may deserve a more specific disclosure rather than a checklist reference.

**ASOP 36 (Statements of Actuarial Opinion).**
Not applicable — this is an internal working draft, not an SAO. Should the analysis progress to a formal actuarial opinion, the negative IBNR positions and single-method reliance on incurred would need to be resolved first.

---

### Diagnostic Consistency

**Incurred IBNR% pattern — 11 reversals.** The tech review flags 11 reversals in the Incurred IBNR% sequence (expected to be non-increasing as maturity increases). This directly reflects the IE-driven selections producing an erratic ultimate pattern across accident years — some mature years receive high IE ultimates (e.g., AY 2008 at 203 months: incurred selected $2,543,927 vs paid selected $1,426,693) while others receive very low ones (AY 2010 at 179 months: $1,134,301). The underlying cause is the IE fallback's sensitivity to the shape of the incurred diagonal by year rather than a smooth development-based extrapolation.

**Paid-to-incurred ratio (raw data).** The raw paid-to-incurred ratio (before selection) shows 4 reversals in expected monotone increase. These are modest and within tolerance for a normal WC triangle with case reserve movements. The most-mature diagonal shows paid/incurred near 100% for all old AYs, consistent with near-closure.

**Severity and frequency trends.** The tech review flags 11 accident years with >25% YoY severity change and 5 with frequency > 2× median. In a live analysis this would typically prompt investigation of large-loss years or changes in claim mix. For this test data, AY 2007 and AY 2015 are the clearest outliers (paid actuarial loss substantially above adjacent years) and are correctly called out in the analyst's report. No additional action recommended for a test run, but these would be high-priority diagnostic items in production.

**X-to-Ultimate triangles.** The Incurred-to-Ult triangle contains 73 cells > 1.0 and 157 cells where Incurred-to-Ult < Paid-to-Ult. Both flags are downstream consequences of the IE-based incurred selections: because the incurred selected ultimate is artificially low for many periods, the X-to-Ult ratios exceed 1.0 (current diagonal > selected ultimate) and fall below the paid-to-ult ratio. These will resolve once incurred selections are corrected.

---

### Documentation Quality

**REPORT.md.** The report is well-written and contains substantive rather than boilerplate content in nearly all sections. The analyst has correctly pre-populated the open questions section with exactly the items a reviewer needs to scrutinize. Minor items to address before distribution: (1) populate Section 1.3 intended users; (2) add a brief note in §8.2 about the potential downside scenario if the incurred CL interface issue understated reserves (quantify the effect if incurred CL-based selections had been used); (3) the comparison-to-prior table in §2 remains unfilled — this is expected for a first valuation but should be struck or explicitly noted as "First valuation — no prior."

**REPLICATE.md.** The reproducibility log is thorough and generally satisfies ASOP 41's supporting documentation requirements. One gap: Step 5 contains placeholder text ("[Ran / Skipped - reason]") for the IE and BF scripts rather than specifying what actually ran. REPLICATE.md states the fallback approximation was used (confirmed in the Notes section), but Step 5 itself should be updated to explicitly state both scripts ran using the fallback ELR.

**ASOP 41 alignment.** The combination of REPORT.md and REPLICATE.md would allow another actuary to understand the methods, data, and rationale. The key reproducibility gap is the incurred CL selector's reported "unavailability" — because this is a data interface issue rather than a deliberate exclusion, REPLICATE.md does not document it. If the next analyst reading REPLICATE.md followed the replication instructions, they would reproduce the same defective result without knowing why.

---

### Technical Review Diagnostics

The Tech Review.xlsx contains 2 PASS groups, 1 FAIL, and 18 WARN categories. Results are summarized below with reviewer commentary.

**FAIL: 'Incurred Loss' IBNR >= 0** — 9 periods below tolerance (2005, 2007, 2010, 2011, 2014, 2015, 2018, 2019, 2023). This is the primary numerical integrity failure and is the mechanistic output of findings H-1 and H-2 above. Requires resolution.

**WARN: Paid Loss selected <= Incurred Loss selected** — 13 violations. Directly linked to the incurred selection defect. Expected to self-correct once incurred CL interface is repaired.

**WARN: 'Incurred Loss' IBNR% non-increasing** — 11 reversals (exceeds N/5=4 tolerance). Downstream of incurred selection defect.

**WARN: 'Incurred-to-Ult' values in (0,1] / non-decreasing** — 73 cells > 1.0 and 31 reversals. Downstream of incurred selection defect.

**WARN: Average IBNR** — 73 negative cells, 31 reversals. Downstream of incurred selection defect.

**WARN: Incurred-to-Ult >= Paid-to-Ult** — 157 violations. Downstream of incurred selection defect.

**WARN: 'CL - Incurred Loss' link ratios** — 31 sub-1.0 ratios and 96 above ceiling. The incurred triangle is inherently more volatile than paid for WC; these flags reflect real data characteristics and may not indicate a data defect. Analyst commentary in §3.3 and §5.4 adequately addresses this.

**WARN: Severity/Frequency Trends** — 11 severity spikes and 5 frequency spikes. Notable but appropriate for test data with atypical years (2007, 2015). See diagnostic consistency section above.

**WARN: Closure rate checks** — skipped due to absent closed count. Noted in §3.4. Acceptable.

All remaining WARNs (paid LDF ceiling violations, paid non-decreasing reversals within tolerance, paid-to-incurred raw data reversals, case reserve reversals) are within expected ranges for an annual WC triangle of this size and do not require remediation.

---

## Proposed Alternatives

### Incurred Loss Selections — Rebuild Using Incurred CL Where Available

**Issue:** The incurred ultimate selector used IE exclusively for AYs 2002–2024 due to a reported CL "unavailability" that appears inconsistent with the workbook data.

**Analyst's current selection:** 100% IE for all periods except AY 2001. Total incurred selected: $46,003,887.

**Reviewer's proposed approach:** Before rebuilding selections, run a diagnostic to confirm whether the incurred CL values in the workbook are methodologically reliable (i.e., CDFs applied correctly, tail factor incorporated). If so, apply a maturity-consistent blend mirroring the paid method weighting:

| AY Range | Age Range | Proposed Incurred Weighting |
|---|---|---|
| 2001–2008 | 203–287 mo | 100% Incurred CL |
| 2009–2011 | 167–191 mo | 80% CL / 20% BF |
| 2012–2013 | 143–155 mo | 60% CL / 40% BF |
| 2014–2016 | 107–131 mo | 50% CL / 50% BF |
| 2017–2018 | 83–95 mo | 60–65% BF / 35–40% CL |
| 2019–2024 | 11–71 mo | 70–95% BF / 5–30% CL |

For reference, applying 100% Incurred CL for the mature years would move the largest problem AYs significantly:

| AY | Current Inc Selected | Inc CL Indication | Proposed Alternative | Difference |
|---|---|---|---|---|
| 2007 | $2,850,338 | $4,972,115 | ~$4,947,059 (CL-dominant) | +$2,096,721 |
| 2011 | $1,542,649 | $2,048,920 | ~$2,019,075 (80/20 CL/BF) | +$476,426 |
| 2015 | $1,669,813 | $3,784,630 | ~$3,651,000 (50/50 CL/BF) | +$1,981,187 |
| 2005 | $1,712,285 | $2,296,903 | ~$2,299,899 (CL-dominant) | +$587,614 |

Aggregate impact of rebuilding incurred selections using CL is likely to increase total incurred by $5–7M, bringing it above paid at the aggregate level and producing a positive IBNR for all periods.

### Paid Loss Tail Factor — Consider Modest Load

**Analyst's selection:** 1.0039 (Bondy method, cutoff age 203 months).
**Open-ended AI selection:** 1.0181 (Exponential Decay Product, cutoff age 143 months).

The rules-based Bondy tail is mechanically sound (selecting the lowest defensible tail from the curve suite), but WC is a long-tail line and the 1.0039 Bondy result relies on fitting from the very end of development where data is sparse. The open-ended selector's choice of 1.0181 is based on a 0.23 R² fit — not strong. A middle-ground selection in the range of **1.010–1.015** may be more defensible and broadly consistent with industry WC paid tail benchmarks. This would add approximately $480K–$650K to total paid ultimates.

### Incurred Loss Tail Factor — Acknowledge Uncertainty

**Analyst's selection:** 1.0000 (McClenahan method).
**Open-ended AI selection:** 1.0812 (Double Exponential, R²=0.884).

The 1.0812 open-ended tail reflects a strong curve fit but a result that large for WC incurred at age 203 months would be unusual and would imply substantial open case activity beyond 17 years. The 1.0000 McClenahan result may reflect the dataset's near-flat incurred factors at late ages (consistent with a mostly closed book), but could also be an artifact of the IE-based selections pulling down the apparent development at late ages. The reviewer would suggest treating this question as open until incurred selections are corrected — the apparent tail behavior may shift materially once CL-based incurred ultimates are in place.

---

*This review is advisory in nature. No selections have been modified. All proposed alternatives are for analyst consideration; the analyst retains judgment over final selections.*
