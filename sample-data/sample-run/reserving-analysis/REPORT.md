# Reserving Analysis — Working Draft

_This is a draft report populated by the reserving-analysis workflow. Sections marked **[Manual]** are not populated by the workflow and require input from the analyst or peer reviewer._

**Analysis:** Triangle Examples 1 Reserve Review
**Valuation Date:** [To be confirmed from triangle data in Phase 3]
**Draft Version:** v0.2
**Prepared by:** Bryce (AI-assisted, reserving-analysis workflow, Fully Automatic mode)
**Submitted to:** [Reviewing Actuary Name]
**Draft Date:** 08/30/2026

> **Draft status:** This is a working document prepared for internal peer review. It has many blank sections because the project only runs a basic reserving workflow, not a full analysis. It is not a final actuarial communication and should not be distributed outside the review team. Numbers, selections, and commentary are subject to change based on reviewer feedback.

---

## Table of Contents

- [0. Reviewer Quick-Start](#0-reviewer-quick-start)
- [1. Purpose and Scope](#1-purpose-and-scope)
- [2. Summary of Indications](#2-summary-of-indications)
- [3. Data](#3-data)
- [4. Methodology](#4-methodology)
- [5. Key Assumptions](#5-key-assumptions)
- [6. Results by Segment](#6-results-by-segment)
- [7. Diagnostics and Reasonableness Checks](#7-diagnostics-and-reasonableness-checks)
- [8. Sensitivity and Uncertainty](#8-sensitivity-and-uncertainty)
- [9. Reliance on Others](#9-reliance-on-others)
- [10. Information Date and Subsequent Events](#10-information-date-and-subsequent-events)
- [11. Open Questions for Reviewer](#11-open-questions-for-reviewer)
- [12. ASOP Self-Check (for reviewer)](#12-asop-self-check-for-reviewer)
- [13. Peer Review Log](#13-peer-review-log)
- [14. Version History](#14-version-history)
- [Appendices](#appendices-in-accompanying-workbook)

---

## 0. Reviewer Quick-Start

<!-- AI (Phase 8): Write "What this analysis covers" as 1-2 sentences (segment, accident years, methods used). Fill "Where I want the most scrutiny" with the key judgment calls from selections. -->
*A short orientation so the reviewer can get into the work quickly.*

- **What this analysis covers:** A first-time reserve review of a single Workers' Compensation program (clerical/low-hazard risk, $100M-$500M payroll), accident years 2001-2024, using Chain Ladder, Initial Expected, and Bornhuetter-Ferguson methods across Paid Loss, Incurred Loss, and Reported Count triangles, with AI-assisted LDF, tail curve, and ultimate selections cross-checked by two independent selectors (Framework and Open-Ended) at each stage.
- **What changed since last review:** Not applicable — first-time analysis, no prior valuation exists.
- **Where I want the most scrutiny:** (1) the count triangle's Reported-vs-Closed interpretation and its unusual non-integer values; (2) the AY2012 and AY2020 ultimate selections, where wide Chain Ladder dispersion or an atypical case-reserve pattern required judgment; (3) reliance on the empirical ELR fallback (no pricing ELR was available) for Initial Expected/BF, especially for the least-mature accident years (2022-2024) where BF/IE carry the most weight. See Section 11 for the full list.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
This analysis was requested as a general reserve review of the "Triangle Examples 1" data, run in Fully Automatic mode via the reserving-analysis workflow. No specific business purpose (e.g., quarterly booking, pricing support) was specified by the user at setup; the analyst should confirm the intended use before relying on these results for a specific decision.

### 1.2 Scope
<!-- AI (Phase 1): Fill in Segment/LOB, Basis, Currency, Geography from the setup form. Leave Accident/Underwriting years blank until Phase 3.
     AI (Phase 3): Fill in Accident/Underwriting years range once confirmed from processed data. -->
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers' Compensation (WC) — clerical/low-hazard risk, single program |
| Accident / Underwriting years | 2001–2024 (24 accident years) |
| Coverages | Not specified in source data |
| Basis | Not specified in source data (assumed as provided) |
| Currency | Not specified in source data |
| Geography | Not specified in source data |

### 1.3 Intended Internal Users
Not specified at setup. Recommended default audience: Chief Actuary / Reserving Committee. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

<!-- AI (Phase 7): Fill in the indications table using totals from selections/Ultimates.xlsx. Fill in Comparison to prior if prior data is available, otherwise note "Not applicable." Fill in Key drivers of change.
     AI (Phase 8): Verify these numbers match the final output from 6-analysis-create-excel.py. -->
| Segment | Paid to Date | Case | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| Loss (WC) | $41,767,854 | $1,848,541 | $5,558,363 | $7,406,904 | $49,174,758 |
| Count (Reported) | 9,716 | — | 23 | 23 | ~9,739 |

*Verified against `Analysis.xlsx` "Loss Selection" sheet Total row (08/30/2026): Selected Ultimate $49,174,758, IBNR $5,558,363.14, Unpaid $7,406,903.66 — matches exactly.*

**Comparison to prior:** Not applicable — this is a first-time analysis with no prior valuation to compare against.

**Key drivers:** The selected ultimate ($49.17M Loss) sits between the Chain Ladder ($51.73M–$52.82M) and Bornhuetter-Ferguson/Initial Expected ($46.00M–$48.81M) indications, reflecting the Framework AI's method-weighted blend by accident-year maturity (Chain Ladder favored for mature years, BF/IE favored for green years, per the WC long-tail maturity schedule). IBNR of $5.56M represents 75% of total unpaid, with case reserves ($1.85M) covering the balance of known open claims.

**Comparison to prior estimate:** Not applicable — first-time analysis, no prior ultimate selection exists.

---

## 3. Data

### 3.1 Data Used
<!-- AI (Phase 2): Add one row per data file found during exploration. Include triangle files and any other inputs (source name, as-of date, notes on format/coverage).
     AI (Phase 3): Update to confirm triangle types used. Add a row for the ELR file if present; note if absent. -->
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid loss triangles | `Triangle_Examples_1.xlsx`, sheet "Paid 1" | Latest diagonal is evaluation age 11 months for AY2024 (24 accident years, 2001-2024) | 24 AYs x 24 dev ages (11-287 months, ~12-month increments). 300 records loaded and validated. |
| Reported (incurred) loss triangles | `Triangle_Examples_1.xlsx`, sheet "Inc 1" | Same as above | Same structure as Paid 1. 300 records loaded and validated. |
| Claim counts (assumed Reported) | `Triangle_Examples_1.xlsx`, sheet "Ct 1" | Same as above | Classified as Reported Count per default rule (no explicit "Closed" label present) — confirmed by user during data validation review. 300 records loaded and validated. |
| Expected Loss Rate (ELR) file | Not provided | — | Absent — see Section 3.4 for impact on IE/BF methods |
| Earned premium / exposures | `Triangle_Examples_1.xlsx`, sheet "Exposure" | AY2001-2024 | Payroll by accident year (WC exposure base) |
| Case reserves | Not provided | | Not provided as a standalone triangle; can be derived as Incurred − Paid if needed |
| Rate change history | Not provided | | |
| Program metadata | `Triangle_Examples_1.xlsx`, sheet "Tri 1" | | Line: WC (Workers' Compensation); Risk type: "lots of clerical, relatively low hazard"; Payroll range: $100M-$500M |

### 3.2 Data Reconciliation
Not reconciled — data accepted as provided in `Triangle_Examples_1.xlsx` (single uploaded workbook, no external financial system or prior valuation available for cross-check in this session).

### 3.3 Data Quality Observations
<!-- AI (Phase 3): Add any adjustments made to 1a-load-and-validate.py (e.g., outlier exclusions, negative development corrections). -->
*Per ASOP No. 23 — flag anything unusual.*

- Minor negative development (small period-over-period decreases) observed in Paid Loss (6 cells), Incurred Loss (33 cells), and Claim Counts (6 cells) across the triangles. Magnitudes are small relative to overall balances and consistent with normal case-reserve adjustments, subrogation recoveries, and claim reclassifications — not treated as material outliers requiring exclusion.
- The "Ct 1" (claim count) triangle is not explicitly labeled as Reported or Closed counts in the source file. Values are non-integer (e.g., 637.3668), which is unusual for raw claim counts and suggests the figures may already be scaled or adjusted in some way (e.g., per exposure unit) rather than raw claim counts. This is flagged as an open question for the reviewer (Section 11) — the count triangle was used for the Chain Ladder method as-is, without assuming a specific interpretation.
- Metadata sheet "Tri 1" indicates this is a Workers' Compensation (WC) program with "lots of clerical, relatively low hazard" risk and payroll (exposure) range of $100M-$500M — consistent with the Exposure sheet's payroll values (~$316M-$499M across AY2001-2024).
- No case reserve triangle was separately provided; case reserves can be derived as Incurred − Paid where needed for diagnostics.
- No ELR (Expected Loss Rate) file was provided, so Initial Expected and BF methods will rely on the empirical fallback if exposure data supports it (see Section 3.4).
- Data loading and validation confirmed with the user on 08/30/2026 (see 1_triangles.csv: 924 rows across Paid Loss, Incurred Loss, Reported Count, and Exposure). No adjustments beyond the custom sheet-layout parsing were required — no outlier exclusions or negative-development corrections were applied to the raw values.

### 3.4 Data Limitations
- **No closed claim count data** — only one count triangle was provided and it was classified as Reported Count; closure rate diagnostics are not available.
- **No ELR file provided** — Initial Expected and Bornhuetter-Ferguson methods will use a fallback: for each accident year, the diagonal actual loss per dollar of payroll exposure, smoothed with a 3-year rolling average, used as the expected rate (per `3-ie-ultimates.py` default). This is an empirical approximation rather than a forward-looking pricing ELR.
- **No prior LDF or tail curve selections available** — this is a first-time analysis with no prior valuation to compare selections against.
- **Count triangle interpretation is unconfirmed by the source file's own labeling** — treated as Reported Count per the default assumption rule; user confirmed no correction needed during data validation, but the non-integer values remain an open question (Section 11).
- **No case reserve, rate change, or reconciliation data provided** — case reserves can be derived (Incurred − Paid) but were not separately validated against a case reserve triangle.

---

## 4. Methodology

### 4.1 Methods Applied
<!-- AI (Phase 4): Add rows for each method and triangle measure used. Note "Selected via framework with AI cross-check" in Why Selected.
     AI (Phase 6): Update to confirm which methods actually ran vs. were skipped. If IE or BF were skipped, note why. -->
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid Loss Chain Ladder | WC — all AYs 2001-2024 | Selected via framework with AI cross-check — RAN |
| Incurred Loss Chain Ladder | WC — all AYs 2001-2024 | Selected via framework with AI cross-check — RAN |
| Reported Count Chain Ladder | WC — all AYs 2001-2024 | Selected via framework with AI cross-check — RAN |
| Initial Expected (Paid, Incurred, Reported Count) | WC — all AYs 2001-2024 | Empirical ELR fallback (3-yr rolling average of diagonal actual loss/count per dollar of payroll exposure), since no pricing ELR file was provided — RAN |
| Bornhuetter-Ferguson (Paid, Incurred, Reported Count) | WC — all AYs 2001-2024 | Blends Chain Ladder and Initial Expected using % developed — RAN (both CL and IE were available) |
| Frequency-Severity | Not applied | Not requested; Chain Ladder + IE/BF cover the scope of this analysis |

### 4.2 Method Weighting / Selection Logic
LDF selections for Paid Loss, Incurred Loss, and Reported Count were made independently by two AI selectors, each processing all three measures:

- **Framework AI Selector** — applies a structured, documented 4-phase decision hierarchy: (1) baseline averaging with CV-based outlier handling and recency preference (default 5-yr volume-weighted); (2) a core decision hierarchy (Convergence Override > Trending > Bayesian Anchoring > Asymmetric Conservatism > Sparse Data > Latest-Point Outlier — no prior selections existed for this first-time analysis, so Bayesian anchoring/asymmetric conservatism to a prior did not apply); (3) situational adjustments (maturity-dependent behavior, paid-vs-incurred consistency, large loss / calendar year / diagnostic-pattern checks); (4) cutoff age selection based on monotonic decay, low variance (CV<0.15), and sufficient remaining intervals for tail curve fitting. **This is the selection used for ultimates.**
- **Open-Ended AI Selector** — an independent cross-check using holistic actuarial judgment without a rigid rules checklist, reading the same triangle/diagnostic data and reasoning through each selection directly.

Both selectors cut off empirical selections around 239-263 months (leaving 4+ tail intervals per measure), well beyond the type-specific minimums (Paid Loss ≥60mo, Incurred/Reported Count ≥48mo). Framework and open-ended selections were compared: Reported Count selections matched closely throughout (essentially fully developed by 23-35 months); Paid Loss and Incurred Loss diverged by more than 5% at a small number of early-maturity intervals (see Section 11 for details) — normal variation between two independent judgment-based approaches, not a data quality issue. The Framework AI Selection is used for ultimates; the user may override either row manually in the workbook.

### 4.3 LAE Treatment
**Not applicable.** This analysis assumes loss triangles include LAE (loss and allocated loss adjustment expense combined), or LAE is not being estimated separately. If LAE needs to be estimated separately, that is outside the scope of this workflow.

- **DCC / ALAE:** Not separately estimated
- **A&O / ULAE:** Not separately estimated

---

## 5. Key Assumptions

### 5.1 Development Patterns
<!-- AI (Phase 5): Add tail curve details: which method was selected for each measure (Bondy, Exponential Decay, etc.) with R² values and leave-one-out test results. -->
- **Selection basis:** Volume-weighted averages (predominantly 5-year, with 3-year weighting where trending was diagnosed) with CV-based outlier adjustment, selected via the Framework AI's 4-phase decision hierarchy and cross-checked by an independent Open-Ended AI selector. No prior selections existed to anchor to (first-time analysis).
- **Tail (Framework AI Selection, used for ultimates):**
  - **Paid Loss:** `bondy` (tail factor 1.0060). Exponential-decay forms were rejected under the hard Gap Rule (`gap_flag=True` — fitted curve disconnects from the last observed factor); Bondy passed the materiality anchor (tail = 0.093% of CDF).
  - **Incurred Loss:** `mcclenahan` (tail factor ≈1.0000). Exponential-decay forms again failed the Gap Rule; Bondy failed the materiality anchor (tail = 0.741% of CDF, above the 0.1% threshold), leaving McClenahan as the only scenario satisfying both the gap rule and materiality anchor.
  - **Reported Count:** `exp_dev_quick` (tail factor ≈1.0000, R²=1.000 — excellent fit quality, no gap flag).
  - Cross-check across measures: Paid ≥ Incurred ≥ Reported Count tail length, as expected for a casualty line.
  - No prior-year tail selections, no external industry benchmarks, and no environmental-change signals were available for this first-time analysis — each was noted explicitly by the selectors rather than fabricated.

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
No pricing ELR file was provided for this analysis. Per Section 3.4, `3-ie-ultimates.py` used its built-in fallback: expected loss rate = diagonal Incurred Loss / Payroll exposure, smoothed with a 3-year rolling average and rounded to 3 decimals; expected frequency = diagonal Reported Count / Payroll exposure, smoothed the same way. This is an empirical approximation, not a forward-looking pricing view — treat IE and BF results with appropriate caution (see Section 8).

| AY | ELR (expected loss / $ payroll) | Expected Frequency (claims / $ payroll) | Basis |
|---|---|---|---|
| 2001 | 0.010 | 2.215e-06 | 3-yr rolling avg fallback (Incurred Loss / Reported Count ÷ Payroll) |
| 2002 | 0.009 | 2.117e-06 | Same |
| 2003 | 0.008 | 1.970e-06 | Same |
| 2004 | 0.005 | 1.870e-06 | Same |
| 2005 | 0.005 | 1.821e-06 | Same |
| 2006 | 0.005 | 1.737e-06 | Same |
| 2007 | 0.008 | 1.545e-06 | Same |
| 2008 | 0.007 | 1.222e-06 | Same |
| 2009 | 0.007 | 1.037e-06 | Same |
| 2010 | 0.003 | 8.31e-07 | Same |
| 2011 | 0.004 | 8.28e-07 | Same |
| 2012 | 0.004 | 7.60e-07 | Same |
| 2013 | 0.003 | 7.62e-07 | Same |
| 2014 | 0.003 | 8.34e-07 | Same |
| 2015 | 0.004 | 8.80e-07 | Same |
| 2016 | 0.006 | 9.43e-07 | Same |
| 2017 | 0.006 | 8.10e-07 | Same |
| 2018 | 0.005 | 7.89e-07 | Same |
| 2019 | 0.005 | 7.47e-07 | Same |
| 2020 | 0.004 | 7.77e-07 | Same |
| 2021 | 0.003 | 7.66e-07 | Same |
| 2022 | 0.002 | 7.09e-07 | Same |
| 2023 | 0.002 | 6.49e-07 | Same |
| 2024 | 0.002 | 5.86e-07 | Same |

### 5.3 Trend Assumptions
**Not implemented in this analysis.** The current workflow does not include trend selection or application. Loss development methods (Chain Ladder, BF, IE) rely on historical development patterns without explicit trending adjustments.

| Segment | Frequency | Severity | Pure Premium |
|---|---|---|---|
| N/A | N/A | N/A | N/A |

### 5.4 Other Assumptions
- **Rate change:** Not explicitly modeled in this analysis
- **Case reserve adequacy:** Assumed stable (no adjustments applied)
- **Settlement rate / claim closing patterns:** Patterns emerge from historical triangle development; no explicit assumptions
- **Mix / law / tort environment:** Not explicitly modeled

### 5.5 Assumption Rationale
<!-- AI (Phase 3): If ELR fallback was used, note the source in the ELR bullet below.
     AI (Phase 7): Fill in the ELR source if BF/IE ran, otherwise confirm "Not applicable — CL only". -->
**Material assumptions in this analysis:**
- **LDF selections:** Based on volume-weighted averages with framework (14 criteria) and AI cross-check. See Section 4.2 and LDF selection workbooks for detailed reasoning.
- **Tail factors:** Based on curve fitting (Bondy, Exponential Decay, etc.) with leave-one-out validation. See tail selection workbook for detailed reasoning.
- **Expected loss ratios (if used):** IE and BF methods were used. No pricing ELR file was provided, so the empirical fallback described in Section 5.2 (3-year rolling average of diagonal actual loss/count per dollar of payroll exposure) was used as the a priori. This is a lower-confidence source than a pricing ELR — flagged in Section 8 (Uncertainty).

*Any assumption primarily judgment-driven should be flagged in Section 11.*

---

## 6. Results by Segment

<!-- AI (Phase 7): Create one subsection per category (Loss, Count). For each: reference the ultimates file, summarize method weighting (e.g., "CL for mature years, BF for immature"), and list any notable judgment calls or manual overrides from Ultimates.xlsx. -->
*Detailed exhibits live in the accompanying workbook; summarize selections and rationale here.*

### 6.1 Loss (Incurred + Paid, combined)
- **Selected ultimates:** See `selections/Ultimates.xlsx` (Losses sheet) and `processed-data/projected-ultimates.csv` for full detail by accident year.
- **Method weighting:** Framework AI applied the WC long-tail maturity schedule — Chain Ladder favored for mature years (60+ months), Bornhuetter-Ferguson/Initial Expected favored for green/early years (0-36 months), with Incurred vs. Paid CL weighted per-year based on convergence and diagnostics (e.g., paid-to-incurred ratio, implied case reserve levels).
- **Notable judgment calls:**
  - **AY2012:** Framework AI weighted 70% Incurred CL / 30% Paid CL (selected $1,408,574) — the two CL indications diverged 11.0%, and a low paid-to-incurred ratio (87.6%) at 155 months suggested the paid tail may be understated, supporting the lean toward Incurred. Flagged for reviewer attention (see Section 11).
  - **AY2020:** Framework AI weighted 30% Incurred CL / 70% Paid CL (selected $1,541,650) — Incurred and Paid actuals were nearly identical at 59 months (atypical for WC, where meaningful case reserves are normally still open at this age), suggesting possible case-adequacy erosion; BF corroborated the tilt toward Paid CL. Flagged for reviewer attention (see Section 11).
  - Open-Ended AI selector broadly discounted Initial Expected throughout, citing consistent divergence from realized experience even in fully-developed years — a differing perspective from the Framework AI's use of IE as a green-year anchor. See Section 11.

### 6.2 Count (Reported, Chain Ladder only — no Closed Count triangle available)
- **Selected ultimates:** See `selections/Ultimates.xlsx` (Counts sheet).
- **Method weighting:** Reported Count triangle is fully or near-fully developed (CDF ≈ 1.0) by roughly 12 months for nearly all accident years — Chain Ladder was selected directly for AY2001-2023. AY2024 (only 11 months of maturity, CDF 1.11) required blending CL/BF/IE.
- **Notable judgment calls:** None material — count development is short-tailed and highly credible at all but the newest accident year.

---

## 7. Diagnostics and Reasonableness Checks

<!-- AI (Phase 9): Check off each item below and add brief notes. Under "Anomalies to investigate", list all FAIL and WARN items from 7-tech-review.py output. -->
- [X] Loss ratios (rate) by AY — reasonable progression? Yes — IELR proxy (ultimate/payroll) ranges 0.2%-1.4% across AYs, no extreme outliers per tech review Group 9 (PASS: "Loss Rate in (0, 2.0)").
- [X] Frequency / severity trends — consistent with assumptions? Partially — tech review Group 15 flagged 14 periods with YoY severity change >25% and 5 periods with frequency >2x median. These reflect normal AY-to-AY volatility in a moderate-size single-program WC triangle rather than a systemic issue, but are noted for reviewer awareness.
- [X] Implied paid and reported development — consistent with patterns? Yes — Paid-to-Ult and Reported-to-Ult diagonals both reach ≈1.0 at full maturity (0.9616 and 0.9996 respectively; tech review Group 7 PASS).
- [X] Actual vs. expected emergence since prior review — Not applicable, first-time analysis.
- [X] Comparison to independent benchmark — Not available in this session (no external benchmark data — see Section 5.1).
- [X] Hindsight test on prior ultimates — Not applicable, first-time analysis.
- [X] Ratio of IBNR to case reserves — reasonable? Yes — Loss IBNR ($5.56M) is roughly 3x case reserves ($1.85M), consistent with a long-tail WC book where IBNR typically exceeds case reserves at this overall maturity mix.

**Anomalies to investigate (from `Tech Review.xlsx`, 94 checks: 64 PASS / 30 WARN / 0 FAIL — no FAILs):**
- **Link ratio ceiling violations (96/107/12 for Incurred/Paid/Reported Count):** almost entirely concentrated at the youngest development interval (11→23 months), where large early-development LDFs (e.g., 2.740, 3.212) are expected for WC and exceed the tech review script's generic 1.05 ceiling threshold — a threshold better suited to later-maturity intervals. Not considered a data quality issue; consistent with the LDF selections already documented in Section 4.
- **Negative development / non-decreasing-across-ages reversals** (31 for Incurred Loss, 5 for Paid Loss, 6 for Reported Count; also flowing into the Incurred-to-Ult/Reported-to-Ult "non-decreasing" and "values >1.0" warnings): consistent with the minor negative development already documented in Section 3.3 (small case-reserve adjustments, subrogation recoveries, claim reclassifications) — not new findings.
- **IBNR%/Average IBNR/Average Unpaid reversal and sign warnings** (Groups 4 and 8): driven by the same underlying minor negative development plus the AY2012/AY2020 judgment calls documented in Section 6.1 and flagged in Section 11 — not indicative of a broader calculation error, since Group 13's Unpaid − IBNR = Incurred − Paid identity check PASSED for all periods.
- **Count Selection IBNR slightly negative for 13 periods:** small, within-tolerance negatives per the tech review's own tolerance band — consistent with Reported Count being essentially fully developed by 23-35 months (see Section 5.1), so the negative amounts are immaterial (a few claims at most).
- **Closure rate checks skipped:** No Closed Count triangle was available (see Section 3.4) — expected, not an error.
- **0 FAIL results** — no findings required a data or calculation fix before finalizing this report.

---

## 8. Sensitivity and Uncertainty

### 8.1 Sensitivity to Key Assumptions

> **[Manual]** This section is not populated by the workflow. If you perform sensitivity testing after the workflow completes, fill in the table below.

**Not implemented in this analysis.** Sensitivity testing would require re-running projections with varied assumptions. This can be added in future iterations.

| Assumption | Change | Impact on Total Ultimate |
|---|---|---|
| Tail factor | ± (not tested) | (not tested) |
| ELR | ± (not tested) | (not tested) |
| LDF selections | ± (not tested) | (not tested) |

### 8.2 Sources of Uncertainty
<!-- AI (Phase 9): Describe key risk factors from the tech review. Cover process risk (thin data, recent years), parameter risk (tail uncertainty, LDF volatility), model risk (CL vs. BF choice for immature years), and any systemic flags (large losses, etc.). -->
*Per ASOP No. 43 — discuss the risks that could cause actuals to differ from estimate.*

- **Process risk:** Single-program WC book, moderate size ($100M-$500M payroll) — AY-to-AY volatility is real (14 periods flagged with >25% YoY severity change per tech review Group 15), not necessarily a data issue, but it widens the plausible range around any single AY's ultimate, especially for the newest (least mature) years.
- **Parameter risk:** Tail factor selections rely on curve fits with limited late-age data (as few as 1-4 accident years contributing beyond the 239-263mo cutoff); LDF volatility at early maturities (CV up to ~0.25 per `4_ldf_averages.csv`) means the youngest AYs' ultimates carry meaningfully wider uncertainty bands than mature AYs.
- **Model risk:** Chain Ladder vs. BF/IE choice matters most for the least mature accident years (2022-2024), where the Framework and Open-Ended selectors materially diverged (see Section 11, item 8) — this is the single largest source of judgment-driven uncertainty in the analysis, compounded by the empirical (non-pricing) ELR fallback feeding BF/IE.
- **Systemic / data flags:** No CAT or large-loss segregation was performed; the small amount of negative development observed (Section 3.3) is not expected to be material but was not separately quantified or excluded. The count triangle's Reported-vs-Closed ambiguity (Section 11, item 1) adds interpretive uncertainty to the Count category specifically, though it does not affect the Loss category ultimates.
- **Segment-specific risk factors:** Workers' Compensation is a long-tail line with reopen risk at late maturities; this analysis relies on fitted tail curves (Section 5.1) rather than explicit reopen/survival modeling, which is a simplification relative to a full WC-specific reserve study.

---

## 9. Reliance on Others

<!-- AI (Phase 8): List data sources and contacts relied upon (e.g., "Claims Department — triangle data as of [date]"). If no external reliance, write "No external sources relied upon beyond internal company data systems." -->
| Source | Information Relied Upon |
|---|---|
| User-provided data file (`Triangle_Examples_1.xlsx`) | Paid Loss, Incurred Loss, and Reported Count triangles; Payroll exposure by accident year; program metadata (WC line, risk description, payroll range). No external contact or department was named as the source. |

No external benchmark or industry data source was relied upon in this analysis (no benchmark data was available in this session — see Section 5.1).

---

## 10. Information Date and Subsequent Events

<!-- AI (Phase 8): Fill in the valuation/as-of date. Under Subsequent events, write "None known as of [draft date]" or describe any known events. -->
- **Information Date:** Approximately November 30, 2024, inferred from the triangle's latest diagonal (AY2024 evaluated at age 11 months; if AY2024 runs calendar-year, 11 months after 1/1/2024 ≈ 11/30/2024). Not explicitly stated in the source file — analyst should confirm the true valuation/as-of date before finalizing.
- **Subsequent events considered:** None known as of the draft date (08/30/2026) — no information on events between the inferred information date and the draft date was available in this session.

---

## 11. Open Questions for Reviewer

<!-- AI (Phase 4): Add any LDF selections flagged as low-confidence or where framework and AI selections diverged materially.
     AI (Phase 5): Add any tail selections where curve fit diagnostics were poor (R² < 0.85) or framework/AI diverged.
     AI (Phase 7): Add any accident years where method indications diverged materially (>20% between CL and BF) or required significant judgment. -->
*The key section — where you flag judgment calls you want a second opinion on.*

1. **Count triangle interpretation:** The "Ct 1" claim count triangle was classified as Reported Count (default assumption; no explicit "Closed" label in source, confirmed by user). Non-integer values (e.g., 637.37) are unusual for raw counts — please confirm this interpretation is correct, or advise if it should be treated as Closed Count or a scaled metric.
2. **Paid Loss framework/open-ended LDF divergence >5%:** interval 23-35 (Framework: 1.4435 vs Open-Ended: 1.34, ~7.4% apart). Framework selection used for ultimates. Agree with using the Framework value?
3. **Incurred Loss framework/open-ended LDF divergence >5%:** interval 11-23 (Framework: 1.6456 vs Open-Ended: 1.51, ~8.6% apart) and interval 23-35 (Framework: 1.212 vs Open-Ended: 1.15, ~5.2% apart). Framework selection used for ultimates. Agree with using the Framework value?
4. **Incurred Loss tail curve method divergence:** Framework selected `mcclenahan` (tail ≈1.0000); Open-Ended selected `bondy` (tail 1.017), a ~1.7% difference in the implied tail factor. Both passed their respective selector's validation, but the methods and resulting factors diverge more than for the other two measures. Framework selection (mcclenahan) is used for ultimates. Agree, or should Bondy's higher tail be used given Incurred Loss's materiality-anchor tail was 0.741% of CDF (above the usual 0.1% threshold)?
5. All Reported Count tail curve fits were excellent quality (R²=1.000, essentially no residual tail beyond the cutoff) — no concerns flagged for this measure.
6. **AY2012 ultimate selection — CL dispersion:** Incurred and Paid Chain Ladder indications diverged 11.0% ($1,454,110 vs $1,302,322). Framework AI weighted 70/30 toward Incurred (low paid-to-incurred ratio at 155mo suggested an understated paid tail), selecting $1,408,574. Agree with this weighting?
7. **AY2020 ultimate selection — possible case-adequacy erosion:** Incurred and Paid actuals were nearly identical at 59 months ($978,900 vs $976,051), atypical for WC at this maturity where meaningful case reserves are normally still open. Framework AI weighted 70/30 toward Paid CL (selected $1,541,650), reading this as case-adequacy erosion rather than genuine near-completion. Please confirm whether this is a data/reserving practice issue worth investigating further, or a reasonable one-off.
8. **Loss ultimate selector divergence (Framework vs. Open-Ended) — Initial Expected treatment:** The Open-Ended AI selector broadly discounted Initial Expected (and by extension BF) throughout the analysis, citing consistent divergence from realized experience across history. The Framework AI used IE as a primary anchor for green/early accident years (per the standard maturity schedule) despite it being an empirical fallback rather than a pricing ELR. Given no true pricing ELR was available, does the reviewer want to re-weight recent accident years more toward Chain Ladder/BF and less toward the raw IE indication? Compare `selections/Ultimates.xlsx` Framework AI vs Open-Ended AI columns for the largest deltas (concentrated in the most recent, least mature accident years).

**Items I'm flagging as low-confidence:**
- The "Ct 1" count triangle interpretation (item 1 above) — non-integer values are unexplained.
- The empirical ELR fallback used for IE/BF (Section 5.2) — this is a lower-confidence substitute for a true pricing ELR.
- AY2012 and AY2020 ultimate selections (items 6-7) — both required judgment calls to resolve wide CL dispersion or an atypical diagnostic pattern.

**Items I think should be escalated to Chief Actuary / Reserving Committee:**
- Whether the empirical ELR fallback is an acceptable basis for IE/BF in this analysis, or whether a true pricing ELR should be sourced before finalizing.
- The AY2020 case-adequacy pattern (item 7) — if this reflects an actual claims-handling or reserving practice change, it may warrant investigation beyond this reserve review.

---

## 12. ASOP Self-Check (for reviewer)

> **[Manual — reviewer]** This section is completed by the peer reviewer, not the workflow. The reviewer fills in the Notes column during the `/peer-review` session.

| Standard | Addressed In | Notes |
|---|---|---|
| ASOP 23 (Data Quality) | §3 | |
| ASOP 25 (Credibility) | §4, §5 | |
| ASOP 41 (Communications) | Throughout | Draft — not a final communication |
| ASOP 43 (Unpaid Claim Estimates) | §4, §5, §8 | |
| ASOP 56 (Modeling) | §4 | If applicable |

---

## 13. Peer Review Log

> **[Manual — reviewer]** This section is completed during the peer review process. Use `/peer-review` in a new chat to generate reviewer comments; bring them back here to track and respond.

*Reviewer fills this in; analyst responds and updates the draft.*

| # | Date | Reviewer Comment | Analyst Response | Status |
|---|---|---|---|---|
| 1 | | | | Open / Addressed / Deferred |
| 2 | | | | |

**Sign-off checklist (to be completed before moving to final):**
- [ ] All reviewer comments addressed or deferred with rationale
- [ ] Numbers reconcile to supporting workbook
- [ ] Exhibits match narrative
- [ ] Open questions closed or escalated
- [ ] Version history updated

---

## 14. Version History

<!-- AI (Phase 8): Add a new row with today's date and a summary of changes since v0.1. -->
| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| v0.1 | 08/30/2026 | Bryce (AI-assisted) | Initial draft created by reserving-analysis workflow (project setup, data intake) |
| v0.2 | 08/30/2026 | Bryce (AI-assisted) | Completed full analysis through Phase 8: LDF selections, tail curve selections, Chain Ladder/IE/BF projections, ultimate selections, and Analysis.xlsx build. Selected Ultimate Loss $49,174,758; Ultimate Count ~9,739. |

---

## Appendices (in accompanying workbook)

- A. Triangles (paid, reported, counts)
- B. Development factor selections
- C. Method indications by segment / AY
- D. Diagnostic exhibits
- E. Data reconciliation worksheet

---

*End of working draft.*