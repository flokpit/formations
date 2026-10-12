---
type: Comparison
title: Portable Instructions and Skills
description: AGENTS.md and the per-vendor instruction files, and the Agent Skills load paths, across Claude Code, Codex, Gemini CLI, Copilot, Cursor, OpenCode, Kiro, Amp and goose.
tags: [agents-md, instructions, skills, agent-skills, aaif, portability, claude-code, codex, gemini-cli, copilot, cursor, opencode]
sources:
  - id: agentsmd
    resource: https://agents.md/
    title: AGENTS.md
  - id: aaif
    resource: https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
    title: Linux Foundation announces the formation of the Agentic AI Foundation
  - id: agentsmd-issues
    resource: https://github.com/agentsmd/agents.md/issues
    title: agentsmd/agents.md issues (#9, #135, #149, #184)
  - id: cc-memory
    resource: https://code.claude.com/docs/en/memory
    title: Claude Code - How Claude remembers your project
  - id: codex-agentsmd
    resource: https://learn.chatgpt.com/docs/agent-configuration/agents-md
    title: Codex - AGENTS.md
  - id: gemini-md
    resource: https://geminicli.com/docs/cli/gemini-md/
    title: Gemini CLI - GEMINI.md
  - id: gemini-config
    resource: https://geminicli.com/docs/reference/configuration/
    title: Gemini CLI configuration reference
  - id: copilot-instr
    resource: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
    title: Copilot - Add repository custom instructions
  - id: copilot-review
    resource: https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/copilot-code-review
    title: Copilot code review
  - id: cursor-rules
    resource: https://cursor.com/docs/context/rules
    title: Cursor rules
  - id: opencode-rules
    resource: https://opencode.ai/docs/rules/
    title: OpenCode rules
  - id: kiro-steering
    resource: https://kiro.dev/docs/steering/
    title: Kiro steering
  - id: amp-agentsmd
    resource: https://ampcode.com/docs/customize/agents-md
    title: Amp AGENTS.md
  - id: goose-skills
    resource: https://goose-docs.ai/docs/guides/context-engineering/using-skills
    title: goose - Using skills (via search summary)
  - id: skills-spec
    resource: https://agentskills.io/specification
    title: Agent Skills specification
  - id: aaif-proposals
    resource: https://github.com/aaif/project-proposals/issues/47
    title: AAIF project proposals - Agent Skills (#47), Agent Hooks Core (#53)
  - id: cc-skills
    resource: https://code.claude.com/docs/en/skills
    title: Claude Code - Skills
  - id: codex-skills
    resource: https://learn.chatgpt.com/docs/build-skills
    title: Codex - Build skills
  - id: gemini-skills
    resource: https://geminicli.com/docs/cli/skills/
    title: Gemini CLI - Skills
  - id: vscode-skills
    resource: https://code.visualstudio.com/docs/copilot/customization/agent-skills
    title: VS Code - Agent skills
  - id: cursor-skills
    resource: https://cursor.com/docs/context/skills
    title: Cursor - Skills
  - id: opencode-skills
    resource: https://opencode.ai/docs/skills/
    title: OpenCode - Skills
  - id: amp-skills
    resource: https://ampcode.com/docs/customize/skills
    title: Amp - Skills
  - id: kiro-skills
    resource: https://kiro.dev/docs/skills/
    title: Kiro - Skills
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Portable Instructions and Skills

These are the two breed features with real cross-vendor standards: the main
instruction (AGENTS.md) and skills (Agent Skills). Checked against vendor docs
on 2026-10-12; "unverified" marks secondary or undocumented claims.

## 1. AGENTS.md

- **Format.** Plain markdown, no required fields, no frontmatter: "a README for
  agents". The nearest AGENTS.md in the directory tree wins; explicit chat
  prompts override it. No size limit in the spec.[^agentsmd]
- **Governance.** Stewarded by the Agentic AI Foundation (AAIF), a directed
  fund of the Linux Foundation, announced 2025-12-09 with three founding
  projects: MCP (Anthropic), goose (Block) and AGENTS.md (OpenAI). Platinum
  members: AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft,
  OpenAI.[^aaif]
- **Adopters** listed on agents.md: Codex, Jules, Factory, Aider, goose,
  opencode, Zed, Warp, VS Code, Devin, UiPath, Junie, Amp, Cursor, RooCode,
  Gemini CLI, Kilo Code, Semgrep, GitHub Copilot coding agent, Ona, Windsurf,
  Augment.[^agentsmd]
- **Open proposals, none merged:** a `.agents/` rules directory (#9), sub-agents
  and links to skills, hooks and rules (#149), an "Agent Specification" with a
  `.agent/` tree (#184). A v1.1 codifying precedence was closed unmerged
  (#135).[^agentsmd-issues]

### Which tool reads which file

| Tool | Native file(s) | Reads AGENTS.md | Precedence | Imports | Size limit |
|---|---|---|---|---|---|
| Claude Code | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `~/.claude/CLAUDE.md`, `.claude/rules/*.md` | yes since 2.1.277 (built-in plugin); by default only when no CLAUDE.md exists, `claude-md-and-agents-md` reads both; never `.agents/`[^cc-memory] | ancestors at launch, subdirectories on demand | `@path`, 4 hops | recommends under 200 lines |
| Codex | `AGENTS.md`, `AGENTS.override.md` | native[^codex-agentsmd] | global, then git root down to cwd, deeper wins | not documented | **32 KiB** combined (`project_doc_max_bytes`) |
| Gemini CLI | `GEMINI.md` (global, workspace, just-in-time) | only with `context.fileName: ["AGENTS.md","GEMINI.md"]`[^gemini-md][^gemini-config] | concatenated | `@file.md` | none documented |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | yes, nearest wins; a root CLAUDE.md or GEMINI.md also accepted[^copilot-instr] | personal > repository > organisation | no | **code review reads only the first 4,000 characters**[^copilot-review] |
| Cursor | `.cursor/rules/*.mdc`, user and team rules | yes, including nested[^cursor-rules] | team > project > user | not documented | keep rules under 500 lines |
| OpenCode | `AGENTS.md`, `instructions[]` in opencode.json | native; falls back to CLAUDE.md[^opencode-rules] | | agent reads `@refs` itself | none documented |
| Kiro | `.kiro/steering/*.md` | yes; custom agents load steering only via `resources`[^kiro-steering] | workspace > global | `#[[file:...]]` | none documented |
| Amp | `AGENTS.md` | native; falls back to `AGENT.md`, `CLAUDE.md`[^amp-agentsmd] | cwd up to `$HOME`, subtrees lazily | `@path`, globs | none documented |
| goose | `.goosehints` | yes (unverified, secondary)[^goose-skills] | local > global | - | - |

**For breeds:** AGENTS.md is the portable carrier of the main instruction.
Keep it under 4,000 characters for its core rules if Copilot code review
matters, and well under 32 KiB in total. Claude Code reads it natively only
when no CLAUDE.md exists, which is the normal case in a flokpit pod.

## 2. Agent Skills

- **Spec.** A directory with `SKILL.md`: `name` (64 chars, matches the
  directory), `description` (1024), `license`, `compatibility` (500),
  `metadata`, experimental `allowed-tools`; optional `scripts/`,
  `references/`, `assets/`.[^skills-spec] Details in
  [Official Skill Sources](/skills/official-sources.md).
- **Governance.** AAIF proposal #47 "Agent Skills" (opened 2026-09-24) is
  TC-approved and in governing-board vote; it cites 46 client products. The
  move into AAIF is not final yet.[^aaif-proposals]

### Load paths

| Tool | Project | User | Notes |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | **does not read `.agents/skills`**[^cc-skills][^cc-memory] |
| Codex | `.agents/skills` | `~/.agents/skills`, admin `/etc/codex/skills` | optional `agents/openai.yaml` sidecar[^codex-skills] |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` | `.agents` wins within a tier[^gemini-skills] |
| Copilot (VS Code) | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | CLI and cloud agent paths unverified[^vscode-skills] |
| Cursor | `.agents/skills/`, `.cursor/skills/`, `.claude/skills`, `.codex/skills` | same under `~` | extra fields `paths`, `disable-model-invocation`[^cursor-skills] |
| OpenCode | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | per-agent `permission.skill` globs[^opencode-skills] |
| Amp | `.agents/skills/`, `.claude/skills/` | `~/.agents/skills/`, `~/.config/amp/skills/`, `~/.claude/skills/` | first match by name wins[^amp-skills] |
| Kiro | `.kiro/skills/` | `~/.kiro/skills/` | custom agents opt in via `resources: ["skill://..."]`[^kiro-skills] |
| goose | `.agents/skills/`, `.goose/skills/`, `.claude/skills/` | `~/.agents/skills/` | secondary source[^goose-skills] |

**For breeds:** `.agents/skills/` and `~/.agents/skills/` is the de-facto
shared location, read by Codex, Gemini CLI, Copilot, Cursor, OpenCode, Amp and
goose. Claude Code and Kiro are the exceptions. Store skills once and install
them into `~/.agents/skills/` plus `~/.claude/skills/` (symlink or copy); for
Kiro, generate `skill://` resources.

[^agentsmd]: AGENTS.md
[^aaif]: Linux Foundation announces the formation of the Agentic AI Foundation
[^agentsmd-issues]: agentsmd/agents.md issues (#9, #135, #149, #184)
[^cc-memory]: Claude Code - How Claude remembers your project
[^codex-agentsmd]: Codex - AGENTS.md
[^gemini-md]: Gemini CLI - GEMINI.md
[^gemini-config]: Gemini CLI configuration reference
[^copilot-instr]: Copilot - Add repository custom instructions
[^copilot-review]: Copilot code review
[^cursor-rules]: Cursor rules
[^opencode-rules]: OpenCode rules
[^kiro-steering]: Kiro steering
[^amp-agentsmd]: Amp AGENTS.md
[^goose-skills]: goose - Using skills (via search summary)
[^skills-spec]: Agent Skills specification
[^aaif-proposals]: AAIF project proposals - Agent Skills (#47), Agent Hooks Core (#53)
[^cc-skills]: Claude Code - Skills
[^codex-skills]: Codex - Build skills
[^gemini-skills]: Gemini CLI - Skills
[^vscode-skills]: VS Code - Agent skills
[^cursor-skills]: Cursor - Skills
[^opencode-skills]: OpenCode - Skills
[^amp-skills]: Amp - Skills
[^kiro-skills]: Kiro - Skills
