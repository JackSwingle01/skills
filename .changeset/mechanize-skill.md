---
"skills": minor
---

New user-invoked **`mechanize`** skill. It audits a skill or an automated agent job for mechanical work the model does that code should do instead (fetching, copying verbatim, counting, filling a fixed template, side-effect writes), using a bundled `tally.py` that counts tool-call shapes across the job's transcripts. It places each step on a ladder (fetched before the model starts, one bundled script, a shared skill's script, or left to the model), proposes them with their measured cost, and builds the ones the user picks. **`dev-flow`** routes to it.
