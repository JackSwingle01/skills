## What it does

`verification` decides which kind of check a change needs and when to run it. It starts from the failure, not from a catalogue: the agent names each risk in one line, then picks the cheapest check that goes red on it, from types and lint up to canaries in production.

The expected result for every check comes from the spec, a worked example, or an invariant, never from the code just written. When one agent writes both the code and its tests, they share one misunderstanding, and an independent oracle is what separates them.

## When to reach for it

Type `/verification`, or the agent reaches for it automatically when a task fits: deciding what kind of test a risk needs, adding a kind of test the repo lacks, choosing what to run before a commit or a PR, or when the suite is too slow to run every cycle. [implement](../../skills/engineering/implement/SKILL.md), [tdd](../../skills/engineering/tdd/SKILL.md), and [retro](../../skills/engineering/retro/SKILL.md) load it, so in the main flow you rarely type it.

For how to write a good test once the kind is chosen, use [tdd](../../skills/engineering/tdd/SKILL.md).

## Four tables, one per phase

The techniques live in four tables, split by where they run: **pre-production** (in the session and in CI), **deploy** (the new version on production infrastructure before users reach it), **release** (exposing it gradually), and **post-release** (ongoing, under real traffic). Every row has the same columns:

| Column | What it tells you |
| --- | --- |
| Create when | the risk that earns the technique a place |
| Run at | its cadence: every edit, every red-green cycle, before each commit, before the PR, or in CI |
| Setup | the one-time cost of the first one, infrastructure included |
| Per addition | the cost of one more test, rule, flag, or alert |
| Run time | wall-clock for one run, which decides its cadence |
| Payoff | how often it catches what matters |

Per addition and run time decide between two checks that both catch a failure. Setup weighed against payoff decides whether to propose a technique the repo doesn't have yet.

Risks that only production shows (real traffic, real config, scale) get no test in the session. The agent names a **guard** for each one instead, in the Guards line of the PR's Merge Danger section.

## Common questions

**Where do the scores come from?**

They are defaults for an agent-assisted product codebase, set by judgement rather than measurement. Agents make code-shaped checks cheap (property tests, formal methods), while infrastructure (canaries, shadowing) costs what it always did. Your domain moves them: payments raises the payoff of property tests, a static site lowers contract tests.

**Why does it name canaries and feature flags when the agent can't run them?**

Because the alternative is silence about the riskiest part of the change. Naming the guard in the PR tells whoever ships it what to watch, and any instrumentation the guard depends on becomes part of the change.

## It's working if

- Each risk in the work log has a check that goes red on it, a named guard, or a follow-up saying why neither exists.
- Slow checks run before the PR when the diff touches what they guard, not on every cycle.
- PRs that carry a production-only risk have a Guards line naming the signal that decides rollback.

## Where it fits

`verification` is a reference the build step pulls in: [implement](../../skills/engineering/implement/SKILL.md) loads it before driving [tdd](../../skills/engineering/tdd/SKILL.md), its guards land in the [pr](../../skills/engineering/pr/SKILL.md) body, and [retro](../../skills/engineering/retro/SKILL.md) uses it to pick the check that would have caught a mistake. [dev-flow](../../skills/engineering/dev-flow/SKILL.md) is the router over the whole set.
