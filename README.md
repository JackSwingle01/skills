# Skills

Agent skills for engineering work: grilling, spec and ticket flows, TDD, code review, domain modelling and more.

Forked from [mattpocock/skills](https://github.com/mattpocock/skills) and modified from there. Upstream changes are not pulled in automatically, so expect this set to drift from the original.

## Installation

Pick one route per agent: a plugin and a copied install side by side give you every skill twice.

### From a local clone

```bash
git clone https://github.com/JackSwingle01/skills.git
```

```bash
skills/scripts/link-skills.sh
```

This symlinks every skill outside `misc/` into `~/.claude/skills` and `~/.agents/skills`, so a `git pull` updates them. Re-run it after adding, removing or renaming a skill.

### As a plugin

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add JackSwingle01/skills
claude plugin install mp@jackswingle01
```

To update, run `claude plugin marketplace update jackswingle01`.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add JackSwingle01/skills
codex plugin add mp@jackswingle01
```

Updates itself at startup.

</details>

<details>
<summary><strong>GitHub Copilot</strong> (CLI and VS Code)</summary>

```bash
copilot plugin marketplace add JackSwingle01/skills
copilot plugin install mp@jackswingle01
```

Then, once, add to `~/.copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "jackswingle01": { "source": { "source": "github", "repo": "JackSwingle01/skills" }, "autoUpdate": true }
  }
}
```

In VS Code, run **Chat: Install Plugin From Source** and enter `https://github.com/JackSwingle01/skills`.

</details>

<details>
<summary><strong>Gemini CLI</strong> (manual updates)</summary>

```bash
gemini skills install https://github.com/JackSwingle01/skills.git --path skills/engineering
gemini skills install https://github.com/JackSwingle01/skills.git --path skills/productivity
```

Re-run both commands to update.

</details>

<details>
<summary><strong>Any other agent, or editable files</strong> (manual updates)</summary>

```bash
npx skills@latest add JackSwingle01/skills -a <agent>  # cursor, opencode, devin, windsurf, amp, pi; omit -a to choose
```

To update, run `npx skills@latest update`, and re-run `add` to pick up new skills.

</details>

The skills follow each repo's own conventions (issue tracker, ticket format, where specs and DRs live), so document those in that repo's `AGENTS.md` or `CLAUDE.md`.

## Approach

Each part of the set targets a common way agent-driven work goes wrong:

- **Misalignment.** The agent builds something other than what you meant. [`/grill-me`](./skills/productivity/grill-me/SKILL.md) and [`/grill-with-docs`](./skills/engineering/grill-with-docs/SKILL.md) interview you before any code is written.
- **Missing shared language.** The agent guesses at project jargon and spends twenty words where one would do. [`/grill-with-docs`](./skills/engineering/grill-with-docs/SKILL.md) and [`domain-modeling`](./skills/engineering/domain-modeling/SKILL.md) build a `GLOSSARY.md` and decision records as you go, so names stay consistent across code and conversation.
- **Weak feedback loops.** Without feedback on how its code runs, the agent flies blind. [`tdd`](./skills/engineering/tdd/SKILL.md) drives a red-green loop, [`verification`](./skills/engineering/verification/SKILL.md) picks checks by the failure they catch, and [`diagnosing-bugs`](./skills/engineering/diagnosing-bugs/SKILL.md) runs a gated debugging loop.
- **Entropy.** Agents speed up coding, and with it the slide into a ball of mud. [`codebase-design`](./skills/engineering/codebase-design/SKILL.md) holds the deep-module vocabulary, and [`/improve-codebase-architecture`](./skills/engineering/improve-codebase-architecture/SKILL.md) surveys a codebase for deepening opportunities.

[`/dev-flow`](./skills/engineering/dev-flow/SKILL.md) maps how the skills chain together, from idea to pull request.

## Reference

These split on one axis: who can invoke them. **User-invoked** skills are reachable only when you type them (e.g. `/grill-me`); their job is to orchestrate. **Model-invoked** skills can be invoked by you _or_ reached for automatically by the agent when the task fits; they hold the reusable discipline. A user-invoked skill may invoke model-invoked skills, but never another user-invoked one.

### Engineering

Daily code work.

**User-invoked**

- **[dev-flow](./skills/engineering/dev-flow/SKILL.md)**: Walk through the flow from idea to pull request one step at a time: it reads where the work is from the repo, names the next skill, and says whether to continue, clear, or compact first.
- **[grill-with-docs](./skills/engineering/grill-with-docs/SKILL.md)**: Grilling session that also builds your project's domain model, sharpening terminology and updating `GLOSSARY.md` and DRs inline.
- **[triage](./skills/engineering/triage/SKILL.md)**: Verify an incoming issue, or a ticket someone else wrote, fill any gaps, and route it to the next step.
- **[improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/SKILL.md)**: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **[to-spec](./skills/engineering/to-spec/SKILL.md)**: Turn the current conversation into a spec, saved as a dated file in the repo. No interview, just synthesizes what you've already discussed.
- **[to-tickets](./skills/engineering/to-tickets/SKILL.md)**: Break any plan, spec, or conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published in the repo's ticket conventions.
- **[wayfinder](./skills/engineering/wayfinder/SKILL.md)**: Plan a huge chunk of work, more than one agent session can hold, as a shared map of decision tickets on the issue tracker, and resolve them one at a time until the way to the destination is clear.
- **[retro](./skills/engineering/retro/SKILL.md)**: Suggest improvements to the coding agent's environment (navigation, automated checks, coding standards, steering files, tooling) after a session, most severe first.
- **[mechanize](./skills/engineering/mechanize/SKILL.md)**: Audit a skill or automated agent job, its text and its runs' transcripts, for mechanical work the model does that code should do instead, and propose moving each step into a pre-fetched brief or a bundled script.

**Model-invoked**

- **[implement](./skills/engineering/implement/SKILL.md)**: Build the work described by a spec or set of tickets: scout and design the change, drive `/tdd` at pre-agreed seams, close out with `/code-review`, and open the pull request. A parent agent can hand it to a subagent.
- **[prototype](./skills/engineering/prototype/SKILL.md)**: Build a throwaway prototype to answer a design question, either a single shareable HTML file for state/logic questions, or several radically different UI variations toggleable from one route.
- **[diagnosing-bugs](./skills/engineering/diagnosing-bugs/SKILL.md)**: Disciplined diagnosis loop for hard bugs and performance regressions: build a feedback loop that goes red on this bug → minimise → hypothesise → instrument → fix → regression-test.
- **[research](./skills/engineering/research/SKILL.md)**: Investigate a question against high-trust primary sources and capture the findings as a cited Markdown file in the repo, run as a background agent.
- **[tdd](./skills/engineering/tdd/SKILL.md)**: Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **[domain-modeling](./skills/engineering/domain-modeling/SKILL.md)**: Actively build and sharpen a project's domain model: challenge terms against the glossary, stress-test with edge-case scenarios, and update `GLOSSARY.md` and DRs inline.
- **[codebase-design](./skills/engineering/codebase-design/SKILL.md)**: Shared discipline and vocabulary for designing deep modules: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface.
- **[code-review](./skills/engineering/code-review/SKILL.md)**: Two-axis review of the diff since a fixed point: **Standards** (does it follow the repo's coding standards, plus a Fowler smell baseline?) and **Spec** (does it faithfully implement the originating issue/spec?), run as parallel sub-agents so neither pollutes the other.
- **[pr](./skills/engineering/pr/SKILL.md)**: The shape a pull request body should take: a summary as the smallest visual that makes the change clear, before/after evidence that it works, and a merge-danger call (one-way or two-way door, plus blast radius).
- **[wizard](./skills/engineering/wizard/SKILL.md)**: Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover.
- **[verification](./skills/engineering/verification/SKILL.md)**: Choose checks by the failure they catch and run them at the right cadence: a table of techniques across pre-production, deploy, release, and post-release, each with when to create it, when to run it, its costs, and its payoff.
- **[loose-ends](./skills/engineering/loose-ends/SKILL.md)**: Sweep the pull requests merged since the last sweep for loose ends (untracked follow-ups, decisions an agent made without a person, new or undefined terms) and file them as one grilling ticket. Built to run on a schedule.
- **[work-log](./skills/engineering/work-log/SKILL.md)**: Keep a per-ticket log, outside git, of the hypothesis made before any code and each revision and follow-up as it happens, so review, the PR body, and retros read what changed and why.
- **[transcript-tally](./skills/engineering/transcript-tally/SKILL.md)**: Tally agent transcripts into numbers: tool calls by shape, errors, repeats, time split between tools, the model and a person, stops, permission decisions and denials, tokens and cost. `/retro` and `/mechanize` read it.

### Productivity

General workflow tools, not code-specific.

**User-invoked**

- **[grill-me](./skills/productivity/grill-me/SKILL.md)**: Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved.
- **[teach](./skills/productivity/teach/SKILL.md)**: Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.
- **[to-questionnaire](./skills/productivity/to-questionnaire/SKILL.md)**: Turn a decision you can't answer alone into a Markdown questionnaire for the one person who can, filled in async, or together over a meeting. It grills you about the send (who it's for, what you need back), not the subject.
- **[wait-what](./skills/productivity/wait-what/SKILL.md)**: Fire this the moment a message doesn't land. The agent re-pitches it with the context you're missing, in plain English, using your `GLOSSARY.md` vocabulary.

**Model-invoked**

- **[grilling](./skills/productivity/grilling/SKILL.md)**: Interview the user relentlessly about a plan, decision, or idea until every branch of the design tree is resolved. The reusable interview primitive behind `grill-me`, `grill-with-docs`, `triage`, `wayfinder` and `improve-codebase-architecture`.
- **[writing-for-agents](./skills/productivity/writing-for-agents/SKILL.md)**: Writing documents for agents: skills, AGENTS.md/CLAUDE.md, and any doc an agent reaches by a pointer.
