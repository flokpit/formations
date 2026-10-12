---
type: Comparison
title: Declarative Agent Specifications
description: Whole-agent and multi-agent definition formats (Oracle Agent Spec, AGNTCY OASF, A2A Agent Card, docker-agent, kagent, Microsoft AgentSchema, OpenGAP, Snap Agent Format, CrewAI, ADK and others) compared against the breed and formation features.
tags: [agent-spec, oasf, a2a, docker-agent, kagent, agentschema, opengap, agent-format, open-workflow, formations, aaif]
sources:
  - id: oracle-spec
    resource: https://github.com/oracle/agent-spec
    title: oracle/agent-spec
  - id: oracle-paper
    resource: https://arxiv.org/html/2510.04173v3
    title: Open Agent Specification (Agent Spec) technical report
  - id: oracle-lang
    resource: https://oracle.github.io/agent-spec/development/agentspec/language_spec_nightly.html
    title: Agent Spec language specification (nightly)
  - id: oasf
    resource: https://docs.agntcy.org/oasf/open-agentic-schema-framework/
    title: AGNTCY OASF overview
  - id: oasf-record
    resource: https://docs.agntcy.org/oasf/agent-record-guide/
    title: OASF Agent Record guide
  - id: oasf-modules
    resource: https://schema.oasf.outshift.com/module_categories
    title: OASF module categories (1.1.0)
  - id: a2a-aaif
    resource: https://aaif.io/blog/a2a-joins-aaif
    title: A2A joins AAIF (2026-08-17)
  - id: a2a-spec
    resource: https://a2a-protocol.org/latest/specification/
    title: A2A Protocol Specification v1.0
  - id: docker-agent
    resource: https://docs.docker.com/ai/docker-agent/reference/config/
    title: docker-agent configuration reference
  - id: kagent
    resource: https://github.com/kagent-dev/kagent/tree/main/go/api/v1alpha3
    title: kagent v1alpha3 CRD types
  - id: ark
    resource: https://github.com/mckinsey/agents-at-scale-ark
    title: McKinsey Ark agentic runtime
  - id: agent-sandbox
    resource: https://github.com/kubernetes-sigs/agent-sandbox
    title: kubernetes-sigs/agent-sandbox
  - id: m365-da
    resource: https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/declarative-agent-manifest-1.6
    title: M365 Copilot declarative agent schema 1.6
  - id: maf
    resource: https://learn.microsoft.com/en-us/agent-framework/agents/declarative
    title: Microsoft Agent Framework - Declarative agents
  - id: agentschema
    resource: https://microsoft.github.io/AgentSchema/reference/
    title: Microsoft AgentSchema reference
  - id: letta
    resource: https://github.com/letta-ai/agent-file
    title: Letta Agent File (.af)
  - id: prompty
    resource: https://github.com/microsoft/prompty
    title: Prompty
  - id: dotprompt
    resource: https://github.com/google/dotprompt
    title: Dotprompt
  - id: opengap
    resource: https://github.com/open-gitagent/opengap
    title: OpenGAP (Git Agent Protocol)
  - id: snap
    resource: https://github.com/agent-format/agent-format-schema
    title: Snap Agent Format schema
  - id: lmos
    resource: https://eclipse.dev/lmos/docs/arc/adl/adl_learn/
    title: Eclipse LMOS ADL
  - id: faf
    resource: https://ftp.kaist.ac.kr/ietf/draft-wolfe-faf-agent-01.html
    title: IETF draft FAF Agent Format
  - id: crewai
    resource: https://docs.crewai.com/en/concepts/agents
    title: CrewAI Agents
  - id: adk
    resource: https://adk.dev/agents/config/
    title: Google ADK Agent Config
  - id: cc-subagents
    resource: https://code.claude.com/docs/en/sub-agents
    title: Claude Code - Subagents
  - id: aaif
    resource: https://aaif.io/
    title: Agentic AI Foundation
  - id: owf
    resource: https://github.com/open-workflow-specification/specification
    title: Open Workflow Specification
  - id: autogen
    resource: https://github.com/microsoft/autogen
    title: AutoGen (maintenance mode notice)
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
status: draft
stale_after: 2026-12-12T00:00:00Z
---

# Declarative Agent Specifications

No vendor-neutral, foundation-governed specification covers a whole breed
(identity, model, tools, skills, permissions, limits, lifecycle, spawn rights,
runtime). The foundation-governed specs each cover one slice; the whole-agent
formats are single-vendor. GitHub numbers checked on 2026-10-12.

## 1. Specifications

| Spec | Owner and governance | Status, adoption, licence | What it defines | Multi-agent |
|---|---|---|---|---|
| **Oracle Agent Spec** | Oracle, single vendor | 26.3.1 (2026-09-11), 441 stars, Apache-2.0 or UPL; runtime WayFlow, adapters for LangGraph, AutoGen, CrewAI | components with `id`, `name`, `inputs`, `outputs`; `Agent` (`system_prompt`, `llm_configuration`, `tools`, `toolboxes`, `human_in_the_loop`); LLM configs for OpenAI, vLLM, Ollama, OCI, Gemini; MCP toolboxes; `A2AAgent`, `RemoteAgent`; no skills, budgets or container[^oracle-spec][^oracle-paper] | **strongest**: `Swarm`, `ManagerWorkers`, `Flow` graphs with parallel, map and branch nodes[^oracle-lang] |
| **AGNTCY OASF** | Linux Foundation (LF Projects), started by Cisco | 1.1.0 (2026-07-10), 339 stars, Apache-2.0 | catalogue record: `name`, `version`, `authors`, `domains[]`, `skills[]` (numbered taxonomy, not SKILL.md), `modules[]` (language model, prompt, Agent Skills, MCP, A2A, Agent Spec, observability), `locators[]` (source, container image)[^oasf][^oasf-record][^oasf-modules] | via A2A or Agent Spec modules |
| **A2A Agent Card** | AAIF since 2026-08-17 | v1.0.1, 26k stars, 150+ organisations, Apache-2.0 | public description at `/.well-known/agent-card.json`: `name`, `version`, `supportedInterfaces`, `provider`, `capabilities`, `securitySchemes`, advertised `skills[]`, JWS `signatures`; no model, prompt, tools or limits[^a2a-aaif][^a2a-spec] | protocol for delegation between agents |
| **docker-agent** (was cagent) | Docker Inc. | v1.150.0, schema version 15, 4.4k stars, Apache-2.0; agents distributable as OCI artifacts | `models`, `providers`, `agents`, `mcps`, `toolsets`, `permissions` (allow/deny globs like `shell:cmd=sudo*`), `skills`; per agent `instruction_file`, `toolsets`, `readonly`, `sub_agents`, `handoffs`, `max_iterations`, `max_consecutive_tool_calls`, `hooks`, `harness` (delegate to a coding CLI)[^docker-agent] | `sub_agents` tree plus `handoffs` |
| **kagent v1alpha3** | CNCF (sandbox, per secondary source) | v1.0.0-alpha11, 4k stars, Apache-2.0 | **`AgentTemplate`** (portable behaviour: model ref, system prompt, MCP tools with allowlist and `requireApproval`, sub-agent tools, skills and plugins from immutable OCI, git-commit or S3 sources) separate from **`Harness`** (runtime: `kagent`, `codex`, `claude` or bring-your-own; image, env, substrate) plus `SandboxTemplate`, `ModelConfig`[^kagent] | sub-agent as a tool; A2A |
| McKinsey Ark | McKinsey | v1alpha1 preview, 429 stars, Apache-2.0 | CRDs Agent, Team, Model, Query, Tool, MCPServer, A2AServer[^ark] | `Team`: sequential, graph, selector, round-robin |
| kubernetes-sigs/agent-sandbox | Kubernetes SIG Apps | v1beta1, 4.2k stars | `Sandbox`, `SandboxTemplate`, `SandboxWarmPool`, `SandboxClaim`; gVisor and Kata; runtime isolation only[^agent-sandbox] | - |
| M365 declarative agent | Microsoft, M365 only | schema 1.8 | `instructions` (8k chars), `capabilities[]`, `actions[]`, `worker_agents[]` (preview); no model, limits or container[^m365-da] | preview |
| Microsoft AgentSchema / Agent Framework YAML | Microsoft | AgentSchema 1.0.0-beta.7 (MIT); Agent Framework 14k stars; AutoGen in maintenance mode[^autogen] | `PromptAgent` (model, tools, instructions, schemas), `Workflow`, **`ContainerAgent`** (image, resources, env); tool kinds Function, Mcp, OpenApi, CodeInterpreter, WebSearch[^maf][^agentschema] | `Workflow` (thin) |
| Letta Agent File (.af) | Letta | 1.2k stars, last push 2026-03, no version | serialized stateful agent: model, prompt, memory blocks, history, tools[^letta] | roadmap only |
| Prompty, Dotprompt | Microsoft; Google | 1.3k and 570 stars | single prompt: model, inputs, tools, template[^prompty][^dotprompt] | - |
| **OpenGAP / GitAgent** | open-gitagent (small org) | spec 0.1.0, ~3k stars, MIT | an agent is a repository: `agent.yaml` (model with fallback, skills, tools, sub-agents with delegation, `runtime.max_turns`, `timeout`, `compliance`), `SOUL.md`, `RULES.md`, `DUTIES.md`, `AGENTS.md`, `skills/`, `workflows/`, `hooks/`, `memory/`, recursive `agents/`[^opengap] | `agents/` tree and DAG workflows |
| **Snap Agent Format** | Snap | schema 1.0, 22 stars, quiet since 2026-03 | `action_space` (tools, MCP servers, local and remote agents), `execution_policy` (react, sequential, parallel, loop, ...), **`constraints`**: token, duration, LLM-call, tool-call and delegation-depth limits with a **`tighten_only_invariant`** (a child never exceeds its parent)[^snap] | execution policies |
| Eclipse LMOS ADL | Eclipse Foundation, incubating | alpha; in production at Deutsche Telekom | markdown DSL for behaviour (use cases, steps, fallback, `@tool()` calls); no model, tools or runtime[^lmos] | - |
| IETF draft-wolfe-faf-agent | individual draft | 2026-08, no traction | `.fafa` YAML agent format[^faf] | - |
| CrewAI YAML | CrewAI | 59.6k stars, MIT | `agents.yaml` (role, goal, backstory, llm, tools), `tasks.yaml`; `max_iter`, `max_rpm`, `max_execution_time`, `allow_delegation`[^crewai] | crew: sequential or hierarchical |
| Google ADK Agent Config | Google | experimental, 21.8k stars | `agent_class`, `name`, `model` (Gemini only), `instruction`, `tools`, `sub_agents`[^adk] | `sub_agents` |
| Claude Code subagent | Anthropic, de-facto format | widely copied | `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `isolation`; body is the prompt[^cc-subagents] | Agent tool allowlist |
| **Open Workflow Specification** (was CNCF Serverless Workflow) | CNCF | 1.0.3 (2026-07-31), Apache-2.0 | general workflow DSL; `call: a2a` and `call: mcp` tasks on main (in a release unverified)[^owf] | deterministic workflows |

**AAIF** hosts MCP, goose, AGENTS.md, agentgateway and A2A. It has working
groups on taxonomy, workflows (with role definitions) and identity, but no
agent-definition project.[^aaif]

## 2. Coverage of breed features

Y covered, P partial, N not covered.

| Spec | Instruction | Model | Tools, MCP | SKILL.md | Permissions | Limits | Lifecycle | Spawn, teams | Runtime | Neutral governance |
|---|---|---|---|---|---|---|---|---|---|---|
| Oracle Agent Spec | Y | Y | Y | N | P | P | N | **Y** | N | N |
| AGNTCY OASF | Y (catalogue) | P | P | P | N | N | N | P | P | **Y** |
| A2A Agent Card | Y (public) | N | N | P | P | N | N | P | N | **Y** |
| docker-agent | Y | Y | Y | Y | Y | Y | P | Y | P | N |
| kagent v1alpha3 | Y | Y | Y | Y | P | P | Y | Y | **Y** | P |
| MS AgentSchema | Y | Y | Y | N | N | N | N | P | Y | N |
| OpenGAP | Y | Y | Y | Y | Y | Y | Y | Y | P | N |
| Snap Agent Format | Y | P | Y | Y | Y | **Y** | P | Y | N | N |
| Claude Code subagent | Y | Y | Y | Y | Y | P | P | P | P | N |
| CrewAI | Y | Y | P | N | N | Y | N | Y | N | N |
| Open Workflow Spec | N | N | P | N | N | P | Y | Y | N | **Y** |
| AGENTS.md, Agent Skills, MCP | Y | - | Y (MCP) | Y | - | - | - | - | - | **Y** |

## 3. Assessment

1. **Build on the foundation-governed pieces**: AGENTS.md for the main
   instruction, Agent Skills for skills, MCP for tool servers, and an A2A
   Agent Card when a breed or flock is exposed to other systems.
2. **Keep the breed schema our own and small.** No whole-agent spec is both
   neutral and complete. Oracle Agent Spec is the best export target for
   formations (Swarm, ManagerWorkers, Flow) but is governed by Oracle alone
   and lacks skills, limits and runtime. OASF records fit if breeds are ever
   published in a catalogue.
3. **Patterns worth borrowing:**
   - kagent: split portable behaviour (`AgentTemplate`) from runtime
     (`Harness`), and pin skills to immutable sources (OCI digest, git commit).
   - docker-agent: field vocabulary for `sub_agents`, `handoffs`,
     `permissions`, `max_iterations`, OCI distribution.
   - Snap Agent Format: limits as `constraints` with a tighten-only rule, so a
     spawned agent can never exceed its spawner's limits.
   - Open Workflow Specification for deterministic formations.
4. **Not as canonical format:** M365 manifest (M365 only), ADK config
   (experimental, Gemini only), Letta .af (state snapshots, stale),
   Prompty/Dotprompt (single prompts). OpenGAP is conceptually closest to a
   breed folder but is version 0.1 from a small organisation.

[^oracle-spec]: oracle/agent-spec
[^oracle-paper]: Open Agent Specification (Agent Spec) technical report
[^oracle-lang]: Agent Spec language specification (nightly)
[^oasf]: AGNTCY OASF overview
[^oasf-record]: OASF Agent Record guide
[^oasf-modules]: OASF module categories (1.1.0)
[^a2a-aaif]: A2A joins AAIF (2026-08-17)
[^a2a-spec]: A2A Protocol Specification v1.0
[^docker-agent]: docker-agent configuration reference
[^kagent]: kagent v1alpha3 CRD types
[^ark]: McKinsey Ark agentic runtime
[^agent-sandbox]: kubernetes-sigs/agent-sandbox
[^m365-da]: M365 Copilot declarative agent schema 1.6
[^maf]: Microsoft Agent Framework - Declarative agents
[^agentschema]: Microsoft AgentSchema reference
[^letta]: Letta Agent File (.af)
[^prompty]: Prompty
[^dotprompt]: Dotprompt
[^opengap]: OpenGAP (Git Agent Protocol)
[^snap]: Snap Agent Format schema
[^lmos]: Eclipse LMOS ADL
[^faf]: IETF draft FAF Agent Format
[^crewai]: CrewAI Agents
[^adk]: Google ADK Agent Config
[^cc-subagents]: Claude Code - Subagents
[^aaif]: Agentic AI Foundation
[^owf]: Open Workflow Specification
[^autogen]: AutoGen (maintenance mode notice)
