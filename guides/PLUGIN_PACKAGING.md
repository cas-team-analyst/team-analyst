# Plugin Packaging Reference

Research conducted: 2026-09-18

This guide records what each supported tool accepts as a plugin or skill install, how this repo is packaged for them, and what has and has not been verified.

## Summary

In August 2026 the vendors agreed on an open plugin format called [Agent Plugins 1.0](https://agent-plugins.org/specification). A plugin is a directory with a root `plugin.json`, a `skills/` folder, and an optional `mcp.json`. VS Code, GitHub Copilot, Cursor, Codex and ChatGPT read it, and Antigravity's plugin layout is nearly identical. Claude and Microsoft keep their own formats.

This repo ships a root `skills/` folder and a root `plugin.json`, so most tools can install straight from the repo's Git URL. Zips are built into `import/` by `create_import_zips.py` for tools that take an upload or a manual folder copy.

## Key findings

- Agent Plugins 1.0 requires only `$schema` and `name` in `plugin.json`. Skills live in `skills/<name>/SKILL.md`. The spec covers skills and MCP servers only. Commands, hooks, subagents and rules stay client specific. ([spec](https://agent-plugins.org/specification), published 2026-08-06)
- A plugin is a directory, not an archive. Installation is left to each client, so installing from a link means a Git URL, not a zip. ([spec](https://agent-plugins.org/specification))
- VS Code, Copilot CLI and Codex accept the root `plugin.json` format. Copilot CLI also falls back to `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and Codex lists `.claude-plugin/marketplace.json` as a legacy marketplace location. ([Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [Codex plugins](https://developers.openai.com/plugins/build/plugins))
- Anthropic is not a listed adopter. Claude Code and Cowork keep `.claude-plugin/`. ([Agent Plugins explainer](https://blog.agentailor.com/posts/agent-plugins-explained))
- Microsoft 365 Copilot Agent Builder takes a per-skill zip only (max 8 skills per agent, 50 MB per zip, `SKILL.md` at the zip root, instructions under 20,000 characters). It has no plugin format. ([Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills))

## Per-tool formats

| Tool | Format | Install route | Status |
|------|--------|---------------|--------|
| Claude Code | `.claude-plugin/plugin.json` and `marketplace.json` | `claude plugin marketplace add cas-team-analyst/team-analyst`, then `claude plugin install team-analyst@team-analyst`. `--scope user` (default), `project` or `local` | Verified against the installed CLI. ([docs](https://code.claude.com/docs/en/plugin-marketplaces)) |
| Claude Cowork | Zip of `.claude-plugin/`, `skills/`, `agents/` | Upload `import/teamanalyst-plugin-cowork.zip` | Built by `create_import_zips.py`. |
| Claude Chat or Desktop | Per-skill zip | Upload `import/<skill>.zip` as a Skill | Built by `create_import_zips.py`. |
| Microsoft Copilot | Per-skill zip, `SKILL.md` at zip root | Upload `import/<skill>.zip` in Agent Builder | Uses the same per-skill zips. |
| Codex | Root `plugin.json` (Agent Plugins) or `.codex-plugin/plugin.json`. Marketplace at `.agents/plugins/marketplace.json` | `codex plugin marketplace add cas-team-analyst/team-analyst`, then `/plugins` | Not tested. Docs say marketplace entries need `policy` fields the Claude marketplace file lacks. Community repos ship a separate `.agents/plugins/marketplace.json`. ([docs](https://developers.openai.com/plugins/build/plugins)) |
| GitHub Copilot CLI | Root `plugin.json`, or `.github/plugin/marketplace.json`, or `.claude-plugin/marketplace.json` | `copilot plugin install cas-team-analyst/team-analyst`, or `copilot plugin marketplace add` then `copilot plugin install team-analyst@team-analyst` | Not tested. ([docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)) |
| VS Code (Copilot) | Root `plugin.json` with the Agent Plugins `$schema`, or `.claude-plugin/plugin.json` | Command palette "Chat: Install Plugin From Source" with the repo URL, or add the repo to `chat.plugins.marketplaces` | Not tested. ([docs](https://code.visualstudio.com/docs/agent-customization/agent-plugins)) |
| Cursor | Root `plugin.json` (Agent Plugins) or `.cursor-plugin/plugin.json`. Multi-plugin repos use `.cursor-plugin/marketplace.json` | Team plans: Dashboard, Plugins, Import from Repo. Individuals: copy into `~/.cursor/plugins/local` and restart | Not tested. No GitHub URL install for individuals is in Cursor's docs. One community repo shows `agent plugin marketplace add <git URL>`, which is unconfirmed. ([docs](https://cursor.com/docs/reference/plugins)) |
| Antigravity CLI | Root `plugin.json` (`name` required) with `skills/`, `agents/`, `rules/` | `agy plugin install https://github.com/cas-team-analyst/team-analyst`. Also accepts a local folder or `plugin@marketplace`. No scope option, so installs are global | Git URL install and manifest validation tested with `agy` on 2026-09-18. ([docs](https://antigravity.google/docs/plugins?tab=cli)) |
| Antigravity IDE / 2.0 | Same plugin folder | Copy to `.agents/plugins/` (project) or `~/.gemini/config/plugins/` (global). The Customizations panel lists installed plugins | Manual copy is the only documented route. |
| ChatGPT | Codex-style plugin | Workspace admins can publish internally | Depends on the Codex plugin. ([submission](https://developers.openai.com/plugins/deploy/submission)) |
| Gemini CLI | `gemini-extension.json` and `GEMINI.md` | `gemini extensions install <repo URL>`. Global only | Retired for free and individual users on 2026-06-18. |
| `npx skills` (any agent) | Root `skills/` folder | `npx skills add cas-team-analyst/team-analyst -a <agent>`. Project by default, `-g` for global | Project and global behavior not checked against the CLI. |

Windsurf and Cline are out of scope.

## How this repo is packaged

`create_import_zips.py` at the repo root writes four zips into `import/`:

| Zip | Contents | Used by |
|-----|----------|---------|
| `teamanalyst-plugin-cowork.zip` | `.claude-plugin/` (without `marketplace.json`), `skills/`, and the selector agents copied to `agents/` as `selector-x.md` | Claude Cowork |
| `teamanalyst-plugin-other.zip` | Root `plugin.json` and `skills/`, with the selector agents left in `skills/reserving-analysis/agents/` as `selector-x.agent.md` | Cursor local folder, Antigravity IDE, and other tools that read Agent Plugins |
| `reserving-analysis.zip`, `peer-review.zip` | One skill's contents at the zip root | Claude Chat or Desktop, Microsoft Copilot |

All zips exclude `__pycache__/`, `.pytest_cache/`, `.pyc` files and `conftest.py`. The script stops with an error if `version` differs across `plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (when a plugin entry has one) and `gemini-extension.json`.

The root `plugin.json` is:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "team-analyst",
  "version": "1.0.0",
  "description": "Actuarial reserving workflow with selector subagents and Python helper scripts.",
  "author": { "name": "CAS TeamAnalyst Research Team", "url": "https://github.com/cas-team-analyst" },
  "homepage": "https://github.com/cas-team-analyst/team-analyst",
  "repository": "https://github.com/cas-team-analyst/team-analyst",
  "license": "MIT"
}
```

The spec allows only the ten listed top-level fields, so anything else warns. The repo `LICENSE` is MIT.

### Selector agents

Agent Plugins 1.0 has no portable subagent slot. The workflow refers to the selector agents by bare name (for example `selector-tail-curve-ai-framework`) with no path, so it does not depend on the folder they sit in. Claude Cowork gets them in a top-level `agents/` folder. Other tools get them inside the skill folder.

## Verification status

Checked 2026-09-18 with the `claude` and `agy` CLIs installed on the dev machine.

Verified:

- `agy plugin install <git URL>` clones the repo and installs it. A bad URL fails at `git clone`. Local folders and `plugin@marketplace` targets are also accepted.
- `agy plugin validate` passes on the repo with the root `plugin.json`, reporting "skills: 2 processed". Before the root manifest existed it failed with "missing plugin.json".
- `agy plugin import` copies plugins in from `gemini` or `claude`. It does not read a Claude marketplace from a repo.
- `agy plugin install` has no scope option.
- `claude plugin install` and `claude plugin marketplace add` both take `--scope` with `user` (default), `project` or `local`.

Not verified:

- Codex: whether `codex plugin marketplace add cas-team-analyst/team-analyst` accepts `.claude-plugin/marketplace.json` as is. OpenAI's docs list it as a legacy marketplace location, but they also say entries need `policy` fields, and community repos ship a separate `.agents/plugins/marketplace.json`. A community repo also reports that skills-only plugins need no Codex manifest because Codex finds `skills/*/SKILL.md` itself. Codex is not installed on the dev machine.
- Cursor: whether individuals can install from a GitHub link. Cursor's docs only show team import from a repo. Cursor is not installed on the dev machine.
- Copilot CLI and VS Code: install routes follow the docs and have not been run. Whether a root `plugin.json` and `.claude-plugin/plugin.json` in the same repo cause either tool to pick the wrong one is unknown. VS Code detects the Agent Plugins format from the `$schema` value.
- Project versus global scope for Codex, Copilot CLI and `npx skills -g`.
- Whether a zip of the plugin folder installs directly in any tool. The spec says plugins are directories.
- The reserving workflow has not been run end to end from a non-Claude install.

## Sources

1. [Agent Plugins Specification v1.0.0](https://agent-plugins.org/specification), 2026-08-06
2. [Agent plugins in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-plugins)
3. [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
4. [Creating a plugin marketplace for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace)
5. [Package your plugin, OpenAI Developers](https://developers.openai.com/plugins/build/plugins)
6. [Cursor plugins reference](https://cursor.com/docs/reference/plugins) and [Cursor plugins](https://cursor.com/docs/plugins)
7. [Plugins in Google Antigravity](https://antigravity.google/docs/plugins?tab=cli)
8. [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
9. [Add custom skills in Agent Builder, Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills), 2026-09-03
10. [Agent Plugins explained](https://blog.agentailor.com/posts/agent-plugins-explained), secondary source
