---
name: peer-review
description: Actuarial peer review of reserve analysis. Use when the user asks to peer review, review selections, check reserve work, or validate actuarial analysis. Reads output/complete-analysis.xlsx and produces PEER_REVIEW.md. Should only run after tech review checks have passed and after final methods/diagnostics are complete.
---

# Actuarial Peer Review

Review the reserve analysis at `output/complete-analysis.xlsx`. Produce `output/PEER_REVIEW.md` with findings.

## Quick Reference

1. Read the complete analysis workbook
2. Prioritize high-materiality and low-confidence areas
3. Run checks below → document findings in `output/PEER_REVIEW.md`
4. Frame all feedback as advisory: "you may want to consider…"

Standards to verify against:
- CAS Paper: "Estimating Unpaid Claims Using Basic Techniques" (Friedland et al.)
- ASOP No. 13 — Trending — see `assets/ASOP-13-Trending.md`
- ASOP No. 23 — Data Quality — see `assets/ASOP-23-Data-Quality.md`
- ASOP No. 25 — Credibility — see `assets/ASOP-25-Credibility.md`
- ASOP No. 36 — SAO for P/C Reserves — see `assets/ASOP-36-SAO-PC-Reserves.md`
- ASOP No. 41 — Actuarial Communications — see `assets/ASOP-41-Actuarial-Communications.md`
- ASOP No. 43 — P/C Unpaid Claim Estimates — see `assets/ASOP-43-PC-Unpaid-Claim-Estimates.md`

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

Before answering the bullets below, open the relevant ASOP file in `assets/` and verify against its **Key Requirements** and **Red Flags** sections. Cite the specific requirement in findings, not just the ASOP number.

- Are data sources and adjustments documented? (ASOP 23 — see `assets/ASOP-23-Data-Quality.md`; ASOP 41 — see `assets/ASOP-41-Actuarial-Communications.md`)
- Are trending procedures appropriate? (ASOP 13 — see `assets/ASOP-13-Trending.md`)
- Is credibility weighting applied where warranted? (ASOP 25 — see `assets/ASOP-25-Credibility.md`)
- Are selections consistent with the diagnostics shown? (ASOP 43 — see `assets/ASOP-43-PC-Unpaid-Claim-Estimates.md`)
- Would selections support an actuarial opinion? (ASOP 36 — see `assets/ASOP-36-SAO-PC-Reserves.md`)

### 5. Diagnostic Consistency

- Do selected factors align with the diagnostic exhibits (e.g., residual plots, weighted averages, volume-weighted averages)?
- Are outlier exclusions documented and justified?

---

## Output Format

Write `output/PEER_REVIEW.md` structured as:

```markdown
# Peer Review — [Line of Business / Segment]

**Analysis file:** output/complete-analysis.xlsx
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
[For each ASOP with findings, cite the specific requirement from the corresponding `assets/ASOP-NN-*.md` file, not just the ASOP number. Organize findings by standard.]

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