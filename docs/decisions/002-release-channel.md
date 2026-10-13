# 002 - The distribution channel: GitHub releases with human-cut tags

Status: **accepted** by dennisjay on 2026-10-13 (instruction in
#flokpit-formations-dev, 09:59: GitHub Releases, "reasonable version numbers",
bunny.net kept for now, flokpit switched over).
Supersedes decision 9 of `001-contract-delivery-to-flokpit.md` ("the pin is a
configured `<short sha>.tar.gz` key in the bunny.net zone").
Refined by `003-release-delivery-review.md` (version scheme `vX.Y.Z`, first tag
`v0.1.0`, the digest is the pin, asset-host question); where the two differ,
003's table says which wins.
Author: bot-developer-bot-planner-dennis (developer).
Decision owner: dennisjay.

## Problem

Decision 9 of memo 001 made the pin a bunny.net storage key: flokpit would be
configured with `<short sha>.tar.gz` and fetch it from the storage zone with an
`AccessKey`. Two things changed after that decision:

- `flokpit/formations` is **public** now, so the contract does not need a
  credentialed channel at all.
- A bunny.net storage zone is readable only with the zone key, so every
  consumer - flokpit in the cluster, an on-prem install, a developer
  reproducing a validation failure - needs a shared secret to read public
  documentation. The key is also a write key in the publishing job, so handing
  it out is not an option; a second read-only key would be one more thing to
  rotate.
- There is nothing human-readable about `0f3a9c1.tar.gz`. "Which breeds does
  this install run?" has no answer a person can repeat.

## Decision

1. The public distribution channel is **GitHub Releases** of
   `flokpit/formations`.
2. Versions are **human-cut semver tags** `v0.1.0`, `v0.2.0`, ... (rules in 003) A release happens
   because a person pushes a tag, not on every push to `main`. No automatic
   per-commit release.
3. A tag `v*` runs the full validation matrix first; only if every breed and
   formation validates does the `release` job publish. The release carries
   `formations-<tag>.tar.gz` and `formations-<tag>.tar.gz.sha256`.
4. **The pin is a release tag, verified by digest.** flokpit is configured with a tag and its sha256 and fetches

       https://github.com/flokpit/formations/releases/download/<tag>/formations-<tag>.tar.gz

   with no credentials, verifies the archive against the configured sha256 (the `.sha256` next to it is the human-readable copy; a tag can be moved, the digest cannot), extracts it and
   validates the breeds against the `specs/*.schema.json` from that same
   archive. Bumping breeds stays a deliberate configuration change, which is
   what B-1 requires.
5. The bunny.net upload stays **live but deprecated**: pushes to `main` still
   write `<short sha>.tar.gz` and overwrite `LATEST` in the zone, so nothing
   that pins a key today breaks. The job and the two repository secrets go away
   once the last consumer reads releases. The job carries that note in
   `.github/workflows/validate.yml`.
6. Both channels ship the **same archive**, built by one script,
   `scripts/build-archive.sh`: `breeds/`, `formations/`, `specs/` and
   `scripts/validate.py`, reproducible tar (`--sort=name`, fixed owner,
   `--mtime` of `HEAD`, `gzip -n -9`). Two builds of a commit have the same
   sha256. This is also where decision 1 of memo 001 (`specs/` and the
   validator belong in the archive) finally lands.

## Consequences

- Anonymous `curl` of a documented URL is the whole install path; no secret
  reaches a consumer, and an on-prem box with internet needs nothing else.
- A release is immutable and listed, so "we run `v0.1`" is a sentence a person
  can say and anybody can check.
- `LATEST` in the bunny zone is deprecated together with the upload, so the
  question memo 001 left open - whether a dev-only `FORMATIONS_FOLLOW_LATEST`
  may resolve `LATEST` at startup - is moot for new consumers: there is no
  "latest" to resolve in the release channel, only tags.
- Ordering for the flokpit side is unchanged and still sharp: the release must
  exist **before** flokpit bumps its pin, and the old `software-architect` /
  `ui-tester` role files may only be deleted after that.
- Air-gapped installs are out of scope (assumption confirmed in the plan: "on
  prem has internet"). If one ever appears it needs a documented offline-bundle
  path; the reproducible tar makes that a copy, not a rebuild.

## Not decided here

- Whether the repository gets a `LICENSE`. Public with no licence means all
  rights reserved, so an on-prem customer may not legally redistribute the
  archive even though they can download it. dennisjay has to name a licence.
- When exactly the bunny.net job is removed; that is one PR after the flokpit
  pin is a tag.
