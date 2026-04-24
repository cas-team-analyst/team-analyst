# Reserving Analysis — Working Draft

**Analysis:** Workers Compensation - Chain Ladder Analysis
**Valuation Date:** 04/24/2026
**Draft Version:** v0.1
**Prepared by:** AI Analyst (TeamAnalyst)
**Submitted to:** [Reviewing Actuary Name]
**Draft Date:** 04/24/2026

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
Demonstration of chain-ladder reserving analysis workflow on Workers Compensation data. This analysis applies both rules-based and open-ended AI selection frameworks to develop actuarial loss development factor and tail factor selections, culminating in ultimate loss estimates by accident year.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers Compensation |
| Accident / Underwriting years | 2001–2024 |
| Coverages | Loss (Paid, Incurred); Closed Claim Count |
| Basis | Gross |
| Currency | USD |
| Geography | Not specified (Commercial account, clerical/low hazard) |
| Exposure Base | Payroll ($100M–$500M range) |

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
| Paid loss triangles | input_data.xlsx (Sheet: Paid 1) | 04/24/2026 | 24 AYs (2001–2024), 24 evaluation ages (11–287 months); staircase pattern |
| Incurred loss triangles | input_data.xlsx (Sheet: Inc 1) | 04/24/2026 | 24 AYs (2001–2024), 24 evaluation ages (11–287 months); same structure as paid |
| Closed claim counts | input_data.xlsx (Sheet: Ct 1) | 04/24/2026 | 24 AYs (2001–2024), 24 evaluation ages; count-based development |
| Payroll (exposure) | input_data.xlsx (Sheet: Exposure) | 04/24/2026 | 24 AYs (2001–2024); base $316.4M with ~2% annual growth; used for BF fallback ELR |
| Metadata | input_data.xlsx (Sheet: Tri 1) | 04/24/2026 | Workers Comp, low-hazard/clerical, payroll $100M–$500M range |
| Expected Loss Rates | N/A | N/A | No ELR file provided. BF method will use fallback: diagonal paid loss per dollar of payroll, smoothed with 3-yr rolling average. Initial Expected method skipped. |

### 3.2 Data Reconciliation
- Data source is a standalone triangle file; no external reconciliation performed.
- Reconciliation note: Incurred and Paid are aligned in structure (same AYs and ages); recommended to verify totals match GL if available.

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- **Development pattern:** All triangles show normal development to mature values; no unusual negative or zero development observed.
- **Alignment:** Paid and Incurred generally show expected P/I ratios for WC (paid typically 60–70% of incurred, matching portfolio risk profile).
- **Maturity:** Data is fully developed through 287+ months (23+ years); tail factors will be applied as appropriate.
- **No data adjustments required** at this stage; data appears clean and usable as-is.

### 3.4 Data Limitations
- **No ELR file provided:** Initial Expected (IE) method was skipped. Bornhuetter-Ferguson (BF) will use the fallback approximation: for each accident year, diagonal paid loss per dollar of payroll exposure, smoothed with a 3-year rolling average and rounded to 3 decimals.
- **No prior selections:** No LDF or tail factor selections from a prior analysis were available for comparison. All selections are new.
- **Closed count vs. reported count:** The count triangle reflects closed claims (not reported/open). Development patterns differ from reported count — interpretation of count-based diagnostics should account for this.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid LDF | [ ] | |
| Reported LDF | [ ] | |
| Paid B-F | [ ] | |
| Reported B-F | [ ] | |
| Expected Loss Ratio | [ ] | |
| Frequency-Severity | [ ] | |
| [Other] | | |

### 4.2 Method Weighting / Selection Logic
[Describe how methods were weighted by maturity, and any segment-specific logic. Call out where judgment was applied vs. formulaic selection.]

### 4.3 LAE Treatment
- **DCC / ALAE:** [Analyzed with loss / separately / ratio method]
- **A&O / ULAE:** [Paid-to-paid ratio / other]

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** [e.g., volume-weighted 5-year average with outlier adjustment]
- **Tail:** [Source — curve fit, industry benchmark, judgment]

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
| v0.1 | 04/24/2026 | AI Analyst (TeamAnalyst) | Initial draft — project setup complete |
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