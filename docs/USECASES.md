# Use cases and permission simulation

Supporting document for `breeds/` and `formations/`. The breed `tools`,
`os.network` and `credentials` sections were written from the top down (what
should an agent be *allowed*); this document works from the bottom up: what
does each breed actually *do*, command by command, and does the current
configuration let it?

Method: for every breed, realistic use cases are walked through step by step.
Each step is checked against the merged breed (`_base` + breed file) using the
semantics of `docs/CONCEPT.md` section 5.4: `deny` beats `allow`, anything not
allowed is denied, there is no prompt (`--permission-mode dontAsk`). The
formations are then walked as timelines, because most real blockers appear at
the seams between agents.

Status: **simulation on paper, nothing executed.** The decisions of section 5
were applied to `breeds/`, `formations/` and `docs/CONCEPT.md` on 2026-11-21,
then reconciled with the upstream changes of the same weeks (breeds renamed to
`architect` and `tester`, mise project tasks, roosts and event breeds, the
`ui-bugfixing` formation and the top-level `integration_branch`). Sections 1
and 2 describe the configuration **before** that change (they are the
evidence for it); section 3 is what was applied, with the deviations listed at
its top; section 7 re-runs the timelines. The new breeds (consultant,
pr-checker, issue-checker, watchdog, resumer) and `ui-bugfixing` are walked in
section 8. **Section 9 is the current state**: the table of which
breed or formation serves which software engineering task, the breeds and
formations added for the gaps, the check against different project setups,
and the permission decisions made under "functionality over security".
Where sections 1 to 8 describe a narrower rule, section 9 wins.

Legend: ✅ works as configured · ⚠️ works with a caveat or depends on
something unverified · ❌ blocked by the current configuration.

## 0. Ground rules for the simulation

### 0.1 What the permission rules really protect

- `Bash(python3 *)`, `Bash(node *)`, `Bash(npx *)`, `Bash(make *)`,
  `Bash(npm *)` and `Bash(find *)` (with `-exec`) are each equivalent to an
  arbitrary shell. Deny rules like `curl *` or `kubectl *` are therefore a
  second layer at best: `python3 -c "import urllib.request..."` does the same.
- The real boundaries are the ones CONCEPT requirement X-5 already names: the
  pod (non-root, read-only root filesystem, no `sudo`), the egress proxy
  allowlist, and the gateway-held GitHub credentials (assumed: no token inside
  the pod; to be confirmed).
- Consequence for tuning: **be generous where the pod, proxy or credential
  already contains the damage; keep hard denies where the credential is the
  harm** (push to the default branch, merge, delete issues, force push to
  someone else's branch). Today it is the other way round in places: wide
  interpreter allows next to missing `git blame`.

### 0.2 Assumptions to verify in the Claude Code spike

These decide several results below. They belong in the same spike as S-6.

| # | Question | Why it matters |
|---|---|---|
| V-1 | Which shell commands count as read-only and run under `dontAsk` without a rule (`ls`, `cat`, `head`, `wc`, `grep`, `pwd`, `cd`, `echo`, `sleep`)? CONCEPT 5.4 assumes the usual set. | Every breed uses them; `sleep` and `kill` may not be in the set. |
| V-2 | Is each part of `cd x && npm test`, `a \| b`, `$(...)` and heredocs matched separately? | **Answered upstream (flokpit#255): compound commands, heredocs, `cd`, `&&` and `cat` are denied.** Agents write bodies to a file with the edit tool and run one plain command (`gh issue create --body-file`). Instructions in this repository follow that rule, e.g. the reviewer posts inline comments with `gh api ... --input /tmp/review.json`. |
| V-3 | Can `gh api` be restricted by HTTP method in a rule? | It cannot, as far as the rule syntax shows. Plan: allow `gh api repos/*`, deny `-X DELETE`/`--method DELETE` forms, and let the credential be the real limit. |
| V-4 | Do reviewer and developer push and review as the **same** GitHub identity? | GitHub refuses `gh pr review --approve` on one's own PR. If the gateway uses one app identity for all agents, approvals fail (see G-X8). |

### 0.3 Result summary

| Breed | Covers its core use case today? | Main blockers |
|---|---|---|
| developer | mostly ✅ | cannot see CI, cannot read inline review comments, cannot force-push own branch after rebase, JS/Python only |
| reviewer | ❌ | cannot install dependencies, cannot post inline comments, cannot read the linked issue, 3Gi memory (the developer breed documents 3Gi OOM on the same suite) |
| tester | ❌ | `curl` denied for health checks, `git add` too narrow to commit its own config, cannot read the issue or spec, blocked CDN and font hosts |
| architect | ⚠️ | cannot edit `PROGRESS.md`, cannot read PRs or CI, cannot create the flock label, no docs access |
| planner | ⚠️ as planner, ❌ as bug-sweep lead | cannot run anything, so cannot "reproduce or confirm" issues; no label creation; missing PR credential |
| project-manager | ❌ for discovery | no checkout and no write access, yet its hand-off is "spec in a PR" and its progress file is in the repository |

## 1. Breeds

Use cases are what a human would plausibly ask for in the channel.

### 1.1 developer

Merged tools: `git *` (minus pushes to `main`/`master`, `--force*`), `gh pr
create|view|comment`, `gh issue view|comment`, `npm|npx|pnpm|bun|node|python3|uv|make *`;
edit under `/workspace/**` and `/tmp/**`; egress GitHub, npm, PyPI; credentials
`contents:write-own-branch`, `pull_requests:write`, `issues:read`.

| # | Use case | Needs | Result |
|---|---|---|---|
| D-1 | Implement an issue with TDD: read the issue, write a failing test, implement, run tests, push, open PR | `gh issue view`, `npm ci` or `uv sync`, test runner, `git commit/push`, `gh pr create` | ✅ |
| D-2 | Debug a bug, reproduce against a locally started service | start server, hit `localhost` | ⚠️ `curl *` is denied in `_base`; `python3 -c` works around it, which is exactly the kind of workaround a deny should not need (G-D1) |
| D-3 | Address review feedback: read inline comments per file and line, fix, push | `gh api repos/*/pulls/*/comments`; `gh pr view --comments` does not list inline threads | ❌ no `gh api` (G-D2) |
| D-4 | Rebase on a moved default branch and update the PR | `git fetch`, `git rebase`, then a push that is not a fast-forward | ⚠️ upstream deliberately forbids force-pushes ("fetch and rebase; never force-push"); my proposal to allow `--force-with-lease` on the own branch was **dropped**, so a rebased, already-pushed branch needs a merge instead or a new branch (G-D3) |
| D-5 | CI is red after the push: read the failing job log, fix | `gh pr checks`, `gh run view --log-failed`; credentials `checks:read`, `actions:read` | ❌ neither command nor scope (G-D4); formations require `ci-green` but the author cannot see CI |
| D-6 | Look up a library's documentation or an error message | `WebFetch` to docs hosts, egress to them | ❌ `webfetch: {}`, `websearch: deny`, no docs host allowed (G-D5) |
| D-7 | Add a dependency | `npm i`, registry | ✅ |
| D-8 | Work in a Go, Rust, Java or Ruby repository | toolchain on the image, module proxy in egress, `go`/`cargo`/`mvn`/`bundle` rules | ❌ features are Node and Python only; egress has no `proxy.golang.org`, `crates.io`, Maven Central (G-X5) |
| D-9 | Integration tests that need Postgres or Redis | a service container or an in-process alternative | ❌ no sidecar mechanism; not a permission issue, but the same user-visible failure (G-X5) |
| D-10 | Edit labels or the body of its own issue/PR, list open PRs for context | `gh pr edit`, `gh issue edit`, `gh pr list`, `gh issue list` | ❌ (G-D6) |
| D-11 | Install a native module (node-gyp, prebuilt binary from a GitHub release) | egress `nodejs.org`, `objects.githubusercontent.com` | ❌ release assets redirect to `objects.githubusercontent.com`, not allowed (G-X4) |

Also found (too loose, see section 4): `git push * main` does not match
`git push origin HEAD:main`; only the `write-own-branch` credential stops it.

### 1.2 reviewer

Merged tools: `git fetch*|checkout*`, `gh pr view|diff|checks|review|comment`,
`npm test*`, `npm run *`, `npx *`, `pnpm test*`, `bun test*`,
`python3 -m pytest*`, `make test*`; edit only `/tmp/**`; credentials
`contents:read`, `pull_requests:write`; memory limit 3Gi.

| # | Use case | Needs | Result |
|---|---|---|---|
| R-1 | Review a PR and run its tests in a fresh checkout | `npm ci` / `pnpm install` / `uv sync` before `npm test` | ❌ only `npm test*`, `npm run *` and `npx *` are allowed; there is no install, so tests cannot run on a clean clone (G-R1) |
| R-2 | Post findings with file and line (the breed's own rule) | `gh api repos/*/pulls/N/reviews` with inline `comments[]`; `gh pr review` only takes a body | ❌ (G-R2) |
| R-3 | Check the PR against its issue's acceptance criteria | `gh issue view`; credential `issues:read` | ❌ neither (G-R3); formation `acceptance-criteria-checked` cannot be backed |
| R-4 | Prove a regression test fails without the fix | check out the PR, revert the fix, run, restore: `git stash`, `git worktree add`, `git switch` | ⚠️ `git checkout*` works for a path-limited revert; `git stash`/`worktree` do not (G-R4) |
| R-5 | Differential and security review incl. dependency audit | `npm audit`, `pip-audit`, `git blame`, `git log -S` | ❌ `npm audit` not covered by `npm run *`; `git blame` missing from `_base` (G-R1, G-X3) |
| R-6 | Reproduce a suspected bug with a scratch test | write a test file next to the code | ⚠️ `edit` only allows `/tmp/**`; tests outside the repo rarely resolve imports. Harmless to allow in the workspace because `git push` is denied and the credential is read-only (G-R5) |
| R-7 | Approve or request changes | `gh pr review --approve` | ⚠️ works only if the reviewer is a different GitHub identity than the author (V-4, G-X8) |
| R-8 | Run the full suite of a large repo | same memory as the developer | ❌ 3Gi against a developer limit of 6Gi, set because 3Gi was OOMKilled by builds and test runs (G-R6) |
| R-9 | Re-review after fixes | `git fetch`, `git diff old..new` | ✅ |

### 1.3 tester

Merged tools: edit `tests/e2e/**`, `playwright.config.*`, `/tmp/**`; `git add
tests/e2e*`, `git commit*`, `git push origin {branch}*`, `gh pr create|comment`,
`npm|npx|pnpm|node|python3 *`, `playwright-cli *`, `agent-browser *`; egress
GitHub, registries, `localhost`; memory limit 4Gi.

| # | Use case | Needs | Result |
|---|---|---|---|
| T-1 | Start the app and wait until it answers | background server, `curl -sf localhost:3000`, `sleep`, `kill` | ❌/⚠️ `curl *` denied (V-1 decides `sleep`/`kill`); `npx wait-on` is a workaround (G-T1) |
| T-2 | Explore flows exploratorily with `playwright-cli` / `agent-browser` | browser binary, `localhost` | ✅ |
| T-3 | Test a page that loads fonts, a CDN script or a payment sandbox | egress to those hosts, or request interception | ⚠️ blocked hosts surface as hangs or load errors that look like app bugs; Playwright route mocking works but is not what the skills assume (G-T2) |
| T-4 | Write an e2e test plus add `@playwright/test` and a config | edit `package.json`, `package-lock.json`, `playwright.config.ts`, `.gitignore`; `git add` of the same | ❌ `git add` only allows `tests/e2e*`, so the config and the dependency change cannot be committed even though the config may be edited; `package.json` cannot be edited with the Edit tool (G-T3) |
| T-5 | Run an accessibility audit (axe) on every page | `npx @axe-core/cli` or `@axe-core/playwright` | ✅ |
| T-6 | Deliver a report with screenshots | commit images and a markdown report where humans can open them | ⚠️ default Playwright output is `test-results/`, outside what `git add` allows and ephemeral with the pod; the breed must name a committed path such as `tests/e2e/reports/{flock}/` (G-T4) |
| T-7 | Read the acceptance criteria from the issue or the spec PR | `gh issue view`, `gh pr view`, `git fetch`, `git merge` | ❌ none of them (G-T5) |
| T-8 | Test a staging or preview deployment | egress to that host | ❌ allowlist is static; no way for the spawner to add a host (G-X6) |
| T-9 | Start a backend with seed data | `make *`, `uv *`, `docker compose` | ⚠️ `make` and `uv` are not allowed for this breed although `developer` has them; no Docker in the pod (G-T1) |
| T-10 | Flake triage (`--repeat-each 20`) | `npx playwright test` | ✅ |
| T-11 | Run Chromium plus a dev server plus a build | memory | ⚠️ 4Gi is tight; Chromium alone takes about 1Gi with a few tabs (G-T6) |

### 1.4 architect

Merged tools: edit `docs/adr/**`, `docs/architecture/**`, `/tmp/**`; `git add
docs/*`, `git commit*`, `git push origin {branch}*`, `gh pr create|comment`,
`gh issue create|view`, `tree *`, `find *`; credentials `contents:write-own-branch`,
`pull_requests:write`, `issues:write`; may spawn developer, reviewer, tester.

| # | Use case | Needs | Result |
|---|---|---|---|
| A-1 | Map an unfamiliar codebase | read, `rg`, `tree`, `find`, `git log`, dependency listing (`npm ls`, `go list -m all`, `pipdeptree`) | ⚠️ reading works; dependency commands are not allowed (G-A5) |
| A-2 | Write an ADR with Mermaid diagrams, open a PR | edit under `docs/adr`, `git add docs/*`, commit, push, `gh pr create` | ✅ (Mermaid syntax cannot be checked without a renderer; accepted limitation) |
| A-3 | STRIDE threat model of a new endpoint | edit `docs/architecture/**` | ✅ |
| A-4 | Compare two libraries or a vendor API, cite docs | `WebFetch`/`WebSearch`, egress | ❌ (G-A4); the "at least two options with trade-offs" rule is hard to meet from training data alone |
| A-5 | Lead a feature-team: file issues with the flock label | `gh label create`, `gh issue create --label`, `gh issue edit`, `gh issue close` | ❌ label creation, edit and close are missing (G-A1) |
| A-6 | Lead: keep `PROGRESS.md` (the formation's record of state) | edit `/workspace/repo/PROGRESS.md`, `git add PROGRESS.md` | ❌ neither the edit path nor the `git add` path (G-A2) |
| A-7 | Lead: check whether developer PRs are approved and green | `gh pr list`, `gh pr view --json reviews`, `gh pr checks` | ❌ only `gh pr create\|comment` (G-A3) |
| A-8 | Review a developer PR for design conformity | `gh pr diff`, `gh pr view` | ❌ (G-A3) |
| A-9 | Decide how work items land when they depend on each other | merge approved PRs into a flock integration branch | ❌ no merge right of any kind (G-X7) |

`find *` is also an unintended `-exec` escape hatch (section 4).

### 1.5 planner

Merged tools: `gh issue *` (minus `delete`), `gh label list*`, `gh pr list|view*`,
`/tmp/**` edit; base git read-only set; runtime `[]`; 1Gi memory; egress GitHub
only; credentials `contents:read`, `issues:write` (no `pull_requests:read`).

| # | Use case | Needs | Result |
|---|---|---|---|
| P-1 | Turn a goal into issues with acceptance criteria | `gh issue create --body-file`, labels, milestone | ⚠️ works if the labels exist; `gh label create` is missing (G-P1); V-2 for inline bodies |
| P-2 | Detect duplicates of existing issues and PRs | `gh issue list`, `gh search issues`, `gh pr list` | ⚠️ `gh search` missing; `gh pr list` allowed but credential has no `pull_requests:read`, so private repos return 403 (G-P2) |
| P-3 | Triage a bug issue: reproduce or confirm it (bug-sweep `work_split`) | run the app or tests, install dependencies | ❌ nothing runnable: no `npm`/`python3`, no registry access, no workspace edit, 1Gi memory (G-P3) |
| P-4 | Order issues by impact and file overlap | `git log --name-only`, `git blame`, `rg` | ⚠️ `git log` works, `git blame` and `git grep` missing (G-X3) |
| P-5 | Lead bug-sweep: spawn, track PRs and CI, close issues after approval | `gh pr view --json`, `gh pr checks`, `gh issue close` | ⚠️ `gh pr checks` missing; no `checks:read` (G-P4) |
| P-6 | Group issues into a milestone | `gh api repos/*/milestones` | ❌ (the project-manager has it, the planner does not) (G-P1) |
| P-7 | Comment on an issue to hand over context | `gh issue comment` | ✅ |

### 1.6 project-manager

Merged tools: `gh issue *`, `gh pr list|view|checks*`, `gh api repos/*/milestones*`,
`gh project *`, `/tmp/**` edit; **`workspace.clone: false`**; credentials
`contents:read`, `issues:write`, `pull_requests:read`, `projects:write`.

| # | Use case | Needs | Result |
|---|---|---|---|
| M-1 | Write a spec as an issue | `gh issue create` | ✅ |
| M-2 | Write a spec **as a PR** (product-discovery hand-off: "confirmed spec in a PR") | checkout, edit `docs/specs/**`, `git add/commit/push`, `gh pr create`, `contents:write-own-branch`, `pull_requests:write` | ❌ no clone, no edit path, no git write, no `gh pr create`, read-only contents credential (G-M1) |
| M-3 | Keep `docs/discovery/{flock}.md` (formation `progress_file`) | same as M-2 | ❌ (G-M1) |
| M-4 | Groom the backlog: labels, milestones, assignees, project board | `gh label create`, `gh issue edit`, `gh api milestones`, `gh project` | ⚠️ everything except `gh label create` (G-M2) |
| M-5 | Status report: done, in progress, blocked, risks | `gh issue list --json`, `gh pr list --json`, `gh run list`, commit counts | ⚠️ issue and PR data works; CI runs and commits do not (no clone, no `gh run`) (G-M3) |
| M-6 | Understand the repository before writing a spec | README, tree, recent PRs | ❌ no clone and no `gh repo view` / `gh api repos/*/contents` (G-M4) |
| M-7 | Research market, users or competitors for a spec | `WebSearch`, `WebFetch` | ❌ (G-M5); optional, humans can answer |
| M-8 | Lead discovery: spawn architect, tester, planner | `flokpit/*` | ✅ |

## 2. Formations

Each formation is walked as a timeline for a concrete task. Rows show the first
step that fails; later steps are only listed when they fail for a different
reason.

### 2.1 feature-team: "Add CSV export to the reports page (API plus UI)"

Flock: architect (lead), two developers, reviewer, tester.

| Step | Actor | Action | Result |
|---|---|---|---|
| 1 | architect | kickoff `QUESTION` in the channel, wait | ✅ |
| 2 | architect | ADR with options, PR | ✅ |
| 3 | architect | create label `flock:csv-export`, file two issues with it | ❌ label does not exist and cannot be created (G-A1) |
| 4 | architect | spawn two developers and the reviewer (`flokpit/*`) | ✅ |
| 5 | architect | write the plan into `PROGRESS.md` on its branch | ❌ (G-A2) |
| 6 | developer A, B | implement item A (API) and B (UI) in parallel | ✅ (D-1) |
| 7 | developer B | item B calls the API of item A, which is an unmerged PR | ❌ the work split says "items must not depend on unmerged work", which only holds if item B can be written against a mock; real integration needs A's code (G-X7) |
| 8 | developer | push, open PR | ✅ |
| 9 | reviewer | check out PR, install dependencies, run tests | ❌ (R-1) |
| 10 | reviewer | review against the issue, post inline findings | ❌ (R-2, R-3) |
| 11 | developer | read inline comments, fix, rebase, force-push | ❌ (D-3, D-4) |
| 12 | architect | decide `all_items_verified`: reviews approved and CI green | ❌ cannot read PR state or CI (A-7) |
| 13 | tester | spawned after the PRs are approved to test the whole feature | ❌ its branch comes from the default branch, so neither the API nor the UI is in the checkout; no `git fetch/merge`; no issue read (T-7, G-X7) |
| 14 | reviewer | approve | ⚠️ identity (V-4) |
| 15 | human | merge each PR | by design; but the tester in step 13 needed that merge first |

The shape is right, the plumbing between agents is missing. Steps 7 and 13 are
structural, not a missing glob: members need to see each other's approved,
unmerged work. See G-X7.

### 2.2 bug-sweep: "Fix the 12 open issues labelled `bug`"

Flock: planner (lead), up to five developers, one reviewer.

| Step | Actor | Action | Result |
|---|---|---|---|
| 1 | planner | list issues, confirm or reproduce each one | ❌ cannot run anything (P-3); only static confirmation by reading code is possible |
| 2 | planner | label and order, drop duplicates | ⚠️ (P-1, P-2) |
| 3 | planner | spawn reviewer and first developers | ✅ |
| 4 | developer | reproduce, write failing regression test, fix, PR | ✅ (D-1) |
| 5 | developer | two issues touch the same files: second PR on top of the first | ✅ stacked PR via `gh pr create --base <first branch>` is covered by `git *` and `gh pr create*` |
| 6 | reviewer | verify the regression test failed before the fix | ⚠️ (R-4) |
| 7 | reviewer | tests, inline comments, approve | ❌ (R-1, R-2, V-4) |
| 8 | planner | see CI and review state, assign the next issue | ⚠️ `gh pr view` works, `gh pr checks` does not (P-5) |
| 9 | developer | turn limit | ⚠️ `max_turns` 40 per human message is tight for fix, CI fix and one review round; it is lower than the breed's 60 on purpose, keep but watch |
| 10 | human | merge approved PRs | by design |

Of the three formations this one is closest to working: after the reviewer
fixes, only the planner's reproduction step needs a decision. Recommendation:
move reproduction to the developer (the regression test already proves it)
and let the planner confirm statically. That keeps the planner read-only,
which is the better trade than giving it a toolchain.

### 2.3 product-discovery: "Idea: a shared shopping list for a household"

Flock: project-manager (lead), architect, tester, planner. Fresh,
nearly empty repository.

| Step | Actor | Action | Result |
|---|---|---|---|
| 1 | PM | restate the idea, ask `QUESTION` | ✅ |
| 2 | PM | read the repository for context | ❌ no checkout and no `gh repo view` (M-6) |
| 3 | PM | write the spec, put it in a PR | ❌ (M-2) |
| 4 | PM | keep `docs/discovery/{flock}.md` | ❌ (M-3) |
| 5 | human | confirm the spec | ✅ by design |
| 6 | architect | sketch architecture, ADRs for options, PR | ✅; ❌ for the spec itself, which is in an unmerged PR (G-X7) unless the human merged it first |
| 7 | tester | turn acceptance criteria into failing e2e tests in a repo that has no app, no `package.json`, no Playwright | ❌/⚠️ it needs the spec (T-7), `npm init`/`npm i -D @playwright/test` works but cannot be committed (T-4); tests must fail for the right reason ("no app yet" is the wrong reason; the breed says "post BLOCKED if the app does not start") |
| 8 | planner | file backlog issues with the flock label | ⚠️ label (P-1) |
| 9 | PM | link spec, ADRs, tests, issues; post summary | ⚠️ cannot read PR state (M-5) |

Discovery is the formation with the least dependence on code execution and the
most dependence on one agent handing a document to the next. Most of its
problems are the project-manager breed being configured as read-only while its
hand-off requires a write (M-1, M-2). Decision for the tester on a
greenfield: it needs a "scaffold mode" (allowed to create `package.json` and
the Playwright config) or the formation must say tests are written against the
spec only and are expected to fail at "no server on `localhost`".

## 3. Proposed changes

Applied, with these deviations from the drafts below: **no force push**
(upstream rule kept, so the developer's `--force-with-lease` allow of 3.2 was
not applied); **no lead-integrates-by-tool design and no `{base}`
placeholder** (G-X7 below is superseded by the upstream `integration_branch`
and `contents:write-integration-branch`, see 3.8); the developer keeps
`issues:read` and has no `gh issue edit*`; `wget *` is allowed next to `curl *`
for developer; the reviewer writes inline reviews through `--input
/tmp/review.json` because heredocs are denied. Gap ids used in the tables above point here by prefix: `G-D` to
3.2, `G-R` to 3.3, `G-T` to 3.4, `G-A` to 3.5, `G-P` to 3.6, `G-M` to 3.7,
`G-X3`/`G-X4` to 3.1, `G-X5` to `G-X8` to 3.8. `G-X8` is the identity item
(3.8, also V-4). Q-ids are the open decisions in section 5.

### 3.1 `_base.yaml`

```yaml
os:
  network:
    allow:                       # replaces the list; breeds that override it must repeat these
      - github.com
      - api.github.com
      - codeload.github.com
      - raw.githubusercontent.com
      - objects.githubusercontent.com   # GitHub release assets redirect here

tools:
  bash:
    # read-only git that every breed needs (V-1 decides what is covered already)
    "git blame*": allow
    "git grep*": allow
    "git ls-files*": allow
    "git rev-parse*": allow
    "git merge-base*": allow
    "git cat-file*": allow
    "git rev-list*": allow
    "git branch*": allow
    "git fetch*": allow
    # read-only GitHub for orientation and status
    "gh repo view*": allow
    "gh search *": allow
    "gh issue view*": allow
    "gh issue list*": allow
    "gh pr view*": allow
    "gh pr list*": allow
    "gh pr diff*": allow
    "gh pr checks*": allow
    "gh run list*": allow
    "gh run view*": allow
    "gh label list*": allow
```

`credentials.github` default becomes `["contents:read", "issues:read",
"pull_requests:read", "checks:read", "actions:read"]` so the read-only
commands above work for every breed; breeds add write scopes on top (lists
replace, so each breed repeats the full list).

### 3.2 developer

```yaml
tools:
  bash:
    # not applied: upstream keeps "git push --force*": deny
    "gh pr edit*": allow
    "gh issue edit*": allow
    "gh api repos/*/pulls/*": allow      # inline review comments; V-3
    "gh api -X DELETE*": deny
    "gh api --method DELETE*": deny
    "curl *": allow                      # replaces the _base deny; egress proxy is the boundary
    "pytest*": allow
    "ruff *": allow
    "pip *": allow
  webfetch:
    "domain:developer.mozilla.org": allow   # curated docs hosts, also added to os.network.allow
    "domain:docs.python.org": allow
    "domain:nodejs.org": allow
credentials:
  github: ["contents:write-own-branch", "pull_requests:write", "issues:write",
           "checks:read", "actions:read"]
```

`issues:write` only if developers should edit labels (D-10); otherwise keep
`issues:read` and drop `gh issue edit*`.

### 3.3 reviewer

```yaml
pod:
  resources:
    limits: { cpu: "2", memory: 6Gi, ephemeral-storage: 8Gi }   # same as developer
tools:
  bash:
    "gh pr checkout*": allow
    "gh api repos/*/pulls/*": allow      # inline review with comments[] (R-2)
    "gh api -X DELETE*": deny
    "gh api --method DELETE*": deny
    "npm ci*": allow
    "npm audit*": allow
    "npm ls*": allow
    "pnpm install*": allow
    "pnpm audit*": allow
    "bun install*": allow
    "uv sync*": allow
    "uv run *": allow
    "python3 -m pip *": allow
    "git stash*": allow
    "git switch*": allow
    "git worktree *": allow
    "git blame*": allow
  edit:
    "/workspace/**": allow               # scratch repro; harmless: push denied, credential read-only (R-6)
credentials:
  github: ["contents:read", "pull_requests:write", "issues:read", "checks:read", "actions:read"]
```

If R-6 is rejected as too lax for a breed whose rule is "never edits code",
keep `/tmp/**` and accept ⚠️.

### 3.4 tester

```yaml
pod:
  resources:
    limits: { cpu: "2", memory: 6Gi, ephemeral-storage: 8Gi }
os:
  network:
    allow: [github.com, api.github.com, codeload.github.com, raw.githubusercontent.com,
            objects.githubusercontent.com, registry.npmjs.org, pypi.org,
            files.pythonhosted.org, localhost]   # plus an optional per-spawn host, see G-X6
tools:
  edit:
    "/workspace/repo/tests/e2e/**": allow
    "/workspace/repo/playwright.config.*": allow
    "/workspace/repo/package.json": allow
    "/workspace/repo/.gitignore": allow
    "/tmp/**": allow
  bash:
    "git add *": allow                    # replaces "git add tests/e2e*"
    "git add -A*": deny
    "git add .": deny
    "git fetch*": allow
    "git merge *": allow                  # to bring in an approved branch for testing (G-X7)
    "curl *": allow
    "sleep *": allow
    "kill *": allow
    "make *": allow
    "uv *": allow
    "gh issue view*": allow
    "gh pr view*": allow
credentials:
  github: ["contents:write-own-branch", "pull_requests:write", "issues:read"]
```

The report path goes into the instructions: commit screenshots and the report
under `tests/e2e/reports/{flock}/` and link them in the PR, because the pod's
`test-results/` disappears with the pod.

### 3.5 architect

```yaml
tools:
  edit:
    "/workspace/repo/docs/adr/**": allow
    "/workspace/repo/docs/architecture/**": allow
    "/workspace/repo/PROGRESS.md": allow           # lead's progress_file
    "/tmp/**": allow
  bash:
    "git add PROGRESS.md": allow
    "gh label create*": allow
    "gh issue edit*": allow
    "gh issue close*": allow
    "gh issue comment*": allow
    "gh pr view*": allow
    "gh pr list*": allow
    "gh pr diff*": allow
    "gh pr checks*": allow
    "find * -exec*": deny                          # find * currently doubles as arbitrary exec
    "find * -delete*": deny
    "npm ls*": allow
    "pip list*": allow
    "go list *": allow
  webfetch:
    "domain:docs.github.com": allow                # curated; extend per project
credentials:
  github: ["contents:write-own-branch", "pull_requests:write", "issues:write", "checks:read"]
```

Websearch: allow it for the architect only if option comparison with current
facts is wanted; it widens prompt-injection exposure, so it is a human
decision (Q-1 in section 5).

### 3.6 planner

```yaml
tools:
  bash:
    "gh label create*": allow
    "gh api repos/*/milestones*": allow
    "gh issue transfer*": deny                    # `gh issue *` also allowed moving issues to other repos
    "gh issue pin*": deny
credentials:
  github: ["contents:read", "issues:write", "pull_requests:read", "checks:read"]
```

Plus a change in `formations/bug-sweep.yaml`: `work_split` says developers
reproduce and write the regression test first; the planner confirms
statically (reading code and issue text) and escalates what it cannot judge.

### 3.7 project-manager

Option A (recommended): the PM may write documents, not code.

```yaml
workspace:
  clone: true                                      # needed for specs and progress file
tools:
  edit:
    "/workspace/repo/docs/specs/**": allow
    "/workspace/repo/docs/discovery/**": allow
    "/tmp/**": allow
  bash:
    "git add docs/*": allow
    "git commit*": allow
    "git push origin {branch}*": allow
    "gh pr create*": allow
    "gh pr comment*": allow
    "gh label create*": allow
    "gh run list*": allow
    "gh repo view*": allow
    "gh api repos/*/contents/*": allow
credentials:
  github: ["contents:write-own-branch", "issues:write", "pull_requests:write", "projects:write"]
```

Option B: keep `clone: false` and change the hand-off to "spec as an issue"
(the `to-spec` skill already works that way) plus `progress_file` as an
issue or the channel topic. Smaller, but discovery then has no spec file for
the tester and architect to read in the repository.

### 3.8 Structural items (need a decision, not a glob)

| ID | Item | Proposal |
|---|---|---|
| G-X7 | Members cannot see each other's approved, unmerged work; the lead cannot sequence dependent items; the tester cannot test a feature that is only in PRs. | **Superseded upstream.** `integration_branch` (formation, top level) with `contents:write-integration-branch` lets developers merge into a flock branch; `ui-bugfixing` uses it. That path skips the pull request and so the review gate. My earlier design (lead integrates review-gated PRs through a flokpit tool, `state.integration_branch`, `{base}`) was dropped in the merge; whether feature-team needs a review-gated variant is open (Q-3). |
| G-X5 | Per-stack toolchains (Go, Rust, Java, Ruby) need runtime features, egress hosts and command rules together. | A `stack` profile chosen at spawn that bundles `runtime.features`, `os.network.allow` additions and `bash` rules; profiles live in the repository like breeds. Out of scope for this change; until then developer is Node and Python only. |
| G-X8 / V-4 | Approving needs a different identity than the author. | Gateway issues per-breed GitHub identities, or the reviewer posts `gh pr review --comment` with an explicit verdict line and the formation reads that. |
| G-X4 | Egress hosts for GitHub release downloads. | `objects.githubusercontent.com` in `_base` (3.1). |
| G-X5 | Services for tests (Postgres, Redis). | Sidecar containers per breed (`pod.services`); not a permission issue but the same user-visible failure. Not proposed here. |
| G-X6 | UI testing against a preview or staging URL. | A spawn argument `--allow-host <h>` that a **human** supplies, not an agent; it widens egress, so it is the one place where `tighten_only` is deliberately not applied, and it needs a flokpit decision. |

## 4. Too loose (the other direction)

Found while simulating; small, but they belong next to the loosening because
they change what is safe to loosen.

| Where | Issue | Fix |
|---|---|---|
| `_base` `read: "**": allow` | Includes `/proc/*/environ`, `/var/run/secrets/**` (service account token) and gh/ssh config | Applied: `deny` for `/proc/**`, `/var/run/secrets/**`, `/run/secrets/**`, `/home/agent/.ssh/**`, `/home/agent/.config/gh/**`. `~/.claude/**` stays readable because skills read their own files there. The real fix is not mounting secrets (OS layer) |
| developer `git push * main` | Does not match `git push origin HEAD:main` or `git push origin HEAD:refs/heads/main`; relies on the credential | Add `git push * HEAD:main*`, `git push * HEAD:master*`, `git push *:main`; keep the credential as the backstop |
| developer `git *` | Also allows `git config`, `git remote add/set-url`, `git clean -fdx` | Acceptable in an isolated pod; deny `git remote *` to keep the push target fixed |
| architect `find *` | `find . -exec ...` runs anything | deny `-exec` and `-delete` (3.5) |
| planner `gh issue *` | Includes `transfer`, `pin`, `lock`, `develop` | Enumerate: `create`, `edit`, `comment`, `list`, `view`, `close`, `reopen` |
| `gh api` | Any method on any path once allowed (V-3) | Allow `repos/*/...` only, deny delete forms, depend on the credential |

## 5. Decisions for the humans

**Decided 2026-11-21: all six recommendations accepted** (Q-1 WebFetch on curated hosts for developer and architect, WebSearch for the architect only; Q-2 option A; Q-3 integration branch, reconciled with upstream's mechanism (see section 3 and Q-3 note); Q-4 yes; Q-5 developer reproduces; Q-6 distinct identities). Sections 3.2 to 3.8 were applied with the deviations listed at the top of section 3.

| # | Decision | Recommendation |
|---|---|---|
| Q-1 | Allow `WebSearch` for the architect (and `WebFetch` on curated docs hosts for developer and architect)? | `WebFetch` on a curated list yes; `WebSearch` only for the architect, because reading arbitrary pages is the main prompt-injection path. |
| Q-2 | Project-manager Option A (writes docs) or Option B (issues only)? | A: the formation's own hand-off requires a PR. |
| Q-3 | Flock integration branch (G-X7) or independent-items-only for now? | Integration branch; without it feature-team cannot finish a dependent item without a human in the loop at every step. |
| Q-4 | Reviewer may edit the workspace for scratch repro? | Yes; the credential is read-only and push is denied. |
| Q-5 | Who reproduces bugs in bug-sweep? | The developer; the planner stays read-only. |
| Q-6 | Distinct GitHub identities per breed (G-X8)? | Yes; otherwise `reviewer-approved` cannot be a GitHub fact. |

## 6. After applying

1. Apply 3.1 to 3.7 to `breeds/`, run `uv run scripts/validate.py`, keep
   `breeds/README.md` (table of tools and credentials) and `docs/CONCEPT.md`
   (sections 5.4 and 5.8) in sync.
2. Re-run each timeline in section 2 against the merged breeds; every ❌ and ⚠️
   that remains needs a named owner.
3. In the flokpit spike (V-1 to V-4), record the results here and replace this
   document's "simulation on paper" status line.

## 7. Re-run after applying

The timelines of section 2 against the merged breeds as they are now.

| Item | Before | Now | What still stands |
|---|---|---|---|
| D-2, D-3, D-4, D-5, D-6, D-10, D-11 | ❌/⚠️ | ✅ | D-10 only for PRs (`gh pr edit`); issue labels are the lead's job |
| D-8 Go, Rust, Java, Ruby | ❌ | ❌ | needs the stack profile (G-X5): runtime features, egress hosts and rules together |
| D-9 test services (Postgres, Redis) | ❌ | ❌ | needs sidecars; not a permission |
| R-1 to R-6, R-8, R-9 | ❌/⚠️ | ✅ | reviewer memory is 6Gi |
| R-7 approve | ⚠️ | ⚠️ | needs distinct identities (F-8, gateway) |
| T-1, T-4, T-5, T-6, T-7, T-9, T-11 | ❌/⚠️ | ✅ | |
| T-3 external fonts and CDNs | ⚠️ | ⚠️ | still blocked by egress; tests must mock them |
| T-8 staging or preview URL | ❌ | ❌ | needs a human-supplied `--allow-host` (G-X6), a flokpit decision |
| A-1 to A-3, A-5 to A-9 | ❌/⚠️ | ✅ | A-9 only with a review-gated integration step (open, Q-3 note); Mermaid syntax still unchecked |
| A-4 compare libraries | ❌ | ✅ | WebSearch is on for this breed only |
| P-1, P-2, P-4 to P-7 | ⚠️/❌ | ✅ | |
| P-3 reproduce an issue | ❌ | by design | moved to the developer (bug-sweep `work_split`) |
| M-1 to M-6, M-8 | ❌/⚠️ | ✅ | M-2/M-3 write only under `docs/specs/**` and `docs/discovery/**` |
| M-7 market research | ❌ | ❌ | no web access for the project-manager; humans answer |
| feature-team steps 7, 13 | ❌ | ❌ | open: needs a review-gated integration step or direct merges into an `integration_branch` (Q-3 note) |
| feature-team steps 9 to 12 | ❌ | ✅ | |
| bug-sweep steps 1, 6 to 8 | ❌/⚠️ | ✅ | step 7 approve needs F-8 |
| product-discovery steps 2 to 4, 6, 7 | ❌ | ✅ | the tester on a greenfield repo may add `package.json` and the Playwright config; "fails for the right reason" is still a prompt-level judgement |

**Depends on flokpit, not on this repository:** distinct identities (F-8),
the new read scopes in the gateway (CONCEPT 5.8), and the spike for `gh api`
by method (V-3). Until a review-gated integration step exists, run
feature-team and product-discovery expecting a human to merge between phases.

**Q-3 note after the merge with upstream.** Upstream introduced
`integration_branch` and developers merging into it directly (no PR). I did
not set it on feature-team or product-discovery: with a required reviewer a
direct merge bypasses `reviewer-approved`. Still open: either accept direct
merges for those formations, or add a review-gated integration step (the lead
integrates approved, green PRs through a flokpit tool, which was my original
proposal).

## 8. Second pass: the event breeds, ui-bugfixing, and the errors of the live k3s run

Added after flokpit's v3 k3s bugfixing run (flokpit#323, 2026-11-21) and the
review of PR #18. Sources: the findings note of that run
(`notes/v3-k3s-bugfixing-findings.md` in flokpit) and the cluster events;
the server pod's log had been rotated by a restart, so the list below is the
run's own record, not a log grep. Method as before, **paper simulation**: the
only things executed on the cluster were a taskless `bug-sweep` flight, one
tester turn and echo flocks.

### 8.1 Errors of the run and what prevents their repeat

| Error in the run | Cause | Where it is handled |
|---|---|---|
| every clone answered 407 | agentd cloned without the agent's proxy identity | flokpit (`networkEnv`); nothing in breeds |
| `mise install` refused: api.npmjs.org, npm.jsr.io, api.osv.dev, tuf-repo-cdn.sigstore.dev | egress allowlist too narrow for toolchain installs | flokpit unions `TOOLCHAIN_EGRESS_HOSTS` (wildcards) into **every** agent's allowlist, also where a breed sets its own `os.network.allow`; breeds therefore list only extra docs hosts |
| `watchdog` and `resumer` cannot `fly` or `land` | the breeds relied on `privileges.op`, which v2 ignores | **fixed here:** `commands: [honk, fly, land]` and `[honk, fly]`; formations carry `lead_commands`/`member_commands`; the validator rejects `fly` without `may_spawn` |
| `ErrImagePull` for the default image | breed named the shipped default image | flokpit; breeds use `runtime.image: base` |
| turn limit hit in long runs | `max_turns` 15 to 60 | PR #18: 512 per breed, 256 for the flock overrides |
| a turn's final answer never shown | agent did not call `chat_send` | flokpit; instructions already end with `chat_done`/DONE posts |
| a run without a task paid for an empty turn | taskless flight | flokpit holds it; `ui-bugfixing` is the one formation that is meant to run without a task, its lead has the kickoff as its first message |

### 8.2 Breeds not walked before

| # | Use case | Needs | Result |
|---|---|---|---|
| W-1 | Watchdog: inventory, ask a quiet agent | `chat_agents`, `chat_whois`, `chat_read`, `chat_send` (MCP `flokpit/*`) | ✅ no shell needed |
| W-2 | Watchdog: land a stuck agent, fly a replacement | `land`, `fly` command grants, `may_spawn` | ❌ before (`op` ignored), ✅ now. ⚠️ the replacement is created in the project; that it joins the flock of the stuck member is unverified |
| W-3 | Watchdog: bring in a consultant for a troubled agent | `fly`, `may_spawn: [consultant]` | ✅ now |
| W-4 | Resumer: wake survivors | `chat_send` | ✅ |
| W-5 | Resumer: respawn an agent that the token limit killed | `fly`, `may_spawn` | ❌ before, ✅ now |
| C-1 | Consultant: write a decision memo for a `needs-decision` issue and push it | `gh issue view`, edit `docs/decisions/**`, `git add docs/decisions/*`, commit, `git push origin {branch}`, `gh issue comment`; `contents:write-own-branch`, `issues:write` | ✅ |
| C-2 | Consultant: look at open PRs for context | `gh pr list`, `gh pr view` | ✅ |
| C-3 | Consultant: look up an external source for the memo | `WebFetch`, egress host | ⚠️ `webfetch: {}` and only base hosts; the memo is limited to the repository and the issue (decide whether to add docs hosts like the architect) |
| PC-1 | PR checker: check out a PR, install, run the integration tests | `gh pr checkout`, `mise install`, `mise run test-suite\|check\|test`; egress via toolchain hosts | ✅ |
| PC-2 | PR checker: rate risk (size, conflicts, base moved) | `gh pr diff`, `git merge-tree`, `git merge-base`, `git rev-list` | ✅ |
| PC-3 | PR checker: one comment per PR, request changes when critical | `gh pr comment`, `gh pr review --request-changes --body-file`, body in `/tmp`; `pull_requests:write` | ✅ ("update" is a new comment that supersedes the old one because `gh api` is not allowed) |
| PC-4 | PR checker: a PR from a fork | `gh pr checkout` of a fork branch | ⚠️ works with a public fork; the gateway token has no access to a private one |
| IC-1 | Issue checker: read, classify, label | `gh issue view\|list`, `gh label list`, `gh issue edit --add-label`; `issues:write` | ✅ |
| IC-2 | Issue checker: reproduce a bug | `mise install`, `mise run <task>`; no other project execution | ⚠️ only when a task reaches the bug; the breed says so and falls back to reading code |
| IC-3 | Issue checker: replace the triage section in the body | `gh issue edit --body-file` | ✅ |

### 8.3 ui-bugfixing as a timeline

| Step | Who | Needs | Result |
|---|---|---|---|
| 1 | flokpit | `/fly ui-bugfixing` with no task; creates channel, roosts (watchdog, resumer, pr-checker preset with `head_ref: flokpit/*`) | ✅ roosts need the event catalogue pinned with the breeds |
| 2 | planner (lead) | kickoff: `git ls-remote origin {integration_branch}`; cannot push | ✅ asks a developer to create the branch |
| 3 | developer | create and push `ui-bugfixing/{date}`; credential `contents:write-integration-branch` | ✅ |
| 4 | tester | `mise run start`, `mise run ui-test`, headless browser, `localhost` | ✅ in the browser image; ⚠️ a pod without it reports BLOCKED, the lead tells the human |
| 5 | tester → planner | one message per UI issue with screenshot path | ⚠️ the path lives in the tester's pod; the planner (another pod) cannot open it. The report must name a committed path or paste the steps; the steps are enough to triage |
| 6 | planner | file an issue for risky items: `gh issue create`, label `flock:{flock}` (`gh label create`) | ✅ |
| 7 | developer | fix, regression check, merge into the integration branch, push | ✅ |
| 8 | pr-checker | roosted by `pull_request_updated` of the flock's own branches | ✅ ⚠️ only when the fix goes through a PR; direct merges into the integration branch raise no PR event |
| 9 | watchdog | every 15 minutes: ask, land and fly | ✅ now (was ❌, see W-2) |
| 10 | resumer | on `provider.event.budget_reset` | ✅ now (was ❌, see W-5) |
| 11 | planner | land the flock: `/land` (in `lead_commands`) | ✅ |
| 12 | termination `no_progress_rounds: 3` | workflow-detected | ✅ |

### 8.4 Still open after this pass

- Use cases that need a real multi-agent flock with model turns have not been
  executed; everything above is paper plus the one tester turn of the run.
- W-2 (replacement joins the flock), C-3 (consultant web access) and step 5
  (screenshots across pods) are decisions or flokpit questions, not
  permission gaps in the breed files.
- Reviewer approval with distinct identities (F-8) is unchanged.

## 9. Third pass: which breed for which task, missing breeds, project setups (2026-11-21)

Paper simulation again, against the merged breeds (`_base` + breed file) and
flokpit's renderer (`packages/specs/src/breed-fields.ts`: `bash: {"*": allow}`
becomes the whole `Bash` tool, a command line is checked per sub-command,
`deny` beats `allow`). Rule for this pass, set by the maintainer:
**functionality goes over security** at the tool layer; pod, egress proxy and
credentials stay the boundary (0.1).

### 9.1 Software engineering task → breed or formation

"Agent" = fly one breed alone; "roost" = let an event start it
(`docs/ROOST.md`); a formation name = fly that flock.

| # | Task | Use | Why this one |
|---|---|---|---|
| **Understand and decide** | | | |
| S-1 | An unclear wish, a dead end, "should we do X or Y" | agent `consultant` (roost: label `needs-decision`) | elicits, checks feasibility, one decision memo |
| S-2 | Turn an idea into spec, architecture sketch, acceptance tests and backlog | `product-discovery` | spec first, humans confirm, nothing is built |
| S-3 | Write or update a spec, keep backlog, milestones and status | agent `project-manager` (roost: daily status) | documents and GitHub only |
| S-4 | Understand a codebase, design a change, write an ADR, threat model | agent `architect` (roost: label `architecture`, `design`) | reads, runs `check` to see it work, writes ADRs |
| S-5 | Cut a goal or an epic into issues with acceptance criteria | agent `planner` (roost: label `epic`, `plan`) | issues only, never code |
| **Set up** | | | |
| S-6 | Make a new or existing repository workable (toolchain, tasks, pipeline, first tests, AGENTS.md) | `project-setup`; for one item only, agent `devops` | the pieces depend on each other, so they meet on a setup branch |
| S-7 | Add or repair CI, build, packaging, Dockerfile, infrastructure files | agent `devops` (roost: label `ci`, `build`, `infrastructure`) | owns the pipeline; has the workflow scope |
| **Build** | | | |
| S-8 | One feature or change in one area | agent `developer` (roost: label `flokpit`) plus roost `reviewer` on `pr-ready` | TDD, PR, independent review |
| S-9 | A feature across several modules, with design | `feature-team` | ADR, parallel developers, reviewer, integration branch |
| S-10 | Refactoring or a migration across modules (framework upgrade, API change) | `feature-team` with the task named as a refactoring | same shape: design the order, split by module, tests stay green |
| S-11 | Performance work, a data migration, a library or CLI change | agent `developer` | measure first is part of "root cause"; no special breed |
| **Fix** | | | |
| S-12 | One bug | agent `developer` (roost: label `flokpit`) | failing regression test first |
| S-13 | Many small independent issues | `bug-sweep` | planner triages, one developer per issue, reviewer |
| S-14 | A UI that should be explored and fixed without tickets | `ui-bugfixing` | tester explores, planner triages, developers merge into a dated branch |
| S-15 | A red pipeline on the default branch | roost `devops` on `ci-failed` | diagnosis first, fix PR or "not the pipeline's fault" |
| S-16 | A review that requests changes on an agent's PR after the agent is gone | roost `developer` on `changes-requested` | picks the branch up again |
| **Verify** | | | |
| S-17 | Review a pull request | agent or roost `reviewer` | runs the tests itself, inline findings, verdict |
| S-18 | Risk rating and integration tests on every PR | roost `pr-checker` | one comment, changes requested when critical |
| S-19 | Triage incoming issues | roost `issue-checker` on `new-issue` | type, reproduction, labels |
| S-20 | Test a UI, write e2e tests, accessibility audit | agent `tester` (roost: PR opened or updated) | headless browser, WCAG 2.2 AA |
| S-21 | End-to-end tests for an API, a CLI or a library | agent `tester` | same breed, no browser part |
| S-22 | Unit or integration tests for untested code (coverage backfill) | agent `developer` with that task | tests next to code are the developer's ground |
| S-23 | Security audit of a codebase or its dependencies | agent `security-auditor` (roost: weekly); with fixes `security-sweep` | reports, never fixes; the sweep adds developers and re-test |
| **Ship and keep running** | | | |
| S-24 | Prepare a release: scope, version, changelog, notes, regression | agent `release-manager` for a small one; `release` with a regression pass and blockers | a human tags and publishes |
| S-25 | Dependency updates | roost `devops` on `weekly-dependencies`, or agent `devops` | one PR per group, audit result, green checks |
| S-26 | Documentation: README, guides, API reference, changelog, AGENTS.md | agent `tech-writer` (roost: label `documentation`) | runs every example it documents |
| S-27 | Keep a repository healthy day to day without a task | `maintenance` | everything event-driven; the project manager reports |
| S-28 | Agents that hang, loop or lost their provider budget | roosts `watchdog`, `resumer` (part of every formation) | ask, replace, wake |
| **Not served, on purpose** | | | |
| S-29 | Merge into the default branch, tag, publish, deploy, rotate secrets, change repository settings | a human | every formation escalates these |
| S-30 | Debug a production system, read production data or logs | nobody | no access from the pod; paste the evidence into an issue, then S-12 |
| S-31 | Work that needs Docker, a database service or a cloud account inside the pod | partly | agents run what they can and take CI as evidence (9.4, X-1) |

Gaps this pass closed with new breeds: S-6, S-7, S-15, S-25 (`devops`), S-26
(`tech-writer`), S-23 (`security-auditor`), S-24 (`release-manager`); with new
formations: S-6 (`project-setup`), S-23 (`security-sweep`), S-24 (`release`),
S-27 (`maintenance`); with a roost preset: S-16. S-21 was closed by widening
the tester instead of adding a breed.

### 9.2 The new breeds and formations, walked

| # | Use case | Needs | Result |
|---|---|---|---|
| O-1 | devops: fix a failing workflow | `gh run view --log-failed`, edit `.github/workflows/**`, push; `workflows:write` | ✅ rules; ⚠️ the push needs the gateway to grant `workflows:write` (else BLOCKED, as instructed) |
| O-2 | devops: rerun a flaky run | `gh run rerun --failed`; `actions:write` | ✅ / ⚠️ same dependency on the gateway |
| O-3 | devops: write mise.toml and tasks, verify on a clean checkout | edit, `mise install`, `mise run check`, `git worktree add /tmp/clean` | ✅ |
| O-4 | devops: change a Dockerfile or Terraform | no Docker daemon, no cloud account | ⚠️ lint and render only; the build is proven by CI, stated in the PR |
| O-5 | devops: weekly dependency update | package manager, audit, lockfile, PR | ✅ for registries flokpit allows; ❌ private registries and Maven Central (X-3) |
| O-6 | tech-writer: fix a README and run its commands | edit anywhere, any command, PR | ✅ |
| O-7 | tech-writer: build a docs site (Docusaurus, MkDocs, Sphinx) | package manager, build | ✅; ⚠️ themes that fetch from hosts outside the allowlist fail the build |
| O-8 | security-auditor: dependency audit | `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`; advisory databases | ✅ npm, osv, GitHub; ⚠️ auditors that download a database from another host fail and are named in the report |
| O-9 | security-auditor: prove a finding against a local instance | start the app, `curl localhost`, script under /tmp | ✅ |
| O-10 | security-auditor: report on a private repository | `gh issue create`, `gh label create`; `issues:write` | ✅ |
| O-11 | security-auditor: report on a public repository | private advisory via `gh api`; `security_advisories:write` | ⚠️ needs the gateway scope; otherwise counts only in the channel and a QUESTION, as instructed |
| O-12 | security-auditor: read Dependabot alerts | `gh api repos/*/dependabot/alerts`; `security_events:read` | ⚠️ gateway scope; the local audit covers the same ground |
| O-13 | release-manager: find the release process, list changes since the last tag | `git tag --list`, `gh release list`, `git log`, `gh pr list --state merged` | ✅ |
| O-14 | release-manager: version bump with lockfile, changelog, package dry run | edit, package manager, `npm pack --dry-run`, `uv build` | ✅ |
| O-15 | release-manager: draft release notes | `gh release create --draft`; `releases:write-draft` | ⚠️ gateway scope; fallback is the notes in the PR, as instructed |
| O-16 | release-manager: tag and publish | - | by design a human (denied: `git tag v*`, tag pushes, `* publish`) |
| O-17 | developer roost `changes-requested` | `gh pr checkout`, read comments, fix, push to the PR branch | ⚠️ `write-own-branch` must cover a `flokpit/*` branch another agent created; the maintenance roost filters on `flokpit/*`. Gateway question (X-4) |

Formations (timeline checks, only the steps that could fail):

| Formation | Step | Result |
|---|---|---|
| project-setup | devops creates `setup/{flock}`; every PR goes against it; author merges after approval | ✅ `contents:write-integration-branch` for devops, developer, tester, tech-writer, architect |
| project-setup | repository without a single commit | by design a human makes the first commit; the kickoff asks for it |
| project-setup | reviewer proves `mise install && mise run check` in a fresh worktree | ✅ |
| security-sweep | lead (auditor) spawns developers | ✅ `may_spawn`, `lead_commands: fly` |
| security-sweep | fix PR on a public repository reveals the hole | ⚠️ escalated (`public_repository_disclosure`); a private fork is a human's setup |
| security-sweep | auditor re-tests the fix branch | ✅ `git fetch`, `git checkout`, its /tmp reproduction |
| release | release branch `release/{flock}`, blocker PRs against it, lead's bump last | ✅ |
| release | tester's regression pass on a project without a UI | ✅ since the tester covers APIs and CLIs |
| maintenance | all members `on_roost`; several roosts for one breed (developer, devops) | ✅ validator; ⚠️ events from before the flight start nobody, the kickoff lists those items |
| maintenance | lead idle for hours | ⚠️ the project-manager's `idle_timeout` is 60m; DONE posts of roosted agents wake it, a silent day lets it land. Fly it again or roost the formation on `townclock.event.daily` |
| feature-team | items that build on each other (was ❌, steps 7 and 13) | ✅ `integration_branch: feature/{flock}`; review gate kept: the author merges only after approval and green checks |

### 9.3 Different project setups

Each cell: can the breed follow its instructions there?

| Setup | developer, devops, tech-writer | reviewer, pr-checker, issue-checker | tester | architect, planner, PM, consultant |
|---|---|---|---|---|
| mise.toml with the contract tasks (reference: toy-example-bun) | ✅ | ✅ | ✅ | ✅ |
| no mise; Node with npm, pnpm, yarn or bun | ✅ any command (was: `bun add`, `bunx`, `yarn` denied) | ✅ (was ❌ for the checkers: only `mise run` allowed, so nothing ran) | ✅ | ✅ |
| no mise; Python (uv, pip, poetry, tox) | ✅ | ✅ (was ⚠️: only `uv sync`, `python3 -m pytest`) | ✅ | ✅ |
| Go, Rust, Ruby | ✅ if the tool is in mise.toml; registries are on flokpit's toolchain list (was ❌ D-8) | ✅ | ✅ | ✅ |
| Java, Kotlin, .NET, PHP | ⚠️ rules fine; Maven Central, Gradle plugins, NuGet, Packagist are not on the egress list (X-3) | ⚠️ same | ⚠️ same | ✅ |
| monorepo (workspaces, several packages) | ✅ house rule: work in the package the task names | ✅ | ✅ edits anywhere (was ❌: only root `package.json` and `tests/e2e/`) | ✅ |
| other layout (`doc/adr`, `e2e/`, `specs/`, `cypress/`) | ✅ | ✅ | ✅ (was ❌) | ✅ edits anywhere, "use the project's place" (was ❌: fixed paths) |
| project scripts (`./scripts/test.sh`, `./gradlew`, `just`, `task`) | ✅ (was ❌: no rule matched) | ✅ (was ❌) | ✅ | n/a |
| no tests at all | ✅ instructed: smallest test setup or commands with output | ✅ "not run" is stated, CI or reading is the basis | ✅ writes the first ones | ✅ |
| no CI | ✅ local checks are the evidence; `ci-green` cannot be met and the lead says so | ✅ | ✅ | ✅ |
| tests need Docker, Postgres or Redis | ⚠️ in-process or mise-provided alternative, otherwise CI is the evidence (X-1) | ⚠️ same, named in the review | ⚠️ BLOCKED when the app itself needs it | ✅ |
| no browser UI (API, CLI, library) | ✅ | ✅ | ✅ API and CLI end to end (was BLOCKED) | ✅ |
| page loads fonts or CDN scripts | n/a | n/a | ✅ common font and script CDNs allowed (was ⚠️ T-3); other hosts are mocked | n/a |
| preview or staging URL | n/a | n/a | ❌ host not on the list; BLOCKED with the host name (X-2) | n/a |
| issues disabled on GitHub | ✅ | ⚠️ issue-checker has nothing to do | ✅ reports in the PR | ⚠️ instructed fallback: checklist in the channel or a file |
| private repository | ✅ read scopes repeated in every credential list (was ❌ for pr-checker, issue-checker, consultant: `gh pr checks` would 403) | ✅ | ✅ | ✅ |
| PR from a fork | n/a | ✅ public fork; ❌ private fork without access | ✅ | n/a |
| default branch not `main` or `master` | ✅ instructions say "default branch"; the push deny rules only name main and master, the credential refuses the rest | ✅ | ✅ | ✅ |
| protected branches, required reviews | ✅ nothing pushes there | ✅ | ✅ | ✅ |
| reviewer and author share one GitHub identity | n/a | ✅ instructed fallback: COMMENT review with "Verdict:" line (was ⚠️ R-7) | n/a | n/a |
| empty repository (no commit) | ❌ nothing to branch from; a human makes the first commit (project-setup kickoff) | n/a | n/a | ⚠️ |
| no repository attached to the project | ⚠️ house rule: ask with QUESTION | ⚠️ same | ⚠️ same | ✅ planner, PM, consultant can work in chat |
| git submodules, Git LFS | ⚠️ public submodules ✅ (`git submodule update`); private ones and LFS objects depend on the gateway credential and the LFS host | ⚠️ | ⚠️ | ✅ |

### 9.4 Situations

| Situation | What happens now |
|---|---|
| Base moved under a pushed PR branch | developer merges the base (`git merge origin/<base>`); never a force push (was contradictory: "rebase, never force-push") |
| Several developers of a flock and PROGRESS.md | only the lead writes it (was: every developer, so every PR conflicted) |
| CI red for a reason outside the change | developer or devops reruns once (`gh run rerun --failed`) and names it |
| Developer finds an unrelated bug | files an issue (`issues:write`), keeps the PR small |
| Tester's screenshots for other agents | committed and pushed next to the report; the path and branch are named (was: a path inside the tester's pod) |
| pr-checker runs again on an updated PR | updates its one comment in place through `gh api` (was: a new comment each time) |
| Watchdog replaces a stuck agent, resumer respawns one | `commands: fly` (and `land`) granted (section 8) |
| A lead spawns its members | `lead_commands` now include `fly`; breeds with `may_spawn` carry `fly` for work outside a flock; the validator checks both |
| A needed scope is not granted by the gateway | the breed posts BLOCKED at that step and names the scope or file; nothing else stops |
| WebFetch to a documentation host | ✅ now. Before, the rules were written as `domain:<host>`, which flokpit renders as `WebFetch(domain:domain:<host>)`: no fetch ever matched |
| An agent needs a current fact (API change, error message) | WebSearch for every breed (provider-side, no egress needed) |
| Pipes, `cd`, `cat`, `ls` | allowed for every breed in `_base` (flokpit#255 found them denied) |

### 9.5 Permission decisions of this pass

| Decision | Reason | What still protects |
|---|---|---|
| `bash: {"*": allow}` for the nine breeds that run project code | per-command rules failed in every stack they did not list; interpreters were already allowed | deny rules for default-branch pushes, force pushes, merges, deletes, tags, publishing; pod without root or Docker; proxy; credential |
| edits anywhere in the checkout for every breed that writes | layouts differ; fixed paths blocked monorepos and other conventions | instructions name what a breed may change; reviewers and checkers cannot commit or push; review before merge; humans merge |
| one egress list in `_base`, with documentation hosts and font and script CDNs | per-breed lists dropped base entries (lists replace) and blocked lookups | read-only hosts; no credential to publish anywhere |
| WebFetch `*` and WebSearch for all | lookups instead of guesses | the proxy list; web content is data, not instructions (house rule) |
| `curl` and `wget` for breeds that run code | health checks and API tests | the proxy list |
| `issues:write` for developer, reviewer, tester | findings outside the task need a place | no delete rule; the gateway scope has no delete |
| `workflows:write`, `actions:write` for developer and devops | CI files are code; a workflow change is reviewed like any PR | own branch only; review; the gateway |
| `contents:write-integration-branch` for every breed that delivers into a flock branch | authors merge approved work themselves | never the default branch; approval by instruction, checked by the lead |
| issue-checker runs project commands, not only `mise run` | projects without mise could never be reproduced | it runs the project's commands, never a command copied from the issue text; pod and proxy; `issues:write` is its only write scope |
| higher memory for issue-checker (6Gi) | same builds as the developer, where 3Gi was OOMKilled | - |

Kept on purpose: no `sudo`, no `kubectl`, no subagents of the CLI, read
denies for `/proc`, service account and credential files, no merge into the
default branch, no tags or publishing, planner without project execution,
watchdog and resumer without a shell.

### 9.6 What depends on flokpit

| # | Item | Until then |
|---|---|---|
| X-1 | Service containers (Postgres, Redis) or Docker for tests | CI is the evidence; stated in PR and review |
| X-2 | A human-supplied extra egress host per flight (preview URLs, private registries) | tester and devops post BLOCKED with the host |
| X-3 | Registries missing from the toolchain hosts: Maven Central, Gradle plugin portal, NuGet, Packagist, Docker Hub metadata | JVM, .NET and PHP projects install nothing in the pod |
| X-4 | Gateway: the new scopes of CONCEPT 5.8, and whether `write-own-branch` covers a `flokpit/*` branch of an earlier agent | affected steps post BLOCKED; listed per use case in 9.2 |
| X-5 | Distinct GitHub identities for reviewing breeds (F-8) | the "Verdict:" comment fallback |
| X-6 | The lead of a standing flock (maintenance) outliving its idle timeout | fly again, or roost the formation daily |
| X-7 | Whether a replacement flown by the watchdog joins the flock of the agent it replaces (W-2) | a flock's lead is never replaced (the watchdog tells it); for other members it is unverified |

Not executed: everything in this section. The first real check is a flight
of each formation against toy-example-bun and against one repository that is
not flokpit-compatible.
