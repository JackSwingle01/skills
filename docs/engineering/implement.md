## What it does

`implement` builds work that has already been decided. You point it at a [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket), a [spec](https://www.aihero.dev/ai-coding-dictionary/spec), or the plan you just agreed in the conversation, and it scouts the change, designs it to fit the existing system, writes the code test-first with [tdd](https://aihero.dev/skills-tdd), validates the acceptance criteria end to end, runs [code-review](https://aihero.dev/skills-code-review), and opens a pull request.

It never reopens the plan. There is no interview and no clarifying round: whatever was settled upstream is the input. The design phase decides how to build it, not what to build, and it flags any change to existing behaviour that the ticket didn't ask for. That is what separates it from typing "build this" at a fresh [agent](https://www.aihero.dev/ai-coding-dictionary/agent), which often redesigns the work while it builds it.

## When to reach for it

You invoke this by typing `/implement` yourself, and the agent won't reach for it on its own. It ships with `disable-model-invocation: true`, so no other skill can call it either. Wherever [ask-matt](https://aihero.dev/skills-ask-matt) or [to-tickets](https://aihero.dev/skills-to-tickets) says "then `/implement` per ticket", that is an instruction to you, not something the agent will do unprompted.

Where the work currently lives decides whether this is the right skill:

| The work is… | Reach for |
| --- | --- |
| A ticket on the tracker | `/implement #42`, one ticket per [session](https://www.aihero.dev/ai-coding-dictionary/session), [clearing](https://www.aihero.dev/ai-coding-dictionary/clearing) context between tickets |
| A spec, not yet split up, and the build spans sessions | [to-tickets](https://aihero.dev/skills-to-tickets) first, then `/implement` per ticket |
| A spec, and the build is small | `/implement` directly against the spec |
| Only in the conversation you just had, and it's still small | `/implement` right there, in the same window |
| Not written down anywhere yet | [grill-with-docs](https://aihero.dev/skills-grill-with-docs), or [grill-me](https://aihero.dev/skills-grill-me) if there's no codebase |
| One concrete behaviour you want test-first, with no spec | [tdd](https://aihero.dev/skills-tdd) directly |
| Already built, and you want it checked | [code-review](https://aihero.dev/skills-code-review) directly |

The same-session case is worth naming because the skill's own first line doesn't cover it. `SKILL.md` says "the spec or tickets", which pushes the [model](https://www.aihero.dev/ai-coding-dictionary/model) to look for a file that doesn't exist. If the plan lives only in the thread, say so when you invoke it.

## Prerequisites

`implement` follows the repo's branch conventions. Where there are none, it commits to the branch you are on without asking, so check that branch before you start.

If the tickets came from [to-tickets](https://aihero.dev/skills-to-tickets), [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) configured the tracker they live on. `code-review` reads the same configuration to find the originating spec at close-out.

## What one run does

A run has these steps, in order:

1. Read the ticket or spec and start the work log.
2. Design:
   - **a. Scout.** Start a [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent) with a fresh context window to scout the change: its blast radius, test coverage, and existing patterns, how it can be validated locally, and the existing behavior it affects, grounded in real usage where logs or data allow.
   - **b. Design.** Call [codebase-design](https://aihero.dev/skills-codebase-design) and design the change to fit the existing system, not to sit on top of it. Decide for each affected behavior whether it stays, changes, or goes, and flag any change the ticket didn't ask for. Then design in two steps: decomposition (break the work into stages) and encapsulation (pick the right abstraction for each stage at every level, from modules down to functions and data structures, so each stage can be verified on its own).
   - **c. Review.** Start a subagent with a fresh context window for an adversarial design review against the ticket and the scout's report. Weigh each finding on its merits rather than accepting it, and log each change made as a Revised line.
3. Drive [tdd](https://aihero.dev/skills-tdd) at the pre-agreed seams, one red-green slice at a time. If the spec names seams, it uses them unless there is a good reason not to, and logs any seam it adds or changes as a Revised line.
4. Typecheck often, run single test files as it goes.
5. Run the full test suite once, at the end.
6. Validate each acceptance criterion end to end, logging any it couldn't validate as a follow-up.
7. Commit to the current branch.
8. Run [code-review](https://aihero.dev/skills-code-review) against the branch's base, passing it the work log and treating decisions made during the work as context to challenge, not spec. Commit its fixes separately.
9. Open the pull request with [pr](https://aihero.dev/skills-pr).

One run covers one ticket. The tickets [to-tickets](https://aihero.dev/skills-to-tickets) produces are tracer-bullet vertical slices sized to fit a single fresh [context window](https://www.aihero.dev/ai-coding-dictionary/context-window), so the intended rhythm is: clear context, implement one ticket, commit, clear again. Each ticket is self-contained, so you can discard the previous ticket's context.

## Pre-agreed seams

The skill's central idea is the **seam**, the public boundary you observe behaviour at without reaching inside. Tests live at seams. When the seam is agreed before any code exists, the tests last, and you can rewrite the implementation underneath without changing them.

The "pre-agreed" part matters, and it is also the skill's weakest point. Nothing inside `implement` agrees the seams. `tdd` is the skill that asks, and it refuses to write a test at an unconfirmed seam. So in practice the agreement happens either upstream in the spec, or in the first exchange of the run. If it happens nowhere, the run becomes "just write the code" and nothing warns you. Naming the seams in the spec is what stops that.

## Common questions

**It finished, but my ticket is still open and the acceptance criteria are still unchecked.**

Correct, and expected. `implement` has no completion step. It ends at the commit and never touches the work item. This is the same on GitHub Issues and on the local markdown tracker, so it is not a tracker integration problem. It also does not act on the findings `code-review` produced, and does not tick the `- [ ]` boxes on the originating issue. Close the ticket and reconcile the criteria yourself. This matters most on a dependency chain, because `to-tickets` defines the frontier as tickets whose blockers are all closed. If nothing gets closed, nothing ever becomes visibly unblocked.

**Can I point it at all my tickets at once, or run several in parallel?**

Not with `/implement`: one invocation, one ticket. For a whole spec in one run, use [implement-spec](https://aihero.dev/skills-implement-spec), which gives each ticket on the ready frontier to a [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent) in its own worktree, then merges the results onto one integration branch. Running several `/implement` sessions side by side in one checkout is worse than unsupported. One field report describes a `git commit --amend` in one session landing on another session's commit, a stash vanishing from `refs/stash`, and commits landing on the wrong branch, all in a single afternoon across three issues. The sessions share one working directory, one index, and one HEAD. Users work around this with git worktrees, but `refs/stash` is shared across worktrees too, so worktrees alone do not fix the stash case.

**Does it open a pull request, or just commit?**

Both. It commits the implementation, commits the review's fixes separately, then calls [pr](https://aihero.dev/skills-pr) and opens the pull request in the same session, with the work log's revisions and follow-ups in the body. The split commits are deliberate: across runs, the share of tickets that needed a review commit measures how well the build and the review are each doing.

**`code-review` says it cannot see my changes.**

`code-review` reviews `git diff <fixed-point>...HEAD`, which excludes staged and working-tree changes. `implement` now commits before it reviews, so this should no longer happen inside a run. If you run `code-review` yourself, commit first, then review against the point you branched from.

Separately, some people do not want the review inside the run at all, because an agent reviewing the code it just wrote is biased toward its own solution. Running [code-review](https://aihero.dev/skills-code-review) in a fresh session against a fixed point is a valid alternative. The same bias is why that skill runs its two axes in separate sub-agents.

**One ticket burned 150k tokens. Am I using it wrong?**

Probably not. The ticket is more likely too big. A run does codebase exploration, a red-green loop per seam, a full suite, and a review, so a non-trivial ticket exceeding 100k [tokens](https://www.aihero.dev/ai-coding-dictionary/token) is normal rather than a sign something broke. The fix is upstream. Right-size the tickets in [to-tickets](https://aihero.dev/skills-to-tickets) so each fits one fresh window. If a single ticket keeps going over, split it rather than raising the [effort](https://www.aihero.dev/ai-coding-dictionary/effort) level.

**`/implement #2` in a fresh session worked on something completely unrelated.**

The agent resolved `#2` against another numbered list in context, such as a todo file or checklist, rather than the configured tracker. `implement` now fetches a passed reference from the issue tracker and states its title before starting, and asks when the reference is ambiguous. Check that title matches the ticket you meant; passing the issue URL or `owner/repo#2` removes the ambiguity entirely.

## It's working if

- The session opens by reading the ticket or spec and restating what it will build, rather than asking you what to build.
- Two fresh subagents appear in the trace before any code: one scouting the change, one reviewing the design.
- The work log's hypothesis has an `Affects:` line naming existing behaviour, and design-review changes show up as `Revised` lines.
- You can see an actual `tdd` Skill tool call in the trace, not just tests appearing in the diff.
- Typechecks and single test files run repeatedly during the run, and the full suite runs once near the end.
- Every acceptance criterion is either validated end to end or listed as a follow-up with what was missing.
- The run reaches an open pull request without you prompting it to carry on.
- The diff is one ticket's worth of change: a vertical slice through every layer, not several tickets swept together.

## Where it fits

`implement` is the build step of the main chain:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

Its neighbours are [to-tickets](https://aihero.dev/skills-to-tickets), which produces the tickets it consumes and declares the blocking edges that decide their order; [tdd](https://aihero.dev/skills-tdd), which it drives internally at each seam; and [code-review](https://aihero.dev/skills-code-review), which it runs before committing. It sits downstream of the planning skills and trusts them. It does not re-validate the shape of what it was handed, so a badly-structured map or a horizontally-layered ticket gets built as written.

That trust is why [wayfinder](https://aihero.dev/skills-wayfinder) merges onto the chain at [to-spec](https://aihero.dev/skills-to-spec) rather than looping its map straight into `implement`. Go straight to `implement` from a map only when the effort turned out small.

[ask-matt](https://aihero.dev/skills-ask-matt) is the router over the whole set when you are not sure which flow you are in.
