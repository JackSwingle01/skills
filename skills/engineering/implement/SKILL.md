---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask. If the ticket links a spec, read it.

If the repo requires a ticket for every change (check `AGENTS.md`/`CLAUDE.md`) and there isn't one yet, create it first using the repo's conventions. Follow the repo's branch conventions too.

Before writing code, call the Skill tool with "codebase-design" for the vocabulary of modules, interfaces, depth, and seams.

## Work log

Keep a **work log**: one file per ticket in `.agent-logs/`, named `YYYY-MM-DD-short-name.md`, dated the day the work started, with the ticket reference in the short name. The log stays out of git: if the folder isn't ignored, add it to the file `git rev-parse --git-path info/exclude` prints.

The log holds only these lines, appended as they happen, in `GLOSSARY.md` terms:

```text
# <ticket reference>: <title>

Hypothesis:
- Changes: <modules>
- Stays green: <tests or suites>
- First red: <test> fails on <symptom>

Revised: <what you found> → <what you did>
Revised (review): <what you found> → <what you did>
Follow-up: <work found outside this ticket's scope>
```

Each line is a fact and an action, nothing else. A revision you can't phrase in glossary terms marks a glossary gap: write it in the code's words and tag it `(term)`, combining tags as `(review, term)`.

## Steps

1. **Hypothesis.** Write it to the log before any code.

2. **Build.** Call the Skill tool with "tdd" where possible, at pre-agreed seams. Use whatever lint, typecheck, and test commands the repo has. Run typechecking and single test files regularly, and the full test suite once at the end.

   When you learn something that changes the approach, change it, and log a **revision** at that moment. A better solution always beats the hypothesis. Every pre-existing test you change gets a revision too.

   Anything you can't verify yourself gets a follow-up naming what would let an agent verify it next time: a harness, a fixture, access, or a check.

   A change to what the ticket or spec promises (a public interface, the scope, or a DR) is the user's decision; every other choice is yours. Bring the facts you found, the options, and your recommendation, worded so "yes" accepts it, and keep building any slice that doesn't depend on the answer. If the user is AFK and the choice is reversible, take your recommendation, log it as a revision, and continue.

3. **Commit** your work to the current branch, following the repo's commit conventions.

4. **Review.** Call the Skill tool with "code-review", with the branch's base as the fixed point, passing it the work log's path. Commit the fixes separately. Any review finding that changes the approach gets a `Revised (review):` line.

5. **Pull request.** Call the Skill tool with "pr" to write the body, passing it the work log's path, and open the pull request using the repo's conventions. Open it in this session: the PR needs this session as a primary source.
