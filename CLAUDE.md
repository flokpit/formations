# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`formations` is the central store for describing the agents that run in
[flokpit](../flokpit) (sibling checkout; its design docs are in
`../flokpit/docs`, an OKF bundle as well). flokpit is the runtime: Claude Code
agents in Kubernetes pods coordinating through an IRC-style chat backed by
Temporal. This repository holds the content those agents are built from. The
concept is in `docs/IDEA.md`; read it before changing anything conceptual.
`docs/CONCEPT.md` is the implementation brief for flokpit (requirements with
ids, success criteria); keep it consistent with `breeds/`, `formations/` and
`specs/` when they change.

There is no code to build or test yet; the repository is documentation plus
one maintenance script.

## Vocabulary

- **Breed**: a kind of agent (developer, reviewer, planner, tester,
  architect, project-manager). flokpit calls this a *role*
  (`roles/*.yaml`, `RoleSpec` in `../flokpit/docs/concepts/agent_spawner.md`
  section 8); do not use "role" here. A breed defines pod resources, OS
  permissions, skills, the `AGENTS.md` main instruction, runtime features,
  model choice, limits, lifecycle, tool permissions and spawn/chat privileges.
- **Formation**: a predefined swarm template (breeds, counts, lead, hand-offs,
  verification, termination). **Flock**: a running formation. **Lead**: the
  agent orchestrating a flock.

## Constraints from flokpit that shape this repository

- Agents run `claude -p --bare`: skills, hooks, settings and `CLAUDE.md` in a
  cloned repository are ignored on purpose. Breed skills must reach the agent
  through the image or `flokpit-agentd` (personal scope `~/.claude/skills`).
- Third-party skills are adopted only vendored and pinned to a commit, after
  review (rules in `docs/resources/skills/security.md`).
- Breeds should stay vendor-neutral where a standard exists (AGENTS.md, Agent
  Skills, MCP); see `docs/resources/portable-agents/summary.md`. The main
  instruction lives inline in the breed YAML and is rendered into `AGENTS.md`.

## Breeds (`breeds/`)

One YAML file per breed (`formations/v1alpha1`), all extending
`breeds/_base.yaml` (deep merge: maps merge, lists and scalars replace). The
schema is documented in `breeds/README.md` and enforced by
`specs/breed.schema.json`; keep README, schema and files in sync.
Skills are referenced by repository, commit and path and stay
`review: pending` until someone has read them.

## Formations (`formations/`)

One YAML file per formation (`formations/v1alpha1`), schema in
`formations/README.md`. Formations may only narrow breeds: `spawn_tree`
entries must be subsets of the breed's `privileges.may_spawn`, member
`overrides` may only lower limits, and `limits.max_agents` must cover the
lead plus every member at its `count.max`.

## Validation

`specs/breed.schema.json` and `specs/formation.schema.json` (JSON Schema
2020-12) define the file shapes; `scripts/validate.py` checks every file
against them plus the cross-file rules (merged breeds complete, references
exist, formations only narrow). Run it after any change to `breeds/`,
`formations/` or `specs/`; dependencies come from the script's inline
metadata via `uv`:

```sh
uv run scripts/validate.py              # all breeds and formations
uv run scripts/validate.py breeds/x.yaml  # errors for these files only
```

A new field needs a schema change first: unknown keys are rejected.

CI (`.github/workflows/validate.yml`) runs the validator once per breed and
formation file, as a matrix built from `breeds/*.yaml` and
`formations/*.yaml`, on every push to `main` and every pull request.

The release ships an archive built by `scripts/build-archive.sh`:
`README.md`, `LICENSE`, `breeds/`, `formations/`, `specs/` and
`scripts/validate.py` in a reproducible
tar.gz (the validator keeps that exact path, so it runs in place after
extraction), plus a `.sha256` next to it.

The public channel is **GitHub Releases** with human-cut tags (`v0.1.0`, `v0.2.0`,
...; see `docs/decisions/002-release-channel.md`). Pushing a tag `v*` runs the
validation matrix and then the `release` job, which attaches
`formations-<tag>.tar.gz` and its `.sha256` to a release. Consumers download

```
https://github.com/flokpit/formations/releases/download/<tag>/formations-<tag>.tar.gz
```

unauthenticated, and the pin is that tag.

The bunny.net storage zone upload (`<short sha>.tar.gz` plus `LATEST`) is gone;
the zone was deleted. Releases are the only publish path.

## Research bundle (`docs/resources/`)

An Open Knowledge Format v0.2 bundle
(https://github.com/GoogleCloudPlatform/open-knowledge-format, spec
`SPEC.md`). Conventions are in `docs/resources/conventions.md`; the essentials:

- Every non-index page has frontmatter with `type`, `title`, `description`,
  `tags`, `sources` (`id`, `resource`, `title`), `generated: { by, at }`,
  `status: draft`, and `stale_after` for fast-moving research. `resource` only
  when the page describes one concrete asset.
- Claims cite sources with footnotes keyed to `sources[].id`, footnote text =
  source title. Links inside the bundle are bundle-relative (`/skills/summary.md`).
- In table rows, escape `|` inside code spans as `\|`.
- `index.md` files are generated; never edit them by hand. New directories
  need a heading and description in `DIRS` in `scripts/okf.py`.
- Every change gets an entry in `docs/resources/log.md` (newest date first).

Commands:

```sh
python3 scripts/okf.py index docs/resources   # regenerate all index.md files
python3 scripts/okf.py check docs/resources   # OKF conformance, footnotes, links
```

Run `check` before committing changes to the bundle.
