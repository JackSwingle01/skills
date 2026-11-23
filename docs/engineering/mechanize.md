## What it does

`mechanize` audits a skill, or an automated job that runs one, for **mechanical** work: the steps the model does the same way every run, such as fetching what the next step needs, copying lines verbatim, counting, or filling a fixed template. It proposes moving each one into code, so the model spends its tokens only on judgment and writing.

It measures before it proposes. A bundled script tallies the tool calls across several transcripts of the same job, and a call that appears in every run with only its arguments changing is the strongest evidence a step is mechanical. Without transcripts it still reads the skill's text, but marks every candidate unconfirmed.

## When to reach for it

You invoke this by typing `/mechanize`, and the agent won't reach for it on its own.

Reach for it when a skill tells the model to run a list of commands, when an unattended job is slow or expensive for what it decides, or when two skills fetch the same thing. For a single session that went badly, use [retro](../../skills/engineering/retro/SKILL.md) instead: it reads one session and improves the agent's environment, where `mechanize` reads many runs of one job.

## The ladder

Each mechanical step goes on the highest rung it fits:

| Rung | Where the work runs | Use when |
|---|---|---|
| 1. Nothing to run | the caller fetches it before the model starts: a workflow step writing a brief, a session-start hook, a `` !`command` `` line in a Claude Code skill | the model always needs it |
| 2. One bundled script | beside the `SKILL.md`, run once by the model | what to fetch depends on a decision made mid-run |
| 3. A shared skill's script | a model-invoked skill that owns the fetch, called through the Skill tool | a second skill needs the same fetch |
| 4. The model | the model's own tool calls | choosing what to look at next is the judgment |

The scripts it builds fetch text verbatim and interpret none of it: a PR body is copied whole, never parsed by its headings, because its shape can change. They keep the raw data as JSON for code, and give the model Markdown, one file per record with an index, so Grep and Read are all it needs to search them.

## Common questions

**Why not have the scripts parse the PR sections the skill cares about?**

Because a PR body's headings change, and a parser that misses a renamed section fails silently, while the model reading the whole body adapts. The script saves the fetching; the model keeps the reading.

**Why Markdown for the model and not JSON?**

Long prose inside JSON becomes one escaped string, which costs more tokens and defeats Grep, since a match returns the whole body as one line. JSON stays on disk for scripts and `jq`.

## It's working if

- The skill's text shrinks: a list of commands becomes one line naming a brief or a script.
- The next tally of the job shows fewer calls and no retries, with the same result.
- An automated job's model has lost its write permission, because the job makes the write from a file the model wrote.

## Where it fits

Periodic maintenance on the agent's tooling, beside [retro](../../skills/engineering/retro/SKILL.md) (one session, the environment) and [improve-codebase-architecture](../../skills/engineering/improve-codebase-architecture/SKILL.md) (the code). [writing-for-agents](../../skills/productivity/writing-for-agents/SKILL.md) sets the style for the skill text it changes. [dev-flow](../../skills/engineering/dev-flow/SKILL.md) maps the whole set.
