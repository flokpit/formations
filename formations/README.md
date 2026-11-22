# Formations

One YAML file per formation. A formation is a predefined swarm: which
[breeds](../breeds/README.md) take part, how many, who leads, how work is
split and handed off, who verifies, and when the flock stops. A running
formation is a **flock**; its orchestrating agent is the **lead**. Concept:
`docs/IDEA.md`, section "Next step: formations".

All formations are **proposals** (`status: proposal`). Nothing in flokpit
reads them yet; until it does, the lead's breed instructions plus the rendered
formation text are what make the flock behave.

| Formation | Lead | Members | Shape | Use | Pods at take-off |
|---|---|---|---|---|---|
| [feature-team](feature-team.yaml) | architect | developers (1-4), reviewer, tester, devops, tech-writer (optional) | orchestrator, workers, independent verifier, on an integration branch | a feature that spans several modules | 2 |
| [bug-sweep](bug-sweep.yaml) | planner | developers (1-5), reviewer | fan-out, independent verifier | many small, independent issues | 2 |
| [ui-bugfixing](ui-bugfixing.yaml) | planner | tester, developers (3) | continuous find, triage, fix on an integration branch | keep a UI healthy without tickets: the tester explores, the planner triages, developers merge fixes | 5 |
| [project-setup](project-setup.yaml) | architect | devops, reviewer, developers (0-2), tester, tech-writer (optional) | bootstrap on an integration branch | make a new or existing repository workable: mise contract, pipeline, first tests, AGENTS.md | 3 |
| [security-sweep](security-sweep.yaml) | security-auditor | developers (0-3), reviewer | audit, fix, re-test | audit a repository and fix what the audit finds | 2 |
| [release](release.yaml) | release-manager | reviewer, tester, developers (0-3), devops, tech-writer (optional) | stabilise on a release branch, hand over | get a release ready; a human tags and publishes | 2 |
| [maintenance](maintenance.yaml) | project-manager | issue-checker, pr-checker, reviewer, developer, devops, security-auditor, tech-writer, consultant: all roosted | standing, event-driven | keep a repository healthy for a day without a task | 1 |
| [product-discovery](product-discovery.yaml) | project-manager | architect, tester, planner (optional) | discovery before any code | turn an idea into a spec, an architecture sketch, acceptance tests and a backlog | 2 |

Every formation also carries the roosted helpers `watchdog` and `resumer`,
most of them `pr-checker` and an on-demand `consultant`. Which formation fits
which task: [`docs/USECASES.md`](../docs/USECASES.md) section 9.1.

## Schema (`formations/v1alpha1`)

Machine-readable: [`specs/formation.schema.json`](../specs/formation.schema.json).
Validate with `uv run scripts/validate.py`.

| Section | Formation feature | Fields |
|---|---|---|
| `name`, `description`, `status`, `shape` | identity | name `^[a-z][a-z0-9-]{0,31}$` |
| `integration_branch` | shared branch | optional; branch (e.g. `ui-bugfixing/{date}`) that flokpit creates from the default branch and that members merge into directly; if it is missing, a developer creates it (the lead is read-only for git writes) |
| `lead` | 1. lead | `breed`, `op` (lead gets `+o` in the flock channel), `overrides` |
| `lead_commands`, `member_commands` | 1a. command grants | required; flokpit v2 commands the lead and the other members may use in the flock (same names as a breed's `commands`; `/land` and `/kick` act on the own flock). Replaces `op`, which v2 ignores. A lead with a `spawn_tree` entry needs `fly` (validator) |
| `members` | 2. members | list of `{breed, count: {min, max}, start: with_flock \| on_demand \| on_roost, overrides}`; `on_roost` members are started only by a roost of the formation |
| `spawn_tree` | 3. spawn tree | breed → breeds it may spawn inside the flock; omitted breeds spawn nothing |
| `roosts` | 3a. roosts | list of `{name, breed, preset, filter?, task?, max_concurrent?, cooldown?}`: roosts that `/fly` creates in the flock channel and `/land` removes, each from a member breed's preconfigured roost (`preset`, a name from the breed's `roosts`) with overrides (`event_name_filter` replaces, `event_detail_filter` merges per key and `null` removes a key, `task` and guards replace); placeholders are rendered at `/fly`; see [`docs/ROOST.md`](../docs/ROOST.md) section 4 |
| `work_split` | 4. work split | how the lead decomposes the task (text, rendered into the lead's instructions) |
| `handoffs` | 5. hand-off contract | breed → `{deliver, to}`; uses flokpit intents `DONE`, `BLOCKED`, `QUESTION` |
| `state` | 6. shared state | `kind` (`github-issues`), `label`, `progress_file` |
| `verification` | 7. verification gate | `required`, `optional`, `verifier_is_not_author` |
| `termination` | 8. termination | `conditions` (any one ends the flock; `limits_reached` is required), `summary` (what the lead posts at the end) |
| `limits` | 9. flock budget and limits | `max_agents` (channel mode `M`), `max_lifetime`, `max_budget_usd` (0 = no cap), `turn_budget` (agent wakes per human message) |
| `channel` | 10. channel setup | `create`, `name`, `topic`, `modes` |
| `escalate_to_human` | 11. escalation | situations where the lead asks a human with intent `QUESTION`; must list `member_failed_to_start` when a `with_flock` member has `count.min > 0` |
| `kickoff` | start | what the lead posts and does first |
| `member_brief` | start | first message of every `with_flock` and `on_demand` member, in place of the task; must contain `{lead}`. A member's optional `brief` is appended for that breed. Required when a member starts with the flock or on demand (validator) |

Placeholders: `{flock}` (flock name), `{task}` (the task given at start),
`{repo}`, `{spawner}`, `{date}` (ISO date `YYYY-MM-DD` of flock start), `{integration_branch}`, `{lead}` (handle of the flock's lead; a formation placeholder only, breed texts have none because a breed also runs alone). An unknown `{word}` is a validator error. *Pods at take-off* in the table is 1 + the sum of `count.min` of the `with_flock` members.

## Rules

- **Tighten only.** A formation may narrow its breeds, never widen them:
  `spawn_tree` entries must be subsets of the breed's `privileges.may_spawn`,
  and `overrides` may only lower limits or remove tools.
- **Roosts narrow too.** A formation roost starts from a breed preset and may
  only change its filters, task and guards, never the breed; the merged filter
  must still name declared events and filterable details. An `on_roost`
  member must have a roost of the formation that names its breed, and its
  `count.max` bounds how many the roost may have alive (`max_agents` counts
  them like every member).
- **Independent verification.** With `verifier_is_not_author: true`, no agent
  verifies work it produced.
- **Limits stack.** Each agent keeps its breed limits; the flock limits apply
  on top. `max_agents` counts the lead.
- **Integration branch.** With `integration_branch`, members with
  `contents:write-integration-branch` merge there directly; the default branch
  stays human-only.
- **Humans stay in charge.** Ops in the channel can stop the flock at any
  time; merges to the default branch always need a human.
- **Use cases.** Each formation was walked through a concrete task against its
  breeds' permissions in [`docs/USECASES.md`](../docs/USECASES.md).
