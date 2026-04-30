# Tail Cutoff Refactor Plan

## Phase 1: Move Cutoff Selection to LDF Selectors
- [x] Update LDF Selector Prompts
  - **Context:** Modify `selector-chain-ladder-ldf-ai-rules-based.agent.md` and `selector-chain-ladder-ldf-ai-open-ended.agent.md`.
  - **Action:** Agents must now select a `tail_cutoff` interval (the last interval selected before curve fitting) alongside LDFs. They already receive CV, slope, etc., to make this decision. Update the output JSON schema to include the cutoff.

- [x] Update Chain Ladder Selections Extraction
  - **Context:** Modify `2b-chainladder-update-selections.py`.
  - **Action:** Parse the `tail_cutoff` from the agents' responses and persist it (in JSON, Parquet, or Excel) so it can be passed to the tail fitting step.

- [x] Update Chain Ladder Excel Workbook
  - **Context:** Modify `2a-chainladder-create-excel.py`.
  - **Action:** Add rows/cells to capture the selected tail cutoff for each method (User, Rules-Based AI, Open-Ended AI). The workbook should stop populating LDF cells at the chosen cutoff (different methods may populate different numbers of cells).

## Phase 2: Refactor Tail Fitting & Diagnostics
- [x] Refactor Tail Methods Script
  - **Context:** Modify `2c-tail-methods-diagnostics.py`.
  - **Action:** Remove logic that searches for starting age candidates. Instead, read the `tail_cutoff` selected from Phase 1.
  - **Action:** Only fit the tail curves on the selected LDFs up to the cutoff.
  - **Action:** Add curve-based LDFs for the intervals *after* the cutoff, as well as the final CDF at the end of the curve (reference `examples/ken-tail-factor` for final CDF logic).
  - **Action:** Expand context parameters to include min/max age-to-age factors (from empirical ATAs at cutoff interval), along with average, slope, and CV from `4_ldf_averages.parquet`.

## Phase 3: Update Tail Selector Agents
- [x] Update Tail Selector Prompts — Renamed to `selector-tail-curve-*`, output schema now only requires `method` (no `tail_factor`). Reasoning updated to focus on curve selection.

- [x] Update Tail Excel & Selections Extraction — `2d` now outputs "Tail Curve Selection" (Method/Reasoning/Notes, no Tail Factor column); MD context has a **Cutoff Diagnostics** block with avg/min/max ATA, CV, slope, monotonicity at the cutoff. `2e` column mapping updated to match.

## Phase 4: Downstream Updates
- [ ] Update Analysis Workbook
  - **Context:** Modify `6-analysis-create-excel.py`.
  - **Action:** When calculating Incurred/Paid/Other, use the LDFs from the tail curve to fill out ages after the selected LDFs drop off due to the tail cutoff. Highlight these curve-derived LDFs visually to distinguish them from empirical selections.

- [ ] Update Documentation
  - **Context:** Modify `skills/reserving-analysis/SKILL.md` and `progress.md`.
  - **Action:** Update the workflow descriptions to accurately describe the new separation of concerns: LDF agents pick the cutoff, Tail agents pick the curve.
