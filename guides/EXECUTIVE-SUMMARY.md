# Executive Summary

## Overview

TeamAnalyst is a proof-of-concept tool created by the Casualty Actuarial Society (CAS) to show how modern AI assistants can support actuarial reserve analysis. It packages a guided workflow, reusable scripts, and structured review steps into a format that can run inside several agent-based AI tools, including Claude CoWork and Agent Skills-compatible environments such as GitHub Copilot, Cursor, Claude Code, and similar applications.

The project is designed to help CAS members see what an agentic actuarial workflow can look like in practice. Rather than asking a user to piece together prompts, code, and review steps from scratch, TeamAnalyst provides an organized starting point for preparing data, running selected reserving methods, making documented selections, assembling a draft analysis, and performing structured review.

## The Need

Many actuaries are interested in AI, but there is still a gap between general curiosity and practical adoption. Most professionals do not need another abstract demonstration of what AI might do. They need an example that is concrete, relevant to actuarial work, and structured enough to learn from safely.

Reserve analysis is a useful setting for that example because it combines data preparation, repeatable calculations, professional judgment, documentation, and review. It is also a domain where users need transparency and reproducibility. A useful AI-enabled workflow therefore has to do more than generate text. It must help users organize work, preserve logic, support review, and leave behind steps that another actuary can follow.

TeamAnalyst addresses that need by giving CAS members a working example of how AI can assist with actuarial analysis without treating AI as a black box. It is intended to help users understand both the promise and the practical constraints of applying agentic tools to professional work.

## The Solution

TeamAnalyst combines guided instructions, prebuilt Python scripts, standardized working documents, and focused subagents into one bundle that can be easily installed into a number of agentic tools (Claude CoWork, Claude Code, Cursor, Codex, etc.). The core workflow walks a user through a simplified reserving analysis from raw triangle data to a draft report. Along the way, the tool balances deterministic processing with AI assistance.

That balance is central to the design. TeamAnalyst uses AI where flexibility and judgment are valuable, such as interpreting incoming data layouts, assisting with development factor selections, selecting ultimates, answering questions, and performing peer-style review. It uses predefined scripts where consistency, speed, and repeatability matter more, such as producing diagnostics, running standard reserving calculations, generating Excel workbooks, and performing technical review checks.

This design helps reduce cost and runtime, improves consistency across runs, and leaves behind a workflow that can be reviewed or repeated later. The output is not positioned as a final actuarial work product. Instead, it is a transparent, teachable, and modifiable starting point that shows how human judgment and AI assistance can work together.

## What TeamAnalyst Can Do

In its current proof-of-concept form, TeamAnalyst can support a simplified reserve analysis workflow that includes the following:

- Reading triangle-style input data, even when the incoming format varies
- Preparing and enhancing data for analysis
- Producing diagnostics and supporting metrics used in reserve review
- Running three standard reserving approaches: Chain Ladder, Initial Expected, and Bornhuetter-Ferguson
- Assisting with pre-ultimate selections such as development factor choices
- Assisting with ultimate selections across methods
- Creating Excel workbooks that support review and selection decisions
- Assembling a simple draft reserving analysis package
- Performing a scripted technical review and an AI-assisted peer review
- Answering user questions about the analysis and workflow

The repository also includes orientation and reference materials so users can understand what the tool is doing, inspect the built-in selection logic, and modify the workflow if they want to build on it.

## How the Tool Can Be Used

TeamAnalyst is meant to be used as a guided starting point rather than a finished production system. A typical user experience is straightforward.

First, the user installs the bundle into a supported AI environment. For many users, Claude CoWork is the most approachable path. For more technical users, the same content can also be used with Agent Skills-compatible environments such as GitHub Copilot, Claude Code, Cursor, Windsurf, Cline, and Gemini CLI. Installation instructions are available at https://github.com/cas-team-analyst/team-analyst. 

To test the tool quickly, users can provide the project sample data to the agent. Sample input data is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data, and a sample workflow run with example output files is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run.

Once installed, the tool itself will guide the user through setup, data exploration, data intake, calculations, selections, review, and draft reporting. The experience is conversational, but the work is anchored by project files that document progress, replication steps, and reporting language.

The user can choose how much control to keep. The workflow supports more hands-on use, where the user reviews key decisions step by step, as well as more automated use, where the tool performs more of the routine work with fewer pauses.

The user can also branch into supporting capabilities when needed. The bundle includes:

- A help skill for orientation and onboarding
- A selection-logic skill for understanding the built-in decision framework
- A peer-review skill for reviewing completed analysis output against applicable best practices and guidance from ASOPs

The simplest way to describe use of TeamAnalyst is:

1. Install the TeamAnalyst bundle into a supported AI tool.
2. Start the reserving-analysis workflow.
3. Provide the analysis folder and input data (the sample data at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data can be used for testing).
4. If helpful, review the sample workflow run and output at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run to see the expected structure.
5. Follow the guided prompts as the tool prepares data, runs methods, and supports selections.
6. Review the generated analysis materials, technical checks, and peer review output.
7. Start a new session to run the peer-review.
8. Use the resulting files as a draft and learning aid, not as a final unchecked work product.

In practical terms, this means TeamAnalyst can be used in several ways: as a learning aid for actuaries who want to understand agentic workflows, as a demonstration of AI-assisted reserving, as a reusable template for internal experimentation, or as a base that technical users can adapt to their own methods and preferences.

## Why It Matters

TeamAnalyst matters because it turns a broad conversation about AI into something concrete, inspectable, and useful. It gives CAS members a realistic example of how AI can support actuarial work without pretending that professional judgment, accountability, or review no longer matter.

It also shows an approach to AI adoption that is likely to be more durable than prompt-only experimentation. By combining reusable scripts, structured markdown files, explicit review steps, and targeted AI assistance, the project demonstrates how to build workflows that are more transparent, token-efficient, and reproducible than ad hoc chat interactions.

For the CAS, this creates a strong promotional and educational asset. It highlights the potential of modern AI tools, introduces members to the structure of a modern agentic project, and gives them a practical jumping-off point for further experimentation. It also helps frame future research by showing what works well today, what still requires human oversight, and where additional development could expand the value of this approach.

## Lessons Learned

Building TeamAnalyst required considerable trial and error. Many approaches that seemed promising initially proved ineffective in practice. This section documents the key lessons from that research process so others can avoid the same mistakes.

**The application-building trap.** When most technical professionals approach a problem like actuarial reserving analysis, the instinct is to build an app—a fixed user interface, hardcoded logic, and predetermined workflows. That approach has intuitive appeal: applications feel concrete, controllable, and professional. The TeamAnalyst project initially explored this path as well. But in practice, actuarial applications must handle countless edge cases: varying data formats, different triangle structures, client-specific methods, unique business rules, evolving standards, and one-off adjustments. The more cases you accommodate, the more complex the codebase becomes, and the harder it is to modify. Eventually, the system becomes rigid precisely where users need flexibility. Attempts to build a traditional application framework for this workflow consistently ran into these limitations.

**The agentic framework detour.** The research also explored using agentic Python frameworks such as LangChain's DeepAgents and retrieval-augmented generation (RAG) systems. These approaches seemed promising because they are purpose-built for AI workflows and offer abstractions designed for agent orchestration. However, they introduced problems of their own. First, these frameworks lag behind the tools built by major AI companies. Features, performance improvements, and model updates appear in platforms like Claude CoWork, GitHub Copilot, and Gemini CLI months before third-party frameworks catch up. Second, these frameworks still require writing code rather than natural language specifications, which defeats one of the key goals: making the workflow accessible to actuaries who are not professional developers. Third, enterprise platforms built by major AI companies offer stronger security features, audit trails, and compliance controls than open-source frameworks typically provide. For actuarial work, where data sensitivity and professional accountability matter, this difference is significant.

**The spec-based alternative.** Instead of building an application or adopting an agentic framework, TeamAnalyst defines a specification—a set of structured instructions, scripts, and decision frameworks that an AI agent interprets and executes. This spec-based approach has several fundamental advantages. First, it can be modified by anyone who can write clear natural language. An actuary does not need to understand Python internals or UI frameworks to adjust the workflow. They can edit a markdown file, refine a prompt, or change a decision rule, and the agent adapts accordingly. This dramatically lowers the barrier to customization and makes the tool far more flexible than any fixed application could be. Second, specification-driven design stays compatible with future AI systems. As agent capabilities improve or new agent platforms emerge, the same specifications can be reused or adapted with minimal rework. The workflow is not locked to a specific tool version or proprietary framework.

**The need for balance.** However, this flexibility must be balanced with discipline. Early experiments with purely conversational AI workflows, where everything was generated on the fly, proved inefficient and unreliable. They consumed excessive tokens, produced inconsistent results, and were difficult to reproduce or review. The solution is to use predefined scripts wherever deterministic behavior is required—data preparation, standard calculations, technical checks, file generation—and reserve AI assistance for tasks that genuinely benefit from interpretation and judgment, such as understanding varied input formats, making selections, and performing reviews.

This balanced design is the key to making spec-based actuarial workflows practical. It preserves the flexibility and accessibility of natural language instructions while maintaining the efficiency, repeatability, and transparency that professional work requires. The lesson for future projects is clear: resist the urge to build a restrictive app when a well-structured specification can do more with less, adapt more easily, and remain viable as the underlying technology evolves.

## Important Limitations

TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

The current scope is intentionally narrow. The example workflow focuses on a simplified reserving analysis using triangle-based inputs and a limited set of reserving methods. That focus is a feature, not a flaw: it keeps the tool understandable, teachable, and easier to evaluate while still demonstrating the broader potential of agentic AI in actuarial practice.
