---
"skills": minor
---

**`loose-ends`** gains a bundled `gather.py`: on GitHub it fetches the window's PRs (body, comments, reviews and review threads with author association, files changed, commits, committed work logs, glossary and decision-record diffs) and the whole tracker into one brief folder, verbatim, and exits non-zero when a fetch fails or a list comes back short. The sweep reads the brief instead of calling GitHub, and can write the ticket's title and body to paths its caller names, for the caller to file. `gather.py` defaults to `domain-modeling`'s glossary and decision-record layout and takes the repo's own paths with `--docs`. **`mechanize`** now rates a step the target's text requires on every run as high confidence from one measured run.
