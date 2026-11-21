# Roost: event-triggered agents in flokpit

**Audience:** a flokpit developer agent (or human) implementing event-triggered
spawns; a breed or formation author who wants a breed to be started by an
event.
**Status:** draft, 2026-11-07. Nothing described here exists in flokpit yet;
the event catalogue (`events/catalogue.yaml`) and its schema exist in this
repository and are validated by `scripts/validate.py`.
Supersedes the sketch in flokpit issue [#217](https://github.com/flokpit/flokpit/issues/217)
("flokpit events"); the open questions there are answered or carried over below.
**Key words:** MUST, SHOULD and MAY as in RFC 2119. Requirements have ids
(`R-…`) so that issues, PRs and tests can cite them.

---

## 1. Summary

Today an agent is only started by a human or an agent typing `/spawn` or
`/fly`, and only woken by a message that addresses it. A **roost** adds a third
way: an event listener placed in a channel that says *when an event matching
this filter happens, start this breed (or fly this formation) here*. The birds
sit on the roost until something stirs them.

Events come from outside (GitHub: issue opened, pull request opened, CI run
failed), from the built-in **townclock** (minutely, hourly, daily and weekly
ticks whose details carry minute, hour and weekday) and from flokpit itself
(agent spawned, agent killed, flock flown or landed, provider tokens
exhausted and limit reset).

Every event that can happen is declared in this repository, in
`events/catalogue.yaml`, next to the breeds and pinned with them. A listener
can only refer to declared events and declared details.

## 2. Vocabulary

| Term | Meaning |
|---|---|
| **Event** | Something that happened. It has a **name** `<source>.event.<name>` (`townclock.event.hourly`, `github.event.issue_opened`) and **event details**, a flat map keyed `<source>.event_detail.<key>` (`townclock.event_detail.minute: 0`, `github.event_detail.repo: flokpit/flokpit`). Plus an envelope: id, time, org, channel (if channel-scoped), `caused_by`. |
| **Source** | Where a class of events comes from and the prefix of its names: `townclock`, `agent`, `flock`, `provider` (internal), `github` (external). |
| **Event catalogue** | `events/catalogue.yaml`: every source, every event, every detail with type and whether it is filterable. The single list of events that can happen. |
| **Townclock** | The built-in clock source. Emits `townclock.event.minutely`, `.hourly`, `.daily`, `.weekly` (UTC) with minute, hour, weekday, day and month as details. It never spawns anything by itself; cron-like schedules are detail filters. |
| **Filter expression** | The condition a listener states: `event_name_filter` (one pattern on the name) and an optional `event_detail_filter` (a map of detail key to pattern; every entry must match). See section 3 for the pattern forms. |
| **Listener** | Something that waits for events matching a filter expression: a roost (spawns or flies), and later a running agent or flock (is woken). |
| **Roost** | A listener placed in a channel by an op: filter expression plus action (`spawn` a breed or `fly` a formation), owned by the human who created it. Also the name of the feature. |
| **Preconfigured roost** (preset) | An entry of a breed's `roosts:` list: the filter expression the breed is written for, its default task and guards. Every breed declares its presets; a roost in a channel is created from one and may override the filters. |
| **Firing** | One match of a roost and the spawn or fly it caused (or the skip, with its reason). Firings are recorded with the event that caused them. |

Not used: "subscription" (attention stays channel-only), "hook" (reserved for
Claude Code hooks), "schedule" (the Temporal primitive), "trigger" as a noun
(a roost *is triggered*; the verb is fine).

## 3. Filter expressions

A filter expression is a JSON object:

```json
{ "event_name_filter": "townclock.event.hourly" }
```

```json
{ "event_name_filter": "townclock.event.minutely",
  "event_detail_filter": { "townclock.event_detail.minute": 0 } }
```

```json
{ "event_name_filter": "github.event.pull_request_*",
  "event_detail_filter": { "github.event_detail.repo": "flokpit/*",
                           "github.event_detail.draft": false } }
```

```json
{ "event_name_filter": "townclock.event.hourly",
  "event_detail_filter": { "townclock.event_detail.hour": 9,
                           "townclock.event_detail.weekday": "/^[1-5]$/" } }
```

Each pattern, for the name and for every detail value, is one of:

| Form | Example | Matches |
|---|---|---|
| **Exact value** | `0`, `false`, `"flokpit/flokpit"` | equality; numbers and booleans compare as typed, strings byte-wise |
| **Glob** | `"flokpit/*"`, `"github.event.pull_request_*"` | `*` any run of characters, `?` one character; only for strings and names |
| **Regex** | `"/^feature\\/.*/"`, `"/^[1-5]$/"` | a JavaScript regular expression between slashes, optional flags after the closing slash (`"/x/i"`); non-string details are matched on their string form |
| **Any of** | `[1, 2, 3]`, `["approved", "/^changes/"]` | a list of the above; one must match |

Rules:

- **R-F1** `event_name_filter` MUST match at least one declared event name
  (resolved against the catalogue at creation; `NOSUCHEVENT` otherwise).
  Every key in `event_detail_filter` MUST be a declared, filterable detail of
  every event the name filter can match (`NOSUCHDETAIL`).
- **R-F2** A detail that is absent (nullable detail with no value) matches
  only the exact value `null`.
- **R-F3** For `string[]` details (GitHub labels) the pattern is applied to
  each element; the entry matches if any element matches.
- **R-F4** Regexes are compiled once at creation with a 1 KB length limit
  and the `v`-flag syntax, rejected on error; matching runs with a step
  budget so that a pathological pattern cannot stall the roost workflow
  (the same concern as the ban-mask backtracking of
  [#51](https://github.com/flokpit/flokpit/issues/51)).
- **R-F5** Filters are evaluated in the roost workflow (section 6), never in
  the channel workflow.

## 4. A roost in the channel

Roosts are channel state, managed with one command and shown in the UI
(channel menu, "Roosts"; later a Settings page per org listing all roosts):

```
/roost add pr-review on github.event.pull_request_opened spawn reviewer "Review {github.event_detail.url}"
/roost add nightly   on townclock.event.daily fly bug-sweep "label:nightly"
/roost add standup   on townclock.event.hourly townclock.event_detail.hour=9 townclock.event_detail.weekday=/^[1-5]$/ spawn planner "Post the standup"
/roost add replace   on agent.event.killed agent.event_detail.breed=developer agent.event_detail.reason=crashed spawn developer
/roost list
/roost pause pr-review | /roost resume pr-review | /roost remove pr-review
```

Grammar: `/roost add <name> on <event_name_filter> [<detail key>=<pattern> ...] (spawn <breed> | fly <formation>) [<task>]`.

The usual way is shorter: every breed ships **preconfigured roosts** (its
`roosts:` list, section 8), and a roost is created from one of them, the
preset, overriding only what differs:

```
/roost add pr-review from pr-checker                        # preset pr-opened-or-updated as shipped
/roost add fixes     from pr-checker github.event_detail.head_ref=flokpit/*
/roost add hourly    from watchdog/quarter-hour townclock.event_detail.minute=0
/roost add nightly   from planner/issue-labeled github.event_detail.label=nightly "Plan the nightly issue {github.event_detail.url}"
```

Grammar: `/roost add <name> from <breed>[/<preset>] [on <event_name_filter>] [<detail key>=<pattern> | <detail key>= ...] [<task>]`;
without `/<preset>` the breed's first preset is used, `on` replaces the
preset's event (R-11, e.g. `from watchdog/quarter-hour on townclock.event.minutely`),
a bare `<key>=` removes that key from the preset's detail filter. The UI's "Add roost" dialog does the
same: pick a breed, pick a preset, edit the filters.

The command is sugar; the canonical form is the JSON filter expression of
section 3 plus the action, which the API and the UI use directly. A roost
created from a preset records `breed` and `preset` and only the overrides:

```json
{ "name": "hourly",
  "breed": "watchdog", "preset": "quarter-hour",
  "filter": { "event_detail_filter": { "townclock.event_detail.minute": 0 } } }
```

```json
{ "name": "standup",
  "filter": { "event_name_filter": "townclock.event.hourly",
              "event_detail_filter": { "townclock.event_detail.hour": 9,
                                       "townclock.event_detail.weekday": "/^[1-5]$/" } },
  "action": { "spawn": "planner", "task": "Post the standup" },
  "max_concurrent": 1, "cooldown": "1m", "self": false }
```

The task is a template: `{<detail key>}` is replaced with the detail value;
the full event (envelope and details) is handed to the agent as JSON in its
task context as well, so a breed can read it without parsing prose.

Rules:

- **R-1** Only channel ops (`+o`) MAY add, pause, resume or remove a roost;
  the check is the same as for `/spawn` and lives in the channel workflow.
- **R-2** A roost belongs to the human who created it (`owner`). Every firing
  spawns with `spawner = owner`: the agent uses the owner's provider account
  and git token, like a manual spawn. An agent MAY create a roost only if its
  breed's `privileges.may_spawn` covers the breed or formation; the owner is
  then the human at the root of the agent's spawn chain.
- **R-3** When the owner leaves the org, loses `+o`, or has no usable provider
  account, the roost is paused with a `NOTICE`, never deleted.
- **R-4** The breed or formation of a roost MUST resolve at creation time; a
  roost whose breed, event or detail disappears after a formations bump is
  paused with a `NOTICE` at the next firing.
- **R-5** A fly roost obeys the flock rules unchanged: it fails with
  `FLOCKFLYING` while a flock is flying in the channel and the firing is
  dropped (recorded, not queued).
- **R-11** Overrides of a preset: `event_name_filter` replaces the preset's
  as a whole; `event_detail_filter` merges per key, `null` removes a key;
  `task`, `max_concurrent`, `cooldown` and `self` replace. The merged
  expression MUST pass R-F1. The breed cannot be changed: a roost for
  another breed starts from that breed's preset.
- **R-12** A roost created from a preset keeps `breed` and `preset` and
  stores only its overrides, so a formations bump that changes a preset
  changes the roost; a roost whose preset disappears is paused with a
  `NOTICE` (R-4).

## 5. Guards against floods and loops

Agents cause events (pushing a branch opens a PR, a spawn is an
`agent.event.spawned` event). Without guards a roost can chase its own tail.

- **R-6** Every roost has `max_concurrent` (default 1): while that many
  agents started by the roost are still alive, a match is queued, not
  dropped (flokpit issue #265). The queue fires in order when a slot frees
  and the cooldown allows; it holds at most 20 matches per roost (the
  oldest is dropped as skipped `concurrent`) for at most 24 h, a queued
  match that no longer matches the roost's filter is dropped as `expired`,
  a paused roost keeps its queue and a removed one drops it. An agent
  frees its slot when it ends or when it posts with intent `BLOCKED`.
- **R-7** Every roost has `cooldown` (default `1m`) and a per-channel cap of
  firings per hour (`FLOKPIT_ROOST_MAX_FIRINGS_PER_HOUR`, default 30). A match
  arriving while older ones wait in the queue joins it; otherwise skips are
  final and recorded with the reason (`cooldown`, `rate`). The firing log
  shows a queued match as `queued` until it fires or is dropped, and a firing
  whose agent never started as `failed` with the reason.
- **R-8** Events are deduplicated by the envelope id (GitHub delivery id,
  townclock minute, agent nick plus spawn turn) within 24h.
- **R-9** Internal events carry `caused_by` in the envelope and, where
  declared, as a detail (the nick of the agent whose action produced them).
  A roost does not fire on an event caused by an agent it started itself,
  unless `self: true` is set.
- **R-10** Every firing counts against the org's agent caps
  (`FLOKPIT_MAX_AGENTS`, `FLOKPIT_MAX_AGENTS_PER_ORG`) and the owner's budget
  like a manual spawn; there is no separate roost budget.

## 6. Sources

The catalogue is the source of truth for names and details; this section
only says how each source gets its events into flokpit.

### 6.1 GitHub (external)

- flokpit-server exposes `POST /api/roost/github/<org slug>`; each org has a
  webhook secret (Settings > Integrations, generated by flokpit, shown once).
  Signature `X-Hub-Signature-256` MUST verify, otherwise `401` and no event.
- Mapping: the webhook belongs to the org; a channel receives the event if
  the repository matches the channel's bound repository
  ([#106](https://github.com/flokpit/flokpit/issues/106)) or a roost in the
  channel filters on `github.event_detail.repo`. Events without any matching
  roost are counted and dropped.
- Declared: `issue_opened`, `issue_labeled`, `pull_request_opened`,
  `pull_request_review_submitted`, `push`, `workflow_run_failed`. A GitHub
  App ([#190](https://github.com/flokpit/flokpit/issues/190)) can replace the
  per-org webhook later without changing the event names.

### 6.2 Townclock (internal)

- `townclock.event.minutely` every minute, `.hourly` at minute 0, `.daily`
  at 00:00 UTC, `.weekly` on Monday 00:00 UTC; details carry the calendar
  fields so that a schedule is a detail filter (`hour: 9`, `weekday: [1..5]`
  as a list or regex). A `cron=` convenience MAY be added later as sugar
  that compiles to a `minutely` filter; it adds no event.
- The townclock is a timer in the roost workflow that sleeps until the
  earliest tick any townclock roost of the org can match, so an org without
  townclock roosts costs nothing.
- A missed window (worker down) fires at most once on catch-up, never once
  per missed minute.

### 6.3 flokpit (internal)

`agent.event.spawned`, `agent.event.killed`, `flock.event.flown`,
`flock.event.landed` are emitted by the channel workflow where they happen,
scoped to that channel. `provider.event.budget_exhausted` and
`provider.event.budget_reset` (detail `budget`: `tokens` for the provider's
rate limit, `usd` for the account's monthly `budget_usd`) are emitted by
flokpit-server (the egress proxy sees the provider's rate limit
answers and headers), org-wide, and reach every channel of the org that has
a matching roost. An agent that is shut down because its account ran out of
tokens ends with `agent.event_detail.reason: exhausted`; the pair
`budget_exhausted` / `budget_reset` carries the nicks of the interrupted
agents so that a resumer can bring them back (section 8.1).

## 7. Where it runs (Temporal)

- One `RoostWorkflow` per org (`roost:<org slug>`) holds the roosts of all
  channels of the org, the firing log (ring buffer like channel history) and
  the townclock timer. It receives events as signals (GitHub and provider
  from flokpit-server, agent and flock from channel workflows), evaluates
  the filter expressions and sends the existing `spawn` or `fly` Update to
  the channel workflow with `by = owner`. Matching outside the channel
  workflow keeps ticks and unmatched webhooks out of channel histories.
- `/roost` commands are Updates on the channel workflow (for the `+o` check),
  which forwards them to the roost workflow; the channel keeps only the roost
  names for `/roost list` and the UI.
- `FlokpitRoosts` search attribute on the roost workflow (count of active
  roosts) for the admin page, like `FlokpitFlocks`.

## 8. What lives in this repository

- **`events/catalogue.yaml`** (schema `specs/event-catalogue.schema.json`,
  checked by `scripts/validate.py`): every source with origin and scope,
  every event with name, source, description, `since` release and its
  details with type (`string`, `integer`, `number`, `boolean`, `string[]`),
  optional `enum`, `min`, `max`, `nullable` and `filterable` (details such
  as URLs, shas and costs are declared `filterable: false`). Rules enforced:
  names are `<source>.event.<name>`, detail keys `<source>.event_detail.<key>`,
  names are unique, the source is declared.
- **R-C1** flokpit MUST emit only declared events with only declared
  details, and MUST validate filter expressions against the pinned
  catalogue (R-F1). Adding an event is: declare it here, release, bump the
  pin in flokpit, emit it.
- **R-C2** Removing or renaming an event or detail is a breaking change of
  the catalogue: it is marked `deprecated` for one release before removal,
  and roosts that reference it are paused (R-4), never silently broken.
- Every breed declares `roosts:` (schema `$defs/roosts` in
  `specs/breed.schema.json`, required on a resolved breed, empty for a breed
  that is never roosted): a list of `{name, description, filter, task,
  max_concurrent?, cooldown?}`, its preconfigured roosts. A roost in a
  channel is created from one of them (R-11, R-12); the UI lists them per
  breed. The list is not a listener by itself: nothing fires until an op
  creates a roost from it. The validator checks every filter against the
  catalogue (R-F1 at authoring time) and every `{<detail key>}` of the task
  against the matched events. Shipped presets: `developer`, `architect`,
  `planner` and `consultant` on `github.event.issue_labeled` with their
  labels (`flokpit`, `architecture`/`design`, `epic`/`plan`,
  `needs-decision`), `reviewer` on `pull_request_opened`, `tester` on
  opened or updated pull requests, `project-manager` on the townclock every
  weekday at 09:00 UTC, and the four roost-only breeds of section 8.1.
- A formation MAY declare `roosts:` (schema `$defs/roosts` in
  `specs/formation.schema.json`): `{name, breed, preset, filter?, task?,
  max_concurrent?, cooldown?}`, each from a member breed's preset with the
  overrides of R-11. `/fly` creates them in the flock channel with the
  flock's placeholders rendered (`{repo}`, `{flock}`, ...), `/land` removes
  them. Members with `start: on_roost` are started only by such a roost and
  count toward `max_agents` like every member. All four shipped formations
  roost a `watchdog` and a `resumer`; `bug-sweep`, `feature-team` and
  `ui-bugfixing` roost a `pr-checker` on the flock's own branches
  (`head_ref: flokpit/*`) of `{repo}`, `bug-sweep` also an `issue-checker`,
  and `product-discovery` a `consultant` on `needs-decision` issues. The
  watchdog's and resumer's `spawn_tree` entries name the members they may
  replace plus the `consultant` member.

### 8.1 Event breeds shipped here

| Breed | Roosted on | What it does | Stops |
|---|---|---|---|
| `watchdog` | `townclock.event.minutely`, minute in `[0, 15, 30, 45]`, one at a time, `max_lifetime: 12m` | Inventories the agents of the channel, classifies them (working, waiting, unclear, troubled, stuck), asks the unclear ones once, spawns one consultant for troubled ones and tells them whom to ask, kills stuck ones and respawns the same breed with the same task (never a flock lead, never an agent waiting on a human), posts a "watchdog report" | after one pass; the next watchdog reads the report and the answers |
| `issue-checker` | `github.event.issue_opened` | Classifies the issue, reproduces a bug in the checkout, appends a "Triage" section to the description, adds existing labels, comments only when the author must act | after one issue |
| `pr-checker` | `github.event.pull_request_opened` or `pull_request_updated`, `draft: false` | Checks out the PR, runs `mise run test-suite` (or `check`, `test`), rates the integration risk 1 to 5, keeps one marked comment per PR, requests changes for critical findings (blocks the merge under branch protection), never approves | after one PR |
| `resumer` | `provider.event.budget_reset` | Wakes the interrupted agents of the account owner that are still alive and respawns the ones shut down with reason `exhausted`, with their task; flock members go to their lead; posts a "resumer report" | after one pass |

All four are roost-only: their `roosts:` preset is the only way they start,
and the roost gives them the event (section 4: the full event is in the task
context). They need nothing else: no repository for `watchdog` and
`resumer` (`workspace.clone: false`), the channel's repository for the two
checkers. `watchdog` and `resumer` carry `chat.op: true` because `chat_kill`
and `chat_spawn` need `+o`; their `may_spawn` lists every breed they may
replace, and the consultant breed is ported here from flokpit's shipped
breed file for the watchdog to spawn.

## 9. Phases

1. **Roost core:** `/roost` command, roost workflow, filter expressions,
   internal sources (`agent.*`, `flock.*`), guards R-6 to R-10, firing log,
   UI list in the channel menu.
2. **Townclock:** the four tick events, catch-up rule, `#community` digests
   of [#216](https://github.com/flokpit/flokpit/issues/216) as the first
   user.
3. **GitHub:** webhook endpoint and secret, the six declared events,
   repository mapping, Settings > Integrations card.
4. **Catalogue in flokpit, breeds and formations:** load and validate
   against the pinned catalogue (R-C1), breed `events:` as roost defaults
   in the UI, formation `roosts:`, validator rules for formations (breeds
   are done here).
5. **Provider events:** `budget_exhausted` and `budget_reset` from the egress
   proxy's accounting (rate limit headers) and the usage indicator (monthly
   budget), kill reason `exhausted`, the `resumer` breed.

## 10. Open questions

- GitHub actor: agents push as the human who spawned them, so a PR opened by
  an agent looks like the human's PR. R-9 covers internal events only; for
  GitHub events the branch name prefix of flocks (`flock/<name>/…`) is the
  only hint. Decide whether agents should push with a marker (commit trailer
  or branch prefix) that a detail filter can exclude.
- Waking a running agent or flock on an event ("listener" in section 2,
  [#217](https://github.com/flokpit/flokpit/issues/217)'s "subscriptions")
  is left out of the first phases. The natural form is a roost action
  `post "<message> @nick"` into the channel, so attention stays
  channel-only; a breed's `events:` would then double as the default
  filter for such a wake.
- Where the org-wide roost list is edited: channel menu only, or also a
  Settings > Roosts page with all roosts of the org (needs the org-level
  permission question of
  [#233](https://github.com/flokpit/flokpit/issues/233)).
- Retention of the firing log and whether firings appear in the channel
  history as a `ROOST` system line (proposed: yes, one line per firing and
  per skip with reason).

## 11. References

flokpit issues:

- [#217](https://github.com/flokpit/flokpit/issues/217) flokpit events: external and internal event triggers for agents (the sketch this draft supersedes)
- [#190](https://github.com/flokpit/flokpit/issues/190) Integrations: GitHub issues as tasks, then Linear, Jira, Slack, Notion, GitLab (GitHub App, Settings > Integrations)
- [#216](https://github.com/flokpit/flokpit/issues/216) Global channels for onboarding, QA, feedback and community (first townclock user)
- [#106](https://github.com/flokpit/flokpit/issues/106) Channel repository: bind a channel to a GitHub repository (webhook mapping)
- [#180](https://github.com/flokpit/flokpit/issues/180) Flight recorder: replay a channel's day (consumer of the firing log)
- [#211](https://github.com/flokpit/flokpit/issues/211) Wire flocks into Temporal: `/fly`, `/land` (the `fly` Update a roost reuses)
- [#233](https://github.com/flokpit/flokpit/issues/233) Server admin UI (org-level permission question for a Settings > Roosts page)
- [#105](https://github.com/flokpit/flokpit/issues/105) Organisations as the tenant (org-scoped roost workflow, webhook secret per org)
- [#51](https://github.com/flokpit/flokpit/issues/51) Ban mask regex backtracking hang (why regex filters get a step budget)

Documents:

- `events/catalogue.yaml`, `specs/event-catalogue.schema.json` (the declared events)
- `docs/CONCEPT.md` sections 4 and 5.9 (breed and formation data model)
- `../flokpit/docs/concepts/temporal.md` (`fly` Update, flocks state)
