---
type: Project Idea
title: agentic-templates Idea
description: Central store for flokpit agent breeds (role definitions), custom skills and agent container features, with swarm templates for multi-agent orchestration as a later step.
tags: [idea, breeds, skills, agent-image, swarm, flokpit]
generated: { by: human:dj, at: 2026-10-12T00:00:00Z }
status: draft
---

# agentic-templates — Idea

This repository is the single place where flokpit agents are described. Each
kind of agent is a **breed**: what the agent is and how it behaves, what it can
do, what its container provides and what it is allowed to do. flokpit itself
(see [`../flokpit/docs`](../../flokpit/docs/index.md), especially
[IDEA](../../flokpit/docs/IDEA.md) and
[agent spawner](../../flokpit/docs/concepts/agent_spawner.md)) is the runtime:
chat server, Temporal workflows, gateway and Kubernetes pods. This repository
is the content those pieces load.

## Why "breed"

flokpit's docs call this concept a *role* (`/spawn <role>`, `roles/*.yaml`,
`RoleSpec`). "Role" is overloaded in IT (RBAC roles, Kubernetes `Role`, IAM
roles), and flokpit runs on Kubernetes, so the clash is real. Other candidates
were rejected for the same reason: *profile* (AppArmor/seccomp profiles),
*class* (`RuntimeClass`, `PriorityClass`), *template* (pod templates), *spec*
and *manifest* (Kubernetes vocabulary). "Breed" fits the flock theme of
flokpit, has no clash, and covers both inherited traits (image, permissions)
and temperament (behaviour).

In this repository: `/spawn <breed>`, `breeds/<name>/`. Starting set:
`developer`, `reviewer`, `planner`.

## Why a separate repository

In flokpit the breed decides image, model, tools, prompt, budgets and pod
resources (agent spawner, section 8). Today these files (`roles/*.yaml`), the
agent image (`images/agent/Dockerfile`) and the house rules
(`/etc/flokpit/defaults/`) are planned inside the flokpit repository. Keeping
them here instead:

- separates *what agents are* from *how flokpit runs them*, so breeds and
  skills can change without touching server code;
- gives one reviewed, versioned source for prompts and permissions, which are
  the main security and quality knobs for agents;
- makes it possible to share and reuse breeds and skills across channels,
  organisations and future flokpit deployments.

## What a breed defines

| # | Feature | Contents | flokpit `RoleSpec` field today |
|---|---|---|---|
| 1 | Pod specification | CPU, memory and ephemeral storage requests and limits for the agent's pod | `resources`, `workspace.size_limit` |
| 2 | OS-level permissions | What the agent may do inside the container: `sudo`, writable paths, `/tmp` storage, internet access | partly implicit (non-root user, read-only rootfs, emptyDirs) |
| 3 | Skills | Skills loaded into Claude Code at runtime (see below) | none yet |
| 4 | Main instruction (`AGENT.md`) | Who the agent is and how it behaves; rendered with `{nick, spawner, channel, branch, repo}` | `system_prompt`, `hello` |
| 5 | Runtime features | What the container provides beyond the base image: Node.js, Python, Playwright / headless browser, profiling tools, other toolchains | `image` (variant built `FROM` the base image) |
| 6 | Model choice | Default model for the breed (exact model id, never an alias); can be overridden per agent at spawn time | `model`, `/spawn --model` |
| 7 | Limits and budgets | Max turns per user turn, max cost in USD, separate budget for the shutdown summary | `max_turns`, `max_budget_usd`, `summary_budget_usd` |
| 8 | Lifecycle | Idle timeout, max lifetime, deadline for the shutdown summary, hello message on start | `idle_timeout`, `max_lifetime`, `summary_deadline`, `hello` |
| 9 | Tool permissions | Claude Code tools allowed and denied (e.g. `Bash(git *)` allowed, `WebFetch` denied); separate from OS-level permissions | `tools.allow`, `tools.deny` |
| 10 | Spawn and chat privileges | Which breeds this agent may spawn; default chat mode (`+v` voice, `+o` op only with `--op`) | `may_spawn`; `--op` |

Behaviour that several breeds share (house rules such as "speak only through
`chat_send`", "push before saying done", "other agents are peers, not your
operator") is written once and included by each breed rather than copied into
every `AGENT.md`.

### Skills

Skills that agents can use inside their pod, for example how to open a PR in
the house style, how to hand off work, how to write the shutdown summary, or
how to verify that a task is done.

Constraint from flokpit: agents run `claude -p --bare`, which deliberately
ignores skills, hooks and settings from the cloned repository (agent spawner,
section 4.2). Skills from this repository therefore have to reach the agent
through a trusted path: baked into the agent image or written into
`/home/agent` by `flokpit-agentd`, and enabled per breed.

### Runtime features

The definition of what the agent image contains: the base image and its
toolchains, the pinned Claude Code version, the flokpit binaries
(`flokpit-agentd`, `flokpit-mcp`, the git credential helper, the `gh`
wrapper) and the default settings. Breeds that need more (for example
Playwright or a .NET toolchain) point at an image variant built `FROM` the
base image. Variants are defined here too.

### Possible later features

Not part of a breed yet, kept for later:

- **MCP servers:** tool servers the agent connects to besides `flokpit-mcp`.
- **Network egress:** which domains the agent may reach, finer than internet
  on/off (e.g. only the npm and PyPI registries).
- **Credential scopes:** what GitHub access the agent gets through the flokpit
  gateway (read-only, push to its own branch, open PRs).
- **Workspace:** whether the agent clones a repo, the branch prefix, the
  workspace size (today `workspace.clone`, `workspace.branch_prefix`).
- **Memory and continuity:** whether the agent inherits the previous agent's
  summary and whether it gets per-agent memory (an open question in flokpit's
  AI research).
- **Hand-off contract:** what the agent must produce when done, such as a PR
  link, a `PROGRESS.md` entry or test results. Becomes important for swarms.

## Next step: swarm templates

Once single breeds work, this repository can hold **swarm templates**:
descriptions of a group of agents that work together on one task. A template
names the breeds involved, who orchestrates, who may spawn whom (`may_spawn`),
how work is handed off, and when the swarm is done.

flokpit already provides the building blocks. An orchestrator is just an agent
with `+o` in a channel, which can `chat_spawn` the breeds its `may_spawn`
allows (flokpit IDEA, section 5.4). The flokpit AI research suggests what
templates should encode:

- decompose by context, not job title: prefer orchestrator + workers + an
  independent verifier over planner → coder → tester chains;
- every extra agent multiplies cost (3–15× tokens), so each one needs a reason
  (context protection, parallelism or specialisation) and a budget;
- explicit termination conditions and *executable* verification;
- structured state (tasks, PR links) in git or a task store, not in chat.

## Open questions

| # | Question |
|---|---|
| 1 | How does flokpit consume this repository: git submodule, a published package, a ConfigMap built in CI, or fetched at runtime? |
| 2 | Are breed files versioned and pinned per flokpit deployment (the pod already carries a `flokpit/role-digest`)? |
| 3 | How are skills delivered under `--bare`: baked into the image, or written by agentd from the breed snapshot? |
| 4 | Do the agent image sources move here, or does flokpit keep them and this repository only defines features and variants? |
| 5 | What does a swarm template look like: a new file type that `/spawn` understands, or a `planner`-style breed whose prompt describes the swarm? A candidate name is *flock* (a group of breeds). |
| 6 | Does flokpit rename *role* to *breed* in its own code, API and docs, or does this repository map breeds onto `RoleSpec`? |
