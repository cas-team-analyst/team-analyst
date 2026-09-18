# Notes for Developers Working on Skills

_This is a working document. It is slim now but will be expanded by the community as we identify new helpful content._

## General Notes

Much of the information you need will be in `README.md`. This document gives a few more tips for technically-minded developers who would like to work with this code.

- Skill files are saved at `skills/` within the project directory.

- Agent skills for working with this codebase (not specifically related to reserving) are provided at `.agents/skills/` and `.claude/skills/`.

- After modifying a skill, run `python create_import_zips.py` to rebuild the packaged artifacts.

- Follow best practices from [Anthropic's Guide to Skills for Claude Code](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en)


## Troubleshooting

- If something unexpected is happening, you may have some sneaky instructions that go against what you actually want the agent to do. Review the instructions for something that might be causing the issue. Ask the agent "did you receive instructions to do ..." and it can help you give it better instructions for next time. Continue tuning instructions until you get the desired behavior. 

- Turn off memory (different agents have different settings for this) to prevent prior sessions from impacting new interactions.


