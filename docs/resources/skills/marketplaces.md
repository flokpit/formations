---
type: Comparison
title: Skill Marketplaces, Registries and Installers
description: Where skills and plugins are listed and installed (skills.sh, the official Claude plugin directory, ClawHub, SkillsMP, aitmpl, Tessl, Smithery and others), with the install leaderboards that show which skills are actually used most.
tags: [skills, marketplace, registry, leaderboard, installs, skills-sh, claude-plugins, clawhub, cli]
sources:
  - id: skillssh
    resource: https://skills.sh
    title: skills.sh leaderboard (page data parsed 2026-10-12)
  - id: skillssh-docs
    resource: https://www.skills.sh/docs
    title: skills.sh docs
  - id: vercel-blog
    resource: https://vercel.com/blog/building-a-self-driving-skills-sh-leaderboard
    title: Building a self-driving skills.sh leaderboard (via search summary)
  - id: claude-plugins
    resource: https://claude.com/plugins
    title: Claude plugin directory (page data parsed 2026-10-12)
  - id: cc-discover
    resource: https://code.claude.com/docs/en/discover-plugins
    title: Claude Code - Install and manage plugins
  - id: cc-anthropic-mkt
    resource: https://code.claude.com/docs/en/plugins/anthropic-marketplaces
    title: Claude Code - Anthropic's marketplaces
  - id: rywalker
    resource: https://rywalker.com/research/claude-plugin-marketplace
    title: Ry Walker - Claude plugin marketplace research (June 2026)
  - id: claudemarket
    resource: https://www.claudemarket.ai/blog/claude-code-plugin-ecosystem-data-2026
    title: Claude Market ecosystem data
  - id: skillsmp
    resource: https://skillsmp.com
    title: SkillsMP
  - id: claudemarketplaces
    resource: https://claudemarketplaces.com
    title: Claude Marketplaces
  - id: claude-plugins-dev
    resource: https://claude-plugins.dev
    title: claude-plugins.dev
  - id: aitmpl
    resource: https://www.aitmpl.com
    title: Claude Code Templates (aitmpl)
  - id: smithery
    resource: https://smithery.ai/skills
    title: Smithery Skills
  - id: tessl
    resource: https://tessl.io/registry
    title: Tessl Skills Registry
  - id: mcpmarket
    resource: https://mcpmarket.com/tools/skills
    title: MCP Market Agent Skills
  - id: playbooks
    resource: https://playbooks.com
    title: Playbooks
  - id: clawhub
    resource: https://clawhub.ai
    title: ClawHub (and /api/v1/skills?sort=downloads)
  - id: parallel
    resource: https://parallel.ai/articles/best-clawhub-skills-for-openclaw
    title: Best ClawHub skills (2026-08-18)
  - id: gh-topic-as
    resource: https://github.com/topics/agent-skills
    title: GitHub topic agent-skills
  - id: gh-topic-cs
    resource: https://github.com/topics/claude-skills
    title: GitHub topic claude-skills
  - id: gh-skill-cli
    resource: https://github.blog/changelog/2026-04-17-manage-agent-skills-with-github-cli/
    title: Manage agent skills with GitHub CLI
  - id: openskills
    resource: https://jimmysong.io/ai/openskills
    title: OpenSkills overview
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-11-12T00:00:00Z
---

# Skill Marketplaces, Registries and Installers

Only two sources publish real install telemetry: **skills.sh** (skills, all
agents) and **claude.com/plugins** (Claude Code plugins). Everything else ranks
by GitHub stars or publishes no counts. Both leaderboards were read from the
page data on 2026-10-12. This page is marked stale after one month because the
rankings move quickly.

## 1. skills.sh (Vercel)

- Lists SKILL.md folders from GitHub repositories (and some well-known URLs);
  install with `npx skills add <owner/repo> [--skill <name>]`; 20 agents
  supported, including Claude Code, Codex, Cursor, Copilot, Gemini, Windsurf,
  Cline, Amp and OpenClaw.[^skillssh]
- Counts come from anonymous CLI telemetry with hourly fingerprint
  de-duplication.[^skillssh-docs] Installing a whole repository counts once for
  every skill in it, so bundle skills show near-identical numbers.
- Each skill page shows three audits graded Pass, Warn or Fail: Gen Agent
  Trust Hub (code execution, prompt injection, exfiltration), Socket (supply
  chain) and Snyk (credentials, third-party content). Vercel says installed
  skills are also reviewed by Claude in a sandbox, but "cannot guarantee the
  quality or security of every skill".[^skillssh-docs][^vercel-blog]
- Index size is ambiguous: the page data holds `totalSkills: 9893` and an
  unlabelled `1,294,292`.

### 1.1 All-time top 25

| # | Skill | Repository | Installs | Last week |
|---|---|---|---|---|
| 1 | find-skills | vercel-labs/skills | 3,814,898 | 110,524 |
| 2 | grill-me | mattpocock/skills | 1,339,209 | 58,939 |
| 3 | grill-with-docs | mattpocock/skills | 1,147,196 | 52,205 |
| 4 | agent-browser | vercel-labs/agent-browser | 1,100,262 | 67,374 |
| 5 | improve-codebase-architecture | mattpocock/skills | 1,095,007 | 53,008 |
| 6 | tdd | mattpocock/skills | 1,069,471 | 54,986 |
| 7 | setup-matt-pocock-skills | mattpocock/skills | 987,795 | 52,357 |
| 8 | frontend-design | anthropics/skills | 978,590 | 25,306 |
| 9 | handoff | mattpocock/skills | 968,753 | 54,020 |
| 10 | hyperframes-cli | heygen-com/hyperframes | 956,862 | 146,752 |
| 11 | triage | mattpocock/skills | 929,772 | 46,500 |
| 12 | prototype | mattpocock/skills | 925,297 | 44,844 |
| 13 | hyperframes | heygen-com/hyperframes | 914,614 | 137,375 |
| 14 | reddit-automation | flowkit-labs/skills (suspect, see 1.3) | 902,031 | 113,172 |
| 15 | grilling | mattpocock/skills | 895,026 | 61,775 |
| 16 | media-use | heygen-com/hyperframes | 835,077 | 146,510 |
| 17 | hyperframes-registry | heygen-com/hyperframes | 812,565 | 115,713 |
| 18 | domain-modeling | mattpocock/skills | 805,972 | 53,941 |
| 19 | hyperframes-animation | heygen-com/hyperframes | 805,929 | 144,874 |
| 20 | teach | mattpocock/skills | 798,658 | 47,203 |
| 21 | vercel-react-best-practices | vercel-labs/agent-skills | 792,696 | 22,366 |
| 22 | codebase-design | mattpocock/skills | 782,115 | 52,900 |
| 23 | hyperframes-core | heygen-com/hyperframes | 773,687 | 106,623 |
| 24 | design-mobile-apps | designed-by-ai/skills (suspect) | 768,766 | 140,054 |
| 25 | diagnosing-bugs | mattpocock/skills | 767,359 | 53,687 |

Further down: 22 Lark/Feishu skills (open.feishu.cn, about 760K each),
web-design-guidelines (vercel-labs, 727K), more mattpocock skills (code-review,
implement, to-spec, research, to-tickets: 645K-719K), remotion-best-practices
(607K), design-taste-frontend (598K), caveman (570K), about 20
microsoft/azure-skills (500K-561K each).[^skillssh]

### 1.2 Totals per repository and well-known ranks

| Repository | Installs | Skills |
|---|---|---|
| mattpocock/skills | 27.5M | 53 |
| open.feishu.cn | 20.3M | 28 |
| microsoft/azure-skills | 13.8M | 32 |
| heygen-com/hyperframes | 12.8M | 38 |
| larksuite/cli | 11.6M | 27 |
| prime-skills/runcomfy-agent-skills | 11.6M | 30 |
| leonxlnx/taste-skill | 5.1M | 13 |
| coreyhaines31/marketingskills | 4.8M | 53 |
| juliusbrussee/caveman | 4.0M | 20 |
| vercel-labs/skills | 3.8M | 1 |
| obra/superpowers | 3.4M | 14 |
| google/agents-cli | 3.4M | 7 |
| anthropics/skills | 3.4M | 18 |
| prisma/skills | 3.1M | 9 |
| vercel-labs/agent-skills | 2.8M | 9 |

Ranks of known skills: anthropics `skill-creator` #165 (404K), `pptx` #270,
`pdf` #285, `docx` #294, `webapp-testing` #309, `mcp-builder` #351;
obra/superpowers `brainstorming` #176 (389K), `systematic-debugging` #245
(289K), `writing-plans` #257, `requesting-code-review` #264,
`test-driven-development` #265; `supabase-postgres-best-practices` #131
(442K); `shadcn` #256; `neon-postgres` #268.[^skillssh]

**mattpocock/skills** is the most installed repository on skills.sh but is
used almost entirely through `npx skills`: as a Claude Code plugin it has only
1,745 installs.[^claude-plugins]

### 1.3 Suspected install inflation

Not verified, inferred from installs versus stars and first-seen dates. Several
top-100 entries have 700K-900K installs, a repository with 7-15 stars and a
first-seen date in August or September 2026: `101-skills/superpowers`
(ai-video-generation, promotes a third-party CLI), `flowkit-labs/skills`
(reddit-automation), `designed-by-ai/skills` (design-mobile-apps, Snyk
**Fail**, needs a third-party API key). The same skill set is cloned under
several orgs all named `*/superpowers`, borrowing the name of obra/superpowers.
No public report of manipulation was found. Treat skills.sh counts as a signal
only for established publishers (Anthropic, Vercel, obra, mattpocock, vendors).

## 2. Official Claude plugin directory

- claude.com/plugins, operated by Anthropic; catalogue is
  `anthropics/claude-plugins-official` (see
  [Official Sources](/skills/official-sources.md)). The page shows 342 plugins
  on 2026-10-12 (222 in June, 101 in March 2026).[^claude-plugins][^rywalker]
- The official marketplace is added automatically on the first interactive
  session; `/plugin install <name>@claude-plugins-official`. Since Claude Code
  2.1.275, `/plugin install X --marketplace owner/repo` adds and installs in
  one step.[^cc-discover]
- Some plugins carry an "Anthropic verified" badge. Anthropic does not review
  third-party marketplaces.[^cc-anthropic-mkt]

### 2.1 Top 30 plugins by installs

| # | Plugin | Installs | # | Plugin | Installs |
|---|---|---|---|---|---|
| 1 | Frontend Design | 1,134,112 | 16 | Figma | 167,556 |
| 2 | Superpowers | 1,009,371 | 17 | Supabase | 118,617 |
| 3 | Code Review | 438,525 | 18 | PR Review Toolkit | 114,856 |
| 4 | Context7 | 417,801 | 19 | Pyright LSP | 109,778 |
| 5 | Code Simplifier | 346,763 | 20 | Chrome DevTools | 102,569 |
| 6 | Playwright | 319,887 | 21 | telegram | 100,332 |
| 7 | GitHub | 319,381 | 22 | Atlassian | 92,289 |
| 8 | CLAUDE.md Management | 287,247 | 23 | Slack | 92,287 |
| 9 | Feature Dev | 256,017 | 24 | Serena | 89,147 |
| 10 | Security Guidance | 241,800 | 25 | Plugin Developer Toolkit | 67,663 |
| 11 | Vercel | 227,688 | 26 | Agent SDK Dev | 66,631 |
| 12 | TypeScript LSP | 212,522 | 27 | Explanatory Output Style | 64,377 |
| 13 | Ralph Loop | 196,527 | 28 | Playground | 64,198 |
| 14 | Claude Code Setup | 195,067 | 29 | Stripe | 61,066 |
| 15 | Commit Commands | 171,244 | 30 | Hookify | 60,376 |

Next: Greptile 56.6K, Remember 51.4K, Linear 48.0K, GitLab, Firecrawl 39.3K,
Sentry 38.8K, Hugging Face Skills 34.6K, CodeRabbit 32.4K, Semgrep 19.5K.
In June 2026 the top five were Frontend Design 867K, Superpowers 787K, Code
Review 359K, GitHub 270K, Playwright 258K.[^claude-plugins][^rywalker]

## 3. Other directories and registries

| Registry | Operator | Lists | Size (date) | Install | Popularity | Security review |
|---|---|---|---|---|---|---|
| [ClawHub](https://clawhub.ai) | OpenClaw Foundation | OpenClaw skills and plugins | ~67K (2026-08, vendor blog)[^parallel] | `clawhub` CLI | downloads, installs, stars via API | VirusTotal scan and daily rescans since Feb 2026[^clawhub] |
| [SkillsMP](https://skillsmp.com) | community | skills aggregated from GitHub | claims 3M+ (2026-10) | copy to `~/.claude/skills`; REST API, MCP server | GitHub stars | none stated[^skillsmp] |
| [claudemarketplaces.com](https://claudemarketplaces.com) | mertbuilds.com | skills, plugin marketplaces, MCP servers | 23.6K skills, 2.7K marketplaces, 12.8K MCP servers | copy command | installs (apparently mirrored from skills.sh), stars | spam checks only[^claudemarketplaces] |
| [claude-plugins.dev](https://claude-plugins.dev) | community | plugins and skills from GitHub marketplaces | not stated | `npx claude-plugins install <id>` | downloads, stars | none[^claude-plugins-dev] |
| [aitmpl.com](https://www.aitmpl.com) | davila7/claude-code-templates | 890 skills, 422 agents, 288 commands, MCPs, hooks | 2,175 components, 1.6M downloads | `npx claude-code-templates@latest --skill ...` | per-component downloads | none[^aitmpl] |
| [Smithery](https://smithery.ai/skills) | Smithery (Arcade.dev) | skills and MCP servers | 25,140 skills | Smithery CLI | low counts | unexplained "verified" badge[^smithery] |
| [Tessl Registry](https://tessl.io/registry) | Tessl | versioned skills | not stated | `npx tessl i ...` | quality and impact scores from evals | Snyk scan with review date[^tessl] |
| [MCP Market](https://mcpmarket.com/tools/skills) | MCP Market | skills (some paid), MCP | 368,155 skills | "MCP Market Hub" plugin | unlabelled counts | none stated[^mcpmarket] |
| [claudemarket.ai](https://www.claudemarket.ai) | independent | plugins and marketplaces | 3,688 plugins, 1,463 marketplaces (2026-08) | - | stars | -[^claudemarket] |
| [playbooks.com](https://playbooks.com) | unknown | skills, bundles, MCP configs | not stated | `npx playbooks find skill` (unverified) | unknown | unknown[^playbooks] |
| GitHub topics | GitHub | repositories | `agent-skills` 31,849; `claude-skills` 10,917 repos | - | stars | -[^gh-topic-as][^gh-topic-cs] |

aitmpl top downloads: skills frontend-design 49.5K, code-reviewer 32.7K,
senior-frontend 29.5K, ui-ux-pro-max 27.9K, senior-backend 25.4K,
senior-architect 20.7K, skill-creator 17.0K.[^aitmpl]

ClawHub top downloads (OpenClaw, not Claude Code): self-improving-agent 484K,
skill-vetter 277K, self-improving 211K, github 201K, ontology 200K. Downloads
are far higher than reported installs (self-improving-agent: 18.5K
installs).[^clawhub]

## 4. Installers

| Command | Installs | Notes |
|---|---|---|
| `/plugin marketplace add owner/repo`, `/plugin install <p>@<mkt>`, `claude plugin install` | Claude Code plugins | official channel[^cc-discover] |
| `npx skills add <owner/repo> [--skill x]` | skills | cross-agent, Vercel[^skillssh-docs] |
| `gh skill install OWNER/REPO [skill][@ref] --agent claude-code --scope user` | skills | GitHub CLI 2.90+, preview since 2026-04; also search, update, publish[^gh-skill-cli] |
| `npx openskills install <repo>`, `openskills sync` | skills | writes to AGENTS.md for agents without native skills[^openskills] |
| `npx claude-plugins install <id>` | plugins | claude-plugins.dev |
| `npx claude-code-templates ...` | components | aitmpl |
| `npx tessl i ...` | skills | Tessl |
| `clawhub` | skills, plugins | ClawHub |

For flokpit the relevant property is pinning: `gh skill install ...@ref` and
marketplace entries with a `sha` give reproducible installs; `npx skills add`
without a ref follows the default branch.

[^skillssh]: skills.sh leaderboard (page data parsed 2026-10-12)
[^skillssh-docs]: skills.sh docs
[^vercel-blog]: Building a self-driving skills.sh leaderboard (via search summary)
[^claude-plugins]: Claude plugin directory (page data parsed 2026-10-12)
[^cc-discover]: Claude Code - Install and manage plugins
[^cc-anthropic-mkt]: Claude Code - Anthropic's marketplaces
[^rywalker]: Ry Walker - Claude plugin marketplace research (June 2026)
[^claudemarket]: Claude Market ecosystem data
[^skillsmp]: SkillsMP
[^claudemarketplaces]: Claude Marketplaces
[^claude-plugins-dev]: claude-plugins.dev
[^aitmpl]: Claude Code Templates (aitmpl)
[^smithery]: Smithery Skills
[^tessl]: Tessl Skills Registry
[^mcpmarket]: MCP Market Agent Skills
[^playbooks]: Playbooks
[^clawhub]: ClawHub (and /api/v1/skills?sort=downloads)
[^parallel]: Best ClawHub skills (2026-08-18)
[^gh-topic-as]: GitHub topic agent-skills
[^gh-topic-cs]: GitHub topic claude-skills
[^gh-skill-cli]: Manage agent skills with GitHub CLI
[^openskills]: OpenSkills overview
