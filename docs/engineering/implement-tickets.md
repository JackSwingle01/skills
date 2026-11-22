## What it does

`implement-tickets` builds a whole set of tickets from one command and lands them as **GitHub stacks**. It reads the tickets and their spec, cuts the blocking graph into stacks, and hands each ticket to a fresh subagent that runs [implement](../../skills/engineering/implement/SKILL.md) end to end (scout, design, test-first build, review, pull request) in its own git worktree. Independent stacks build in parallel. When a subagent proposes the seams it wants to test at, the dispatching session judges them against the spec and answers, so you aren't asked for each ticket.

The dispatcher builds nothing itself. Every ticket gets exactly the run `/implement` would give it in a session of its own. The dispatcher decides the stacks, sets up the worktrees, links each finished pull request into its stack with `gh stack`, and answers the subagents' questions.

## When to reach for it

You invoke this by typing `/implement-tickets` with a spec path, a parent issue, or a list of tickets, and the agent won't reach for it on its own.

| Your situation | Reach for |
| --- | --- |
| A set of tickets with blocking edges, and you want them all built without dispatching each yourself | `/implement-tickets` |
| One ticket, or you want to watch and steer each ticket's run | [implement](../../skills/engineering/implement/SKILL.md), one session per ticket |
| A spec that isn't split into tickets yet | [to-tickets](../../skills/engineering/to-tickets/SKILL.md) first |

## Prerequisites

- **The `gh stack` extension** and a GitHub repo with stacked pull requests. Without the extension, the dispatcher asks whether to install it or fall back to plain stacked pull requests.
- **Tickets on the tracker your `AGENTS.md`/`CLAUDE.md` documents**, with blocking edges, as [to-tickets](../../skills/engineering/to-tickets/SKILL.md) writes them.
- **Setup steps the repo documents.** Each worktree is a fresh checkout, so the dispatcher runs the repo's setup in it and copies in untracked files the checks need. Setup that lives only in your head doesn't reach the worktrees.
- **A spec that names its seams.** The dispatcher judges each proposed seam against the spec. With no seams in the spec it falls back on the spec rule (an existing seam over a new one, the highest one possible, as few as possible), which is weaker.
- **A harness whose subagents run in the background, call skills, and start subagents of their own**, because each `implement` run starts a scout and a design reviewer.

## One stack per connected group

A GitHub stack is a chain, so the dispatcher gives each connected group of tickets one stack and builds it bottom to top, while unconnected groups build in parallel. The cost shows up in a diamond: two siblings blocked by the same ticket could run side by side, but in one chain they run in turn.

## The dispatcher and the seams

The key idea is the **dispatcher**: one session that holds the plan and the spec, and nothing else. It passes each subagent context pointers (the ticket, the spec path, the worktree, the base branch), not summaries, and reads no code. Its own context window lasts the whole set while each ticket's heavy context is thrown away with its subagent.

[tdd](../../skills/engineering/tdd/SKILL.md) never writes a test at an unconfirmed **seam**. In a subagent, it confirms with the parent instead of with you. That puts the dispatcher where you would sit in a hand-run `/implement`. It approves seams the spec named, pushes back with a concrete alternative on ones that are lower or more numerous than needed, and escalates to you only when a proposal contradicts the spec. Every judgement goes into the final report, so you can check what was decided on your behalf.

## Common questions

**How is this different from running `/implement` on each ticket myself?**

With `/implement` you are the dispatcher: one session per ticket, `/clear` in between, keeping track of which tickets are unblocked, retargeting pull request bases, and answering each run's seam question yourself. `implement-tickets` gives that job to one session and runs independent work at the same time. Each ticket's build is identical. The cost is that you no longer watch each run as it happens; you read the stacks and the judgement log at the end instead.

**Two parallel stacks conflict when the second one merges.**

Worktrees keep parallel runs apart while they build, which moves any collision to merge time rather than removing it. Tickets with no blocking edge between them can still touch the same config registry, message catalogue, or shared type, and neither implementer sees the other's work. If two stacks are likely to touch one shared file, add a blocking edge between them in the tracker so they land in one stack and build in order.

**A ticket failed. Did the run stop?**

Only for the rest of that ticket's stack. The other stacks carry on, and the failed ticket's worktree is kept so you can inspect it.

## It's working if

- The run opens by showing the stacks and their order, then starts without asking you to confirm what was already decided.
- Unrelated stacks have subagents running at the same time; inside a stack, a ticket starts as soon as the one below has its pull request open.
- Each ticket's trace shows a fresh subagent calling `implement` in its own worktree, not the dispatcher reading code or writing tests itself.
- Seam questions are answered by the dispatcher and reach you only when a proposal contradicts the spec.
- On GitHub, each stack's pull requests appear linked as one stack, each based on the one below.

## Where it fits

`implement-tickets` is the build step of the main chain, as the one-command alternative to running [implement](../../skills/engineering/implement/SKILL.md) once per ticket:

```txt
grill-with-docs → to-spec → to-tickets → implement-tickets → retro
```

Upstream is [to-tickets](../../skills/engineering/to-tickets/SKILL.md), whose blocking edges decide the stacks; underneath is [implement](../../skills/engineering/implement/SKILL.md), which does every ticket's actual work, unchanged. [dev-flow](../../skills/engineering/dev-flow/SKILL.md) is the router over the whole set when you are not sure which flow you are in.
