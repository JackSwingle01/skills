## What it does

`work-log` keeps one small file per ticket recording what the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) expected before it wrote any code, and every point where that expectation turned out wrong. It opens with a **hypothesis** (which modules change, which existing behaviour they touch, which tests stay green, which test goes red first and why), then gains a `Revised:` line each time the approach changes and a `Follow-up:` line for work that belongs outside the ticket.

It records surprises, not progress. A log of "did X, then did Y" restates the diff. A log of "expected X, found Y, did Z" is the one thing the diff can't show you, and it is written at the moment of the surprise, so it never depends on the agent's memory of the [session](https://www.aihero.dev/ai-coding-dictionary/session).

## When to reach for it

Type `/work-log`, or the agent reaches for it automatically when a task fits: starting a build or a bug fix, changing approach mid-build, or changing a pre-existing test. [implement](https://aihero.dev/skills-implement) loads it at the start of every ticket, so in the main flow you never type it.

Reach for it directly when you're building outside `/implement` and still want the PR to carry its revisions.

## Prerequisites

It writes into `.agent-logs/` at the repo root and keeps that folder out of git by adding it to the repo's local exclude file, so nothing lands in your `.gitignore` or your commits.

## Revisions are the point

A **revision** is a fact and an action: `Revised: totals computed in both Invoice and Cart → Cart calls Invoice.total`. The log never gets rewritten; a later line that contradicts an earlier one is the record working. A revision the agent can't phrase in your glossary's terms gets a `(term)` tag, which marks a gap in the domain language rather than in the code.

| Reader | What it does with the log |
| --- | --- |
| [code-review](https://aihero.dev/skills-code-review) | Flags any divergence from the hypothesis, or changed pre-existing test, with no matching revision |
| [pr](https://aihero.dev/skills-pr) | Copies the revisions verbatim into the PR's Revisions section, and the follow-ups into Follow-ups |
| [retro](https://aihero.dev/skills-retro) | Treats each revision as a surprise; one that recurs across PRs is its strongest candidate, and a `(term)` tag points at the glossary |

## Common questions

**Why isn't the log committed?**

It is scaffolding for one ticket. What's worth keeping leaves the log by two routes: the revisions get copied into the PR body, and the confirmed cause of a bug goes into the commit message. Committing the log as well would leave a second, drifting copy in the tree.

**Is this the same as the work-log skill some harnesses ship?**

No. This one is scoped to a ticket and feeds review, the PR, and retros. If your harness also has a skill named `work-log`, the plugin's namespaced name (`mp:work-log`) tells them apart.

## It's working if

- A file appears in `.agent-logs/` with a hypothesis in it before the first code change.
- Your PR has a Revisions section, and it reads as a list of things that went differently from the plan, or says `No revisions.`
- `git status` never shows the log.

## Where it fits

`work-log` is the record that runs alongside the build step of the main chain, written by [implement](https://aihero.dev/skills-implement) and [tdd](https://aihero.dev/skills-tdd) and read by [code-review](https://aihero.dev/skills-code-review), [pr](https://aihero.dev/skills-pr), and [retro](https://aihero.dev/skills-retro). [ask-matt](https://aihero.dev/skills-ask-matt) is the router over the whole set.
