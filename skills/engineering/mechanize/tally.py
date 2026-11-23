#!/usr/bin/env python3
"""Tally an agent's tool calls across transcripts, so repeated mechanical work shows up as numbers.

Reads Claude Code session logs (JSONL, one event per line) and claude-code-action execution files
(one JSON array of the same messages). Each file is one run. Prints Markdown: per-run totals, then
every call shape with how many runs it appears in, how often, its errors, and the size of what it
returned. A shape is the tool, plus the program and subcommand for shell calls.

usage: tally.py TRANSCRIPT [TRANSCRIPT ...]
"""
import json
import shlex
import sys
from collections import defaultdict

TWO_WORD = {"gh", "git", "npm", "npx", "pnpm", "yarn", "dotnet", "cargo", "go", "docker", "kubectl", "uv", "pip"}


def events(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    out = []
    for line in text.splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def command_shape(command):
    """First real program in a shell command, with its subcommand for multi-command tools."""
    first = command.strip().split("\n")[0]
    for sep in ("&&", ";", "|"):
        parts = [p.strip() for p in first.split(sep)]
        parts = [p for p in parts if p and not p.startswith("cd ")]
        if parts:
            first = parts[0]
    try:
        words = shlex.split(first)
    except ValueError:
        words = first.split()
    words = [w for w in words if "=" not in w.split("/")[0] or w.startswith("-")]
    if not words:
        return "(empty)"
    prog = words[0].rsplit("/", 1)[-1]
    if prog in TWO_WORD and len(words) > 1:
        sub = [w for w in words[1:] if not w.startswith("-")][:2 if prog == "gh" else 1]
        return " ".join([prog] + sub)
    return prog


def shape(name, inp):
    if name == "Bash":
        return "Bash: " + command_shape(inp.get("command", ""))
    if name == "Skill":
        return "Skill: " + str(inp.get("skill", ""))
    if name.startswith("mcp__"):
        return name.split("__", 2)[-1] + (f" ({inp['method']})" if "method" in inp else "")
    return name


def size(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(len(b.get("text", "")) if isinstance(b, dict) else len(str(b)) for b in content)
    return len(json.dumps(content))


def run_stats(path):
    calls, results, seen_msgs = {}, {}, set()
    out_tokens = in_tokens = 0
    for e in events(path):
        msg = e.get("message") if isinstance(e, dict) else None
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if e.get("type") == "assistant":
            mid = msg.get("id")
            usage = msg.get("usage") or {}
            if mid not in seen_msgs:
                seen_msgs.add(mid)
                out_tokens += usage.get("output_tokens", 0)
                in_tokens += sum(usage.get(k, 0) for k in
                                 ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            for b in content if isinstance(content, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    calls[b["id"]] = (b.get("name", "?"), b.get("input") or {})
        elif e.get("type") == "user":
            for b in content if isinstance(content, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    results[b.get("tool_use_id")] = (bool(b.get("is_error")), size(b.get("content")))
    return calls, results, in_tokens, out_tokens


def main(paths):
    if not paths:
        sys.exit(__doc__)
    shapes = defaultdict(lambda: {"runs": set(), "calls": 0, "errors": 0, "chars": 0, "example": ""})
    print("## Runs\n\n| Run | Tool calls | Errors | Repeated identical calls | Input tokens | Output tokens |\n|---|---|---|---|---|---|")
    for path in paths:
        calls, results, tin, tout = run_stats(path)
        errors = sum(1 for cid in calls if results.get(cid, (False, 0))[0])
        inputs = defaultdict(int)
        for cid, (name, inp) in calls.items():
            inputs[(name, json.dumps(inp, sort_keys=True))] += 1
            s = shapes[shape(name, inp)]
            s["runs"].add(path)
            s["calls"] += 1
            err, chars = results.get(cid, (False, 0))
            s["errors"] += err
            s["chars"] += chars
            if not s["example"]:
                s["example"] = (inp.get("command") or json.dumps(inp))[:100].replace("\n", " ").replace("|", "\\|")
        repeats = sum(n - 1 for n in inputs.values() if n > 1)
        print(f"| `{path}` | {len(calls)} | {errors} | {repeats} | {tin:,} | {tout:,} |")
    n = len(paths)
    print(f"\n## Call shapes\n\nIn N of {n} runs. A shape in every run is the strongest sign of mechanical work.\n")
    print("| Shape | Runs | Calls | Errors | Result KB | Example |\n|---|---|---|---|---|---|")
    for name, s in sorted(shapes.items(), key=lambda kv: (-len(kv[1]["runs"]), -kv[1]["calls"])):
        print(f"| {name} | {len(s['runs'])}/{n} | {s['calls']} | {s['errors']} | {s['chars'] / 1024:.1f} | `{s['example']}` |")


if __name__ == "__main__":
    main(sys.argv[1:])
