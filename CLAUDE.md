# CLAUDE.md — TeamAnalyst

## README is a product artifact

The README is the install surface for this repo. Treat it like product copy, not internal notes.

Rules for README changes:

- Keep install commands accurate for every tool in the "Installation for Other Agentic Tools" section. Tools are grouped by provider (Anthropic, OpenAI, Google, Microsoft, GitHub, Other tools).
- Each tool section starts with the install command. Tools with no terminal command start with the italic line "There is no terminal command to install the skill into this tool." and then give the UI steps.
- Only list a tool once its install path is verified against the vendor's docs, and link those docs.
- Keep the bundle story clear: TeamAnalyst installs all skills and all selector/reference agents together.
- Prefer language that a non-specialist can follow without knowing how agent plugins work internally.
- If packaging behavior changes, update the install section and the "Helpful Commands" zip-build instructions in the same change.
- If you change the skills, run `python create_import_zips.py`.

---

## Project overview

TeamAnalyst is a skill-and-script bundle for actuarial reserve analysis workflows. It packages multiple skills, selector prompts, and Python helper scripts so AI coding agents can guide or execute a repeatable reserving workflow.

The core user-facing workflow is `reserving-analysis`, supported by:

- `peer-review` for reviewing a completed analysis

`skills/` ships exactly these two skills. Contributor-only helper skills (`python`, `excel-formulas`, `improve-agent`, and the caveman skills) live in `.claude/skills/` and `.agents/skills/`, are not part of the shipped bundle, and must not be referenced from shipped files.

The selector files in `skills/reserving-analysis/agents/` are custom subagents consumed by the workflow (six `selector-*.agent.md` files covering chain ladder LDFs, tail curves, and ultimates, each in a framework and an open-ended variant). They must stay aligned with the workflow instructions in `skills/`. There is no separate skill for viewing or explaining selection logic; agents and users refer directly to the selector agent files in `skills/reserving-analysis/agents/`.

---

## File structure and what owns what

### Single source of truth files — edit these directly

| File | What it controls |
|------|------------------|
| `skills/reserving-analysis/SKILL.md` | Main reserving workflow, sequencing, user interaction model, and script/template usage rules. |
| `skills/peer-review/SKILL.md` | Peer review workflow and findings expectations. |
| `skills/reserving-analysis/agents/*.agent.md` | Selector custom subagents. Update these when the decision framework changes. |
| `README.md` | User-facing install and usage documentation. |
| `skills/reserving-analysis/scripts/` | Python helper scripts the workflow runs, with their own `tests/` and `requirements.txt`. |
| `create_import_zips.py` | Builds every zip in `import/` (Cowork plugin, other-tools plugin, one zip per skill) and controls what each includes. |
| `guides/` | Supporting docs linked from the README (data privacy, selection customization, developer notes, executive summary). |
| `.claude-plugin/marketplace.json` | Claude Code marketplace metadata for the full bundle install. |
| `.claude-plugin/plugin.json` | Claude plugin package metadata. |
| `plugin.json` | Agent Plugins 1.0 manifest at the repo root, read by Antigravity (and expected by VS Code, Copilot CLI, Codex, Cursor). Keep `version` equal to the other manifests. The build script fails on a mismatch. |
| `GEMINI.md` | Gemini context file that loads the TeamAnalyst skill bundle. It may only reference skills that exist under `skills/`. |
| `gemini-extension.json` | Gemini extension manifest metadata. |

### Generated artifacts — do not hand-edit unless necessary

| File | How it is produced |
|------|--------------------|
| `import/teamanalyst-plugin-cowork.zip` | Built locally by `create_import_zips.py`. Bundles `.claude-plugin/` and copies the selector agents to `agents/`. |
| `import/teamanalyst-plugin-other.zip` | Built by `create_import_zips.py`. Root `plugin.json` plus `skills/`, for unzipping into `~/.cursor/plugins/local/`, `~/.gemini/config/plugins/` or `.agents/plugins/`. |
| `import/reserving-analysis.zip`, `import/peer-review.zip` | Built locally by `create_import_zips.py`. Skill folder contents at the zip root, for upload in Claude Chat or Desktop and Microsoft Copilot. |

Rebuild all zips from the project root:

```bash
python create_import_zips.py
```

Rebuild after any change under `skills/` or `.claude-plugin/`, and commit the zips. There is no CI build. If the zip contents are wrong, fix the build scripts or the source files instead of editing a zip manually.

---

## Packaging workflow

This repo currently ships one TeamAnalyst bundle, not separate per-skill plugin packages.

Current packaging rules:

1. Claude Code installs one plugin: `team-analyst@team-analyst`
2. That plugin should include the full `skills/` tree (which now includes the subagents)
3. Gemini installs the repo as one extension via `gemini-extension.json` + `GEMINI.md`
4. `npx skills add` targets the repo and installs the TeamAnalyst skill folders for supported agents
5. The Cowork plugin zip and the per-skill upload zips are built locally with the scripts above

When changing packaging behavior:

- keep repo-root `skills/` as the primary source layout
- do not reintroduce old `.claude/skills` or `.claude/agents` assumptions
- exclude generated artifacts such as `__pycache__/`, `.pyc` files, and `conftest.py` from shipped bundles
- update README install instructions in the same change

---

## Skill system

Skills are Markdown files with YAML frontmatter under `skills/<name>/SKILL.md`.

General rules:

- user-facing workflow changes belong in the relevant `SKILL.md`
- assets and scripts that a skill depends on should live alongside that skill under `assets/` and `scripts/`
- if a skill references selector logic, prefer the canonical subagents in its local `agents/` directory rather than duplicating that logic into the skill
- keep descriptions specific, because they are part of skill discovery

The default user journey should begin with `reserving-analysis`.

---

## Agent distribution

How TeamAnalyst reaches each agent type:

| Agent | Mechanism | Auto-activates? |
|-------|-----------|-----------------|
| Claude Code | Marketplace plugin from `.claude-plugin/` | No guaranteed auto-activation; user invokes TeamAnalyst skills on demand |
| Claude Chat or Desktop | Upload `import/*.zip` as Skills (README Quick Start) | No, user invokes skills as needed |
| Claude Cowork | `import/teamanalyst-plugin-cowork.zip` | No, user invokes skills as needed |
| Codex | `npx skills add cas-team-analyst/team-analyst -a codex`. Plugin: `codex plugin marketplace add cas-team-analyst/team-analyst` (docs-based, untested) | No, user invokes with `$reserving-analysis` |
| Gemini CLI | Extension with `GEMINI.md` context file. Retired by Google for free and individual users on 2026-06-18, still works for Enterprise and paid API key users | Yes, context file loads the skill bundle |
| Antigravity CLI and IDE | CLI: `agy plugin install https://github.com/cas-team-analyst/team-analyst` (root `plugin.json`). Also `npx skills add cas-team-analyst/team-analyst -a antigravity`, or copy `skills/*` into `.agents/skills/` | No, user invokes with `/reserving-analysis` |
| Cursor | `npx skills add cas-team-analyst/team-analyst -a cursor`. Plugin (docs-based, untested): unzip `teamanalyst-plugin-other.zip` into `~/.cursor/plugins/local/`, or team import from repo | No, user invokes skills as needed |
| GitHub Copilot | `npx skills add cas-team-analyst/team-analyst -a github-copilot`. Plugin (docs-based, untested): `copilot plugin install cas-team-analyst/team-analyst` in Copilot CLI, or "Chat: Install Plugin From Source" in VS Code | No, user invokes skills as needed |
| Microsoft Copilot | Upload `import/*.zip` in Agent Builder (Frontier Program, work or school account) | No, user invokes with `/reserving-analysis` |
| ChatGPT, Google Gemini | Paste `SKILL.md` into a custom GPT or Gem and upload `assets/` files. Reduced functionality, no script execution | No |
| Others | `npx skills add cas-team-analyst/team-analyst` | No, user invokes skills as needed |

The `skills` CLI installs into the user's `.agents/skills/` (or the tool's own folder) and discovers skills from the repo's root `skills/` folder. This repo's own `.agents/skills/` holds contributor-only skills and is not a link to `skills/`.

This repo does not currently rely on Claude hooks for behavior.

---

## Testing and fixtures

`sample-data/` contains sample and checkpoint data for validating workflow changes. Use it when changing:

- skill sequencing
- selector interpretation behavior
- script expectations
- packaging assumptions that affect shipped workflow assets

`tests/` and `skills/reserving-analysis/scripts/tests/` contain targeted automated checks for parts of the repo. Do not assume test coverage exists for every documentation or packaging path.

When changing a script or packaging rule, prefer a narrow validation step immediately after the edit.

---

## Key rules for agents working here

- Edit the files in `skills/` when changing workflow behavior. Do not try to encode workflow changes only in README or packaging manifests.
- Edit the subagent files in `skills/reserving-analysis/agents/` when changing selector logic. Keep the main workflow aligned with those subagents.
- Keep `README.md`, `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`, `GEMINI.md`, and `gemini-extension.json` consistent with one another.
- Keep the agent distribution table above in sync with the README install section.
- Keep the bundle model intact: the plugin ships all skills and all selector/reference agents together.
- If packaging output is wrong, fix the zip build scripts rather than manually editing a zip, and rebuild.
- Use `sample-data/` to test workflow changes before declaring the packaging or skill update complete.
