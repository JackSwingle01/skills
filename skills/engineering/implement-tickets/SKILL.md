---
name: implement-tickets
description: Build a spec's tickets one after another in blocking order, each in a fresh subagent running implement, while this session judges the seams each one proposes.
disable-model-invocation: true
---

# Implement Tickets

You are the **dispatcher** for a set of tickets, usually the output of `/to-tickets`. Each ticket is built by its own subagent running `implement`, one at a time, blockers first. You build nothing yourself. Your jobs are the order, the branch each ticket starts from, and answering what the subagents ask, above all which seams to test at.

Start every subagent with a fresh context window. Running them one at a time is what replaces the user's `/clear` between tickets, so a subagent that inherits your context defeats the point.

Stay thin. Pass **context pointers** (the ticket reference, the spec path, the base branch), never summaries of them, and don't read code or design the work: that belongs to each subagent's `implement` run. Your window has to last the whole set.

## Steps

1. **Read the set.** Fetch the tickets from the repo's issue tracker (check `AGENTS.md`/`CLAUDE.md` for which one and its conventions): the ones the user named, or every ticket linking the spec or parent issue they passed. Read the spec they link, especially the seams it settled. Skip any ticket already closed or with a merged pull request.

2. **Order them.** Sort by blocking edges, blockers first; among tickets that are ready at the same time, keep the tracker's order. Show the user the order and the base branch each ticket will start from, then begin without waiting unless something is unclear (a cycle, a blocker outside the set that is still open).

3. **Pick the base branch** for the next ticket:
   - every blocker merged into the default branch, or no blockers: the default branch;
   - otherwise: the branch of the last ticket built in this run, which carries every earlier ticket's work. Its pull request stacks on that one.

4. **Dispatch one subagent** in the foreground and wait for it. Tell it to call the Skill tool with "implement" for the ticket reference, name the spec path, and say: start from `<base>`, open the pull request against `<base>`, report proposed seams and any other question to the parent and wait for the answer, and finish by reporting the branch, the pull request link, the work log path, and any follow-ups.

5. **Judge what it asks.** `tdd` has a subagent confirm its seams with the parent before writing a test, so the seam question comes to you. Answer by continuing that same subagent, not a new one, so it keeps its context.
   - **Seams.** Hold each proposal to the spec. Approve seams the spec names. For a seam the spec didn't name, apply the spec's rule: prefer an existing seam to a new one, the highest seam that observes the behaviour, and as few as possible. Approve it if it passes, or answer with the specific seam you'd use instead and why. Escalate to the user only when a proposal contradicts the spec.
   - **Anything else** (an ambiguous reference, a behaviour change the ticket didn't ask for): answer from the spec and the ticket. When they don't settle it, ask the user; never guess on their behalf.

   Keep a line for each judgement for the final report.

6. **Check the result.** A ticket is done when its pull request is open. If the subagent stops without one, or reports that it couldn't finish, skip every ticket that this one blocks, directly or through others, and carry on with the rest.

7. **Repeat from step 3** until no ticket is left.

8. **Report** a table with one row per ticket: its reference, base branch, pull request link (or why there is none), seam judgements, and follow-ups. Under it, list the stacked pull requests in the order they must merge, and every skipped ticket with the blocker that stopped it.
