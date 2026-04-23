# CLAUDE.md — TeamAnalyst

## README is a product artifact

The README is the install surface for this repo. Treat it like product copy, not internal notes.

Rules for README changes:

- Keep install commands accurate for Claude Code, Gemini CLI, and `npx skills`.
- Keep the bundle story clear: TeamAnalyst installs all skills and all selector/reference agents together.
- Prefer language that a non-specialist can follow without knowing how agent plugins work internally.
- If packaging behavior changes, update the install section and the local zip-build instructions in the same change.

---

## Project overview

TeamAnalyst is a skill-and-script bundle for actuarial reserve analysis workflows. It packages multiple skills, selector prompts, and Python helper scripts so AI coding agents can guide or execute a repeatable reserving workflow.

The core user-facing workflow is `reserving-analysis`, supported by:

- `help` for orientation and skill discovery
- `selection-logic` for reviewing the actuarial decision framework
- `peer-review` for reviewing a completed analysis
- supporting/internal skills such as `python`, `excel-formulas`, and `improve-agent`

The selector files in `skills/reserving-analysis/agents/` are custom subagents consumed by the workflow. They must stay aligned with the workflow instructions in `skills/`.

---

## File structure and what owns what

### Single source of truth files — edit these directly

| File | What it controls |
|------|------------------|
| `skills/help/SKILL.md` | Orientation flow and top-level skill discovery. |
| `skills/reserving-analysis/SKILL.md` | Main reserving workflow, sequencing, user interaction model, and script/template usage rules. |
| `skills/selection-logic/SKILL.md` | How selector framework content is presented to users. |
| `skills/peer-review/SKILL.md` | Peer review workflow and findings expectations. |
| `skills/reserving-analysis/agents/*.agent.md` | Selector custom subagents. Update these when the decision framework changes. |
| `README.md` | User-facing install and usage documentation. |
| `.github/workflows/build-plugin.yml` | CI plugin packaging behavior and file inclusion rules. |
| `.claude-plugin/marketplace.json` | Claude Code marketplace metadata for the full bundle install. |
| `.claude-plugin/plugin.json` | Claude plugin package metadata. |
| `GEMINI.md` | Gemini context file that loads the TeamAnalyst skill bundle. |
| `gemini-extension.json` | Gemini extension manifest metadata. |

### Generated artifacts — do not hand-edit unless necessary

| File | How it is produced |
|------|--------------------|
| `.claude-plugin/team-analyst-plugin.zip` | Auto-built by `.github/workflows/build-plugin.yml` CI. |

If the zip contents are wrong, fix `.github/workflows/build-plugin.yml` or the source files in `skills/` and `.claude-plugin/` instead of editing the zip manually.

---

## Packaging workflow

This repo currently ships one TeamAnalyst bundle, not separate per-skill plugin packages.

Current packaging rules:

1. Claude Code installs one plugin: `team-analyst@team-analyst`
2. That plugin should include the full `skills/` tree (which now includes the subagents)
3. Gemini installs the repo as one extension via `gemini-extension.json` + `GEMINI.md`
4. `npx skills add` targets the repo and installs the TeamAnalyst skill folders for supported agents
5. The CoWork plugin zip is automatically built by `.github/workflows/build-plugin.yml` CI

When changing packaging behavior:

- keep repo-root `skills/` as the primary source layout
- do not reintroduce old `.claude/skills` or `.claude/agents` assumptions
- exclude generated artifacts such as `__pycache__/` and `.pyc` files from shipped bundles
- update README install instructions in the same change

---

## Skill system

Skills are Markdown files with YAML frontmatter under `skills/<name>/SKILL.md`.

General rules:

- user-facing workflow changes belong in the relevant `SKILL.md`
- assets and scripts that a skill depends on should live alongside that skill under `assets/` and `scripts/`
- if a skill references selector logic, prefer the canonical subagents in its local `agents/` directory rather than duplicating that logic into the skill
- keep descriptions specific, because they are part of skill discovery

The default user journey should begin with `help` or `reserving-analysis`.

---

## Agent distribution

How TeamAnalyst reaches each agent type:

| Agent | Mechanism | Auto-activates? |
|-------|-----------|-----------------|
| Claude Code | Marketplace plugin from `.claude-plugin/` | No guaranteed auto-activation; user invokes TeamAnalyst skills on demand |
| Gemini CLI | Extension with `GEMINI.md` context file | Yes, context file loads the skill bundle |
| Cursor | `npx skills add cas-team-analyst/team-analyst -a cursor` | No, user invokes skills as needed |
| Windsurf | `npx skills add cas-team-analyst/team-analyst -a windsurf` | No, user invokes skills as needed |
| Cline | `npx skills add cas-team-analyst/team-analyst -a cline` | No, user invokes skills as needed |
| Copilot | `npx skills add cas-team-analyst/team-analyst -a github-copilot` | No, user invokes skills as needed |
| Others | `npx skills add cas-team-analyst/team-analyst` | No, user invokes skills as needed |

This repo does not currently rely on Claude hooks for behavior.

---

## Testing and fixtures

`demo/` contains sample and checkpoint data for validating workflow changes. Use it when changing:

- skill sequencing
- selector interpretation behavior
- script expectations
- packaging assumptions that affect shipped workflow assets

`tests/` contains targeted automated checks for parts of the repo. Do not assume test coverage exists for every documentation or packaging path.

When changing a script or packaging rule, prefer a narrow validation step immediately after the edit.

---

## Key rules for agents working here

- Edit the files in `skills/` when changing workflow behavior. Do not try to encode workflow changes only in README or packaging manifests.
- Edit the subagent files in `skills/reserving-analysis/agents/` when changing selector logic. Keep the main workflow aligned with those subagents.
- Keep `README.md`, `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `GEMINI.md`, and `gemini-extension.json` consistent with one another.
- Keep the bundle model intact: the plugin ships all skills and all selector/reference agents together.
- If CI packaging output is wrong, fix `.github/workflows/build-plugin.yml` rather than manually editing the zip.
- Use `demo/` to test workflow changes before declaring the packaging or skill update complete.