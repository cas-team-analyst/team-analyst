# TeamAnalyst

> **DISCLAIMER**: TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

**[Quick Start](#quick-start)** | **[Contribute](#make-a-contribution)** | **[Repository Layout](#repository-layout)** | **[How It Works](#how-it-works)** | **[Resources](#additional-resources)** | **[Install](#installation-for-other-agentic-tools)**

TeamAnalyst is the result of a research initiative by the Casualty Actuarial Society’s (CAS) Reserves Working Group to explore the use of agentic tools in actuarial work. It targets a specific workflow: development of actuarial reserve ultimate estimates. 

The main deliverable is a zipped collection of files following the [agent skills](https://agentskills.io/) specification for easy loading into common agentic tools. It is NOT a production-ready system, but is instead a proof of concept for exploring the use of agentic tools in actuarial workflows. All you need to use it is an email address and an internet connection! Sample data is provided for easy testing and demonstration purposes.

See [Quick Start](#quick-start) below to get started!

This repository also contains the source files, plus other supporting files that are useful for maintaining and customizing TeamAnalyst. It is an evolving project, so check back often and don't hesitate to add a [GitHub Issue](https://github.com/cas-team-analyst/team-analyst/issues) if you'd like to see a change.

_These files can be downloaded via [`git clone`](https://www.w3schools.com/git/git_clone.asp) or Code (green button at the top of this page) > Download Zip._


## Quick Start

These files can be used with many different agentic tools. For most users, we suggest **Claude Chat** on the web. It is the easiest way to get started and does not require a paid account or software install.

_Instructions for other tools can be found [here](#installation-for-other-agentic-tools)._

1. Sign up for a Claude account at https://claude.ai/
   - **Important Note**: While this approach works on Claude's free tier, free/consumer accounts don't get the same data privacy protections as paid accounts — by default your conversations may be used to train models unless you turn that off in Settings > Privacy. See the [AI Training & Data Privacy Policies guide](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/AI_TRAINING_POLICIES.md) before uploading any real client data.

2. In the chat box, select **Cowork**, **Sonnet**, and **Medium**. Cowork will enable the use of subagents (ignore this if the option is not available on free accounts, Chat will also work). Sonnet is preferred to Opus (quickly hits limits) and Haiku (can lose focus during long workflows).

3. Download the skill zip files here: [`reserving-analysis.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/reserving-analysis.zip) and [`peer-review.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/peer-review.zip).

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
5. Download [`teamanalyst-plugin-cowork.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/teamanalyst-plugin-cowork.zip)
6. Import the plugin: Customize > Personal plugins > + > Create plugin > Upload plugin > Browse files > Select `teamanalyst-plugin-cowork.zip` (downloaded in step 5)
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
- `create_import_zips.py` script that builds every zip in `import/`: the Cowork plugin, the plugin for other tools, and one zip per skill
- `import/` generated zip artifacts for download (`teamanalyst-plugin-cowork.zip`, `teamanalyst-plugin-other.zip`, `reserving-analysis.zip`, `peer-review.zip`)
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

Jump to:

- **[Anthropic](#anthropic):** [Claude Code](#claude-code) | [Claude Cowork](#claude-cowork) | [Claude (Chat or Desktop)](#claude-chat-or-desktop)
- **[OpenAI](#openai):** [Codex](#codex) | [ChatGPT](#chatgpt)
- **[Google](#google):** [Gemini CLI](#gemini-cli) | [Google Gemini](#google-gemini) | [Antigravity CLI](#antigravity-cli) | [Antigravity IDE](#antigravity-ide-gui)
- **[Microsoft](#microsoft):** [Microsoft Copilot](#microsoft-copilot)
- **[GitHub](#github):** [GitHub Copilot CLI](#github-copilot-cli) | [VS Code (GitHub Copilot)](#vs-code-github-copilot) | [GitHub Copilot skills only](#github-copilot-skills-only)
- **[Other tools](#other-tools):** [Cursor](#cursor) | [Any other tool](#any-other-tool)

Two kinds of install are listed. A **plugin install** pulls the whole TeamAnalyst bundle from this GitHub repo in one step. A **skills install** copies the skill folders into your tool with `npx skills`. Use a plugin install where one is listed, and the skills install otherwise. Where a tool supports both, the commands below are shown twice: **global** (available in every project, the simplest choice for most users) and **project** (only the folder you run it in, so it does not affect your other projects). Point-and-click installs in desktop and web apps are global to your account. Plugin installs marked _docs-based_ follow the vendor's documentation and have not yet been tested by the TeamAnalyst team, so tell us if a step differs on your version.

Tools are grouped by provider. Each tool section starts with the command to install where one exists, followed by point-and-click steps where the tool offers them. Uninstall (for tools installed with `npx skills`): run `npx skills remove reserving-analysis; npx skills remove peer-review` (add `-g` to each if you installed globally)

_Distribution strategy adapted from https://github.com/JuliusBrussee/caveman_

## Anthropic

### Claude Code

```bash
# Global (user): available in every project
claude plugin marketplace add cas-team-analyst/team-analyst && claude plugin install team-analyst@team-analyst

# Project: only the project in the current folder (run from the project root, shared with your team through .claude/settings.json)
claude plugin marketplace add cas-team-analyst/team-analyst --scope project && claude plugin install team-analyst@team-analyst --scope project
```

Start Claude Code and type `/reserving-analysis` to begin. To update later, run `claude plugin marketplace update team-analyst`. See [Claude Code plugin docs](https://code.claude.com/docs/en/plugin-marketplaces).

### Claude Cowork

*There is no terminal command to install the skill into this tool.* This installs the TeamAnalyst plugin from this repo. It works in Cowork on the web (claude.ai) or in the Claude Desktop app, and needs a paid Claude account.

1. Download [`teamanalyst-plugin-cowork.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/teamanalyst-plugin-cowork.zip) (open the link and select the download button).
2. **Desktop app only:** install Claude Desktop from https://support.claude.com/en/articles/10065433-installing-claude-desktop. On Windows, also enable long paths (Settings > System > Advanced > Enable Long Paths, slide to "On"). You may need to enable virtualization if prompted and restart.
3. Open Claude Desktop, or go to https://claude.ai/, and select **Cowork** on the top left.
4. Import the plugin: Customize > Personal plugins > + > Create plugin > Upload plugin > Browse files, then select `teamanalyst-plugin-cowork.zip`.
5. To use it, select **New task**, upload your data, and type `/reserving-analysis`.

Use one Claude install path only. If you install this plugin in Cowork, do not also upload the skill zips to Claude Chat, and vice versa.

### Claude (Chat or Desktop)

*There is no terminal command to install the skill into this tool.* This is a point-and-click Skill upload and works on the free tier.

1. Sign in at https://claude.ai/ (or open Claude Desktop).
2. Download the skill zip files here: [`reserving-analysis.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/reserving-analysis.zip) and [`peer-review.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/peer-review.zip) (open each link and select the download button).
3. In Claude Chat, go to Customize > Skills > Add > Upload a skill, and upload each zip, one at a time. Upload the whole zip, not files from inside it.
4. To use it, start a new chat, upload your data, and type `/reserving-analysis`.

Use one Claude install path only. If you upload these skills to Chat, do not also install the Cowork plugin, and vice versa.

## OpenAI

### Codex

```bash
# Project: installs into .agents/skills/ in the current folder only
npx skills add cas-team-analyst/team-analyst -a codex

# Global: available in every project
npx skills add cas-team-analyst/team-analyst -a codex -g
```

Without `-g`, the skills install into `.agents/skills/` in your current project, which Codex scans on startup. In Codex, type `$reserving-analysis` to start the workflow. See [Skills in Codex](https://learn.chatgpt.com/docs/build-skills) and the [`skills` CLI](https://github.com/vercel-labs/skills).

**Plugin install (_docs-based_).** Codex can also add this repo as a plugin marketplace:

```bash
# Global: Codex plugins install for your user account, not per project
codex plugin marketplace add cas-team-analyst/team-analyst
```

Then open `/plugins` inside Codex and install **team-analyst**. If Codex does not list it, use the skills install above, which is the tested path. See [Package your plugin](https://developers.openai.com/plugins/build/plugins).

### ChatGPT

*There is no terminal command to install the skill into this tool.*

As of September 2026, OpenAI is retiring custom GPTs in favor of Plugins and Projects, and new custom GPTs can only be created on Business, Enterprise, or Edu workspace accounts, not on personal plans (Free, Go, Plus, Pro). Check OpenAI's current guidance before relying on this path: [GPTs in ChatGPT](https://help.openai.com/en/articles/8554407-gpts-in-chatgpt).

Where it is still available, ChatGPT does not accept a skill zip file directly, so you paste in the instructions and upload the reference files separately:

1. Sign up for or sign in to a ChatGPT Business, Enterprise, or Edu workspace account.
2. Open the [`reserving-analysis` skill folder](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis) on GitHub and open `SKILL.md`.
3. Go to chatgpt.com/gpts, select **Create**, and open the **Configure** tab.
4. Copy the full text of `SKILL.md` into the instructions box.
5. Upload the files under [`skills/reserving-analysis/assets/`](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis/assets) as knowledge files.
6. Prepare your data as in Quick Start step 5, then start a chat with your new GPT and ask it to begin the reserving analysis workflow.

Full instructions: [Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts).

**Plugins (later).** ChatGPT uses Codex-style plugins. TeamAnalyst is not available as a ChatGPT plugin yet, so use the paste-and-upload steps above.

## Google

### Gemini CLI

```bash
# Global: Gemini CLI extensions install for your user account, not per project
gemini extensions install https://github.com/cas-team-analyst/team-analyst
```

Google retired Gemini CLI for free and individual Google AI Pro and Ultra users on June 18, 2026. It still works for Gemini Code Assist Standard and Enterprise licenses, or with a paid API key. Everyone else should use [Antigravity CLI](#antigravity-cli) below. See Google's [announcement](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) and the [Gemini CLI extensions guide](https://geminicli.com/docs/extensions/).

### Google Gemini

*There is no terminal command to install the skill into this tool.* Gemini does not accept a skill zip file directly either, so the steps are the same paste-and-upload pattern as ChatGPT. This works on both personal Google accounts (including the free tier) and Google Workspace accounts.

1. Sign up for or sign in to a Google account at gemini.google.com.
2. Open the [`reserving-analysis` skill folder](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis) on GitHub and open `SKILL.md`.
3. Select **Explore Gems**, then **New Gem**, and give it a name.
4. Copy the full text of `SKILL.md` into the instructions box.
5. In the **Knowledge** section, select **Add files** and upload the files under [`skills/reserving-analysis/assets/`](https://github.com/cas-team-analyst/team-analyst/tree/main/skills/reserving-analysis/assets) (up to 10 files, 100 MB each), then save the Gem.
6. Prepare your data as in Quick Start step 5, then start a chat with your new Gem and ask it to begin the reserving analysis workflow.

Full instructions: [Tips for creating custom Gems](https://support.google.com/gemini/answer/15235603?hl=en).

### Antigravity CLI

```bash
# Global: agy plugin install has no project option
agy plugin install https://github.com/cas-team-analyst/team-analyst

# Project: skills only, installs into .agents/skills/ in the current folder
npx skills add cas-team-analyst/team-analyst -a antigravity
```

The first command installs TeamAnalyst as a plugin. Start a new `agy` session, then type `/skills` to confirm the TeamAnalyst skills are listed and `/reserving-analysis` to start the workflow. The `npx skills` command installs only the skills, into the directory where you ran it. To make skills available in every project without the plugin, add `-g` to it or copy the folders into `~/.gemini/antigravity-cli/skills/`. Get Antigravity CLI from [antigravity.google/download](https://antigravity.google/download). See [Plugins](https://antigravity.google/docs/plugins?tab=cli) and [Agent Skills](https://antigravity.google/docs/skills/) in the Antigravity docs.

### Antigravity IDE (GUI)

This covers the Antigravity 2.0 desktop app and the IDE. The `npx skills` command above also works here, since both read `.agents/skills/` in your project. To install without a command line:

1. Download the repo from https://github.com/cas-team-analyst/team-analyst (select **Code**, then **Download ZIP**) and unzip it.
2. Copy every folder inside the repo's `skills/` folder (`reserving-analysis`, `peer-review`, and the rest) into one of these locations:
   - **One project only:** `.agents/skills/` inside your project folder. Create it if it does not exist.
   - **All projects:** `.gemini/config/skills/` inside your user folder (on Windows, `C:\Users\<you>\.gemini\config\skills`).
3. Open the agent side panel and check **Customizations** to confirm `reserving-analysis` is listed. No restart is needed.
4. Prepare your data as in Quick Start step 5, then type `/reserving-analysis` in the prompt panel.

**Plugin install (_docs-based_).** To install the whole bundle as a plugin instead, download [`teamanalyst-plugin-other.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/teamanalyst-plugin-other.zip) and unzip it into a folder named `team-analyst` inside one of these locations, so that `plugin.json` sits directly in that folder:

- **One project only:** `.agents/plugins/` inside your project folder.
- **All projects:** `.gemini/config/plugins/` inside your user folder (on Windows, `C:\Users\<you>\.gemini\config\plugins`).

Then open **Customizations** in the agent side panel to confirm the plugin is listed. See [Plugins in Antigravity](https://antigravity.google/docs/plugins?tab=cli).

See [Agent Skills](https://antigravity.google/docs/skills/) and the [Authoring Google Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills) codelab.

## Microsoft

### Microsoft Copilot

*There is no terminal command to install the skill into this tool.*

1. Sign up for or sign in to Microsoft 365 Copilot with a work or school account. Microsoft's skill-upload feature ("Agent Builder") is in preview and currently limited to organizations enrolled in the Microsoft Frontier Program, so a personal Microsoft account will not work. Ask your IT admin to enroll if needed: [Explore AI Early Access in Microsoft 365](https://www.microsoft.com/en-us/microsoft-365-copilot/frontier-program).
2. Download the skill zip files here: [`reserving-analysis.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/reserving-analysis.zip) and [`peer-review.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/peer-review.zip). This is the same download used in [Quick Start](#quick-start).
3. Go to m365.cloud.microsoft, select **Agents & Skills**, then **New agent**.
4. In the **Configure** tab, expand **Skills**, select **Add**, and upload [`reserving-analysis.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/reserving-analysis.zip) (repeat for [`peer-review.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/peer-review.zip)). Upload the whole zip file, not just the `SKILL.md` file inside it.
5. Prepare your data as in Quick Start step 5, then start a new chat and type `/reserving-analysis`.

Full instructions: [Add custom skills to your declarative agent in Agent Builder](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills).

Microsoft 365 Copilot has no plugin format for skills, so the per-skill zips above are the only route. Limits from Microsoft: up to 8 skills per agent, 50 MB per zip, `SKILL.md` at the zip root, and instructions under 20,000 characters.

## GitHub

### GitHub Copilot CLI

```bash
# Global: Copilot CLI plugins install for your user account, not per project
copilot plugin install cas-team-analyst/team-analyst

# Global, alternative: add the repo as a marketplace first, then install from it
copilot plugin marketplace add cas-team-analyst/team-analyst && copilot plugin install team-analyst@team-analyst

# Project: skills only, installs into .agents/skills/ in the current folder
npx skills add cas-team-analyst/team-analyst -a github-copilot
```

Check `copilot plugin list` to confirm it installed. Copilot CLI copies plugin contents at install time, so reinstall to pick up updates. This route is _docs-based_. See [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference) and [Plugin marketplaces for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace).

### VS Code (GitHub Copilot)

*There is no terminal command to install the skill into this tool.* This route is _docs-based_.

1. Open the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P on Mac) and run **Chat: Install Plugin From Source**.
2. Paste `https://github.com/cas-team-analyst/team-analyst` and confirm.
3. Open Copilot Chat in agent mode and type `/reserving-analysis`.

To add the repo as a marketplace instead, add it to the `chat.plugins.marketplaces` setting. See [Agent plugins in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-plugins).

### GitHub Copilot (skills only)

```bash
# Project: installs into .agents/skills/ in the current folder only
npx skills add cas-team-analyst/team-analyst -a github-copilot

# Global: available in every project
npx skills add cas-team-analyst/team-analyst -a github-copilot -g
```

Without `-g`, the skills install into `.agents/skills/` in your project, which GitHub Copilot reads in agent mode in VS Code and JetBrains, in Copilot CLI, and in the Copilot cloud agent. See [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).

## Other tools

### Cursor

```bash
# Project: installs into .agents/skills/ in the current folder only
npx skills add cas-team-analyst/team-analyst -a cursor

# Global: available in every project
npx skills add cas-team-analyst/team-analyst -a cursor -g
```

Without `-g`, the skills install into `.agents/skills/` in your project. In Cursor, open **Customize**, then **Skills**, to confirm they are listed, and type `/` in Agent chat to pick `reserving-analysis`. See [Agent Skills in Cursor](https://cursor.com/docs/context/skills).

**Plugin install (_docs-based_).** Cursor's documentation does not describe installing a plugin from a GitHub link for individual accounts. Choose one of these, both of which use this repo:

- **Local plugin:** download [`teamanalyst-plugin-other.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/teamanalyst-plugin-other.zip), unzip it into `~/.cursor/plugins/local/team-analyst` (so `plugin.json` sits directly in that folder), restart Cursor, and look under **Customize**.
- **Team plans:** an admin opens the Dashboard, selects **Plugins**, then **Import from Repo**, and enters `https://github.com/cas-team-analyst/team-analyst`.

See [Cursor plugins](https://cursor.com/docs/reference/plugins).

### Any other tool

```bash
# Project: installs into the current folder only
npx skills add cas-team-analyst/team-analyst

# Global: available in every project
npx skills add cas-team-analyst/team-analyst -g
```

The [`skills` CLI](https://github.com/vercel-labs/skills) lists every supported agent and where it installs skills.

### Manual folder install

For any tool that reads [Agent Plugins](https://agent-plugins.org/specification) (a folder with a root `plugin.json` and a `skills/` folder), download [`teamanalyst-plugin-other.zip`](https://github.com/cas-team-analyst/team-analyst/blob/main/import/teamanalyst-plugin-other.zip), unzip it, and copy the folder into that tool's plugins folder. Plugins are folders, so unzip first rather than importing the zip itself.

For ChatGPT and Gemini, expect reduced functionality. Pasting in instructions and reference files is not the same as a real skill upload, and neither tool can run the project's Python scripts the way Claude or Microsoft Copilot's Agent Builder can, so calculations may be less consistent and the workflow may need more manual guidance from you. Treat results from these two paths as a rough starting point, not a validated run of the workflow.

# Helpful Commands

Update skill and plugin .zip files. This also builds `import/teamanalyst-plugin-other.zip` (root `plugin.json` plus `skills/`) for manual folder installs, and fails if the plugin versions differ across `plugin.json`, `.claude-plugin/plugin.json` and `gemini-extension.json`.

```bash
python create_import_zips.py
```
