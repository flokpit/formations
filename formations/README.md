# Formations

One YAML file per formation. A formation is a predefined swarm: which
[breeds](../breeds/README.md) take part, how many, who leads, how work is
split and handed off, who verifies, and when the flock stops. A running
formation is a **flock**; its orchestrating agent is the **lead**. Concept:
`docs/IDEA.md`, section "Next step: formations".

All formations are **proposals** (`status: proposal`). Nothing in flokpit
reads them yet; until it does, the lead's breed instructions plus the rendered
formation text are what make the flock behave.

| Formation | Lead | Members | Shape | Use |
|---|---|---|---|---|
| [feature-team](feature-team.yaml) | software-architect | developers (1-4), reviewer, ui-tester (optional) | orchestrator, workers, independent verifier | a feature that spans several modules |
| [bug-sweep](bug-sweep.yaml) | planner | developers (1-5), reviewer | fan-out, independent verifier | many small, independent issues |
| [product-discovery](product-discovery.yaml) | project-manager | software-architect, ui-tester, planner (optional) | discovery before any code | turn an idea into a spec, an architecture sketch, acceptance tests and a backlog |

## Schema (`formations/v1alpha1`)

Machine-readable: [`specs/formation.schema.json`](../specs/formation.schema.json).
Validate with `uv run scripts/validate.py`.

| Section | Formation feature | Fields |
|---|---|---|
| `name`, `description`, `status`, `shape` | identity | name `^[a-z][a-z0-9-]{0,31}$` |
| `lead` | 1. lead | `breed`, `op` (lead gets `+o` in the flock channel), `overrides` |
| `members` | 2. members | list of `{breed, count: {min, max}, start: with_flock \| on_demand, overrides}` |
| `spawn_tree` | 3. spawn tree | breed → breeds it may spawn inside the flock; omitted breeds spawn nothing |
| `work_split` | 4. work split | how the lead decomposes the task (text, rendered into the lead's instructions) |
| `handoffs` | 5. hand-off contract | breed → `{deliver, to}`; uses flokpit intents `DONE`, `BLOCKED`, `QUESTION` |
| `state` | 6. shared state | `kind` (`github-issues`), `label`, `progress_file` |
| `verification` | 7. verification gate | `required`, `optional`, `verifier_is_not_author` |
| `termination` | 8. termination | `conditions` (any one ends the flock), `summary` (what the lead posts at the end) |
| `limits` | 9. flock budget and limits | `max_agents` (channel mode `M`), `max_lifetime`, `max_budget_usd` (0 = no cap), `turn_budget` (agent wakes per human message) |
| `channel` | 10. channel setup | `create`, `name`, `topic`, `modes` |
| `escalate_to_human` | 11. escalation | situations where the lead asks a human with intent `QUESTION` |
| `kickoff` | start | what the lead posts and does first |

Placeholders: `{flock}` (flock name), `{task}` (the task given at start),
`{repo}`, `{spawner}`.

## Rules

- **Tighten only.** A formation may narrow its breeds, never widen them:
  `spawn_tree` entries must be subsets of the breed's `privileges.may_spawn`,
  and `overrides` may only lower limits or remove tools.
- **Independent verification.** With `verifier_is_not_author: true`, no agent
  verifies work it produced.
- **Limits stack.** Each agent keeps its breed limits; the flock limits apply
  on top. `max_agents` counts the lead.
- **Humans stay in charge.** Ops in the channel can stop the flock at any
  time; merges to the default branch always need a human.
