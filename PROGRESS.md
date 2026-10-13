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

## Next

- `.github/workflows/validate.yml` still needs the one-line tar change
  (`-cf - breeds formations specs scripts/validate.py`); the agent token has
  no `workflow` scope, so a human has to commit that line.
- A human merges that PR; then the publish job writes the first archive that
  contains `specs/` and `scripts/validate.py`.
- Only after that archive is published may flokpit bump its pin and delete its
  old `software-architect` / `ui-tester` role files.
- Open, not decided, both flagged in the memo: whether B-1 sanctions a
  dev-only `FORMATIONS_FOLLOW_LATEST`, and whether `name` is filled in for the
  skills of all six breed files (a follow-up to the schema change).
