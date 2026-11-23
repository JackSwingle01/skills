---
name: mechanize
description: "Audit a skill or automated agent job for mechanical work (fetching, copying, counting, formatting) the model does that code should do instead, and propose moving each step into a script."
disable-model-invocation: true
---

The model's tokens belong to the work only a model can do: judgment and writing. Everything else is **mechanical**, the same work every run: fetching what the next step needs, copying lines verbatim, counting, formatting a fixed template, paginating, retrying, deduplicating by ID, working out dates. This skill audits a **target** (a skill, or an automated job that runs one) for mechanical work and proposes moving each piece down the **ladder** into code.

## Steps

### 1. Read the target

Call the Skill tool with "writing-for-agents" for the style any changed skill text must keep.

Read the whole target: the `SKILL.md` and every file bundled beside it, each skill it calls, and the workflow, hook, or scheduled job that invokes it, with the prompt that job passes.

Done when you can name every command, fetch, and write the target asks the model to make, and what each one's output feeds.

### 2. Tally the runs

Collect up to ten recent transcripts of the target's runs: Claude Code session logs (`~/.claude/projects/<project>/*.jsonl`, subagents' logs beside them), or the `execution_file` an automated `claude-code-action` run writes (often saved as a run artifact). Run the tally beside this file over them:

```bash
python3 <this skill's directory>/tally.py <transcript> [<transcript> ...]
```

It prints each run's calls, errors, repeated identical calls, and tokens, then every **call shape** (the tool, plus the program and subcommand for shell calls) with how many runs it appears in and how much it returned. Read the transcripts themselves only where a shape needs explaining.

With no transcripts, audit the text alone and mark every candidate **unconfirmed**: the text shows what could be mechanical, and only runs show what it costs.

Done when every shape that appears in most runs, and every shape with errors or large results, is tied to the step in the target that makes it.

### 3. Find the mechanical work

Look for these signs, in the text and in the tally:

| Sign | Where |
|---|---|
| A list of commands for the model to run | the text |
| "verbatim", "copy", "list every", "count", "for each", a fixed template to fill | the text |
| Date or window arithmetic, cursors, pagination, dedup by ID | the text, and long reasoning before a call |
| A write with side effects (create an issue, push, label) made by the model in an automated job | the text, the tally |
| A done criterion a script could check | the text |
| A shape in every run, with only its arguments changing | the tally |
| The same call repeated, or retried after an error | the tally's repeats and errors |
| A file read only to find a path, ID, or number; JSON output read by eye for two fields | the transcripts |
| The same fetch in another skill too | search every skill's text for it |

What stays with the model: deciding what something means, whether an item is covered, which option to recommend, what to write. A fetch stays with the model only when choosing what to fetch next is itself the judgment, as in a diagnosis.

Done when each command, fetch, and write from step 1 is marked mechanical or judgment, with the reason.

### 4. Place each candidate on the ladder

Put each mechanical step on the highest rung it fits:

1. **Nothing to run.** The caller fetches it before the model starts: a workflow step writing a brief file the prompt names, a session-start hook, or in Claude Code a `` !`command` `` line in the skill, which runs when the skill loads (other harnesses need a fallback: rung 2).
2. **One bundled script**, beside the `SKILL.md`, that the model runs once when it needs the output, because what to fetch depends on a decision made mid-run.
3. **A shared skill's script**, once two skills need the same fetch: it moves into a model-invoked skill that owns it, and every other skill reaches it by calling the Skill tool with that skill, never by a path into another skill's folder.
4. **The model**, for the steps marked judgment.

A side-effect write moves to the caller wherever an automated caller exists: the model writes the body to a file, and the job's next step makes the write. That also takes the write permission off the model.

Each script follows these rules:

- **Fetch verbatim, interpret nothing.** Free text whose shape can change (PR bodies, comments, docs) is copied whole, never parsed by headings or patterns. Pulling out IDs only to decide what else to fetch is fine: an extra fetch costs nothing.
- **Fail loudly.** Retry transient errors with backoff, then exit non-zero naming what is missing. A partial brief that looks complete is worse than none.
- **Store for code, render for the model.** Keep the raw fetch as JSON in the source's own shape, for scripts and `jq`. Give the model Markdown, one file per record plus an index with one line per record, so Grep and Read are its query language. A query CLI earns its help text only when the data is too big to fetch ahead or must be fresh mid-run.
- **Filter by policy, label by judgment.** A rule the caller owns (merged after the cutoff, comments from people with write access) is applied in the script. Anything the model must weigh is kept and labelled (author association, resolved or not).
- **Standard tools only**: the shell, `git`, the tracker's CLI, `jq`, Python's standard library.

Done when each candidate has a rung, the script's inputs and outputs, and what the model still decides.

### 5. Present the candidates

Order them by measured cost (calls, result size, errors across the runs), unconfirmed ones last. For each:

```markdown
### <step, in the target's words>

- **Evidence:** <the tally's numbers, or "unconfirmed: text only">
- **Rung:** <1 to 3>: <where the code lives and who runs it>
- **Output:** <files or text it produces, and their shape>
- **Model still decides:** <the judgment left>
- **Fails loudly when:** <what it checks>
```

Then stop and let the user pick.

### 6. Build the picked ones

For each picked candidate: write the script; replace the target's command list with the one line that names the brief or the script; move the write into the caller where step 4 said to; and run the target once on real input, comparing its result and its tally against a run from before. A promoted skill whose text changed has its docs re-synced in the same change, following the repo's own rules for that.
