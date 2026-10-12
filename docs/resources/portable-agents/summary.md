---
type: Summary
title: Portable Agents Research Summary
description: Which existing standard or convention fits each breed feature independent of the agent vendor, what has no standard, and a proposed vendor-neutral breed layout rendered per agent CLI.
tags: [summary, breeds, formations, portability, agents-md, agent-skills, mcp, devcontainer, agent-sandbox]
sources:
  - id: instructions
    resource: /portable-agents/instructions-and-skills.md
    title: Portable Instructions and Skills
  - id: definitions
    resource: /portable-agents/agent-definitions.md
    title: Custom Agent Definitions Across Vendors
  - id: specs
    resource: /portable-agents/declarative-specs.md
    title: Declarative Agent Specifications
  - id: runtime
    resource: /portable-agents/runtime-and-permissions.md
    title: Portable Runtime, Permissions, MCP, Limits and Hooks
  - id: skills
    resource: /skills/summary.md
    title: Skills Research Summary
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Portable Agents Research Summary

Question: how can every feature of a breed be defined once, independent of
the vendor (Anthropic, OpenAI, Google, GitHub, ...)? Research date
2026-10-12; details and sources on the linked pages.

## Take-aways

1. **No complete vendor-neutral agent standard exists.** The
   foundation-governed standards each cover one slice: AGENTS.md
   (instructions), Agent Skills (skills), MCP (tool servers), A2A (identity
   between agents). All sit in or near the Linux Foundation's Agentic AI
   Foundation.[^instructions][^specs]
2. **Whole-agent formats are single-vendor.** Oracle Agent Spec, docker-agent,
   kagent, Microsoft AgentSchema and OpenGAP each cover most features but are
   governed by one company or a small group.[^specs]
3. **Claude Code's subagent format is the de-facto lingua franca** for custom
   agents: markdown with `name`, `description`, `tools`, `model`
   frontmatter, read directly by Cursor and VS Code Copilot.[^definitions]
4. **Permissions, limits and network egress differ in every CLI**, and only
   some CLIs can enforce them at all. They belong in the pod and the gateway;
   CLI settings are a second layer.[^runtime]
5. **Translators exist.** rulesync renders rules, MCP, subagents, skills,
   hooks and permissions from one source into about 30 tools.[^runtime]

## Breed features and their best portable form

| # | Breed feature | Portable form | Standard status |
|---|---|---|---|
| 1 | Pod specification | Kubernetes resources in a `SandboxTemplate` (agent-sandbox) or the flokpit pod builder | Kubernetes SIG standard[^runtime] |
| 2 | OS-level permissions | pod security context, read-only root filesystem, NetworkPolicy or `SandboxTemplate.networkPolicy`, egress proxy allowlist | Kubernetes; enforced outside the CLI[^runtime] |
| 3 | Skills | Agent Skills (`SKILL.md`), stored once, installed into `~/.agents/skills` and `~/.claude/skills` | open standard, AAIF admission pending[^instructions][^skills] |
| 4 | Main instruction | `AGENTS.md` (core rules under 4,000 characters, total under 32 KiB) | AAIF standard[^instructions] |
| 5 | Runtime features | Dev Container Features baked into the breed image | containers.dev spec; no CLI consumes it as runtime format[^runtime] |
| 6 | Model choice | `model_class` (`frontier`, `balanced`, `fast`) plus `effort`, mapped per vendor; overridable per spawn | no standard; aliases in Claude Code and Gemini CLI[^definitions] |
| 7 | Limits and budgets | `constraints` with a tighten-only rule (Snap Agent Format pattern); turns rendered per CLI; cost and wall-clock enforced by gateway and pod | no standard[^specs][^runtime] |
| 8 | Lifecycle | idle timeout, max lifetime, summary deadline in flokpit's workflow; `SandboxClaim` TTL | flokpit-specific[^runtime] |
| 9 | Tool permissions | `category → glob → allow\|ask\|deny` (rulesync and OpenCode model), rendered per CLI | no standard; rulesync translates[^runtime] |
| 10 | Spawn and chat privileges | `may_spawn` list; flokpit chat modes | flokpit-specific; per-vendor spawn rules differ[^definitions] |
| - | MCP servers (later feature) | MCP Registry `server.json` entries | MCP standard[^runtime] |
| - | Hooks (not a breed feature yet) | Claude-shaped hooks; AAIF Agent Hooks Core proposal | converging[^definitions][^runtime] |
| - | External identity | A2A Agent Card | AAIF standard[^specs] |

## Proposed breed layout

A breed directory written once and rendered per agent CLI:

```
breeds/developer/
  breed.yaml        # pod, OS permissions, model_class, limits, lifecycle,
                    # tool permissions, may_spawn, runtime features, skills, mcp
  AGENTS.md         # main instruction (portable)
  skills/           # Agent Skills, vendored and pinned (or references to skills/)
```

`breed.yaml` is our own small schema. Following the kagent split, it keeps
portable behaviour (instruction, model class, tools, skills, MCP, limits)
apart from runtime (image, Dev Container Features, pod resources, network).
A renderer produces:

- for Claude Code: settings file with `permissions` and `sandbox`, subagent
  or system prompt from `AGENTS.md`, `~/.claude/skills`, `.mcp.json`, CLI
  flags (`--model`, `--max-turns`, `--max-budget-usd`);
- for Codex: `config.toml` (model, `sandbox_mode`, permission profile,
  `[mcp_servers]`), exec-policy rules, `AGENTS.md`, `~/.agents/skills`;
- for other CLIs through rulesync, if it proves reliable;
- for flokpit: the `RoleSpec` it expects today (see open question 6 in
  `docs/IDEA.md`).

Formations are the multi-agent counterpart. Oracle Agent Spec (`Swarm`,
`ManagerWorkers`, `Flow`) and the CNCF Open Workflow Specification are the
best export targets; the formation file itself stays our own.[^specs]

## Open questions

| # | Question |
|---|---|
| 1 | Use rulesync as the renderer, or write a small renderer for the two or three CLIs flokpit will actually run? |
| 2 | Which CLIs besides Claude Code should a breed support first (Codex is the closest in features)? |
| 3 | Should breeds be published as OASF records or A2A Agent Cards for discovery outside flokpit? |
| 4 | How is `model_class` mapped: in the breed renderer, or in flokpit's egress proxy as named model endpoints? |

[^instructions]: Portable Instructions and Skills
[^definitions]: Custom Agent Definitions Across Vendors
[^specs]: Declarative Agent Specifications
[^runtime]: Portable Runtime, Permissions, MCP, Limits and Hooks
[^skills]: Skills Research Summary
