# Breeds

One YAML file per breed. A breed describes a kind of flokpit agent
independent of the agent vendor; a renderer (not written yet) turns it into
what the runtime needs: flokpit's `RoleSpec`, Claude Code settings and flags,
or another CLI's files. Background: `docs/IDEA.md` and
`docs/resources/portable-agents/summary.md`.

All breeds are **proposals** (`status: proposal`). Skills are pinned to a
commit but not yet reviewed (`review: pending`), as required by
`docs/resources/skills/security.md`.

| Breed | Model class | Writes | Lead of |
|---|---|---|---|
| [developer](developer.yaml) | frontier | code on its own branch, PRs | - |
| [reviewer](reviewer.yaml) | balanced | PR reviews only | - |
| [tester](tester.yaml) | balanced | e2e tests, test reports | - |
| [architect](architect.yaml) | frontier | ADRs, architecture docs | feature team, project setup |
| [planner](planner.yaml) | frontier | issues, plans | bug sweep, ui bugfixing |
| [project-manager](project-manager.yaml) | balanced | specs and progress files (docs only), issues, status reports | product discovery, maintenance |
| [devops](devops.yaml) | frontier | CI workflows, build, container and infrastructure files, the mise contract, dependency updates; PRs | - |
| [tech-writer](tech-writer.yaml) | balanced | documentation (README, guides, API reference, changelog, AGENTS.md); PRs | - |
| [security-auditor](security-auditor.yaml) | frontier | findings as issues or private advisories; never the repository | security sweep |
| [release-manager](release-manager.yaml) | balanced | version bump, changelog, release PR, draft release notes; never a tag | release |
| [consultant](consultant.yaml) | frontier | one decision memo under `docs/decisions/` | - |
| [watchdog](watchdog.yaml) | balanced | nothing; asks, spawns a consultant, replaces stuck agents | - (roosted every 15 min) |
| [issue-checker](issue-checker.yaml) | balanced | triage section and labels on one issue | - (roosted on `github.event.issue_opened`) |
| [pr-checker](pr-checker.yaml) | balanced | one risk comment per PR, changes-requested review when critical | - (roosted on opened and updated PRs) |
| [resumer](resumer.yaml) | fast | nothing; wakes and respawns agents interrupted by a token limit | - (roosted on `provider.event.budget_reset`) |

Which breed or formation to use for which software engineering task is the
table in [`docs/USECASES.md`](../docs/USECASES.md) section 9.1.

Every breed declares `roosts:`, its **preconfigured roosts**: the filter
expression it is written for and the default task. A roost in a channel is
created from one of them and may override the filters
([`docs/ROOST.md`](../docs/ROOST.md) section 4). The last four are
**roost-only breeds**: nobody spawns them by hand. They are stateless and
short-lived: the channel history is their memory, and they call `chat_done`
and stop when their pass is over.

## Schema (`formations/v1alpha1`)

Machine-readable: [`specs/breed.schema.json`](../specs/breed.schema.json).
Validate with `uv run scripts/validate.py`.

`extends: _base` deep-merges [`_base.yaml`](_base.yaml): maps merge, lists
and scalars replace. `_base.yaml` is not a breed and cannot be spawned.

| Section | Feature | Fields |
|---|---|---|
| `name`, `description`, `status` | identity | name `^[a-z][a-z0-9-]{0,31}$` |
| `pod` | 1. pod specification | `resources.requests`, `resources.limits` (Kubernetes quantities), `workspace_size` |
| `os` | 2. OS-level permissions | `user`, `sudo`, `root_filesystem`, `writable_paths`, `tmp_size`, `network.egress` (`none`, `allowlist`), `network.allow` (domains) |
| `skills` | 3. skills | list of `{source, ref, path, license, review, name?}`; `source` is a GitHub repository or `local:<path>`, `ref` a commit; optional `name` is the install directory (`^[a-z0-9][a-z0-9._-]{0,63}$`), defaulting to the last segment of `path` |
| `instructions`, `house_rules` | 4. main instruction | rendered into `AGENTS.md` (instructions first, then house rules); placeholders `{nick}`, `{spawner}`, `{channel}`, `{branch}`, `{repo}` |
| `runtime` | 5. runtime features | `image` (`base` or a variant), `features` (Dev Container Feature references with `options`). The image carries no project toolchain: a repository declares its tools in `mise.toml` and flokpit installs them at boot; the tasks a project provides per breed are in [`docs/FLOKPIT_PROJECT_COMPAT.md`](../docs/FLOKPIT_PROJECT_COMPAT.md) |
| `model` | 6. model choice | `class` (`frontier`, `balanced`, `fast`), `effort`, `overridable`, `candidates` (ordered list of `{provider, id, effort?}`; see below) |
| `limits` | 7. limits and budgets | `max_turns`, `max_budget_usd` (0 = no cap), `summary_budget_usd`, `tighten_only` |
| `lifecycle` | 8. lifecycle | `hello`, `idle_timeout`, `max_lifetime`, `summary_deadline` |
| `tools` | 9. tool permissions | category → pattern → `allow` or `deny`; categories `read`, `edit`, `bash`, `webfetch`, `websearch`, `mcp`, `subagents`; `deny` wins over `allow`, and anything not allowed is denied (agents run without prompts; the rules are a guardrail for a cooperative agent, not a sandbox, because an allowed interpreter such as `node *` can do anything; the real boundaries are the network policy, the pod and the token scopes, and the local driver has none); `{branch}` in a pattern is the agent's branch |
| `privileges` | 10. spawn and chat | `may_spawn` (breed names), `chat.mode` (`voice` = `+v`), `chat.op` (v1 leftover: flokpit v2 has no channel operators and ignores it) |
| `commands` | 10a. chat commands | flokpit v2 commands the agent may use: any of `fly`, `land`, `kick`, `rename`, `set`, `trigger`, `meta`, `honk`; a list that is missing or empty grants nothing (flokpit then applies its shipped default `[honk]`). `fly` needs a non-empty `may_spawn` (validator). `_base` grants `honk`; every breed with a `may_spawn` list adds `fly`, `watchdog` also `land`; lists replace |
| `roosts` | 11. preconfigured roosts | required; list of `{name, description, filter, task, max_concurrent?, cooldown?}` (empty for a breed that is never roosted); `filter` is a filter expression (`event_name_filter`, `event_detail_filter`) over [`events/catalogue.yaml`](../events/catalogue.yaml), `task` a template with `{<detail key>}` placeholders; a roost instance is created from one entry (its preset) and may override the filters; the validator checks that every filter names declared events and filterable details ([`docs/ROOST.md`](../docs/ROOST.md) sections 3, 4 and 8) |
| `workspace`, `credentials`, `handoff` | later features | repository clone and branch prefix; GitHub access requested from the flokpit gateway (`contents:write-integration-branch` allows pushing to a formation's `integration_branch`, never the default branch); what the breed must deliver when done |

## Permission design

Breeds were checked against concrete use cases in
[`docs/USECASES.md`](../docs/USECASES.md); section 9 holds the current
decisions. The rule since 2026-11-21 is **functionality over security at the
tool layer**: an agent that cannot run the project's own commands is useless,
and an allowed interpreter (`python3 *`, `npx *`, `make *`) was always as wide
as a shell. The real boundaries are the pod (non-root, read-only root
filesystem, no `sudo`, no Docker), the egress allowlist and the gateway-held
credentials.

- **Breeds that run project code** (developer, reviewer, tester, devops,
  tech-writer, pr-checker, issue-checker, security-auditor, release-manager)
  allow every shell command (`bash: { "*": allow }`) and edits anywhere in
  the checkout, so they work in any stack, layout and package manager. What
  stays denied is what a credential could do: pushes to the default branch,
  force pushes, merges, deletes, tags and publishing; breeds that must not
  change the repository (reviewer, checkers, auditor) are denied `git push`
  and `git commit`.
- **Breeds that only read and write documents** (architect, planner,
  project-manager, consultant, watchdog, resumer) keep an explicit allowlist:
  the shell basics and read-only `git`/`gh` of `_base` plus their own `gh`
  and `git` writes. Document writers may edit anywhere in the checkout, since
  projects keep ADRs, specs and decisions in different places; what they
  write is limited by their instructions.
- `_base` allows the shell basics (`ls`, `cat`, `cd`, `grep`, `head`, ...):
  flokpit checks a command line per sub-command, so a pipe or `cd x && ...`
  is only allowed when every part is.
- **Network:** one allowlist in `_base` for every breed (GitHub,
  documentation hosts, security references, font and script CDNs for pages
  under test). flokpit adds the package registries and toolchain hosts to
  every agent. `webfetch: { "*": allow }` lets WebFetch reach whatever the
  proxy lets through; a `webfetch` pattern is a bare host name (flokpit
  renders `WebFetch(domain:<host>)` itself). `websearch` is allowed for every
  breed: it runs at the provider, not in the pod.
- **Credentials:** lists replace in the merge, so a breed that sets
  `credentials.github` repeats the read scopes of `_base` (`issues:read`,
  `pull_requests:read`, `checks:read`, `actions:read`); without them `gh pr
  checks` and `gh run view` fail on private repositories. Scopes beyond
  flokpit's first set (`workflows:write`, `actions:write`,
  `security_events:read`, `security_advisories:write`,
  `releases:write-draft`) are listed in `docs/CONCEPT.md` 5.8; until the
  gateway grants one, the breed posts BLOCKED at the step that needs it.

`tighten_only: true` means a spawned agent's limits and tools can only be
narrowed by `/spawn` arguments or a formation, never widened (flokpit already
enforces this for `/spawn`).

## Model selection

`model.candidates` is a priority list of models that are capable of the
breed's work. At spawn time the first candidate is chosen that

1. the spawn's provider account offers (flokpit stores the model ids of each
   account at validation), and
2. the agent runtime can run (`provider: anthropic` for Claude Code; other
   providers need a runtime for their CLI).

A `/spawn --model <id>` override replaces the list if `overridable: true`
and the account offers the id. If no candidate matches, the spawn fails with
`NOSUCHMODEL` before anything is created. A candidate may set its own
`effort`; otherwise `model.effort` applies. Only list models that can do the
job: a cheaper but weaker model is not a fallback, it is a different breed.

flokpit's shipped roles name `claude-opus-5` and `claude-sonnet-5`; those ids
are kept as second candidates so breeds still spawn on accounts that do not
offer the 5.5 models yet. The renderer emits the chosen id into flokpit's
`RoleSpec.model`.
