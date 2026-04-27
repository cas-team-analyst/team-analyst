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

- **What this analysis covers:** [1–2 sentences]
- **What changed since last review (if applicable):** [Bullet the deltas]
- **Where I want the most scrutiny:** [Point the reviewer at the judgment calls]
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

*Placeholder numbers — subject to review.*

| Segment | Paid to Date | Case | IBNR | Total Unpaid | Ultimate |
|---|---|---|---|---|---|
| [ ] | | | | | |
| [ ] | | | | | |
| **Total** | | | | | |

**Comparison to prior estimate:**

| Segment | Prior Ultimate | Current Ultimate | Change | % |
|---|---|---|---|---|
| [ ] | | | | |

**Key drivers of change:** [Brief narrative — emergence vs. expected, assumption changes, new data, etc.]

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
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid Loss LDF | Workers Compensation | Standard development method; stable paid triangle available |
| Incurred Loss LDF | Workers Compensation | Cross-check to paid; captures case reserve development |
| Reported Count LDF | Workers Compensation | Supports frequency-severity diagnostics |
| Initial Expected (IE) | Workers Compensation | Exposure-based fallback ELR; useful for immature years |
| Bornhuetter-Ferguson | Workers Compensation | Blends LDF and IE; reduces leverage for recent AYs |

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
| AY | ELR | Basis |
|---|---|---|
| | | |

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

*Detailed exhibits live in the accompanying workbook; summarize selections and rationale here.*

### 6.1 [Segment A]
- Selected ultimates: [Reference exhibit]
- Method weighting: [Summary]
- Notable judgment calls: [ ]

### 6.2 [Segment B]
- [ ]

---

## 7. Diagnostics and Reasonableness Checks

- [ ] Loss ratios by AY — reasonable progression?
- [ ] Frequency / severity trends — consistent with assumptions?
- [ ] Implied paid and reported development — consistent with patterns?
- [ ] Actual vs. expected emergence since prior review
- [ ] Comparison to independent benchmark (if available)
- [ ] Hindsight test on prior ultimates
- [ ] Ratio of IBNR to case reserves — reasonable?

**Anomalies to investigate:** [List anything the diagnostics flagged]

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

- Process / parameter / model / systemic risk commentary as applicable
- Segment-specific risk factors: [ ]

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
| v0.1 | April 27, 2026 | Bryce | Initial draft |
| v0.2 | | | |

---

## Appendices (in accompanying workbook)

- A. Triangles (paid, reported, counts)
- B. Development factor selections
- C. Method indications by segment / AY
- D. Diagnostic exhibits
- E. Data reconciliation worksheet

---

*End of working draft.*