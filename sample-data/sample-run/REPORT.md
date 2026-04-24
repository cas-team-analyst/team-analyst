# Reserving Analysis — Working Draft

**Analysis:** Sample Reserving Analysis — Test Data
**Valuation Date:** 01/01/2026
**Draft Version:** v0.1 — Working Draft
**Prepared by:** Bryce
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

- **What this analysis covers:** Full chain-ladder reserving analysis for a WC (clerical) book using 24 accident years (2001–2024) of paid loss, incurred loss, reported count, and payroll exposure triangles. This is sample output using test data to demonstrate the TeamAnalyst workflow.
- **What changed since last review:** First valuation — no prior to compare against.
- **Where I want the most scrutiny:** (1) Paid and Incurred tail factors — two AI selectors diverged materially; rules-based tails are conservative. (2) Incurred Loss ultimates — the IE fallback ELR produces negative IBNR for 9 accident years; those selections revert to Chain Ladder IE which may be unreliable. (3) AYs 2007 and 2015 show unusually high paid loss relative to adjacent years — worth investigating.
- **Open questions for reviewer:** See Section 11

---

## 1. Purpose and Scope

### 1.1 Purpose of the Analysis
This analysis is being performed to create sample output using test triangle data, demonstrating the full TeamAnalyst reserving workflow including Chain Ladder LDF selections, tail factor selections, and ultimate loss estimates.

### 1.2 Scope
| Item | Detail |
|---|---|
| Segment(s) / LOB | Workers' Compensation (WC) — clerical, low hazard |
| Accident / Underwriting years | 2001–2024 (24 years) |
| Coverages | Loss only (no DCC/ALAE split in source data) |
| Basis | Direct (gross) |
| Currency | USD |
| Geography | Not specified in source data |

### 1.3 Intended Internal Users
[e.g., Chief Actuary, Reserving Committee, CFO]. This draft is not intended for external distribution in its current form.

---

## 2. Summary of Indications

*Placeholder numbers — subject to review.*

| Measure | Paid to Date | Incurred to Date | Selected Ultimate | IBNR | % Developed |
|---|---|---|---|---|---|
| Paid Loss | $41,767,854 | — | $48,024,170 | $6,256,316 | 86.9% |
| Incurred Loss | — | $43,616,395 | $46,003,887 | $2,387,492 | 94.8% |
| Reported Count | 9,716 claims | — | 9,748 claims | 32 claims | 99.7% |

*Note: Paid Loss IBNR is BF-weighted blend (CL=$10.0M, BF=$6.2M, IE=$4.2M). Incurred IBNR driven by IE fallback — interpret with caution (see Section 11).*

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
| Paid loss triangles | Triangle Examples 1.xlsx (sheet: Paid 1) | 01/01/2026 | 24 AYs × 24 ages (annual, 11–287 months) |
| Incurred loss triangles | Triangle Examples 1.xlsx (sheet: Inc 1) | 01/01/2026 | Same structure as paid |
| Reported claim counts | Triangle Examples 1.xlsx (sheet: Ct 1) | 01/01/2026 | Same AY/age structure |
| Payroll exposure | Triangle Examples 1.xlsx (sheet: Exposure) | 01/01/2026 | AYs 2001–2024; $316M–$499M range |

**File summary — Triangle Examples 1.xlsx**

- **Line of Business:** Workers' Compensation (WC)
- **Risk type:** Clerical, relatively low hazard (payroll range $100M–$500M)
- **Accident years:** 2001–2024 (24 years)
- **Evaluation ages:** 11, 23, 35, …, 287 months (12-month spacing; 24 development periods)
- **Three triangles:** Paid Loss, Incurred Loss, Reported Count
- **Exposure:** Annual payroll by AY; average ~$401M; growing from $316M (2001) to $499M (2024)
- **Latest diagonal paid total (all AYs):** ~$41.8M

### 3.2 Data Reconciliation
- This analysis uses test/sample data. No reconciliation to a prior valuation or financial system was performed.

### 3.3 Data Quality Observations
*Per ASOP No. 23 — flag anything unusual.*

- Data appears well-structured with no obvious coding gaps or missing rows in the triangle headers.
- Count triangle values appear to be fractional (non-integer) — likely reflecting partial-year or weighted counts; this is consistent with WC ratable payroll-based exposure allocation.
- Older accident years (2001–2006) appear to have reached or be near-ultimate paid development by the latest diagonal.
- Incurred losses for some AYs show downward development in later ages, consistent with case reserve reductions as WC claims close — typical for low-hazard clerical WC.
- No negative paid loss development observed on preliminary review.

### 3.4 Data Limitations
- No initial expected loss rates (ELR) or expected frequency file was provided. Payroll exposure is available, so the fallback ELR approximation (diagonal loss per unit of exposure, 3-year rolling average) can be used for BF/IE — or these methods can be skipped. To be confirmed.
- No prior LDF or tail factor selections were provided; all selections will be made fresh for this analysis.
- No closed count triangle in source data; only reported count is available for count-based development.
- Data validation confirmed by analyst on 04/24/2026.

---

## 4. Methodology

### 4.1 Methods Applied
| Method | Segments Applied | Why Selected |
|---|---|---|
| Paid LDF Chain Ladder | WC All AYs | Primary method; 24 AYs of history, stable paid patterns |
| Incurred LDF Chain Ladder | WC All AYs | Cross-check to paid; useful for early maturities |
| Reported Count Chain Ladder | WC All AYs | Supports frequency/severity diagnostics and count development |
| Bornhuetter-Ferguson (Paid) | WC All AYs | Ran using fallback ELR; provides credibility-weighted blend for immature AYs |
| Initial Expected | WC Paid + Incurred | Ran using fallback ELR approximation (see §5.2); cross-check for immature years |

### 4.2 Method Weighting / Selection Logic
LDF selections were made using a two-track AI process: a rules-based selector applying a 14-criteria decision hierarchy (convergence override, recency preference, Bayesian anchoring, asymmetric conservatism, outlier handling, trending, sparse data, etc.) and an independent open-ended selector applying holistic actuarial judgment. Both sets of selections are visible in the workbook as purple rows.

The **Rules-Based AI Selection** row is the default used in downstream calculations. The **Open-Ended AI Selection** row serves as a cross-check — material divergences between the two are flagged for reviewer attention. Users can override either AI selection row by entering values in the **User Selection** row.

LDF averages considered: volume-weighted and simple averages at all-year, 3-year, 5-year, and 10-year windows, plus exclude-high/low variants. Coefficient of variation and trend slopes were computed as diagnostics.

### 4.3 LAE Treatment
- **DCC / ALAE:** Not applicable — loss data in source file does not distinguish LAE components.
- **A&O / ULAE:** Not applicable — not present in source data.

---


- **A&O / ULAE:** Not applicable — not present in source data.

---

## 5. Key Assumptions

### 5.1 Development Patterns
- **Selection basis:** Volume-weighted averages as default; 5-year window standard; 3-year applied where trend or regime change detected; all-year applied at late maturities (72+ months) where sparse data warrants wider windows. Simple average used as cross-check. Exclude-high/low variants considered where CV > 0.10.
- **LDF intervals:** 23 development intervals per measure (11–23 months through 275–287 months).
- **Tail:** Selected via curve-fitting diagnostics at cutoff age 203 months for losses; 143 months for count. Methods evaluated: Bondy, Modified Bondy, Exponential Decay (quick/product), Double Exponential, McClenahan, Skurnick. Two AI selectors were applied — rules-based and open-ended — with notable divergence on Paid and Incurred (see open questions, Section 11). Rules-based selections used downstream unless overridden.

| Measure | Cutoff Age | Rules-Based Tail | Method | Open-Ended Tail | Method |
|---|---|---|---|---|---|
| Paid Loss | 203 mo | 1.0039 | Bondy | 1.0181 | Exp Dev Product (age 143) |
| Incurred Loss | 203 mo | 1.0000 | McClenahan | 1.0812 | Double Exponential |
| Reported Count | 143 mo | 1.0000 | Bondy | 1.0000 | Bondy |

### 5.2 Expected Loss Ratios (for B-F and ELR methods)
No ELR file was provided. The fallback approximation was applied: for each accident year, diagonal incurred loss was divided by payroll exposure, then smoothed with a 3-year rolling average. This produces a rough ELR that anchors the BF and IE methods without requiring external rate assumptions. Results should be interpreted with caution for immature accident years where the diagonal incurred may be far from ultimate.

| AY | Basis |
|---|---|
| 2001–2024 | Fallback: 3-yr rolling avg of diagonal incurred / payroll exposure |

### 5.3 Trend Assumptions
No explicit trend assumptions applied. Development patterns reflect historical experience embedded in the triangles.

### 5.4 Other Assumptions
- **Case reserve adequacy:** Assumed stable throughout development history. Downward incurred development at late ages for some AYs is consistent with normal WC claim closure patterns rather than a systematic adequacy change.
- **Settlement rate / claim closing patterns:** No adjustment made; count development confirms near-complete reporting by age 143 months.
- **Mix / law / tort environment:** Not adjusted for. This is test data; no external context available.

### 5.5 Assumption Rationale
Material assumptions are based on the observed triangle data and AI selection frameworks. No external benchmarks or industry data were incorporated given the test data context.

---

## 6. Results by Segment

*Detailed exhibits in `output/complete-analysis.xlsx`. See Ultimates.xlsx for per-AY selections with reasoning.*

### 6.1 Paid Loss
- **Selected ultimates:** $48,024,170 total across AYs 2001–2024.
- **Method weighting:** CL-dominant (80–100%) for AYs 2001–2011 (mature, 167–287 months); blended CL/BF (50/50) for AYs 2012–2015; BF-dominant (60–95%) for AYs 2016–2024 (immature, 11–107 months). IE method down-weighted throughout due to fallback ELR instability.
- **Notable judgment calls:** AY 2007 and AY 2015 show unusually high paid loss relative to adjacent years. CL projects large ultimates for AYs 2023–2024 due to thin early-age development data; BF moderates these.

### 6.2 Incurred Loss
- **Selected ultimates:** $46,003,887 total across AYs 2001–2024.
- **Method weighting:** Chain Ladder available only for AY 2001 (fully developed); IE fallback used for all other years. Nine AYs show negative IE IBNR — those selections default to actual incurred or IE per the rules-based framework. See Section 11, item 4.
- **Notable judgment calls:** Incurred is at or near the end of the development table for AYs 2002–2009; selected ultimates effectively equal actual incurred for mature years.

### 6.3 Reported Count
- **Selected ultimates:** 9,748 claims total; IBNR of only 32 claims.
- **Method weighting:** Chain Ladder only. Near-fully developed — count development is complete by age 143 months for most AYs.

---

## 7. Diagnostics and Reasonableness Checks

- [x] **Loss ratios by AY** — Paid loss ratios to payroll exposure range broadly by AY; AY 2007 and 2015 are notably elevated (likely large losses). No systematic upward or downward trend visible across the book.
- [x] **Frequency / severity trends** — Reported count is stable (245–701 per AY), typical for a consistent WC book. Incurred severity at early ages ranges $890–$2,300+ per claim, consistent with low-to-mid hazard WC.
- [x] **Paid-to-incurred ratio** — Paid/incurred starts ~57% at age 11 and rises to ~95%+ by age 107, consistent with normal WC development.
- [ ] **Actual vs. expected emergence** — Not applicable; first valuation.
- [ ] **Comparison to independent benchmark** — No external benchmark provided; not performed.
- [ ] **Hindsight test on prior ultimates** — Not applicable; first valuation.
- [x] **Ratio of IBNR to case reserves** — Paid IBNR of $6.3M against incurred-to-date of $43.6M implies case reserve ~$1.8M; total unpaid reasonable for WC.

**Anomalies flagged:** Tech review structural warnings relate to workbook assembly (triangle sheets not embedded in complete-analysis.xlsx). No numerical FAIL flags. Analytical anomalies: AY 2007 paid ~$4.8M (2× average), AY 2015 paid ~$3.4M at 107 months (elevated); IE negative IBNR for 9 AYs on Incurred.

---

## 8. Sensitivity and Uncertainty

### 8.1 Sensitivity to Key Assumptions
| Assumption | Change | Impact on Total Paid Ultimate |
|---|---|---|
| Paid tail factor | +1.0% (1.004 → 1.014) | +~$480K |
| Paid tail factor | Use open-ended (1.018) | +~$580K |
| BF weight for immature AYs | Shift 10% toward CL | +~$200K |
| IE ELR | Replace fallback with real ELR | Could shift Incurred ±$2–5M |

### 8.2 Sources of Uncertainty
- **Process risk:** Thin data at late development ages. Random fluctuation in claim counts could move tail factors meaningfully.
- **Parameter risk:** Tail factor uncertainty is the largest driver — Paid range spans 1.000–1.329 across methods; selected 1.004 is at the low end. A shift to 1.020 would add ~$0.8M to Paid ultimates.
- **Model risk:** Incurred Loss ultimates rely entirely on the IE fallback ELR for AYs 2002–2024. The fallback is a rough approximation and may not reflect true expected emergence, particularly for unusual AYs (2007, 2015).
- **Systemic risk:** WC is subject to legislative benefit changes, medical inflation, and jurisdictional shifts. No adjustment has been made for post-2024 changes.

---

## 9. Reliance on Others

| Source | Information Relied Upon |
|---|---|
| Triangle Examples 1.xlsx | All triangle data, exposure data — assumed accurate as provided |

---

## 10. Information Date and Subsequent Events

- **Information Date:** 01/01/2026
- **Subsequent events considered:** None known; this is a sample analysis using test data.

---

## 11. Open Questions for Reviewer

1. **Paid Loss tail factor — material divergence between selectors.** Rules-based selected 1.0039 (Bondy, age 203) vs. open-ended 1.0181 (Exp Dev Product, age 143). The exponential decay methods show R² of only 0.23 at age 143. The Skurnick method produced an implausible 1.329 tail. Reviewer should assess whether 1.0039 is sufficient for WC paid losses or whether a modest load (e.g., 1.010–1.020) is warranted given industry benchmarks.

2. **Incurred Loss tail factor — largest divergence.** Rules-based selected 1.0000 (McClenahan) vs. open-ended 1.0812 (Double Exponential, R²=0.884 at age 203). The data shows incurred factors near 1.000 at late ages, but double exponential fit is strong. Reviewer should determine whether the near-zero McClenahan result reflects genuinely closed development or a data artifact.

3. **No ELR/BF method available.** No expected loss rate file was provided. This analysis relies on Chain Ladder ultimates for Paid and IE fallback for Incurred. Reviewer should confirm adequacy of Chain Ladder alone for this book.

4. **Incurred Loss IE method: multiple years show negative IBNR.** IE produces projected ultimates below current incurred for AYs 2005, 2007, 2010, 2011, 2014, 2015, 2018, 2019, and 2023. AYs 2007 and 2015 are most severe (~$1–2M below current diagonal). The fallback ELR is unreliable for Incurred where smoothed loss rate underestimates actual emergence. Reviewer should scrutinize Incurred ultimates for these AYs.

5. **Paid Loss open-ended ultimates incomplete.** The 5b update script noted only 48 open-ended updates across 2 files — Paid Loss open-ended selections may be missing. This is visible in the workbook.

**Items I'm flagging as low-confidence:**
- Paid Loss and Incurred Loss tail factors (see items 1–2 above)
- Incurred Loss ultimates for AYs 2005, 2007, 2010, 2011, 2014, 2015, 2018, 2019, 2023 (item 4 above)

**Items I think should be escalated to [Chief Actuary / Committee]:**
- None identified at this stage

---

## 12. ASOP Self-Check (for reviewer)

| Standard | Addressed In | Notes |
|---|---|---|
| ASOP 23 (Data Quality) | §3 | Test data; no external reconciliation possible |
| ASOP 25 (Credibility) | §4, §5 | Maturity-based method weighting applied |
| ASOP 41 (Communications) | Throughout | Draft — not a final actuarial communication |
| ASOP 43 (Unpaid Claim Estimates) | §4, §5, §8 | IE/BF limited by fallback ELR |
| ASOP 56 (Modeling) | §4 | AI selection framework documented |

---

## 13. Peer Review Log

| Date | Reviewer | Comments | Response |
|---|---|---|---|
| | | | |

---

## 14. Version History

| Version | Date | Author | Summary |
|---|---|---|---|
| v0.1 | 04/24/2026 | Bryce | Initial draft |
| v0.2 | | | |

---

## Appendices (in accompanying workbook)

- **Appendix A:** LDF Selection Workbook — `selections/Chain Ladder Selections - LDFs.xlsx`
- **Appendix B:** Tail Factor Selection Workbook — `selections/Chain Ladder Selections - Tail.xlsx`
- **Appendix C:** Ultimates Workbook — `selections/Ultimates.xlsx`
- **Appendix D:** Complete Analysis — `output/complete-analysis.xlsx`
- **Appendix E:** Tech Review — `output/tech-review.xlsx`
