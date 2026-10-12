---
type: Comparison
title: Custom Agent Definitions Across Vendors
description: Field-by-field comparison of custom agent and subagent files in Claude Code, Codex, Copilot, Gemini CLI, Cursor, OpenCode, Kiro, goose and Amp, the state of portable agent standards, and how to express model choice without vendor ids.
tags: [subagents, custom-agents, model-choice, portability, rulesync, agent-plugins, litellm]
sources:
  - id: cc-subagents
    resource: https://code.claude.com/docs/en/sub-agents
    title: Claude Code - Subagents
  - id: codex-subagents
    resource: https://learn.chatgpt.com/docs/agent-configuration/subagents.md
    title: Codex - Subagents
  - id: copilot-agents
    resource: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents
    title: Copilot - Create custom agents
  - id: vscode-agents
    resource: https://code.visualstudio.com/docs/copilot/customization/custom-agents
    title: VS Code - Custom agents
  - id: gemini-subagents
    resource: https://geminicli.com/docs/core/subagents/
    title: Gemini CLI - Subagents
  - id: cursor-subagents
    resource: https://cursor.com/docs/context/subagents
    title: Cursor - Subagents
  - id: opencode-agents
    resource: https://opencode.ai/docs/agents/
    title: OpenCode - Agents
  - id: kiro-agents
    resource: https://kiro.dev/docs/custom-agents/configuration-reference/
    title: Kiro - Custom agent configuration reference
  - id: amp-plugins
    resource: https://ampcode.com/docs/customize/plugins
    title: Amp - Plugins, modes and models
  - id: goose-recipes
    resource: https://goose-docs.ai/docs/guides/recipes/recipe-reference
    title: goose - Recipe reference
  - id: agent-plugins
    resource: https://agent-plugins.org/specification
    title: Agent Plugins specification
  - id: aaif-proposals
    resource: https://github.com/aaif/project-proposals/issues/47
    title: AAIF project proposals - Agent Skills (#47), Agent Hooks Core (#53)
  - id: agentsmd-issues
    resource: https://github.com/agentsmd/agents.md/issues
    title: agentsmd/agents.md issues (#149, #184)
  - id: opengap
    resource: https://github.com/open-gitagent/opengap
    title: OpenGAP (GitAgent)
  - id: adp
    resource: https://community.openai.com/t/agent-definition-protocol-adp-esp-a-portable-standard-for-cross-framework-ai-agents/1373415
    title: Agent Definition Protocol (ADP)
  - id: rulesync
    resource: https://github.com/dyoshikawa/rulesync
    title: rulesync
  - id: cc-models
    resource: https://code.claude.com/docs/en/model-config
    title: Claude Code - Model configuration
  - id: codex-config
    resource: https://learn.chatgpt.com/docs/config-file/config-reference
    title: Codex config reference
  - id: gemini-config
    resource: https://geminicli.com/docs/reference/configuration/
    title: Gemini CLI configuration reference
  - id: opencode-models
    resource: https://opencode.ai/docs/models/
    title: OpenCode - Models
  - id: goose-multimodel
    resource: https://goose-docs.ai/docs/guides/multi-model/
    title: goose - Multi-model
  - id: litellm
    resource: https://docs.litellm.ai/docs/proxy/configs
    title: LiteLLM proxy config
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Custom Agent Definitions Across Vendors

A breed is closest to what the coding agents call a *custom agent* or
*subagent*: a named prompt with model, tools and limits. Every vendor has one;
none share a standard yet.

## 1. Locations and formats

| Tool | Location | Format |
|---|---|---|
| Claude Code | `.claude/agents/*.md`, `~/.claude/agents/`, `--agents` JSON, plugins | markdown, YAML frontmatter, body is the prompt[^cc-subagents] |
| Codex | `.codex/agents/*.toml`, `~/.codex/agents/` | TOML, a config layer over the parent session[^codex-subagents] |
| GitHub Copilot | `.github/agents/*.agent.md`; org-wide in `.github` repo; VS Code also reads `.claude/agents/` | markdown, frontmatter[^copilot-agents][^vscode-agents] |
| Gemini CLI | `.gemini/agents/*.md`, `~/.gemini/agents/` | markdown, frontmatter[^gemini-subagents] |
| Cursor | `.cursor/agents/`, plus `.claude/agents/` and `.codex/agents/` for compatibility | markdown, frontmatter[^cursor-subagents] |
| OpenCode | `.opencode/agents/*.md` or `"agent"` in opencode.json | markdown or JSON[^opencode-agents] |
| Kiro | `.kiro/agents/*.json` | JSON (markdown also accepted)[^kiro-agents] |
| goose | recipe files | YAML recipe[^goose-recipes] |
| Amp | `.amp/plugins/` | TypeScript (`amp.createAgent()`), no declarative file[^amp-plugins] |

## 2. Field comparison

| Breed feature | Claude Code | Codex | Copilot | Gemini CLI | OpenCode | Kiro | goose |
|---|---|---|---|---|---|---|---|
| name, description | `name`, `description` | `name`, `description` | `name`, `description` | `name`, `description` | filename, `description` | `name`, `description` | `title`, `description` |
| main instruction | body | `developer_instructions` | body (max 30,000 chars) | body | body or `prompt` | `prompt` | `instructions` |
| model | `model` (alias or id), `effort` | `model`, `model_reasoning_effort` | `model`, ordered fallback list in VS Code | `model`, `temperature` | `provider/model`, `variant` | `model` | `settings.goose_model` |
| tools allow | `tools` | none (sandbox and MCP `enabled_tools`) | `tools` (aliases `read`, `edit`, `execute`, `web`, ...) | `tools` | `permission` (allow/ask/deny, globs) | `tools`, `permissions` | `extensions[].available_tools` |
| tools deny | `disallowedTools` | MCP `disabled_tools` | - | - | `permission: deny` | `permissions` deny | - |
| permission mode | `permissionMode` | `sandbox_mode` | - | - | `permission.*` | `permissions` | global `GOOSE_MODE` |
| MCP servers | `mcpServers` | `[mcp_servers.<id>]` | `mcp-servers` (cloud agent) | `mcpServers` | global config | `mcpServers` | `extensions` |
| skills | `skills` (preloaded) | `[[skills.config]]` | - | - | `permission.skill` | `resources: ["skill://..."]` | - |
| limits | `maxTurns` | thread caps under `[agents]` | - | `max_turns` (30), `timeout_mins` (10) | `steps` | - | `settings.max_turns` |
| spawn rights | `tools: Agent(a, b)`; depth 3 by default | built-in roles, `max_concurrent_threads_per_session` | `agents:` allowlist, `handoffs[]` (VS Code only) | subagents cannot spawn | `permission.task` globs | `toolsSettings.subagent.availableAgents` | `sub_recipes[]` |
| hooks | `hooks` | - | `hooks` (VS Code preview) | - | - | `hooks[]` | - |

Sources for each column: Claude Code,[^cc-subagents] Codex,[^codex-subagents]
Copilot,[^copilot-agents][^vscode-agents] Gemini CLI,[^gemini-subagents]
OpenCode,[^opencode-agents] Kiro,[^kiro-agents] goose.[^goose-recipes]

**De-facto convergence:** "markdown body plus YAML frontmatter with `name`,
`description`, `tools`, `model`" is shared by Claude Code, Copilot, Gemini CLI,
Cursor and OpenCode, and Cursor and VS Code read `.claude/agents/` directly.
Claude Code's subagent format is the closest thing to a lingua franca. Codex
(TOML), Kiro (JSON), goose (YAML recipe) and Amp (code) diverge.

## 3. Portable standards: state on 2026-10-12

No adopted cross-vendor standard for agent definitions exists.

| Effort | Status | Scope |
|---|---|---|
| Agent Plugins 1.0.0 (2026-08-06) | published | `plugin.json`, `skills/`, `mcp.json`; **explicitly excludes agents, hooks, commands, rules** as too client-specific; client extensions in reverse-domain directories[^agent-plugins] |
| AAIF | no agent-definition project | Agent Skills (#47) near acceptance; Agent Hooks Core v0.1 (#53), vendor-neutral hook envelopes with codecs for Claude Code, Codex, Cursor, Gemini, OpenCode, under review[^aaif-proposals] |
| agents.md #149, #184 | open proposals | sub-agents and an `.agent/` tree[^agentsmd-issues] |
| OpenGAP / GitAgent | third-party, ~3k stars | `agent.yaml` (model, skills, tools, compliance) plus `SOUL.md`, `RULES.md`, `DUTIES.md`, `AGENTS.md`, recursive `agents/`; exporters for Claude Code, OpenAI Agents SDK, CrewAI, ADK, LangChain[^opengap] |
| Agent Definition Protocol | single-author draft | manifest plus OCI packaging, no adoption[^adp] |
| rulesync | converter, ~1.5k stars, active | one source → rules, MCP, subagents, skills, hooks and permissions for about 30 tools[^rulesync] |

## 4. Model choice without vendor ids

| Tool | How models are named |
|---|---|
| Claude Code | aliases `fable`, `opus`, `sonnet`, `haiku`, `best`, `inherit`, remapped per provider via `ANTHROPIC_DEFAULT_*_MODEL`; `fallbackModel`; `availableModels` allowlist[^cc-models] |
| Codex | literal ids plus `model_reasoning_effort`; `model_providers` for other endpoints; profiles[^codex-config] |
| Gemini CLI | tier aliases `pro`, `flash`, `flash-lite`, `auto`; custom aliases in `modelConfigs`[^gemini-config] |
| OpenCode | `provider/model-id` via models.dev, per-model `variants`; subagents inherit[^opencode-models] |
| goose | `GOOSE_PROVIDER` / `GOOSE_MODEL`, per recipe and per subagent[^goose-multimodel] |
| Amp | modes `low`, `medium`, `high`, `ultra` bundle model, effort and tools[^amp-plugins] |
| LiteLLM proxy | client-facing alias (`model_name`) mapped to `provider/model`, with load-balancing and fallbacks; works with Claude Code, Codex and OpenCode through custom endpoints[^litellm] |

**For breeds:** a `model_class` (`frontier`, `balanced`, `fast`) plus an
optional `effort`, mapped per vendor at render time: `frontier` → Claude
`opus`, Gemini `pro`, Codex an explicit id with `model_reasoning_effort =
"high"`. The breed's default stays overridable per spawn, as flokpit already
allows with `/spawn --model`. A LiteLLM-style proxy would make the class names
real endpoints, but flokpit's egress proxy already sits in that position.

[^cc-subagents]: Claude Code - Subagents
[^codex-subagents]: Codex - Subagents
[^copilot-agents]: Copilot - Create custom agents
[^vscode-agents]: VS Code - Custom agents
[^gemini-subagents]: Gemini CLI - Subagents
[^cursor-subagents]: Cursor - Subagents
[^opencode-agents]: OpenCode - Agents
[^kiro-agents]: Kiro - Custom agent configuration reference
[^amp-plugins]: Amp - Plugins, modes and models
[^goose-recipes]: goose - Recipe reference
[^agent-plugins]: Agent Plugins specification
[^aaif-proposals]: AAIF project proposals - Agent Skills (#47), Agent Hooks Core (#53)
[^agentsmd-issues]: agentsmd/agents.md issues (#149, #184)
[^opengap]: OpenGAP (GitAgent)
[^adp]: Agent Definition Protocol (ADP)
[^rulesync]: rulesync
[^cc-models]: Claude Code - Model configuration
[^codex-config]: Codex config reference
[^gemini-config]: Gemini CLI configuration reference
[^opencode-models]: OpenCode - Models
[^goose-multimodel]: goose - Multi-model
[^litellm]: LiteLLM proxy config
