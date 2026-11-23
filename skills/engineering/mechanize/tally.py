#!/usr/bin/env python3
"""Tally an agent's tool calls across transcripts, so repeated mechanical work shows up as numbers.

Reads Claude Code session logs (JSONL, one event per line) and claude-code-action execution files
(one JSON array of the same messages). Each file is one run. Prints Markdown: per-run totals, then
every call shape with how many runs it appears in, how often, its errors, the size of what it
returned, and the time spent waiting on it. A shape is the tool, plus the program and subcommand for
shell calls.

Active time leaves out the gaps where an interactive session waited on a person. Tool time counts
overlapping parallel calls once; model time is the rest of the active time. Cost and duration come
from a run's final `result` event when it has one (headless and claude-code-action runs do).

usage: tally.py TRANSCRIPT [TRANSCRIPT ...]
"""
import json
import shlex
import sys
from datetime import datetime
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


def when(e):
    ts = e.get("timestamp") if isinstance(e, dict) else None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() if ts else None
    except ValueError:
        return None


def union(intervals):
    total, end = 0.0, None
    for a, b in sorted(intervals):
        if end is None or a > end:
            total += b - a
            end = b
        elif b > end:
            total += b - end
            end = b
    return total


def run_stats(path):
    calls, results, seen_msgs, started = {}, {}, set(), {}
    out_tokens = in_tokens = 0
    cost = duration = None
    stamps, idle = [], 0.0
    for e in events(path):
        if not isinstance(e, dict):
            continue
        if e.get("type") == "result":
            cost = e.get("total_cost_usd", cost)
            duration = e.get("duration_ms", duration)
        t = when(e)
        msg = e.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        blocks = content if isinstance(content, list) else []
        is_result = any(isinstance(b, dict) and b.get("type") == "tool_result" for b in blocks)
        if t is not None and e.get("type") in ("user", "assistant"):
            if e.get("type") == "user" and not is_result and stamps:
                idle += t - stamps[-1]  # a person's prompt: the gap before it was waiting on them
            stamps.append(t)
        if e.get("type") == "assistant":
            mid = msg.get("id")
            usage = msg.get("usage") or {}
            if mid not in seen_msgs:
                seen_msgs.add(mid)
                out_tokens += usage.get("output_tokens", 0)
                in_tokens += sum(usage.get(k, 0) for k in
                                 ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            for b in blocks:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    calls[b["id"]] = (b.get("name", "?"), b.get("input") or {})
                    started[b["id"]] = t
        elif e.get("type") == "user":
            for b in blocks:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    cid = b.get("tool_use_id")
                    t0 = started.get(cid)
                    wait = (t - t0) if (t is not None and t0 is not None) else None
                    results[cid] = (bool(b.get("is_error")), size(b.get("content")), wait, t0, t)
    active = (stamps[-1] - stamps[0] - idle) if len(stamps) > 1 else 0.0
    if duration is not None:
        active = duration / 1000
    tool = union([(r[3], r[4]) for r in results.values() if r[2] is not None])
    return {"calls": calls, "results": results, "in": in_tokens, "out": out_tokens, "cost": cost,
            "active": active, "tool": tool}


def main(paths):
    if not paths:
        sys.exit(__doc__)
    shapes = defaultdict(lambda: {"runs": set(), "calls": 0, "errors": 0, "chars": 0, "wait": 0.0,
                                  "max": 0.0, "example": ""})
    print("## Runs\n")
    print("| Run | Calls | Errors | Repeats | Active s | Tool s | Model s | Input tokens | Output tokens | Cost |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    totals = defaultdict(float)
    for path in paths:
        r = run_stats(path)
        calls, results = r["calls"], r["results"]
        errors = sum(1 for cid in calls if results.get(cid, (False,))[0])
        inputs = defaultdict(int)
        for cid, (name, inp) in calls.items():
            inputs[(name, json.dumps(inp, sort_keys=True))] += 1
            s = shapes[shape(name, inp)]
            s["runs"].add(path)
            s["calls"] += 1
            err, chars, wait = results.get(cid, (False, 0, None))[:3]
            s["errors"] += err
            s["chars"] += chars
            s["wait"] += wait or 0
            s["max"] = max(s["max"], wait or 0)
            if not s["example"]:
                s["example"] = (inp.get("command") or json.dumps(inp))[:100].replace("\n", " ").replace("|", "\\|")
        repeats = sum(n - 1 for n in inputs.values() if n > 1)
        model = max(r["active"] - r["tool"], 0)
        cost = f"${r['cost']:.3f}" if r["cost"] is not None else ""
        for k, v in (("calls", len(calls)), ("errors", errors), ("repeats", repeats), ("active", r["active"]),
                     ("tool", r["tool"]), ("model", model), ("in", r["in"]), ("out", r["out"]),
                     ("cost", r["cost"] or 0)):
            totals[k] += v
        print(f"| `{path}` | {len(calls)} | {errors} | {repeats} | {r['active']:.0f} | {r['tool']:.0f} | "
              f"{model:.0f} | {r['in']:,} | {r['out']:,} | {cost} |")
    n = len(paths)
    t = {k: v / n for k, v in totals.items()}
    print(f"| **mean of {n}** | {t['calls']:.1f} | {t['errors']:.1f} | {t['repeats']:.1f} | {t['active']:.0f} | "
          f"{t['tool']:.0f} | {t['model']:.0f} | {t['in']:,.0f} | {t['out']:,.0f} | "
          f"{'$%.3f' % t['cost'] if totals['cost'] else ''} |")
    print(f"\n## Call shapes\n\nIn N of {n} runs. A shape in every run is the strongest sign of mechanical work;"
          " a shape with a long wait is a sign of a slow call.\n")
    print("| Shape | Runs | Calls | Errors | Result KB | Wait s | Longest s | Example |")
    print("|---|---|---|---|---|---|---|---|")
    for name, s in sorted(shapes.items(), key=lambda kv: (-len(kv[1]["runs"]), -kv[1]["calls"])):
        print(f"| {name} | {len(s['runs'])}/{n} | {s['calls']} | {s['errors']} | {s['chars'] / 1024:.1f} | "
              f"{s['wait']:.0f} | {s['max']:.0f} | `{s['example']}` |")


if __name__ == "__main__":
    main(sys.argv[1:])
