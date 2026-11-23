---
"skills": minor
---

New user-invoked **`mechanize`** skill. It audits a skill or an automated agent job for mechanical work the model does that code should do instead (fetching, copying verbatim, counting, filling a fixed template, side-effect writes), using the new **`transcript-tally`** skill's counts of tool-call shapes, cost and time across the job's transcripts. It places each step on a ladder (fetched before the model starts, one bundled script, a shared skill's script, or left to the model), weighs each against the flexibility it takes from the model, rates it high or low confidence, and reports "already well mechanized" when nothing earns a move. Slow calls are reported separately, with remedies like a narrower call or deferring to CI. It builds the ones the user picks and compares the target before and after on the same scenario, by cost, tokens, calls and time, with matching results. **`dev-flow`** routes to it.
