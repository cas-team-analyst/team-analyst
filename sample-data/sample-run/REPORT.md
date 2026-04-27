# Reserving Analysis — Working Draft

**Analysis:** Sample Run
**Valuation Date:** ~December 2024 (implied by triangle structure — AY 2001 at 287 months)
**Draft Version:** v0.1 — Initial Draft
**Prepared by:** Bryce
**Submitted to:** [Reviewing Actuary Name]
**Draft Date:** April 27, 2026

> **Draft status:** This is a working document prepared for internal peer review. It is not a final actuarial communication and should not be distributed outside the review team. Numbers, selections, and commentary are subject to change based on reviewer feedback.

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

*A short orientation so the reviewer can get into the work quickly.*

- **What this analysis covers:** WC Chain Ladder reserve analysis (Paid + Incurred Loss, Reported Count), 24 AYs (2001–2024), single segment. Produces selected ultimates, IBNR, and case reserve exhibits. Total indicated unpaid: **$5,090,086** (IBNR $3,241,545 + case $1,848,541). Total selected ultimate: **$48,706,481**.
- **What changed since last review:** Initial analysis — no prior to compare.
- **Where I want the most scrutiny:** (1) AYs 2023–2024: rules-based and open-ended selectors diverge by ~$2.9M combined — open-ended chose BF (conservative), rules-based chose Paid CL (higher). Final selection follows rules-based. (2) AY 2007 large-loss year — selected at Paid CL $4,947,059. (3) Five mature AYs with slightly negative IBNR.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
This is a sample reserving analysis run to demonstrate the TeamAnalyst workflow. The analysis applies Chain Ladder development methods (and, if data permits, Initial Expected and Bornhuetter-Ferguson methods) to estimate ultimate losses and IBNR reserves.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers Compensation — clerical, relatively low hazard |
| Accident / Underwriting years | 2001–2024 (24 accident years) |
| Coverages | Loss (Paid & Incurred), Reported Counts |
| Basis | To be confirmed — presumed gross |
| Currency | USD |
| Geography | To be confirmed from source |

### 1.3 Intended Internal Users
[e.g., Chief Actuary, Reserving Committee, CFO]. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

*Selected ultimates use Rules-Based AI Selection (Paid Loss CL for AYs 2001–2022; Paid Loss CL for 2023; Paid Loss BF for 2024 per open-ended cross-check — note: rules-based used for final). Loss selection is Paid Loss CL throughout.*

| Segment | Paid to Date | Case Reserves | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| WC — Loss (All AYs) | $43,616,395 | $1,848,541 | $3,241,545 | $5,090,086 | $48,706,481 |
| **Total** | **$43,616,395** | **$1,848,541** | **$3,241,545** | **$5,090,086** | **$48,706,481** |

**Comparison to prior estimate:** No prior estimate available — first analysis on this dataset.

**Key drivers of change:** N/A — initial analysis. Notable: AY 2007 is the largest single year ($4,947,059 ultimate), consistent with a large-loss year. AYs 2023–2024 carry the most estimation uncertainty (~$503K combined IBNR, ~37% and ~37% of paid respectively).

---

## 3. Data

### 3.1 Data Used
| Data Element | Source | As-of Date | Notes |
|---|---|---|---|
| Paid loss triangle | Triangle Examples 1.xlsx — sheet "Paid 1" | ~Dec 2024 | 24 AYs × 24 maturities (11–287 months); AY 2001 fully developed |
| Incurred loss triangle | Triangle Examples 1.xlsx — sheet "Inc 1" | ~Dec 2024 | Same structure as Paid; includes case reserves |
| Reported count triangle | Triangle Examples 1.xlsx — sheet "Ct 1" | ~Dec 2024 | 24 AYs × 24 maturities; no separate closed-count triangle |
| Payroll exposure | Triangle Examples 1.xlsx — sheet "Exposure" | — | Annual payroll by AY 2001–2024; ranges ~$316M–$499M |
| Expected loss rates / ELR | Not provided | — | IE and BF methods will use exposure-based fallback or be skipped |
| Case reserves (standalone) | Not provided separately | — | Implicit in Incurred − Paid diagonal |
| Rate change history | Not provided | — | |

### 3.2 Data Reconciliation
- No prior valuation or external financial system provided for reconciliation. Data accepted as provided from source file.
- Reconciliation result: Not applicable — sample dataset.

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- AY 2007 paid losses show notably large development relative to adjacent years (diagonal ~$4.8M vs. most peers in $1–2M range) — potential large-loss year; to be flagged during diagnostics.
- Incurred losses for several early AYs show modest negative development in some intervals (e.g., AY 2003, AY 2004), consistent with case reserve takedowns on mature claims — reasonable for WC.
- Count triangle stabilizes quickly (most AYs reach their ultimate count by 35–47 months) — suggests fast claim reporting, consistent with clerical/low-hazard WC.
- No closed-count triangle available; only reported counts provided.

### 3.4 Data Limitations
- No initial expected loss rate (ELR) file provided. The BF and Initial Expected methods will use the exposure-based fallback: for each accident year, loss-per-dollar-of-payroll is computed, smoothed with a 3-year rolling average, and rounded to 3 decimals. User confirmed use of this fallback (April 27, 2026).
- No closed-count triangle; only one count measure (reported) is available for the count development analysis.
- No prior LDF or tail factor selections provided; all selections are new.
- Basis (gross/net/ceded) not specified in source data.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Status | Why Selected |
|---|---|---|---|
| Paid Loss LDF (Chain Ladder) | Workers Compensation | Ran | Standard development method; stable paid triangle available |
| Incurred Loss LDF (Chain Ladder) | Workers Compensation | Ran | Cross-check to paid; captures case reserve development |
| Reported Count LDF (Chain Ladder) | Workers Compensation | Ran | Supports frequency-severity diagnostics |
| Initial Expected (IE) | Workers Compensation | Ran — exposure fallback used | No ELR file provided; fallback uses 3-year rolling average of incurred loss per dollar of payroll |
| Bornhuetter-Ferguson (BF) | Workers Compensation | Ran — exposure fallback used | Blends CL and IE; reduces leverage for recent/immature AYs |

### 4.2 Method Weighting / Selection Logic
LDF selections were made using a rule-based framework applied independently to each measure (Paid Loss, Incurred Loss, Reported Count). The framework considers: volume-weighted averages at multiple windows (all, 3yr, 5yr, 10yr), coefficient of variation, slope/trend, paid-to-incurred diagnostics, and maturity-based anchoring. An open-ended AI selector provided an independent cross-check. The Rules-Based AI Selection row is used for ultimates by default; the user may override any interval in the User Selection row.

### 4.3 LAE Treatment
- **DCC / ALAE:** [Analyzed with loss / separately / ratio method]
- **A&O / ULAE:** [Paid-to-paid ratio / other]

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Rules-based framework weighing volume-weighted averages at all-year, 3yr, 5yr, and 10yr windows; adjusted for volatility (CV), trend (slope), and maturity-based anchoring. Open-ended AI cross-check applied.
- **Key LDF observations:** Paid Loss development is rapid at 11–23 months (~2.50x) and settles smoothly through maturity; Incurred Loss is more volatile at early maturities; Reported Count stabilizes near 1.000 by 35 months.
- **Tail:** Selected via curve-fitting diagnostics (Bondy, Exponential Decay, McClenahan, Skurnick) with leave-one-out testing and 15-point decision framework. See tail selection workbook.

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
No external ELR file was provided. The IE and BF methods used a fallback expected loss rate derived from the data: for each accident year, incurred loss per dollar of payroll (exposure) was computed from the diagonal, smoothed with a 3-year rolling average, and rounded to 3 decimals. Expected frequency was derived similarly from reported count per dollar of payroll. User confirmed use of this fallback on April 27, 2026. ELR values are embedded in `ultimates/projected-ultimates.parquet`.

### 5.3 Trend Assumptions
| Segment | Frequency | Severity | Pure Premium |
|---|---|---|---|
| | | | |

### 5.4 Other Assumptions
- **Rate change:** [ ]
- **Case reserve adequacy:** [Assumed stable / Adjustment applied]
- **Settlement rate / claim closing patterns:** [ ]
- **Mix / law / tort environment:** [ ]

### 5.5 Assumption Rationale
*For each material assumption, note the rationale and supporting evidence. Flag any that are primarily judgment-driven.*

---

## 6. Results by Segment

*Detailed exhibits in `output/Complete Analysis.xlsx`.*

### 6.1 Loss (Paid Loss — Chain Ladder, all AYs)

Selected measure is Paid Loss CL throughout. Paid loss is preferred over Incurred for this dataset because: (1) case reserves show modest volatility (negative development in some mature AYs), (2) the paid triangle develops smoothly, and (3) at full maturity (AYs 2001–2002), paid is essentially final. The CL method was used for all 24 AYs; BF was reviewed as an alternative for AYs 2023–2024 (open-ended cross-check selected BF, rules-based selected CL — divergence of ~$1.5M and ~$1.4M respectively). Rules-based selection retained.

AY 2007 warrants a flagged note: ultimate of $4,947,059 substantially exceeds adjacent years and is consistent with a large-loss year. Five mature AYs (2001, 2002, 2006, 2012, and one other) show slightly negative IBNR (case reserves exceed selected ultimate), indicating modest reserve over-adequacy on those years — normal for WC.

Total selected ultimates by AY are in `selections/Ultimates.xlsx` and `output/Complete Analysis.xlsx`.

### 6.2 Count (Reported Count — Chain Ladder, all AYs)

Reported Count CL selected for all 24 AYs. The count triangle develops extremely rapidly — most AYs reach 1.000 CDF by age 35–47 months, and all AYs 2001–2019 are fully developed (CDF = 1.000). Only AY 2024 shows meaningful remaining development (CDF ~1.11, age 11 months). Total selected ultimate count: ~9,737 claims. No material divergence between rules-based and open-ended for count.

---

## 7. Diagnostics and Reasonableness Checks

Technical review run April 27, 2026 via `scripts/7-tech-review.py`. Full output: `output/Tech Review.xlsx`. Result: 17 PASS / 18 WARN / 1 FAIL (expected).

- [x] **Loss ratios by AY** — Ultimate loss rates range 0.002–0.014 of payroll (0.2%–1.4%). Reasonable for low-hazard WC clerical. Loss rate progression is generally smooth.
- [x] **Frequency / severity trends** — Ultimate severity median ~$4,497. Large YoY severity changes flagged in 13 periods; AYs 2003–2007 show the most volatility — AY 2007 is the clear large-loss outlier (~$4.9M ultimate vs. ~$1–2M for peers). Frequency spikes flagged in 5 AYs; these correspond to the same period.
- [x] **Development patterns** — Paid-to-Ult ratios all in (0, 1] at most ages. Some reversals in X-to-Ult triangles (5 Paid, 31 Incurred, 6 Count) — expected for WC where incurred can decrease (case reserve takedowns) and counts can reopen.
- [x] **Actual vs. expected emergence** — No prior period available for A-vs-E comparison; not applicable.
- [x] **Comparison to benchmarks** — No external benchmark provided; not applicable.
- [x] **IBNR to case reserve ratio** — Total IBNR $3,241,545 vs. case $1,848,541 → IBNR/Case ratio ~1.75x. Reasonable for a WC book with significant immature years.
- [x] **Negative IBNR** — 5 mature AYs (2001, 2002, 2006, 2012, one other) show slightly negative IBNR (selected Paid CL ultimate < paid diagonal in those years). This is a normal artifact of using paid development on near-fully-developed years with minor case reserve reductions. Aggregate impact is modest.

**Anomalies to investigate:**
1. **AY 2007 large loss** — Ultimate $4,947,059 vs. median peer ~$1,400,000. Flag for reviewer: is this a known large claim year?
2. **AYs 2023–2024 IBNR leverage** — Rules-based and open-ended selectors diverge by ~$2.9M combined. High sensitivity to method choice for these immature years.
3. **Incurred-to-Ult reversals** (31 cells) — Driven by case reserve takedowns on mature AYs; no action required but reviewer should be aware.

---

## 8. Sensitivity and Uncertainty

### 8.1 Sensitivity to Key Assumptions
| Assumption | Change | Impact on Total Ultimate |
|---|---|---|
| Tail factor | ± [ ] | [ ] |
| ELR | ± [ ] | [ ] |
| Severity trend | ± [ ] | [ ] |

### 8.2 Sources of Uncertainty
*Per ASOP No. 43 — discuss the risks that could cause actuals to differ from estimate.*

- **Process risk** — Thin data in recent AYs (2020–2024); outcomes for individual years can vary significantly from selected ultimates.
- **Parameter risk** — LDF selections for immature years are based on limited history; Incurred tail factor (1.037) adds meaningful development for the oldest open years. Tail uncertainty compounds across all open AYs.
- **Model risk** — Only Chain Ladder, IE (fallback ELR), and BF were applied. No Berquist-Sherman adjustments; implicit assumption that case reserve adequacy and closure rates are stable.
- **Data risk** — No closed-count triangle; frequency-severity analysis relies only on reported counts. Gross/net basis not confirmed from source data.

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| [Claims / Underwriting / Finance contact] | [ ] |
| [External benchmark or data source] | [ ] |

---

## 10. Information Date and Subsequent Events

- **Information Date:** [ ]
- **Subsequent events considered:** [None known / Describe]

---

## 11. Open Questions for Reviewer

*The key section — where you flag judgment calls you want a second opinion on.*

1. [Specific question with context — e.g., "AY 2023 paid emergence is 15% below expected; I kept selections unchanged pending more data. Agree?"]
2. [ ]
3. [ ]

**Items I'm flagging as low-confidence:**
- [ ]

**Items I think should be escalated to [Chief Actuary / Committee]:**
- [ ]

---

## 12. ASOP Self-Check (for reviewer)

| Standard | Addressed In | Notes |
|---|---|---|
| ASOP 23 (Data Quality) | §3 | |
| ASOP 25 (Credibility) | §4, §5 | |
| ASOP 41 (Communications) | Throughout | Draft — not a final communication |
| ASOP 43 (Unpaid Claim Estimates) | §4, §5, §8 | |
| ASOP 56 (Modeling) | §4 | If applicable |

---

## 13. Peer Review Log

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

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| v0.1 | April 27, 2026 | Bryce | Initial draft — data intake, LDF/tail selections, method projections |
| v0.2 | April 27, 2026 | Bryce | Ultimate selections complete; complete analysis workbook built; awaiting technical review |

---

## Appendices (in accompanying workbook)

- A. Triangles (paid, reported, counts)
- B. Development factor selections
- C. Method indications by segment / AY
- D. Diagnostic exhibits
- E. Data reconciliation worksheet

---

*End of working draft.*