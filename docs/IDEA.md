---
type: Project Idea
title: formations Idea
description: Central store for flokpit agent breeds (role definitions), custom skills and agent container features, with formations (predefined multi-agent swarms) as a later step.
tags: [idea, breeds, skills, agent-image, formations, swarm, flokpit]
generated: { by: human:dj, at: 2026-10-12T00:00:00Z }
status: draft
---

# formations — Idea

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

Research on public skills, their usage, fit per breed and security risks:
[Skills research](resources/skills/summary.md).

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
  link, a `PROGRESS.md` entry or test results. Formations (below) define it
  per flock member.

## Next step: formations

Once single breeds work, this repository holds **formations**: predefined
swarms that orchestrate a varying number of agents of different breeds and
define how they work together on one task.

### Naming

| Term | Meaning | Why |
|---|---|---|
| **Formation** | The predefined template: which breeds, how many, who leads, how they hand off work, when they are done | Birds flying in formation follow a fixed shape and fixed rules; the formation is the *plan*, not the birds |
| **Flock** | A running instance of a formation in a channel: the actual agents spawned from it | Matches the flokpit name; "spawn a formation, get a flock" |
| **Lead** | The agent that orchestrates the flock (holds `+o`, spawns and kills members) | In a V-formation one bird leads and the others follow its line |

Rejected alternatives: *swarm* (generic, no flock theme), *murmuration*
(evocative but long and hard to spell), *skein* (obscure), *flock* for the
template (then the running group has no name). This keeps the flock vocabulary
consistent: breeds describe single agents, formations describe groups.

Usage: `/fly <formation> [--repo url] [--task "..."]` or
`/spawn --formation <formation>`; files live in `formations/<name>.yaml`.

### What a formation defines

| # | Feature | Contents |
|---|---|---|
| 1 | Lead | The breed that orchestrates. flokpit already allows this: an orchestrator is an agent with `+o` in the channel that can `chat_spawn` the breeds its `may_spawn` lists (flokpit IDEA, section 5.4). The formation grants `--op` to the lead only |
| 2 | Members | The breeds in the flock, each with `min` and `max` count (e.g. 1 to 4 developers), whether they start with the flock or are spawned on demand by the lead, and per-member overrides that may only narrow the breed (model, budget, tools) |
| 3 | Spawn tree | Who may spawn whom inside the flock. Generated into the members' `may_spawn`; no member may widen it |
| 4 | Work split | How the lead decomposes the task: by context (one developer per module or issue), not by job title. The flokpit AI research recommends orchestrator + workers + an independent verifier over planner → coder → tester chains |
| 5 | Hand-off contract | What each member must deliver and in what form: a branch, a PR link, a `DONE` message with a link, test results. Uses flokpit message intents (`REQUEST`, `INFORM`, `QUESTION`, `DONE`, `BLOCKED`) |
| 6 | Shared state | Where structured state lives: GitHub issues, a task file such as `PROGRESS.md`, PR list. Chat is for coordination, not the system of record |
| 7 | Verification gate | Who decides that work is done and how: a reviewer or ui-tester breed, CI must be green, executable checks. The verifier must not be the author |
| 8 | Termination | When the flock stops: all tasks verified, a human says stop, flock budget or lifetime reached, or too many rounds without progress. The lead posts a flock summary and kills members |
| 9 | Flock budget and limits | A total budget and max lifetime for the whole flock on top of each breed's own limits; max concurrent agents (the channel `M` mode); agent-turn budget between human messages (flokpit's channel `TURN_BUDGET`) |
| 10 | Channel setup | Whether the flock gets its own channel, its topic and modes, and which humans are ops |
| 11 | Escalation | When the lead must ask a human (intent `QUESTION`) instead of deciding: merges to main, scope changes, budget extensions, repeated failures |

### Example

```yaml
# formations/feature-team.yaml
name: feature-team
description: Implements a feature across several modules, reviewed and UI-tested before it is reported done.
lead: software-architect
members:
  - breed: developer
    count: { min: 1, max: 4 }
    start: on_demand          # spawned by the lead, one per module or issue
  - breed: reviewer
    count: { min: 1, max: 1 }
    start: with_flock
  - breed: ui-tester
    count: { min: 0, max: 1 }
    start: on_demand
spawn_tree:
  software-architect: [developer, reviewer, ui-tester]
handoff:
  developer: "DONE with a PR link; tests pass locally"
  reviewer: "DONE with approve or change requests on the PR"
  ui-tester: "DONE with a Playwright report; BLOCKED with screenshots on failure"
state: github-issues           # one issue per work item, linked PRs
verification:
  required: [reviewer, ci-green]
  optional: [ui-tester]
termination:
  - all_items_verified
  - human_stop
  - no_progress_rounds: 3
limits:
  max_agents: 6
  max_lifetime: 8h
  max_budget_usd: 0             # 0 = no cap, as for breeds
escalate_to_human:
  - merge_to_default_branch
  - scope_change
  - budget_extension
```

### Common shapes

| Shape | Lead | Members | Use |
|---|---|---|---|
| Feature team | software-architect | developers (on demand), reviewer, ui-tester | Larger features split across modules |
| Bug sweep | planner | developers (fan-out, one per issue), reviewer | Many independent small issues |
| Review board | reviewer | 2 to 3 reviewers with different focus (security, architecture, tests) | Independent reviews of one large PR |
| Product discovery | project-manager | software-architect, ui-tester | PRD, issue breakdown and acceptance tests before any code |

### Guidelines from flokpit research

- Every extra agent multiplies cost (3–15× tokens), so each member needs a
  reason (context protection, parallelism or specialisation) and a limit.
- Most multi-agent failures are design failures: the formation file is where
  breed specs, hand-offs, termination conditions and executable verification
  are written down.
- Messages from other flock members are from peers, not the operator. Only the
  formation and the humans in the channel set the rules.

## Open questions

| # | Question |
|---|---|
| 1 | How does flokpit consume this repository: git submodule, a published package, a ConfigMap built in CI, or fetched at runtime? |
| 2 | Are breed files versioned and pinned per flokpit deployment (the pod already carries a `flokpit/role-digest`)? |
| 3 | How are skills delivered under `--bare`: baked into the image, or written by agentd from the breed snapshot? |
| 4 | Do the agent image sources move here, or does flokpit keep them and this repository only defines features and variants? |
| 5 | Is a formation enforced by flokpit (a new file type that the server reads, generating `may_spawn` and limits), or only described in the lead's `AGENT.md`? Enforcement is safer; prompt-only is faster to try |
| 6 | Does flokpit rename *role* to *breed* in its own code, API and docs, or does this repository map breeds onto `RoleSpec`? |
| 7 | Does a flock need its own Temporal workflow (flock budget, termination), or is the lead agent's workflow enough? |
