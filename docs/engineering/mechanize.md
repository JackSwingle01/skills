## What it does

`mechanize` audits a skill, or an automated job that runs one, for **mechanical** work: the steps the model does the same way every run, such as fetching what the next step needs, copying lines verbatim, counting, or filling a fixed template. It proposes moving each one into code, so the model spends its tokens only on judgment and writing.

Every move trades the model's **flexibility** (adapting when an input changes shape or a call fails in a new way) for savings, so it weighs the two and rates each candidate high or low confidence. "Already well mechanized" is a normal answer.

It measures before it proposes. [transcript-tally](../../skills/engineering/transcript-tally/SKILL.md) counts the tool calls across several transcripts of the same job, and a call that appears in every run with only its arguments changing is the strongest evidence a step is mechanical. Without transcripts it still reads the skill's text, but marks every candidate unconfirmed.

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

**Won't it find something to script every time I run it?**

It shouldn't, and a second audit of the same skill should find less than the first. A candidate whose saving is a call or two per run, or that removes a step the model handled differently across runs for a good reason, is dropped. When nothing is left, it reports the skill as already well mechanized, with the tally that shows it.

**My job spends most of its time waiting on a slow test suite. Will this help?**

Not by mechanizing: a script runs the same slow suite just as slowly. The tally shows each run's tool time apart from the model's, and a run dominated by one call is reported as a waiting finding, with remedies that fit it: a narrower call, running it in the background, caching, or deferring it to CI.

**How do I know a change was worth it?**

It runs the target before and after on the same scenario, at least three times each, and reports the mean saving in cost, tokens, calls and time, with whether the results match. That suits runs of a few minutes; for a long build it compares only the changed step. A cheaper run with a worse result is reverted.

**Why not have the scripts parse the PR sections the skill cares about?**

Because a PR body's headings change, and a parser that misses a renamed section fails silently, while the model reading the whole body adapts. The script saves the fetching; the model keeps the reading.

**Why Markdown for the model and not JSON?**

Long prose inside JSON becomes one escaped string, which costs more tokens and defeats Grep, since a match returns the whole body as one line. JSON stays on disk for scripts and `jq`.

## It's working if

- The skill's text shrinks: a list of commands becomes one line naming a brief or a script.
- The before-and-after comparison shows fewer calls, lower cost and less time, with the same result.
- A second audit finds less than the first, and sometimes nothing.
- An automated job's model has lost its write permission, because the job makes the write from a file the model wrote.

## Where it fits

Periodic maintenance on the agent's tooling, beside [retro](../../skills/engineering/retro/SKILL.md) (one session, the environment) and [improve-codebase-architecture](../../skills/engineering/improve-codebase-architecture/SKILL.md) (the code). [writing-for-agents](../../skills/productivity/writing-for-agents/SKILL.md) sets the style for the skill text it changes. [dev-flow](../../skills/engineering/dev-flow/SKILL.md) maps the whole set.
