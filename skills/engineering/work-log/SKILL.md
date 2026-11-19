---
name: work-log
description: "Keep a per-task work log of the hypothesis, revisions, and follow-ups, outside git, so review, the PR body, and retros read what actually changed and why. Use when starting a build or bug fix, when the approach changes mid-build, when a pre-existing test changes, or when a skill asks for the work log's path or format."
---

A **work log** is a record of surprises, written at the moment they happen. It is not a diary: it holds a hypothesis made before any code, and a line for each time reality disagreed with it.

## Where it lives

One file per ticket in `.agent-logs/`, named `YYYY-MM-DD-short-name.md`, dated the day the work started, with the ticket reference in the short name. Work with no ticket uses a short name for the task. The log stays out of git: if the folder isn't ignored, add it to the file `git rev-parse --git-path info/exclude` prints.

If a log for this ticket already exists, append to it rather than starting a new one.

## Format

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

Each line is a fact and an action, nothing else.

| Line | When to write it |
|---|---|
| `Hypothesis:` | Once, before any code. |
| `Revised:` | The moment something you learn changes the approach, and for every pre-existing test you change. A better solution always beats the hypothesis: change the approach, then log it. |
| `Revised (review):` | A review finding that changes the approach. |
| `Follow-up:` | Work found outside this ticket's scope, and anything you couldn't verify yourself, naming what would let an agent verify it next time: a harness, a fixture, access, or a check. |

A revision you can't phrase in glossary terms marks a glossary gap: write it in the code's words and tag it `(term)`, combining tags as `(review, term)`.

Never rewrite or delete a line once written. A later line that contradicts an earlier one is the record working.

## Readers

When another skill needs the log, pass it the path, not a summary.

- `code-review`: a divergence from the hypothesis, or a changed pre-existing test, with no matching `Revised` line is a finding.
- `pr`: copies the `Revised` lines verbatim into Revisions and the `Follow-up` lines into Follow-ups.
- `retro`: reads each revision as a surprise; a `(term)` tag is a glossary gap.
