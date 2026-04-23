# TeamAnalyst

TeamAnalyst is the result of a research initiative by the Casualty Actuarial Society (CAS) to explore the use of agentic tools in actuarial work. It targets a specific workflow: development of actuarial reserve ultimate estimates. 

The project is a collection of Markdown files and Python scripts that agentic tools can use to run the workflow, organized to match the expected organization of these files for different tools.

> **DISCLAIMER**: TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

## Quick Start

These files can be used with many different agentic tools. For most users, we suggest Claude CoWork:

1. Sign up for a Claude Pro account (~$20/month) at https://claude.ai/ and follow installation instructions at https://support.claude.com/en/articles/10065433-installing-claude-desktop
2. Open Claude Desktop and select "CoWork" on the top left (default is "Chat")
3. Download `teamanalyst-cowork.zip` from https://github.com/cas-team-analyst/team-analyst/blob/main/plugins/teamanalyst-cowork.zip
4. Import the plugin: Customize > Personal plugins > + > Create plugin > Upload plugin > Browse files > Select `teamanalyst-cowork.zip`
5. Click "New task"
6. Type "/reserving-analysis" (it will auto-complete and you can press enter to select it) in the chat box and press enter to get started!

Want to test the workflow quickly? Sample input data is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data. Provide a file from sample-data to the agent as your input data. A sample workflow run with example output files is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run.

## This Repository

The repository ships as a full bundle, not a single-skill install. The plugin and extension layouts include:

- every skill under `skills/`
- selector custom subagents under `skills/reserving-analysis/agents/`
- skill-local assets and scripts used by the reserving workflow

The primary end-user entry points are:

- `/help` for orientation and available workflows
- `/reserving-analysis` for the full reserving workflow
- `/selection-logic` to inspect the LDF and tail selection framework
- `/peer-review` to review a completed analysis

## Repository Layout

- `skills/` contains the TeamAnalyst skills, each with its own `SKILL.md` plus any `assets/` and `scripts/`
- `skills/reserving-analysis/agents/` contains selector custom subagents used by the reserving workflow
- `.claude-plugin/` contains the Claude marketplace and plugin metadata
- `GEMINI.md` and `gemini-extension.json` define Gemini extension context and manifest metadata
- `create_plugin_cowork.py` packages skills for upload into CoWork and writes `plugins/teamanalyst-cowork.zip`
- `plugins/` stores generated plugin artifacts for distribution
- `sample-data/` contains example input data and a sample run with representative outputs
- `guides/` contains supplementary notes for developers and advanced users
- `AGENTS.md` and `CLAUDE.md` capture workflow and maintenance guidance for contributors

## Advanced

See `guides/` for more information for advanced users looking to build on this work.

Contributions via GitHub Issues and Pull Requests are welcome!

## Other Tools

| Agent | Install |
|-------|---------|
| **Claude Code** | `claude plugin marketplace add cas-team-analyst/team-analyst && claude plugin install team-analyst@team-analyst` |
| **Gemini CLI** | `gemini extensions install https://github.com/cas-team-analyst/team-analyst` |
| **Cursor** | `npx skills add cas-team-analyst/team-analyst -a cursor` |
| **Windsurf** | `npx skills add cas-team-analyst/team-analyst -a windsurf` |
| **Copilot** | `npx skills add cas-team-analyst/team-analyst -a github-copilot` |
| **Cline** | `npx skills add cas-team-analyst/team-analyst -a cline` |
| **Any other** | `npx skills add cas-team-analyst/team-analyst` |

Uninstall: `npx skills remove team-analyst`
