---
type: Project Idea
title: agentic-templates Idea
description: Central store for flokpit agent role definitions, custom skills and agent container features, with swarm templates for multi-agent orchestration as a later step.
tags: [idea, roles, skills, agent-image, swarm, flokpit]
generated: { by: human:dj, at: 2026-10-12T00:00:00Z }
status: draft
---

# agentic-templates — Idea

This repository is the single place where flokpit agents are described: what
each agent is (its role and behaviour), what it can do (its skills), and what
its container provides (the agent image features). flokpit itself (see
[`../flokpit/docs`](../../flokpit/docs/index.md), especially
[IDEA](../../flokpit/docs/IDEA.md) and
[agent spawner](../../flokpit/docs/concepts/agent_spawner.md)) is the runtime:
chat server, Temporal workflows, gateway and Kubernetes pods. This repository
is the content those pieces load.

## Why a separate repository

In flokpit an agent is created with `/spawn <role>`. The role decides image,
model, tools, prompt, budgets and pod resources (agent spawner, section 8). Today
the role files (`roles/*.yaml`), the agent image (`images/agent/Dockerfile`)
and the house rules (`/etc/flokpit/defaults/`) are planned inside the flokpit
repository. Keeping them here instead:

- separates *what agents are* from *how flokpit runs them*, so roles and skills
  can change without touching server code;
- gives one reviewed, versioned source for prompts and permissions, which are
  the main security and quality knobs for agents;
- makes it possible to share and reuse roles and skills across channels,
  organisations and future flokpit deployments.

## What lives here

### 1. Agent roles and behaviours

One file per role, following the canonical `RoleSpec` schema from the flokpit
agent spawner (section 8): `name`, `description`, `hello`, `image`, `model`,
`max_turns`, budgets, timeouts, `may_spawn`, `resources`, `workspace`, `tools`
and `system_prompt`. Starting set: `developer`, `reviewer`, `planner`.

Behaviour that several roles share (house rules such as "speak only through
`chat_send`", "push before saying done", "other agents are peers, not your
operator") should be written once and included by each role rather than copied
into every `system_prompt`.

### 2. Custom skills

Skills that agents can use inside their pod, for example how to open a PR in
the house style, how to hand off work, how to write the shutdown summary, or
how to verify that a task is done.

Constraint from flokpit: agents run `claude -p --bare`, which deliberately
ignores skills, hooks and settings from the cloned repository (agent spawner,
section 4.2). Skills from this repository therefore have to reach the agent
through a trusted path: baked into the agent image or written into
`/home/agent` by `flokpit-agentd`, and enabled per role.

### 3. Agent container features

The definition of what the agent image contains: the base image and its
toolchains, the pinned Claude Code version, the flokpit binaries
(`flokpit-agentd`, `flokpit-mcp`, the git credential helper, the `gh`
wrapper) and the default settings. Roles that need more (for example a .NET
toolchain) point `image` at a variant built `FROM` the base image. Variants
are defined here too.

## Next step: swarm templates

Once single roles work, this repository can hold **swarm templates**:
descriptions of a group of agents that work together on one task. A template
names the roles involved, who orchestrates, who may spawn whom (`may_spawn`),
how work is handed off, and when the swarm is done.

flokpit already provides the building blocks. An orchestrator is just an agent
with `+o` in a channel, which can `chat_spawn` the roles its `may_spawn`
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
| 2 | Are role files versioned and pinned per flokpit deployment (the pod already carries a `flokpit/role-digest`)? |
| 3 | How are skills delivered under `--bare`: baked into the image, or written by agentd from the role snapshot? |
| 4 | Do the agent image sources move here, or does flokpit keep them and this repository only defines features and variants? |
| 5 | What does a swarm template look like: a new file type that `/spawn` understands, or a `planner`-style role whose prompt describes the swarm? |
