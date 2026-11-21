# Post-release

Ongoing checks under real traffic. Most are telemetry the change has to emit, so the session's part is adding the instrumentation. The score columns use the scale in `SKILL.md`. Rows run roughly from cheapest to most expensive overall.

| Technique | Create when | Run at | Setup | Per addition | Run time | Payoff |
|---|---|---|---|---|---|---|
| Real user monitoring | Client-side changes: load time, rendering, client errors by device and region | Continuously | 2 | 1 | - | 5 |
| Logs and events | The change has a failure nobody could otherwise see. Structured fields, one wide event per request | Continuously | 3 | 1 | - | 8 |
| Profiling | A performance-sensitive change, to compare real workloads before and after | Continuously, or for the release window | 3 | 1 | - | 5 |
| On-call readiness | The change adds a failure mode: is it debuggable from what is emitted, and does a runbook cover it | Before release, and after each incident | 3 | 4 | 8 | 8 |
| Auditing | Compliance records, or invariants over stored data that a reconciliation job can check | On a schedule | 4 | 3 | - | 5 |
| Dynamic exploration | An unexplained production symptom: query the telemetry by arbitrary fields | On demand | 5 | 1 | - | 7 |
| Tracing | The change crosses services, or the latency risk sits in a hop between them | Continuously, sampled | 6 | 2 | - | 6 |
| A/B test | A product hypothesis to validate, not correctness. Needs enough traffic for statistical power. Run time is the experiment window | Over the experiment window | 6 | 4 | 9 | 5 |
| Chaos | Testing resilience assumptions, once basic resilience exists | On a schedule | 7 | 4 | 5 | 4 |
| Teeing | A copy of a production stream for an experiment or analysis pipeline, the original untouched | For the experiment's life | 8 | 3 | - | 3 |
