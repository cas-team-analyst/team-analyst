# TeamAnalyst

**[Quick Start](#quick-start)** | **[Contribute](#make-a-contribution)** | **[Repository Layout](#repository-layout)** | **[How It Works](#how-it-works)** | **[Resources](#additional-resources)** | **[Install](#installation-for-other-agentic-tools)**

TeamAnalyst is the result of a research initiative by the Casualty Actuarial Society (CAS) to explore the use of agentic tools in actuarial work. It targets a specific workflow: development of actuarial reserve ultimate estimates. 

The project is a collection of Markdown files and Python scripts that agentic tools can use to run the workflow, organized to match the expected organization of these files for different tools.

> **DISCLAIMER**: TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

_These files can be downloaded via `git clone` or Code (green button at the top of this page) > Download Zip._


## Quick Start

These files can be used with many different agentic tools. For most users, we suggest Claude Cowork:

_The video from our CAS presentation can be found at https://www.youtube.com/watch?v=8JZz2zYrim0. It is an edited screen recording of the plugin setup and workflow in Claude Cowork. It does not have audio but will give you feel for the workflow._

1. Sign up for a Claude Pro account (~$20/month) at https://claude.ai/ and follow installation instructions at https://support.claude.com/en/articles/10065433-installing-claude-desktop
2. Open Claude Desktop and select "Cowork" on the top left (default is "Chat")
3. Select the "Sonnet" model on the bottom right below the chat widget. Opus will quickly hit limits. Haiku loses focus during long workflows.
4. Download `teamanalyst-Cowork.zip` from https://github.com/cas-team-analyst/team-analyst/blob/main/plugins/teamanalyst-Cowork.zip
5. Import the plugin: Customize > Personal plugins > + > Create plugin > Upload plugin > Browse files > Select `teamanalyst-Cowork.zip`
6. Prepare your data. At least one loss or claim count triangle is required. Optionally, you can also provide exposures, prior selections, and initial expected loss rate and/or frequency. You can also download a file from https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data to use.

Now you are ready to run the workflow! It may take 20-40 minutes to complete the workflow, so you may want to wait until you have about 40 minutes of free time.

If you want to just see what the output looks like, a sample workflow run with example output files is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run.

7. Open Claude Desktop in Cowork mode and click "New task"
8. Type `/reserving-analysis` (it will auto-complete and you can press enter to select it) in the chat box and press enter to get started!

Additional skills are also available:

- `/help` for orientation and help using the workflow
- `/reserving-analysis` for the full reserving workflow
- `/selection-logic` to inspect the LDF, tail, and ultimates selection strategy
- `/peer-review` perform AI peer review on a completed analysis

To go further:

See sections below on [How It Works](#how-it-works) and [Additional Resources](#additional-resources)

See the [Executive Summary](https://github.com/cas-team-analyst/team-analyst/tree/main/guides/EXECUTIVE_SUMMARY.md) for a more detailed overview. 

See [guides](https://github.com/cas-team-analyst/team-analyst/tree/main/guides) for more information for advanced users looking to build on this work.


# Make a Contribution

The CAS has generously funded this program. Now it is up to the community to expand and maintain it. Contributions via GitHub Issues and Pull Requests are welcome!

For an introduction to collaborating on GitHub, we recommend this tutorial on Git and GitHub: https://www.w3schools.com/git/default.asp


## Repository Layout

- `skills/` the TeamAnalyst skills, each with its own `SKILL.md` plus `assets/` and `scripts/`
- `skills/reserving-analysis/agents/` custom selection subagents
- `.claude-plugin/` Claude marketplace plugin and metadata
- `GEMINI.md` and `gemini-extension.json` Gemini extension context and manifest metadata
- `plugins/create_plugin_cowork.py` script to package skills into `plugins/teamanalyst-Cowork.zip` for upload into Cowork
- `plugins/` generated plugin artifacts for download
- `sample-data/` example input data and a sample run with representative outputs
- `guides/` supplementary notes for developers and advanced users and the [Executive Summary](https://github.com/cas-team-analyst/team-analyst/tree/main/guides/EXECUTIVE_SUMMARY.md)  providing more detail and context
- `AGENTS.md` and `CLAUDE.md` instructions for AI agents working on this repository (not the workflow itself)


## How It Works

For readers who want to understand how TeamAnalyst works under the hood, the following files and folders offer the most insight into the workflow design, decision logic, and practical implementation:

**Core Workflow Specifications**

- [Reserving Analysis Agent Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/SKILL.md) — Guardrails and context for getting the agent started on a reserving analysis. Establishes file handling principles, script execution rules, and communication standards. The actual step-by-step workflow is defined in PROGRESS.md.

- [Progress Tracker](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets/PROGRESS.md) — The detailed step-by-step workflow process that defines what happens at each stage of the analysis. This is the actual executable workflow specification that the agent follows, tracking decisions, data characteristics, and interim findings throughout the analysis.

- [Python Scripts](https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run/scripts) — Complete set of Python scripts generated during a workflow run. Shows how the workflow combines reusable script templates with dynamically generated analysis code. Includes data preparation, method calculations, Excel workbook generation, and technical review scripts.

- [Peer Review Agent Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/peer-review/SKILL.md) — Guardrails and context for conducting peer reviews. Defines advisory-only principles, ASOP grounding, and materiality-first review approach. The actual review output is captured in PEER_REVIEW.md.

**Selection Logic Frameworks**

The rules-based selector agent specifications show how actuarial judgment is encoded into structured decision frameworks that the AI interprets:

- [LDF Rules-Based Selector](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-chain-ladder-ldf-ai-rules-based.agent.md) — Decision framework for development factor selections, including 14 selection criteria and 10 diagnostic adjustment rules.

- [Tail Factor Rules-Based Selector](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-tail-factor-ai-rules-based.agent.md) — Framework for tail factor selections based on curve fitting, industry benchmarks, and maturity analysis.

- [Ultimates Rules-Based Selector](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-ultimates-ai-rules-based.agent.md) — Logic for blending Chain Ladder, Initial Expected, and Bornhuetter-Ferguson method results based on data maturity and credibility.

**Sample Workflow Run**

The sample-run folder contains a complete example of what TeamAnalyst produces from start to finish:

- [Draft Report](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/REPORT.md) — The draft analysis report generated by the workflow, demonstrating the documentation structure and narrative that TeamAnalyst produces.

- [Draft Analysis](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/Analysis.xlsx) — The draft analysis excel file generated by the workflow.

- [Replication Instructions](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/REPLICATE.md) — Complete reproducibility log documenting all input files, scripts run, customizations made, and manual selections applied. Enables a reviewer to reproduce the analysis results without AI assistance by following the documented steps exactly.

- [Peer Review Output](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/PEER_REVIEW.md) — The structured peer review evaluation of the completed analysis, showing how the tool identifies strengths, weaknesses, and areas requiring additional attention.

These files provide the clearest view into how TeamAnalyst works in practice and how the balance between deterministic processing and AI assistance is achieved.


# Additional Resources

For more detailed information on specific aspects of TeamAnalyst, refer to the following guides:

- **[AI Training & Data Privacy Policies](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/AI_TRAINING_POLICIES.md)** — Essential guidance on protecting sensitive actuarial data when using AI tools. Explains the critical difference between consumer and enterprise AI accounts, provider-specific policies (OpenAI, Anthropic, Google), and how to ensure your client data and proprietary methods are never used for model training.

- **[Customizing Selection Logic](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/MODIFY_SELECTION_GUIDELINES.md)** — Instructions for viewing and modifying the selection logic frameworks used in the workflow. Covers how to adjust thresholds, averaging windows, conservatism levels, decision hierarchies, and selection criteria for LDF selections, tail factors, and ultimates.

- **[Developer Notes](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/DEVELOPER_NOTES.md)** — Testing strategies and guidelines for developers working on TeamAnalyst skills. Includes git workflow recommendations, branch testing approaches, and links to helpful resources like Anthropic's guide to building skills for Claude Code.


## Installation for Other Agentic Tools

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

_Distribution strategy adapted from https://github.com/JuliusBrussee/caveman_
