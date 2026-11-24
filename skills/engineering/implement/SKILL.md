---
name: implement
description: "Implement a piece of work based on a spec or set of tickets: scout, design, build test-first, review, and open a pull request. Use when the user or a parent agent asks to implement, build, or ship a ticket, issue, or spec, or when an orchestrating agent hands a subagent a ticket to build."
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask. If the ticket links a spec, read it.

If the repo requires a ticket for every change (check `AGENTS.md`/`CLAUDE.md`) and there isn't one yet, create it first using the repo's conventions. Follow the repo's branch conventions too.

Call the Skill tool with "work-log" and keep this ticket's log from before the first line of code.

Before designing, start a sub-agent with a fresh context window to scout the change: its blast radius, test coverage, and existing patterns, how it can be validated locally, and the existing behavior it affects, grounded in real usage where logs or data allow. Record that behavior in the work log's hypothesis.

Before writing code, call the Skill tool with "codebase-design" and design the change to fit the existing system, not to sit on top of it. Decide for each affected behavior whether it stays, changes, or goes, and flag any change the ticket didn't ask for. Then design in two steps:

1. Decomposition: break the work into stages.
2. Encapsulation: pick the right abstraction for each stage at every level, from modules down to functions and data structures, so each stage can be verified on its own.

Before writing code, start a sub-agent with a fresh context window for an adversarial design review against the ticket and the scout's report. Weigh each finding on its merits rather than accepting it, and log each change you make as a Revised line.

Call the Skill tool with "verification" to choose a check for each risk and when to run it.

Call the Skill tool with "tdd" where possible, at pre-agreed seams. If the spec names seams, use them unless there is a good reason not to, and log any seam you add or change as a Revised line.

Use whatever lint, typecheck, and test commands the repo has, at `verification`'s cadence.

After the targeted tests pass, validate each acceptance criterion end to end, and log any you couldn't validate as a Follow-up with what was missing.

Commit your work to the current branch, following the repo's commit conventions.

Then start the full suite and every other check `verification` scheduled for before the PR in the background and, without waiting for them, call the Skill tool with "code-review" against the branch's base, passing it the work log's path, with decisions made during the work as context to challenge, not spec. When the review returns, read the checks' result. Commit a fix for a failed check on its own, then commit the review's fixes separately. The review commit is a measurement: across runs, the share that needed one shows how well the implementation and the review are each doing their job.

Finally, call the Skill tool with "pr", passing it the work log's path, and open the pull request in this session using the repo's conventions.
