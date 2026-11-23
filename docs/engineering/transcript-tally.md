## What it does

`transcript-tally` turns agent transcripts into numbers: tool calls grouped by shape, errors, repeated calls, where the time went (tools, the model, waiting on a person), the stops where the agent waited on you, who approved each call and what was denied, tokens, and cost. Each harness writes transcripts in its own format, so each gets its own script. `tally_claude.py` reads Claude Code session logs, headless `claude -p` output, and the execution files `claude-code-action` writes. Cursor, Codex or any other harness gets a `tally_<provider>.py` of its own, printing the same columns, rather than one script that parses every format.

It counts and never judges. A long tool wait, a stop or a denial is a place to look, and the skill that called it decides what that place means.

## When to reach for it

Type `/transcript-tally`, or the agent reaches for it automatically when a task needs evidence about how agent runs went. [retro](../../skills/engineering/retro/SKILL.md) and [mechanize](../../skills/engineering/mechanize/SKILL.md) both call it; reach for it directly to compare two versions of a skill on the same task.

## Common questions

**Why does a run that waited on my approvals look slow on tools?**

A transcript records when a call started and when its result came back, not when it was approved, so the wait for your approval lands in the call's tool time. Read long tool waits in an interactive session with that in mind.

**Why count stops rather than the time I took to answer?**

Your time measures your schedule as much as the agent. The number of stops, and what each one asked, is what says whether the agent could have carried on without you.

## It's working if

- A slow step, a repeated call or a recurring denial shows up as a number you can point at, not an impression.
- Two versions of a skill run on the same task can be compared by calls, time and cost.

## Where it fits

Shared measurement under [retro](../../skills/engineering/retro/SKILL.md) (one session, the agent's environment) and [mechanize](../../skills/engineering/mechanize/SKILL.md) (many runs of one job, the split between the model and code). [dev-flow](../../skills/engineering/dev-flow/SKILL.md) maps the whole set.
