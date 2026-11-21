# Deploy

Checks against the new version running on production infrastructure before users reach it. They catch what no staging environment reproduces: real IAM, DNS, secrets, network paths, data, and capacity. The score columns use the scale in `SKILL.md`. Rows run roughly from cheapest to most expensive overall.

| Technique | Create when | Run at | Setup | Per addition | Run time | Payoff |
|---|---|---|---|---|---|---|
| Config verification | The change reads config that must resolve in the real environment: secrets present, endpoints reachable, flags parse | After deploy, before traffic | 3 | 1 | 2 | 8 |
| Integration in production | The change depends on real permissions, DNS, secrets, or network paths staging fakes | After deploy, before traffic | 6 | 3 | 4 | 7 |
| Load | A capacity question, or how the new version degrades past its limit, on real infrastructure | After deploy, before release, off-peak | 6 | 3 | 7 | 5 |
| Soak | Suspected leaks or slow exhaustion: memory, connections, handles, disk | After deploy, held for hours or days | 5 | 2 | 10 | 4 |
| Shadowing | Live traffic mirrored to the new version, responses discarded. Isolate side effects (writes, emails, charges) first | After deploy, before release | 9 | 3 | - | 7 |
| Tap compare | A rewrite where old and new should return the same responses. Diff two old instances too, to filter nondeterministic fields | After deploy, before release | 9 | 3 | - | 6 |
