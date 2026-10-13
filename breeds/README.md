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
| [architect](architect.yaml) | frontier | ADRs, architecture docs | feature team |
| [planner](planner.yaml) | frontier | issues, plans | bug sweep |
| [project-manager](project-manager.yaml) | balanced | issues, specs, status reports | product discovery |

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
| `runtime` | 5. runtime features | `image` (`base` or a variant), `features` (Dev Container Feature references with `options`) |
| `model` | 6. model choice | `class` (`frontier`, `balanced`, `fast`), `effort`, `overridable`, `candidates` (ordered list of `{provider, id, effort?}`; see below) |
| `limits` | 7. limits and budgets | `max_turns`, `max_budget_usd` (0 = no cap), `summary_budget_usd`, `tighten_only` |
| `lifecycle` | 8. lifecycle | `hello`, `idle_timeout`, `max_lifetime`, `summary_deadline` |
| `tools` | 9. tool permissions | category → pattern → `allow` or `deny`; categories `read`, `edit`, `bash`, `webfetch`, `websearch`, `mcp`, `subagents`; `deny` wins over `allow`, and anything not allowed is denied (agents run without prompts); `{branch}` in a pattern is the agent's branch |
| `privileges` | 10. spawn and chat | `may_spawn` (breed names), `chat.mode` (`voice` = `+v`), `chat.op` |
| `workspace`, `credentials`, `handoff` | later features | repository clone and branch prefix; GitHub access requested from the flokpit gateway; what the breed must deliver when done |

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
