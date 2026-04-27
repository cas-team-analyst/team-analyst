---
name: peer-review
description: Peer review of completed reserve analysis. Use after reserving-analysis workflow finishes. Do NOT use during initial analysis (separate skill exists).
---

# Actuarial Peer Review

## Quick Reference

**What this does:** Reviews completed reserve analysis - workbook, tech review, REPORT.md, and REPLICATE.md - and produces advisory findings in `PEER_REVIEW.md`.

**When to use:** After technical review passes and all selections are finalized. Do NOT use during initial analysis workflow (separate skill exists).

**Key principles:**
- **Advisory only** - propose alternatives, never override analyst selections
- **Materiality-first** - focus on largest reserves and widest method spreads
- **ASOP-grounded** - check against ASOP 23, 25, 36, 41, 43 standards
- **Clear feedback** - findings actionable by both AI and human users

**Navigation:**
- [Initial Setup](#initial-setup)
- [Workflow](#workflow)
- [Checks to Perform](#checks-to-perform)
- [Output Format](#output-format)
- [Key Principles](#key-principles)
- [ASOP Reference Standards](#asop-reference-standards)

---

## Initial Setup

Focus first exclusively on **orienting to the OS environment**.

1. **Identify and mount the plugin skill folder** (if applicable, NOT the anthropic-skills folder)
2. **Identify the analysis folder** - where the completed analysis lives (project root folder)
3. **Verify required files exist in the analysis folder:**
   - `Analysis - Values Only.xlsx` - the values-only workbook to review (formulas pre-evaluated)
   - `Tech Review.xlsx` - the technical review diagnostics to review
   - `REPORT.md` - the actuarial report to review
   - `REPLICATE.md` - the reproducibility log to review
   - `PROGRESS.md` - to confirm analysis state
4. **Confirm project is ready for review:**
   - Technical review must be complete (Step 7 in PROGRESS.md)
   - All selections finalized
   - If analysis is incomplete, stop and advise user to finish reserving-analysis first

**CoWork Agent Guidelines:**

**File operations:** Use `cp` for file operations. Convert Windows paths to Unix: `C:\Users\...` → `/mnt/c/Users/...`. Mount skill folder first if accessing templates.

**Output:** Write findings to `PEER_REVIEW.md` in the analysis folder root (alongside REPORT.md, REPLICATE.md, PROGRESS.md).

**Other:** Cache out of date? Suggest close/reopen CoWork. Never use unicode symbols in commands.

---

## Workflow

1. **Read the analysis folder files:**
   - `Analysis - Values Only.xlsx` - selections and projections (values only, formulas pre-evaluated)
   - `Tech Review.xlsx` - technical review diagnostics and checks
   - `REPORT.md` - actuarial report documentation
   - `REPLICATE.md` - reproducibility log
2. **Prioritize high-materiality segments** - largest reserves, widest uncertainty
3. **Run checks** listed in [Checks to Perform](#checks-to-perform)
4. **Document findings** in `PEER_REVIEW.md` using [Output Format](#output-format)
5. **Frame all feedback as advisory** - "you may want to consider..." not "you must change..."

---

## Checks to Perform

### 1. Cross-Method Consistency

- **Paid vs Incurred development**: Paid development factors should generally exceed incurred. Flag if violated consistently across accident periods.
- **Method bias detection**: If one method is consistently higher or lower than another across all periods, the tail or selections may need adjustment. If methods alternate (paid higher one year, incurred the next), no systematic bias exists.
- **BF vs development methods**: If BF is consistently higher/lower than development methods, the expected loss ratio seed may be mis-calibrated.

### 2. Paid vs Incurred Ultimate Reasonability

- If paid ultimate < incurred losses, the paid method likely shouldn't be averaged in—unless the incurred triangle shows significant negative development, in which case a lower paid ultimate may be appropriate.
- Flag these situations and note the incurred development pattern.

### 3. Recent Year Loss Ratio / Loss Rate Stability

- Compare the implied loss ratio (or loss rate) from the most recent 2 accident years against more mature years.
- If recent years produce ratios materially higher or lower, flag it. This often indicates LDFs are too highly leveraged and BF methods should be preferred for those years.

### 4. Selection Quality per ASOPs

- Are data sources and adjustments documented? (ASOP 23, 41)
- Are trending procedures appropriate? (ASOP 13)
- Is credibility weighting applied where warranted? (ASOP 25)
- Are selections consistent with the diagnostics shown? (ASOP 43)
- Would selections support an actuarial opinion? (ASOP 36)

### 5. Diagnostic Consistency

- Do selected factors align with the diagnostic exhibits (e.g., residual plots, weighted averages, volume-weighted averages)?
- Are outlier exclusions documented and justified?

### 6. Documentation Quality

- **REPORT.md completeness**: Are all sections filled in (not just boilerplate)? Are assumptions, methods, and rationale documented?
- **REPLICATE.md reproducibility**: Can another actuary reproduce the analysis from the log? Are scripts, manual edits, and data sources listed?
- **ASOP 41 alignment**: Does documentation meet actuarial communication standards?

### 7. Technical Review Diagnostics

- **Review Tech Review.xlsx**: Check all automated diagnostic tests passed or were appropriately addressed
- **Cross-check flags**: Are any issues flagged in Tech Review.xlsx properly documented in REPORT.md Section 7?
- **Reasonableness checks**: Loss ratio progression, frequency/severity trends, actual vs expected emergence

---

## Output Format

Write `PEER_REVIEW.md` in the analysis folder root, structured as:

```markdown
# Peer Review — [Line of Business / Segment]

**Analysis folder:** [path]
**Review date:** [date]
**Status:** Advisory — no selections were modified

**Files reviewed:**
- Analysis - Values Only.xlsx
- Tech Review.xlsx
- REPORT.md
- REPLICATE.md

## Summary
[2-3 sentence overall assessment]

## High-Priority Findings
[Material issues requiring analyst attention, each with section reference]

## Detailed Findings

### Cross-Method Consistency
[Findings and advisory suggestions]

### Paid vs Incurred Reasonability
[Findings]

### Recent Year Stability
[Findings]

### ASOP Compliance
[Findings by standard]

### Diagnostic Consistency
[Findings]

### Documentation Quality
[Findings on REPORT.md and REPLICATE.md completeness and ASOP 41 compliance]

### Technical Review Diagnostics
[Findings from Tech Review.xlsx - any failed checks, flags requiring attention, or issues with automated diagnostics]

## Proposed Alternatives
[Where the reviewer would select differently, show both the analyst's selection and the proposed alternative with rationale. Do NOT apply changes.]
```

---

## Key Principles

- **Advisory only**: Propose, never override. Use language like "consider whether…" and "this may warrant…"
- **Materiality-first**: Spend most effort on segments with largest reserves or widest method spreads.
- **Show your work**: When proposing alternatives, include the numeric comparison.
- **Tight feedback loop**: Write findings clearly enough that both the analyst agent and human user can act on them immediately.

---

## ASOP Reference Standards

### ASOP No. 13 — Trending Procedures in Property/Casualty Insurance

**Scope (one line):** governs selection and use of trending procedures (frequency, severity, pure premium, loss ratio, exposure, premium) in P/C ratemaking and related estimates, including reserve analyses that rely on trend.

**Key Requirements for Peer Review:**
- **Separate experience vs. exposure trends** where the data and methods permit — combining them into a single trend factor is acceptable only if cross-effects are understood and disclosed.
- **Use data appropriate to the subject business** — industry/external indices may supplement but must be tested against own data where credibility allows.
- **Trend period** (from midpoint of experience to midpoint of forecast/estimate period) must be computed correctly; watch for off-by-half-period errors.
- **Evaluate the historical trend** (fit, length of series, outliers, structural breaks) before selecting a prospective trend.
- **Consider known or anticipated changes** (law changes, inflation regime shifts, mix shifts, coverage changes) and adjust the historical trend or select a different prospective trend when warranted.
- **Model/method selection** (exponential, linear, multiplicative, additive, generalized linear) should match the data pattern — justify the choice.

**Red Flags to Look For:**
- Flat trend selected across recent years that clearly show a regime change (e.g., social inflation, medical CPI spike).
- A single blended trend used where frequency and severity move in opposite directions.
- Trend fit window that cherry-picks endpoints (starts at a trough, ends at a peak, or vice versa).
- External index relied on with no back-test against the subject book.
- Trend period miscomputed (wrong midpoints, rate change dates ignored).
- No consideration of whether the trend should be the same prospectively as retrospectively.

**Disclosure / Documentation Checks:**
- Data source and period of the experience used for trend.
- The specific trend model/form and parameter(s) selected.
- Rationale for selected trend where it differs from the fitted trend.
- Any reliance on external data and the reasonableness check performed.
- Known or anticipated changes that influenced the selection.

**Common Misapplications:**
- Treating "trend" as a single number without distinguishing frequency and severity.
- Applying a pure-premium trend and a separate loss-ratio trend without reconciling the implicit exposure trend.
- Extrapolating a short-term trend as if it were a long-run rate.
- Ignoring the effect of large loss capping / development on observed severity trends.

---

### ASOP No. 23 — Data Quality

**Scope (one line):** governs the actuary's selection of data, review of data for reasonableness, use of imperfect data, and disclosure of data limitations in any actuarial work product.

**Key Requirements for Peer Review:**
- **Data selection:** data used must be appropriate for the purpose of the analysis — relevance, level of detail, time period, and segmentation all matter.
- **Review for reasonableness and consistency:** the actuary must perform a data review unless such review is not practicable given scope/resources — but even then the lack of review must be disclosed.
- **Use of imperfect data:** if data have known material defects, the actuary must judge whether they can still support the estimate, and may need to adjust, supplement, or decline the assignment.
- **Reliance on data supplied by others:** the actuary may rely on data supplied by others but remains responsible for disclosing the reliance and the limits of the review performed.
- **Sufficiency:** data should be sufficient in volume and time span to support the methods used; where not sufficient, use methods that accommodate the limitation (e.g., credibility weighting, BF with external prior).

**Red Flags to Look For:**
- No documented data reasonableness check (no reconciliation to accounting, no record counts, no min/max/negative scan).
- Triangles that don't tie to financial reports and the tie-out isn't shown.
- Unexplained large movements diagonal-to-diagonal (large-loss emergence, coding change, system migration) treated as normal development.
- Gaps (missing periods, missing segments) with no explanation.
- Claim count or exposure definitions shift over time and the analyst doesn't discuss it.
- Data "received as-is from the client" with no reliance disclosure.

**Disclosure / Documentation Checks:**
- Source and as-of date of every data element.
- Reconciliations performed (and results).
- Known defects, errors, or limitations found during review.
- What the actuary did (or didn't do) to review data supplied by others.
- Impact of any data limitations on the estimate (qualitative or quantitative).

**Common Misapplications:**
- Treating "data passed a reconciliation" as equivalent to "data is fit for purpose."
- Skipping the reasonableness review because the data came from a trusted system.
- Using imperfect data without disclosing the imperfection because an adjustment was made.
- Excluding outliers without documenting the rule and the impact.

---

### ASOP No. 25 — Credibility Procedures

**Scope (one line):** governs the selection, application, and blending of a credibility procedure whenever the actuary blends subject experience with related experience (a "complement of credibility") to produce an estimate.

**Key Requirements for Peer Review:**
- **Purpose fit:** the credibility procedure must be appropriate for the intended use — procedures that are fine for ratemaking may be inadequate for reserving and vice versa.
- **Subject experience:** should be reviewed for homogeneity, volume, and whether it reflects the risk characteristics being estimated.
- **Complement of credibility:** must be related to (share risk characteristics with) the subject experience. Common complements — industry, prior-period own experience, external benchmarks, BF a priori — must be chosen with stated rationale.
- **Credibility assignment:** whether classical (limited fluctuation), Bühlmann/Bühlmann-Straub, Bayesian, or judgmental, the method and its key parameters should be documented. Judgmental credibility is allowed but must be justified.
- **Consistency over time:** a sudden change in credibility method or weight from prior analyses should be explained.

**Red Flags to Look For:**
- BF method used with an expected loss ratio "selected" with no stated source (no pricing indication, no prior study, no benchmark).
- Credibility weights pulled from thin air ("60% paid / 40% incurred") with no link to volume, age, or stability.
- Complement that is not actually related to the subject (e.g., using countrywide severity as a complement for a narrow state-specific segment with different coverage triggers).
- Full credibility given to recent years that clearly lack volume.
- No credibility adjustment where the analysis selects a method (like paid development) that is obviously unstable at the age in question.

**Disclosure / Documentation Checks:**
- The credibility procedure used (classical, Bayesian, Bühlmann, judgmental).
- Key parameters (full-credibility standard, EPV/VHM, prior mean and variance, or the basis for judgmental weights).
- The source of the complement of credibility.
- Rationale for the homogeneity of the subject experience as grouped.
- Any material change in the procedure from prior analyses.

**Common Misapplications:**
- Using "BF" as a black box where the a priori loss ratio is set equal to the latest paid estimate, defeating the purpose of the complement.
- Selecting weights based on which method gives the answer the user wants.
- Applying a single credibility standard across segments with very different volume profiles.
- Ignoring the age dimension — credibility of a development-based ultimate at 12 months is not the same as at 60 months.

---

### ASOP No. 36 — Statements of Actuarial Opinion Regarding P/C Loss and Loss Adjustment Expense Reserves

**Scope (one line):** governs the issuance of written Statements of Actuarial Opinion (SAOs) on P/C loss and LAE reserves, including opinions filed with regulators.

**Key Requirements for Peer Review:**
- **Scope of opinion:** the SAO must clearly describe what reserves are covered (net vs. gross, lines included, discounting, loss vs. LAE, ceded vs. assumed, etc.) and any items carved out.
- **Opinion type — must be one of:**
  - **Reasonable** — the booked reserves make a reasonable provision.
  - **Redundant / Excessive** — booked reserves are greater than a reasonable provision.
  - **Deficient / Inadequate** — booked reserves are less than a reasonable provision.
  - **Qualified** — reasonable for all items except specifically identified items.
  - **No Opinion** — unable to form an opinion, with stated reason.
- **Range vs. point estimate:** the actuary may support the opinion with a point estimate, a range of reasonable estimates, or both. A range must actually reflect reasonable estimates, not just sensitivity bounds.
- **Risk of Material Adverse Deviation (RMAD):** the actuary must state whether significant risk of material adverse deviation exists, disclose the materiality standard used, and identify the major risk factors.
- **Reliance:** any reliance on others for data, underlying analyses, or segments must be disclosed with the name/role of the person relied upon.
- **Consistency with the supporting work product:** the selections, methods, and estimates in the underlying analysis must actually support the opinion issued.

**Red Flags to Look For:**
- Booked reserves very close to (or outside) the high end of the actuary's reasonable range, with a "reasonable" opinion and no RMAD.
- Materiality standard for RMAD not disclosed, or disclosed but untethered from surplus/capital.
- Range of reasonable estimates set mechanically (e.g., ±10%) rather than derived from method/assumption variation.
- Segments carved out of the opinion without explanation.
- Reliance statements listing "management" generically rather than specific individuals and specific items.
- Selected point estimate not reproducible from the supporting analysis workbook.

**Disclosure / Documentation Checks:**
- Opinion type and the reserve amounts covered.
- Materiality standard and whether RMAD exists.
- Specific risk factors contributing to RMAD (mass torts, reinsurance disputes, reserving changes, etc.).
- Reliance on others and scope of that reliance.
- Whether the opinion relates to net, gross, or both.
- Discounting treatment.

**Common Misapplications:**
- Treating the opinion as a compliance formality; issuing "reasonable" without genuinely testing whether the booked amount falls within the range.
- Using a range so wide that almost any booked number would fall inside it.
- Failing to update the materiality standard when capital/surplus changes materially.
- Opining on a segment where underlying data quality is so poor that "no opinion" would be the honest answer.

---

### ASOP No. 41 — Actuarial Communications

**Scope (one line):** governs every actuarial communication (written, electronic, or oral) that conveys actuarial findings — covers what must be disclosed and how the work must be documented so another actuary could understand and evaluate it.

**Key Requirements for Peer Review:**
- **Identify the actuary:** name of the actuary and the principal, and the intended users of the communication.
- **Intended purpose and users:** state what the communication is for and who may rely on it. Caveat against use by unintended users when appropriate.
- **Actuarial findings must be clear:** methods, assumptions, data, and limitations all disclosed at a level that lets another qualified actuary evaluate the work.
- **Actuarial Report (the supporting document) must include:**
  - the scope and intended use;
  - the data relied on and reliance disclosures;
  - the methods and assumptions with rationale;
  - any material changes in methods or assumptions from prior;
  - uncertainty, risk, and limitations;
  - a statement of conflicts of interest if any.
- **Deviation from standards:** if the actuary deviates from ASOP guidance, the deviation and the reason must be disclosed.
- **Qualifications:** the actuary must comply with applicable qualification standards and may be required to disclose compliance.
- **Dating:** the communication must identify the information date and the date of issuance; note any subsequent events considered.

**Red Flags to Look For:**
- Communication that states a point estimate with no range, no method description, and no data disclosure.
- "Intended user" section missing, leaving unclear who may rely on the work.
- Material assumption (e.g., selected tail factor, a priori loss ratio) stated without rationale.
- Reliance on another party's data or analysis without naming the party or describing the scope of reliance.
- Language that overstates precision ("the estimate is") where the underlying analysis has wide variation.
- Prior-year comparison that omits why methods or assumptions changed.

**Disclosure / Documentation Checks:**
- Name of actuary and principal.
- Intended users, intended purpose, and any use restrictions.
- Information date and date of communication.
- Scope of the analysis (what's in, what's out).
- Data sources and reliances.
- Methods, assumptions, and rationales.
- Risks, limitations, and uncertainty.
- Changes from prior work and reasons.
- Any deviation from ASOPs and reason.

**Common Misapplications:**
- Issuing a short "letter" opinion without a supporting actuarial report that meets ASOP 41 content requirements.
- Treating the report as the deliverable to the client rather than as documentation an independent actuary could use to reproduce and evaluate the work.
- Boilerplate caveats that don't actually describe the risks of this specific analysis.
- Missing subsequent-events discussion when there's a meaningful gap between information date and issuance date.

---

### ASOP No. 43 — Property/Casualty Unpaid Claim Estimates

**Scope (one line):** governs the estimation of P/C unpaid claims — claim liabilities, ultimate losses, IBNR, LAE — for any purpose (reserving, pricing support, M&A, litigation, regulatory).

**Key Requirements for Peer Review:**
- **Define the measurement:** the estimate must be clearly scoped — what is included (indemnity, ALAE, ULAE, salvage/subrogation), definition of claim, loss date basis (AY/RY/PY), gross vs. ceded vs. net, discounting, risk margins, currency.
- **Intended measure:** identify what the estimate represents — e.g., the mean of the distribution, the median, a high estimate, an actuarial central estimate — and communicate it.
- **Methods and models:** select multiple methods where appropriate; each method's use must be justified given data, environment, and age. Consider paid and incurred development, BF, Cape Cod, frequency-severity, exposure-based, and credibility-weighted combinations as relevant.
- **Assumptions:** tail, trend, a priori loss ratios, credibility weights, and any other material assumption must be explicitly identified, reasonable in the aggregate, and internally consistent.
- **Changes from prior:** material changes in methods, assumptions, or data must be identified and their effect on the estimate discussed.
- **Uncertainty:** the estimate should reflect consideration of the uncertainty in the outcome — not necessarily a full distribution, but a reasoned discussion of process, parameter, model, and systemic risk.
- **Reasonableness review:** the final estimate must be reviewed in aggregate for reasonableness — not just method-by-method.
- **Documentation:** sufficient to allow another qualified actuary to understand the methods, data, and rationale (ties to ASOP 41).

**Red Flags to Look For:**
- A single method selected for every segment regardless of age, volume, or stability.
- Weighted average of methods where the weights are the same across all accident years (ignoring that recent years usually warrant BF over development).
- Paid ultimate below incurred losses with no commentary.
- Tail factor selected by analogy to "what we used last year" with no re-test.
- Assumptions internally inconsistent (e.g., loss ratio trend in pricing disagrees with a priori loss ratio used in BF).
- No aggregate reasonableness check — just the sum of segment selections.
- Subsequent events (large claim, law change) ignored between data date and estimate date.
- Gross/ceded/net treatment unclear or inconsistent across segments.

**Disclosure / Documentation Checks:**
- Intended measure (mean, central, high, etc.) and definition of the liability.
- Scope: loss dates, coverage triggers, ALAE/ULAE inclusion, gross vs. net, discount.
- Methods used and why.
- Key assumptions and rationale.
- Data used and any reliance (ties to ASOP 23).
- Changes from prior estimate.
- Uncertainty discussion (process, parameter, model, systemic).
- Subsequent events considered.

**Common Misapplications:**
- Averaging methods mechanically (e.g., 50/50 paid and incurred CL) when diagnostics favor one strongly over the other.
- Selecting the latest-year ultimate from a development method that is clearly over-leveraged at the current age.
- Treating "IBNR" as a plug (booked minus case) rather than as the output of a coherent estimate of ultimate losses.
- Failing to reconcile segment-level estimates to an aggregate view.
- No uncertainty discussion because a range wasn't asked for.

---

## Checks to Perform

### 1. Cross-Method Consistency

- **Paid vs Incurred development**: Paid development factors should generally exceed incurred. Flag if violated consistently across accident periods.
- **Method bias detection**: If one method is consistently higher or lower than another across all periods, the tail or selections may need adjustment. If methods alternate (paid higher one year, incurred the next), no systematic bias exists.
- **BF vs development methods**: If BF is consistently higher/lower than development methods, the expected loss ratio seed may be mis-calibrated.

### 2. Paid vs Incurred Ultimate Reasonability

- If paid ultimate < incurred losses, the paid method likely shouldn't be averaged in—unless the incurred triangle shows significant negative development, in which case a lower paid ultimate may be appropriate.
- Flag these situations and note the incurred development pattern.

### 3. Recent Year Loss Ratio / Loss Rate Stability

- Compare the implied loss ratio (or loss rate) from the most recent 2 accident years against more mature years.
- If recent years produce ratios materially higher or lower, flag it. This often indicates LDFs are too highly leveraged and BF methods should be preferred for those years.

### 4. Selection Quality per ASOPs

- Are data sources and adjustments documented? (ASOP 23, 41)
- Are trending procedures appropriate? (ASOP 13)
- Is credibility weighting applied where warranted? (ASOP 25)
- Are selections consistent with the diagnostics shown? (ASOP 43)
- Would selections support an actuarial opinion? (ASOP 36)

### 5. Diagnostic Consistency

- Do selected factors align with the diagnostic exhibits (e.g., residual plots, weighted averages, volume-weighted averages)?
- Are outlier exclusions documented and justified?

---

## Output Format

Write `PEER_REVIEW.md` structured as:

```markdown
# Peer Review — [Line of Business / Segment]

**Analysis file:** Analysis - Values Only.xlsx
**Review date:** [date]
**Status:** Advisory — no selections were modified

## Summary
[2-3 sentence overall assessment]

## High-Priority Findings
[Material issues requiring analyst attention, each with section reference]

## Detailed Findings

### Cross-Method Consistency
[Findings and advisory suggestions]

### Paid vs Incurred Reasonability
[Findings]

### Recent Year Stability
[Findings]

### ASOP Compliance
[Findings by standard]

### Diagnostic Consistency
[Findings]

## Proposed Alternatives
[Where the reviewer would select differently, show both the analyst's selection and the proposed alternative with rationale. Do NOT apply changes.]
```

## Key Principles

- **Advisory only**: Propose, never override. Use language like "consider whether…" and "this may warrant…"
- **Materiality-first**: Spend most effort on segments with largest reserves or widest method spreads.
- **Show your work**: When proposing alternatives, include the numeric comparison.
- **Tight feedback loop**: Write findings clearly enough that both the analyst agent and human user can act on them immediately.