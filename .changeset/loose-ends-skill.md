---
"skills": minor
---

New model-invoked **`loose-ends`** skill. It sweeps the pull requests merged since its last sweep (body, work log, decision records, glossary diff, and comments from people with write access) for loose ends: follow-ups nobody ticketed, decisions an agent made without a person, and new or undefined terms. It drops what is already ticketed or answered and files the rest as one grilling ticket to work through with `/grill-with-docs`. It keeps its cursor in a marker on that ticket, so it can run unattended on a schedule. **`dev-flow`** routes to it.
