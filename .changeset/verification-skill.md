---
"mattpocock-skills": minor
---

New model-invoked **`verification`** skill. It picks a check for each risk by the failure it catches and sets when each check runs, from four tables (pre-production, deploy, release, post-release) scoring every technique on setup, per-addition cost, run time, and payoff. **`implement`** loads it before `tdd` and takes its cadence from it in place of its own; **`tdd`** points to it for the kind of check a risk needs; **`pr`** gains a Guards line under Merge Danger for production guards; **`retro`** uses it to pick the check that would have caught a mistake; **`software-factory`** points to it for its automated checks; **`dev-flow`** lists it under the vocabulary underneath.
