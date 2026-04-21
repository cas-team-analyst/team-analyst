# TeamAnalyst for Claude Code

## Project Overview
This project supports the development of actuarial reserve ultimate estimates using systematic methodology and thorough documentation, with the help of an AI coding agent.


## Prerequisites

- Sign up for a Claude account at https://claude.ai/
- 

After installation, set up your identity in Git:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
  ```


## Quick Start

**Claude CoWork**

1. Sign up for a Claude Pro account (~$20/month) at https://claude.ai/ and follow installation instructions at https://support.claude.com/en/articles/10065433-installing-claude-desktop.
2. Download the `team-analyst-plugin.zip` from https://github.com/cas-team-analyst/claude-code/blob/plugin/.claude-plugin/team-analyst-plugin.zip.
3. Import the plugin into CoWork by following these instructions with the downloaded zip: [TBD]
4. Create a folder to work in.
5. Start a new CoWork sessions with your new folder as the Working Directory.
6. Type /reserve-analysis and press enter to get started.

**Claude Code**

1. Sign up for a Claude account at https://claude.ai/ and follow installation instructions at https://code.claude.com/docs/en/setup.
2. Clone (download) this repository into a new folder (Learn Git at https://www.w3schools.com/git/default.asp) or download it from [this link](https://storage.googleapis.com/data-downloads-by-bryce/team-analyst.zip) and unzip it. 
3. Open the folder in your favorite terminal. For example: 
  - Unzip the file. 
  - Click into the "team-analyst" folder, you should see another "team-analyst" folder. If you don't, go back.
  - Right-click the "team-analyst" folder > Open in Terminal
  - Run this command: `claude "Let's go!"`
  - To run without having to confirm all the agent's operations, use `claude --dangerously-skip-permissions "Let's go!"`

The agent will run you through Chain Ladder selections. That's as far as we've gotten.

# Demo Folders

There are a few demo checkpoints in the `demos/` folder meant for jumping ahead to demo or test specific steps. 

- demo1-data: Only has the test data at `raw-data/`. Use to test starting from the beginning.
- demo2-selections-ldfs: Data intake and processing is complete. Use to test AI selections for Chain Ladder LDFs.
- demo3-selections-ultimates: For testing AI selections for Ultimates.
- demo4-complete: Current workflow is completed, showing all output in the latest version.

# Notes for Developers Working on Skills

## Testing strategy

You can use a branch to run a test and then easily switch back to the baseline repo.

```bash
git branch -D test
git checkout -B test
claude
```

Then make notes in a notepad for things you want to change. 

When done testing
```bash
git checkout main
```

And then make and commit your baseline to the baseline tool state. 

## Guidelines

- If something unexpected is happening, first check to make sure the skill isn't making it happen. Avoid creating new instructions that override prior instructions, which can happen easily if the skill is complex. 

## Helpful Links

- [Anthropic's Guide to Skills for Claude Code](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en)

## Customizing Selection Logic

The TeamAnalyst plugin uses customizable selection logic frameworks for LDF selections, tail factors, and ultimates. You can view and modify these frameworks to match your actuarial judgment.

**To view selection logic:** Ask Claude "Show me the selection logic" or read the selector agent files in `.claude/agents/`

**To modify selection logic:** See the complete [Selection Logic Adjustment Guide](.claude/skills/selection-logic/assets/selection-logic-adjustment-guide.md) which covers:
- How to adjust thresholds, averaging windows, and conservatism levels
- How to reorder the decision hierarchy
- How to add or remove selection criteria
- Testing and validating your changes
