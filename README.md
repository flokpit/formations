# formations

Breeds and formations for [flokpit](https://github.com/flokpit/flokpit): the
content that describes the agents a flokpit swarm runs.

- A **breed** is a kind of agent (developer, reviewer, planner, tester,
  architect, project-manager): pod resources, OS permissions, skills, the
  `AGENTS.md` main instruction, runtime features, model, limits, tool
  permissions and spawn/chat privileges. See [`breeds/`](breeds/README.md).
- A **formation** is a predefined swarm template: which breeds, how many, who
  leads, how work is handed off and verified, and when the flock stops. See
  [`formations/`](formations/README.md).
- [`specs/`](specs/) holds the JSON Schemas (2020-12) both file types are
  validated against.

The files are vendor-neutral YAML. flokpit loads them, but nothing in them
requires flokpit: any runtime can read the same breeds and formations.

The idea is in [`docs/IDEA.md`](docs/IDEA.md); the implementation brief for
flokpit is [`docs/CONCEPT.md`](docs/CONCEPT.md).

## Use a release

Releases are human-cut tags (`v0.1.0`, `v0.2.0`, ...). Each one ships a
reproducible archive with `breeds/`, `formations/`, `specs/`,
`scripts/validate.py`, this README and the LICENSE, plus its checksum. No credentials are needed:

```sh
tag=v0.1.0
base=https://github.com/flokpit/formations/releases/download/$tag
curl -fsSLO $base/formations-$tag.tar.gz -O $base/formations-$tag.tar.gz.sha256
sha256sum -c formations-$tag.tar.gz.sha256
mkdir formations && tar -xzf formations-$tag.tar.gz -C formations
(cd formations && uv run scripts/validate.py)
```

Pin the tag *and* its sha256: a tag can be moved, the digest cannot. Why, and
how the channel works: [`docs/decisions/`](docs/decisions/).

## Work on this repository

```sh
uv run scripts/validate.py                 # all breeds and formations
uv run scripts/validate.py breeds/x.yaml   # just these files
```

CI runs the validator once per file on every push to `main` and every pull
request. A new field needs a schema change first: unknown keys are rejected.
Contributor guidance for coding agents is in [`CLAUDE.md`](CLAUDE.md).

## Layout

| Path | Contents |
|---|---|
| `breeds/` | one YAML file per breed, all extending `_base.yaml` |
| `formations/` | one YAML file per formation |
| `specs/` | JSON Schemas for both |
| `scripts/` | validator, archive builder, bundle tooling |
| `docs/` | idea, concept, decision memos, research bundle |

## License and attribution

[MIT](LICENSE). Use it in commercial or non-commercial products, modify it,
ship it, including in products similar to flokpit. The one condition is to keep
the copyright and license notice: a short credit in your product's
third-party / libraries section is enough, for example:

> formations - breeds and formations for agent swarms.
> Copyright (c) 2026 Dennis Jöst, MIT License.
> https://github.com/flokpit/formations
