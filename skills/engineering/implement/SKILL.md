---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask. If the ticket links a spec, read it.

If the repo requires a ticket for every change (check `AGENTS.md`/`CLAUDE.md`) and there isn't one yet, create it first using the repo's conventions. Follow the repo's branch conventions too.

Before writing code, call the Skill tool with "codebase-design" for the vocabulary of modules, interfaces, depth, and seams.

## Steps

1. **Hypothesis.** Call the Skill tool with "work-log", start this ticket's log, and write the hypothesis to it before any code.

2. **Build.** Call the Skill tool with "tdd" where possible, at pre-agreed seams. Use whatever lint, typecheck, and test commands the repo has. Run typechecking and single test files regularly, and the full test suite once at the end.

   When you learn something that changes the approach, change it, and log a **revision** at that moment. Every pre-existing test you change gets a revision too, and anything you can't verify yourself gets a follow-up.

   A change to what the ticket or spec promises (a public interface, the scope, or a DR) is the user's decision; every other choice is yours. Bring the facts you found, the options, and your recommendation, worded so "yes" accepts it, and keep building any slice that doesn't depend on the answer. If the user is AFK and the choice is reversible, take your recommendation, log it as a revision, and continue.

3. **Commit** your work to the current branch, following the repo's commit conventions.

4. **Review.** Call the Skill tool with "code-review", with the branch's base as the fixed point, passing it the work log's path. Commit the fixes separately. Any review finding that changes the approach gets a `Revised (review):` line.

5. **Pull request.** Call the Skill tool with "pr" to write the body, passing it the work log's path, and open the pull request using the repo's conventions. Open it in this session: the PR needs this session as a primary source.
