---
name: implement-tickets
description: Build a spec's tickets as GitHub stacks, each ticket in a fresh subagent running implement in its own worktree, independent stacks in parallel, while this session judges the seams each one proposes.
disable-model-invocation: true
---

# Implement Tickets

You are the **dispatcher** for a set of tickets, usually the output of `/to-tickets`. Each ticket is built by its own subagent running `implement` in its own git worktree, and the pull requests land as GitHub stacks. You build nothing yourself: you plan the stacks, set up the worktrees, and answer what the subagents ask, above all which seams to test at.

Start every subagent with a fresh context window. Pass **context pointers** (the ticket reference, the spec path, the worktree, the base branch), never summaries, and don't read code or design the work. Your window has to last the whole set.

If `gh stack` isn't installed, ask the user whether to install it (`gh extension install github/gh-stack`) or open plain stacked pull requests instead.

## Steps

1. **Read the set.** Fetch the tickets from the repo's issue tracker (check `AGENTS.md`/`CLAUDE.md`): the ones the user named, or every ticket linking the spec or parent issue they passed. Read the spec, especially the seams it settled. Skip tickets already closed or merged.

2. **Plan the stacks.** A stack is a chain, so give each connected group of unmerged tickets one stack, blockers first, tracker order otherwise. Unconnected groups are separate stacks. Show the user the plan, then begin without waiting unless something is unclear.

3. **Dispatch every ready ticket**: the next unbuilt ticket of each stack, once the one below it has an open pull request. For each:
   - create a worktree on a new branch, named by the repo's conventions, from its base: the default branch at the bottom of a stack, else the branch below. Run the repo's setup in it and copy in any untracked files its checks need;
   - start a background subagent that calls the Skill tool with "implement" for the ticket, given the spec path, the worktree, and the base to open the pull request against. Tell it to report proposed seams and other questions to you and wait, and to finish with the pull request link, work log path, and follow-ups.

4. **Judge what they ask**, answering by continuing the same subagent so it keeps its context.
   - **Seams.** Approve seams the spec names. For any other, prefer an existing seam, the highest one that observes the behaviour, and as few as possible; approve it, or answer with the seam you'd use instead and why. Escalate to the user only when a proposal contradicts the spec.
   - **Anything else**: answer from the spec and the ticket, and ask the user when they don't settle it.

   Log each judgement for the report.

5. **Stack each finished ticket** with `gh stack link --base <default-branch>` and its stack's branches so far, bottom to top. Only you run `gh stack`. If a subagent ends without a pull request, stop that stack and carry on with the others.

6. **Clean up** each finished stack's worktrees; keep a failed ticket's worktree for the user.

7. **Report** each stack bottom to top: ticket, pull request (or why none), seam judgements, follow-ups, and any tickets left unbuilt with what stopped them.
