# TeamAnalyst

## Project Overview

TeamAnalyst is the result of a research initiative by the Casualty Actuarial Society (CAS) to explore using agentic tools in actuarial work. It targets a specific workflow: development of actuarial reserve ultimate estimates. 

The project is a collection of Markdown files and Python scripts that agentic tools can use to run the workflow, organized to match the expected organization of these files for different tools.

> **DISCLAIMER**: This is a proof of concept research initiative and is not meant for real-world actuarial work. 

## Quick Start

These files can be used with many different agentic tools. For most users, we suggest Claude CoWork:

1. Sign up for a Claude Pro account (~$20/month) at https://claude.ai/ and follow installation instructions at https://support.claude.com/en/articles/10065433-installing-claude-desktop.
2. Open Claude Desktop and select "CoWork" on the top left (default is "Chat").
2. Download the `team-analyst-plugin.zip` from [LOCATION_TBD].
3. Import the plugin: Customize > Personal plugins > + > Create plugin > Upload plugin > Browse files > Select `team-analyst-plugin.zip`.
4. Click "New task".
5. Type "/reserving-analysis" (it will auto-complete and you can press enter to select it) in the chat box and press enter to get started!

## Advanced 

See `guides/` for more information for advanced users looking to build on this work. 

Contributions via GitHub Issues and Pull Requests are welcome!

## Other Tools

TeamAnalyst can also be imported into other tools:

### Claude Code

1. Sign up for a Claude account at https://claude.ai/ and follow installation instructions at https://code.claude.com/docs/en/setup.
2. Clone (download) this repository into a new folder (Learn Git at https://www.w3schools.com/git/default.asp) or download it from [this link](https://storage.googleapis.com/data-downloads-by-bryce/team-analyst.zip) and unzip it. 
3. Open the folder in your favorite terminal. For example: 
  - Unzip the file. 
  - Click into the "team-analyst" folder, you should see another "team-analyst" folder. If you don't, go back.
  - Right-click the "team-analyst" folder > Open in Terminal
  - Run this command: `claude "Let's go!"`
  - To run without having to confirm all the agent's operations, use `claude --dangerously-skip-permissions "Let's go!"`

The agent will run you through Chain Ladder selections. That's as far as we've gotten.