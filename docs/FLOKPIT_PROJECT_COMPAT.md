# Making a project flokpit-compatible

How a repository has to look so that every breed and formation in this
repository can work on it inside a flokpit agent pod. The contract has three
parts: the **toolchain** (what to install), the **tasks** (how to run things)
and the **places** (which files and directories a breed writes to). It is
vendor-neutral: the same `mise.toml` serves a developer's laptop, CI and the
flokpit agent image. The reference project is
[`flokpit/toy-example-bun`](https://github.com/flokpit/toy-example-bun).

## 1. The toolchain comes from mise, not from the image

The flokpit agent image carries only flokpit's runtime: `claude`,
`flokpit-agentd`, `git`, `gh`, `jq`, `rg` and [`mise`](https://mise.jdx.dev).
There is no project toolchain in it (no bun, python, make, pnpm, Playwright).
A repository declares what it needs in a mise configuration at its root:

```toml
# mise.toml
min_version = "2026.1.0"

[tools]
bun = "1.4.4"                      # the app
node = "24.22.1"                   # only for the Playwright test runner and CLIs
"npm:@playwright/cli" = "0.1.22"   # the browser CLI the tester drives
agent-browser = "0.39.2"           # headless browser sessions

[env]
PORT = "{{ get_env(name='PORT', default='3000') }}"

[hooks]
postinstall = "bun install --frozen-lockfile"   # dependencies, right after the tools
```

What flokpit does with it (`flokpit-agentd`, boot step "toolchain"):

1. After the clone it runs `mise install` in the checkout. The configuration is
   trusted (`MISE_TRUSTED_CONFIG_PATHS=/workspace`, `MISE_YES=1`), so `[env]`
   templates and `[hooks]` work without `mise trust`; installs and cache land
   on the workspace volume (`/workspace/.mise`).
2. It passes the result of `mise env` (the tool `PATH` and the project's
   `[env]`) to the agent, so plain commands work in every directory: `bun test`,
   `npx playwright test`, `agent-browser open ...`. Variables flokpit owns
   (`FLOKPIT_*`, `CLAUDE_*`, `ANTHROPIC_*`, `MISE_*`, `GIT_*`, `GH_*`, `HOME`,
   the proxy variables) cannot be set by a project.
3. It tells the agent the outcome in the system prompt (`Toolchain: ...`). A
   failure never stops the agent; the agent reports `BLOCKED` when a tool it
   needs is missing. The step has a five minute budget.

Rules that follow:

- **Pin exact versions.** `bun = "1.4.4"`, not `"latest"`: mise needs no
  version lookup beyond its metadata host, and two agents of a flock get the
  same tools.
- **Downloads go through the egress proxy.** Allowed are GitHub releases
  (`github.com` and its asset hosts), `nodejs.org`, `registry.npmjs.org`,
  `pypi.org`/`files.pythonhosted.org` and mise's metadata host
  `mise-versions.jdx.dev`. Tools from other hosts fail to install; prefer
  core tools (`bun`, `node`, `python`, `go`, `rust`), the `npm:` backend and
  `aqua:`/`ubi:` tools released on GitHub.
- **Browsers are the exception.** Chromium cannot be installed by a project
  (no browser CDN is reachable). The `browser` image variant bakes Chromium for
  one Playwright release (`PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright`,
  `AGENT_BROWSER_EXECUTABLE_PATH`); pin `@playwright/test` in `package.json`
  to that release (currently `1.64.1`) and `agent-browser` uses the baked
  binary. Do not run `playwright install` in the pod: `/opt/ms-playwright` is
  read-only and the command fails on its lock file; a `browser:install` task
  checks for `$PLAYWRIGHT_BROWSERS_PATH/chromium-*` first (see section 2). A
  different Playwright version would look for a build that is not there and
  fail with a clear error.
- **No `mise trust` in instructions.** It is not needed in the pod and not
  allowed by the breeds' tool rules.
- **Keep `mise.local.toml` out of git** and put CI-only settings in
  `mise.ci.toml` (`MISE_ENV=ci`).

## 2. Tasks: what each breed looks for

Breeds run a project through **mise tasks** (`mise run <task>`) when the
repository has a mise configuration, and only otherwise fall back to the
commands named in the project's `AGENTS.md` or `CLAUDE.md` (which flokpit hands
to the agent with its first turn), then its README. Every breed may run
`mise tasks` and `mise ls`; breeds that run code may run `mise run <task>` and
`mise install`. Task names are the contract; what they do is the project's
business. Define them in `[tasks.<name>]` with a `description`, so `mise tasks`
is self-explaining.

| Task | What it must do | Needed by | Notes |
|---|---|---|---|
| `start` | run the whole application in the foreground on `$PORT` (default 3000) with one plain command, no watch mode | **tester** (required), ui-bugfixing | the tester starts it and leaves it running; `PORT` from `[env]` |
| `dev-server` | the same with restart on changes | tester, developer (optional) | preferred by the tester when both exist |
| `test` | unit tests | **developer**, **reviewer**, **tester** (required) | fast; no browser |
| `test:integration` | tests against a running or spawned instance of the app, no browser | developer, reviewer (optional) | |
| `e2e` | browser end-to-end tests under `tests/e2e/`; starts the app itself | **tester** (required), developer, reviewer | Playwright, Chromium only |
| `test-suite` | every automated test (`test`, `test:integration`, `e2e`) | **reviewer** (required: one command to verify a PR), developer | `depends` on the three |
| `typecheck`, `lint` | static checks | developer, reviewer (optional) | |
| `check` | what CI runs: static checks plus `test-suite` | **developer** (required: the "done" gate), reviewer, bug-sweep, feature-team | a developer may not claim done before `mise run check` is green |
| `smoke` | start, hit the app once, stop; no browser | developer (optional) | cheap confidence for small fixes |
| `ui-test [path]` | start the app if nothing answers on `$PORT`, open a headless browser session on `path`, save a screenshot under `screenshots/`, print the accessibility snapshot; leave both running | **tester** (required for exploratory testing), ui-bugfixing | the session continues with `agent-browser click|fill|snapshot|screenshot ...` |
| `ui-test:stop` | close that browser session and the app it started | **tester** (required with `ui-test`) | |
| `browser:install` | download the browser the tests need | tester (optional) | must be a no-op when `PLAYWRIGHT_BROWSERS_PATH` already holds a `chromium-*` build (the pod: that directory is read-only, so a plain `playwright install` fails on its lock file even when the version matches) |
| `install` | project dependencies from the lockfile | all (optional) | normally the `postinstall` hook already did this |

Minimum per breed:

| Breed | Tasks it needs | Fallback without mise |
|---|---|---|
| developer | `test`, `check` (and whatever `check` depends on) | the test and lint commands in AGENTS.md / CLAUDE.md |
| reviewer | `test-suite` (or `check`) | the test commands in AGENTS.md / CLAUDE.md |
| tester | `start` (or `dev-server`), `e2e`, `ui-test`, `ui-test:stop`; `test` to run the suite it inherits | the start command in AGENTS.md / CLAUDE.md, `npx playwright test`, `agent-browser` directly |
| architect, planner, project-manager | none (they read code and work on GitHub) | - |

A project that has no browser UI needs no `start`, `e2e` or `ui-test`; the
tester then posts `BLOCKED` with that reason, and formations with a tester
(`ui-bugfixing`, the optional tester of `feature-team` and `product-discovery`)
are not the right choice for it.

## 3. Places: what the breeds read and write

The breeds' edit rules are path patterns under `/workspace/repo`; a project
that keeps these paths can be worked on by every breed without widening a rule.

| Path | Who | Why |
|---|---|---|
| `AGENTS.md` (or `CLAUDE.md`) | every breed reads it | the fallback when there is no mise configuration, and the place for conventions (test layout, commit rules); flokpit passes it to the agent with its first turn, at most 16 KB |
| `PROGRESS.md` | developer, tester write; feature-team's `progress_file` | what is done and what is next, kept up to date by the agents |
| `tests/e2e/`, `playwright.config.*` | tester (its only writable paths in the checkout) | one failing end-to-end test per confirmed bug |
| `docs/adr/`, `docs/architecture/` | architect (its only writable paths) | ADRs and architecture notes, Mermaid in markdown |
| `docs/discovery/` | product-discovery's `progress_file` (`docs/discovery/<flock>.md`) | the discovery record |
| `docs/decisions/` | flokpit's shipped consultant breed | decision memos |
| GitHub issues and labels | planner, project-manager, bug-sweep (`flock:<flock>` label) | the backlog; the project must allow issues |
| the default branch | humans only | agents push `flokpit/<nick>` branches and open PRs; a formation's `integration_branch` (`ui-bugfixing/<date>`) is created by a developer and merged into by developers |

Directories must exist in git (a `README.md` inside is enough) when a breed
has to write into them: the tester's and architect's edit rules allow files
under those paths, not the creation of unrelated ones.

## 4. Checklist

- [ ] `mise.toml` at the root with pinned `[tools]`, `PORT` in `[env]`, a
      `postinstall` hook for dependencies; `mise.ci.toml` for `CI=1`
- [ ] tasks `start`, `test`, `e2e`, `test-suite`, `check`, `ui-test`,
      `ui-test:stop` (plus `typecheck`/`lint` where they exist), each with a
      `description`
- [ ] `@playwright/test` pinned to the browser image's Playwright release;
      tests under `tests/e2e/`, `playwright.config.ts` reads `PORT` and `CI`
- [ ] `AGENTS.md` (referenced from `CLAUDE.md`) with setup, the task table and
      the plain-command equivalents, conventions and layout
- [ ] `PROGRESS.md`, `docs/adr/`, `docs/architecture/`, `docs/discovery/`,
      `docs/decisions/` present
- [ ] `.gitignore` covers `node_modules/`, `test-results/`,
      `playwright-report/`, `screenshots/`, `.run/`, `mise.local.toml`
- [ ] `mise install && mise run check` passes on a clean clone
- [ ] issues enabled on GitHub; the people who spawn agents have `repo` scope

## 5. Verifying a project

Locally, with mise installed:

```sh
git clone <repo> && cd <repo>
mise trust && mise install
mise run check            # what the developer and reviewer run
mise run ui-test && mise run ui-test:stop   # what the tester does (needs Chromium)
```

In the agent image (what the pod does; `--read-only`, uid 1000, writable
`/workspace`, `/home/agent`, `/tmp`, `/dev/shm`):

```sh
docker run --rm --read-only --user 1000:1000 --tmpfs /tmp --tmpfs /dev/shm \
  -v "$PWD/ws:/workspace" -v "$PWD/home:/home/agent" -v "<repo>:/src/repo:ro" \
  -e HOME=/home/agent --entrypoint bash ghcr.io/flokpit/flokpit/agent-browser:main -c \
  'git clone -q /src/repo /workspace/repo && cd /workspace/repo && mise install && mise run check'
```

`toy-example-bun` passes both; use it as the template for a new sandbox.
