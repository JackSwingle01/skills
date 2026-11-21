# Pre-production

Checks that run before the change reaches production: in the session, at commit, before the PR, and in CI. **Run at** uses the tiers in `SKILL.md`; the score columns use its scale. Rows run roughly from cheapest to most expensive overall.

| Technique | Create when | Run at | Setup | Per addition | Run time | Payoff |
|---|---|---|---|---|---|---|
| Lint | The same mechanical mistake lands twice | Edit | 1 | 1 | 1 | 4 |
| Unit | Logic with branches, at its seam. Pair with a property or acceptance test: same-author unit tests drift toward restating the code | Cycle | 1 | 1 | 1 | 5 |
| Coverage | Use only to find changed lines no test executes. Never a target | PR | 1 | 1 | 2 | 1 |
| Regression | Every bug fix, at the lowest seam that went red on the bug. Kept forever | Cycle | 1 | 2 | 1 | 7 |
| Config validation | Config, env vars, flags, or infra-as-code the app reads: schema and parse checks | Commit; PR when the diff touches config | 2 | 1 | 1 | 8 |
| Property-based | An invariant (round-trip, ordering, idempotence, conservation) is easier to state than the cases | Cycle with few examples; CI with many | 2 | 2 | 2 | 7 |
| Types and schemas | Always on. Tighten (strict mode, tagged types, exhaustive matches) wherever an invalid state got through. Setup is higher when retrofitting strictness onto old code | Edit | 3 | 1 | 2 | 8 |
| Static analysis | Untrusted input, null-heavy code, or a known bug class a tool can find | Commit; full scan at PR | 2 | 2 | 3 | 7 |
| Threat model | At design time, for a new trust boundary, external input, or store of sensitive data | Once, before code | 2 | 3 | 8 | 8 |
| Component | A module or service tested whole through its interface, external dependencies stubbed | Commit | 3 | 2 | 3 | 6 |
| Smoke | The few flows whose failure means nothing works | First in every end-to-end run; after every deploy | 3 | 2 | 4 | 8 |
| Acceptance | One per acceptance criterion, worded from the criterion. Validation lives here | PR | 3 | 3 | 4 | 7 |
| Mutation | Tests written alongside the code. A surviving mutant on a changed line is a missing assertion | PR, scoped to touched modules; CI in full | 3 | 2 | 8 | 6 |
| Fuzz | Parsers, deserialisers, protocol handlers: anything fed untrusted bytes | PR when the diff touches them, short run; CI campaigns | 3 | 3 | 7 | 4 |
| Migration | Schema, migration, or persisted-format change | PR when the diff touches them, against real-shaped data, both directions if reversible | 4 | 2 | 5 | 8 |
| Integration | The risk is in how you use a real dependency: queries, transactions, serialisation, timeouts, retries | Commit for related tests; PR in full | 4 | 3 | 5 | 7 |
| Benchmark | A stated performance requirement or a known hot path | PR when the diff touches it, against the base branch on the same machine | 4 | 2 | 5 | 4 |
| Contract | A boundary between separately owned or separately deployed parts. Setup includes agreeing the broker and workflow across teams | Commit for the side you changed; PR for both sides | 5 | 3 | 2 | 7 |
| End-to-end and UI | A user flow whose breakage costs most. Keep them few. Visual diffs for layout risk | PR for affected flows; CI in full | 5 | 4 | 7 | 5 |
| Formal methods | Concurrent or distributed protocols, and state machines where interleavings matter. A human reviews the spec: a proof of the wrong property passes | When the spec or protocol changes | 6 | 5 | 4 | 5 |
| Penetration | The change opens new attack surface | Follow-up for a human or a scheduled engagement | 4 | 7 | 10 | 7 |
| Usability | The change alters a flow users have learned | Follow-up for a session with real people | 4 | 7 | 10 | 6 |
| Performance | A throughput or latency requirement at system level, in a production-like environment | CI, or a Follow-up when no such environment exists | 6 | 3 | 7 | 5 |
