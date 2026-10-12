---
type: Reference
title: Community Skill Repositories on GitHub
description: 66 non-Anthropic GitHub repositories that publish Agent Skills or Claude Code plugin marketplaces, sorted by stars, with licence, activity, size, type and notable skills.
tags: [skills, github, community, awesome-list, plugins, marketplace, vendor-skills]
sources:
  - id: gh-api
    resource: https://docs.github.com/en/rest/repos/repos#get-a-repository
    title: GitHub REST API repository metadata (queried 2026-10-12)
  - id: superpowers
    resource: https://github.com/obra/superpowers
    title: obra/superpowers
  - id: mattpocock
    resource: https://github.com/mattpocock/skills
    title: mattpocock/skills
  - id: addy
    resource: https://github.com/addyosmani/agent-skills
    title: addyosmani/agent-skills
  - id: composio
    resource: https://github.com/ComposioHQ/awesome-claude-skills
    title: ComposioHQ/awesome-claude-skills
  - id: awesome-cc
    resource: https://github.com/hesreallyhim/awesome-claude-code
    title: hesreallyhim/awesome-claude-code
  - id: wshobson
    resource: https://github.com/wshobson/agents
    title: wshobson/agents
  - id: awesome-copilot
    resource: https://github.com/github/awesome-copilot
    title: github/awesome-copilot
  - id: voltagent
    resource: https://github.com/VoltAgent/awesome-agent-skills
    title: VoltAgent/awesome-agent-skills
  - id: trailofbits
    resource: https://github.com/trailofbits/skills
    title: trailofbits/skills
  - id: tob-curated
    resource: https://github.com/trailofbits/skills-curated
    title: trailofbits/skills-curated
  - id: openai-skills
    resource: https://github.com/openai/skills
    title: openai/skills
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Community Skill Repositories on GitHub

Star counts, licence, last push and archive status come from the GitHub API on
2026-10-12.[^gh-api] SKILL.md and `plugin.json` counts come from each
repository's git tree and are rough: several large repositories keep one copy
per agent harness, and awesome-lists link out, so their count is 0. "none" in
the licence column means GitHub detected no licence file, so reuse rights are
unclear. Anthropic's own repositories are in
[Official Sources](/skills/official-sources.md); for reference,
anthropics/skills has 180.7k stars.

**Renamed repositories** (the API redirects): VoltAgent/awesome-claude-skills →
`VoltAgent/awesome-agent-skills`; K-Dense-AI/claude-scientific-skills →
`K-Dense-AI/scientific-agent-skills`; jeremylongshore/claude-code-plugins-plus →
`jeremylongshore/tons-of-skills-marketplace`; sickn33/antigravity-awesome-skills
→ `sickn33/agentic-awesome-skills`; stripe/agent-toolkit → `stripe/ai`;
getsentry/sentry-for-claude → `getsentry/sentry-for-ai`.

Type: **AL** awesome-list or directory, **C** multi-domain collection, **SD**
single-domain or vendor pack, **MP** has a Claude Code `marketplace.json`.

## Repositories by stars

| # | Repository | Stars | Licence | Last push | SKILL.md / plugins | Type | Domain and notable skills |
|---|---|---|---|---|---|---|---|
| 1 | [obra/superpowers](https://github.com/obra/superpowers) | 298,151 | MIT | 2026-10-10 | 15 / 7 | C, MP | Development method: brainstorming, writing-plans, executing-plans, TDD, systematic-debugging, subagent-driven-development, using-git-worktrees[^superpowers] |
| 2 | [mattpocock/skills](https://github.com/mattpocock/skills) | 287,804 | MIT | 2026-10-12 | 38 | C | Engineering and productivity: tdd, diagnosing-bugs, improve-codebase-architecture, domain-modeling, to-spec, to-tickets, triage, handoff, grill-me; most installed repository on skills.sh[^mattpocock] |
| 3 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 135,140 | MIT | 2026-10-12 | 13 / 1 | SD, MP | UI/UX design rules, styles and palettes across stacks |
| 4 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 105,549 | MIT | 2026-10-10 | 25 / 3 | C, MP | Engineering practice: spec-driven development, TDD, security hardening, performance, CI/CD, code review[^addy] |
| 5 | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | 76,949 | none | 2026-09-18 | 864 / 1 | AL, C | Largest awesome-list; also hundreds of SaaS automation skills (Composio)[^composio] |
| 6 | [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 64,075 | MIT | 2026-10-11 | ~1 | SD | Researches a topic across Reddit, X, YouTube, HN, Polymarket |
| 7 | [blader/humanizer](https://github.com/blader/humanizer) | 56,163 | MIT | 2026-09-28 | ~1 | SD | Removes signs of AI-generated writing |
| 8 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 55,519 | NOASSERTION | 2026-10-12 | links | AL | The main Claude Code awesome-list: skills, hooks, commands, plugins[^awesome-cc] |
| 9 | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | 54,358 | MIT | 2026-10-08 | 50 / 2 | SD, MP | Marketing: CRO, copywriting, SEO, launch, pricing |
| 10 | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | 49,450 | MIT | 2026-09-15 | 6 / 1 | SD, MP | Obsidian markdown, bases, JSON canvas, CLI |
| 11 | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 48,553 | MIT | 2026-10-12 | 177 / 1 | SD | Science: RDKit, scanpy, PubMed, lab tools |
| 12 | [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | 47,506 | MIT | 2026-10-12 | ~8,359 (duplicated) / 181 | C, MP | Huge aggregated catalogue; quality varies widely |
| 13 | [wshobson/agents](https://github.com/wshobson/agents) | 40,492 | MIT | 2026-10-12 | 184 / 144 | MP | Full-stack, ops, security, data: subagents, commands and skills per plugin (ADRs, API design, STRIDE, WCAG, e2e)[^wshobson] |
| 14 | [github/awesome-copilot](https://github.com/github/awesome-copilot) | 39,954 | MIT | 2026-10-12 | 445 / 104 | C, MP | Copilot-first but SKILL.md format: ADRs, PRDs, implementation plans, Playwright, GitHub issues[^awesome-copilot] |
| 15 | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 35,579 | MIT | 2026-10-12 | links | AL | "1000+" skills, focused on official vendor skills[^voltagent] |
| 16 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | 34,003 | MIT | 2026-10-09 | tooling | tool | `npx skills` installer for any agent (see [Marketplaces](/skills/marketplaces.md)) |
| 17 | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | 32,581 | MIT | 2026-10-12 | 915 / 40 | C, MP | CLI and web catalogue (aitmpl.com): agents, commands, hooks, MCPs, skills |
| 18 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 32,295 | none | 2026-08-28 | 9 / 0 | SD | react-best-practices, web-design-guidelines, composition-patterns, deploy-to-vercel |
| 19 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 28,741 | MIT | 2026-09-14 | 1 | SD | Multi-phase security audit with verified, machine-readable findings |
| 20 | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 28,071 | MIT | 2026-08-30 | 846 / 100 | C, MP | "380+ skills": engineering, product, marketing, C-level, compliance |
| 21 | [openai/skills](https://github.com/openai/skills) | 28,026 | unverified | unverified | 44 | C | Codex catalogue, same format (found by topic search only)[^openai-skills] |
| 22 | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 27,411 | MIT | 2026-10-12 | ~1 | SD | Persistent markdown plan files for long tasks |
| 23 | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | 26,921 | MIT | 2026-10-10 | 69 / 9 | SD, MP | Product management: discovery, strategy, PRDs, launch |
| 24 | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | 26,591 | MIT | 2026-09-10 | 22 | C, MP | Content creation for Chinese and Western social platforms |
| 25 | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | 25,669 | MIT | 2026-10-11 | subagents | AL | 100+ subagents (adjacent, not skills) |
| 26 | [google/skills](https://github.com/google/skills) | 21,214 | Apache-2.0 | 2026-10-12 | 160 / 3 | SD | Google Cloud, Firebase, Gemini product skills |
| 27 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 20,053 | Apache-2.0 | 2026-10-12 | tooling | tool | Scans skills for prompt injection and malicious patterns |
| 28 | [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18,115 | MIT | 2026-10-12 | 24 / 1 | SD, MP | Context compression, memory, multi-agent patterns |
| 29 | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | 15,376 | none | 2026-04-28 | links | AL | Early, widely cited list; quiet since April |
| 30 | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 13,489 | MIT | 2026-10-11 | 98 | SD, MP | ML training, fine-tuning, eval, serving |
| 31 | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills) | 11,844 | MIT | 2026-10-03 | 67 / 1 | C, MP | Role and framework specialists for full-stack work |
| 32 | [huggingface/skills](https://github.com/huggingface/skills) | 11,161 | Apache-2.0 | 2026-10-08 | 26 / 2 | SD, MP | HF CLI, LLM training, datasets, Spaces |
| 33 | [BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills) | 10,242 | none | 2026-09-21 | links | AL | Curated list |
| 34 | [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 8,480 | Apache-2.0 | 2026-08-17 | 16 / 6 | SD, MP | Design-to-code with Stitch MCP |
| 35 | [trailofbits/skills](https://github.com/trailofbits/skills) | 7,494 | CC-BY-SA-4.0 | 2026-10-09 | 85 / 47 | SD, MP | Security: CodeQL, Semgrep, fuzzing, differential review, constant-time analysis[^trailofbits] |
| 36 | [SnailSploit/Claude-Red](https://github.com/SnailSploit/Claude-Red) | 7,450 | MIT | 2026-10-12 | 79 | SD | Offensive security; dual-use |
| 37 | [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) | 7,290 | NOASSERTION | 2026-09-01 | 77 / 1 | SD, MP | Framework-based PM skills |
| 38 | [tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) | 7,051 | NOASSERTION | 2026-10-09 | 92 / 2 | C, MP | Development; claims a validated registry |
| 39 | [remotion-dev/skills](https://github.com/remotion-dev/skills) | 5,073 | none | 2026-10-12 | 12 | SD | Programmatic video with Remotion |
| 40 | [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude) | 3,622 | MIT | 2026-10-12 | 399 / 149 | AL, MP | Hub site plus marketplace |
| 41 | [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) | 3,433 | MIT | 2026-09-13 | 11 | SD | CTF: web, pwn, crypto, reversing, forensics |
| 42 | [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | 3,186 | MIT | 2026-10-01 | 1 / 1 | SD, MP | General Playwright automation |
| 43 | [microsoft/skills](https://github.com/microsoft/skills) | 3,105 | MIT | 2026-10-12 | 210 / 26 | SD, MP | Azure SDKs, Foundry |
| 44 | [cloudflare/skills](https://github.com/cloudflare/skills) | 3,045 | Apache-2.0 | 2026-10-12 | 18 / 4 | SD, MP | Workers, Durable Objects, Agents SDK, wrangler |
| 45 | [jeremylongshore/tons-of-skills-marketplace](https://github.com/jeremylongshore/tons-of-skills-marketplace) | 2,831 | MIT | 2026-10-12 | ~6,123 / 598 | MP | Very large generated set with the `ccpi` package manager; uneven quality |
| 46 | [expo/skills](https://github.com/expo/skills) | 2,791 | MIT | 2026-10-07 | 26 / 7 | SD, MP | Expo Router, EAS, upgrades |
| 47 | [supabase/agent-skills](https://github.com/supabase/agent-skills) | 2,788 | MIT | 2026-10-02 | 2 | SD, MP | Supabase and Postgres best practices |
| 48 | [wondelai/skills](https://github.com/wondelai/skills) | 2,391 | MIT | 2026-09-10 | 196 / 21 | C, MP | Business, marketing and UX frameworks from books |
| 49 | [mrgoonie/claudekit-skills](https://github.com/mrgoonie/claudekit-skills) | 2,228 | none | 2026-04-03 | 45 / 12 | C, MP | better-auth, chrome-devtools, mcp-builder, thinking tools |
| 50 | [glittercowboy/taches-cc-resources](https://github.com/glittercowboy/taches-cc-resources) | 1,981 | MIT | 2026-04-01 | 12 / 1 | C, MP | Meta skills: create skills, create plans |
| 51 | [composio-community/awesome-claude-plugins](https://github.com/composio-community/awesome-claude-plugins) | 1,941 | none | 2026-07-26 | 23 / 25 | AL, MP | Curated plugin list |
| 52 | [stripe/ai](https://github.com/stripe/ai) | 1,913 | MIT | 2026-10-12 | 60 / 5 | SD, MP | stripe-best-practices, upgrade-stripe, Connect |
| 53 | [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) | 1,755 | GPL-3.0 | 2026-08-26 | 204 / 15 | C, MP | Agent quality, spec-driven development, review; GPL |
| 54 | [callstackincubator/agent-skills](https://github.com/callstackincubator/agent-skills) | 1,667 | MIT | 2026-10-08 | 13 / 6 | SD, MP | React Native performance and upgrades |
| 55 | [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | 1,453 | MIT | 2026-10-12 | 118 | C, MP | Development workflow |
| 56 | [quemsah/awesome-claude-plugins](https://github.com/quemsah/awesome-claude-plugins) | 1,427 | none | 2026-10-12 | index | AL | Automated plugin index with adoption metrics |
| 57 | [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace) | 1,295 | MIT | 2026-10-10 | marketplace | MP | superpowers, superpowers-chrome, superpowers-lab; superpowers-skills is archived |
| 58 | [jezweb/claude-skills](https://github.com/jezweb/claude-skills) | 1,059 | MIT | 2026-10-09 | 63 / 11 | C, MP | Cloudflare, React, Tailwind v4 |
| 59 | [getsentry/skills](https://github.com/getsentry/skills) | 1,048 | Apache-2.0 | 2026-10-09 | 28 / 1 | C, MP | find-bugs, code-review, skill-scanner, gha-security-review, iterate-pr |
| 60 | [ccplugins/awesome-claude-code-plugins](https://github.com/ccplugins/awesome-claude-code-plugins) | 970 | Apache-2.0 | 2026-08-12 | links | AL | Plugin list |
| 61 | [awslabs/agent-plugins](https://github.com/awslabs/agent-plugins) | 918 | Apache-2.0 | 2026-10-09 | 34 / 17 | SD, MP | Architect, deploy and run on AWS |
| 62 | [hashicorp/agent-skills](https://github.com/hashicorp/agent-skills) | 893 | MPL-2.0 | 2026-10-05 | 20 / 4 | SD, MP | Terraform style, tests, stacks, provider development |
| 63 | [posit-dev/skills](https://github.com/posit-dev/skills) | 539 | MIT | 2026-10-07 | 28 | SD, MP | R and Python data science, Shiny, Quarto |
| 64 | [trailofbits/skills-curated](https://github.com/trailofbits/skills-curated) | 513 | CC-BY-SA-4.0 | 2026-07-14 | 31 / 29 | MP | Security-reviewed third-party skills[^tob-curated] |
| 65 | [firebase/agent-skills](https://github.com/firebase/agent-skills) | 468 | Apache-2.0 | 2026-10-10 | 13 / 4 | SD, MP | Firebase |
| 66 | [getsentry/sentry-for-ai](https://github.com/getsentry/sentry-for-ai) | 269 | MIT | 2026-10-09 | 34 / 5 | SD, MP | Sentry setup and debugging |

## Smaller or less verified

Found by topic search, trees not inspected: Skill_Seekers (15.1k, turns docs
into skills), gamedev-skills/awesome-gamedev-agent-skills (1.5k),
mohitagw15856/pm-claude-skills (1.4k), dgreenheck/webgpu-claude-skill (1.2k),
vercel-labs/next-skills (1.0k), simonw/claude-skills (0.9k, a copy of Claude's
own `/mnt/skills`, stale since 2025-12), better-auth/skills, mongodb/agent-skills,
neondatabase/agent-skills, prisma/skills. VoltAgent/awesome-openclaw-skills
(53k) and openclaw/clawhub (9.5k) target OpenClaw. gsd-build/get-shit-done
(64k) is archived and a prompting system rather than a skill pack.

## Observations

- **A few repositories dominate.** obra/superpowers and mattpocock/skills each
  have more stars than anthropics/skills; addyosmani/agent-skills, wshobson/agents and
  github/awesome-copilot are the other large general development sources.
- **Vendors ship official packs:** Google, Microsoft, AWS, Cloudflare, Vercel,
  Stripe, Supabase, Expo, HashiCorp, Hugging Face, Sentry, Firebase, Remotion.
  For stack-specific work these are the most trustworthy source.
- **Mega-aggregators** (sickn33, jeremylongshore, ComposioHQ, alirezarezvani)
  re-host thousands of skills of uneven quality and origin, much of it
  generated or duplicated. Use them for discovery, not as a direct source.
- **Licences:** ComposioHQ, travisvn, BehiSecc, vercel-labs/agent-skills,
  remotion-dev/skills and mrgoonie have no licence file; trailofbits is
  CC-BY-SA-4.0 (share-alike); NeoLabHQ is GPL-3.0.
- **Star counts were not audited** for inflation.
- Security risks of third-party skills are covered in
  [Security](/skills/security.md).

[^gh-api]: GitHub REST API repository metadata (queried 2026-10-12)
[^superpowers]: obra/superpowers
[^mattpocock]: mattpocock/skills
[^addy]: addyosmani/agent-skills
[^composio]: ComposioHQ/awesome-claude-skills
[^awesome-cc]: hesreallyhim/awesome-claude-code
[^wshobson]: wshobson/agents
[^awesome-copilot]: github/awesome-copilot
[^voltagent]: VoltAgent/awesome-agent-skills
[^trailofbits]: trailofbits/skills
[^tob-curated]: trailofbits/skills-curated
[^openai-skills]: openai/skills
