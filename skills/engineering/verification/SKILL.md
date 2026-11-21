---
name: verification
description: Choose and schedule checks. Use when deciding which kind of test or check fits a risk, adding a kind of test the repo lacks, choosing what to run after a change or before a commit or PR, or when the suite is too slow to run every cycle.
---

# Verification

**Verification** asks whether the code does what the spec says. **Validation** asks whether the spec says what the user needs. Know which one each check performs: a green verification suite says nothing about validation.

This skill decides which check to add and when to run it. How to write a good test at a seam lives in `tdd`.

## Technique files

Each phase has its own table of techniques: when to create it, when to run it, its costs, and its payoff.

- [PRE-PRODUCTION.md](PRE-PRODUCTION.md): checks that run in the session and in CI. Read it before step 2 below, every time.
- [DEPLOY.md](DEPLOY.md): checks against the new version in production, before users reach it.
- [RELEASE.md](RELEASE.md): guards that expose the change to users gradually and roll it back.
- [POST-RELEASE.md](POST-RELEASE.md): ongoing checks under real traffic.

Read the last three when a risk survives step 2: no pre-production row goes red on it because only production shows it (real traffic, real config, scale).

### Scores

Every score is a 1 to 10 default for an agent-assisted product codebase. The repo's domain moves them (payments raises the payoff of property tests and formal methods; a static site lowers contract tests).

| Column | Measures | 1 | 4 | 7 | 10 |
|---|---|---|---|---|---|
| **Setup** | one-time effort to make the first one work, including standing up its infrastructure | minutes | a day | weeks | a quarter |
| **Per addition** | effort to add one more test, rule, flag, or alert | an agent in minutes | an hour | a day, needs a human | days of human work |
| **Run time** | wall-clock for one run | milliseconds | seconds | minutes | hours or days |
| **Payoff** | how often it catches what matters | rarely | sometimes | often | the main defence |

A dash in **Run time** means the technique runs continuously, so there is no single run to time; its cost shows up in **Setup** and **Per addition**.

How to use them:

- **Choosing between rows that both catch a failure:** compare **Per addition** and **Run time**. Setup is already paid when the repo has the row.
- **Proposing a row the repo lacks:** weigh **Setup** against **Payoff**. That is a Follow-up or a proposal to the user, never a side quest inside the ticket.
- **Placing a check in a tier:** **Run time** decides it (see Cadence).

## Pick the check by the failure

For each risk the change carries:

1. **Name the failure** in one line: what goes wrong, and for whom. "Discount applied twice when the cart is re-priced", not "pricing logic".
2. **Pick the cheapest row in PRE-PRODUCTION.md that goes red on it**, judged by Per addition and Run time. A type that makes the bad state unrepresentable beats every test of it. When only an expensive row can see a failure that lives in one module, the seam is in the wrong place: log it.
3. **Source the oracle independently.** The expected result comes from the spec, a worked example, or an invariant, not from the code you just wrote. When one agent writes the code and its tests, both carry the same misunderstanding; an independent oracle is what tells them apart.
4. **Note what it catches and what it misses**, one line each. A miss that matters is another risk: back to step 1.
5. **Name the production guard** for any risk no pre-production row catches. Pick it from the other three files and put it in the PR's merge-danger call, with the signal that decides promote or roll back. Instrumentation the guard depends on is part of this change.

Done when every risk named in the ticket, the spec, or the work log has a check that goes red on it, a named production guard, or a Follow-up saying why neither exists.

## Cadence

The **Run at** column in PRE-PRODUCTION.md names one of these tiers. The repo's scripts and CI config hold the real commands; map them onto the tiers.

| Tier | Budget | When |
|---|---|---|
| **Edit** | seconds | after every edit |
| **Cycle** | under ~30s | every red → green cycle, scoped to the file or seam in hand |
| **Commit** | a minute or two | before each commit, scoped to tests related to changed files |
| **PR** | minutes | before opening the PR: the full suite plus every row whose trigger the diff matches |
| **CI** | unbounded | in CI or on a schedule |

A check that outgrows its tier's budget moves down a tier. When you need that protection every cycle, add a cheaper row that catches the same failure rather than running the slow one more often. A repo with no way to run only related tests is a Follow-up.

## Flakes

A test that gives different results on the same code is broken, whatever colour it shows. On an unexpected red, rerun it once. If the rerun disagrees, it is a flake: it stops counting as evidence about your change. Log it as a Follow-up with both outputs and carry on. A test retried until it passes proves nothing.
