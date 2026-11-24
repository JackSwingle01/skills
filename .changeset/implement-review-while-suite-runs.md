---
"skills": minor
---

**`implement`** starts the full suite and the other pre-PR checks in the background after the implementation commit and runs `code-review` without waiting for them, so the reviewers and the suite overlap. A failed check gets a fix commit of its own, apart from the review's fixes.
