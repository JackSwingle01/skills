---
"mattpocock-skills": minor
---

**`implement`** gains a design phase before code. A fresh subagent scouts the change (blast radius, coverage, patterns, local validation, and the existing behaviour it affects), the design is shaped with `codebase-design` to fit the existing system, and a second fresh subagent reviews it adversarially. After the tests pass, each acceptance criterion is validated end to end. `code-review` now treats decisions made during the work as context to challenge, not spec. **`work-log`**'s hypothesis gains an `Affects:` line for the behaviour the scout finds.
