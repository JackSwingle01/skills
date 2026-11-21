# Release

Guards that expose the change to users gradually and turn a bad change into a fast rollback. The score columns use the scale in `SKILL.md`. Rows run roughly from cheapest to most expensive overall.

| Technique | Create when | Run at | Setup | Per addition | Run time | Payoff |
|---|---|---|---|---|---|---|
| Exception tracking | Always on. Name the error signature that would show this change failing | Continuously; watch it for the first hours after release | 2 | 1 | - | 9 |
| Feature flag | A behaviour change with an uncertain blast radius. Ship dark, turn on by cohort, keep the kill switch. Per addition includes removing the flag once it is fully on | At release, and as the rollback | 3 | 2 | - | 9 |
| Monitoring and alerts | Name the signal (latency, errors, saturation) and the threshold that means roll back | During rollout and after | 4 | 2 | - | 8 |
| Canary | Any risk that shows only on real traffic or at scale. Name the metric that decides promote or roll back. Run time is the rollout's duration | At release | 8 | 1 | 6 | 10 |
| Traffic shaping | The rollout needs weighted or targeted routing the platform lacks. Prerequisite for canaries | At release | 8 | 1 | - | 6 |
