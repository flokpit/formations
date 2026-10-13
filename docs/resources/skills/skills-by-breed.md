---
type: Analysis
title: Skills by Breed
description: Which public skills fit the developer, tester, architect, project-manager, reviewer and planner breeds, what each needs inside the agent container, and which do not work headless in a flokpit pod.
tags: [skills, breeds, developer, tester, architect, project-manager, reviewer, planner, headless, container]
sources:
  - id: anthropic-skills
    resource: https://github.com/anthropics/skills
    title: anthropics/skills
  - id: superpowers
    resource: https://github.com/obra/superpowers
    title: obra/superpowers
  - id: mattpocock
    resource: https://github.com/mattpocock/skills
    title: mattpocock/skills
  - id: vercel-skills
    resource: https://github.com/vercel-labs/agent-skills
    title: vercel-labs/agent-skills
  - id: agent-browser
    resource: https://github.com/vercel-labs/agent-browser
    title: vercel-labs/agent-browser
  - id: dev-browser
    resource: https://github.com/SawyerHood/dev-browser
    title: SawyerHood/dev-browser
  - id: playwright-skill
    resource: https://github.com/lackeyjb/playwright-skill
    title: lackeyjb/playwright-skill
  - id: playwright-cli
    resource: https://github.com/microsoft/playwright-cli
    title: microsoft/playwright-cli
  - id: chrome-devtools
    resource: https://github.com/ChromeDevTools/chrome-devtools-mcp
    title: ChromeDevTools/chrome-devtools-mcp
  - id: trailofbits
    resource: https://github.com/trailofbits/skills
    title: trailofbits/skills
  - id: kwp
    resource: https://github.com/anthropics/knowledge-work-plugins
    title: anthropics/knowledge-work-plugins
  - id: official
    resource: https://github.com/anthropics/claude-plugins-official
    title: anthropics/claude-plugins-official
  - id: wshobson
    resource: https://github.com/wshobson/agents
    title: wshobson/agents
  - id: awesome-copilot
    resource: https://github.com/github/awesome-copilot
    title: github/awesome-copilot
  - id: softaworks
    resource: https://github.com/softaworks/agent-toolkit
    title: softaworks/agent-toolkit
  - id: atlassian
    resource: https://github.com/atlassian/atlassian-mcp-server
    title: atlassian/atlassian-mcp-server
  - id: notion-plugin
    resource: https://github.com/makenotion/claude-code-notion-plugin
    title: makenotion/claude-code-notion-plugin
  - id: notion-mcp
    resource: https://github.com/makenotion/notion-mcp-server
    title: makenotion/notion-mcp-server
  - id: linear-mcp
    resource: https://linear.app/docs/mcp
    title: Linear MCP docs
  - id: supabase
    resource: https://github.com/supabase/agent-skills
    title: supabase/agent-skills
  - id: cloudflare
    resource: https://github.com/cloudflare/skills
    title: cloudflare/skills
  - id: expo
    resource: https://github.com/expo/skills
    title: expo/skills
  - id: stripe
    resource: https://github.com/stripe/ai
    title: stripe/ai
  - id: sentry
    resource: https://github.com/getsentry/skills
    title: getsentry/skills
  - id: skillssh
    resource: https://skills.sh
    title: skills.sh leaderboard
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Skills by Breed

Repository and SKILL.md paths were checked against the GitHub API on
2026-10-12 unless marked unverified. Paths are relative to the repository;
browse with `https://github.com/<repo>/tree/HEAD/<path>`. "Primary" means part
of the breed's default skill set, "secondary" means useful for some tasks or
stacks. Breeds are defined in [IDEA](../../IDEA.md) (outside this bundle).

## developer

| Skill | Repository and path | Purpose | Runtime in the pod | Fit |
|---|---|---|---|---|
| test-driven-development | obra/superpowers `skills/test-driven-development` | Red-green-refactor discipline | none | primary[^superpowers] |
| systematic-debugging | obra/superpowers `skills/systematic-debugging` | Root cause before fix | none | primary |
| executing-plans, subagent-driven-development | obra/superpowers `skills/...` | Work a written plan task by task | none | primary |
| verification-before-completion | obra/superpowers | Run evidence commands before claiming done | none | primary |
| requesting-code-review, receiving-code-review | obra/superpowers | Hand off to the reviewer, handle feedback | none | primary |
| finishing-a-development-branch | obra/superpowers | Merge, PR or clean-up decision | git, `gh` | primary |
| using-git-worktrees | obra/superpowers | One worktree per task | git | secondary (each pod already has its own clone) |
| tdd, diagnosing-bugs, implement, pr | mattpocock/skills `skills/engineering/...` | Among the most installed development skills on skills.sh | none | primary candidates[^mattpocock][^skillssh] |
| git-guardrails-claude-code, setup-pre-commit | mattpocock/skills `skills/misc/...` | Guard rails for git and commits | git | secondary |
| react-best-practices, composition-patterns | vercel-labs/agent-skills `skills/...` | React and Next.js rules | none | stack-specific[^vercel-skills] |
| supabase, supabase-postgres-best-practices | supabase/agent-skills `skills/...` | Supabase and Postgres | none; CLI and token only to act | stack-specific[^supabase] |
| workers-best-practices, wrangler, durable-objects | cloudflare/skills `skills/...` | Cloudflare Workers | Node, wrangler; API token to deploy | stack-specific[^cloudflare] |
| stripe-best-practices, upgrade-stripe | stripe/ai `skills/...` | Stripe integration | none; key to act | stack-specific[^stripe] |
| expo-router, expo-upgrade, eas-* | expo/skills `plugins/expo/skills/...` | Expo and React Native | Node; `EXPO_TOKEN` for EAS | stack-specific[^expo] |
| mcp-builder | anthropics/skills `skills/mcp-builder` | Build MCP servers | Node or Python | secondary[^anthropic-skills] |
| frontend-design | anthropics/skills `skills/frontend-design` | Distinctive UI implementation; #1 Claude Code plugin | none | secondary (frontend) |
| modern-python, property-based-testing, mutation-testing | trailofbits/skills `plugins/<name>/skills/<name>` | Python tooling, PBT, mutation tests | Python, uv | secondary[^trailofbits] |
| commit, iterate-pr, find-bugs | getsentry/skills `skills/...` | Commit hygiene, CI fix loop | git, `gh` | secondary[^sentry] |

## tester

| Skill | Repository and path | Purpose | Runtime in the pod | Headless | Fit |
|---|---|---|---|---|---|
| webapp-testing | anthropics/skills `skills/webapp-testing` | Python Playwright scripts with server lifecycle helper | Python 3, `playwright`, Chromium | yes; the skill says always launch headless | primary[^anthropic-skills] |
| playwright-cli | microsoft/playwright-cli `skills/playwright-cli` | Token-efficient Playwright CLI: snapshots, actions, screenshots | Node, `@playwright/cli`, browsers | yes (default unverified) | primary[^playwright-cli] |
| agent-browser (and dogfood) | vercel-labs/agent-browser `skills/agent-browser` | Browser CLI over CDP with accessibility-tree refs; exploratory QA | `agent-browser` CLI plus Chromium | yes by default | primary[^agent-browser] |
| chrome-devtools, a11y-debugging | ChromeDevTools/chrome-devtools-mcp `skills/...` | Console, network, performance, accessibility | Node, Chrome, MCP server | yes with `--headless --isolated` | primary[^chrome-devtools] |
| debug-optimize-lcp, memory-leak-debugging | ChromeDevTools/chrome-devtools-mcp `skills/...` | Web performance and leaks | same | yes | secondary |
| Playwright plugin | anthropics/claude-plugins-official `external_plugins/playwright` | Playwright MCP tools (no SKILL.md) | Node, browsers | needs `--headless` | primary[^official] |
| web-design-guidelines | vercel-labs/agent-skills `skills/web-design-guidelines` | Audit UI against Vercel's guidelines | network (fetches rules, unverified) | yes | primary |
| wcag-audit-patterns, screen-reader-testing | wshobson/agents `plugins/accessibility-compliance/skills/...` | WCAG audit procedure | none; pair with axe-core | yes; real screen readers no | secondary[^wshobson] |
| e2e-testing-patterns | wshobson/agents `plugins/developer-essentials/skills/...` | Playwright and Cypress patterns | none | yes | secondary |
| playwright-generate-test, playwright-explore-website | github/awesome-copilot `skills/...` | Generate tests by exploring a site | Playwright MCP | yes | secondary[^awesome-copilot] |
| qa-test-planner | softaworks/agent-toolkit `skills/qa-test-planner` | Test plans and cases | none | yes | secondary[^softaworks] |
| playwright-skill | lackeyjb/playwright-skill `skills/playwright-skill` | General Playwright automation | Node 20+, Chromium download on first run | **visible browser by default**, must be forced headless | secondary[^playwright-skill] |
| dev-browser | SawyerHood/dev-browser `skills/dev-browser` | Persistent-page browser scripting | `dev-browser` CLI, Chrome | `--headless` works; extension mode does not | secondary[^dev-browser] |

The tester is the only breed that needs a browser in its image (Playwright
plus Chromium is about 400 MB). Browsers must be baked into the image, not
downloaded on first run.

## architect

| Skill | Repository and path | Purpose | Runtime in the pod | Fit |
|---|---|---|---|---|
| architecture, system-design | anthropics/knowledge-work-plugins `engineering/skills/...` | Architecture analysis, system design | none | primary[^kwp] |
| tech-debt, documentation, testing-strategy | anthropics/knowledge-work-plugins `engineering/skills/...` | Debt assessment, docs, test strategy | none | primary/secondary |
| improve-codebase-architecture, domain-modeling, codebase-design | mattpocock/skills `skills/engineering/...` | Highly installed architecture skills | none | primary candidates[^mattpocock][^skillssh] |
| architecture-decision-records | wshobson/agents `plugins/documentation-generation/skills/...` | ADR templates and process | none | primary[^wshobson] |
| architecture-patterns, api-design-principles, microservices-patterns | wshobson/agents `plugins/backend-development/skills/...` | Clean, hexagonal, DDD; REST/GraphQL; service split | none | primary |
| stride-analysis-patterns, threat-mitigation-mapping, attack-tree-construction | wshobson/agents `plugins/security-scanning/skills/...` | Threat modelling | none | primary |
| c4-architecture, mermaid-diagrams | softaworks/agent-toolkit `skills/...` | C4 and other diagrams as Mermaid text | none for text; `mmdc` plus Chromium to render | primary[^softaworks] |
| excalidraw, draw-io | softaworks/agent-toolkit `skills/...` | Editable diagram files | none for JSON/XML | secondary |
| audit-context-building, entry-point-analyzer, sharp-edges, supply-chain-risk-auditor | trailofbits/skills `plugins/<name>/skills/<name>` | Codebase context, attack surface, risky APIs, dependency risk | light; some use `gh` and network | primary (security architecture)[^trailofbits] |
| semgrep, codeql | trailofbits/skills `plugins/static-analysis/skills/...` | Static analysis | semgrep, CodeQL CLI (large) | secondary |
| create-architectural-decision-record, architecture-blueprint-generator | github/awesome-copilot `skills/...` | ADRs, architecture docs from code | none | alternative[^awesome-copilot] |
| database-schema-designer | softaworks/agent-toolkit `skills/...` | Schema design | none | secondary |

Keep the architect text-only (Mermaid source, ADR markdown) so it does not
need a browser in its image.

## project-manager

| Skill | Repository and path | Purpose | Auth in a pod | Headless | Fit |
|---|---|---|---|---|---|
| GitHub plugin (MCP) | anthropics/claude-plugins-official `external_plugins/github` | Issues, PRs, projects | token | yes | primary[^official] |
| github-issues, prd, breakdown-feature-prd | github/awesome-copilot `skills/...` | Issue workflow; PRD to issues | GitHub MCP | yes | primary/secondary[^awesome-copilot] |
| Linear plugin (MCP) | anthropics/claude-plugins-official `external_plugins/linear` | Issues, projects, cycles | API key as bearer header | yes with API key; default OAuth is interactive | primary[^linear-mcp] |
| spec-to-backlog, triage-issue, generate-status-report, jira-sprint-dashboard, capture-tasks-from-meeting-notes | atlassian/atlassian-mcp-server `skills/...` | Jira and Confluence workflows | API token | yes with token; OAuth needs a browser | primary for Jira users[^atlassian] |
| write-spec, sprint-planning, roadmap-update, stakeholder-update, synthesize-research | anthropics/knowledge-work-plugins `product-management/skills/...` | Specs, sprints, roadmap, updates | none | yes | primary[^kwp] |
| status-report, risk-assessment, change-request | anthropics/knowledge-work-plugins `operations/skills/...` | Status, risks, change control | none | yes | primary/secondary |
| standup | anthropics/knowledge-work-plugins `engineering/skills/standup` | Standup summaries | none | yes | secondary |
| internal-comms | anthropics/skills `skills/internal-comms` | Status updates, newsletters | none | yes | primary[^anthropic-skills] |
| triage, to-spec, to-tickets, retro | mattpocock/skills `skills/engineering/...` | Triage, spec and ticket breakdown, retrospectives | none | yes | candidates[^mattpocock][^skillssh] |
| grill-me, grilling | mattpocock/skills `skills/productivity/...` | Interrogates requirements before work starts | none | interactive by design | secondary |
| Notion skills (spec-to-implementation, meeting-intelligence, knowledge-capture) | makenotion/claude-code-notion-plugin `skills/notion/...` | Notion specs and notes | hosted MCP uses interactive OAuth; swap to notion-mcp-server with an integration token (unverified) | only with the swap | secondary[^notion-plugin][^notion-mcp] |
| doc-coauthoring | anthropics/skills `skills/doc-coauthoring` | Structured document writing | none | partly interactive | secondary |
| jira | softaworks/agent-toolkit `skills/jira` | Jira via CLI or MCP | token | yes | alternative[^softaworks] |

## reviewer

| Skill | Repository and path | Purpose | Fit |
|---|---|---|---|
| receiving-code-review, verification-before-completion | obra/superpowers | Review protocol, demand evidence | primary[^superpowers] |
| differential-review | trailofbits/skills `plugins/differential-review/skills/...` | Security-focused diff review | primary[^trailofbits] |
| code-review, security-review, find-bugs, code-simplifier | getsentry/skills `skills/...` | Sentry's review practice | primary[^sentry] |
| code-review, pr-review-toolkit | anthropics/claude-plugins-official `plugins/...` | Multi-agent PR review (agents and commands, no SKILL.md); #3 Claude Code plugin | primary[^official] |
| code-review | anthropics/knowledge-work-plugins `engineering/skills/code-review` | Review checklist | secondary[^kwp] |
| sharp-edges, fp-check, second-opinion | trailofbits/skills | Risky APIs, false-positive triage | secondary |
| code-review-excellence, multi-reviewer-patterns | wshobson/agents | Review practice | secondary[^wshobson] |
| react-best-practices, web-design-guidelines | vercel-labs/agent-skills | Frontend review rubric | secondary[^vercel-skills] |

## planner

| Skill | Repository and path | Purpose | Fit |
|---|---|---|---|
| writing-plans | obra/superpowers `skills/writing-plans` | Small-step implementation plans | primary[^superpowers] |
| dispatching-parallel-agents | obra/superpowers `skills/dispatching-parallel-agents` | Split work across agents; maps onto flokpit spawning | primary |
| brainstorming | obra/superpowers `skills/brainstorming` | Design before plan | primary, with the interactive caveat |
| create-implementation-plan, breakdown-plan | github/awesome-copilot `skills/...` | Plan templates | secondary[^awesome-copilot] |
| write-spec, sprint-planning | anthropics/knowledge-work-plugins | Spec and sprint | secondary[^kwp] |
| spec-to-backlog | atlassian/atlassian-mcp-server | Spec to Jira epics and tickets | secondary[^atlassian] |

## Formation leads

A formation lead (see [IDEA](../../IDEA.md)) needs orchestration skills on top
of its breed's own: `dispatching-parallel-agents` and `writing-plans`
(superpowers), mattpocock `handoff` (`skills/productivity/handoff`) and `to-tickets`, and a hand-off and
verification discipline (`requesting-code-review`,
`verification-before-completion`). None of the public skills knows flokpit's
`chat_spawn`, `+o` or message intents, so a flokpit-specific lead skill has to
be written here.

## Headless and container caveats

- **Interactive OAuth.** Notion hosted MCP, Linear and Atlassian on their
  default OAuth flows, and the Asana plugin need a browser login. Use API keys
  or tokens (Linear bearer key, Atlassian API token, GitHub token) delivered
  through the flokpit gateway, not stored in the pod.
- **GUI browsers.** Claude in Chrome, the desktop browser and dev-browser's
  extension mode do not work in a pod. playwright-skill defaults to a visible
  browser; Playwright MCP needs `--headless`; chrome-devtools-mcp needs
  `--headless --isolated`.
- **Interactive skills.** superpowers `brainstorming`, mattpocock `grill-me`,
  `doc-coauthoring` and `requirements-clarity` ask the user questions. In
  flokpit those questions must go to the channel with intent `QUESTION`, or
  the skill must be told to proceed on its own.
- **Image weight.** Playwright and Chromium only in the tester image;
  Mermaid rendering also pulls in Chromium; CodeQL is large.
- **Network.** Some skills fetch rules or browsers at runtime; pre-bake them
  and keep egress closed.
- **Trust.** See [Security](/skills/security.md).

[^anthropic-skills]: anthropics/skills
[^superpowers]: obra/superpowers
[^mattpocock]: mattpocock/skills
[^vercel-skills]: vercel-labs/agent-skills
[^agent-browser]: vercel-labs/agent-browser
[^dev-browser]: SawyerHood/dev-browser
[^playwright-skill]: lackeyjb/playwright-skill
[^playwright-cli]: microsoft/playwright-cli
[^chrome-devtools]: ChromeDevTools/chrome-devtools-mcp
[^trailofbits]: trailofbits/skills
[^kwp]: anthropics/knowledge-work-plugins
[^official]: anthropics/claude-plugins-official
[^wshobson]: wshobson/agents
[^awesome-copilot]: github/awesome-copilot
[^softaworks]: softaworks/agent-toolkit
[^atlassian]: atlassian/atlassian-mcp-server
[^notion-plugin]: makenotion/claude-code-notion-plugin
[^notion-mcp]: makenotion/notion-mcp-server
[^linear-mcp]: Linear MCP docs
[^supabase]: supabase/agent-skills
[^cloudflare]: cloudflare/skills
[^expo]: expo/skills
[^stripe]: stripe/ai
[^sentry]: getsentry/skills
[^skillssh]: skills.sh leaderboard
