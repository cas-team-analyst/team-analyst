## Customizing Selection Logic

The TeamAnalyst plugin uses customizable selection logic frameworks for LDF selections, tail factors, and ultimates. These frameworks live in the selector agent files:

| File | Purpose |
|---|---|
| [`selector-chain-ladder-ldf-ai-framework.agent.md`](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-chain-ladder-ldf-ai-framework.agent.md) | LDF and tail cutoff point selection framework (criteria + diagnostic adjustment rules) |
| [`selector-tail-curve-ai-framework.agent.md`](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-tail-curve-ai-framework.agent.md) | Tail curve selection framework |
| [`selector-ultimates-ai-framework.agent.md`](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/agents/selector-ultimates-ai-framework.agent.md) | Ultimates selection framework |

The easiest way to modify these is the ask the Claude agent directly to modify the selection logic using natural language. The agent can view and modify these files. 

Alternatively, you can edit the files directly and then re-compile and install the skill. This method is more technical and is out of scope for this document.

After modifying, run `python create_import_zips.py` to rebuild the packaged artifacts.

_More information can be found in the [developer notes](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/DEVELOPER_NOTES.md) and the individual agent files linked above._
