# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`formations` is the central store for describing the agents that run in
[flokpit](../flokpit) (sibling checkout; its design docs are in
`../flokpit/docs`, an OKF bundle as well). flokpit is the runtime: Claude Code
agents in Kubernetes pods coordinating through an IRC-style chat backed by
Temporal. This repository holds the content those agents are built from. The
concept is in `docs/IDEA.md`; read it before changing anything conceptual.

There is no code to build or test yet; the repository is documentation plus
one maintenance script.

## Vocabulary

- **Breed**: a kind of agent (developer, reviewer, planner, ui-tester,
  software-architect, project-manager). flokpit calls this a *role*
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
  Skills, MCP); see `docs/resources/portable-agents/summary.md` for the
  proposed `breeds/<name>/{breed.yaml, AGENTS.md, skills/}` layout.

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
