---
name: selection-logic
description: View the base actuarial LDF selection logic used for chain-ladder selections. Use when an actuary wants to review or understand the selection framework, criteria, and diagnostic rules.
---

# Selection Logic

## Quick Reference

**What this covers:** LDF selection framework (non-tail factors), tail factor selection framework (15-point decision), diagnostic adjustment rules (10 types), AI selector approaches (rules-based vs open-ended)

**Four views available:**
1. LDF selection framework → [Section A](#a-view-ldf-selection-framework)
2. Tail factor selection framework → [Section B](#b-view-tail-factor-selection-framework)  
3. Diagnostic rules → [Section C](#c-view-diagnostic-rules)
4. AI selector approach → [Section D](#d-view-ai-selector-approach)

**Note:** LDF (age-to-age factors) and tail factors are handled separately with distinct frameworks.

---

## Getting Started

When a user invokes this skill, always begin by presenting the following introduction:

---

**Selection Logic — TeamAnalyst Plugin**

This is the selection-logic skill from the TeamAnalyst plugin package. It allows you to view the selection logic used for chain-ladder LDF and tail factor selections. This logic is applied during the core reserving-analysis workflow when making actuarial selections.

Your selection logic defines the criteria, thresholds, and decision hierarchy that guide how Loss Development Factors and tail factors are chosen from triangle data.

**Note:** LDF selections (age-to-age factors for non-tail intervals) and tail factor selections (ultimate development beyond the last observed age) are handled separately with distinct frameworks.

---

Then use the AskUserQuestion tool with exactly these four options and no others:

1. **View LDF selection framework** — See the rule-based LDF selection criteria and decision hierarchy
2. **View tail factor selection framework** — See the 15-point tail factor decision framework
3. **View diagnostic rules** — See the 10 diagnostic adjustment rules (applied to LDF selections)
4. **View AI selector approach** — See how AI selectors differ from rule-based selectors

## A. View LDF Selection Framework

**Authoritative Source:** `.claude/agents/selector-chain-ladder-ldf-ai-rules-based.md`

Read the agent file and present a summary with this structure:

1. **Framework Scope** — what types of selections this applies to (non-tail only)
2. **High-Level Approach** — how many criteria/rules, what decision hierarchy exists
3. **Key Sections** — table of contents showing major sections (e.g., Section 1: Outlier Handling, Section 2: Recency Preference, etc.)
4. **How to Explore** — remind user they can ask for specific sections

Format the summary as plain prose, not bullet lists. Avoid restating specific thresholds, formulas, or numeric criteria.

Once done, remind: "When you're ready to see this logic in action on your data, use `/reserving-analysis` to start a reserving analysis."

## B. View Tail Factor Selection Framework

**Authoritative Source:** `.claude/agents/selector-tail-factor-ai-rules-based.md`

Read the agent file and present a summary with this structure:

1. **Framework Scope** — what types of selections this applies to (tail only, beyond last observed age)
2. **High-Level Approach** — how many decision points, what curve fitting methods are available
3. **Key Sections** — table of contents showing the 15 decision points and major sections
4. **Output Format** — where tail selections appear (`Chain Ladder Selections - Tail.xlsx`)
5. **How to Explore** — remind user they can ask for specific decision points or curve methods

Format the summary as plain prose, not bullet lists. Avoid restating specific diagnostic thresholds, formulas, or numeric criteria.

Once done, remind: "When you're ready to see this logic in action on your data, use `/reserving-analysis` to start a reserving analysis."

## C. View Diagnostic Rules

**Authoritative Source:** `.claude/agents/selector-chain-ladder-ldf-ai-rules-based.md` (Section 10)

Read Section 10 from the agent file and present a summary with this structure:

1. **Diagnostic Scope** — when diagnostics are applied (after baseline LDF, not tail)
2. **Process Flow** — the sequence from baseline through diagnostic adjustment
3. **Available Diagnostics** — list the 10 diagnostic types by name only (e.g., "Reported Counts, Incurred Severity...")
4. **Common Structure** — explain that each diagnostic has no-action zones, triggers, and adjustment magnitudes
5. **How to Explore** — remind user they can ask for specific diagnostic details

Format the summary as plain prose, not bullet lists. Avoid restating specific threshold values or adjustment formulas.

Once done, remind: "When you're ready to see this logic in action on your data, use `/reserving-analysis` to start a reserving analysis."

## D. View AI Selector Approach

**Authoritative Sources:**
- `.claude/agents/selector-chain-ladder-ldf-ai-rules-based.md` (LDF selections, rules-based)
- `.claude/agents/selector-chain-ladder-ldf-ai-open-ended.md` (LDF selections, open-ended)
- `.claude/agents/selector-tail-factor-ai-rules-based.md` (Tail selections, rules-based)
- `.claude/agents/selector-tail-factor-ai-open-ended.md` (Tail selections, open-ended)
- `.claude/agents/selector-ultimates-ai-rules-based.md` (Ultimate selections, rules-based)
- `.claude/agents/selector-ultimates-ai-open-ended.md` (Ultimate selections, open-ended)

Read all AI agent files and present a summary with this structure:

1. **AI vs Rule-Based** — explain the fundamental difference (rules-based vs open-ended judgment)
2. **LDF AI Approaches** — describe both rules-based and open-ended approaches
3. **Tail AI Approaches** — describe both rules-based and open-ended approaches
4. **Ultimate AI Approaches** — describe both rules-based and open-ended approaches
5. **Common Elements** — what all AI agents share (data inputs, JSON output format, opus model for open-ended)
6. **Use Cases** — when to use rules-based vs open-ended selections
7. **Selection Priority** — how Excel selections take precedence over JSON outputs

Format the summary as plain prose, not bullet lists. Quote brief excerpts from the agent prompts to illustrate tone/approach, but don't reproduce them entirely.

Once done, remind: "When you're ready to see both selectors in action on your data, use `/reserving-analysis` to start a reserving analysis."

## Guardrails

- This is a **read-only** skill. It does not create, modify, or save any files.
- It reads from these authoritative sources only:
  - `.claude/agents/selector-chain-ladder-ldf-ai-rules-based.md` (LDF rules-based framework)
  - `.claude/agents/selector-chain-ladder-ldf-ai-open-ended.md` (LDF open-ended AI framework)
  - `.claude/agents/selector-tail-factor-ai-rules-based.md` (Tail rules-based framework)
  - `.claude/agents/selector-tail-factor-ai-open-ended.md` (Tail open-ended AI framework)
  - `.claude/agents/selector-ultimates-ai-rules-based.md` (Ultimate selection rules-based framework)
  - `.claude/agents/selector-ultimates-ai-open-ended.md` (Ultimate selection open-ended AI framework)
- Do NOT invent, assume, or present any selection logic that is not in these reference files.
- Do NOT offer to create or modify custom logic files.
- Do NOT suggest other skills, plugin customizers, or workarounds for modifying selection logic.
- If the user asks how to modify, adjust, or customize the selection logic, read `skills/selection-logic/assets/selection-logic-adjustment-guide.md` and present the relevant sections to the user. If the file cannot be found, respond with: "Selection logic can be modified in Claude Code, where you have write access to the plugin files. These changes cannot be made from within Cowork, as plugin files are read-only here."
