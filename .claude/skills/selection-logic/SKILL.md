---
name: selection-logic
description: View the base actuarial LDF selection logic used for chain-ladder selections. Use when an actuary wants to review or understand the selection framework, criteria, and diagnostic rules.
---

# Selection Logic

## Getting Started

When a user invokes this skill, always begin by presenting the following introduction:

---

**Selection Logic — TeamAnalyst Plugin**

This is the selection-logic skill from the TeamAnalyst plugin package. It allows you to view the selection logic used for chain-ladder LDF selections. This logic is applied during the core reserving-analysis workflow when making actuarial selections.

Your selection logic defines the criteria, thresholds, and decision hierarchy that guide how Loss Development Factors are chosen from triangle data.

---

Then use the AskUserQuestion tool with exactly these two options and no others:

1. **View selection criteria** — See the 14 selection criteria and decision hierarchy
2. **View diagnostic rules** — See the 10 diagnostic adjustment rules

## A. View Selection Criteria

Read `skills/reserving-methods/assets/chain-ladder/SELECTION-LOGIC-REFERENCE.md`. If the file cannot be found, tell the user plainly: "The base selection logic file could not be found at the expected path." and stop.

First, present the **Decision Hierarchy** (priority order in which criteria are applied):

| Priority | Criterion | Description |
|---|---|---|
| 1 | Convergence Override | If all averages agree within +/-2%, select the midpoint — overrides all other criteria |
| 2 | Diagnostic-confirmed Trend | Trend supported by diagnostics takes priority over the prior |
| 3 | Bayesian Anchoring | Absent convergence or confirmed trends, anchor to prior selection |
| 4 | Asymmetric Conservatism | Move faster toward higher LDFs, slower toward lower ones |
| 5 | Sparse Data Caution | Dampens all movements when data is thin |
| 6 | Latest-Point Outlier | Pre-filter applied before averaging or trending |

Then present the **14 Selection Criteria** in this summary table:

| # | Criterion | Key Thresholds | When It Applies |
|---|---|---|---|
| 1 | Outlier Handling | CV <= 0.10: standard; 0.10-0.20: exclude 1 high/low; >0.20: exclude 2 or flag | Always — first pass on raw LDFs |
| 2 | Recency Preference | Default 5-yr vol-weighted; 3-yr if diverge >3%; 7-yr if <50 claims/AY | Always — determines averaging window |
| 3 | Asymmetric Conservatism | Upward >3%: move 60-80%; Downward 3-10%: move 30-50% | When selection moves from prior |
| 4 | Bayesian Anchoring | Within +/-2%: hold prior; 2-5%: partial move; >5%: need 2+ confirmations | When prior selections exist |
| 5 | Latest-Point Outlier | Deviation >1.5 sigma or >15% from 5-yr average | Latest diagonal looks anomalous |
| 6 | Trending | 3+ consecutive LDFs same direction or slope p<0.10 | Systematic pattern in recent data |
| 7 | Sparse Data | <50 claims/AY; <$1M incurred; <5 LDFs in column | Thin or immature data |
| 8 | Convergence Override | All averages within +/-2% and midpoint >3% from prior | Averages agree strongly |
| 9 | Maturity-Dependent | Early: conservatism; Mid: trending; Late: sparse data/tails | Always — modifies other criteria by age |
| 10 | Paid vs. Incurred Consistency | >5% divergence triggers investigation | Both paid and incurred triangles available |
| 11 | Negative/Sub-1.000 Development | Paid: never <1.000; Incurred late: 0.995 minimum | LDFs near or below 1.000 |
| 12 | Large Loss Handling | Removal changes LDF >5%: use ex-large + separate load | Large loss distorts column |
| 13 | Calendar Year Effects | Diagonal LDFs high/low across 3+ columns simultaneously | Reserve study or inflation event |
| 14 | Tail Factor | Required if last LDF >1.005 incurred or >1.010 paid | Late maturities with remaining development |

After presenting the tables, offer: "Would you like me to explain any specific criterion in detail?"

If the user asks about a specific criterion, read the full details for that section from the reference file and present them.

Once the user is done exploring, tell them: "When you're ready to see this logic in action on your data, you can use `/reserving-analysis` to start a reserving analysis."

## B. View Diagnostic Rules

Read `skills/reserving-methods/assets/chain-ladder/SELECTION-LOGIC-REFERENCE.md`. If the file cannot be found, tell the user plainly: "The base selection logic file could not be found at the expected path." and stop.

Explain that diagnostics are applied **after** setting the baseline LDF from the core selection criteria. The sequence is: set baseline, screen diagnostics, cross-check, adjust, then reasonability test (>10% method divergence = re-examine).

Present the **10 Diagnostic Adjustment Rules** in this table:

| Diagnostic | No-Action Zone | Trigger & Action |
|---|---|---|
| Reported Counts | +/-10% | >+10%: use 3-yr LDFs if new business. >-10%: widen window. >+/-25%: potential AY outlier |
| Incurred Severity | <+2% p.a. trend | +2-5%: increase LDFs 1-2% at early maturities. >+5%: weight 3-yr heavily |
| Paid Severity | Within 5-yr corridor | >10% above: increase paid LDFs. >10% below: increase later-maturity LDFs |
| Paid-to-Incurred | +/-5pp of benchmark | >5pp below + slow closure: increase later LDFs. >5pp above: lower later incurred LDFs |
| Open Counts | +/-10% | >10% high: upper-range LDFs, add 0.005-0.015 to tail. >25%: investigate structural break |
| Avg Case Reserve | <+/-5% | +5-15%: dampen incurred, weight paid. >+15%: rely on paid only. -5-15%: incurred artificially low |
| Claim Closure Rate | +/-3pp | >3pp slow: increase LDFs (~0.5-1.5% per 5pp). >3pp fast: lower later LDFs |
| Incr Incurred Severity | +/-10% | >+10% + paid up: real, select high end. >+10% + paid flat: reserving, dampen |
| Incr Paid Severity | +/-10% | >+10%: increase paid LDF unless one-time large loss. 3+ diagonal trend: re-anchor |
| Incr Closure Rate | +/-2pp | >2pp fast: lower LDF slightly. >2pp slow: increase LDF + next 1-2 columns |

After presenting the table, offer: "Would you like me to explain any specific diagnostic rule in detail?"

If the user asks about a specific diagnostic, read the full details from the reference file and present them.

Once the user is done exploring, tell them: "When you're ready to see this logic in action on your data, you can use `/reserving-analysis` to start a reserving analysis."

## Guardrails

- This is a **read-only** skill. It does not create, modify, or save any files.
- It reads from one source only: `skills/reserving-methods/assets/chain-ladder/SELECTION-LOGIC-REFERENCE.md`
- Do NOT invent, assume, or present any selection logic that is not in the reference file.
- Do NOT offer to create or modify custom logic files.
- Do NOT suggest other skills, plugin customizers, or workarounds for modifying selection logic.
- If the user asks how to modify, adjust, or customize the selection logic, respond with exactly this: "Selection logic can be modified in Claude Code, where you have write access to the plugin files. See the **Selection Logic Adjustment Guide** in the project repository for step-by-step instructions on how to change criteria, thresholds, diagnostic rules, and the decision hierarchy. These changes cannot be made from within Cowork, as plugin files are read-only here."
