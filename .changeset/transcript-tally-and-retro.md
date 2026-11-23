---
"skills": minor
---

New model-invoked **`transcript-tally`** skill. Its `tally.py` reads Claude Code session logs, headless `claude -p` output and `claude-code-action` execution files, and reports each run's tool calls, errors, repeated calls, time split between tools, the model and a person, stops, permission decisions by source, denials, tokens and cost, then every call shape across runs. **`retro`** now reads a tally of the session and gains two categories, **Stopping for the human** (a stop the agent could have avoided with a pointer, access or a standing rule) and **Permission friction** (repeated denials or prompts on one call shape), and its Tool economy category covers a session dominated by one slow call. **`mechanize`** reads the same tally.
