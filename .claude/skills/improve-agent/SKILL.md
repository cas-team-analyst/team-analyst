---
name: improve-agent
description: Guide for improving Claude Code Agent performance through skills, CLAUDE.md memory, AGENTS.md, or other configuration. Use this when asked to improve agent behavior, create/update skills, modify CLAUDE.md memory, update AGENTS.md, or customize Claude Code performance in projects.
---

# Agent Improvement Guide

Guide for improving Claude Code Agent performance through skills, CLAUDE.md memory, AGENTS.md, and other extension methods.

## Quick Reference

**What this skill covers:** Improving Claude Code Agent performance through multiple approaches including Skills, CLAUDE.md Memory, Auto Memory, Modular Rules, and AGENTS.md. Learn when to use each method and how to implement them.

**Extension types:**
- **Skills** = On-demand, specialized (`.claude/skills/NAME/SKILL.md` or `~/.claude/skills/NAME/SKILL.md`) → [Details](#agent-skills)
- **CLAUDE.md Memory** = Always-in-context, general (`CLAUDE.md` or `.claude/CLAUDE.md`) → [Details](#claudemd-memory-setup)
- **Auto Memory** = Claude's automatic learning (`~/.claude/projects/<project>/memory/`) → [Details](#auto-memory)
- **Modular Rules** = Topic-specific instructions (`.claude/rules/*.md`) → [Details](#modular-rules)
- **AGENTS.md** = Directory-based precedence (nearest `AGENTS.md` wins) → [Details](#agent-instructions-agentsmd)

**Decision:** Need it for 80%+ of tasks? → CLAUDE.md Memory. Specific workflows only? → Skill. Different rules per directory? → Modular Rules or AGENTS.md.  
→ [See detailed decision guide](#skills-vs-claudemd-memory-decision-guide)

**Key principles:**
- **Concise is key**: Context window is shared. Only add what Claude doesn't already know. Challenge each piece: "Does this justify its token cost?"
- **First 50 lines critical**: Claude often only reads the start of files. Put essential content first with lots of # references to detailed sections below.
- **Iterative not comprehensive**: Skills grow over time. First draft should be concise and focused, not exhaustive. → [Iteration guide](#step-4-iterate)
- **Match freedom to fragility**: High freedom (text) for flexible tasks, low freedom (specific scripts) for fragile operations. → [Details](#degrees-of-freedom)
- **Keep CLAUDE.md under 500 lines**: Move reference material to skills which load on-demand.
- **Keep skills under 1,000 lines when reasonable**: Focus on actionable guidance, condense redundant content, split if too large. → [Details](#writing-effective-skills)

**Improvement process:**
0. Identify what needs improvement (agent understanding, task execution, domain knowledge, etc.). Ask the user questions if you aren't sure. → [See Step 0](#step-0-identify-improvement-area)
1. Decide best approach: CLAUDE.md memory, skill, AGENTS.md, or modular rules? → [Decision guide](#skills-vs-claudemd-memory-decision-guide)
2. **If CLAUDE.md memory:** Update `CLAUDE.md` or `.claude/CLAUDE.md` → [Setup guide](#claudemd-memory-setup)
3. **If AGENTS.md:** Create/update `AGENTS.md` in relevant directory → [AGENTS.md guide](#agent-instructions-agentsmd)
4. **If skill:** Understand with concrete examples → [See Step 1](#step-1-understand-with-concrete-examples)
5. **If skill:** Create/update SKILL.md file → [See Step 2](#step-2-create-skillmd)
6. **If skill:** Write metadata and body → [See Step 3](#step-3-write-the-skill)
7. Test and iterate based on usage → [See Step 4](#step-4-iterate)

**Writing best practices:** → [Effective instructions](#writing-effective-instructions), [What NOT to include](#what-not-to-include-in-instructions), [Testing approach](#testing-and-iterating), [Troubleshooting](#troubleshooting)

**Naming:** lowercase-with-hyphens, under 64 chars, verb-led (e.g., `rotate-pdf`, `debug-github-actions`)

**Agent improvement methods overview:** → [See all methods](#agent-improvement-methods)

**SKILL.md structure:**
- **YAML frontmatter** (required):
  - `name`: Unique identifier, lowercase with hyphens
  - `description`: What it does AND when Claude should use it (this is how Claude decides to load the skill)
  - `context` (optional): Set to `fork` to run in isolated subagent
  - `agent` (optional): Which subagent type when using `context: fork`
  - `disable-model-invocation` (optional): Set to `true` to prevent auto-loading
  - `user-invocable` (optional): Set to `false` to hide from menu
  - `allowed-tools` (optional): Tools Claude can use without asking
  - `argument-hint` (optional): Hint for expected arguments
- **Markdown body**: Instructions, examples, and guidelines for Claude to follow → [Writing guide](#writing-effective-skills)

**How Claude uses skills:** When performing tasks, Claude decides when to use skills based on your prompt and the skill's description. When Claude chooses a skill, the SKILL.md file is injected into the agent's context. → [Content tips](#content-organization)

**String substitutions in skills:** `$ARGUMENTS` (all args), `$N` or `$ARGUMENTS[N]` (specific arg), `${CLAUDE_SESSION_ID}` (session ID)

**Dynamic context injection:** Use `` !`command` `` to run shell commands before skill loads (output replaces placeholder)

---

## Detailed Guidance

### Agent Improvement Methods

**Skills provide:**
- Specialized workflows for specific domains
- Tool integrations for file formats or APIs
- Domain expertise (schemas, business logic)
- Procedural knowledge and best practices
- Can run in isolated subagent contexts with `context: fork`

**CLAUDE.md memory provides:**
- Project-wide coding standards and conventions
- Build, test, and run commands
- Project structure and architecture
- Always-available foundational knowledge
- Hierarchical loading (parent to child directories)
- Import syntax (`@path/to/file`) for modular organization

**Auto memory provides:**
- Claude's automatic learning and note-taking
- Project patterns discovered during sessions
- Debugging insights and solutions
- Your preferences and workflow habits
- Persisted in `~/.claude/projects/<project>/memory/`

**Modular rules (`.claude/rules/*.md`) provide:**
- Topic-specific instructions organized by file
- Path-specific rules using `paths:` frontmatter with globs
- Better organization than single large CLAUDE.md
- Supports subdirectories and symlinks

**AGENTS.md provides:**
- Directory-based instruction precedence
- Module-specific agent behavior
- Cross-agent compatibility (open standard)
- Alternative to CLAUDE.md with hierarchical override

### Writing Effective Skills

**First 50 lines are critical:** Claude often only reads the beginning of files. Structure skills with essential content and navigation first, detailed sections below. Expect Claude to read the first 50 lines, then jump to specific sections as needed.

**Be iterative:** Don't aim for comprehensive coverage in first draft. Skills improve over time through real usage. Start concise and focused, add details as patterns emerge.

**Keep it focused:** If a skill becomes too large, consider splitting into multiple focused skills rather than one comprehensive skill.

**Keep skills under 1,000 lines when reasonable:** Skills should be concise and focused. Aim to keep skills under 1,000 lines by:
- Removing redundant explanations
- Condensing examples to essentials
- Summarizing validation checks rather than exhaustive lists
- Focusing on actionable guidance over comprehensive documentation
- Splitting overly large skills into multiple focused skills
If a skill exceeds 1,000 lines, evaluate whether content can be condensed or split. Remember: skills are loaded on-demand, but once loaded they consume context tokens. Lean skills are more effective.

**Description is key:** The `description` field in YAML frontmatter is how Claude decides whether to use your skill. Be comprehensive and specific about what the skill does and when it should be used.

**Supporting files:** Skills can include multiple files in their directory (templates, examples, scripts). Reference them from SKILL.md so Claude knows when to load them.

### Skills vs CLAUDE.md Memory: Decision Guide

**CRITICAL: Before creating a skill, determine if CLAUDE.md memory is more appropriate.**

#### CLAUDE.md Memory (`CLAUDE.md` or `.claude/CLAUDE.md`)

**Use CLAUDE.md memory when:**
- Information is relevant to **almost every task** in the project
- Guidance applies broadly across all files and features
- Content describes "how this project works" in general

**Examples of CLAUDE.md memory:**
- Coding standards and style preferences
- Build, test, and run commands
- Project structure and architecture overview
- Where to find key files (configs, tests, docs)
- CI/CD pipeline steps and validation requirements
- Common gotchas and workarounds
- Environment setup and dependencies
- Naming conventions and coding patterns

**Benefits:**
- **Always in context** - No need for Claude to decide when to load them
- Perfect for foundational knowledge every task needs
- Reduces repetitive explanations across multiple skills
- Hierarchical loading from parent directories
- Supports imports with `@path/to/file` syntax

**Locations:**
- Project: `CLAUDE.md` or `.claude/CLAUDE.md` (committed to git)
- User: `~/.claude/CLAUDE.md` (personal preferences, all projects)
- Local: `CLAUDE.local.md` (personal project settings, gitignored)
- Managed: System paths for enterprise deployments

**How to create:** → [See CLAUDE.md Memory Setup](#claudemd-memory-setup)

#### Agent Skills (`.claude/skills/` or `~/.claude/skills/`)

**Use skills when:**
- Information is relevant only to **specific tasks or domains**
- Guidance is specialized for particular workflows
- Content would clutter context if always loaded

**Examples of skills:**
- Debugging specific integrations (GitHub Actions, API endpoints)
- Working with specialized file formats (Parquet, PDF, DOCX)
- Domain-specific queries (DuckDB patterns, database schemas)
- Testing patterns for specific frameworks
- Deployment procedures for specific environments

**Benefits:**
- **Loaded on-demand** - Keeps context lean until needed
- Perfect for specialized, detailed workflows
- Can be very detailed without worrying about always using tokens
- Can run in isolated subagent contexts with `context: fork`
- Supports dynamic context injection with `` !`command` ``
- Can include supporting files (templates, examples, scripts)

#### Modular Rules (`.claude/rules/*.md`)

**Use modular rules when:**
- Different parts of your codebase have **different rules**
- Specific file types or directories need unique guidance
- You want to organize instructions by topic instead of one large CLAUDE.md
- You want to avoid cluttering repository-wide memory with niche rules

**Examples of modular rules:**
- API routes require specific error handling patterns
- Test files have different standards than production code
- Frontend components follow React patterns; backend follows Express patterns
- Database migrations need special naming conventions
- Legacy directories have different rules than new code
- Language-specific guidelines organized by file

**Benefits:**
- **Automatically loaded** - All `.md` files in `.claude/rules/` are loaded
- Combined with CLAUDE.md memory (both apply)
- Can use `paths:` frontmatter with glob patterns for conditional rules
- Supports subdirectories for organization
- Supports symlinks to share rules across projects

**How to create:** → [See Modular Rules](#modular-rules)

#### Agent Instructions (AGENTS.md)

**Use AGENTS.md when:**
- You want **directory-based precedence** (nearest file wins)
- Different subdirectories represent different modules with unique patterns
- Building multi-module projects where each module has distinct rules
- Want portability across different AI agents (not just Claude Code)

**Examples of AGENTS.md usage:**
- Monorepo with multiple apps (each with `AGENTS.md`)
- Frontend/backend split requiring different agent behaviors
- Per-package instructions in a workspace
- Module-specific coding patterns

**Benefits:**
- **Hierarchical precedence** - Closer files override parent instructions
- Works across multiple AI agents (open standard)
- Natural mapping to project structure

**How to create:** → [See Agent Instructions](#agent-instructions-agentsmd)

**Note:** AGENTS.md is an alternative to CLAUDE.md. While CLAUDE.md is Claude-specific and supports rich features like imports, AGENTS.md is cross-platform and uses directory-based precedence.

**Decision matrix:**

| Need | CLAUDE.md Memory | Skill | Modular Rules | AGENTS.md |
|------|------------------|-------|---------------|-----------||
| "How do I run tests?" | Yes | No | No | No |
| "How to debug GitHub Actions?" | No | Yes | No | No |
| "What's the project structure?" | Yes | No | No | No |
| "API routes need special error handling" | No | No | Yes | Possible |
| "Code style preferences" | Yes | No | Possible | No |
| "Frontend uses React, backend uses Express" | No | No | Yes | Yes |
| "Adding filters to Trend Analysis" | No | Yes | No | No |
| "Organize conventions by topic" | No | No | Yes | No |

**Rules of thumb:**
- **80%+ of tasks** need this info → CLAUDE.md memory
- **Specific workflows only** → Skill
- **Different rules per file type/directory** → Modular rules
- **Different rules per module with hierarchy** → AGENTS.md
- **Organize by topic** → Modular rules (`.claude/rules/`)

### CLAUDE.md Memory Setup

#### Project-Wide Memory

Create `CLAUDE.md` or `.claude/CLAUDE.md` with general guidance for the entire project:

```powershell
# Option 1: Root-level CLAUDE.md
New-Item CLAUDE.md

# Option 2: In .claude directory (recommended for organization)
New-Item -ItemType Directory -Force .claude
New-Item .claude\CLAUDE.md
```

**What to include:**
1. **Project overview** - What the project does, tech stack, size
2. **Build instructions** - Bootstrap, build, test, run, lint commands with exact steps
3. **Project layout** - Where key files live, architecture overview
4. **Validation steps** - CI checks, pre-commit hooks, manual validation
5. **Common patterns** - Coding standards, naming conventions, file organization
6. **Known issues** - Workarounds, timing requirements, order-dependent commands

**Example structure:**
```markdown
# Project Overview
This is a Next.js claims analytics app with TypeScript, Tailwind CSS, and Highcharts.

# Build & Test Commands
- Install: `npm install`
- Dev server: `npm run dev`
- Tests: `npm test` (runs Jest)
- Coverage: `npm run test:coverage`

# Project Structure
- `app/` - Next.js app directory (pages, components, API routes)
- `__tests__/` - Jest test files
- `.claude/skills/` - Claude Code agent skills

# Coding Standards
- Use TypeScript strict mode
- Test coverage requirement: >80%
- Always add test command comment to new test files
```

**Pro tip:** Ask Claude to generate it for you: "Create a CLAUDE.md file for this project with our conventions and build commands."

**Recommended template structure:**
```markdown
# [Technology or Domain Name] Guidelines

## Purpose
Brief statement of what this file covers and when these instructions apply.

## Naming Conventions
- Rule 1
- Rule 2

## Code Style
- Style rule 1

```javascript
// Example showing correct pattern
const activeUsers = users.filter(user => user.isActive);
```

## Error Handling
- How to handle errors
- What patterns to use

## Security Considerations
- Security rule 1
- Security rule 2

## Testing Guidelines
- Testing expectation 1

## Performance
- Performance consideration 1
```

Adapt this structure to your needs while maintaining clear sectioning and bullet-point format.

**Memory scopes:**
- **Project**: `CLAUDE.md` or `.claude/CLAUDE.md` - Committed to git, shared with team
- **User**: `~/.claude/CLAUDE.md` - Personal preferences, applies to all projects
- **Local**: `CLAUDE.local.md` or `.claude/CLAUDE.local.md` - Project-specific personal settings, auto-gitignored
- **Managed**: System paths (enterprise deployments) - Organization-wide policies

**CLAUDE.md imports:** Use `@path/to/file` to import additional files:
```markdown
See @README.md for project overview and @package.json for available commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
- personal preferences @~/.claude/my-project-prefs.md
```

**Keep CLAUDE.md under 500 lines:** Move detailed reference material to skills (loaded on-demand) or `.claude/rules/` (modular organization).

#### Modular Rules

**When to use:** Organize instructions by topic or apply rules conditionally based on file paths.

**When to use:** Organize instructions by topic or apply rules conditionally based on file paths.

**Use modular rules when:**
- Different parts of your codebase have different rules (e.g., API routes vs frontend components)
- You want to organize instructions by topic instead of one large CLAUDE.md
- Specific directories require unique validation or patterns
- You want better organization and maintainability

**Examples:**
- API routes must follow specific error handling patterns
- Test files have different coding standards than production code
- Database migration files require special naming conventions
- Language-specific guidelines (TypeScript, Python, etc.)
- Frontend conventions vs backend conventions

Create `.claude/rules/NAME.md` files (where NAME describes the topic):

```powershell
New-Item -ItemType Directory -Force .claude\rules
New-Item .claude\rules\api-guidelines.md
New-Item .claude\rules\testing-standards.md
```

**All `.md` files in `.claude/rules/` are automatically loaded.** For unconditional rules (apply everywhere):

```markdown
# Testing Standards

- All functions must have unit tests
- Test coverage must exceed 80%
- Use descriptive test names
```

**For path-specific rules,** add YAML frontmatter with `paths:` field using glob patterns:

```yaml
---
paths:
  - "app/api/**/*.ts"
---

# API Route Guidelines

API routes must:
- Use Next.js App Router patterns
- Include proper error handling
- Return typed responses
- Validate all inputs
```

**Glob pattern examples:**
- `**/*.ts` - All TypeScript files
- `app/components/**/*.tsx` - All components
- `__tests__/**/*.test.tsx` - All test files
- `**/database/**/*` - All files in any database directory
- `src/**/*.{ts,tsx}` - All TypeScript files in src (brace expansion)
- `{src,lib}/**/*.ts` - TypeScript files in src or lib directories

**Organize with subdirectories:**
```
.claude/rules/
├── frontend/
│   ├── react.md
│   └── styles.md
├── backend/
│   ├── api.md
│   └── database.md
└── testing.md
```

**Share rules with symlinks:**
```powershell
# Link to shared company standards
New-Item -ItemType SymbolicLink -Path .claude\rules\security.md -Target ~\company-standards\security.md

# Link entire directory
New-Item -ItemType SymbolicLink -Path .claude\rules\shared -Target ~\shared-claude-rules
```

**User-level rules:** Create personal rules in `~/.claude/rules/` that apply to all your projects:
```powershell
New-Item -ItemType Directory -Force ~\.claude\rules
New-Item ~\.claude\rules\my-preferences.md
```

**When combined:** If a file matches both CLAUDE.md and modular rules, both are combined and used together. Rules without `paths:` frontmatter apply everywhere.

#### Writing Effective Memory and Rules

**Length limits:** Keep CLAUDE.md under ~500 lines. Keep individual rule files under ~1,000 lines maximum. Beyond these limits, Claude may overlook some content due to context constraints.

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

**Understanding Claude's behavior:**
- **Non-deterministic** - Claude may not follow every instruction perfectly every time
- **Context limits** - Very long memory files may result in some content being overlooked
- **Specificity matters** - Clear, specific instructions work better than vague directives
- **First 200 lines of auto memory** - Only first 200 lines of `MEMORY.md` load automatically

#### What NOT to Include in Memory

Claude Code memory and rules work best with actionable instructions. Avoid:

**Generic quality improvements:**
- "Be more accurate"
- "Don't miss any issues"
- "Be consistent in your output"

**UI or formatting changes:**
- "Use bold text for critical issues"
- "Add emoji to comments"
- "Change the format of responses"

**External references without content:**
- "Follow coding standards at https://example.com/standards"
- **Better:** Copy relevant content directly into CLAUDE.md or use `@path/to/local-file`

**Redundant information:**
- README.md content (Claude can read it directly)
- Package documentation (available online)
- Common knowledge (language syntax, well-known patterns)

**What TO include:**
- Project-specific conventions and patterns
- Build, test, and run commands
- Architecture decisions and gotchas
- Domain-specific knowledge
- Common pitfalls and workarounds

#### Testing and Iterating

**Start small:** Begin with 10-20 specific rules addressing your most common needs, then iterate based on results.

**Test with real work:**
1. Save your memory/rule files
2. Use Claude on real tasks
3. Observe which instructions it follows effectively
4. Note instructions that are consistently missed or misinterpreted

**Iterate based on results:**
1. Identify a pattern that Claude could handle better
2. Add a specific instruction for that pattern
3. Test with new work
4. Refine the instruction based on results

**Use `/memory` command:** Open memory files quickly for editing during a session.

This iterative approach helps you understand what works and keeps files focused.

#### Troubleshooting

**Issue: Instructions are ignored**

Possible causes:
- CLAUDE.md file is too long (over 500 lines recommended)
- Instructions are vague or ambiguous
- Instructions conflict with each other

Solutions:
- Move detailed content to skills or `.claude/rules/`
- Rewrite vague instructions to be more specific and actionable
- Review for conflicting instructions and prioritize the most important ones

**Issue: Language-specific rules applied to wrong files**

Possible causes:
- Missing or incorrect `paths:` frontmatter in `.claude/rules/` files
- Rules in CLAUDE.md instead of modular rules file

Solutions:
- Add `paths:` frontmatter to rules that should apply conditionally
- Move language-specific rules from `CLAUDE.md` to appropriate `.claude/rules/*.md` files

**Issue: Inconsistent behavior across sessions**

Possible causes:
- Instructions are too numerous
- Instructions lack specificity
- Natural variability in AI responses

Solutions:
- Focus on your highest-priority instructions
- Add concrete examples to clarify intent
- Accept that some variability is normal for AI systems

**Issue: CLAUDE.md not loading**

Possible causes:
- File not in project root or `.claude/` directory
- Syntax errors in frontmatter (for rules with `paths:`)
- Permissions issues

Solutions:
- Verify file location: `CLAUDE.md`, `.claude/CLAUDE.md`, or `~/.claude/CLAUDE.md`
- Use `/memory` command to check which files are loaded
- Check file permissions and syntax

**Additional resources:**
- [Claude Code Memory Documentation](https://code.claude.com/docs/en/memory)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

#### Auto Memory

**What is auto memory:** Claude automatically saves learnings, patterns, and insights as it works. Unlike CLAUDE.md (which you write), auto memory contains notes Claude writes for itself.

**What Claude remembers:**
- Project patterns: build commands, test conventions, code style preferences
- Debugging insights: solutions to tricky problems, common error causes
- Architecture notes: key files, module relationships, important abstractions
- Your preferences: communication style, workflow habits, tool choices

**Where it's stored:** `~/.claude/projects/<project>/memory/`
- Each project gets its own memory directory
- Git repository root determines the project path
- Git worktrees get separate memory directories

**Structure:**
```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Index (first 200 lines loaded at session start)
├── debugging.md       # Detailed notes on debugging patterns
├── api-conventions.md # API design decisions
└── ...                # Other topic files Claude creates
```

**How it works:**
- First 200 lines of `MEMORY.md` load at session start
- Claude reads/writes memory files during your session
- Topic files load on-demand when Claude needs them

**Manage auto memory:**
- Use `/memory` command to view and edit memory files
- Tell Claude explicitly: "remember that we use pnpm, not npm"
- Edit memory files directly - they're just markdown

**Opt in/out:**
```powershell
# Force auto memory on
$env:CLAUDE_CODE_DISABLE_AUTO_MEMORY = "0"

# Force auto memory off
$env:CLAUDE_CODE_DISABLE_AUTO_MEMORY = "1"
```

**Note:** Auto memory is being rolled out gradually. Use environment variable to opt in if not yet available.

#### Agent Instructions (AGENTS.md)

**When to use:** Instructions specifically for AI agents, with hierarchical directory-based precedence.

**Use AGENTS.md when:**
- You want instructions that follow your directory structure (nearest file takes precedence)
- Different subdirectories need different agent behaviors
- You're building a multi-module project where each module has unique patterns
- You want cross-platform agent compatibility (not Claude-specific)

**How AGENTS.md works:**
- Place `AGENTS.md` files anywhere in your repository
- When Claude is working on a file, it uses the **nearest** `AGENTS.md` in the directory tree
- Closer `AGENTS.md` files override instructions from parent directories

**Example structure:**
```
project-root/
├── AGENTS.md                    # General project-wide agent instructions
├── src/
│   ├── frontend/
│   │   ├── AGENTS.md           # Frontend-specific (overrides root)
│   │   └── components/
│   └── backend/
│       ├── AGENTS.md           # Backend-specific (overrides root)
│       └── api/
└── tests/
    └── AGENTS.md               # Test-specific (overrides root)
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

When working on `src/frontend/App.tsx`, Claude uses `src/frontend/AGENTS.md` (not root).  
When working on `src/backend/routes.ts`, Claude uses `src/backend/AGENTS.md` (not root).

**AGENTS.md vs CLAUDE.md:**
- **CLAUDE.md** - Claude Code specific, supports imports/features, hierarchical loading
- **AGENTS.md** - Cross-platform standard, directory-based precedence, works across different AI agents

**Recommendation:** For Claude Code projects, prefer `CLAUDE.md` and `.claude/rules/` for richer features. Use `AGENTS.md` when you need cross-platform compatibility or directory-based override behavior.

#### When Memory Takes Effect

- **Immediately** - Memory is active as soon as you save the file
- **Automatic** - No restart or reload needed
- **Session start** - CLAUDE.md files load at the start of every Claude Code session
- **On-demand** - Subdirectory CLAUDE.md files load when Claude accesses files in those directories

**Verify usage:** Use the `/memory` command to see which memory files are currently loaded.

**Hierarchical loading:** Claude reads CLAUDE.md files recursively:
1. Starts in current working directory
2. Recurses up to (but not including) root directory
3. Discovers nested CLAUDE.md files in subdirectories as it accesses them

**Example:**
```
project/
├── CLAUDE.md              # Loaded at session start
├── src/
│   ├── CLAUDE.md          # Loaded at session start (if in src/ or below)
│   └── components/
│       └── CLAUDE.md      # Loaded when working with files in components/
```

#### Priority When Multiple Memory Sources Exist

**Memory hierarchy (highest to lowest priority):**
1. **Managed** (system-level, enterprise deployments)
2. **User** (`~/.claude/CLAUDE.md`)
3. **Project** (`CLAUDE.md` or `.claude/CLAUDE.md`)
4. **Local** (`CLAUDE.local.md`, gitignored)

**Modular rules:** All `.md` files in `.claude/rules/` are loaded and combined with CLAUDE.md

**Skills:** When same name exists at multiple levels:
- Managed > User > Project
- Plugin skills use `plugin-name:skill-name` namespace (no conflicts)

**AGENTS.md:** Nearest file wins (directory-based precedence)

**Additive vs Override:**
- **CLAUDE.md**: Additive - all levels contribute content simultaneously
- **AGENTS.md**: Override - nearest file wins, others ignored
- **Rules**: Additive - all matching rules apply
- **Skills**: Override - higher priority location wins for same name

**Avoid conflicts:** When instructions conflict, Claude uses judgment with more specific instructions taking precedence. Try to keep instructions consistent across levels.

### Degrees of Freedom

Match specificity to task fragility:
- **High freedom (text instructions)**: Multiple valid approaches, context-dependent decisions
- **Medium freedom (pseudocode/parameterized scripts)**: Preferred pattern exists, some variation acceptable  
- **Low freedom (specific scripts)**: Fragile operations, consistency critical, specific sequence required

### Content Organization

**What NOT to include in skills:** README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, etc. Only include essential information for task execution.

**Remember:** Build commands, project structure, and coding standards belong in CLAUDE.md memory, not skills!

---

## Skill Creation Process

**Note:** Use this section when you've determined that creating or updating a skill is the best approach for improving agent performance.

### Step 0: Identify Improvement Area

**Common improvement needs:**
- Agent doesn't understand project-specific workflows
- Repetitive tasks that could be automated
- Domain expertise needed for specific file types
- Specialized debugging procedures
- Deployment or release workflows

**Questions to ask:**
1. Is this knowledge needed for 80%+ of tasks? → Use CLAUDE.md memory instead
2. Is this specific to certain file types? → Consider `.claude/rules/` with `paths:` frontmatter
3. Is this a specialized workflow? → Skill is appropriate
4. Should this run in isolation? → Consider `context: fork` in skill

### Step 1: Understand with Concrete Examples

Clarify concrete examples of skill usage. For a workflow debugging skill, ask:
- "What functionality should this support?"
- "Can you give examples of how this would be used?"
- "What prompts would trigger this skill?"

Avoid overwhelming with too many questions at once. Conclude when functionality is clear.

### Step 2: Create SKILL.md

Create the skill directory and SKILL.md file:

**Project-level skill** (shared with team via git):
```powershell
New-Item -ItemType Directory -Force .claude\skills\<skill-name>
New-Item .claude\skills\<skill-name>\SKILL.md
```

**User-level skill** (personal, all projects):
```powershell
New-Item -ItemType Directory -Force ~\.claude\skills\<skill-name>
New-Item ~\.claude\skills\<skill-name>\SKILL.md
```

**Note:** Skill files must be named `SKILL.md` (case-sensitive).

**Supporting files:** Skills can include additional files in their directory:
```powershell
# Example: skill with templates and scripts
.claude\skills\my-skill\
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill in
├── examples\           # Example outputs
│   └── sample.md
└── scripts\            # Scripts Claude can execute
    └── validate.ps1
```

Reference supporting files from SKILL.md so Claude knows when to load them:
```markdown
## Additional Resources

- For complete examples, see [examples/sample.md](examples/sample.md)
- To validate output, run [scripts/validate.ps1](scripts/validate.ps1)
```

### Step 3: Write the Skill

**Write YAML frontmatter:**
```yaml
---
name: skill-name
description: Clear description of what the skill does and when Claude should use it. Be specific about the triggers and use cases.
# Optional fields:
context: fork                      # Run in isolated subagent context
agent: Explore                     # Which subagent type (Explore, Plan, general-purpose, or custom)
disable-model-invocation: true     # Prevent Claude from auto-loading (manual /skill-name only)
user-invocable: false              # Hide from / menu (Claude can still use it)
allowed-tools: Read, Grep, Glob    # Tools Claude can use without asking permission
argument-hint: "[issue-number]"    # Hint shown during autocomplete
model: claude-sonnet-4             # Model to use when skill is active
---
```

**Description examples:**
- Good: "Guide for debugging failing GitHub Actions workflows. Use this when asked to debug failing GitHub Actions workflows, analyze CI failures, or investigate workflow run errors."
- Good: "Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when the user asks 'how does this work?'"
- Too vague: "Help with debugging" (What kind of debugging? When to use?)

**String substitutions in content:**
- `$ARGUMENTS` - All arguments passed to skill
- `$N` or `$ARGUMENTS[N]` - Specific argument by index (0-based)
- `${CLAUDE_SESSION_ID}` - Current session ID

**Dynamic context injection:**
```markdown
## Pull Request Context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`

Claude receives the command output, not the commands themselves.
```

**Write Markdown body:** 
- Use imperative form
- First 50 lines should contain essential content with references to detailed sections below
- Include clear step-by-step instructions
- Provide examples where helpful
- Keep concise, iterate over time

**Example structure:**
```markdown
# Skill Name

Quick overview of what this skill does.

## Quick Reference
[Essential patterns, commands, gotchas]

---

## Detailed Steps
[Step-by-step instructions]

## Examples
[Real-world usage examples]
```

**For subagent execution (`context: fork`):**
- Skill content becomes the task prompt for the subagent
- Choose appropriate `agent` type:
  - `Explore` - Read-only exploration, research
  - `Plan` - Planning and architecture
  - `general-purpose` - Full capabilities
  - Custom agent name from `.claude/agents/`
- Subagent gets isolated context (no conversation history)
- Returns summary to main conversation

### Step 4: Iterate

Use skill in real Claude sessions → notice where Claude struggles or gets confused → update SKILL.md → test again. Skills grow and improve through actual usage with Claude Code.

**Testing tips:**
- Use clear prompts that should trigger the skill
- Observe when Claude uses the skill (check if it follows your instructions)
- Refine the description if Claude doesn't load the skill when expected
- Add examples or clarifications to the body based on real usage patterns
- Use `/memory` to verify which skills are loaded
- Check if `disable-model-invocation: true` is needed for manual-only skills

**Skill invocation patterns:**
- **Auto-load**: Claude loads skill based on description matching your request
- **Manual invoke**: You type `/skill-name` to explicitly invoke
- **With arguments**: `/skill-name arg1 arg2` passes arguments to skill
- **Subagent**: Skills with `context: fork` run in isolated context

**Common refinements:**
- Add `disable-model-invocation: true` if Claude triggers skill inappropriately
- Add `argument-hint` to improve autocomplete UX
- Split large skills into focused smaller skills
- Move supporting content to separate files in skill directory
- Add concrete examples when Claude misinterprets instructions

**Performance optimization:**
- Keep SKILL.md under 500 lines (move extras to supporting files)
- Put essential navigation in first 50 lines
- Use clear section headers for Claude to jump to relevant parts
- Reference supporting files so Claude knows when to load them