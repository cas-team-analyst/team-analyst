
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
