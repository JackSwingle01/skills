## What it does

`loose-ends` reads every pull request merged since its last run and files what they left for a person as one ticket: an agenda you grill through with [grill-with-docs](../../skills/engineering/grill-with-docs/SKILL.md). It reads each PR's primary sources (the body, the work log, the decision records and glossary changes, the comments from people with write access), not a summary of them.

It gathers and files; it never answers. Every loose end is a question for you, because each one is either work nobody has ticketed or a choice nobody with the authority to make it has made. Answering them is the grilling session's job, which records each answer where it belongs.

## When to reach for it

Type `/loose-ends`, or the agent reaches for it when you ask what recent PRs left open. It is built to run unattended on a schedule (daily, say), so the ticket is waiting for you rather than you remembering to sweep.

Reach for it when agents merge work faster than you read the PR bodies, and especially when an unattended agent builds tickets: its PRs carry decisions it made on its own. For improving how agents work rather than what they decided, use [retro](../../skills/engineering/retro/SKILL.md) instead.

## What counts as a loose end

| Class | Examples |
|---|---|
| **Confirm** | a choice an agent marked as made unattended, a test whose bar it lowered, a number it tuned to pass a gate, a DR an agent wrote on its own |
| **Follow-up** | work found outside the PR's scope, or something the PR could not verify |
| **Term** | a `(term)` revision in a work log, a glossary entry an agent added, a word a DR or the code uses that the glossary lacks |

Anything already ticketed, answered in a later PR or comment, fixed on the default branch, or on an earlier sweep's agenda is dropped before filing. A sweep that finds nothing files nothing.

## Prerequisites

An issue tracker the agent can read and write, documented in `AGENTS.md`/`CLAUDE.md`, and PR bodies and work logs that record follow-ups and revisions: [pr](../../skills/engineering/pr/SKILL.md) and [work-log](../../skills/engineering/work-log/SKILL.md) write them in the shape it reads. A scheduled job passes the window itself (the PRs merged since its last successful run). Run by hand, it finds where the last sweep stopped from a marker in its last ticket, so it keeps no state of its own. A sweep that finds nothing open posts nothing.

## Common questions

**Why one ticket, not a ticket per follow-up?**

A follow-up is rarely ready to build: it needs a decision first, often one that hangs off another item on the same list. One agenda lets the grilling work the items as a tree, and the answers become tickets once they are ready to be.

**Will my automated issue agent pick the ticket up and try to build it?**

It should not. The ticket is marked as a grilling ticket and carries the repo's label for keeping a ticket out of automated work queues. Check that your queue honours that label.

## It's working if

- Decisions an unattended agent made reach you within a day, instead of when they surprise you later.
- PR follow-ups stop going stale in merged PR bodies.
- The glossary grows from the grilling sessions, not from agents quietly redefining words.

## Where it fits

Periodic maintenance, feeding the main flow at its first step: `loose-ends → grill-with-docs → to-tickets → implement`. [pr](../../skills/engineering/pr/SKILL.md) and [work-log](../../skills/engineering/work-log/SKILL.md) write what it reads, and [grill-with-docs](../../skills/engineering/grill-with-docs/SKILL.md) resolves what it files. [dev-flow](../../skills/engineering/dev-flow/SKILL.md) maps the whole set.
