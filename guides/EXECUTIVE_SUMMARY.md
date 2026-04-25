# TeamAnalyst: Executive Summary

## Table of Contents

- [Overview](#overview)
- [The Need](#the-need)
- [The Solution](#the-solution)
- [Why It Matters](#why-it-matters)
- [How the Tool Can Be Used](#how-the-tool-can-be-used)
- [Closing Note](#closing-note)
- [Appendix A: Lessons Learned](#appendix-a-lessons-learned)
- [Appendix B: Important Limitations](#appendix-b-important-limitations)
- [Appendix C: Additional Resources](#appendix-c-additional-resources)
- [Appendix D: Exploring the Project in Detail](#appendix-d-exploring-the-project-in-detail)

## Overview

TeamAnalyst is a proof-of-concept research project funded by the Casualty Actuarial Society (CAS) to show how modern AI assistants can support actuarial work. It packages a guided workflow, reusable scripts, and structured review steps into a format that can run inside several agentic AI tools.

The project is designed to help CAS members understand what an agentic actuarial workflow can look like in practice. Rather than asking a user to piece together prompts, code, and review steps from scratch, TeamAnalyst provides an organized starting point for preparing data, running selected reserving methods, making documented selections, assembling a draft analysis, and performing structured review.

## The Need

Many actuaries are interested in AI, but there is still a gap between general curiosity and practical adoption. Most professionals do not need another abstract demonstration of what AI might do. They need an example that is concrete, relevant to actuarial work, ready to use, and structured enough to learn from safely.

Reserve analysis is a useful setting for that example because it combines data preparation, repeatable calculations, professional judgment, documentation, and review. It is also a domain where users need transparency and reproducibility. A useful AI-enabled workflow therefore has to do more than generate text. It must help users organize work, preserve logic, support review, and leave behind steps that another actuary can follow.

TeamAnalyst addresses that need by giving CAS members a working example of how AI can assist with actuarial analysis without treating AI as a black box or a replacement for expertise. It is intended to help users understand both the promise and the practical constraints of applying agentic tools to professional work.

## The Solution

TeamAnalyst combines guided instructions, prebuilt Python scripts, standardized working documents, and focused subagents into one bundle that can be easily installed into a number of agentic tools (Claude CoWork, Claude Code, Cursor, Codex, etc.). The core workflow walks a user through a simplified reserving analysis from raw triangle data to a draft report. Along the way, the tool balances deterministic processing with AI assistance.

That balance is central to the design. TeamAnalyst uses AI where flexibility and judgment are valuable, such as interpreting incoming data layouts, suggesting baseline selections, answering questions, and performing peer-style review. It uses predefined scripts where consistency, speed, and repeatability matter more, such as producing diagnostics, running standard reserving calculations, generating Excel workbooks, and performing technical review checks.

This design helps reduce cost and runtime, improves consistency across runs, and leaves behind a workflow that can be reviewed or repeated later by humans. The output is not positioned as a final actuarial work product. Instead, it is a transparent, teachable, and modifiable starting point that shows how human judgment and AI assistance can work together.

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

## Why It Matters

TeamAnalyst turns a broad conversation about AI into something concrete, inspectable, and useful. It gives CAS members a realistic example of how AI can support actuarial work without pretending that professional judgment, accountability, or review no longer matter.

It also shows an approach to AI adoption that is likely to be more durable than prompt-only experimentation. By combining reusable scripts, structured markdown files, explicit review steps, and targeted AI assistance, the project demonstrates how to build workflows that are more transparent, token-efficient, and reproducible than ad hoc chat interactions.

For the CAS, this creates a strong educational asset. It highlights the potential of modern AI tools, introduces members to the structure of a modern agentic project, and gives them a practical jumping-off point for further experimentation. It also helps frame future research by showing what works well today, what still requires human oversight, and where additional development could expand the value of this approach.

## How the Tool Can Be Used

TeamAnalyst is meant to be used as a guided starting point rather than a finished production system. A typical user experience is straightforward.

First, the user installs the bundle into a supported AI environment. For most users, Claude CoWork is the most approachable path. For more technical users, the same content can also be used with Agent Skills-compatible environments such as GitHub Copilot, Claude Code, Cursor, Windsurf, Cline, and Gemini CLI. Installation instructions are available at https://github.com/cas-team-analyst/team-analyst. 

To test the tool quickly, users can provide one of three sample workbooks to the agent. Sample input data is available at https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data.

Once installed, the tool itself will guide the user through setup, data exploration, data intake, calculations, selections, review, and draft reporting. The experience is conversational, but the work is anchored by project files that document progress, replication steps, and reporting language.

The user can also branch into supporting capabilities when needed. The bundle includes:

- A help skill for orientation and onboarding
- A selection-logic skill for understanding the built-in decision framework
- A peer-review skill for reviewing completed analysis output against applicable best practices and guidance from ASOPs

For more instructions on getting started, see https://github.com/cas-team-analyst/team-analyst. 

In practical terms, this means TeamAnalyst can be used in several ways: as a learning aid for actuaries who want to understand agentic workflows, as a demonstration of AI-assisted reserving, as a reusable template for internal experimentation, or as a base that technical users can adapt to their own methods and preferences.

## Closing Note

The TeamAnalyst Research Team hopes this tool serves you well in your exploration of AI-assisted actuarial workflows. We welcome your feedback, suggestions, and contributions. If you encounter issues, have ideas for improvements, or would like to contribute to the project, please visit our GitHub repository at https://github.com/cas-team-analyst/team-analyst. Issues and pull requests are always welcome.

We wish you success in your actuarial work and in discovering new ways to integrate AI assistance into your professional practice,

Sincerely,

The TeamAnalyst Research Team  
Bryce Chamberlain, Esther Becker, Ken Zesso, Jack Tarantino, and Chris McKenna

## Appendix A: Lessons Learned

Building TeamAnalyst required considerable trial and error. Many approaches that seemed promising initially proved ineffective in practice. This section documents the key lessons from that research process so others can avoid the same mistakes.

**The application-building trap.** When most technical professionals approach a problem like actuarial reserving analysis, the instinct is to build an app—a fixed user interface, hardcoded logic, and predetermined workflows. That approach has intuitive appeal: applications feel concrete, controllable, and professional. The TeamAnalyst project initially explored this path as well. But in practice, actuarial applications must handle countless edge cases: varying data formats, different triangle structures, client-specific methods, unique business rules, evolving standards, and one-off adjustments. The more cases you accommodate, the more complex the codebase becomes, and the harder it is to modify. Eventually, the system becomes rigid precisely where users need flexibility. Attempts to build a traditional application framework for this workflow consistently ran into these limitations.

**The agentic framework detour.** The research also explored using agentic Python frameworks such as LangChain's DeepAgents and retrieval-augmented generation (RAG) systems. These approaches seemed promising because they are purpose-built for AI workflows and offer abstractions designed for agent orchestration. However, they introduced problems of their own. First, these frameworks lag behind the tools built by major AI companies. Features, performance improvements, and model updates appear in platforms like Claude CoWork, GitHub Copilot, and Gemini CLI months before third-party frameworks catch up. Second, these frameworks still require writing code rather than natural language specifications, which defeats one of the key goals: making the workflow accessible to actuaries who are not professional developers. Third, enterprise platforms built by major AI companies offer stronger security features, audit trails, and compliance controls than open-source frameworks typically provide. For actuarial work, where data sensitivity and professional accountability matter, this difference is significant.

**The spec-based alternative.** Instead of building an application or adopting an agentic framework, TeamAnalyst defines a specification—a set of structured instructions, scripts, and decision frameworks that an AI agent interprets and executes. This spec-based approach has several fundamental advantages. First, it can be modified by anyone who can write clear natural language. An actuary does not need to understand Python internals or UI frameworks to adjust the workflow. They can edit a markdown file, refine a prompt, or change a decision rule, and the agent adapts accordingly. This dramatically lowers the barrier to customization and makes the tool far more flexible than any fixed application could be. Second, specification-driven design stays compatible with future AI systems. As agent capabilities improve or new agent platforms emerge, the same specifications can be reused or adapted with minimal rework. The workflow is not locked to a specific tool version or proprietary framework.

**The need for balance.** However, this flexibility must be balanced with discipline. Early experiments with purely conversational AI workflows, where everything was generated on the fly, proved inefficient and unreliable. They consumed excessive tokens, produced inconsistent results, and were difficult to reproduce or review. The solution is to use predefined scripts wherever deterministic behavior is required—data preparation, standard calculations, technical checks, file generation—and reserve AI assistance for tasks that genuinely benefit from interpretation and judgment, such as understanding varied input formats, making selections, and performing reviews.

This balanced design is the key to making spec-based actuarial workflows practical. It preserves the flexibility and accessibility of natural language instructions while maintaining the efficiency, repeatability, and transparency that professional work requires. The lesson for future projects is clear: resist the urge to build a restrictive app when a well-structured specification can do more with less, adapt more easily, and remain viable as the underlying technology evolves.

## Appendix B: Important Limitations

TeamAnalyst is a proof of concept and should be presented that way. It is not intended to be a complete, error-free, or production-approved actuarial system. The CAS does not guarantee the accuracy of the output, and users should not rely on the generated material as a final actuarial work product without appropriate professional review.

The current scope is intentionally narrow. The example workflow focuses on a simplified reserving analysis using triangle-based inputs and a limited set of reserving methods. That focus is a feature, not a flaw: it keeps the tool understandable, teachable, and easier to evaluate while still demonstrating the broader potential of agentic AI in actuarial practice.

## Appendix C: Additional Resources

For more detailed information on specific aspects of TeamAnalyst, refer to the following guides:

- **[AI Training & Data Privacy Policies](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/AI_TRAINING_POLICIES.md)** — Essential guidance on protecting sensitive actuarial data when using AI tools. Explains the critical difference between consumer and enterprise AI accounts, provider-specific policies (OpenAI, Anthropic, Google), and how to ensure your client data and proprietary methods are never used for model training.

- **[Customizing Selection Logic](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/MODIFY_SELECTION_GUIDELINES.md)** — Instructions for viewing and modifying the selection logic frameworks used in the workflow. Covers how to adjust thresholds, averaging windows, conservatism levels, decision hierarchies, and selection criteria for LDF selections, tail factors, and ultimates.

- **[Developer Notes](https://github.com/cas-team-analyst/team-analyst/blob/main/guides/DEVELOPER_NOTES.md)** — Testing strategies and guidelines for developers working on TeamAnalyst skills. Includes git workflow recommendations, branch testing approaches, and links to helpful resources like Anthropic's guide to building skills for Claude Code.

## Appendix D: Exploring the Project in Detail

For readers who want to understand how TeamAnalyst works under the hood, the following files and folders offer the most insight into the workflow design, decision logic, and practical implementation:

**Core Workflow Specifications**

- [Reserving Analysis Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/reserving-analysis/SKILL.md) — Guardrails and context for getting the agent started on a reserving analysis. Establishes file handling principles, script execution rules, and communication standards. The actual step-by-step workflow is defined in PROGRESS.md.

- [Peer Review Skill](https://github.com/cas-team-analyst/team-analyst/blob/main/skills/peer-review/SKILL.md) — Guardrails and context for conducting peer reviews. Defines advisory-only principles, ASOP grounding, and materiality-first review approach. The actual review output is captured in PEER_REVIEW.md.

**Selection Logic Examples**

The rules-based selection files show how actuarial judgment is encoded into structured decision frameworks that the AI interprets. These are actual outputs from a completed workflow run:

- [Chain Ladder Rules-Based Selections - Incurred Loss](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/selections/chainladder-ai-rules-based-incurred_loss.json) — Example of how development factor selections are documented with supporting rationale, pattern analysis, and decision hierarchy.

- [Chain Ladder Rules-Based Selections - Paid Loss](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/selections/chainladder-ai-rules-based-paid_loss.json) — Shows selection logic for paid loss development patterns.

- [Chain Ladder Rules-Based Selections - Reported Count](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/selections/chainladder-ai-rules-based-reported_count.json) — Demonstrates selection framework applied to claim count development.

**Python Implementation**

- [Python Scripts Folder](https://github.com/cas-team-analyst/team-analyst/tree/main/sample-data/sample-run/scripts) — Complete set of Python scripts generated during a workflow run. Shows how the workflow combines reusable script templates with dynamically generated analysis code. Includes data preparation, method calculations, Excel workbook generation, and technical review scripts.

**Sample Workflow Run**

The sample-run folder contains a complete example of what TeamAnalyst produces from start to finish:

- [Progress Document](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/PROGRESS.md) — The detailed step-by-step workflow process that defines what happens at each stage of the analysis. This is the actual executable workflow specification that the agent follows, tracking decisions, data characteristics, and interim findings throughout the analysis.

- [Replication Instructions](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/REPLICATE.md) — Complete reproducibility log documenting all input files, scripts run, customizations made, and manual selections applied. Enables a reviewer to reproduce the analysis results without AI assistance by following the documented steps exactly.

- [Final Report](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/REPORT.md) — The draft analysis report generated by the workflow, demonstrating the documentation structure and narrative that TeamAnalyst produces.

- [Peer Review Output](https://github.com/cas-team-analyst/team-analyst/blob/main/sample-data/sample-run/PEER_REVIEW.md) — The structured peer review evaluation of the completed analysis, showing how the tool identifies strengths, weaknesses, and areas requiring additional attention.

These files provide the clearest view into how TeamAnalyst works in practice and how the balance between deterministic processing and AI assistance is achieved.
