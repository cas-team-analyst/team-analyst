# TeamAnalyst Handoff

## Purpose

This file summarizes the repository migration work completed so far, the current validated state, and the remaining tasks for the next agent. The immediate unresolved item is the move from bundled selector prompt files in `agents/` to real clean-context custom agents for selection tasks.

## What Was Completed

### Packaging and install surface

- Updated the repo to use repo-root `skills/` and `agents/` as the bundle source of truth.
- Reworked `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` to point at `cas-team-analyst/team-analyst` and represent a single TeamAnalyst bundle install.
- Added Gemini support with root `gemini-extension.json` and `GEMINI.md`.
- Rewrote `README.md` to use Caveman-style install instructions for:
  - Claude Code marketplace install
  - Gemini CLI extension install
  - `npx skills add` installs for Cursor, Windsurf, Cline, and Copilot
  - local zip build flow
- Updated `admin/create_plugin_zip.py` so the generated zip includes:
  - all repo-root `skills/`
  - all repo-root `agents/`
  - plugin metadata files
  - Gemini files
- Fixed the packager to exclude generated artifacts such as `__pycache__/` and `.pyc` files.

### Documentation and repo guidance

- Reworked `AGENTS.md` into a lightweight routing file that points at the main skills.
- Rebuilt `CLAUDE.md` into the project playbook for packaging, documentation, and source-of-truth ownership.
- Added repo memory documenting packaging conventions and the bundle model.

### Validation already completed

- Rebuilt `.claude-plugin/team-analyst-plugin.zip` successfully after fixing the packager.
- Confirmed the zip no longer included Python cache artifacts.
- Ran targeted error checks on the edited packaging and documentation files.
- Confirmed there is currently:
  - no `.github/` directory
  - no `.github/agents/` directory
  - no `*.agent.md` files anywhere in the repo

## Current Architectural State

### What `agents/` currently is

The files under `agents/` are currently selector/reference prompt files bundled with the repo. They are used as content that skills can read or reference. They are not formal custom agents.

Current selector/reference files include:

- `selector-chain-ladder-ldf-ai-open-ended.md`
- `selector-chain-ladder-ldf-ai-rules-based.md`
- `selector-tail-factor-ai-open-ended.md`
- `selector-tail-factor-ai-rules-based.md`
- `selector-ultimates-ai-open-ended.md`
- `selector-ultimates-ai-rules-based.md`

### What is missing for real subagents

The requested clean-context subagent model has not been implemented yet. There are no formal custom agents registered in the workspace. Based on the VS Code custom-agent guidance reviewed during this session, real custom agents should live under:

- `.github/agents/*.agent.md`

Those files can define focused subagents with their own frontmatter and tool access, and can be invoked as true custom agents rather than treated as plain markdown prompts.

## Important Findings From Research

### Custom-agent implementation direction

The correct path for real workspace custom agents is:

- `.github/agents/`

Relevant frontmatter fields from the researched VS Code agent format include:

- `name`
- `description`
- `tools`
- `model`
- `argument-hint`
- `agents`
- `user-invocable`
- `disable-model-invocation`
- `handoffs`

The key design goal for the next phase is to create true selection agents that run with isolated context rather than relying on loose references to `agents/*.md` prompt files.

### Current workflow/docs still assume subagents conceptually

The reserving workflow already talks about selection subagents, especially in `skills/reserving-analysis/assets/PROGRESS.md`, but those references are conceptual only. There is no registered custom-agent implementation behind them yet.

## Current Skills State

The current `skills/` directory contains:

- `excel-formulas/`
- `help/`
- `peer-review/`
- `reserving-analysis/`
- `selection-logic/`

During the prior conversation, the user clarified that `python` and `improve-agent` had been in `skills/` by accident and were moved out. The next agent should treat the above five folders as the current expected skill surface unless the repo changes again.

## Files Most Relevant For Continuation

### Packaging and install

- `README.md`
- `CLAUDE.md`
- `AGENTS.md`
- `admin/create_plugin_zip.py`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `gemini-extension.json`
- `GEMINI.md`

### Workflow and selector behavior

- `skills/reserving-analysis/SKILL.md`
- `skills/reserving-analysis/assets/PROGRESS.md`
- `skills/selection-logic/SKILL.md`
- `agents/*.md`

## Outstanding Work

### Highest priority

Implement real custom selection agents so the workflow can hand work to clean-context subagents instead of only referencing prompt files.

### Suggested next tasks

1. Create `.github/agents/`.
2. Add real custom-agent files for the six selector roles:
   - chain ladder LDF rules-based
   - chain ladder LDF open-ended
   - tail rules-based
   - tail open-ended
   - ultimate rules-based
   - ultimate open-ended
3. Keep each custom agent narrowly scoped with minimal tools and a clear output contract.
4. Decide whether the existing `agents/*.md` files become:
   - source prompt content consumed by the new `.agent.md` files, or
   - obsolete files replaced fully by `.github/agents/*.agent.md`
5. Update `skills/reserving-analysis/assets/PROGRESS.md` so its “task a subagent” language points to real custom-agent names and not generic prompt files.
6. Re-check `README.md`, `CLAUDE.md`, and `AGENTS.md` after the custom-agent implementation so docs reflect the new agent model accurately.

### Secondary cleanup

- Remove or update any stale references to old `.claude/agents` or `.claude/skills` assumptions if any remain.
- Re-scan docs for references to removed accidental skills.
- Validate whether the plugin packaging should include `.github/agents/` once real custom agents are added.

## Recommended Implementation Shape For The Next Agent

Use the current selector/reference files as the behavioral source material, but create true custom-agent wrappers under `.github/agents/` that:

- expose a focused role per selector
- restrict tool access to the minimum needed
- are likely `user-invocable: false` if they are intended to be dispatched only by the main workflow
- clearly specify expected inputs and output artifacts
- preserve the distinction between rules-based and open-ended selection logic

The main workflow should then refer to these real agent names explicitly instead of using “subagent” as a loose concept.

## Known Constraint

The repo migration to the new bundle/install layout is substantially complete, but the clean-context custom-agent architecture is still only researched, not implemented. The next agent should not assume any real subagent registration already exists.