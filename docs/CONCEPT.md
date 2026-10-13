# Breeds and Formations in flokpit: Implementation Concept

**Audience:** a flokpit developer agent (or human) implementing breeds and
formations in the flokpit repository.
**Status:** proposal, 2026-10-12. Nothing described here exists in flokpit yet,
except where a section says "today".
**Key words:** MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are used as in
RFC 2119. Requirements have ids (`B-…` breeds, `M-…` models, `S-…` skills,
`F-…` formations, `X-…` cross-cutting) so that issues, PRs and tests can cite them.

---

## 1. Summary

flokpit spawns agents from **roles** (`packages/spawner/roles/*.yaml`). This
concept replaces roles with **breeds** and adds **formations**:

- A **breed** is a kind of agent defined once, vendor-neutrally, in the
  `flokpit/formations` repository: pod resources, OS permissions, skills, main
  instruction, runtime features, an ordered list of capable models, limits,
  lifecycle, tool permissions, spawn and chat privileges.
- A **formation** is a predefined swarm: which breeds, how many, which one
  leads, who may spawn whom, how work is split and handed off, who verifies,
  and when it stops. A running formation is a **flock**; its orchestrating
  agent is the **lead**.

The work has three phases that each ship on their own: breeds as the source
of flokpit roles (phase 1), model priority lists and skills (phase 2),
formations (phase 3).

## 2. Background

### 2.1 Why

- *Role* is overloaded in IT and clashes with Kubernetes `Role`; *breed* fits
  the flock theme and has no clash (`docs/IDEA.md`, "Why breed").
- Roles today mix runtime facts (image, resources) with behaviour (prompt,
  tools) in a Claude-Code-specific shape (`tools.allow: ["Bash(git *)"]`). A
  breed separates them and states permissions in a neutral form that can be
  rendered for Claude Code now and other agent CLIs later.
- Multi-agent work in flokpit is ad hoc: an op spawns agents one by one. A
  formation makes good team shapes (orchestrator, workers, independent
  verifier) repeatable and bounded.

### 2.2 flokpit today (verified 2026-10-12)

| Topic | Where | Facts that matter here |
|---|---|---|
| Role files | `packages/spawner/roles/*.yaml` | 9 roles: `architect`, `consultant`, `designer`, `developer`, `devops`, `hello` (runtime `echo`, used by `bun run smoke`), `planner`, `reviewer`, `tester` |
| Role schema (strict) | `packages/specs/src/roles.ts` (`Role`, `parseRole`, `readRole`, `loadRoles`, `renderTemplate`, `maySpawn`) | zod, `.strict()`; one `model` string; `tools.allow`/`tools.deny` are Claude Code rule strings; template keys `nick`, `spawner`, `channel`, `branch`, `repo` |
| Role schema (lenient) | `packages/spawner/src/role.ts` (`RoleSpec`) | parsed by agentd from the register snapshot; parity test `role.test.ts` (issue #138) |
| Roles directory | `packages/specs/src/config.ts` `rolesDir`, env `FLOKPIT_ROLES_DIR`; in cluster `/etc/flokpit/roles` (ConfigMap `roles`) | |
| Model check | `packages/api/src/services.ts` `requireKnownModel` | an explicit `--model` must be in the provider account's validated `models` list, else `NOSUCHMODEL`; the role default is not checked |
| Spawn rights | `maySpawn()` in `roles.ts`, gateway `chat_spawn` | humans unrestricted; agents limited by the caller role's `may_spawn` |
| Agent runtime | `packages/spawner/src/agentd/*`, image `packages/spawner/image/Dockerfile` | `claude -p --bare`: repository skills, hooks, settings and `CLAUDE.md` are ignored on purpose; agentd writes settings and the system prompt into `/home/agent/.claude/`; **no skill installation exists** |
| Network | `packages/infra/src/agent-pod.ts`, NetworkPolicy `default-deny-egress` in `flokpit-agents` | all egress goes through the egress proxy |
| Concepts | `docs/concepts/agent_spawner.md` (section 8 is the canonical role schema), `docs/concepts/temporal.md` | |

Read `CLAUDE.md` of flokpit before starting: TypeScript on Bun everywhere,
workflow code import restrictions, "Decisions already made".

### 2.3 Background research

In this repository (`flokpit/formations`), OKF bundle `docs/resources/`:

- `docs/resources/portable-agents/summary.md` – which standard fits which
  breed feature; why permissions and limits belong in the pod and gateway.
- `docs/resources/skills/summary.md`, `skills-by-breed.md`, `security.md` –
  where the referenced skills come from and the rules for adopting them.

## 3. Sources of truth and their locations

All paths below are in `flokpit/formations` unless prefixed with `flokpit:`.

| What | Path | Role in the implementation |
|---|---|---|
| Breed files | `breeds/*.yaml` | the content flokpit loads; `_base.yaml` holds shared defaults |
| Breed documentation | `breeds/README.md` | field meaning, merge rule, model selection |
| Breed schema | `specs/breed.schema.json` (JSON Schema 2020-12, `$id` `https://github.com/flokpit/formations/specs/breed.schema.json`) | contract; `$defs/resolved` describes a merged, complete breed |
| Formation files | `formations/*.yaml` | three proposals: `feature-team`, `bug-sweep`, `product-discovery` |
| Formation documentation | `formations/README.md` | field meaning, tighten-only rules |
| Formation schema | `specs/formation.schema.json` | contract; references breed `$defs` |
| Reference validator | `scripts/validate.py` (`uv run scripts/validate.py [FILE...]`) | schema checks plus cross-file rules; the behaviour flokpit's loader must match |
| CI | `.github/workflows/validate.yml` | runs the validator per file |
| Concept | `docs/IDEA.md`, this file | |

The schemas are the contract between the two repositories. flokpit MUST NOT
keep a diverging copy of them (see X-2).

## 4. Data model

### 4.1 Breed (`apiVersion: formations/v1alpha1`, `kind: Breed`)

| Section | Meaning | Today's role field |
|---|---|---|
| `name`, `description`, `status` | identity; `status` `proposal`, `active`, `deprecated` | `name`, `description` |
| `extends` | name of a `BreedBase` to deep-merge first | – |
| `model.class`, `model.effort`, `model.overridable`, `model.candidates[]` | ordered `{provider, id, effort?}` list of capable models | `model` (single id) |
| `instructions`, `house_rules` | main instruction; rendered to one prompt (instructions, blank line, house rules) | `system_prompt` |
| `skills[]` | `{source, ref, path, license, review}` | – |
| `runtime.image`, `runtime.features[]` | image variant, Dev Container Features | `image` |
| `pod.resources`, `pod.workspace_size` | Kubernetes requests/limits, workspace emptyDir size | `resources`, `workspace.size_limit` |
| `os` | `user`, `sudo`, `root_filesystem`, `writable_paths`, `tmp_size`, `network.egress`, `network.allow` | implicit in `buildAgentPod()` and the egress proxy |
| `limits` | `max_turns`, `max_budget_usd`, `summary_budget_usd`, `tighten_only` | same names |
| `lifecycle` | `hello`, `idle_timeout`, `max_lifetime`, `summary_deadline` | same names (top-level) |
| `tools` | category → pattern → `allow`/`deny`; categories `read`, `edit`, `bash`, `webfetch`, `websearch`, `mcp`, `subagents` | `tools.allow`, `tools.deny` (Claude rule strings) |
| `privileges` | `may_spawn`, `chat.mode`, `chat.op` | `may_spawn` |
| `workspace` | `clone`, `branch_prefix` | `workspace.clone`, `workspace.branch_prefix` |
| `credentials.github` | requested GitHub scopes, e.g. `contents:write-own-branch` | – (gateway decides today) |
| `handoff` | `done`, `next` | – |

Merge rule: maps merge recursively, lists and scalars replace. A breed's
`model.candidates` therefore replaces the base list entirely.

### 4.2 Formation (`kind: Formation`)

Sections: `lead {breed, op, overrides}`, `members[] {breed, count {min, max},
start: with_flock|on_demand, overrides}`, `spawn_tree`, `work_split`,
`handoffs`, `state`, `verification`, `termination {conditions, summary}`,
`limits {max_agents, max_lifetime, max_budget_usd, turn_budget}`, `channel`,
`escalate_to_human`, `kickoff`. Placeholders `{flock}`, `{task}`, `{repo}`,
`{spawner}`. Details: `formations/README.md`.

## 5. Technical concept

### 5.1 Getting the files into flokpit

Recommended: pin `flokpit/formations` as a **git submodule** at
`flokpit:vendor/formations` (a commit, never a branch). flokpit reads
`vendor/formations/breeds` locally and ships it in the `roles` ConfigMap (or a
new `breeds` ConfigMap) in the cluster, as it does with roles today.
`FLOKPIT_BREEDS_DIR` configures the path like `FLOKPIT_ROLES_DIR`.

Alternative: a CI job in `flokpit/formations` publishes a versioned tarball
or OCI artifact. Choose it only if submodules cause trouble; the requirements
below hold either way.

### 5.2 Loading and resolving breeds (phase 1)

New module `flokpit:packages/specs/src/breeds.ts`, next to `roles.ts`:

1. Read every `*.yaml` in the breeds directory (`Bun.YAML.parse`).
2. Validate each file against `specs/breed.schema.json` (Ajv 2020-12, loaded
   from the vendored repository, not copied).
3. Resolve `extends` with the merge rule of 4.1; validate the result against
   `breed.schema.json#/$defs/resolved`.
4. Run the cross-file checks of `scripts/validate.py` (file name = name,
   `may_spawn` and `handoff.next` name existing breeds).
5. Render each resolved breed into today's `Role` (5.3) and validate it with
   the existing strict `Role` schema.

Everything downstream (spawn, gateway register, agentd, `/roles`) keeps
working on `Role` in phase 1. That keeps the change small and lets the parity
tests of issue #138 keep guarding agentd.

### 5.3 Rendering a breed into a flokpit `Role`

| Role field | From the breed |
|---|---|
| `name`, `description` | same |
| `runtime` | `claude` (breeds have no echo runtime; see B-9) |
| `hello` | `lifecycle.hello` |
| `image` | resolved from `runtime.image` (`base` → the current agent image tag, `browser` → the browser variant) |
| `model` | phase 1: `model.candidates[0].id`; phase 2: see 5.5 |
| `max_turns`, `max_budget_usd`, `summary_budget_usd` | `limits.*` (`summary_budget_usd: null` → omit) |
| `idle_timeout`, `max_lifetime`, `summary_deadline` | `lifecycle.*` |
| `may_spawn` | `privileges.may_spawn` |
| `resources` | `pod.resources` |
| `workspace` | `workspace.clone`, `workspace.branch_prefix`, `size_limit` ← `pod.workspace_size` |
| `tools.allow`, `tools.deny` | rendered from `tools` (5.4) |
| `system_prompt` | `instructions` + `"\n\n"` + `house_rules` (placeholders stay for `renderTemplate`) |

Fields with no `Role` counterpart (`skills`, `runtime.features`, `os`,
`credentials`, `handoff`, `chat`) are carried in a new optional
`Role.breed` object (phase 2) or ignored with a startup log line (phase 1).

### 5.4 Rendering tool permissions for Claude Code

The breed states permissions per category; Claude Code wants rule strings.

| Breed category | Pattern | Claude Code rule |
|---|---|---|
| `read` | `"**"` | `Read`, `Glob`, `Grep` |
| `read` | absolute path glob `/tmp/**` | `Read(//tmp/**)` (Claude needs `//` for absolute paths) |
| `edit` | absolute path glob `/workspace/**` | `Edit(//workspace/**)`, plus `Write` once any edit is allowed |
| `bash` | command pattern `git *` | `Bash(git *)` |
| `webfetch` | `allow`/`deny` or domain pattern | `WebFetch` / `WebFetch(domain:<d>)` |
| `websearch` | `allow`/`deny` | `WebSearch` |
| `mcp` | `flokpit/*` | `mcp__flokpit__*` (server/tool → `mcp__server__tool`) |
| `subagents` | `allow`/`deny` | `Agent` (Task) |

Semantics the renderer MUST keep:

- `deny` beats `allow`. Every `deny` pattern becomes a `tools.deny` entry.
- Anything not allowed is denied: agents run with `--permission-mode
  dontAsk --permission-prompts none`, so there is no "ask".
- Patterns containing `{branch}` (for example `git push origin {branch}*`)
  are rendered per agent at register time with the same template values as
  `system_prompt`.
- Read-only shell commands that Claude Code allows without a rule need no
  entry; the renderer MUST NOT emit duplicates or an allow that equals a deny
  (the lenient `RoleSpec` rejects that).

Golden test: the rendered `developer` breed is compared with today's
`developer.yaml`; every difference is listed in the PR and justified.

### 5.5 Model selection (phase 2)

Extend `Role` with `models: string[]` (ordered; `model` stays for
compatibility and equals the chosen id after selection). At spawn time, in
`flokpit:packages/api/src/services.ts` next to `requireKnownModel`:

```
choose(breed, account, override):
  if override:
    if not breed.model.overridable: fail INVALID_PARAMS
    requireKnownModel(account, override)          # existing NOSUCHMODEL check
    return override
  offered = account.models                        # validated list, may be absent
  for c in breed.model.candidates:
    if c.provider not in runtimeProviders(breed): continue   # claude runtime: anthropic
    if offered is absent or c.id in offered: return c.id (and c.effort or model.effort)
  fail NOSUCHMODEL "none of <ids> is available on provider account <name>"
```

The chosen id goes into the role snapshot that `POST /gateway/register`
returns, the audit row and `/whois`, exactly where `model` goes today.

### 5.6 Skills (phase 2)

Today agents get no skills, and `--bare` ignores repository skills by
design. Delivery path:

1. **Vendor at build time.** The image build (or a skills bundle built in
   CI) fetches every `skills[]` entry at its `ref` (a commit) into
   `/opt/flokpit/skills/<source>/<ref>/<path>`. Builds MUST fail if a ref
   cannot be fetched or a licence file is missing.
2. **Install at boot.** agentd copies (or symlinks) the agent's breed skills
   into `/home/agent/.claude/skills/<skill-name>/` before starting `claude`.
   Claude Code loads skills from the personal scope even with `--bare`;
   verify this in a spike and record the result in the PR (see S-6).
3. **No runtime fetching.** No skill is downloaded from GitHub or a registry
   while an agent runs; egress stays closed.
4. **Review gate.** Only skills with `review: approved` are installed in
   production; `pending` skills only when `FLOKPIT_ALLOW_UNREVIEWED_SKILLS=1`
   (development).

### 5.7 Runtime features, OS permissions and network

- `runtime.image` selects an image variant built `FROM` the agent image
  (`packages/spawner/image/Dockerfile`). Dev Container Features listed in
  `runtime.features` are installed at image build time, not at boot. The
  `ui-tester` breed needs a `browser` variant with Chromium and a
  `local:features/playwright` feature that does not exist yet.
- `os` is enforced by the pod, not by Claude Code: non-root user, no `sudo`
  binary, read-only root filesystem with emptyDirs for `writable_paths`,
  `tmp_size` as emptyDir `sizeLimit`, `/dev/shm` as a memory emptyDir when
  listed. `buildAgentPod()` in `flokpit:packages/infra/src/agent-pod.ts` is
  the place.
- `os.network.allow` becomes the per-agent allowlist of the egress proxy (the
  `default-deny-egress` NetworkPolicy stays). `localhost` always works inside
  the pod.

### 5.8 Credentials, workspace, hand-off

- `credentials.github` lists scopes the agent asks the gateway for. The
  gateway MUST NOT grant more than today's role behaviour allows; a breed can
  only narrow (`contents:read` instead of write).
- `workspace.clone: false` (project-manager) means no checkout; agentd starts
  in an empty `/workspace`.
- `handoff.done` is appended to the system prompt as "When you are done:
  …"; `handoff.next` is informational in phase 1–2 and used by formations.

### 5.9 Formations (phase 3)

**Start.** `/fly <formation> [--repo url] [--task "..."]` (deprecated alias
`/spawn --formation <name>`), REST and WS equivalents, ops only. flokpit:

1. validates the formation (4.2, F-1 to F-4) and the caller's rights;
2. creates the flock channel if `channel.create` (name from `channel.name`
   with `{flock}` = `<formation>-<short id>`), sets topic and modes, gives the
   caller `+o`;
3. spawns the lead with `--op` if `lead.op`, then every member with
   `start: with_flock` at `count.min`;
4. sends the lead a kickoff turn built from `kickoff`, `work_split`,
   `handoffs`, `verification`, `termination` and `escalate_to_human`
   (rendered text, placeholders filled).

**Enforcement.** A new `FlockWorkflow` (child of the channel workflow,
id `flock:<org>:<flock>`) owns the flock state:

- **Spawn tree.** `chat_spawn` by a flock member is allowed only if the
  caller's breed lists the target in `spawn_tree` (in addition to its
  `may_spawn`), the target is a member breed, and the member's `count.max`
  and `limits.max_agents` are not exceeded.
- **Overrides** are applied to the role snapshot of each spawned member
  (tighten only).
- **Limits.** `max_lifetime` is a workflow timer; `max_agents` sets channel
  mode `M`; `turn_budget` sets the channel's agent-turn budget;
  `max_budget_usd > 0` is summed from per-turn cost deltas (already reported
  by agentd).
- **Termination.** `human_stop` (an op runs `/land <flock>`), `limits_reached`
  and `no_progress_rounds` are detected by the workflow; content conditions
  (`all_items_verified`, `backlog_ready`) are declared by the lead with intent
  `DONE` and confirmed by a human op. On termination: summary request to the
  lead, graceful kill of all members, lead posts `termination.summary`, then
  the lead is killed.
- **Escalation** is prompt-level: the lead is instructed to ask with intent
  `QUESTION`; merges are additionally blocked by tool permissions.

## 6. Implementation plan

| Phase | Scope | Main code | Done when |
|---|---|---|---|
| 0 | Decisions: role → breed naming in flokpit, delivery path (5.1), command names | issue and decision record in `flokpit:docs/decisions/` | decisions recorded |
| 1 | Breeds as the source of roles: vendoring, `breeds.ts` loader, renderer, golden tests, `/roles` lists breeds | `specs`, `infra` (ConfigMap), `spawner` (image tag mapping) | SC-1 to SC-5 |
| 2a | Model priority lists | `specs` (`Role.models`), `api` (selection), `temporal` (snapshot), UI shows chosen model | SC-6, SC-7 |
| 2b | Skills | image build, agentd install, review gate | SC-8 to SC-10 |
| 2c | OS permissions and network from breeds | `infra/agent-pod.ts`, egress proxy allowlist | SC-11 |
| 3 | Formations | `api` (`/fly`), `temporal` (`FlockWorkflow`), `mcp` (`chat_spawn` checks), UI | SC-12 to SC-16 |

Each phase is one or more PRs with tests; no phase may break `bun run smoke`.

## 7. Requirements

### 7.1 Breeds

| Id | Requirement |
|---|---|
| B-1 | flokpit MUST load breeds from a pinned commit of `flokpit/formations`; it MUST NOT follow a branch at runtime. |
| B-2 | Every breed file MUST validate against `specs/breed.schema.json`, and every resolved breed against `#/$defs/resolved`. An invalid breed MUST NOT be spawnable; flokpit MUST report it at startup (like `loadRoles` errors today) and keep serving the valid ones. |
| B-3 | Resolution MUST use the merge rule of 4.1 exactly (maps merge, lists and scalars replace). |
| B-4 | The rendered `Role` MUST pass the existing strict `Role` schema and the agentd `RoleSpec` parity test. |
| B-5 | Tool rendering MUST follow 5.4: deny beats allow, unlisted means denied, absolute paths use `//`, `{branch}` rendered per agent. |
| B-6 | `/spawn <breed>` arguments and formations MUST only narrow a breed (limits lower, tools fewer, spawn rights fewer); flokpit already enforces this for `/spawn`. |
| B-7 | `privileges.may_spawn` MUST replace `Role.may_spawn` in `maySpawn()` with unchanged semantics (humans unrestricted). |
| B-8 | User-facing text MUST say "breed"; the API SHOULD accept `role` as a deprecated alias for one release. |
| B-9 | The smoke test's `hello` agent (runtime `echo`) MUST keep working: either keep `hello.yaml` as a role, or add an optional `runtime` to the breed schema in `flokpit/formations` first. |
| B-10 | Existing roles without a breed (`consultant`, `designer`, `devops`, `hello`) MUST stay available until a breed replaces them. A breed and a role with the same name MAY coexist: the breed wins, and flokpit MUST log the shadowing once per load. |
| B-11 | Name mapping MUST be explicit and MUST NOT be aliased silently. Decided in phase 0 (decision 6): the breeds are renamed, `software-architect` to `architect` and `ui-tester` to `tester`, and flokpit keeps its role names `architect` and `tester`. The resulting name clash is resolved by B-10 (the breed wins). |

### 7.2 Models

| Id | Requirement |
|---|---|
| M-1 | Model selection MUST follow 5.5: override if allowed and offered, else the first candidate the account offers and the runtime supports, else `NOSUCHMODEL` before anything is created. |
| M-2 | An account without a validated model list MUST select the first candidate (today's behaviour for the role default). |
| M-3 | The chosen model id MUST appear wherever `model` appears today (register snapshot, audit row, `/whois`, agent card). |
| M-4 | Candidates of a provider the runtime cannot run MUST be skipped, not fail the spawn. |

### 7.3 Skills

| Id | Requirement |
|---|---|
| S-1 | Skills MUST be fetched at build time at their pinned `ref`; nothing is fetched while an agent runs. |
| S-2 | Only `review: approved` skills MUST be installed in production; `pending` only behind an explicit development flag. |
| S-3 | Each installed skill MUST keep its licence file and a record of source, ref and path. |
| S-4 | agentd MUST install exactly the skills of the agent's breed and no others. |
| S-5 | A skill MUST NOT widen tool permissions; `allowed-tools` in a `SKILL.md` is ignored or narrowed by the breed's tools. |
| S-6 | Before shipping, a spike MUST confirm that `claude -p --bare` loads skills from `/home/agent/.claude/skills`; if it does not, document the alternative (`--add-dir`, plugin, settings) in the PR. |

### 7.4 Formations

| Id | Requirement |
|---|---|
| F-1 | Formation files MUST validate against `specs/formation.schema.json` and the cross-file rules of `scripts/validate.py` (breeds exist, spawn tree and overrides only narrow, participants only, `max_agents` ≥ lead + all members at max). |
| F-2 | Only channel ops (or the org admin) MAY start a flock. |
| F-3 | flokpit MUST enforce `spawn_tree`, member `count.max`, `limits.max_agents`, `limits.max_lifetime` and `limits.turn_budget` server-side; prompt instructions alone are not enforcement. |
| F-4 | Every flock MUST end on `human_stop`, and on `limits_reached`; the termination path MUST post the summary and kill all members. |
| F-5 | Merges to the default branch MUST NOT be possible for any flock member (tool permissions), regardless of what the formation text says. |
| F-6 | Flock state (members, counts, termination reason) SHOULD be visible in the UI's channel overview and via a query on `FlockWorkflow`. |
| F-7 | The lead's kickoff text SHOULD be built from the formation sections, not hand-written per formation. |

### 7.5 Cross-cutting

| Id | Requirement |
|---|---|
| X-1 | Follow flokpit conventions: TypeScript on Bun, zod in `specs`, workflow import rules, `bun run typecheck`, `bun test`, `bun run smoke`. |
| X-2 | The JSON Schemas in `flokpit/formations/specs/` are the contract. flokpit MUST validate against them (vendored, not copied) and MUST NOT add a second schema that disagrees. zod types MAY be derived from them. |
| X-3 | Behaviour MUST match `scripts/validate.py` on the same input: a file it rejects flokpit rejects, and vice versa (shared fixtures). |
| X-4 | Schema changes happen in `flokpit/formations` first (schema, README, validator, files), then flokpit bumps the pin. |
| X-5 | Security-relevant limits (filesystem, network, credentials, cost, wall-clock) MUST be enforced by pod, gateway, egress proxy or workflow; CLI settings are only a second layer. |
| X-6 | Update `flokpit:docs/concepts/agent_spawner.md` (section 8), `temporal.md` (flocks) and `docs/log.md` in the same PRs. |
| X-7 | The renderer SHOULD be structured so that a second agent CLI (for example Codex) can be added as another target without touching breed files. |

## 8. Success criteria

| Id | Criterion | How to check |
|---|---|---|
| SC-1 | All breeds of the pinned `flokpit/formations` load; `/roles` (or `/breeds`) lists them with descriptions | unit test plus manual `/roles` |
| SC-2 | `/spawn developer` with breeds behaves like today's developer role: same tools in effect, same limits, same lifecycle | golden test of the rendered `Role`; documented, justified diff |
| SC-3 | An invalid breed is reported at startup with file and path, the others keep working | unit test with a broken fixture |
| SC-4 | `bun run typecheck`, `bun test`, `bun run smoke` pass; CI green | CI |
| SC-5 | Shared fixtures produce the same accept/reject verdicts in `scripts/validate.py` and the flokpit loader | parity test |
| SC-6 | With an account that lacks `claude-opus-5-5` but offers `claude-opus-5`, `/spawn developer` runs on `claude-opus-5`; with neither, `NOSUCHMODEL` and no pod | unit tests in `api` |
| SC-7 | `/spawn developer --model <id not offered>` fails with `NOSUCHMODEL` | existing test still passes |
| SC-8 | A spawned `reviewer` has exactly its breed's approved skills in `~/.claude/skills`, each with licence and source record | agentd test plus pod inspection |
| SC-9 | No network request to GitHub or a skill registry happens while an agent runs | egress proxy log |
| SC-10 | The `--bare` skill-loading spike result is recorded | PR description |
| SC-11 | A breed with `os.network.allow: [github.com]` cannot reach `pypi.org`; `sudo` is absent; root filesystem is read-only | k3s scenario test |
| SC-12 | `/fly feature-team --task "..."` creates the channel, the lead with `+o` and the reviewer; the lead receives the kickoff | e2e with `echo`-runtime fixtures, then one real run |
| SC-13 | A developer in a `bug-sweep` flock cannot spawn anyone; the planner cannot spawn a sixth developer | workflow tests |
| SC-14 | `max_lifetime` expiry and `/land` both end the flock: summary posted, all members gone | workflow tests |
| SC-15 | No flock member can merge to the default branch | tool rendering test and one real attempt |
| SC-16 | Docs updated (X-6) | review |

## 9. Non-goals

- Supporting agent CLIs other than Claude Code (keep the door open, X-7).
- Publishing breeds to external registries (OASF, A2A agent cards).
- Automatic skill review; review stays a human step.
- Formations that change themselves at runtime, or nested flocks.
- Merging, deploying or closing issues on behalf of humans.

## 10. Phase-0 decisions

All six were decided by dennisjay on 2026-10-13; the record with the request
ids is `docs/decisions/001-contract-delivery-to-flokpit.md`.

| # | Decision | Options | Decided |
|---|---|---|---|
| 1 | Rename roles to breeds in flokpit's code, API and UI, or keep `Role` internally and only render? | full rename (cleaner, larger PR) / internal `Role` with breed loader | internal `Role` with a breed loader for phase 1; user-facing text says "breed" (B-8) |
| 2 | Name conflicts | rename flokpit `architect`, `tester` / rename the breeds | rename the breeds: `software-architect` to `architect`, `ui-tester` to `tester`; flokpit keeps its role names (B-11), the clash is resolved by B-10 |
| 3 | Delivery of `flokpit/formations` | git submodule / published artifact | the published artifact: flokpit loads a configured `<short sha>.tar.gz` key, `LATEST` may only be fetched to notice and log a newer key (B-1); the archive carries `breeds/`, `formations/`, `specs/` and `scripts/validate.py` |
| 4 | Echo runtime for breeds | keep `hello` as a role / add `runtime` to the breed schema | decided for phase 1: `hello` stays a role; an optional `runtime` in the breed schema stays the recorded alternative for a later phase (B-9) |
| 5 | Commands | `/fly` + `/land` / `/spawn --formation` + `/kill --flock` | `/fly <formation>` and `/land <flock>`, with `/spawn --formation <name>` kept as a deprecated alias (5.9); `/kill --flock` is not the vocabulary |
| 6 | Where content termination conditions are judged | lead declares, human confirms / verifier agent / workflow heuristics | the lead declares with intent `DONE` and a human op confirms; no verifier agent and no workflow heuristics. `limits_reached` and `no_progress_rounds` stay workflow-detected (F-3, F-4) |

## 11. References

- `docs/IDEA.md` – idea, breed features, formation features
- `breeds/README.md`, `formations/README.md`, `specs/*.schema.json`,
  `scripts/validate.py`
- `docs/resources/portable-agents/summary.md`, `docs/resources/skills/summary.md`,
  `docs/resources/skills/security.md`
- `flokpit:CLAUDE.md`, `flokpit:docs/concepts/agent_spawner.md` (sections 2–8),
  `flokpit:docs/concepts/temporal.md`, `flokpit:docs/concepts/api.md`,
  `flokpit:packages/specs/src/roles.ts`, `flokpit:packages/spawner/src/role.ts`,
  `flokpit:packages/api/src/services.ts` (`requireKnownModel`),
  `flokpit:packages/infra/src/agent-pod.ts`
