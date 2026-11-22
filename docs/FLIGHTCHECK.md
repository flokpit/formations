# Flight check

Run before a tag is cut (`README.md`, "Use a release"). It is the acceptance
test of the behaviour in `breeds/_base.yaml` house rules and the formations'
`kickoff`, `member_brief` and `termination`. It can only pass once flokpit
reads those fields (`docs/CONCEPT.md` section 7.6, V-1 to V-3); until then it
is the acceptance test of that wiring.

## Setup

- Repository `toy-example-bun` with its mise contract
  (`docs/FLOKPIT_PROJECT_COMPAT.md`), the release archive to be tagged mounted
  in flokpit, a quota for the pods at take-off (`formations/README.md`:
  `ui-bugfixing` 5, `feature-team` 2, up to 9 and 14 later).
- Fly `ui-bugfixing` (no task), then `feature-team` with a small task (for
  example "add a footer with the version to the page"). Do not intervene except
  where a pass line below says a human acts.

## Pass lines

Each is observable in the channel and the pod logs. Record pass or fail and the
evidence (message ids, run links) per formation.

| # | Pass line |
|---|---|
| 1 | No member makes a tool call before the lead's first message to it; no member hands out work |
| 2 | No agent posts the same text twice; no post exists that only acknowledges (messages per finished item stay under the bound set for the run) |
| 3 | The final summary is addressed to the user and arrives as a notification |
| 4 | The flock reaches `landed` without a human (the lead lands it); with a member that failed to start, a honk is raised instead |
| 5 | The tester opened a browser page and got a 200 from the started app on `localhost` (browser binary present, server start allowed, HTTP to `localhost` allowed) |

## After the run

A failed line is a defect in the content (this repository) or the wiring
(flokpit); file it where its cause is. The result decides whether P6 (developer
and reviewer without a browser) and P7 (tester keeps
`contents:write-integration-branch`) of issue #19 hold.
The tester's background server start is part of line 5 once it has been
reproduced; add its documented form here then.
