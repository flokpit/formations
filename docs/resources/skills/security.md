---
type: Analysis
title: Security of Third-Party Skills
description: Studies and incidents on malicious and vulnerable Agent Skills (ClawHavoc, Snyk ToxicSkills, Unit 42, ESET, academic scans), the attack techniques used, available scanners, and the rules this repository follows when adopting a skill.
tags: [skills, security, supply-chain, prompt-injection, malware, clawhub, scanning]
sources:
  - id: liu
    resource: https://arxiv.org/abs/2601.10338
    title: "Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale"
  - id: koi
    resource: https://koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting
    title: Koi Security - ClawHavoc
  - id: thn
    resource: https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html
    title: The Hacker News - 341 malicious ClawHub skills
  - id: snyk-toxic
    resource: https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub
    title: Snyk - ToxicSkills (2026-02-05)
  - id: snyk-landscape
    resource: https://research.snyk.io/blog/agent-skills-threat-landscape/
    title: Snyk - Exploring the Threat Landscape of Agent Skills
  - id: unit42
    resource: https://unit42.paloaltonetworks.com/openclaw-ai-supply-chain-risk/
    title: Unit 42 - OpenClaw AI supply chain risk (2026-06-23)
  - id: cso
    resource: https://www.csoonline.com/article/4129393/openclaw-integrates-virustotal-malware-scanning-as-security-firms-flag-enterprise-risks.html
    title: CSO - OpenClaw integrates VirusTotal
  - id: eset
    resource: https://expertinsights.com/news/1-in-300-ai-agent-skills-is-directly-malicious-eset-research-finds
    title: ESET H1 2026 findings (2026-07-13)
  - id: csa-ciso
    resource: https://cloudsecurityalliance.org/articles/5-claude-agent-skills-risks-every-ciso-should-know
    title: CSA - 5 Claude Agent Skills Risks Every CISO Should Know
  - id: csa-briefing
    resource: https://labs.cloudsecurityalliance.org/research/alt-ciso-briefing-2026-07-06/
    title: CSA briefing (SkillCloak)
  - id: skillsdirectory
    resource: https://skillsdirectory.com/blog/claude-skills-security-report
    title: Skills Directory - Claude skills security report (vendor)
  - id: skillssh-docs
    resource: https://www.skills.sh/docs
    title: skills.sh docs
  - id: skillspector
    resource: https://github.com/NVIDIA/SkillSpector
    title: NVIDIA/SkillSpector
  - id: tob-curated
    resource: https://github.com/trailofbits/skills-curated
    title: trailofbits/skills-curated
  - id: sentry-skills
    resource: https://github.com/getsentry/skills
    title: getsentry/skills (skill-scanner)
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Security of Third-Party Skills

A skill is instructions plus optional scripts that run with the agent's full
permissions. Installed skills land silently in `~/.claude/skills` and inherit
everything the agent may do.[^csa-ciso] In a flokpit pod that means the
breed's tools, the repository checkout and the gateway token.

## Findings

| Date | Who | Finding |
|---|---|---|
| 2026-01/02 | Koi Security, "ClawHavoc" | 341 of 2,857 ClawHub skills malicious, mostly delivering Atomic Stealer on macOS through a fake "Prerequisites" install step and typosquatted names; later raised to 824[^koi][^thn] |
| 2026-02-05 | Snyk, "ToxicSkills" | 3,984 skills (all of ClawHub plus the skills.sh top 100): 13.4% critical issues, 36.8% any flaw, 76 confirmed malicious payloads; the skills.sh top 100 had negligible critical findings[^snyk-toxic][^snyk-landscape] |
| 2026-02 | OpenClaw | VirusTotal scanning added to ClawHub: benign auto-approved, suspicious warned, malicious blocked, daily rescans[^cso] |
| 2026 | Liu et al. (arXiv 2601.10338) | 31,132 skills analysed: 26.1% with at least one vulnerability; data exfiltration 13.3%, privilege escalation 11.8%; 5.2% high-severity patterns suggesting intent; skills with scripts 2.12× more likely to be vulnerable[^liu] |
| 2026-06-23 | Palo Alto Unit 42 | 5 evasive malicious ClawHub skills still unblocked: base64 curl-pipe-bash droppers, payload swapping on paste sites, cron auto-updaters, Telegram exfiltration of crypto keys, 22 MB README padding to exceed scanner size limits, runtime affiliate injection[^unit42] |
| 2026-07 | HKUST "SkillCloak" (via CSA) | a packing technique evaded all 8 tested marketplace scanners over 90% of the time (unverified secondary source)[^csa-briefing] |
| 2026-07-13 | ESET H1 2026 report | ~900K skills analysed, ~25K suspicious, 3,000+ directly malicious (about 1 in 300)[^eset] |
| 2026 | Skills Directory (vendor) | 103,619 skills scanned, 3.8% with a critical-capability finding[^skillsdirectory] |

Most confirmed malware sits in open registries without review (ClawHub,
aggregators). Curated sources (Anthropic, vendor packs, the skills.sh top
entries) scored far better, but no registry guarantees safety; skills.sh says
so explicitly.[^skillssh-docs]

## Attack techniques to check for

- Install instructions that download and run a binary ("mandatory setup",
  `curl ... | bash`, base64 blobs).
- Scripts that read credentials, tokens or keys, or post data to chat
  services, paste sites or unknown hosts.
- Prompt injection in SKILL.md or reference files ("ignore previous
  instructions", hidden text, instructions aimed at the agent rather than the
  task).
- Self-updating skills (cron jobs, fetch-latest-at-runtime) and skills that
  fetch remote instructions on each run.
- Typosquatted names and clones of well-known repositories (see the
  `*/superpowers` clones in [Marketplaces](/skills/marketplaces.md)).
- Oversized files meant to exceed scanner limits.

## Tools

- `uvx mcp-scan@latest --skills` (Snyk).[^snyk-toxic]
- [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector): prompt
  injection and malicious pattern scanner.[^skillspector]
- `skill-scanner` skill in getsentry/skills.[^sentry-skills]
- [trailofbits/skills-curated](https://github.com/trailofbits/skills-curated):
  security-reviewed marketplace of third-party skills.[^tob-curated]

Scanners help but can be evaded, so they do not replace reading the skill.

## Rules for agentic-templates

1. Prefer first-party (Anthropic) and vendor-official packs; treat
   aggregators as discovery only.
2. Vendor every adopted skill into this repository at a pinned commit, with
   its licence and source URL; never install from a registry at pod runtime.
3. Read every file of a skill before adopting it, run a scanner, and record
   the review (who, when, commit).
4. Prefer instruction-only skills; scripts need a reason, and their runtime
   needs go into the breed's runtime features.
5. A skill may not widen a breed's tool permissions or network egress; the
   breed's `tools.allow`/`tools.deny` stay authoritative.
6. Re-review on every update of the pinned commit.

[^liu]: Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale
[^koi]: Koi Security - ClawHavoc
[^thn]: The Hacker News - 341 malicious ClawHub skills
[^snyk-toxic]: Snyk - ToxicSkills (2026-02-05)
[^snyk-landscape]: Snyk - Exploring the Threat Landscape of Agent Skills
[^unit42]: Unit 42 - OpenClaw AI supply chain risk (2026-06-23)
[^cso]: CSO - OpenClaw integrates VirusTotal
[^eset]: ESET H1 2026 findings (2026-07-13)
[^csa-ciso]: CSA - 5 Claude Agent Skills Risks Every CISO Should Know
[^csa-briefing]: CSA briefing (SkillCloak)
[^skillsdirectory]: Skills Directory - Claude skills security report (vendor)
[^skillssh-docs]: skills.sh docs
[^skillspector]: NVIDIA/SkillSpector
[^tob-curated]: trailofbits/skills-curated
[^sentry-skills]: getsentry/skills (skill-scanner)
