---
"skills": minor
---

New user-invoked **`implement-tickets`** skill, bringing back `implement-spec` in the shape the current flow needs. It orders a spec's tickets by their blocking edges and hands each, one at a time, to a fresh subagent running **`implement`** unchanged, then judges the seams each subagent proposes against the spec. Ticket branches stack when blockers haven't merged, and the run ends with a report of pull requests in merge order, seam judgements, and skipped tickets. **`dev-flow`** routes to it as the one-command way to build a set of tickets.
