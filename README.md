# TeamAnalyst

**[Quick Start](#quick-start)** | **[Contribute](#make-a-contribution)** | **[Repository Layout](#repository-layout)** | **[How It Works](#how-it-works)** | **[Resources](#additional-resources)** | **[Install](#installation-for-other-agentic-tools)**

TeamAnalyst is the result of a research initiative by the Casualty Actuarial Society (CAS) to explore the use of agentic tools in actuarial work. It targets a specific workflow: development of actuarial reserve ultimate estimates. 

The project is a collection of Markdown files and Python scripts that agentic tools can use to run the workflow, organized to match the expected organization of these files for different tools.

> **DISCLAIMER**: TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

_These files can be downloaded via `git clone` or Code (green button at the top of this page) > Download Zip._


## Quick Start

These files can be used with many different agentic tools. For most users, we suggest Claude Cowork. 

_Instructions for other tools can be found [here](#installation-for-other-agentic-tools)._

_The video from our CAS presentation can be found at https://www.youtube.com/watch?v=8JZz2zYrim0. It is an edited screen recording of the plugin setup and workflow in Claude Cowork. It does not have audio but will give you a feel for the workflow._

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

The CAS has generously funded this program. Now it is up to the community to expand and maintain it. 

Contributions are welcome via [Issues](https://github.com/cas-team-analyst/team-analyst/issues) (the community may both add and resolve them) and [Pull Requests](https://github.com/cas-team-analyst/team-analyst/pulls).

For an introduction to collaborating on GitHub, we recommend this tutorial on Git and GitHub: https://www.w3schools.com/git/default.asp.

Please keep in mind that our team is small and is not compensated for any work we do to support the project post release.
- Do not submit a Pull Request until you are familiar with the project (see [How It Works](#how-it-works)) and have spent time using it, have carefully considered the implications of your change, and have thoroughly tested the change. 
- Do not submit an issue until you have tried fixes and confirmed it is an issue with this repository and not your agentic tooling. 
- Please be patient with us, we will respond when the time becomes available to do so.

This is to protect our time and limit it to reviewing high quality contributions, and to protect the users of this repository from unexpected bugs. 


## Repository Layout

- `README.md` this document, with introduction info and links for more detail.
- `skills/` the TeamAnalyst skills, each with its own `SKILL.md` plus `assets/` and `scripts/`
- `skills/reserving-analysis/agents/` custom selection subagents
- `.claude-plugin/` Claude marketplace plugin and metadata
- `GEMINI.md` and `gemini-extension.json` Gemini extension context and manifest metadata
- `plugins/create_plugin_cowork.py` script to package skills into `plugins/teamanalyst-Cowork.zip` for upload into Cowork
- `plugins/` generated plugin artifacts for download
- `sample-data/` example input data and a sample run with representative outputs
- `guides/` supplementary notes for developers and advanced users and the [Executive Summary](https://github.com/cas-team-analyst/team-analyst/tree/main/guides/EXECUTIVE_SUMMARY.md)  providing more detail and context
- `AGENTS.md, CLAUDE.md, .claude/, .agents/` instructions for AI agents working on this repository (not the workflow itself)
-  folders contain skills for AI 


## How It Works

For readers who want to understand how TeamAnalyst works under the hood, the following files and folders offer the most insight into the workflow design, decision logic, and practical implementation:

**Core Workflow**

These files control the workflow and provide resources the agent can use to complete it.

- [Main Agent Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/SKILL.md) Instructions the agent receives to kick off (or resume) the workflow.

- [Progress Tracker](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets/PROGRESS.md) Detailed workflow with checkboxes to save progress.

- [Python Scripts](https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run/scripts) Pre-written scripts the agent will use to keep results consistent and avoid using tokens to write static scripts. 

- [Peer Review Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/peer-review/SKILL.md) Instructions the agent receives when asked to perform peer review.

- [Other Assets](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets) Templates for replication, report, user interface forms and messages, etc.

**Selection Logic**

Instructions that rules-based (as opposed to open-ended) selector subagents use to make selections.

- [LDFs & Tail Cutoff](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-chain-ladder-ldf-ai-rules-based.agent.md)
- [Tail Fit Curve](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-tail-factor-ai-rules-based.agent.md)
- [Ultimates](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-ultimates-ai-rules-based.agent.md)

**Sample Workflow Run**

Explore these files to understand what the final output looks like.

- [Analysis](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/Analysis.xlsx) Complete traditional actuarial analysis. _Note: Values are hard-coded. Including formulas was out of scope for this research project._

- [Report](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/REPORT.md) Draft of a complete actuarial report following relevant ASOPs. This uses the related [template](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets/REPORT.md). _Note: Some of the sections are missing because they are not covered by this workflow yet._

- [Peer Review Output](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/PEER_REVIEW.md) Report created by the peer review agent skill.

- [Replication](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/REPLICATE.md) Instructions to replicate the study and results without the use of AI. Useful for auditing or moving the workflow to a non-AI platform.


# Additional Resources

For more detailed information on specific aspects of TeamAnalyst, refer to the following guides:

- **[AI Training & Data Privacy Policies](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/AI_TRAINING_POLICIES.md)** Answers the question "will AI companies use my data to train their models?"

- **[Customizing Selection Logic](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/MODIFY_SELECTION_GUIDELINES.md)** Guide on modifying the selection logic to your preference.

- **[Developer Notes](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/DEVELOPER_NOTES.md)** Guidelines for developers who would like to modify this code base.


# Installation for Other Agentic Tools

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
