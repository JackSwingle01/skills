---
"skills": minor
---

New user-invoked **`implement-tickets`** skill, bringing back `implement-spec` in the shape the current flow needs. It cuts a spec's blocking graph into GitHub stacks (one per connected group of tickets) and hands each ticket to a fresh subagent running **`implement`** unchanged, in its own git worktree. Independent stacks build in parallel, tickets inside a stack build bottom to top, and the dispatcher links each finished pull request into its stack with `gh stack link`. It judges the seams each subagent proposes against the spec. **`dev-flow`** routes to it as the one-command way to build a set of tickets.
