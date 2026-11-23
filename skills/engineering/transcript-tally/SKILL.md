---
name: transcript-tally
description: "Tally agent transcripts into numbers, with one script per harness (Claude Code today): tool calls by shape, errors, repeats, time split between tools, the model and a person, stops, permission decisions and denials, tokens and cost. Use when a task needs evidence about how agent runs went, such as a retro or an audit of a skill's runs."
---

Each agent harness writes transcripts in its own format, so each has its own script beside this file, named `tally_<provider>.py`. Pick the one for the transcripts' harness and run it over one or more of them. Each file is one run:

```bash
python3 <this skill's directory>/tally_<provider>.py <transcript> [<transcript> ...]
```

| Script | Harness | Where its transcripts are |
|---|---|---|
| `tally_claude.py` | Claude Code, headless `claude -p`, `claude-code-action` | sessions: `~/.claude/projects/<project>/<session>.jsonl`, one event per line, with each subagent's log under its parent session's folder; headless: `claude -p "<prompt>" --output-format stream-json --verbose > run.jsonl`; `claude-code-action`: the step's `execution_file` output, one JSON array, kept only if the workflow uploads it as an artifact |

**One script per provider, and one provider per run.** A script reads its own harness's format and no other, so a change for one harness never breaks another. Tally each harness's transcripts with its own script, never several harnesses in one call.

**A harness with no script** (Cursor, Codex, ...) gets a new `tally_<provider>.py` beside the others, added to the table above. It prints the same sections and columns, below, so the skills that read a tally never need to know the harness. A field its transcripts don't record (a permission decision, a cost) is left blank, and the script says so in its docstring, rather than guessed.

## What it prints

**Runs**, one row each, then the mean:

| Column | Meaning |
|---|---|
| Calls, Errors | tool calls, and those whose result was an error |
| Repeats | calls identical to an earlier call in the same run |
| Active s | the run's length, without the gaps spent waiting on a person; a run's own `duration_ms` when it records one |
| Tool s | time waiting on tool calls, overlapping parallel calls counted once |
| Model s | active time less tool time: the model reading and writing |
| Human s, Stops | time spent waiting on a person, and the prompts after the first: each is a point where the agent stopped |
| Permissions | who decided each call: `rule`, `classifier` (auto mode), `mode`, or `other` |
| Tokens, Cost | input (cached reads included) and output tokens; cost when the run records it |

**Denials**: each call a permission check rejected, with its shape and reason.

**Call shapes**: each shape (the tool, plus the program and subcommand for shell calls) with the runs it appears in, its calls, errors, result size, total wait, and longest wait.

## Reading it

- A call that waited on a person's approval counts that wait as tool time: transcripts record when a call started and when its result came back, not when it was approved. In a session with many approvals, read long tool waits with that in mind.
- Human time measures the person's schedule as much as the agent: count stops and read what each one asked, rather than weighing the seconds.
- Compare runs of the same task. Across unrelated sessions, a shape appearing in every run means little.
