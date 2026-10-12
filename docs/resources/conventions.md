---
type: Guide
title: Bundle Conventions
description: How documents in this OKF v0.2 bundle are written, linked, sourced and maintained.
tags: [okf, conventions, meta]
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: Open Knowledge Format (OKF) v0.2 specification
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-12T00:00:00Z }
---

# Bundle Conventions

`docs/resources/` is an Open Knowledge Format v0.2 bundle: a directory of
markdown concept documents with YAML frontmatter, an `index.md` in every
directory and a `log.md` at the root.[^okf-spec]

## Frontmatter

| Field | Use here |
|---|---|
| `type` | required; e.g. `Summary`, `Reference`, `Comparison`, `Analysis`, `Guide` |
| `title`, `description`, `tags` | always set; `description` is copied into `index.md` |
| `resource` | only when a concept describes one concrete asset (a repository, a spec); omitted for syntheses |
| `sources` | every external or internal material used, each with `id`, `resource`, `title` |
| `generated` | `{ by: <producer>/<version> or human:<id>, at: <ISO 8601 UTC> }` |
| `verified` | added only after a human (`human:<id>`) or process checked the content |
| `status` | `draft` until verified |
| `stale_after` | set on fast-moving research: one month for leaderboards, two months otherwise |

## Body

- Per-claim attribution with footnotes whose label is a `sources[].id` and
  whose text is the source title.
- Links between concepts are bundle-relative (`/skills/summary.md`); links
  out of the bundle (for example to `docs/IDEA.md`) are relative.
- Structural markdown (headings, tables, lists) over prose.
- Unverified claims are marked "unverified" in the text.

## Maintenance

- `index.md` files are generated: `python3 scripts/okf.py index docs/resources`.
- Conformance and link check: `python3 scripts/okf.py check docs/resources`.
- Every change gets a dated entry in [the log](/log.md), newest first.

[^okf-spec]: Open Knowledge Format (OKF) v0.2 specification
