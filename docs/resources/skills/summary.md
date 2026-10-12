---
type: Summary
title: Skills Research Summary
description: Which skill sources are actually used most, which are trustworthy, which skills fit which breed, and what this means for delivering skills to flokpit agents.
tags: [summary, skills, breeds, recommendations]
sources:
  - id: official
    resource: /skills/official-sources.md
    title: Official Skill Sources and the Agent Skills Format
  - id: community
    resource: /skills/community-repos.md
    title: Community Skill Repositories on GitHub
  - id: markets
    resource: /skills/marketplaces.md
    title: Skill Marketplaces, Registries and Installers
  - id: breeds
    resource: /skills/skills-by-breed.md
    title: Skills by Breed
  - id: security
    resource: /skills/security.md
    title: Security of Third-Party Skills
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Skills Research Summary

Research date 2026-10-12. Details and sources are on the linked pages.

## Take-aways

1. **One format, many agents.** Agent Skills (`SKILL.md`) is an open standard
   at agentskills.io adopted by about 45 agents, including Codex, Copilot,
   Cursor and Gemini CLI. Skills in this repository are therefore portable
   beyond Claude Code.[^official]
2. **Two distribution channels.** Claude Code *plugins* (marketplaces with
   `marketplace.json`, installed with `/plugin install`) and plain *skills*
   (installed with `npx skills add` or `gh skill install`). Usage differs
   sharply: mattpocock/skills is the most installed repository on skills.sh
   (27.5M) but has under 2,000 plugin installs.[^markets]
3. **What is used most.** Claude Code plugins: Frontend Design (1.13M),
   Superpowers (1.01M), Code Review, Context7, Code Simplifier, Playwright,
   GitHub. Skills (skills.sh): find-skills, the mattpocock set (grill-me, tdd,
   improve-codebase-architecture, handoff, triage), agent-browser,
   frontend-design, vercel-react-best-practices. Some top skills.sh entries
   look inflated (700K+ installs on repositories with 7-15 stars).[^markets]
4. **The core sources** are few: anthropics/skills (181k stars),
   anthropics/claude-plugins-official (315 plugins), obra/superpowers (298k),
   mattpocock/skills (288k), addyosmani/agent-skills, wshobson/agents, github/awesome-copilot,
   anthropics/knowledge-work-plugins, plus vendor packs from Google,
   Microsoft, AWS, Cloudflare, Vercel, Stripe, Supabase, Expo, HashiCorp,
   Hugging Face, Sentry and Trail of Bits.[^official][^community]
5. **Open registries carry real malware.** ClawHavoc (341+ malicious ClawHub
   skills), Snyk ToxicSkills (13.4% critical issues, 76 malicious payloads),
   ESET (about 1 in 300 skills malicious). Curated and vendor sources scored
   far better. Scanners can be evaded.[^security]

## Recommended starting sets per breed

| Breed | Primary skills |
|---|---|
| developer | superpowers or mattpocock (choose one process set): test-driven-development, systematic-debugging, executing-plans, verification-before-completion, requesting-code-review, finishing-a-development-branch; vendor packs for the project's stack |
| ui-tester | anthropics webapp-testing, microsoft playwright-cli, vercel agent-browser, chrome-devtools and a11y-debugging, web-design-guidelines; image with Playwright and Chromium |
| software-architect | knowledge-work-plugins architecture and system-design, wshobson ADRs, architecture-patterns, api-design-principles and STRIDE, softaworks c4-architecture and mermaid-diagrams, Trail of Bits audit-context-building |
| project-manager | GitHub or Linear or Atlassian with token auth, knowledge-work-plugins product-management (write-spec, sprint-planning, stakeholder-update), operations status-report, anthropics internal-comms |
| reviewer | superpowers receiving-code-review and verification-before-completion, Trail of Bits differential-review, Sentry code-review and security-review, official pr-review-toolkit |
| planner | superpowers writing-plans, dispatching-parallel-agents, brainstorming (non-interactive) |

Full tables, runtime needs and headless caveats: [Skills by
Breed](/skills/skills-by-breed.md).[^breeds]

## Consequences for agentic-templates

- **Delivery under `--bare`.** flokpit agents ignore skills in the cloned
  repository. Breed skills must be vendored here, pinned to a commit, and
  installed into the personal scope (`~/.claude/skills`) by the image or by
  `flokpit-agentd`. Never install from a registry at pod runtime.
- **Skills drive image variants.** Browser skills need Playwright and
  Chromium; diagram rendering needs Chromium; CodeQL is large. Only the
  ui-tester image should carry a browser.
- **Interactive skills need a channel.** Skills that ask the user questions
  must ask in the flokpit channel (intent `QUESTION`) or run without asking.
- **OAuth-only integrations do not work in pods.** Use token-based MCP
  servers through the flokpit gateway.
- **flokpit-specific skills are missing.** No public skill knows flokpit's
  chat tools, `chat_spawn`, intents or hand-off rules; formation leads and
  the shared house rules need skills written here.
- **Adopt with review.** Follow the rules in [Security](/skills/security.md):
  first-party and vendor sources first, vendored and pinned, read and
  scanned, no widening of breed permissions.

## Open questions

| # | Question |
|---|---|
| 1 | Vendor skills as plain folders under `skills/`, or as a flokpit plugin marketplace (`marketplace.json`) that the image installs? |
| 2 | How are licences tracked for vendored skills (CC-BY-SA, GPL and unlicensed repositories exist)? |
| 3 | Which mattpocock skills to adopt next to or instead of superpowers? Both cover TDD, debugging and planning, and overlapping process skills would conflict |
| 4 | Should skill adoption be measured (task success with and without a skill, like Tessl's impact score) before it becomes a breed default? |

[^official]: Official Skill Sources and the Agent Skills Format
[^community]: Community Skill Repositories on GitHub
[^markets]: Skill Marketplaces, Registries and Installers
[^breeds]: Skills by Breed
[^security]: Security of Third-Party Skills
