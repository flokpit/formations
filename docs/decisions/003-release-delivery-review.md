# 003 - Release delivery: review, version scheme and digest pin

Status: **accepted** by dennisjay on 2026-10-13 (decision
`01M4TZB2E18DZ0KPEB0H2211GD`, relayed in #flockpit-dev as
`01M4TZD76SRZTDAA5BDH11D7HS`): option A, annotated `vX.Y.Z` tags with `rc` as
prerelease, **first tag `v0.1.0`**, tag protection on, and B-1 amended so that
the digest pins and the tag only names it.

This memo was written in parallel with, and reconciled against,
`002-release-channel.md`. **002 is the decision of record for the channel**
(GitHub Releases, human-cut tags, `scripts/build-archive.sh`, bunny.net kept
deprecated). This memo adds to it and overrides it only where the table below
says so.

| Point | 002 as first written | This memo | Resolution |
|---|---|---|---|
| Tag form | `v0.1`, `v0.2` | semver `vX.Y.Z`, first tag `v0.1.0` | **003**; 002, `CLAUDE.md`, `docs/CONCEPT.md` and `PROGRESS.md` updated |
| Checksum asset | `formations-<tag>.tar.gz.sha256` | `SHA256SUMS` | **002** (already built by `scripts/build-archive.sh`; `sha256sum -c` works next to it) |
| What the pin is | the tag | the digest; the tag only names it | **003**; B-1 in `docs/CONCEPT.md` amended |
| bunny.net | live, deprecated | delete the `publish` job | **002**: kept until the last consumer reads releases |
| Asset host | not covered | redirect host must be measured and allowlisted | **003**, still open (see below) |
| Archive layout | four entries, flat | the same | agree |

Still open: the asset-host rule (the host itself is being measured, not
guessed) and the budget cap for the developer breed.
Supersedes the delivery half of
`docs/decisions/001-contract-delivery-to-flokpit.md` together with 002
(its option B and its decision 9). Everything else in 001 - decisions 1-8 and
10-13, including decision 13 (`breeds/developer.yaml:82`, `max_turns` 60 ->
512) - stays in force and is not touched by this memo.

Author: bot-consultant-bot-planner-denni (consultant), requested in
#flockpit-dev by bot-planner-dennisjay-2 (task T1) after dennisjay decided on
2026-10-13 that `flokpit/formations` becomes public and ships fixed versions
as GitHub releases. Decision owner: dennisjay.

## Problem

The delivery path decided in 001 assumed a private repository and a bunny.net
storage zone: CI packs `<short sha>.tar.gz`, uploads it with a write secret
and overwrites a mutable `LATEST` key
(`.github/workflows/validate.yml`, job `publish`, lines 40-95). dennisjay has
replaced that premise: the repository becomes public and fixed versions are
GitHub releases. flokpit's loader (branch `feat/200-wp-a-breeds-loader`,
PR #204) is being written against whatever this repository publishes, so the
pin, the artifact name, its layout, its contents and the "a newer version
exists" source must be nailed down before that code is rewritten.

State when this memo was written, kept for the record; the update below
says what has changed on `main` since:

- The `publish` job packed only `breeds` and `formations`, while `CLAUDE.md`
  already described the four-entry archive. No published artifact satisfied
  X-2/X-3, and nothing in flokpit consumed bunny.net in production, so
  switching delivery costs no migration.
- **Update after reconciliation with 002:** `scripts/build-archive.sh` now
  packs all four entries for both channels; `docs/CONCEPT.md` 5.1, B-1 and
  phase-0 row 3 and `CLAUDE.md` describe the release model; 001 carries its
  "superseded" pointer. The `release` job is now in `validate.yml`. Still owed to a human (agent
  tokens have no `workflow` scope): pushing the tag `v0.1.0`, tag protection, the asset-host allowlist and
  the repository-visibility check. The job checks the tag against the regex
  below and marks `-rc` releases as prerelease.

## Stakeholders

- dennisjay - owner of both repositories; the only one who can make the
  repository public, change `.github/workflows/*` (agent tokens lack the
  `workflow` scope), create tags and releases, delete the bunny.net secrets
  and approve contract changes (X-4, `docs/CONCEPT.md:381`).
- bot-planner-dennisjay-2 - cuts T2-T5; needs the pin format and a release
  that actually exists before T2 (`FORMATIONS_VERSION`, `FORMATIONS_SHA256`)
  can be finished.
- The T2 developer on `feat/200-wp-a-breeds-loader` - implements fetch,
  verify, cache, notify-only latest check, ConfigMap annotations.
- Future flokpit runtime and any other consumer - needs an artifact that is
  self-sufficient (schemas plus reference validator) and whose digest does not
  change under it.

## Constraints

Technical:

- B-1 (`docs/CONCEPT.md:330`): "flokpit MUST load breeds from a pinned commit
  of `flokpit/formations`; it MUST NOT follow a branch at runtime." A release
  tag is not literally a commit, and a git tag is mutable (it can be force
  pushed to another commit). Only a verified content digest makes the pin
  immutable. B-1 needs one sentence (see "Answers to the planner's questions").
- X-2 (`:379`): flokpit validates against the schemas in `specs/`, vendored,
  not copied. X-3 (`:380`): behaviour must match `scripts/validate.py` on the
  same input. Both are only checkable if both travel in the artifact.
- `scripts/validate.py:31` derives its root from its own location
  (`ROOT = Path(__file__).resolve().parent.parent`) and then reads
  `ROOT/specs`, `ROOT/breeds`, `ROOT/formations`. The archive layout must keep
  the path `scripts/validate.py` relative to the archive root (001,
  decision 1).
- `scripts/validate.py` has PEP 723 inline dependencies (pyyaml, jsonschema,
  referencing) and a `uv run` shebang: a consumer needs `uv` plus PyPI egress,
  or a prepared environment. That is outside the artifact.
- Agent pods have default-deny egress with a per-breed host allowlist;
  `breeds/_base.yaml:37-39` allows exactly `github.com`, `api.github.com`,
  `codeload.github.com`. GitHub **release asset** downloads from
  `https://github.com/<owner>/<repo>/releases/download/...` answer with a
  redirect to a `*.githubusercontent.com` asset host, which is in neither that
  list nor the host allowlist the planner specified for T2. Auto-generated
  source tarballs are served by `codeload.github.com` without a cross-host
  redirect. (Redirect target host: GitHub's documented behaviour; I could not
  verify it from this pod - no network, and `gh release` is not in my tool
  allowlist. Whoever implements T2 must confirm the exact host and add it to
  the loader allowlist, and to `breeds/_base.yaml:39` if an agent pod is ever
  to download the artifact.)
- The repository default workflow permission is `contents: read`
  (`.github/workflows/validate.yml:9`). Creating a release needs
  `contents: write` on the release job.

Organisational:

- I may not write CI, create tags or cut releases (see "Out of scope"); T1
  items 3 and 4 are reported BLOCKED in the channel and specified here instead.
- Agent tokens have no `workflow` scope, so `.github/workflows/release.yml`
  must be committed by a human (same reason the one-line tar fix of 001 is
  still owed, `PROGRESS.md`).
- Repository visibility: I cannot verify from this pod whether
  `flokpit/formations` is already public. Treated as an assumption.

Deadlines: none that I read anywhere. #200 is in flight; T2 is blocked on this
memo and on a release that exists.

## Options

### A - Uploaded release asset `formations-<tag>.tar.gz` plus `.sha256`

A tag push `v*` triggers a release workflow: validate, build the archive with
the same reproducible recipe the `publish` job already uses
(`--sort=name --owner=0 --group=0 --numeric-owner --mtime=@<commit time>`,
`gzip -n -9`), write `formations-<tag>.tar.gz.sha256`, create the release with both files attached.
flokpit pins `FORMATIONS_VERSION=vX.Y.Z` plus `FORMATIONS_SHA256=<digest>`.

- Trade-offs: the bytes come from our own recipe and never change; the archive
  contains exactly the contract (four entries, no `docs/`, no `.github/`); the
  layout is identical to what 001 decided, so the T2 extract/validate code and
  `CLAUDE.md:80-88` stay true; the `.sha256` file is a human convenience while the
  configured digest stays authoritative.
- Risks: the download redirects to a `*.githubusercontent.com` asset host -
  the T2 allowlist and `breeds/_base.yaml:39` must be widened, or the loader
  must follow exactly one redirect to one named extra host (a rule a reviewer
  must look at, because "no foreign-host redirect" was a security
  requirement). One more workflow file that only a human can commit.
- Effort: S here (one workflow, one tag), S in flokpit.

### B - Pin GitHub's auto-generated source tarball from codeload

No workflow at all: flokpit fetches
`https://codeload.github.com/flokpit/formations/tar.gz/refs/tags/vX.Y.Z`.

- Trade-offs: zero upstream work beyond tagging; `codeload.github.com` is
  already in `breeds/_base.yaml:39` and in the T2 host list; no redirect to a
  foreign host; works for any tag, including one cut by hand.
- Risks: GitHub does not guarantee byte-stable generated archives (the
  compression layer has changed in the past), so a `FORMATIONS_SHA256` pin can
  start failing on an unchanged tag - the failure mode that is hardest to
  debug and that teaches people to switch verification off. The archive
  carries the whole repository (`docs/`, `.github/`, `CLAUDE.md`), so the
  contract is no longer a defined set of files, and it has a top-level prefix
  directory `formations-X.Y.Z/`, which needs `strip-components=1` or prefix
  discovery in the loader.
- Effort: XS here, S in flokpit (prefix handling, weaker verification).

### C - OCI artifact in `ghcr.io` (ORAS), pinned by digest

Push the same tar as an OCI artifact; flokpit pulls
`ghcr.io/flokpit/formations@sha256:...`.

- Trade-offs: immutability by digest is the registry's native model; same
  mechanism as the agent images; signing (cosign) and mirroring are
  straightforward later.
- Risks: a new host (`ghcr.io`) plus registry handling, a new client
  dependency (`oras`/`crane`) in the flokpit image, and a pin that is no
  longer human-readable in a ConfigMap annotation. It also drops the "a human
  opens the release page and reads the changelog" property, which is half the
  reason for going public.
- Effort: M here, M in flokpit.

## Recommendation

**Option A**, with the redirect-host question answered before T2 merges, and
the bunny.net path removed in the same PR.

Reasons, in order:

1. The digest pin is load-bearing. B-1 forbids following a moving target, and
   a git tag *is* movable; the only thing that makes `vX.Y.Z` a pin is that
   flokpit refuses an archive whose sha256 differs. Under option B that check
   can fail without anybody changing anything, which trains operators to turn
   verification off.
2. The artifact stays exactly the contract - the four entries 001 decided and
   `CLAUDE.md:80-88` already documents - instead of a copy of the whole
   repository including its CI.
3. The layout stays flat, so `scripts/validate.py:31` runs in place after
   extraction and the T2 extraction code from the bunny.net design survives
   almost unchanged.

I agree with the planner's recommendation on the artifact; the point their
task description did not account for is the redirect host.

### Specification for whoever implements it (T1 items 2-4)

Pin and naming:

- Tag: `vX.Y.Z` (semver, annotated). MAJOR = a change that can make a
  previously valid file invalid (field removed, constraint tightened, breed or
  formation renamed or deleted); MINOR = new optional field, new breed, new
  formation; PATCH = documentation, comments, validator fixes with unchanged
  verdicts. Pre-releases `vX.Y.Z-rc.N` are allowed, marked prerelease, and so
  stay out of `releases/latest`.
- Assets: `formations-<tag>.tar.gz` (for example `formations-v0.1.0.tar.gz`)
  and `formations-<tag>.tar.gz.sha256` with the one `sha256sum` line for that
  file (both produced by `scripts/build-archive.sh`).
- Download URL:
  `https://github.com/flokpit/formations/releases/download/<tag>/formations-<tag>.tar.gz`
- Archive layout: **no top-level prefix directory**. The four top-level
  entries are `breeds/`, `formations/`, `specs/` (both schemas) and
  `scripts/validate.py` (that exact path, nothing else from `scripts/`).
  Extraction target equals archive root; the loader should reject any entry
  that is absolute, contains `..`, or whose first segment is not one of those
  four.
- Reproducible build, same recipe as `.github/workflows/validate.yml:63-66`,
  with the `--mtime` of the tagged commit.

Release workflow (`.github/workflows/release.yml`), as a specification - a
human must commit it, agent tokens have no `workflow` scope:

- trigger `push: tags: ['v*']`; `permissions: contents: write`.
- steps: checkout, `astral-sh/setup-uv@v6`, `uv run scripts/validate.py` over
  all files (a tag that does not validate must not become a release), build
  the archive with the recipe above, write the `.sha256` file, list the archive with
  `tar -tzf` into the job summary, then create the release with both assets
  and the digest in the release notes.
- the job must fail if the tag does not match
  `^v[0-9]+\.[0-9]+\.[0-9]+(-rc\.[0-9]+)?$`.

Retiring the old path: 002 keeps the `publish` job live but deprecated; when
the last consumer reads releases, delete it and have dennisjay delete the
repository secrets `FORMATIONS_BUNNY_BUCKET_NAME` and
`FORMATIONS_BUNNY_BUCKET_WRITE_SECRET`.

Second upstream item, added after the planner's review
(`01M4TZ6XK6NPDG1DDCQS60Q300`): `breeds/_base.yaml:39` currently allows
`[github.com, api.github.com, codeload.github.com]`. If an **agent pod** is
ever to download a release asset (for example a consultant reading the
contract, or a developer running the parity fixtures), the asset host must be
added there as well - a breed change in this repository, and therefore an
X-4-style change dennisjay approves, not just a loader setting in flokpit. The
exact host name is to be measured by the T2 developer
(`curl -sIL` on a public release asset through the egress proxy) and reported
in #flockpit-dev before either allowlist is written. If the asset host turns
out to be unreachable through the proxy, that is a decision for dennisjay
(allow it, or switch to option B for the agent-side path) - not a silent
fallback to the codeload tarball.

The redirect rule the planner adopted for the loader, recorded here so the two
repositories agree: follow at most one redirect, only to a host matching the
configured asset-host allowlist (suffix match, https, port 443), and verify
`FORMATIONS_SHA256` before the archive is cached or served, so the asset host
is never trusted.

Also owed, unchanged from 001 and now cheaper to do in one pass:
`docs/CONCEPT.md:128-136` (5.1 still recommends a git submodule), `:330`
(B-1) and `:424` (phase-0 row 3, still `<short sha>.tar.gz` plus `LATEST`)
must be rewritten to the release model.

### Upstream to-do list for dennisjay

Everything this decision needs in `flokpit/formations`, in the order that keeps
`main` green. Open items (a), (c), (f), (g) cannot be done by an agent: they touch
CI, breeds, secrets or repository settings, and agent tokens have no `workflow`
scope.

| # | What | Where |
|---|---|---|
| a | **Applied**, including the tag-format check (a `release` job in `validate.yml`: tag trigger `v*`, `contents: write`, after validation, `scripts/build-archive.sh`, release with both assets). This replaces the separate `release.yml` specified above | `.github/workflows/validate.yml` |
| b | **Done** in `scripts/build-archive.sh`; the same patch makes the `publish` job call it | `scripts/build-archive.sh` |
| c | Add the release-asset host to the agent egress allowlist; without it no agent pod can ever fetch an asset | `breeds/_base.yaml:39` (today `[github.com, api.github.com, codeload.github.com]`) |
| d | **Done** (5.1 and phase-0 row 3 by 002; B-1 digest wording in this reconciliation) | `docs/CONCEPT.md` |
| e | **Done** (decision 9 carries the pointer to 002) | `docs/decisions/001-contract-delivery-to-flokpit.md` |
| f | **Deferred by 002**: the `publish` job and the two secrets stay, marked deprecated, until the last consumer reads releases. Then delete both | `.github/workflows/validate.yml`, repository secrets |
| g | **Approved, pending execution.** Push the first tag `v0.1.0` and post tag, sha256 and asset URL in #flockpit-dev; tag protection on | GitHub, repository settings |

The asset host in (c) is **measured, not guessed**: bot-developer-bot-planner-denn-4
probes the `Location` header of a public release asset through the egress proxy
and reports the host(s) in #flockpit-dev; that measured name goes into the
loader allowlist and into `breeds/_base.yaml:39`. Nothing about the host has to
be trusted either way, because `FORMATIONS_SHA256` is verified before the
archive is cached or served - a wrong or hostile asset host can only cause a
failed load, never a silently different contract.

## Answers to the planner's questions

- **Item 2 (artifact):** agreed - uploaded asset, not the auto-generated
  tarball, for the reasons above. Layout flat, no prefix directory.
- **Item 5 (newer-version source):** `https://api.github.com/repos/flokpit/formations/releases/latest`
  is the right source, notify-only. Two properties the loader must respect: it
  returns the newest **non-draft, non-prerelease** release (so `-rc.N` tags are
  invisible to it, which is intended), and unauthenticated requests share
  GitHub's per-IP rate limit, so the check must be low-frequency, cached, and a
  failure must stay a warning, never a startup error. `api.github.com` is
  already in `breeds/_base.yaml:39`.
- **Item 5 (B-1):** yes, B-1 needs one upstream sentence, because a release tag
  is not a commit and tags are movable. Proposed wording (the rule, not my
  phrasing, is what needs approval): "flokpit MUST load breeds from a pinned
  release of `flokpit/formations`, identified by its tag and verified against a
  configured sha256 of the release asset; it MUST NOT resolve a branch, a
  moving tag or `releases/latest` at runtime." That is an X-4 edit here and
  needs dennisjay's approval - **open**, I did not decide it.
- **Item 5 (`FORMATIONS_FOLLOW_LATEST`):** unchanged from 001, decision 9 -
  **unsanctioned**. B-1 has no development exemption, so the T2 behaviour (off
  by default, WARN when set, ignored when a pin is present) is the most that is
  defensible today. Making it legitimate requires the B-1 sentence above to
  carve it out explicitly; dennisjay decides.
- **Item 6 (X-2):** holds unchanged. flokpit validates against the schemas
  inside the fetched archive and keeps no second copy; option A keeps `specs/`
  in the artifact, which is the only reason X-2 is satisfiable at all.
- **Item 6 (the temporary copy in flokpit):** with a public repository and a
  release that contains `specs/`, the copy under `flokpit:docs/formations/` has
  no remaining purpose and is the second source of truth X-2 forbids, so it
  should be deleted when T2 lands. Caveat: I cannot read `flokpit/flokpit`, so
  I cannot confirm what that directory contains today or whether anything
  imports it; the T2 developer must check before deleting.

## Open risks and unknowns

- **Not verified: the repository is public.** Everything here assumes
  unauthenticated reads of `github.com`, `api.github.com` and the asset host.
  I have no network access and no `gh repo view` in my tool allowlist.
- **The asset redirect host.** If the loader must not follow a redirect to a
  host outside `github.com` / `api.github.com` / `codeload.github.com`, option
  A does not work as specified. Either the allowlist gains the asset host (and
  `breeds/_base.yaml:39` too, if agent pods should ever fetch), or the rule is
  relaxed to "exactly one redirect, to one named host". Open for dennisjay and
  the T2 reviewer.
- **Tag immutability: decided** - tag protection is on (decision
  `01M4TZB2E18DZ0KPEB0H2211GD`). Residual risk: it is a repository setting
  nobody has verified as applied, and the digest check stays the real
  safeguard.
- **First version number: decided** - `v0.1.0`, pre-1.0 while the schema still
  moves (`status: proposal` everywhere, `formations/README.md`). Residual
  risk: the tag does not exist yet, so T2 pins a value that is not yet
  resolvable; the pin must stay configurable and must not be baked in.
- **The repository does not yet contain the archive contents it documents.**
  Until the tar entry list is fixed (owed since 001, `PROGRESS.md`), a release
  built from the current `publish` recipe would ship two directories instead of
  four. The release workflow must carry the correct recipe from the start.
- **Open risk kept on record (planner item 7):** `breeds/developer.yaml:82`
  sets `max_turns: 512` while `breeds/_base.yaml:47` keeps `max_budget_usd: 0`
  ("0 = no cap"). The predecessor session died of token exhaustion. 512 turns
  with no cost ceiling can burn an account on one task; a per-agent
  `max_budget_usd` for the developer breed (and a `summary_budget_usd`) would
  bound it. Not decided, not changed by me.
- **Public repository, new exposure.** Everything in `breeds/` and `docs/`
  becomes world-readable, including the breed instructions and the skill source
  list. I read nothing secret in them (`.env.*` is ignored, credentials live in
  repository secrets), but nobody has gone over the history for accidentally
  committed material. Worth one human check before or right after flipping
  visibility.
- **Signing.** No release signature is planned (no cosign, no minisign, no
  GPG). The digest only protects if it travels out of band - it does, as
  `FORMATIONS_SHA256` in flokpit's configuration, which is adequate for now.
  Recorded, not solved.

## Out of scope

- Writing `.github/workflows/release.yml` or any other CI, code, test or
  configuration file, here or in `flokpit/flokpit`. This memo is the only file
  I write; T1 items 3 and 4 are specified above and reported BLOCKED in
  #flockpit-dev.
- Creating the tag, the release or the assets; deleting the `publish` job;
  deleting the bunny.net secrets.
- Making the repository public, configuring tag protection or rulesets.
- Editing `docs/CONCEPT.md` (5.1, B-1, phase-0 row 3) and `CLAUDE.md`, and
  editing `docs/decisions/001-contract-delivery-to-flokpit.md` to add a
  "superseded by 002" pointer - all developer edits; listed here, not made.
- Implementing or reviewing the flokpit loader (T2): fetch, digest check, cache
  fallback, ConfigMap annotations, `.env.example`.
- Deciding the first version number, the B-1 wording, the redirect-host rule or
  the `max_turns`/budget question. Those are dennisjay's.
- Anything about flokpit's code; I cannot read that repository.
