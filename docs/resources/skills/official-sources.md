---
type: Reference
title: Official Skill Sources and the Agent Skills Format
description: The Agent Skills open standard, the SKILL.md format, where Claude Code loads skills from, and every first-party Anthropic repository and plugin marketplace that ships skills.
tags: [skills, agent-skills, anthropic, claude-code, plugins, marketplace, specification]
sources:
  - id: blog-skills
    resource: https://claude.com/blog/skills
    title: Introducing Agent Skills (2025-10-16, updated 2025-12-18)
  - id: blog-dir
    resource: https://claude.com/blog/organization-skills-and-directory
    title: Skills for organizations, partners, the ecosystem (2025-12-18)
  - id: agentskills
    resource: https://agentskills.io/
    title: Agent Skills overview and client showcase
  - id: spec
    resource: https://agentskills.io/specification
    title: Agent Skills Specification
  - id: platform
    resource: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
    title: Agent Skills - Claude Platform docs
  - id: cc-skills
    resource: https://code.claude.com/docs/en/skills
    title: Claude Code - Skills
  - id: cc-mkt
    resource: https://code.claude.com/docs/en/plugin-marketplaces
    title: Claude Code - Create a marketplace
  - id: cc-mkt-ref
    resource: https://code.claude.com/docs/en/plugins/marketplace-reference
    title: Claude Code - Marketplace reference
  - id: gh-skills
    resource: https://github.com/anthropics/skills
    title: anthropics/skills
  - id: gh-official
    resource: https://github.com/anthropics/claude-plugins-official
    title: anthropics/claude-plugins-official
  - id: gh-cc
    resource: https://github.com/anthropics/claude-code/tree/main/plugins
    title: anthropics/claude-code plugins
  - id: gh-community
    resource: https://github.com/anthropics/claude-plugins-community
    title: anthropics/claude-plugins-community
  - id: claude-skills-page
    resource: https://claude.com/skills
    title: Claude Skills product page
  - id: connectors
    resource: https://claude.com/connectors
    title: Claude connectors and plugins directory
  - id: gh-kwp
    resource: https://github.com/anthropics/knowledge-work-plugins
    title: anthropics/knowledge-work-plugins
  - id: gh-fin
    resource: https://github.com/anthropics/financial-services
    title: anthropics/financial-services
  - id: gh-ls
    resource: https://github.com/anthropics/life-sciences
    title: anthropics/life-sciences
  - id: gh-legal
    resource: https://github.com/anthropics/claude-for-legal
    title: anthropics/claude-for-legal
  - id: gh-tag
    resource: https://github.com/anthropics/claude-tag-plugins
    title: anthropics/claude-tag-plugins
  - id: gh-k12
    resource: https://github.com/anthropics/k12-teacher-skills
    title: anthropics/k12-teacher-skills
  - id: gh-defend
    resource: https://github.com/anthropics/defending-code-reference-harness
    title: anthropics/defending-code-reference-harness
  - id: gh-launch
    resource: https://github.com/anthropics/launch-your-agent
    title: anthropics/launch-your-agent
  - id: gh-cookbooks
    resource: https://github.com/anthropics/claude-cookbooks/tree/main/skills
    title: claude-cookbooks skills
  - id: gh-spec
    resource: https://github.com/agentskills/agentskills
    title: agentskills/agentskills (spec repository)
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Official Skill Sources and the Agent Skills Format

Star counts, licences and push dates were read from the GitHub API on
2026-10-12. "Unverified" marks claims that could not be checked.

## 1. The format

**History.** Agent Skills launched on 2025-10-16 in the Claude apps, the API
(`/v1/skills`, needs the code-execution tool) and Claude Code.[^blog-skills]
On 2025-12-18 Anthropic published the format as an open standard at
agentskills.io, together with org-wide admin provisioning and a partner
directory.[^blog-dir] The standard is developed in the open in
`agentskills/agentskills` (26k stars, Apache-2.0), which also ships the
`skills-ref validate` validator.[^gh-spec] Whether it has moved to a foundation
is unverified.

**Adopters.** The agentskills.io showcase lists, among others: Claude Code,
Claude, ChatGPT and Codex, GitHub Copilot, VS Code, Cursor, Gemini CLI, Junie,
OpenCode, OpenHands, Amp, Goose, Letta, Factory, Kiro, Roo Code, TRAE, Mistral
Vibe, Spring AI, Databricks, Snowflake Cortex Code, Tabnine, Qodo and
OpenClaw.[^agentskills] A skill written once therefore works far beyond Claude
Code; most community repositories target several agents.

**SKILL.md.** A skill is a directory with `SKILL.md` (YAML frontmatter plus a
markdown body) and optional `scripts/`, `references/` and `assets/`.[^spec]

| Field | Rule |
|---|---|
| `name` | required; 1-64 chars, `a-z`, `0-9`, `-`; no leading, trailing or double hyphen; must match the directory name |
| `description` | required; 1-1024 chars; what the skill does and when to use it |
| `license`, `compatibility` (max 500), `metadata` (string map) | optional |
| `allowed-tools` | optional, experimental; space-separated, e.g. `Bash(git:*) Read` |

Progressive disclosure: about 100 tokens of metadata at start-up, the body
(recommended under 5,000 tokens, under 500 lines) when the skill activates,
bundled files only when needed.[^spec]

**Claude Code extensions.** Claude Code also accepts `when_to_use`,
`argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`,
`disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`,
`hooks`, `paths` and `shell`. Outside Claude Code (claude.ai upload, Skills
API) any field beyond the standard ones is a hard error.[^cc-skills]

**Load locations in Claude Code.**[^cc-skills]

| Scope | Path |
|---|---|
| Enterprise | managed settings directory `.claude/skills/` |
| Personal | `~/.claude/skills/<name>/SKILL.md` |
| Project | `.claude/skills/`, nested `<subdir>/.claude/skills/`, `--add-dir` directories |
| Plugin | `<plugin>/skills/<name>/SKILL.md`, invoked as `/plugin:skill` |
| Synced from claude.ai | `~/.claude/skills/synced/` |

Precedence: enterprise > personal > project. For flokpit agents (`claude -p
--bare`) the project scope of a cloned repository is ignored on purpose, so
breed skills must land in the personal scope or arrive as a plugin (see the
[summary](/skills/summary.md)).

**API and claude.ai.** Pre-built skill ids `pptx`, `xlsx`, `docx`, `pdf` exist
on the API and claude.ai but not in Claude Code. API skills run without network
access and cannot install packages. Custom skills do not sync between
surfaces.[^platform]

## 2. Plugin marketplaces

A marketplace is a repository with `.claude-plugin/marketplace.json`
(`name`, `owner`, `plugins`). Add it with `/plugin marketplace add <owner/repo
| git URL | path | URL>`, install with `/plugin install <plugin>@<marketplace>`,
check with `claude plugin validate`. Plugin sources can be a relative path,
`github` (repo, ref, sha), any git `url`, `git-subdir` (sparse clone), `npm`,
an `archive` with sha256, or a `command`. A plugin bundles skills, commands,
agents, hooks, MCP servers and LSP servers.[^cc-mkt][^cc-mkt-ref]

Marketplace names such as `claude-plugins-official`, `anthropic-agent-skills`,
`knowledge-work-plugins`, `claude-community` and `life-sciences` are reserved
for repositories under github.com/anthropics, so these names cannot be
spoofed.[^cc-mkt-ref]

## 3. First-party repositories

| Repository | Stars | Licence | Last push | Content |
|---|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 180,720 | Apache-2.0 per skill; docx/pdf/pptx/xlsx source-available | 2026-10-09 | 19 skills in 5 plugins (marketplace `anthropic-agent-skills`)[^gh-skills] |
| [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins) `plugins/` | 150,409 | none detected | 2026-10-11 | 13 plugins (marketplace `claude-code-plugins`); older originals of the official ones[^gh-cc] |
| [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/skills) `skills/` | 53,381 | MIT | 2026-10-10 | 3 notebooks, 3 example skills (financial statements, brand guidelines, financial models)[^gh-cookbooks] |
| [anthropics/financial-services](https://github.com/anthropics/financial-services) | 39,536 | Apache-2.0 | 2026-09-21 | 19 plugins, 112 SKILL.md (banking, equity research, PE, KYC, month-end close)[^gh-fin] |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 37,738 | Apache-2.0 | 2026-10-12 | the official directory: 315 plugins, 53 vendored, 262 pinned to vendor repos[^gh-official] |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | 29,319 | Apache-2.0 | 2026-10-12 | 123 plugins, 252 SKILL.md; job plugins (engineering, product-management, operations, design, data, ...) plus partners[^gh-kwp] |
| [anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal) | 9,652 | Apache-2.0 | 2026-09-29 | 13 plugins, 151 SKILL.md[^gh-legal] |
| [anthropics/defending-code-reference-harness](https://github.com/anthropics/defending-code-reference-harness) | 7,568 | NOASSERTION | 2026-08-06 | 9 security skills (threat-model, triage, vuln-scan, patch, verify, ...)[^gh-defend] |
| [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | 4,630 | Apache-2.0 | 2026-10-12 | read-only mirror of the community directory: 2,284 plugins[^gh-community] |
| [anthropics/launch-your-agent](https://github.com/anthropics/launch-your-agent) | 1,045 | Apache-2.0 | 2026-09-23 | 2 skills: idea to a live Claude Managed Agent[^gh-launch] |
| [anthropics/life-sciences](https://github.com/anthropics/life-sciences) | 618 | none detected | 2026-08-14 | 21 plugins, mostly MCP connectors; 6 SKILL.md[^gh-ls] |
| [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) | 562 | Apache-2.0 | 2026-09-01 | 4 teaching skills[^gh-k12] |
| [anthropics/claude-tag-plugins](https://github.com/anthropics/claude-tag-plugins) | 60 | Apache-2.0 | 2026-10-07 | 20 plugins for Claude in Slack[^gh-tag] |

### 3.1 anthropics/skills

Install: `/plugin marketplace add anthropics/skills`, then
`/plugin install document-skills@anthropic-agent-skills` or
`example-skills@anthropic-agent-skills`.[^gh-skills]

| Group | Skills |
|---|---|
| Documents (source-available) | `docx`, `pdf`, `pptx`, `xlsx` |
| Creative and design | `algorithmic-art`, `canvas-design`, `slack-gif-creator`, `theme-factory`, `brand-guidelines`, `frontend-design` |
| Development | `mcp-builder`, `webapp-testing` (Playwright), `web-artifacts-builder`, `claude-api`, `skill-creator` |
| Communication | `internal-comms`, `doc-coauthoring` |
| Learning | `academy-guide`, `discernment-nudge` |

### 3.2 anthropics/claude-plugins-official

The curated directory most Claude Code users install from.[^gh-official]

- **Anthropic workflow plugins (vendored):** `code-review`,
  `pr-review-toolkit`, `feature-dev`, `code-simplifier`, `commit-commands`,
  `security-guidance`, `claude-security`, `code-modernization`, `hookify`,
  `plugin-dev`, `skill-creator`, `mcp-server-dev`, `claude-md-management`,
  `claude-code-setup`, `frontend-design`, `ralph-loop`, `project-artifact`,
  `session-report`, `playground`, `agent-sdk-dev`, output styles.
- **Language servers:** clangd, csharp, gopls, jdtls, kotlin, lua, php,
  pyright, ruby, rust-analyzer, swift, typescript.
- **Vendored MCP integrations:** asana, context7, firebase, github, gitlab,
  laravel-boost, linear, playwright, serena, terraform.
- **External plugins (262, pinned to vendor SHAs) by category:** development
  96, productivity 51, database 38, monitoring 22, security 16, deployment 9,
  design 8, other 22. Examples: superpowers, expo, stripe, supabase,
  cloudflare, vercel, sentry, datadog, semgrep, sonarqube, figma, canva,
  atlassian, notion, slack, huggingface-skills, chrome-devtools-mcp,
  mattpocock-skills. Which of them contain SKILL.md (rather than only MCP
  servers) is unverified per plugin.

### 3.3 Partner skills

The 2025-12-18 announcement names Notion, Canva, Figma and Atlassian as
directory partners.[^blog-dir] claude.com/skills and claude.com/connectors
show built-in skills, connectors and plugins but no separate partner-skill
listing.[^claude-skills-page][^connectors] Partner skills live in the vendors'
own repositories, as referenced from the official directory:[^gh-official]

| Partner | Repository |
|---|---|
| Notion | makenotion/claude-code-notion-plugin |
| Figma | figma/mcp-server-guide |
| Canva | canva-sdks/canva-skills |
| Atlassian | atlassian/atlassian-mcp-server |
| Stripe | stripe/ai |
| Vercel | vercel/vercel-plugin |
| Cloudflare | cloudflare/skills |
| Sentry | getsentry/plugin-claude |
| Zapier | zapier/zapier-mcp |
| Box | box/skills |
| Slack | slackapi/slack-mcp-plugin |
| Miro | miroapp/miro-ai |
| Hugging Face | huggingface/skills |
| Supabase | supabase-community/supabase-plugin |
| Azure | microsoft/azure-skills |

[^blog-skills]: Introducing Agent Skills (2025-10-16, updated 2025-12-18)
[^blog-dir]: Skills for organizations, partners, the ecosystem (2025-12-18)
[^agentskills]: Agent Skills overview and client showcase
[^spec]: Agent Skills Specification
[^platform]: Agent Skills - Claude Platform docs
[^cc-skills]: Claude Code - Skills
[^cc-mkt]: Claude Code - Create a marketplace
[^cc-mkt-ref]: Claude Code - Marketplace reference
[^gh-skills]: anthropics/skills
[^gh-official]: anthropics/claude-plugins-official
[^gh-cc]: anthropics/claude-code plugins
[^gh-community]: anthropics/claude-plugins-community
[^claude-skills-page]: Claude Skills product page
[^connectors]: Claude connectors and plugins directory
[^gh-kwp]: anthropics/knowledge-work-plugins
[^gh-fin]: anthropics/financial-services
[^gh-ls]: anthropics/life-sciences
[^gh-legal]: anthropics/claude-for-legal
[^gh-tag]: anthropics/claude-tag-plugins
[^gh-k12]: anthropics/k12-teacher-skills
[^gh-defend]: anthropics/defending-code-reference-harness
[^gh-launch]: anthropics/launch-your-agent
[^gh-cookbooks]: claude-cookbooks skills
[^gh-spec]: agentskills/agentskills (spec repository)
