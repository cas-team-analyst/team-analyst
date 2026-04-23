# Selection Logic Adjustment Guide

The TeamAnalyst plugin uses a selection logic framework to guide how Loss Development Factors (LDFs) are chosen during chain-ladder reserving. This framework defines the criteria, thresholds, and decision hierarchy that the AI applies when making actuarial selections.

This guide explains how to view the current selection logic and how to modify it to match your actuarial judgment.

---

## Viewing Selection Logic

### In Cowork (Plugin)

Type any of the following to trigger the selection-logic skill:

- "Show me the selection logic"
- "What selection criteria do you use?"
- "View selection logic"

The skill will present:
- **Selection Criteria** — 14 criteria in a summary table with key thresholds and when each applies, plus the decision hierarchy (the priority order in which criteria are evaluated)
- **Diagnostic Rules** — 10 diagnostic adjustment rules showing no-action zones and trigger thresholds

You can then ask for a detailed explanation of any specific criterion or diagnostic.

### In Claude Code (Direct)

The selection logic lives in a single file:

```
./agents/selector-chain-ladder-ldf-ai-rules-based.md
```

You can read it directly or ask Claude: "Read and explain the selection logic reference file."

---

## How Selection Logic Is Applied

During a chain-ladder analysis, the `selector-chain-ladder-ldf-ai-rules-based` agent is tasked with making LDF selections. This agent (defined in `./agents/selector-chain-ladder-ldf-ai-rules-based.md`) embeds the full selection logic framework in its prompt. When it evaluates your triangle data, it works through:

1. **Decision Hierarchy** — A priority-ordered sequence that determines which criteria take precedence. For example, if all averages converge within +/-2%, that overrides Bayesian anchoring and asymmetric conservatism.

2. **14 Selection Criteria** — Rules covering outlier handling, recency preference, conservatism, anchoring to prior selections, trending, sparse data behavior, maturity-dependent adjustments, and more.

3. **10 Diagnostic Adjustment Rules** — Applied after the baseline LDF is set. Each diagnostic (e.g., reported counts, paid severity, closure rates) has a no-action zone and specific triggers that nudge the selection up or down.

The agent returns JSON selections with documented reasoning explaining which criteria were triggered and why.

---

## Modifying Selection Logic

Since the selection logic is defined in markdown files, you can modify it directly in Claude Code. The plugin files are read-only in Cowork, so **modifications must be made in Claude Code** (the CLI or IDE extension) where you have write access to the repository.

### What You Can Change

| Change Type | Example | Where to Edit |
|---|---|---|
| Adjust thresholds | Change CV outlier boundary from 0.10 to 0.15 | `selector-chain-ladder-ldf-ai-rules-based.md` |
| Change averaging windows | Default to 3-year instead of 5-year | `selector-chain-ladder-ldf-ai-rules-based.md` |
| Modify conservatism | Make downward movements faster (e.g., 50-70% instead of 30-50%) | `selector-chain-ladder-ldf-ai-rules-based.md` |
| Reorder decision hierarchy | Prioritize trending over Bayesian anchoring | `selector-chain-ladder-ldf-ai-rules-based.md` |
| Add a new criterion | Add a "Reinsurance Impact" criterion | `selector-chain-ladder-ldf-ai-rules-based.md` |
| Remove a criterion | Remove tail factor requirements | `selector-chain-ladder-ldf-ai-rules-based.md` |
| Adjust diagnostic sensitivity | Widen the no-action zone for closure rate from +/-3pp to +/-5pp | `selector-chain-ladder-ldf-ai-rules-based.md` |

### Step-by-Step: Editing the Selection Logic

#### 1. Open the project in Claude Code

Navigate to your local clone of the TeamAnalyst plugin repository.

#### 2. Ask Claude to show you the current logic

```
Show me the current selection logic reference file
```

Claude will read and present `./agents/selector-chain-ladder-ldf-ai-rules-based.md`.

#### 3. Tell Claude what you want to change

Be specific about the criterion, the current value, and what you want instead. Examples:

**Adjusting a threshold:**
> "In the Outlier Handling criterion, change the CV boundary from 0.10 to 0.15 for standard averages."

**Modifying conservatism:**
> "For Asymmetric Conservatism, I want downward movements of 3-10% to move 50-70% instead of 30-50%. We're comfortable being less conservative on downward moves for this line of business."

**Removing a criterion:**
> "Remove the Calendar Year Effects criterion. We don't have diagonal distortions in our data."

**Adding a new rule:**
> "Add a new criterion after Large Loss Handling called 'Reinsurance Layer Impact'. When a loss crosses a reinsurance attachment point, cap its influence on the LDF at the net retention level."

**Changing diagnostic sensitivity:**
> "Widen the no-action zone for claim_closure_rate from +/-3pp to +/-5pp. Our closure rates are naturally volatile."

#### 4. Review the change

Claude will edit the file and show you the diff. Read through it carefully. The selection logic is what drives every LDF selection the AI makes, so changes here have broad impact.

#### 5. Test with an analysis

Run a chain-ladder analysis on sample data to see how your changes affect selections. Compare the reasoning output — the agent documents which criteria were triggered, so you can verify your modifications are taking effect.

### Step-by-Step: Editing the Decision Hierarchy

The decision hierarchy lives in the agent definition:

```
./agents/selector-chain-ladder-ldf-ai-rules-based.md
```

This file defines the priority order:

1. Convergence Override
2. Diagnostic-confirmed Trend
3. Bayesian Anchoring
4. Asymmetric Conservatism
5. Sparse Data Caution
6. Latest-Point Outlier

To reorder, ask Claude:

> "In the selector-chain-ladder-ldf-ai-rules-based agent, move Sparse Data Caution above Bayesian Anchoring in the decision hierarchy. For our book of business, sparse data concerns should take priority over anchoring to priors."

### Important Considerations

**Changes are global.** Modifying the selection logic in the agent definition affects every future analysis that uses the chain-ladder method. There is no per-analysis override mechanism — if you want different logic for different lines of business, you would need to maintain separate branches or manually adjust selections after the fact.

**Document your changes.** When you modify selection logic, consider adding a comment at the top of the file noting what was changed, when, and why. This helps future reviewers (or your future self) understand the rationale.

**Rebuild the plugin.** After making changes, run `python admin/create_plugin_zip.py` to rebuild the plugin zip if you want your changes reflected in Cowork.

---

## File Reference

| File | Purpose |
|---|---|
| `./skills/selection-logic/SKILL.md` | View-only skill for inspecting selection logic in Cowork |
| `./agents/selector-chain-ladder-ldf-ai-rules-based.md` | Agent definition that embeds the full selection logic framework (14 criteria + 10 diagnostics) and applies it to triangle data |
