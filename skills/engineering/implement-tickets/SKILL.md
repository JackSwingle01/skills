---
name: implement-tickets
description: Build a spec's tickets as GitHub stacks, each ticket in a fresh subagent running implement in its own worktree, independent stacks in parallel, while this session judges the seams each one proposes.
disable-model-invocation: true
---

# Implement Tickets

You are the **dispatcher** for a set of tickets, usually the output of `/to-tickets`. Each ticket is built by its own subagent running `implement` in its own git worktree, and the pull requests are chained into **GitHub stacks** with the `gh stack` extension. You build nothing yourself. Your jobs are the plan, the worktrees, the stacks, and answering what the subagents ask, above all which seams to test at.

Start every subagent with a fresh context window. A subagent that inherits your context carries every other ticket with it, which is what it was meant to escape.

Stay thin. Pass **context pointers** (the ticket reference, the spec path, the worktree, the base branch), never summaries of them, and don't read code or design the work: that belongs to each subagent's `implement` run. Your window has to last the whole set.

## Stacks

A GitHub stack is a **linear chain**: each pull request is based on the one below it, and the bottom one on the default branch. It can't fork into a tree, so the blocking graph has to be cut into chains:

- **One stack per connected group.** Ignoring blockers that have already merged, tickets joined by blocking edges, directly or through others, form one stack, ordered blockers first; among tickets with no edge between them, keep the tracker's order. Every ticket's unmerged blockers are then below it in its own stack.
- **Stacks run in parallel; tickets inside a stack run one at a time.** A ticket starts once the ticket below it has its pull request open. Two tickets in one stack that don't block each other still wait for each other, because there is only one top to build on.

You are the only one who runs `gh stack`. Subagents commit, push, and open their pull request like any `implement` run; you then link it into its stack.

## Steps

1. **Check the tool.** Run `gh stack --help`. If it is missing, tell the user it installs with `gh extension install github/gh-stack` (it needs `gh` 2.0+ and Git 2.36+), and ask whether to install it or carry on with plain stacked pull requests and no GitHub stack.

2. **Read the set.** Fetch the tickets from the repo's issue tracker (check `AGENTS.md`/`CLAUDE.md` for which one and its conventions): the ones the user named, or every ticket linking the spec or parent issue they passed. Read the spec they link, especially the seams it settled. Skip any ticket already closed or with a merged pull request.

3. **Plan the stacks** as above. Show the user each stack's tickets in order, then begin without waiting unless something is unclear (a cycle, a blocker outside the set that is still open).

4. **Dispatch every ready ticket**: the bottom ticket of each stack, then, as each one finishes, the next ticket up. For each:
   - **Base**: the default branch for a stack's bottom ticket, else the branch of the ticket below it.
   - **Worktree**: create one on a new branch from the base, named by the repo's branch conventions (`git worktree add -b <branch> <path> <base>`), and run the repo's documented setup in it (dependencies, generated files). A worktree holds only what git tracks, so copy in any untracked file the repo's checks need, such as a local env file, and tell the subagent which ones you copied.
   - **Subagent**: run it in the background. Tell it to call the Skill tool with "implement" for the ticket reference, name the spec path, and say: work in `<path>` on the branch checked out there, open the pull request against `<base>`, report proposed seams and any other question to the parent and wait for the answer, and finish by reporting the pull request link, the work log path, and any follow-ups.

5. **Judge what they ask.** `tdd` has a subagent confirm its seams with the parent before writing a test, so the seam question comes to you. Answer by continuing that same subagent, not a new one, so it keeps its context.
   - **Seams.** Hold each proposal to the spec. Approve seams the spec names. For a seam the spec didn't name, apply the spec's rule: prefer an existing seam to a new one, the highest seam that observes the behaviour, and as few as possible. Approve it if it passes, or answer with the specific seam you'd use instead and why. Escalate to the user only when a proposal contradicts the spec.
   - **Anything else** (an ambiguous reference, a behaviour change the ticket didn't ask for): answer from the spec and the ticket. When they don't settle it, ask the user; never guess on their behalf.

   Keep a line for each judgement for the final report.

6. **Link each finished ticket.** A ticket is done when its pull request is open. Run `gh stack link --base <default-branch> <branch> ...` with every branch of its stack built so far, bottom to top. It reuses the open pull requests, corrects any wrong base, and creates or extends the stack on GitHub. Then dispatch the next ticket up that stack.

   If a subagent stops without a pull request, or reports that it couldn't finish, the rest of its stack stays unbuilt: nothing can sit on a missing layer. Carry on with the other stacks.

7. **Repeat** until every stack is built or stopped.

8. **Clean up** each worktree once its stack is finished (`git worktree remove <path>`). Keep a failed ticket's worktree and name it in the report so the user can inspect it.

9. **Report** each stack as a table, bottom to top: the ticket reference, the pull request link (or why there is none), its seam judgements, and follow-ups. Under each stack, list the tickets left unbuilt and the ticket that stopped them. End with how to land and maintain the stacks: `gh stack merge` merges a stack, or the stack up to one pull request, all or nothing, and review changes to a lower layer are cascaded upward with `gh stack checkout <pr>` then `gh stack sync`.
