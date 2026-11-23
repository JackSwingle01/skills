---
name: mechanize
description: "Audit a skill or automated agent job for mechanical work (fetching, copying, counting, formatting) the model does that code should do instead, weigh each move against the flexibility it costs, and compare before and after."
disable-model-invocation: true
---

The model's tokens belong to the work only a model can do: judgment and writing. Everything else is **mechanical**, the same work every run: fetching what the next step needs, copying lines verbatim, counting, formatting a fixed template, paginating, retrying, deduplicating by ID, working out dates. This skill audits a **target** (a skill, or an automated job that runs one) for mechanical work and proposes moving each piece down the **ladder** into code.

Every move trades **flexibility** for savings. The model adapts when an input changes shape, a call fails in a new way, or a run needs something no one planned for; a script does what it was written to do. A move earns its place only when the savings are real and the step never needed that adapting. "Already well mechanized, nothing worth moving" is a normal result: report it rather than reach for marginal candidates. A skill audited twice should find less the second time, not the same amount.

## Steps

### 1. Read the target

Call the Skill tool with "writing-for-agents" for the style any changed skill text must keep.

Read the whole target: the `SKILL.md` and every file bundled beside it, each skill it calls, and the workflow, hook, or scheduled job that invokes it, with the prompt that job passes.

Done when you can name every command, fetch, and write the target asks the model to make, and what each one's output feeds.

### 2. Tally the runs

Collect up to ten recent transcripts of the target's runs, and call the Skill tool with "transcript-tally" to tally them. Of its columns, this audit reads the call shapes, repeats, errors, the split between tool and model time, tokens, and cost. Human time, stops, and permissions are `/retro`'s concern, with one exception: a script that replaces many calls the auto mode classifier checks with one call a rule allows saves a little, which is worth a line on a candidate but never a reason for one. Read the transcripts themselves only where a shape needs explaining.

Pick runs whose inputs differ. A shape the target's text requires is the job's own on any input; a shape the model chose is the job's own only when it recurs across varied inputs, and one seen on a single kind of input may be that input's.

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

**Waiting** is a separate finding, not mechanical work. When most of a run's active time is one slow call (a full test suite, a long build), moving it into a script saves nothing. Name the call and the share of time it takes, and the remedy that fits: a narrower call (one test class, not the suite), running it in the background while the model works on, caching its result, or deferring it to CI or a nightly run.

What stays with the model: deciding what something means, whether an item is covered, which option to recommend, what to write. A fetch stays with the model only when choosing what to fetch next is itself the judgment, as in a diagnosis.

Done when each command, fetch, and write from step 1 is marked mechanical, judgment, or waiting, with the reason.

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

### 5. Weigh each candidate

For each candidate, set what it saves against what it costs:

- **Saves**: calls and model turns per run (each call costs a model turn around it, often more than the call itself), tokens, errors and retries, minutes.
- **Costs**: the flexibility it removes (did the model handle this step differently across runs for a good reason, or recover from something a script would fail on?), the code to keep working as the source changes, and how quietly it could fail.

Rate each **high** or **low** confidence:

- **High**: the step recurs and its cost is measured, and the script's output is all the model ever used from it. It recurs when the target's text requires it on every run (one measured run is then enough, since the text guarantees the repeat and the run gives the cost), or when the tally shows it, done the same way, across varied runs.
- **Low**: a step the model chose to take, seen on one run or one kind of input; text with no run to measure it; a small saving; or a step the model sometimes did differently for a reason.

Drop a candidate whose saving is a call or two per run, or whose flexibility cost outweighs it. If none is left, the result is "already well mechanized": say so, with the tally that shows it.

Done when each candidate is dropped or rated, with its saving and its cost stated.

### 6. Present the candidates

Write the report for a reader who has not read this skill: the ladder, its rung numbers, and the tally's shape labels are this skill's working vocabulary, not the reader's. Say where the code would run and who runs it, and name each call by what it fetches or does ("15 calls fetching PR comments", not "15 × `get_comments`").

Order them by confidence, then by measured saving. For each:

```markdown
### <step, in the target's words>

- **Confidence:** <high or low>, because <reason>
- **Evidence:** <the tally's numbers, in plain words, or "text only">
- **Moves to:** <where the code lives and what runs it, e.g. "a workflow step that writes the brief before the model starts", "a script beside the skill that the model runs once">
- **Output:** <files or text it produces, and their shape>
- **Model still decides:** <the judgment left>
- **Flexibility lost:** <what the model could adapt to that the script can't, or "none seen">
- **Fails loudly when:** <what it checks>
```

List waiting findings after them, each with its remedy, and the dropped candidates in one line each with why. Then stop and let the user pick.

### 7. Build and compare

For each picked candidate: write the script; replace the target's command list with the one line that names the brief or the script; move the write into the caller where step 4 said to. A promoted skill whose text changed has its docs re-synced in the same change, following the repo's own rules for that.

Then compare the target before and after on the same scenario. Run its own invocation (its job's prompt, or a headless `claude -p` with the same prompt, saving the transcript with `--output-format stream-json --verbose`) at least three times each with the skill as it was (a git worktree at the commit before the change) and as changed, and tally each set. A full comparison suits a run of a few minutes or less. For a long run (a build), compare only the changed step's calls in its tally rather than rerunning the whole job.

Report the mean saving in cost, tokens, calls, and active time, and whether the results match: the same decisions, the same items, the same output a person would act on. A cheaper run with a worse result is a regression: revert that move. Done when the comparison is reported and every move kept shows a saving with matching results.
