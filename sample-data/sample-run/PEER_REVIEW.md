# Peer Review — Workers Compensation (Sample Run)

**Analysis folder:** C:\Users\super\Documents\actuarial\cas-rfp\spec-only\team-analyst\sample-data\sample-run
**Review date:** 2026-04-27
**Status:** Advisory — no selections were modified

**Files reviewed:**
- Analysis - Values Only.xlsx
- Tech Review.xlsx
- REPORT.md
- REPLICATE.md

---

## Summary

This analysis covers 24 accident years (2001–2024) of Workers Compensation using Paid Loss CL, Incurred Loss CL, and Bornhuetter-Ferguson projections on both loss measures, plus Reported Count CL. The data preparation and selection mechanics appear well-executed and the AI selectors exercised appropriate judgment for most mature years. However, three issues require analyst attention before this analysis is ready for external use: (1) REPORT.md is essentially unfilled boilerplate and does not meet ASOP 41 documentation requirements; (2) the two AI selectors diverge materially for AY 2023 and AY 2024, where the choice between CL and BF moves the total reserve by approximately $3.2M; and (3) the Tech Review shows a structural FAIL plus several warnings — most critically, extreme year-over-year severity spikes — that are undocumented in the report.

---

## High-Priority Findings

**P1 — REPORT.md is unfilled template (ASOP 41 non-compliant).** Sections 0, 2, 3.1–3.4, 4.1–4.3, 5.1–5.5, 6, 7, 8, 9, 10, 11, and 14 are all placeholder text or unchecked checklist items. The report cannot support an actuarial opinion in its current form. See [Documentation Quality](#documentation-quality).

**P2 — AY 2023 and AY 2024 selector disagreement is ~$3.2M.** The rules-based selector chose Paid BF for both years; the open-ended selector chose Paid CL. The implied reserve difference is $1.7M for AY 2023 and $1.5M for AY 2024. For years at 23 and 11 months of age, this is the single most consequential judgment in the analysis and it is unresolved. See [Recent Year Stability](#recent-year-stability) and [Proposed Alternatives](#proposed-alternatives).

**P3 — Tech Review FAIL: Measure sheets absent from Values Only workbook.** The tech review cannot validate structure, period consistency, maturity, selections, CL triangle integrity, development factors, paid-to-incurred ratios, case reserve reasonableness, or closure rate reasonableness because the expected measure-level sheets (Incurred Loss, Paid Loss, Reported Count) are absent from the values file. Checks 2, 3, 6, 10–14 are all listed as WARN/skipped as a result. The reviewer is unable to complete a full mechanical validation without these sheets.

**P4 — Severity spikes flagged in Tech Review are undocumented.** Three development periods show year-over-year severity increases of 45%, 101%, and 244%. The 244% spike in particular is anomalous and is not addressed in REPORT.md Section 7. AY 2007 also shows ultimate severity roughly 2–3× the book average, which may reflect a large loss or unusual claim mix. Neither is documented. See [Diagnostic Consistency](#diagnostic-consistency).

**P5 — IE/BF a priori calibration appears significantly mis-calibrated.** The Initial Expected method produces negative IBNR for the majority of accident years across both Paid and Incurred measures, which means actual emerged losses have already exceeded the a priori expected ultimate for those years. This pattern is pervasive and is not discussed anywhere in the report or REPLICATE.md. See [ASOP Compliance](#asop-compliance) (ASOP 25).

---

## Detailed Findings

### Cross-Method Consistency

**Paid vs. Incurred CL direction.** For most mature years (2001–2017), Paid CL ultimate is below Incurred CL ultimate, which is the expected direction for Workers Compensation — incurred development factors are generally lower because case reserves are already established, so paid development ratios are larger. The magnitude is reasonable for most years (1–4% difference), with two notable exceptions:

- **AY 2002 (275 months):** Paid CL of $2,216,837 is 7.9% below Incurred CL of $2,406,197. At 23 years of age this is a wide gap. Consider whether an incurred case reserve movement is driving the Incurred CL higher than warranted at this maturity.
- **AY 2006 (227 months):** Paid CL of $1,505,496 is 7.1% below Incurred CL of $1,621,406. Similar concern at 19 years of age.
- **AY 2012 (155 months):** Paid CL of $1,307,267 is 13.3% below Incurred CL of $1,508,059. This is the largest divergence among all mid-to-mature years and is flagged as a priority — see [Paid vs. Incurred Reasonability](#paid-vs-incurred-reasonability) below.

**Recent years where Paid CL exceeds Incurred CL.** For AY 2018–2022, the Paid CL ultimates exceed Incurred CL ultimates (ranging from +2.9% to +6.6%). This reversal of the normal pattern — paid ultimates above incurred ultimates — can occur when incurred losses develop downward due to case reserve releases. The analysis does not comment on this. It is worth considering whether this reflects a structural change in claims handling or reserve adequacy that might affect tail factor assumptions.

- AY 2018: Paid CL $3,053,328 vs. Incurred CL $2,966,114 (+2.9%)
- AY 2020: Paid CL $1,541,397 vs. Incurred CL $1,452,868 (+6.1%)
- AY 2021: Paid CL $1,690,288 vs. Incurred CL $1,586,081 (+6.6%)
- AY 2022: Paid CL $1,645,673 vs. Incurred CL $1,557,461 (+5.7%)

**BF vs. development methods.** The Paid BF ultimates are consistently below Paid CL for recent years (AY 2020–2022), which is consistent with the a priori expected rates being lower than what CL is projecting. However, for AY 2019, Paid BF ($3,053,319) is 9.7% below Paid CL ($3,379,669), which is a material gap at 71 months. Consider whether the rules-based selection of Paid CL for AY 2019–2022 is appropriate given the BF-CL divergence and the immaturity of the data.

---

### Paid vs. Incurred Reasonability

**AY 2012 is the highest-concern mature year.** At 155 months (nearly 13 years), Paid CL of $1,307,267 is 13.3% below Incurred CL of $1,508,059 — a $200,792 gap. For a year that is 91% developed, this implies there is significant open reserve being carried on the incurred side. The paid triangle shows a stable, nearly flat development pattern through 155 months, which lends credibility to the Paid CL. However, the incurred IBNR of $144,306 at this maturity seems elevated and warrants review of the open case reserve position for this year.

**AY 2023 paid ultimate below actual incurred losses on diagonal.** At 23 months, Paid CL projects $3,548,451 while the open-ended selector chose this value. However, the Incurred CL at $3,909,735 is materially higher, and the most recent incurred actual of $1,651,757 already exceeds the paid actual of $1,199,242 by 38% — a high incurred-to-paid ratio at this age, suggesting significant open case reserves and/or that claims are more complex. This makes the choice of BF over CL for AY 2023 more defensible.

**AY 2024 paid ultimate exceeds incurred IE and BF.** For the youngest year, Paid CL of $2,757,368 substantially exceeds both Paid BF ($1,224,487) and Incurred BF ($1,640,331). At 13% paid development, the CL is highly leveraged and a single large payment could move the ultimate dramatically. The rules-based selector's preference for BF is well-supported here.

---

### Recent Year Stability

**AY 2023 and AY 2024 present the widest method spread in the analysis and drive the most material unresolved judgment.**

For AY 2023 (23 months, 34% paid developed):

| Method | Ultimate | IBNR |
|---|---|---|
| Paid CL | $3,548,451 | $2,349,209 |
| Paid BF | $1,846,865 | $647,622 |
| Incurred CL | $3,909,735 | $2,257,978 |
| Difference (CL vs. BF) | **$1,701,586** | — |

For AY 2024 (11 months, 13% paid developed):

| Method | Ultimate | IBNR |
|---|---|---|
| Paid CL | $2,757,368 | $2,402,120 |
| Paid BF | $1,224,487 | $869,239 |
| Incurred CL | $3,586,977 | $2,696,822 |
| Difference (CL vs. BF) | **$1,532,881** | — |

At these maturities, Paid CL is subject to extreme leverage (CDFs of 2.96 and 7.76 respectively). A single large payment in the most recent diagonal can distort the projected ultimate significantly. For Workers Compensation — which has long-tailed development for permanent disability claims — BF anchoring at early ages is generally more reliable per actuarial practice and ASOP 43 guidance that the method selected should be appropriate given the data, environment, and age.

The open-ended selector's reasoning for choosing CL for AY 2023 cites "paid CL more consistent with tail development pattern" — but at 34% developed with a CDF of 2.96, this is difficult to defend over a BF estimate that draws on a credible a priori. You may want to consider whether Paid BF or an average of Paid BF and Paid CL is more appropriate for AY 2023.

**Combined impact:** Choosing Paid CL over Paid BF for both AY 2023 and AY 2024 would increase the selected reserve by approximately $3.2M. This is one of the larger single judgments in the analysis and should be flagged explicitly in REPORT.md Section 11.

**Implied loss rates by AY.** Without a final selected-ultimates table being available for review, the reviewer cannot perform a full year-over-year loss rate comparison. This check should be completed and documented in Section 7 of REPORT.md.

---

### ASOP Compliance

**ASOP 23 — Data Quality:**
- Source data is documented at a high level in REPLICATE.md (Triangle Examples 1.xlsx, Workers Compensation). However, REPORT.md Section 3.1 is entirely unfilled with bracketed placeholders.
- No data reconciliation is documented. Section 3.2 states "Reconciled to [financial system / prior valuation / GL] as of [date]" — this is still a template. It is unclear whether any reconciliation was performed.
- Section 3.3 (Data Quality Observations) and Section 3.4 (Data Limitations) are also unfilled. The absence of Closed Count data (which prevents closure rate monitoring), the lack of an expected loss rate file, and the severity spikes flagged by the tech review are all material data quality items that should be documented here.

**ASOP 25 — Credibility:**
- The IE/BF methods are calibrated using an a priori expected loss rate, but the source of this rate is not documented anywhere. The REPLICATE.md states the fallback approximation was likely used (diagonal loss per dollar of exposure, 3-year rolling average), but this is not confirmed. The pervasive negative IBNR from the IE method — visible across the majority of accident years on both Paid and Incurred bases — strongly suggests the a priori rates are materially higher than the underlying experience. This is a mis-calibration that should be investigated and documented.
- Section 4.2 (Method Weighting / Selection Logic) is a placeholder. The credibility basis for the BF selections (particularly for AY 2023–2024, where BF is the most important method) is not documented.

**ASOP 36 — Statements of Actuarial Opinion:**
- The analysis appears to be in a draft state and is not yet positioned as an opinion document. Section 2 (Summary of Indications) contains no numbers — all cells show placeholder brackets. Before any opinion can be issued, this table must be populated from the final selected ultimates.

**ASOP 41 — Actuarial Communications:**
- Section 0 (Reviewer Quick-Start) is entirely unfilled. This section exists specifically to orient a peer reviewer and was not populated.
- The report identifies the intended internal users as "[e.g., Chief Actuary, Reserving Committee, CFO]" — still a placeholder. The intended user must be identified.
- Material assumptions (tail factor source, a priori loss rate basis, method weighting rationale) are not documented with rationale. An independent actuary cannot evaluate the selections from REPORT.md in its current state.
- Version history (Section 14) has no dates filled in.

**ASOP 43 — Property/Casualty Unpaid Claim Estimates:**
- The intended measure (mean, central, high) is not stated.
- Scope is partially filled (Section 1.2 has the LOB and accident year range), but coverage basis, gross vs. net, and discounting treatment are noted as "Not specified."
- Sections 8.1 (Sensitivity) and 8.2 (Sources of Uncertainty) are empty placeholders. ASOP 43 requires a reasoned discussion of process, parameter, model, and systemic risk; for a WC book with 24 years of development history this is particularly important.
- No comparison to prior estimate is shown (Section 2 comparison table is blank).

---

### Diagnostic Consistency

**Tech Review FAIL and WARN items requiring response:**

The Tech Review reported one FAIL and several WARN conditions. The FAIL — "None of: Incurred Loss, Paid Loss, Reported Count, Closed Count" in the values workbook — caused the majority of subsequent checks to be skipped. This is a structural issue that may reflect how the values-only workbook was generated, but it means the automated diagnostic coverage is incomplete. Section 7 of REPORT.md should acknowledge which checks passed and which were skipped and why.

**Severity trend warnings.** The tech review flagged 13 development periods with year-over-year severity changes exceeding 25%, including:
- Period 3: +45%
- Period 4: +101%  
- Period 6: +244%

The 244% spike is extreme. Looking at the diagnostics data for AY 2024 (11 months), the incurred severity is $3,477 per claim, while AY 2023 at 23 months shows $5,419 per claim — a 56% jump. AY 2007 shows consistently elevated per-claim severity throughout development ($6,400–$10,100 per claim vs. $1,600–$5,400 for most other years), suggesting this year may contain one or more large claims. None of this is discussed in the report.

**AY 2007 anomaly.** The AY 2007 ultimate of approximately $4.96M (Paid CL) or $5.14M (Incurred CL) is 3–4× the typical accident year in this book. This could represent a large workers' compensation claim (e.g., permanent total disability). Neither the REPORT.md nor REPLICATE.md flags this as a potential large-loss year or explains whether any special handling was applied. This should be addressed in Section 3.3 or 6 of the report.

**AY 2015 elevation.** AY 2015 also shows an elevated ultimate (~$3.85M Paid CL), approximately 2–3× the typical year, with a large paid development jump from 107 to 119 months (incurred-to-ult reversal flagged). This merits similar commentary.

**Reported-to-Ult cells > 1.0 (136 cells).** The count development factors are slightly below 1.0 for recent years (CDF ~0.997 for 2016–2023), meaning the triangle implies a small reduction in reported count as the year matures. This is unusual — a sub-1.0 CDF for reported counts typically implies claim withdrawals or administrative corrections. The tech review flagged 136 count cells exceeding 1.0 in the percent-developed triangle (i.e., current count > selected ultimate count). This should be investigated and documented.

**Incurred-to-Ult cells > 1.0 (16 cells).** These represent accident years where incurred losses have already exceeded the selected ultimate — consistent with the negative IBNR pattern from the IE method. However, the presence of these cells also suggests the incurred CL selections may be somewhat low for those years, or that incurred development is running above the selected pattern. This deserves discussion in Section 7.

**Non-decreasing pattern reversals:**
- Incurred-to-Ult: 31 reversals
- Paid-to-Ult: 5 reversals
- Reported-to-Ult: 6 reversals

These reversals indicate that in some diagonal-to-diagonal movements, development moved in the unexpected direction. A portion of these may be tied to the Bondy tail factor applying a constant factor to the last observed link ratio — producing small mechanically derived factors that occasionally cause reversals in the to-ultimate triangle. This should be documented.

---

### Documentation Quality

**REPORT.md is not ready for peer sign-off.** A high fraction of the substantive content sections are template placeholders:

| Section | Status |
|---|---|
| 0. Reviewer Quick-Start | Empty |
| 2. Summary of Indications | All numbers blank |
| 3.1 Data Used | All rows placeholder |
| 3.2 Data Reconciliation | Placeholder |
| 3.3 Data Quality Observations | Placeholder |
| 3.4 Data Limitations | Placeholder |
| 4.1 Methods Applied | All rows placeholder |
| 4.2 Method Weighting Logic | Placeholder |
| 4.3 LAE Treatment | Placeholder |
| 5.1 Development Patterns | Placeholder |
| 5.2 Expected Loss Ratios | Empty table |
| 5.3 Trend Assumptions | Empty |
| 5.4 Other Assumptions | All placeholder |
| 5.5 Assumption Rationale | Placeholder |
| 6. Results by Segment | All placeholder |
| 7. Diagnostics | All checklist items unchecked |
| 8.1 Sensitivity | Empty table |
| 8.2 Sources of Uncertainty | Placeholder |
| 9. Reliance on Others | All placeholder |
| 10. Information Date | Blank |
| 11. Open Questions | All placeholder |
| 14. Version History | Dates blank |

Until these sections are populated from the actual analysis output, the report does not satisfy ASOP 41 requirements for actuarial communications and would not support an actuarial opinion under ASOP 36.

**REPLICATE.md** is better populated but has unresolved placeholder text in the "USER ACTION — Manual Selections" blocks for LDF selections, tail factor selections, and ultimate selections. Per the REPLICATE.md instructions, if no manual overrides were made, this should say "All selections are from the Rules-Based AI Selection row/column." Confirm and fill in.

---

### Technical Review Diagnostics

Summary of Tech Review.xlsx findings:

| Status | Check | Comment |
|---|---|---|
| **FAIL** | Measure sheets present | Paid Loss, Incurred Loss, Reported Count absent from values file; most downstream checks skipped |
| WARN | Incurred-to-Ult cells > 1.0 | 16 cells — consistent with negative IBNR on IE/BF |
| WARN | Incurred-to-Ult non-decreasing | 31 reversals — likely tied to tail mechanics; document |
| WARN | Paid-to-Ult non-decreasing | 5 reversals — investigate |
| WARN | Reported-to-Ult cells > 1.0 | 136 cells — sub-1.0 count CDFs causing this; document |
| WARN | Reported-to-Ult non-decreasing | 6 reversals |
| WARN | Average IBNR < 0 | 16 cells — IE negative IBNR not addressed in report |
| WARN | Average IBNR non-increasing | 31 reversals |
| WARN | Average Unpaid non-increasing | 5 reversals |
| WARN | YoY severity change > 25% | 13 periods including +101% and +244% — not documented |
| WARN | Frequency spike > 2× median | 5 periods — not documented |
| PASS | Ultimate severity no outliers | Median $4,584 |
| PASS | Loss rate in (0, 2.0) | Range 0.002–0.014 |
| PASS | Incurred-to-Ult >= Paid-to-Ult | All cells pass |
| PASS | Most-mature diagonal ~= 1.0 | Paid-to-Ult: 0.9961; Reported: 1.0000 |

Checks for period consistency, maturity, selection consistency, CL triangle integrity, development factor reasonableness, paid-to-incurred ratios, case reserve adequacy, and closure rate reasonableness were all skipped due to the structural FAIL. These are material checks for a WC analysis and should be re-run once the workbook structure is corrected.

---

## Proposed Alternatives

### AY 2023 — Consider Paid BF over Paid CL

**Analyst's selection (open-ended AI):** Paid CL — $3,548,451 (IBNR $2,349,209)
**Rules-based AI selection:** Paid BF — $1,846,865 (IBNR $647,622)
**Reviewer's suggested alternative:** Paid BF — $1,846,865, or a blend of Paid BF (75%) and Paid CL (25%) = approximately $2,272,012

**Rationale:** At 23 months and 34% paid developed, the Paid CL CDF of 2.96 is highly sensitive to the most recent diagonal payment pattern. For Workers Compensation, where long-term permanent disability claims can produce irregular cash flows in early years, BF methods anchored on a credible a priori are generally more stable and defensible per ASOP 43. The rules-based selector's reasoning is sound: "very green, 12–24 month boundary" warrants BF primary weighting. The open-ended selector's preference for CL here lacks support from the maturity profile and should be justified or overridden.

### AY 2024 — Paid BF is clearly preferred over Paid CL

**Analyst's selection (open-ended AI):** Paid CL — $2,757,368 (IBNR $2,402,120)
**Rules-based AI selection:** Paid BF — $1,224,487 (IBNR $869,239)
**Reviewer's suggested alternative:** Paid BF — $1,224,487

**Rationale:** At 11 months and 13% paid developed, a CDF of 7.76 means the Paid CL ultimate is roughly 8× the current diagonal payment. This is the most leveraged point in the entire triangle and a single payment aberration could swing the CL ultimate by hundreds of thousands of dollars. BF methods exist specifically for this scenario. The open-ended selector's choice of CL "given maturity constraints and paid emergence patterns" is difficult to defend when 87% of the ultimate has not yet emerged. The rules-based selector is correct here. You may want to consider whether even BF is sufficiently anchored — at this age, an exposure-based or pure a priori approach may also be appropriate.

**Combined reserve impact if BF is adopted for both AY 2023 and AY 2024:**
- Reduction in selected Paid Loss ultimate: approximately **−$3,234,305**
- Reduction in total selected IBNR: approximately **−$3,234,305**

This represents a meaningful proportion of the total estimated reserve and should be flagged to the reviewing actuary.

### AY 2012 — Consider blending Paid and Incurred CL

**Analyst's selection:** Paid CL — $1,307,267
**Incurred CL indication:** $1,508,059
**Divergence:** 13.3% ($200,792)
**Reviewer's suggested alternative:** Average of Paid CL and Incurred CL — approximately $1,407,663

**Rationale:** At 155 months (nearly 13 years), a 13.3% gap between Paid and Incurred CL is unusually large for WC. Both methods have substantial development history at this maturity. The analyst selected Paid CL citing "superior fitness," but the selector reasoning also notes the Incurred CL shows elevated development (CDF 1.106) suggesting possible case reserve adverse movement. Before defaulting to Paid CL exclusively, you may want to consider whether the incurred signal (higher case reserves) is informative rather than noise. A 50/50 blend at $1,407,663 would be more conservative and may be warranted pending review of the AY 2012 open claim file.

---

*This peer review is advisory. No selections in the analysis workbook were modified. All proposed alternatives are for analyst consideration and should be accepted, rejected, or modified based on the analyst's independent actuarial judgment.*
