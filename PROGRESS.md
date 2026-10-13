# Progress

## Done

- 2026-10-13: the nine edits the twelve decisions of
  `docs/decisions/001-contract-delivery-to-flokpit.md` require, as one PR
  (branch `flokpit/bot-developer-dennisjay`): `specs/` and
  `scripts/validate.py` in the published archive, the archive description in
  `CLAUDE.md`, B-10 (breed wins on a name clash), B-11 and the phase-0 table
  verdicts, the decided `/fly` and `/land` vocabulary in CONCEPT 5.9, rule 2
  of `docs/resources/skills/security.md`, the optional `name` in
  `$defs/skill`, the breed rename `software-architect` to `architect` and
  `ui-tester` to `tester`, and the decision memo itself.
- 2026-10-13: decision 13 (item 10): `breeds/developer.yaml` `max_turns` 60 ->
  512, with the narrowing comment in `formations/bug-sweep.yaml` corrected.

- 2026-10-13: the release channel (decision 002). `scripts/build-archive.sh`
  builds the one reproducible archive (`breeds formations specs
  scripts/validate.py`, same sha256 across builds) used by both publish paths;
  `docs/decisions/002-release-channel.md` supersedes
  decision 9 (pin = release tag, human-cut tags, bunny deprecated-but-live);
  `docs/CONCEPT.md` 5.1, B-1 and phase-0 row 3 plus the `CLAUDE.md` archive
  section carry the release URL shape.

## Next

- `.github/workflows/validate.yml` still has to be committed by a human: the
  agent token has no GitHub `workflow` scope, so the push of that file is
  rejected. The exact, cleanly applying diff is
  `docs/patches/002-release-workflow.patch` (`git apply` it on `main`): tags
  `v*` trigger the workflow, a `release` job after the validation matrix runs
  `gh release create` with `formations-<tag>.tar.gz` + `.sha256`, and the
  bunny.net job uses `scripts/build-archive.sh` and is marked deprecated. That
  diff is also what closes issue #1 (`specs/` and the validator in the
  archive). Delete the patch file once it is in.
- A human merges the release-channel PR and then pushes the tag `v0.1.0`; the
  `release` job publishes the first archive that contains `specs/` and
  `scripts/validate.py`. Agents cannot do either: no merge rights, and
  `gh release` / tag pushes are outside the agent tool allowlist.
- Only after that release exists may flokpit bump its pin to the tag and
  delete its old `software-architect` / `ui-tester` role files.
- Remove the deprecated bunny.net `publish` job and its two repository secrets
  once no consumer reads the storage zone any more.
- `LICENSE` is still missing; public with no licence = all rights reserved, so
  an on-prem customer may not redistribute the archive. dennisjay names the
  licence (MIT or Apache-2.0), then a bot commits it.
- Open, not decided, both flagged in the memo: whether B-1 sanctions a
  dev-only `FORMATIONS_FOLLOW_LATEST`, and whether `name` is filled in for the
  skills of all six breed files (a follow-up to the schema change).
