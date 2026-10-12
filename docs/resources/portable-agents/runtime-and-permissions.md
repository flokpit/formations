---
type: Comparison
title: Portable Runtime, Permissions, MCP, Limits and Hooks
description: How runtime features, OS and tool permissions, MCP servers, limits and hooks are expressed in Claude Code, Codex, Gemini CLI, Copilot CLI, OpenCode and goose, which standards exist (Dev Container Features, agent-sandbox, MCP server.json), and which tools translate one definition into many.
tags: [devcontainer, agent-sandbox, kubernetes, permissions, sandbox, network-egress, mcp, hooks, limits, rulesync, ruler]
sources:
  - id: dc-features
    resource: https://containers.dev/implementors/features/
    title: Dev Container Features reference
  - id: dc-dist
    resource: https://containers.dev/implementors/features-distribution/
    title: Dev Container Features distribution (OCI)
  - id: dc-official
    resource: https://github.com/devcontainers/features
    title: devcontainers/features
  - id: cc-devcontainer
    resource: https://code.claude.com/docs/en/devcontainer
    title: Claude Code - Development containers
  - id: cc-selfhosted
    resource: https://code.claude.com/docs/en/self-hosted-environments-configuration
    title: Claude Code - Customize self-hosted environments
  - id: codex-cloud
    resource: https://developers.openai.com/codex/cloud/environments
    title: Codex - Cloud environments
  - id: copilot-env
    resource: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment
    title: Customizing the Copilot coding agent environment
  - id: cursor-env
    resource: https://cursor.com/docs/cloud-agent/setup
    title: Cursor - Cloud environment setup
  - id: ona
    resource: https://ona.com/docs/ona/automations/automations-as-code
    title: Ona - Automations as code
  - id: e2b
    resource: https://e2b.dev/docs/template/migration-v2
    title: E2B - Template v2
  - id: daytona
    resource: https://www.daytona.io/docs/en/declarative-builder
    title: Daytona - Declarative builder
  - id: agent-sandbox
    resource: https://github.com/kubernetes-sigs/agent-sandbox
    title: kubernetes-sigs/agent-sandbox
  - id: cc-settings
    resource: https://code.claude.com/docs/en/settings-reference
    title: Claude Code - Settings reference
  - id: cc-cli
    resource: https://code.claude.com/docs/en/cli-reference
    title: Claude Code - CLI reference
  - id: gemini-sandbox
    resource: https://geminicli.com/docs/cli/sandbox/
    title: Gemini CLI - Sandboxing
  - id: antigravity
    resource: https://docs.flutter.dev/ai/antigravity-cli
    title: Antigravity CLI
  - id: codex-config
    resource: https://learn.chatgpt.com/docs/config-file/config-reference
    title: Codex - Configuration reference
  - id: codex-rules
    resource: https://developers.openai.com/codex/rules
    title: Codex - Rules (execpolicy)
  - id: gemini-config
    resource: https://geminicli.com/docs/reference/configuration
    title: Gemini CLI - Configuration reference
  - id: gemini-policy
    resource: https://geminicli.com/docs/reference/policy-engine/
    title: Gemini CLI - Policy engine
  - id: copilot-cli
    resource: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
    title: Copilot CLI programmatic reference
  - id: copilot-tools
    resource: https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools
    title: Copilot CLI - Allowing tools
  - id: copilot-hooks
    resource: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-hooks-reference
    title: Copilot CLI hooks reference
  - id: copilot-mcp
    resource: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers
    title: Adding MCP servers for Copilot CLI
  - id: opencode-perm
    resource: https://opencode.ai/docs/permissions/
    title: OpenCode - Permissions
  - id: opencode-mcp
    resource: https://opencode.ai/docs/mcp-servers/
    title: OpenCode - MCP servers
  - id: goose
    resource: https://github.com/aaif-goose/goose/tree/main/documentation/docs/guides
    title: goose documentation (permissions, config files, recipes)
  - id: mcp-server-json
    resource: https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md
    title: MCP Registry - server.json reference
  - id: mcp-converter
    resource: https://mcp.directory/tools/mcp-config-converter
    title: MCP Config Converter
  - id: rulesync
    resource: https://github.com/dyoshikawa/rulesync
    title: rulesync
  - id: ruler
    resource: https://github.com/intellectronica/ruler
    title: Ruler
  - id: skills-cli
    resource: https://github.com/vercel-labs/skills
    title: vercel-labs/skills
  - id: agentsync
    resource: https://github.com/dallay/agentsync
    title: AgentSync
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Portable Runtime, Permissions, MCP, Limits and Hooks

These breed features have no shared standard inside the agent CLIs. They have
to be described once and rendered per CLI, and the security-relevant ones are
best enforced at the pod layer, where they do not depend on the CLI.

## 1. Runtime features

**Dev Container Features** are the most portable way to package "Node,
Python, Playwright, profiling tools".[^dc-features]

- `devcontainer-feature.json`: `id`, `version`, `name`, `options` (each
  becomes an environment variable for `install.sh`, which runs as root),
  `containerEnv`, `capAdd`, `mounts`, `dependsOn` (hard, recursive, with
  options), `installsAfter` (soft ordering).
- Published as OCI artifacts (`ghcr.io/<ns>/<id>:1`, tags `1`, `1.2`,
  `1.2.3`, `latest`) with a collection index.[^dc-dist]
- Official features cover node, python, docker-in-docker and more;[^dc-official]
  Anthropic publishes `ghcr.io/anthropics/devcontainer-features/claude-code`.[^cc-devcontainer]
  No official Playwright feature exists; the usual pattern is the node feature
  plus `npx playwright install --with-deps chromium`.

**What agent platforms consume:**

| Platform | Environment definition |
|---|---|
| Claude Code | Dev Container Feature and reference `.devcontainer/` with a firewall script; managed policy in `/etc/claude-code/managed-settings.json`[^cc-devcontainer]; self-hosted runner (beta) with an orchestrator hook designed to spawn Kubernetes Jobs[^cc-selfhosted] |
| Codex cloud | setup and maintenance scripts on `codex-universal`; internet off by default, allowlist presets[^codex-cloud] |
| Copilot coding agent | `.github/workflows/copilot-setup-steps.yml` (Actions job); firewall allowlist[^copilot-env] |
| Cursor cloud agents | `.cursor/environment.json` (`install`, `start`, `terminals`, `build.dockerfile`)[^cursor-env] |
| Ona (ex-Gitpod), DevPod | `devcontainer.json`[^ona] |
| E2B | template SDK from an image or Dockerfile subset[^e2b] |
| Daytona | snapshots from OCI images or a declarative builder; GitHub repository archived[^daytona] |
| Gemini CLI | own sandbox: docker, podman, gVisor (`runsc`), seatbelt profiles, `.gemini/sandbox.Dockerfile`[^gemini-sandbox] |

No agent CLI reads `devcontainer.json` as its own runtime format.

**Kubernetes SIG agent-sandbox** (v1.0.6, 2026-10-08, weekly releases):
`Sandbox` (`agents.x-k8s.io/v1beta1`: `podTemplate`, `volumeClaimTemplates`,
`operatingMode` Running/Suspended, `shutdownPolicy`), `SandboxTemplate` (pod
blueprint plus `networkPolicy` ingress/egress and env injection policy),
`SandboxClaim` (`warmPoolRef`, lifecycle, `ttlSecondsAfterFinished`, `env`),
`SandboxWarmPool`; gVisor or Kata through `runtimeClassName`.[^agent-sandbox]
A breed maps onto a `SandboxTemplate` and a spawned agent onto a
`SandboxClaim`.

## 2. Permissions

No official cross-agent permission standard exists. The CLIs differ:

- **Claude Code:** `permissions.allow`/`ask`/`deny` rules (`Bash(git log *)`,
  `Edit(src/**)`, `WebFetch(domain:x.com)`, `mcp__server__tool`),
  `defaultMode`, `additionalDirectories`; OS sandbox with
  `sandbox.filesystem.allowWrite`/`denyRead` and
  `sandbox.network.allowedDomains`; flags `--allowedTools`,
  `--permission-mode`, `--permission-prompts none`.[^cc-settings][^cc-cli]
- **Codex:** `sandbox_mode` (`read-only`, `workspace-write`,
  `danger-full-access`), `writable_roots`, `network_access`; permission
  profiles with `network.domains."<pattern>" = "allow"|"deny"`;
  `approval_policy`; Starlark exec-policy rules (`prefix_rule(...,
  decision="allow|prompt|forbidden")`, most restrictive wins).[^codex-config][^codex-rules]
- **Gemini CLI:** `tools.core`, `tools.allowed`, `mcp.allowed`; TOML policy
  engine (`toolName`, `commandPrefix`, `decision = allow|deny|ask_user`,
  `priority`); `ask_user` becomes deny when headless.[^gemini-config][^gemini-policy]
  Gemini CLI is being replaced by Antigravity CLI (`agy`) for unpaid tiers
  since 2026-06-18.[^antigravity]
- **Copilot CLI:** `--allow-tool`/`--deny-tool` with `shell(git:*)`,
  `write(...)`, `url(...)`, `<server>(tool)`; `--allow-url`; deny wins.[^copilot-tools][^copilot-cli]
- **OpenCode:** `permission` map: category → glob → `allow|ask|deny`
  (`bash`, `edit`, `webfetch`, `external_directory`, `task`, `skill`), per
  agent; no OS sandbox.[^opencode-perm]
- **goose:** `GOOSE_MODE` (`auto`, `approve`, `smart_approve`, `chat`) and
  per-tool levels; no path, command or domain granularity.[^goose]

### Mapping of abstract permissions

| Abstract permission | Claude Code | Codex | Gemini CLI | Copilot CLI | OpenCode |
|---|---|---|---|---|---|
| write workspace | `Edit(./**)` or `acceptEdits` | `sandbox_mode = "workspace-write"` | `auto_edit` or policy allow on write tools | `--allow-tool write` | `edit: "allow"` |
| extra writable directory | `additionalDirectories`, `sandbox.filesystem.allowWrite` | `writable_roots`, `--add-dir` | sandbox mounts | `--add-dir` | `external_directory` |
| allow shell command | `Bash(npm test *)` | `prefix_rule(["npm","test"], "allow")` | policy `commandPrefix = "npm test"` | `shell(npm test)` | `bash: {"npm test*": "allow"}` |
| deny shell command | deny `Bash(rm -rf *)` | `decision = "forbidden"` | `decision = "deny"` | `--deny-tool 'shell(rm)'` | `"rm *": "deny"` |
| network egress domains | `sandbox.network.allowedDomains` | permission profile `network.domains` | none native | none (cloud agent firewall only) | none |
| web fetch | `WebFetch(domain:...)` | `tools.web_search.allowed_domains` | policy on web tools | `--allow-url` | `webfetch` globs |
| MCP tool | `mcp__github__create_issue` | `enabled_tools` per server | `includeTools`, policy `mcpName` | `github(create_issue)` | `tools: {"github_*": false}` |
| no prompts (headless) | `dontAsk`, `--permission-prompts none` | `approval_policy = "never"` | approval mode yolo; `ask_user` → deny | `--no-ask-user` | `allow` |

Sources: Claude Code,[^cc-settings] Codex,[^codex-config] Gemini
CLI,[^gemini-policy] Copilot CLI,[^copilot-tools] OpenCode.[^opencode-perm]

**Consequence:** only Claude Code and Codex can restrict shell network egress
by domain. Filesystem, network and `sudo` limits belong in the pod
(non-root user, read-only root filesystem, NetworkPolicy or the
`SandboxTemplate.networkPolicy`, egress proxy); CLI settings are a second
layer.

## 3. MCP servers

| Agent | File | Shape |
|---|---|---|
| Claude Code | `.mcp.json`, `--mcp-config` | `mcpServers.<id>: {type, command, args, env, url, headers}` |
| VS Code, Copilot IDE | `.vscode/mcp.json` | `servers.<id>`, plus `inputs` |
| Copilot CLI | `~/.copilot/mcp-config.json` | `mcpServers.<id>: {type: local\|http, command, args, tools}`[^copilot-mcp] |
| Codex | `config.toml` | `[mcp_servers.<id>]` with `command`, `args`, `url`, timeouts, `enabled_tools`, `disabled_tools`, `bearer_token_env_var`[^codex-config] |
| Gemini CLI | `settings.json` | `mcpServers.<id>`: `command`, `url`, `httpUrl`, `timeout` (ms), `trust`, `includeTools`, `excludeTools`[^gemini-config] |
| OpenCode | `opencode.json` | `mcp.<id>: {type: local\|remote, command[], url, environment, enabled, timeout}`[^opencode-mcp] |
| goose | `config.yaml` or recipe | `extensions[]: {type, cmd, args, env_keys, timeout, available_tools}`[^goose] |

The **MCP Registry `server.json`** is the only standard description of a
server: `name` (reverse DNS), `version`, `packages[]` (npm, pypi, oci, ...
with transport, runtime hint, arguments, environment variables marked secret
or required) and `remotes[]` (streamable HTTP or SSE URL, headers).[^mcp-server-json]
No CLI reads it as configuration, but it is a good canonical source to render
from. Web converters exist for the per-CLI formats.[^mcp-converter]

## 4. Limits

| Agent | Turns | Cost or tokens | Timeouts |
|---|---|---|---|
| Claude Code | `--max-turns` | `--max-budget-usd` (client-side estimate, includes subagents) | `MCP_TIMEOUT`[^cc-cli] |
| Codex | none documented | experimental `features.rollout_budget.limit_tokens` | MCP startup and tool timeouts[^codex-config] |
| Gemini CLI | `model.maxSessionTurns` | none | `tools.shell.inactivityTimeout`, MCP `timeout`[^gemini-config] |
| Copilot CLI | none documented | none | cloud agent `timeout-minutes` (max 59)[^copilot-cli] |
| OpenCode | `agent.<name>.steps` | none | MCP `timeout` |
| goose | `GOOSE_MAX_TURNS` (1000), subagents 25, recipe `max_turns` | none | extension `timeout`, recipe retry timeout[^goose] |

Only Claude Code has a native cost cap. Wall-clock limits belong in the pod
(`activeDeadlineSeconds`, `SandboxClaim` TTL) and cost limits in the LLM
gateway (flokpit's egress proxy).

## 5. Hooks

Hooks are converging on Claude Code's shape `hooks.<Event>[]{matcher,
hooks[]{type, command}}`:[^cc-settings]

- **Codex:** same shape and PascalCase events (`PreToolUse`, `PostToolUse`,
  `SessionStart`, `SubagentStop`, `Stop`, ...); command and MCP-tool handlers
  only.[^codex-config]
- **Copilot CLI:** `.github/hooks/*.json`, camelCase events natively,
  PascalCase for Claude-compatible payloads; also reads
  `.claude/settings.json`.[^copilot-hooks]
- **Gemini CLI:** same shape, other event names (`BeforeTool`, `AfterTool`,
  `BeforeAgent`, `SessionStart`, ...), timeouts in milliseconds, exit code 2
  blocks.[^gemini-config]
- **OpenCode:** JavaScript plugins.

The common core is session start and end, pre- and post-tool use, user prompt
submit, stop, subagent stop and pre-compaction. AAIF's Agent Hooks Core
proposal targets the same envelope (see [Agent
Definitions](/portable-agents/agent-definitions.md)).

## 6. Translators

| Tool | Activity | Converts |
|---|---|---|
| **rulesync** | 1.5k stars, v33.0.0 on 2026-10-12 | rules, MCP, commands, subagents, skills, hooks, **permissions** for about 30 tools; canonical `permissions.jsonc` is category → glob → `allow\|ask\|deny`; no Gemini CLI permissions; can also import[^rulesync] |
| **ruler** | 2.9k stars, active | rules (AGENTS.md, CLAUDE.md, ...), MCP (`ruler.toml`), skills, subagents; no permissions or hooks[^ruler] |
| skills CLI (`npx skills`) | 34k stars | Agent Skills into about 80 agents' directories[^skills-cli] |
| agentsync | 67 stars | symlinks instructions, skills, commands; MCP from TOML[^agentsync] |

rulesync is the closest existing "render one breed into vendor files" tool.

[^dc-features]: Dev Container Features reference
[^dc-dist]: Dev Container Features distribution (OCI)
[^dc-official]: devcontainers/features
[^cc-devcontainer]: Claude Code - Development containers
[^cc-selfhosted]: Claude Code - Customize self-hosted environments
[^codex-cloud]: Codex - Cloud environments
[^copilot-env]: Customizing the Copilot coding agent environment
[^cursor-env]: Cursor - Cloud environment setup
[^ona]: Ona - Automations as code
[^e2b]: E2B - Template v2
[^daytona]: Daytona - Declarative builder
[^agent-sandbox]: kubernetes-sigs/agent-sandbox
[^cc-settings]: Claude Code - Settings reference
[^cc-cli]: Claude Code - CLI reference
[^gemini-sandbox]: Gemini CLI - Sandboxing
[^antigravity]: Antigravity CLI
[^codex-config]: Codex - Configuration reference
[^codex-rules]: Codex - Rules (execpolicy)
[^gemini-config]: Gemini CLI - Configuration reference
[^gemini-policy]: Gemini CLI - Policy engine
[^copilot-cli]: Copilot CLI programmatic reference
[^copilot-tools]: Copilot CLI - Allowing tools
[^copilot-hooks]: Copilot CLI hooks reference
[^copilot-mcp]: Adding MCP servers for Copilot CLI
[^opencode-perm]: OpenCode - Permissions
[^opencode-mcp]: OpenCode - MCP servers
[^goose]: goose documentation (permissions, config files, recipes)
[^mcp-server-json]: MCP Registry - server.json reference
[^mcp-converter]: MCP Config Converter
[^rulesync]: rulesync
[^ruler]: Ruler
[^skills-cli]: vercel-labs/skills
[^agentsync]: AgentSync
