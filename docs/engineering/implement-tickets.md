## What it does

`implement-tickets` builds a whole set of tickets from one command. It reads the tickets and their spec, orders them by their blocking edges, and hands each one in turn to a fresh subagent that runs [implement](../../skills/engineering/implement/SKILL.md) end to end: scout, design, test-first build, review, pull request. When a subagent proposes the seams it wants to test at, the dispatching session judges them against the spec and answers, so you aren't asked for each ticket.

The dispatcher builds nothing itself. Every ticket gets exactly the run `/implement` would give it in a session of its own, and the dispatcher only decides the order, the branch each ticket starts from, and the answers to the subagents' questions. Tickets run one after another, never in parallel, so they never collide in the working tree or at merge time.

## When to reach for it

You invoke this by typing `/implement-tickets` with a spec path, a parent issue, or a list of tickets, and the agent won't reach for it on its own.

| Your situation | Reach for |
| --- | --- |
| A set of tickets with blocking edges, and you want them all built without dispatching each yourself | `/implement-tickets` |
| One ticket, or you want to watch and steer each ticket's run | [implement](../../skills/engineering/implement/SKILL.md), one session per ticket |
| A spec that isn't split into tickets yet | [to-tickets](../../skills/engineering/to-tickets/SKILL.md) first |

## Prerequisites

- **Tickets on the tracker your `AGENTS.md`/`CLAUDE.md` documents**, with blocking edges, as [to-tickets](../../skills/engineering/to-tickets/SKILL.md) writes them.
- **A spec that names its seams.** The dispatcher judges each proposed seam against the spec. With no seams in the spec it falls back on the spec rule (an existing seam over a new one, the highest one possible, as few as possible), which is weaker.
- **A harness whose subagents can call skills and start subagents of their own**, because each `implement` run starts a scout and a design reviewer.

## The dispatcher and the seams

The key idea is the **dispatcher**: one session that holds the order and the spec, and nothing else. It passes each subagent context pointers (the ticket, the spec path, the base branch), not summaries, and reads no code, so its own context window lasts the whole set while each ticket's heavy context is thrown away with its subagent.

[tdd](../../skills/engineering/tdd/SKILL.md) never writes a test at an unconfirmed **seam**. In a subagent, it confirms with the parent instead of with you. That puts the dispatcher where you would sit in a hand-run `/implement`. It approves seams the spec named, pushes back with a concrete alternative on ones that are lower or more numerous than needed, and escalates to you only when a proposal contradicts the spec. Every judgement goes into the final report, so you can check what was decided on your behalf.

## Common questions

**How is this different from running `/implement` on each ticket myself?**

With `/implement` you are the dispatcher: one session per ticket, `/clear` in between, keeping track of which tickets are unblocked and answering each run's seam question yourself. `implement-tickets` gives that job to one session. Each ticket's build is identical, and the cost is that you no longer watch each run as it happens. You read the pull requests and the judgement log at the end instead.

**Why not run the tickets in parallel?**

Parallel runs collide. Two tickets described as touching "different parts of the codebase" still share a config registry, a message catalogue, or a type, and two implementers who can't see each other's work pick different names for the same thing. Running in order means each ticket starts from the code its blockers actually produced.

**My pull requests are stacked. Which do I merge first?**

A ticket whose blockers have all merged starts from the default branch. One that still has unmerged blockers starts from the branch of the last ticket built in the run, and its pull request targets that branch. The final report lists the stacked pull requests in merge order. Merge them in that order, retargeting each to the default branch as its base merges, if your host doesn't do that for you.

**A ticket failed. Did the run stop?**

Only for the tickets that depend on it. The dispatcher skips every ticket the failed one blocks, directly or through others, builds the rest, and names each skipped ticket and its blocker in the report.

## It's working if

- The run opens by showing the ticket order and each ticket's base branch, then starts without asking you to confirm what was already decided.
- Each ticket's trace shows a fresh subagent calling `implement`, not the dispatcher reading code or writing tests itself.
- Seam questions are answered by the dispatcher and reach you only when a proposal contradicts the spec.
- Every built ticket ends with an open pull request, and the report lists the judgements made for each one.

## Where it fits

`implement-tickets` is the build step of the main chain, as the one-command alternative to running [implement](../../skills/engineering/implement/SKILL.md) once per ticket:

```txt
grill-with-docs → to-spec → to-tickets → implement-tickets → retro
```

Upstream is [to-tickets](../../skills/engineering/to-tickets/SKILL.md), which declares the blocking edges it orders by; underneath is [implement](../../skills/engineering/implement/SKILL.md), which does every ticket's actual work, unchanged. [dev-flow](../../skills/engineering/dev-flow/SKILL.md) is the router over the whole set when you are not sure which flow you are in.
