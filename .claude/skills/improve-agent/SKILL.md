---
name: improve-agent
description: Guide for improving GitHub Copilot Agent performance through skills, custom instructions, AGENTS.md, or other configuration. Use this when asked to improve agent behavior, create/update skills, modify custom instructions, update AGENTS.md, or customize GitHub Copilot performance in repositories.
---

# Agent Improvement Guide

## Quick Reference

**What this skill covers:** Improving GitHub Copilot Agent performance through Skills, Custom Instructions, AGENTS.md, and path-specific instructions.

**Instruction types:**
- **Skills** = On-demand, specialized (`.github/skills/NAME/SKILL.md`)
- **Custom Instructions** = Always-in-context, general (`.github/copilot-instructions.md`)
- **Path-Specific** = Context for specific files/dirs (`.github/instructions/NAME.instructions.md`)
- **AGENTS.md** = Directory-based precedence (nearest `AGENTS.md` wins)

**Quick decision:** Need it for 80%+ of tasks? → Custom Instructions. Specific workflows only? → Skill. Different rules per directory? → Path-specific or AGENTS.md. → [Decision guide](#skills-vs-custom-instructions-decision-guide)

**Key principles:**
- **Less is more**: Agents overindex on first 50 lines. Put navigation and key decisions first, details below with hash links.
- **Context is costly**: Only add what Copilot doesn't already know. Challenge each piece: "Does this justify its token cost?"
- **Description triggers loading**: The skill `description` field determines when Copilot loads it. Be specific about WHEN to use.
- **Iterate, don't perfect**: Start minimal, add details based on real usage patterns. → [Iteration guide](#testing-and-iterating)
- **Match freedom to fragility**: Text for flexible tasks, specific scripts for fragile operations. → [Details](#degrees-of-freedom)

**Setup guides:**
- [Custom Instructions](#custom-instructions-setup)
- [Path-Specific Instructions](#path-specific-instructions)
- [AGENTS.md](#agent-instructions-agentsmd)
- [Skill creation process](#skill-creation-process)

**Writing best practices:**
- [Writing effective skills](#writing-effective-skills)
- [Writing effective instructions](#writing-effective-instructions)
- [What NOT to include](#what-not-to-include-in-instructions)
- [Testing approach](#testing-and-iterating)
- [Troubleshooting](#troubleshooting)

**Naming:** lowercase-with-hyphens, under 64 chars, verb-led (e.g., `rotate-pdf`, `debug-github-actions`)

---

## Detailed Guidance

### Agent Improvement Methods

**Skills provide:**
- Specialized workflows for specific domains
- Tool integrations for file formats or APIs
- Domain expertise (schemas, business logic)
- Procedural knowledge and best practices

**Custom instructions provide:**
- Repository-wide coding standards and conventions
- Build, test, and run commands
- Project structure and architecture
- Always-available foundational knowledge

**AGENTS.md provides:**
- Directory-based instruction precedence
- Module-specific agent behavior
- Cross-agent compatibility

**Path-specific instructions provide:**
- File type or directory-specific rules
- Context-dependent coding standards
- Conditional guidance based on file location

### Writing Effective Skills

**Critical principles:**
1. **First 50 lines** = Navigation and key decisions. Copilot reads this first, jumps to sections as needed.
2. **Description field** = How Copilot decides to load your skill. Be specific about WHEN to use it.
3. **Start minimal** = First draft should be concise. Add details based on real usage patterns.
4. **Hash links everywhere** = Quick Reference must link to ALL major sections. Copilot uses them to navigate.

**Quick Reference template:**
```markdown
## Quick Reference

**What this does:** One clear sentence.

**When to use:** Specific triggers (file types, tasks, user requests).

**Navigation:**
- [Setup/Installation](#setup)
- [Common patterns](#patterns)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
```

**SKILL.md structure:**
- YAML frontmatter: `name`, `description` (required), `license` (optional)
- Quick Reference section with navigation
- Detailed sections below with clear headings

Detailed sections go below the Quick Reference with proper `###` or `####` headings.

### Skills vs Custom Instructions: Decision Guide

**The 80% rule:** If you need it for 80%+ of tasks → Custom Instructions. Otherwise → Skill.

#### Custom Instructions (`.github/copilot-instructions.md`)

**Use when:**
- Info is relevant to almost every task
- Guidance applies broadly across all files

**Examples:** Build/test commands, project structure, coding standards, common gotchas

**Benefits:** ✅ Always in context ✅ No loading decision needed ✅ Foundational knowledge

#### Agent Skills (`.github/skills/`)

**Use when:**
- Info is relevant only to specific tasks/domains
- Specialized workflows that would clutter context if always loaded

**Examples:** Debugging GitHub Actions, working with Parquet/PDF files, DuckDB queries, testing patterns

**Benefits:** ✅ Loaded on-demand ✅ Detailed without context cost ✅ Keeps context lean

#### Path-Specific Instructions (`.github/instructions/*.instructions.md`)

**Use when:**
- Different parts of codebase have different rules
- File types or directories need unique guidance

**Examples:** API routes error handling, test file standards, frontend vs backend patterns

**Benefits:** ✅ Auto-applied by glob pattern ✅ Combined with repo-wide instructions

#### Agent Instructions (AGENTS.md)

**Use when:**
- Want directory-based precedence (nearest file wins)
- Different modules need unique patterns
- Need portability across AI agents

**Examples:** Monorepo apps, frontend/backend split, per-package instructions

**Benefits:** ✅ Hierarchical precedence ✅ Cross-agent compatibility ✅ Maps to project structure

**Quick comparison:**

| Need | Custom Instructions | Skill | Path-Specific | AGENTS.md |
|------|--------------------|---------|--------------------|--------|
| "How do I run tests?" | ✅ | ❌ | ❌ | ❌ |
| "Debug GitHub Actions?" | ❌ | ✅ | ❌ | ❌ |
| "API routes need special handling" | ❌ | ❌ | ✅ | ✅ |
| "Frontend vs backend patterns" | ❌ | ❌ | ✅ | ✅ |

### Custom Instructions Setup

#### Repository-Wide Instructions

```bash
mkdir .github
New-Item .github/copilot-instructions.md
```

**What to include:**
1. Build commands (install, dev, test, lint) with exact steps
2. Project structure overview
3. Coding standards and naming conventions
4. Known issues and workarounds

**Example:**
```markdown
# Build Commands
- Install: `npm install`
- Dev: `npm run dev`
- Test: `npm test`

# Project Structure
- `app/` - Next.js pages
- `__tests__/` - Jest tests

# Standards
- TypeScript strict mode
- 80%+ test coverage
```

**Pro tip:** Ask Copilot to [generate it for you](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions#asking-copilot-coding-agent-to-generate-a-copilot-instructionsmd-file).

**Takes effect:** Immediately on save. No restart needed.

**More guidance:** [Writing effective instructions](#writing-effective-instructions) | [What NOT to include](#what-not-to-include-in-instructions) | [Examples](https://github.com/github/awesome-copilot/tree/main/instructions)

#### Path-Specific Instructions

**When to use:** Instructions that apply only to specific files, directories, or file types (not the entire repository).

**Use path-specific instructions when:**
- Different parts of your codebase have different rules (e.g., API routes vs frontend components)
- Specific directories require unique validation or patterns
- You want to avoid cluttering repository-wide instructions with niche guidance

**Examples:**
- API routes must follow specific error handling patterns
- Test files have different coding standards than production code
- Database migration files require special naming conventions
- Legacy code sections have different rules than new code

Create `.github/instructions/NAME.instructions.md` (where NAME describes the purpose):

```bash
mkdir .github/instructions
New-Item .github/instructions/api-routes.instructions.md
```

**Add YAML frontmatter with glob pattern:**
```yaml
---
applyTo: "app/api/**/*.ts"
---

API routes must:
- Use Next.js App Router patterns
- Include proper error handling
- Return typed responses
```

**Glob pattern examples:**
- `**/*.ts` - All TypeScript files
- `app/components/**/*.tsx` - All components
- `__tests__/**/*.test.tsx` - All test files
- `**/database/**/*` - All files in any database directory

**Exclude from specific agents (optional):**
```yaml
---
applyTo: "**/*.py"
excludeAgent: "code-review"  # Only for coding-agent, not code-review
---
```

**When combined:** If a file matches both repository-wide and path-specific instructions, both sets are combined and used together.

#### Writing Effective Instructions

**Length limits:** Keep instruction files under ~1,000 lines maximum. Beyond this, Copilot may overlook some instructions due to context limits.

**Structure best practices:**
- **Use distinct headings** to separate different topics
- **Use bullet points** for easy scanning and reference
- **Write short, imperative directives** rather than long narrative paragraphs
- **Provide concrete examples** showing both correct and incorrect patterns

**Example - Before (vague):**
```markdown
When you're reviewing code, it would be good if you could try to look for
situations where developers might have accidentally left in sensitive
information like passwords or API keys, and also check for security issues.
```

**Example - After (clear):**
```markdown
## Security Critical Issues

- Check for hardcoded secrets, API keys, or credentials
- Look for SQL injection and XSS vulnerabilities
- Verify proper input validation and sanitization
```

**Show correct and incorrect examples:**
```markdown
## Naming Conventions

Use descriptive, intention-revealing names.

```javascript
// Avoid
const d = new Date();
const x = users.filter(u => u.active);

// Prefer
const currentDate = new Date();
const activeUsers = users.filter(user => user.isActive);
```
```

**Understanding Copilot's limitations:**
- **Non-deterministic behavior** - Copilot may not follow every instruction perfectly every time
- **Context limits** - Very long instruction files may result in some instructions being overlooked
- **Specificity matters** - Clear, specific instructions work better than vague directives

#### What NOT to Include in Instructions

Copilot currently **does not support** instructions that attempt to:

**Change user experience or formatting:**
- ❌ "Use bold text for critical issues"
- ❌ "Change the format of review comments"
- ❌ "Add emoji to comments"

**Modify pull request overview comments:**
- ❌ "Include a summary of security issues in the PR overview"
- ❌ "Add a testing checklist to the overview comment"

**Change Copilot's core function:**
- ❌ "Block a PR from merging unless all comments are addressed"
- ❌ "Generate a changelog entry for every PR"

**Follow external links:**
- ❌ "Review this code according to https://example.com/standards"
- ✅ **Workaround:** Copy the relevant content directly into your instruction file

**Vague quality improvements:**
- ❌ "Be more accurate"
- ❌ "Don't miss any issues"
- ❌ "Be consistent in your feedback"

These types of instructions add noise without improving effectiveness.

#### Testing and Iterating

**Start small:** Begin with 10-20 specific instructions addressing your most common needs, then iterate based on results.

**Test with real work:**
1. Save your instruction files
2. Use Copilot on real tasks or PRs
3. Observe which instructions it follows effectively
4. Note instructions that are consistently missed or misinterpreted

**Iterate based on results:**
1. Identify a pattern that Copilot could handle better
2. Add a specific instruction for that pattern
3. Test with new work
4. Refine the instruction based on results

This iterative approach helps you understand what works and keeps files focused.

#### Troubleshooting

**Issue: Instructions are ignored**

Possible causes:
- Instruction file is too long (over 1,000 lines)
- Instructions are vague or ambiguous
- Instructions conflict with each other

Solutions:
- Shorten the file by removing less important instructions
- Rewrite vague instructions to be more specific and actionable
- Review for conflicting instructions and prioritize the most important ones

**Issue: Language-specific rules applied to wrong files**

Possible causes:
- Missing or incorrect `applyTo` frontmatter
- Rules in repository-wide file instead of path-specific file

Solutions:
- Add `applyTo` frontmatter to path-specific instruction files
- Move language-specific rules from `copilot-instructions.md` to appropriate `*.instructions.md` files

**Issue: Inconsistent behavior across sessions**

Possible causes:
- Instructions are too numerous
- Instructions lack specificity
- Natural variability in AI responses

Solutions:
- Focus on your highest-priority instructions
- Add concrete examples to clarify intent
- Accept that some variability is normal for AI systems

**Additional resources:**
- See [example custom instructions](https://github.com/github/awesome-copilot/tree/main/instructions) in the Awesome GitHub Copilot repository for inspiration
- Read [Configure custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions) for technical details

#### Agent Instructions (AGENTS.md)

**When to use:** Instructions specifically for AI agents, with hierarchical directory-based precedence.

**Use AGENTS.md when:**
- You want instructions that follow your directory structure (nearest file takes precedence)
- Different subdirectories need different agent behaviors
- You're building a multi-module project where each module has unique patterns
- You want agent-specific instructions separate from general custom instructions

**How AGENTS.md works:**
- Place `AGENTS.md` files anywhere in your repository
- When Copilot is working on a file, it uses the **nearest** `AGENTS.md` in the directory tree
- Closer `AGENTS.md` files override instructions from parent directories

**Example structure:**
```
project-root/
├── AGENTS.md                    # General project-wide agent instructions
├── src/
│   ├── frontend/
│   │   ├── AGENTS.md           # Frontend-specific instructions (overrides root)
│   │   └── components/
│   └── backend/
│       ├── AGENTS.md           # Backend-specific instructions (overrides root)
│       └── api/
└── tests/
    └── AGENTS.md               # Test-specific instructions (overrides root)
```

**Use case example:**
```markdown
# Root AGENTS.md
Use TypeScript strict mode. Always write tests for new features.

# src/frontend/AGENTS.md
Frontend code must:
- Use React hooks, not class components
- Implement responsive design with Tailwind CSS
- Test with React Testing Library

# src/backend/AGENTS.md
Backend code must:
- Use Express.js patterns
- Validate all inputs with Zod
- Test with Supertest
```

When working on `src/frontend/App.tsx`, Copilot uses `src/frontend/AGENTS.md` (not root).  
When working on `src/backend/routes.ts`, Copilot uses `src/backend/AGENTS.md` (not root).

**Alternative: Agent-specific files in root**

Instead of multiple `AGENTS.md` files, you can use a single agent-specific file in your repository root:
- `CLAUDE.md` - Instructions for Claude-based agents
- `GEMINI.md` - Instructions for Gemini-based agents

These root-level files are simpler but don't support directory-based precedence.

**AGENTS.md vs copilot-instructions.md:**
- **copilot-instructions.md** - GitHub Copilot specific, always loaded for the entire repository
- **AGENTS.md** - AI agent standard, directory-based precedence, works across different AI agents

**Recommendation:** For GitHub Copilot projects, prefer `copilot-instructions.md` and path-specific instructions unless you need directory-based precedence.

#### When Instructions Take Effect

- ✅ **Immediately** - Instructions are active as soon as you save the file
- ✅ **Automatic** - No restart or reload needed
- ✅ **Always applied** - Custom instructions are added to every Copilot request in that repository

**Verify usage:** In Copilot Chat, check the "References" section of responses to see if `.github/copilot-instructions.md` is listed.

#### Priority When Multiple Instructions Exist

1. **Personal instructions** (highest priority)
2. **Repository instructions** (`.github/copilot-instructions.md`)
3. **Organization instructions** (lowest priority)
4. **Path-specific** instructions are combined with repository-wide when paths match

**Avoid conflicts:** Try not to provide contradictory guidance across different instruction types.

### Degrees of Freedom

Match specificity to task fragility:
- **High freedom (text instructions)**: Multiple valid approaches, context-dependent decisions
- **Medium freedom (pseudocode/parameterized scripts)**: Preferred pattern exists, some variation acceptable  
- **Low freedom (specific scripts)**: Fragile operations, consistency critical, specific sequence required

### Content Organization

**What NOT to include in skills:** README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, etc. Only include essential information for task execution.

**Remember:** Build commands, project structure, and coding standards belong in custom instructions, not skills!

---

## Skill Creation Process

**Note:** Use this section when you've determined that creating or updating a skill is the best approach for improving agent performance.

### Step 1: Understand with Concrete Examples

Clarify concrete examples of skill usage. For a workflow debugging skill, ask:
- "What functionality should this support?"
- "Can you give examples of how this would be used?"
- "What prompts would trigger this skill?"

Avoid overwhelming with too many questions at once. Conclude when functionality is clear.

### Step 2: Create SKILL.md

Create the skill directory and SKILL.md file in `.github/skills/`:

```bash
mkdir .github/skills/<skill-name>
New-Item .github/skills/<skill-name>/SKILL.md
```

Note: Skill files must be named `SKILL.md` (case-sensitive).

### Step 3: Write the Skill

**Write YAML frontmatter:**
```yaml
---
name: skill-name
description: Clear description of what the skill does and when Copilot should use it. Be specific about the triggers and use cases.
license: Optional - if you want to specify a license
---
```

Example description: "Guide for debugging failing GitHub Actions workflows. Use this when asked to debug failing GitHub Actions workflows, analyze CI failures, or investigate workflow run errors."

**Write Markdown body:** 
- Use imperative form
- First 50 lines should contain essential content with references to detailed sections below
- **CRITICAL:** Include comprehensive Quick Reference with navigation links
- Include clear step-by-step instructions
- Provide examples where helpful
- Keep concise, iterate over time

**Example structure:**
```markdown
# Skill Name

Quick overview of what this skill does.

## Quick Reference

**Navigation:**
- **Setup & Configuration** → [Initial Setup](#setup), [Configuration](#configuration), [Dependencies](#dependencies)
- **Core Patterns** → [Pattern A](#pattern-a), [Pattern B](#pattern-b), [Advanced Usage](#advanced-usage)
- **Mocking** → [Mock Feature X](#mock-feature-x), [Mock Feature Y](#mock-feature-y)
- **Best Practices** → [Do's and Don'ts](#best-practices), [Common Pitfalls](#common-pitfalls)
- **Troubleshooting** → [Common Issues](#troubleshooting)

**Essential commands:**
```bash
command-to-setup
command-to-run
```

**Key pattern example:**
```typescript
// Brief example of most common use case
```

---

## Setup
[Detailed setup instructions]

## Pattern A
[Detailed pattern explanation]

## Mock Feature X
[Detailed mocking guide]

## Best Practices
[Detailed best practices]

## Troubleshooting
[Common issues and solutions]
```

### Step 4: Iterate

Use skill in real Copilot sessions → notice where Copilot struggles or gets confused → update SKILL.md → test again. Skills grow and improve through actual usage with GitHub Copilot.

**Testing tips:**
- Use clear prompts that should trigger the skill
- Observe when Copilot uses the skill (check if it follows your instructions)
- Refine the description if Copilot doesn't load the skill when expected
- Add examples or clarifications to the body based on real usage patterns

---

## Skill Quality Checklist

Before finalizing a skill, verify it includes:

**✅ Required elements:**
- [ ] YAML frontmatter with `name` and comprehensive `description`
- [ ] Quick Reference section in first 50 lines
- [ ] Table of contents with hash links to ALL major sections
- [ ] Essential commands, patterns, or setup instructions
- [ ] Detailed sections with proper `##` or `###` headings
- [ ] Examples showing common use cases
- [ ] Code snippets with proper syntax highlighting

**✅ Navigation structure:**
- [ ] Quick Reference organized into logical groupings (Setup, Patterns, Mocking, etc.)
- [ ] Hash links use exact heading text (case-sensitive, spaces become hyphens)
- [ ] All major sections are linked from Quick Reference
- [ ] Important subsections are included in navigation

**✅ Content quality:**
- [ ] Instructions are imperative and actionable
- [ ] Examples are copy-paste ready
- [ ] Edge cases and common pitfalls covered
- [ ] Troubleshooting section for known issues
- [ ] No unnecessary content that belongs in custom instructions

**❌ Common mistakes to avoid:**
- Missing Quick Reference section entirely
- Quick Reference without hash links to sections
- Incomplete navigation (missing major sections)
- Vague or generic description in frontmatter
- First 50 lines contain only setup code without navigation
- No section headings (makes navigation impossible)
- Content that applies to 80%+ of tasks (belongs in custom instructions instead)