# 001 - How flokpit gets the breed and formation contract

Status: **accepted** by dennisjay on 2026-10-13 (request
`01M4T9VPG4MQW3RHJ5G54Q59SK`), to be merged to `main`; see "Decision log".
Author: bot-consultant-dennisjay (consultant),
requested in #flockpit-dev by bot-planner-dennisjay for flokpit issue #200.
Decision owner: dennisjay.

## Problem

The three developer agents implementing breeds and formations in
`flokpit/flokpit` (issue #200, workers W1-W3) cannot read this repository:
their `gh` is scoped to `flokpit/flokpit` and their pods have no egress to
bunny.net. They therefore cannot read the files that are the contract for
their work: `specs/breed.schema.json`, `specs/formation.schema.json`,
`scripts/validate.py`, `breeds/*.yaml`, `formations/*.yaml`.

Their current workaround is a hand-written copy of the schemas under
`flokpit:docs/formations/`, which `docs/CONCEPT.md` forbids in two places:
X-2 ("flokpit MUST validate against them (vendored, not copied) and MUST NOT
add a second schema that disagrees") and X-4 ("Schema changes happen in
`flokpit/formations` first ..., then flokpit bumps the pin"). B-1 adds that
flokpit MUST load breeds from a pinned commit and MUST NOT follow a branch at
runtime.

A second, independent gap: the published artifact is not self-sufficient. The
`publish` job in `.github/workflows/validate.yml` packs only `breeds` and
`formations` into `<short sha>.tar.gz` and overwrites `LATEST`. The schemas
and the reference validator are **not** in the archive, so an implementation
that consumes only the archive cannot satisfy X-2 or X-3 ("Behaviour MUST
match `scripts/validate.py` on the same input ... shared fixtures").

## Stakeholders

- dennisjay - owner of both repositories, the only one who can grant repository
  access, approve schema changes (X-4) and decide the phase-0 items in
  `docs/CONCEPT.md` section 10.
- bot-planner-dennisjay - cuts and tracks the #200 tasks; needs a stable
  contract source to point workers at.
- W1-W3 (the developer agents) - need the field shapes for the renderer
  (SC-1..SC-5), the skills/OS/network fields (SC-8..SC-11) and the formation
  shape (SC-12..SC-16).
- Future flokpit runtime - loads breeds at startup; a diverging copy of the
  schema would silently accept or reject different files than CI here.

## Constraints

Technical:

- `specs/*.schema.json` are the contract (`docs/CONCEPT.md` section 3, X-2);
  `scripts/validate.py` is the reference behaviour (X-3).
- JSON Schema 2020-12, `additionalProperties: false` everywhere: a new field
  needs a schema change here first (`CLAUDE.md`, X-4).
- The archive on bunny.net contains `breeds/` and `formations/` only
  (`.github/workflows/validate.yml`).
- Agent pods have default-deny egress; allowlists are per breed domain names
  (`breeds/_base.yaml` `os.network.allow`), so a worker pod can only reach what
  its breed lists.
- `formations/README.md`: nothing in flokpit reads formations yet; all breeds
  and formations are `status: proposal`.

Organisational:

- Only humans grant repository access and approve schema PRs; agents here
  cannot open PRs or issues.
- The copies the workers hold today were produced from chat messages, not from
  the files; nothing keeps them in sync when this repository changes.

Deadlines: none that I read anywhere. Assumption: #200 is in flight now, so a
same-day unblock matters more than the long-term shape.

## Options

### A - Pin this repository as a git submodule in flokpit (`vendor/formations`)

What `docs/CONCEPT.md` 5.1 recommends: flokpit reads
`vendor/formations/breeds`, validates against the vendored
`vendor/formations/specs/*.json`, ships the files in a ConfigMap, and
`FLOKPIT_BREEDS_DIR` configures the path like `FLOKPIT_ROLES_DIR` today.

- Trade-offs: satisfies B-1, X-2, X-3 and X-4 without further work; the
  schemas, the fixtures and the reference validator are all present in the
  checkout; version bumps are visible as commits.
- Risks: the worker pods must be able to clone a second repository (submodule
  fetch needs `github.com` plus credentials for a second repo); if that is
  blocked, the option does not unblock anyone today. Submodules are extra
  ceremony for people who dislike them.
- Effort: S for the repository change, S-M for the pod/credential side if a
  second repository is not already reachable.

### B - Extend the published archive and consume it

Add `specs/` and `scripts/validate.py` to the tar in the `publish` job, and
let flokpit (and a one-off download into the worker pods) consume
`LATEST`/`<short sha>.tar.gz`.

- Trade-offs: no second git remote; keeps the pin explicit (a short sha); the
  archive becomes self-sufficient, which also fixes the X-2/X-3 gap for any
  future consumer.
- Risks: needs a change to the workflow in this repository (CI change - out of
  scope for me, a human or the planner's workers must do it); bunny.net egress
  must be allowed for whoever downloads, which is exactly what the worker pods
  lack today; `LATEST` is mutable, so a consumer must record the sha it used.
- Effort: S for the workflow, M for the flokpit-side fetch and pinning.

### C - Keep answering from chat, with a read-only mirror of the contract in flokpit

The current practice: I post field tables in `#flockpit-dev`, the workers keep
`flokpit:docs/formations/` as a temporary, clearly-marked copy for reading
only, and the implementation validates against whatever is vendored later.

- Trade-offs: unblocks the workers immediately, needs no access change; the
  copy can be deleted when A or B lands. The copy must be committed by a
  flokpit worker, not by me: my role allows exactly one file, this memo, and I
  have neither a checkout of nor write access to `flokpit/flokpit` (I also
  cannot read it; `gh api repos/flokpit/flokpit/contents/...` is denied).
- Risks: the copy is a second source of truth the moment this repository moves
  (X-2 forbids exactly that if anything validates against it); errors in my
  transcription become code; it does not give the workers the shared fixtures
  SC-5 and X-3 ask for. Highest risk of silent divergence.
- Effort: S now, and a recurring cost for every schema change.

## Decision by dennisjay, 2026-10-13

In #flokpit-formations-dev dennisjay chose **option B**: `specs/` is to be
included in the `tar.gz` on bunny.net. I may not change CI myself (see
"Out of scope"), so the exact change for whoever implements it:

In `.github/workflows/validate.yml`, job `publish`, step "Build archive", the
tar line is

    -cf - breeds formations | gzip -n -9 > "$archive"

and becomes

    -cf - breeds formations specs | gzip -n -9 > "$archive"

Nothing else needs to change: the entry list stays sorted by `--sort=name`, so
the archive stays reproducible, and upload, checksum, verify and `LATEST` are
unaffected. `tar -tzf "$archive"` in the same step will then list the three
directories, which is the cheapest check that it worked.

Open point I did not decide: whether `scripts/validate.py` goes in as well.
X-3 and SC-5 ask flokpit to produce the same accept/reject verdicts as that
script on shared fixtures, which is much easier to check when the reference
implementation travels with the schemas. It is one more word on the same line
(`breeds formations specs scripts`, or a single file path). I asked dennisjay.

The recommendation below is unchanged for the long run: B makes the archive
self-sufficient, but only a pinned checkout (A) gives flokpit a source it can
also diff and review.

## Decision log

Answers dennisjay gave to the decision requests I opened on 2026-10-13. I
record them verbatim in effect; I did not implement any of them.

### 1 - `scripts/validate.py` in the archive: approved -> it goes in

Request `01M4T90EK84NGXG4E54N025CKJ` in `#flokpit-formations-dev`, approved
09:24, no reason given. The published archive therefore carries **`breeds/`,
`formations/`, `specs/` and `scripts/validate.py`**, which makes X-3 and SC-5
checkable from the artifact alone - the only remaining delivery path after
decision 4.

The change in `.github/workflows/validate.yml`, job `publish`, step "Build
archive": the tar entry list

    -cf - breeds formations | gzip -n -9 > "$archive"

becomes

    -cf - breeds formations specs scripts/validate.py | gzip -n -9 > "$archive"

Two things whoever implements it must not get wrong:

- The path inside the archive must stay `scripts/validate.py`. The script
  derives its root from its own location (`ROOT = Path(__file__).resolve()
  .parent.parent`, scripts/validate.py:31) and then reads `ROOT/specs`,
  `ROOT/breeds`, `ROOT/formations`. Extracted with that layout it runs against
  the extracted tree with no changes; flattened into the root it looks for
  `specs/` one directory too high.
- Listing the single file rather than `scripts` is deliberate: `scripts/` also
  contains `okf.py` and whatever else arrives later, none of which is part of
  the contract. `--sort=name` keeps the archive reproducible either way.

`scripts/validate.py` has PEP 723 inline dependencies (pyyaml, jsonschema,
referencing) and a `uv run` shebang, so a consumer needs `uv` plus egress to
PyPI, or a pre-built environment. That is not in the archive and is the
consumer's problem - worth one sentence in the flokpit PR that adds the parity
test.

### 7 - Command vocabulary: approved -> `/fly` and `/land`

Request `01M4T9V2GPGY6VZS8C253SBA0T` in `#flockpit-dev`, approved 09:36, no
reason given. This settles **phase-0 item 5** (`docs/CONCEPT.md:426`): the
commands are `/fly <formation> [--repo url] [--task "..."]` and
`/land <flock>`, with `/spawn --formation <name>` kept as the deprecated alias
CONCEPT 5.9 already describes. `/kill --flock` is not the vocabulary.

Consequence here: the sentence at the end of 5.9 - "The vocabulary (`/fly`,
`/land`) is a proposal; agree on it before implementing" - and row 5 of the
phase-0 table must be rewritten into the decided rule. Another edit this
repository owes and nobody is assigned to.

Consequence there: it freezes the API paths, the WS command table and the UI
labels, which is why I asked - W2 was building the command surface in the same
hour. B-8 still applies to the wording ("User-facing text MUST say 'breed'; the
API SHOULD accept `role` as a deprecated alias for one release"), so `/spawn
--formation` as a deprecated alias is consistent with how the concept treats
the old vocabulary elsewhere.

### 8 - Content termination conditions: approved -> lead declares, human op confirms

Request `01M4T9V5CA2TE0X4VH8571V7J2` in `#flockpit-dev`, approved 09:36, no
reason given. This settles **phase-0 item 6** (`docs/CONCEPT.md:427`) on
CONCEPT's own preference, which 5.9 already describes: content conditions
(`all_items_verified`, `backlog_ready`) "are declared by the lead with intent
`DONE` and confirmed by a human op". No verifier agent, no workflow heuristics.

What this does not touch: `limits_reached` and `no_progress_rounds` stay
workflow-detected, and the hard limits (`max_agents`, `max_lifetime`,
`turn_budget`, `max_budget_usd`) end a flock server-side without asking anyone
(F-3, F-4). `human_stop` is still required in every formation's
`termination.conditions` by `specs/formation.schema.json:112`
(`"contains": {"const": "human_stop"}`).

Consequence: a flock whose lead declares done and whose human never confirms
runs until `max_lifetime` or `no_progress_rounds` ends it. That is now the
intended behaviour, not a bug - worth saying out loud in the flokpit PR,
because it means the `declared_by` / `confirmed_by` pair in the flock read
model is load-bearing, not decoration. CONCEPT 5.9 and the phase-0 table need
the preference turned into the rule; one more edit this repository owes.

### 9 - The pin: approved -> a configured archive key, `LATEST` only notices

**Superseded on 2026-10-13 by `002-release-channel.md`: the pin is a release
tag and the archive comes from a GitHub release; the bunny.net key below is
deprecated but still written.** The rest of this section is the original
record.

Request `01M4T9V8A5R61J65913S0W9DVA` in `#flockpit-dev`, approved 09:37, no
reason given. flokpit loads a **configured archive key** `<short sha>.tar.gz`;
`LATEST` may be fetched only to notice and log that a newer key exists.
Updating breeds is therefore a deliberate configuration change, which is what
B-1 (`docs/CONCEPT.md:333`) requires: "flokpit MUST load breeds from a pinned
commit of `flokpit/formations`; it MUST NOT follow a branch at runtime."

Why it needed asking: the publish job rewrites `LATEST` on every push to main
(`.github/workflows/validate.yml`, step "Update LATEST", lines 85-95,
`printf '%s' "$ARCHIVE" > LATEST`), so resolving `LATEST` at startup is
following main at runtime. bot-planner-dennisjay had asked the same question in
parallel (their request `01M4T9TVWX4S1KVVEMHD37HCEE`, also approved) and
reports the same answer plus "startup resolution survives behind a dev-only
env".

Caveat I did not decide and did not ask: that dev-only escape hatch has no
basis in this repository. B-1 has no development exemption, and an env var that
resolves `LATEST` at startup is exactly the behaviour B-1 forbids - acceptable
only if it is off by default, loudly logged, and never set in production. If it
is meant to be legitimate, B-1 needs a sentence saying so (X-4). I flag it;
dennisjay or the planner decides.

### 10 - This memo: approved -> it lands on `main`

Request `01M4T9VPG4MQW3RHJ5G54Q59SK` in `#flokpit-formations-dev`, approved
09:40, no reason given. The memo is accepted and belongs on `main`, so `main`
carries the record of why `specs/` and `scripts/validate.py` are in the
archive and which edits the decisions require.

I cannot do it: I may not open a pull request. Two ways it can happen - a
developer puts this file in the PR that makes the owed edits (that is request
`01M4T9VFAT4CN1RYB61H7GBE96`, still open), or dennisjay merges
`flokpit/bot-consultant-dennisjay` himself. The branch is pushed and contains
nothing but this file.

### 11 - Skill install directory name: approved -> add `name` to the skill schema

Request `01M4T9VK1Y7GR6Z88TJH43Z0KD` in `#flokpit-formations-dev`, approved
09:40, no reason given. The install directory name becomes **explicit**: an
optional `name` is added to `$defs/skill` in `specs/breed.schema.json` instead
of deriving it from the last segment of `path`. That removes the collision I
flagged (`receiving-code-review` appears in `breeds/developer.yaml` and
`breeds/reviewer.yaml`; two different sources shipping the same leaf name would
otherwise fight over one directory).

This is a schema change, so it is an X-4 PR in this repository and it must land
before flokpit can rely on the field. Shape I would use - the decision is the
field, not my phrasing:

    "name": { "type": "string", "pattern": "^[a-z0-9][a-z0-9._-]{0,63}$" }

Optional, not required, so no existing breed file becomes invalid; when absent
the consumer falls back to the last segment of `path`, which is what W3 already
does behind one function. Whether to then fill `name` in all six breed files is
a follow-up, not part of the schema change. Note `additionalProperties: false`
on `$defs/skill` means flokpit MUST NOT accept the field before the schema
change is published (X-2).

### 12 - A developer for the owed edits: approved

Request `01M4T9VFAT4CN1RYB61H7GBE96` in `#flokpit-formations-dev`, approved
09:40. dennisjay spawns a developer in `#flokpit-formations-dev` and I hand him
the whole change set. I cannot spawn one myself: `chat_spawn` returns
`FAIL SPAWN NOPRIVILEGES: Role consultant may not spawn developer`, and that is
independent of operator status.

The set, in the order that keeps `main` green at every step:

1. `.github/workflows/validate.yml`, job `publish`, step "Build archive":
   `-cf - breeds formations specs scripts/validate.py | gzip -n -9 > "$archive"`
   (decisions 1 and the earlier option-B choice).
2. `CLAUDE.md` lines 81-83: name `specs/` and `scripts/validate.py` in the
   archive sentence.
3. `docs/CONCEPT.md` B-10 (line 342): drop "MUST NOT coexist"; breed wins, log
   the shadowing once per load (decision 3).
4. `docs/CONCEPT.md` B-11 (line 343) and the phase-0 table (around line 420):
   rows 2, 5 and 6 are decided (breeds renamed; `/fly` + `/land` with the
   `/spawn --formation` alias; lead declares and a human op confirms); row 4
   becomes "decided for phase 1: `hello` stays a role" so the echo-runtime
   alternative is not lost; row 1 and row 3 record what was already chosen.
5. `docs/CONCEPT.md` 5.9: remove "The vocabulary (`/fly`, `/land`) is a
   proposal; agree on it before implementing" (decision 7).
6. `docs/resources/skills/security.md` rule 2 (lines 112-113): pin and licence
   stay, the location moves to the image build (decision 2). OKF bundle:
   `python3 scripts/okf.py check docs/resources` must pass and `index.md` is
   generated, never hand-edited.
7. `specs/breed.schema.json` `$defs/skill`: add the optional `name`
   (decision 11). This one is a contract change - separate commit, and it is
   the one a human must look at closely (X-4).
8. The rename `software-architect` -> `architect`, `ui-tester` -> `tester`
   with the file-and-line list in decision 6. Best as its own commit, because
   it is the only item that changes what the archive contains.
9. This memo, which dennisjay accepted for `main` (decision 10).

Evidence I would require: `uv run scripts/validate.py` exits 0 with its real
output pasted (6 breeds, 3 formations - the count does not change), the
`python3 scripts/okf.py check docs/resources` output, and a local rebuild of
the archive with `tar -tzf` showing `breeds`, `formations`, `specs` and
`scripts/validate.py`. No self-merge: dennisjay merges.

### 2 - Skill delivery: approved -> CONCEPT 5.6 wins, `security.md` is corrected

Request `01M4T90HPZD970SRXYSS545F1C` in `#flokpit-formations-dev`, approved
09:23, no reason given. **Skill bytes are fetched at image build time at their
pinned `ref`, not vendored into this repository.** `docs/CONCEPT.md` 5.6 stands
as written (fetch into `/opt/flokpit/skills/<source>/<ref>/<path>`, build fails
on an unfetchable ref or a missing licence, no runtime fetching).

`docs/resources/skills/security.md` rule 2 (lines 112-113) is now wrong where
it says "Vendor every adopted skill into this repository at a pinned commit":
the pinning and the licence requirement stay, the location changes to the
image build. The second half of the rule ("never install from a registry at
pod runtime") is unaffected and matches CONCEPT 5.6 point 3. Correcting that
sentence is a developer's edit; `docs/resources/` is an OKF bundle, so
`python3 scripts/okf.py check docs/resources` must pass and `index.md` must not
be hand-edited (`CLAUDE.md`).

Consequence for the archive: no skill content ever needs to travel in the
tar.gz, only the `skills[]` references that are already in the breed files.
The `review` gate is unaffected (see decision 5).

### 3 - B-10 vs "breed wins": approved -> the ruling stands, B-10 is edited here

Request `01M4T90MTM640YJZN0S120SC36` in `#flokpit-formations-dev`, approved
09:23, no reason given. **flokpit resolves a breed/role name clash by
preferring the breed** (the behaviour already implemented in flokpit PR #205,
the planner's D5/D8), and `docs/CONCEPT.md` B-10 (line 342) must be rewritten:
its clause "a breed and a role with the same name MUST NOT coexist" no longer
holds. The first half ("existing roles without a breed MUST stay available
until a breed replaces them") is unchanged.

Suggested wording for whoever edits it - the deciding part is the rule, not my
phrasing: a breed and a role with the same name MAY coexist; the breed wins and
the shadowing MUST be logged once per load. I did not edit `docs/CONCEPT.md`
(out of scope); this is the X-4 change dennisjay approved by approving the
ruling.

Together with decision 6 this is now a live case, not a hypothetical: after
`software-architect` becomes `architect`, flokpit's `roles/architect.yaml` is
shadowed by the breed. The two changes can land independently, in either order,
without breaking anything.

### 4 - Read access for the worker pods: rejected -> they stay repo-blind

Request `01M4T90S8JDQ95S3Y1V56EK6ZT` in `#flockpit-dev`, rejected 09:22, no
reason given. The #200 worker pods get **no** read access to
`flokpit/formations`. Consequences, all of them real today:

- The published archive is the only machine-readable delivery path into
  flokpit, which is what dennisjay already chose (option B). Option A (git
  submodule) remains possible for the flokpit *repository*, but it cannot be
  how a worker pod reads the contract.
- Every contract question keeps being routed through chat and through a
  consultant with a checkout. That is a standing dependency on an agent, not a
  pipeline; it is the main reason the schemas were transcribed by hand before.
- SC-5 (parity with `scripts/validate.py` on shared fixtures) is reachable
  only if the fixtures *and* the validator arrive in the archive. The `specs/`
  half is decided; the validator half is decision 1, still open. Until then the
  parity test cannot be written at all - the W2 developer parked it for exactly
  this reason.

### 5 - Unreviewed skills: approved -> `FLOKPIT_ALLOW_UNREVIEWED_SKILLS=1` on dev

Request `01M4T90W6C22F1PQ9EF941K618` in `#flockpit-dev`, approved 09:22, no
reason given. The dev cluster installs `review: pending` skills via
`FLOKPIT_ALLOW_UNREVIEWED_SKILLS=1`; production still requires
`review: approved` (`docs/CONCEPT.md` 5.6 point 4). Every skill in
`breeds/*.yaml` is `pending` today, so without this flag #200 would ship with
no skills at all.

What this does **not** change: the review gate itself. Approving a skill stays
a human step with a recorded review (`docs/resources/skills/security.md`
rule 3), and the schema still has no field for that record - see "Open risks".
The flag is an escape hatch for the dev cluster, not an approval.

### 6 - B-11 / phase-0 item 2: who renames? Rejected -> the breeds are renamed

Request `01M4T90ZAT2SJJZZ0GYN0WQDKQ` in `#flockpit-dev`, rejected by dennisjay
at 09:22, no reason given. Approve meant "flokpit renames its roles", reject
meant "the two breed files here get renamed". So: **`software-architect`
becomes `architect` and `ui-tester` becomes `tester` in this repository**, and
flokpit keeps its role names. `docs/CONCEPT.md` B-11 (line 343) is thereby
decided and should be rewritten from a question into the rule.

I may not make this change (see "Out of scope"). The complete change set for
whoever does, from `grep -rn 'software-architect\|ui-tester'`:

- rename the files `breeds/software-architect.yaml` -> `breeds/architect.yaml`
  and `breeds/ui-tester.yaml` -> `breeds/tester.yaml`, and change `name:` in
  both (line 3 each) - `scripts/validate.py:94` requires name == file stem.
- `breeds/software-architect.yaml:76` `may_spawn: [developer, reviewer,
  ui-tester]`; `breeds/project-manager.yaml:73` `may_spawn:
  [software-architect, planner, ui-tester]` and the prose at :29.
- `formations/feature-team.yaml`: `lead.breed` (:9), member (:19),
  `spawn_tree` key and targets (:24), `handoffs` keys and `to` (:35, :37, :38),
  the description (:4) and the comment at :59. `verification.optional:
  [ui-tester-passed]` (:47) is a condition name, not a breed name - rename it
  only if the deciders want to; validate.py does not check it.
- `formations/product-discovery.yaml`: members (:13, :16), `spawn_tree`
  (:24, :25), `handoffs` (:38, :39, :40), prose at :32, comment at :62.
- `breeds/README.md:17-18`, `formations/README.md:15, :17`, `CLAUDE.md:22-23`,
  `docs/CONCEPT.md:253` and :343, `docs/IDEA.md:146, :161, :164`.
- `docs/resources/skills/` is an OKF bundle: `summary.md:64, 65, 81`,
  `skills-by-breed.md:4, 5, 118, 136, 140, 226` and `index.md:10`. `CLAUDE.md`
  says `index.md` is generated and must not be edited by hand, and
  `python3 scripts/okf.py check docs/resources` must pass before committing
  bundle changes. Possible that the bundle should keep the descriptive names;
  that is a judgement for the editor, not a validator rule.
- evidence: `uv run scripts/validate.py` exits 0 and still prints 6 breeds,
  3 formations (the count does not change, only the names).

Consequence that is now urgent, not hypothetical: after the rename a breed
named `architect` and the flokpit role `architect` have the **same name**, which
B-10 (`docs/CONCEPT.md:342`) forbids ("a breed and a role with the same name
MUST NOT coexist") and which flokpit PR #205 currently resolves as "breed
wins". Decision request 3 (B-10 vs "breed wins") is still open and now decides
what flokpit does the moment this rename lands: silently prefer the breed, or
reject the duplicate and require the role file to be deleted. The rename here
and the collision rule there must land together, otherwise `architect` and
`tester` behave differently from every other breed.

## Recommendation

Superseded by the decision log: dennisjay chose **B** for the delivery,
**rejected** read access for the worker pods (decision 4) and **approved**
putting `scripts/validate.py` into the archive (decision 1). That removes the
premise of the recommendation below - A cannot be how a worker pod reads the
contract, and C is no longer a stopgap but the standing situation for every
question the archive does not answer. With `specs/` and the validator in the
tar, option B does satisfy X-2 and X-3, so the substance of the recommendation
is met by B as decided; what is left is implementing it.

The original recommendation, kept for the record:

**A, with C as the explicit stopgap until A (or B) is in place.** Reason:
X-2, X-3 and X-4 are requirements of the concept the workers are implementing,
and only a vendored checkout gives them the schemas *and* the reference
validator for the parity tests (SC-5). C alone cannot satisfy SC-5 and will
drift; it is acceptable only as reading material, marked as a copy, deleted
when the submodule lands. Choose B over A only if the submodule turns out to be
the thing that blocks the pods (CONCEPT 5.1: "Choose it only if submodules
cause trouble"); in that case add `specs/` and `scripts/validate.py` to the
archive in the same change, because without them B does not satisfy X-2/X-3.

Whatever is chosen: the worker pods need read access to this repository (gh
scope or a clone credential), otherwise every future contract question is
routed through chat and through me.

## Open risks and unknowns

- Answered by decision 4: no read access for the worker pods. The residual
  risk is unchanged - until the archive carries `specs/`, the contract reaches
  them only through chat, and a transcription error becomes code.
- Answered by decision 11: an optional `name` is added to `$defs/skill`.
  Residual risk: until that schema change is published, `additionalProperties:
  false` means the field does not exist, so flokpit must keep deriving the
  directory from `path` and must not accept `name` early (X-2).
- Resolved by decision 2: the image build fetches skills at their `ref`,
  `docs/resources/skills/security.md` rule 2 (lines 112-113) is the sentence
  that must be corrected. Residual risk: that correction is not made yet, so
  the repository still states two different rules, and nobody has been assigned
  to fix it.
- Resolved by decision 5: the dev cluster runs with
  `FLOKPIT_ALLOW_UNREVIEWED_SKILLS=1`. Residual risk: every skill in
  `breeds/*.yaml` is still `review: pending` (`breeds/README.md`), so nothing
  can go to production until a human reviews them one by one, and no review has
  happened.
- The schema has no reviewer, date or checksum field for a skill review, while
  `security.md` rule 3 asks for a recorded review (who, when, commit). If that
  record is wanted in the file, it is a schema change (X-4).
- Resolved by decision 3: "breed wins on a name conflict" stands and
  `docs/CONCEPT.md` B-10 (line 342) must drop its "MUST NOT coexist" clause.
  Residual risk: that edit is not made yet, so this repository still forbids
  what flokpit PR #205 implements, and decision 6 turns `architect`/`tester`
  into a real clash.
- The same ruling assumes "the runtime validation uses the schemas from the
  fetched archive". The archive has no schemas (see Problem). Either option B
  lands or the runtime validates against something that is not the contract.
- bot-planner-dennisjay refers to seven phase-0 decisions in
  `flokpit:docs/decisions/002-200-breeds-formations-phase-0.md`;
  `docs/CONCEPT.md` section 10 lists six. I cannot read that file (no access to
  `flokpit/flokpit`), so I cannot say which item is additional or whether the
  chosen options match this repository.
- Phase-0 item 2 (name conflicts) is **decided**: see the decision log, the
  breeds are renamed to `architect` and `tester`. Not yet done, and it collides
  with B-10 until decision request 3 is answered.
- Phase-0 items 4 (echo runtime for `hello`), 5 (`/fly` and `/land`
  vocabulary) and 6 (who judges content termination conditions) remain open
  human decisions; CONCEPT only marks a preference for 1, 3 and 6.
- Nothing is open for me any more: all twelve decision requests are answered
  and recorded in the decision log. What is open is **work**, not decisions.
- No edit that any of the decisions requires has been made yet. The nine items
  of decision 12 are the complete list; until they land, this repository
  states or does several things that are no longer what was decided - most
  visibly, the published archive still contains only `breeds/` and
  `formations/`, so flokpit cannot validate against the vendored schemas
  (X-2) and SC-5 parity cannot be written. A developer was approved
  (decision 12) but has not joined `#flokpit-formations-dev` at the time of
  writing; earlier pods never did.
- Unknown: whether `docs/CONCEPT.md` should also record the ten decisions
  themselves (a section 10 rewrite) or only the rules they produce. I chose to
  keep the record here and to list only the rule edits for the developer. If
  dennisjay wants section 10 turned into a "decided" table, that is a second
  pass, not part of decision 12.
- Flagged, not decided, and now also carried by flokpit: a dev-only
  `FORMATIONS_FOLLOW_LATEST` escape hatch has no basis in B-1 (see decision
  9). bot-planner-dennisjay has instructed their developer to treat it as
  unsanctioned and to say so in their decisions file; making it legitimate
  needs a sentence in B-1 here, which only dennisjay can approve.

## Out of scope

- Any change to product code, tests, CI or configuration, here or in
  `flokpit/flokpit`. This memo is the only file I write.
- Changing `specs/*.schema.json`. That includes the optional `name` for
  `$defs/skill` that decision 11 approved, a runtime kind for the echo runtime
  of B-9, and review metadata for a skill: each is a human-approved PR in this
  repository, per X-4, written by a developer and merged by dennisjay.
- Adding `specs/` and `scripts/validate.py` to the `publish` job - described as
  option B, not done.
- Performing the `software-architect` -> `architect` and `ui-tester` ->
  `tester` rename of decision 6. I list the files; renaming breeds, formations
  and the OKF bundle is a developer's change, not mine.
- Vendoring skill content into this repository, and reviewing any skill
  (`review: pending` -> `approved`). Review stays a human step
  (`docs/CONCEPT.md` section 9).
- Deciding the phase-0 items, cutting #200 tasks, opening issues or PRs,
  spawning agents - the planner and dennisjay do that.
- Judging whether the workers' current copy under `flokpit:docs/formations/` is
  faithful; I cannot read that repository.
- Anything about flokpit's internal `Role` type, agentd or the egress proxy
  beyond what `docs/CONCEPT.md` states; I did not read the flokpit code.
