# TeamAnalyst

**[Quick Start](#quick-start)** | **[Contribute](#make-a-contribution)** | **[Repository Layout](#repository-layout)** | **[How It Works](#how-it-works)** | **[Resources](#additional-resources)** | **[Install](#installation-for-other-agentic-tools)**

TeamAnalyst is the result of a research initiative by the Casualty Actuarial Society (CAS) to explore the use of agentic tools in actuarial work. It targets a specific workflow: development of actuarial reserve ultimate estimates. 

The project is a collection of Markdown files and Python scripts that agentic tools can use to run the workflow, organized to match the expected organization of these files for different tools.

> **DISCLAIMER**: TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

_These files can be downloaded via `git clone` or Code (green button at the top of this page) > Download Zip._


## Quick Start

These files can be used with many different agentic tools. For most users, we suggest **Claude Chat** on the web. It is the easiest way to get started and does not require a paid account or software install.

_Instructions for other tools can be found [here](#installation-for-other-agentic-tools)._

1. Sign up for a Claude account at https://claude.ai/
   - **Important Note**: While this approach works on Claude's free tier, free/consumer accounts don't get the same data privacy protections as paid accounts — by default your conversations may be used to train models unless you turn that off in Settings > Privacy. See the [AI Training & Data Privacy Policies guide](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/AI_TRAINING_POLICIES.md) before uploading any real client data.

2. In the chat box, select **Cowork**, **Sonnet**, and **Medium**. Cowork will enable the use of subagents (ignore this if the option is not available, Chat will also work). Sonnet is preferred to Opus (quickly hits limits) and Haiku (can lose focus during long workflows).

3. Download the skill zip files from https://github.com/cas-team-analyst/team-analyst/tree/main/skills-import — `reserving-analysis.zip`, `peer-review.zip`.

4. In Claude Chat, go to Customize > Skills > Add > Upload a skill, and upload each zip.

5. Prepare your data. At least one loss or claim count triangle is required. Optionally, you can also provide exposures, prior selections, and initial expected loss rate and/or frequency. You can also download a file from https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data to use.

Now you are ready to run the workflow! It may take some time to complete, so you may want to review the sample outputs first. If you want to just see what the output looks like, a sample workflow run with example output files is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run.

6. Start a new chat, upload your data files, and type `/reserving-analysis` in the chat box and press enter to get started!

**Alternative: Claude Cowork (Desktop App)**

If you have a paid Claude Pro account and prefer using the desktop app's Cowork mode (which can call subagents and work on files on your computer), you can use the Cowork plugin instead:

_These instructions are for Windows only. Mac/Linux is probably similar, if you find different steps please submit a PR to get them added._

1. Follow installation instructions for Claude Desktop at https://support.claude.com/en/articles/10065433-installing-claude-desktop
2. Enable long paths in Windows (Cowork sometimes creates these long paths): Settings > System > Advanced > Enable Long Paths (slide to "On").
3. Open Claude Desktop and select **Cowork** on the top left. (You may need to enable virtualization if prompted and restart).
4. Select the **Sonnet** model with **Medium** effort on the bottom right.
5. Download `teamanalyst-cowork.zip` from https://github.com/cas-team-analyst/team-analyst/blob/main/plugins/teamanalyst-cowork.zip
6. Import the plugin: Customize > Personal plugins > + > Create plugin > Upload plugin > Browse files > Select `teamanalyst-cowork.zip`
7. Click "New task", upload your data, and type `/reserving-analysis` to start.

> **Note:** Use one approach or the other across all of Claude (desktop/app/web) to avoid confusing the agent with multiple versions of the same skill. If you upload the skills to Claude Chat, do not upload the plugin to Cowork, and vice versa. Note that Chat cannot call subagents, so framework and open-ended selections will not be run as fully independent sub-tasks.

These skills are available:

- `/reserving-analysis` for the full reserving workflow
- `/peer-review` perform AI peer review on a completed analysis

The LDF, tail, and ultimates selection strategy is documented directly in the selector agent files under [`skills/reserving-analysis/agents/`](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis/agents) (see [How It Works](#how-it-works)).

To go further:

See sections below on [How It Works](#how-it-works) and [Additional Resources](#additional-resources)

See the [Executive Summary](https://github.com/cas-team-analyst/team-analyst/tree/main/guides/EXECUTIVE_SUMMARY.md) for a more detailed overview. 

See [guides](https://github.com/cas-team-analyst/team-analyst/tree/main/guides) for more information for advanced users looking to build on this work.


# Make a Contribution

The CAS has generously funded this initial version. Now it is up to the community to expand it. 

Contributions are welcome via [Issues](https://github.com/cas-team-analyst/team-analyst/issues) (the community may both add and resolve them) and [Pull Requests](https://github.com/cas-team-analyst/team-analyst/pulls).

For an introduction to collaborating on GitHub, we recommend this tutorial on Git and GitHub: https://www.w3schools.com/git/default.asp.

Please keep in mind that our team is small and is not compensated for any work we do to support the project post release.
- Do not submit a Pull Request until you are familiar with the project and have spent time using it, have carefully considered the implications of your change, and have thoroughly tested the change. See [How It Works](#how-it-works) and developer documentation in the [guides](https://github.com/cas-team-analyst/team-analyst/tree/main/guides) folder.
- Do not submit an issue until you have tried fixes and confirmed it is an issue with this repository and not your agentic tooling. 
- Please be patient with us, we will respond when the time becomes available to do so.

This is to protect our time and limit it to reviewing high quality contributions, and to protect the users of this repository from unexpected bugs. 


## Repository Layout

- `README.md` this document, with introduction info and links for more detail.
- `skills/` the TeamAnalyst skills, each with its own `SKILL.md` plus `assets/` and `scripts/`
- `skills/reserving-analysis/agents/` custom selection subagents
- `.claude-plugin/` Claude marketplace plugin and metadata
- `GEMINI.md` and `gemini-extension.json` Gemini extension context and manifest metadata
- `plugins/create_plugin_zip_cowork.py` script to package skills into `plugins/teamanalyst-cowork.zip` for upload into Cowork
- `plugins/` generated plugin artifacts for download
- `skills-import/create_skills_zips.py` script to package each skill folder into its own zip (e.g. `skills-import/reserving-analysis.zip`) for upload as individual Skills in Claude Chat
- `skills-import/` generated per-skill zip artifacts for download
- `sample-data/` example input data and a sample run with representative outputs
- `guides/` supplementary notes for developers and advanced users and the [Executive Summary](https://github.com/cas-team-analyst/team-analyst/tree/main/guides/EXECUTIVE_SUMMARY.md)  providing more detail and context
- `AGENTS.md, CLAUDE.md, .claude/, .agents/` instructions for AI agents working on this repository (not the workflow itself)


## How It Works

For readers who want to understand how TeamAnalyst works under the hood, the following files and folders offer the most insight into the workflow design, decision logic, and practical implementation:

**Core Workflow**

These files control the workflow and provide resources the agent can use to complete it.

- [Main Agent Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/SKILL.md) Instructions the agent receives to kick off (or resume) the workflow.

- [Progress Tracker](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets/PROGRESS.md) Detailed workflow with checkboxes to save progress.

- [Python Scripts](https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run/reserving-analysis/scripts) Pre-written scripts the agent will use to keep results consistent and avoid using tokens to write static scripts. 

- [Peer Review Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/peer-review/SKILL.md) Instructions the agent receives when asked to perform peer review.

- [Other Assets](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets) Templates for replication, report, user interface forms and messages, etc.

**Selection Logic**

Instructions that framework (as opposed to open-ended) selector subagents use to make selections.

- [LDFs & Tail Cutoff](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-chain-ladder-ldf-ai-framework.agent.md)
- [Tail Fit Curve](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-tail-curve-ai-framework.agent.md)
- [Ultimates](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-ultimates-ai-framework.agent.md)

**Sample Workflow Run**

Explore these files to understand what the final output looks like.

- [Analysis](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/reserving-analysis/Analysis.xlsx) Complete traditional actuarial analysis. _Note: Values are hard-coded. Including formulas was out of scope for this research project._

- [Report](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/reserving-analysis/REPORT.md) Draft of a complete actuarial report following relevant ASOPs. This uses the related [template](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/assets/REPORT.md). _Note: Some of the sections are missing because they are not covered by this workflow yet._

- [Peer Review Output](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/peer-review/PEER_REVIEW_REPORT.md) Report created by the peer review agent skill.

- [Replication](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/reserving-analysis/REPLICATE.md) Instructions to replicate the study and results without the use of AI. Useful for auditing or moving the workflow to a non-AI platform.


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

**Installing without typing commands.** The table above uses typed commands. You can install for the same tools by clicking through the app's own screens instead, if you prefer not to use a command line.

**Claude (Chat or Desktop)** is the only tool where TeamAnalyst installs as an actual point-and-click Skill upload, using the [Quick Start](#quick-start) steps at the top of this page. This is the recommended path for non-technical users. No command line is required.

The same two things you did in Quick Start (sign up for an account, then load the skill files) also work in these other tools. Steps below follow that same order: get an account, then upload.

**Microsoft Copilot**

1. Sign up for or sign in to Microsoft 365 Copilot with a work or school account. Microsoft's skill-upload feature ("Agent Builder") is in preview and currently limited to organizations enrolled in the Microsoft Frontier Program, so a personal Microsoft account will not work. Ask your IT admin to enroll if needed: [Explore AI Early Access in Microsoft 365](https://www.microsoft.com/en-us/microsoft-365-copilot/frontier-program).
2. Download the skill zip files from https://github.com/cas-team-analyst/team-analyst/tree/main/skills-import — `reserving-analysis.zip`, `peer-review.zip`. This is the same download used in [Quick Start](#quick-start).
3. Go to m365.cloud.microsoft, select **Agents & Skills**, then **New agent**.
4. In the **Configure** tab, expand **Skills**, select **Add**, and upload `reserving-analysis.zip` (repeat for `peer-review.zip`). Upload the whole zip file, not just the `SKILL.md` file inside it.
5. Prepare your data as in Quick Start step 5, then start a new chat and type `/reserving-analysis`.

Full instructions: [Add custom skills to your declarative agent in Agent Builder](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills).

**ChatGPT**

As of September 2026, OpenAI is retiring custom GPTs in favor of Plugins and Projects, and new custom GPTs can only be created on Business, Enterprise, or Edu workspace accounts, not on personal plans (Free, Go, Plus, Pro). Check OpenAI's current guidance before relying on this path: [GPTs in ChatGPT](https://help.openai.com/en/articles/8554407-gpts-in-chatgpt).

Where it is still available, ChatGPT does not accept a skill zip file directly, so you paste in the instructions and upload the reference files separately:

1. Sign up for or sign in to a ChatGPT Business, Enterprise, or Edu workspace account.
2. Open the [`reserving-analysis` skill folder](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis) on GitHub and open `SKILL.md`.
3. Go to chatgpt.com/gpts, select **Create**, and open the **Configure** tab.
4. Copy the full text of `SKILL.md` into the instructions box.
5. Upload the files under [`skills/reserving-analysis/assets/`](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis/assets) as knowledge files.
6. Prepare your data as in Quick Start step 5, then start a chat with your new GPT and ask it to begin the reserving analysis workflow.

Full instructions: [Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts).

**Google Gemini**

Gemini does not accept a skill zip file directly either, so the steps are the same paste-and-upload pattern as ChatGPT. This works on both personal Google accounts (including the free tier) and Google Workspace accounts.

1. Sign up for or sign in to a Google account at gemini.google.com.
2. Open the [`reserving-analysis` skill folder](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis) on GitHub and open `SKILL.md`.
3. Select **Explore Gems**, then **New Gem**, and give it a name.
4. Copy the full text of `SKILL.md` into the instructions box.
5. In the **Knowledge** section, select **Add files** and upload the files under [`skills/reserving-analysis/assets/`](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis/assets) (up to 10 files, 100 MB each), then save the Gem.
6. Prepare your data as in Quick Start step 5, then start a chat with your new Gem and ask it to begin the reserving analysis workflow.

Full instructions: [Tips for creating custom Gems](https://support.google.com/gemini/answer/15235603?hl=en).

For ChatGPT and Gemini, expect reduced functionality. Pasting in instructions and reference files is not the same as a real skill upload, and neither tool can run the project's Python scripts the way Claude or Microsoft Copilot's Agent Builder can, so calculations may be less consistent and the workflow may need more manual guidance from you. Treat results from these two paths as a rough starting point, not a validated run of the workflow.

# Helpful Commands

Update skill and plugin .zip files. 

```bash
python plugins/create_plugin_zip_cowork.py; python skills-import/create_skills_zips.py
```
