#!/usr/bin/env python3
"""Fetch everything a loose-ends sweep reads into one brief folder, so the sweep reads files.

GitHub only: it needs `gh` (authenticated) and a local clone with the merge commits in history.
It copies text verbatim and interprets none of it; the one thing it pulls out of text is `#N`
references, to decide which other issues and PRs to fetch.

    gather.py --repo OWNER/NAME --out DIR [--since ISO | --prs "12 15"] [--base main]
              [--git PATH] [--docs PATH ...] [--logs DIR] [--max N]

Window: --prs, else PRs merged after --since, else after the newest `loose-ends` cursor marker on
the tracker, else every merged PR. --max keeps the oldest N, so the next sweep starts after them.

Writes DIR/index.md (start here), DIR/prs/<n>.md, DIR/tracker/index.md, DIR/tracker/<n>.md, and
DIR/raw/*.json. Prints the window's PR numbers, oldest first, and writes them to DIR/prs.txt (empty
when nothing merged). Exits non-zero, naming what is missing, if any fetch fails after retries or
any list comes back shorter than its total.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CURSOR = re.compile(r"<!-- loose-ends: through (\S+) -->")
REF = re.compile(r"(?<![\w/])#(\d+)\b")


def fail(message):
    sys.exit(f"gather.py: {message}")


def run(cmd, retries=4):
    for attempt in range(retries):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout
        if attempt < retries - 1:
            time.sleep(2 ** (attempt + 1))
    fail(f"`{' '.join(cmd[:4])} ...` failed after {retries} tries: {proc.stderr.strip()[:500]}")


def git(repo_dir, *args):
    proc = subprocess.run(["git", "-C", repo_dir, *args], capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"`git {' '.join(args)}` failed: {proc.stderr.strip()[:300]}")
    return proc.stdout


def graphql(query, **variables):
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            continue
        cmd += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    data = json.loads(run(cmd))
    if data.get("errors"):
        fail(f"GraphQL error: {json.dumps(data['errors'])[:500]}")
    return data["data"]


def complete(connection, what):
    """A connection fetched in one page must hold all of its items."""
    if connection["totalCount"] > len(connection["nodes"]):
        fail(f"{what}: {connection['totalCount']} items, only {len(connection['nodes'])} fetched")
    return connection["nodes"]


PEOPLE = "author { login } authorAssociation createdAt body"

PR_FIELDS = f"""
  number title url state mergedAt createdAt author {{ login }} authorAssociation body
  baseRefName headRefName mergeCommit {{ oid }}
  labels(first: 50) {{ totalCount nodes {{ name }} }}
  comments(first: 100) {{ totalCount nodes {{ {PEOPLE} url }} }}
  reviews(first: 100) {{ totalCount nodes {{ {PEOPLE} state }} }}
  reviewThreads(first: 100) {{ totalCount nodes {{ isResolved isOutdated path line
    comments(first: 100) {{ totalCount nodes {{ {PEOPLE} }} }} }} }}
"""

ISSUE_FIELDS = f"""
  number title url state stateReason createdAt closedAt author {{ login }} authorAssociation body
  labels(first: 50) {{ totalCount nodes {{ name }} }}
  comments(first: 100) {{ totalCount nodes {{ {PEOPLE} url }} }}
"""


def fetch_pr(owner, name, number):
    q = f"query($owner:String!,$name:String!,$number:Int!){{repository(owner:$owner,name:$name){{pullRequest(number:$number){{{PR_FIELDS}}}}}}}"
    pr = graphql(q, owner=owner, name=name, number=number)["repository"]["pullRequest"]
    if pr is None:
        fail(f"PR #{number} not found")
    for key in ("labels", "comments", "reviews", "reviewThreads"):
        complete(pr[key], f"PR #{number} {key}")
    for thread in pr["reviewThreads"]["nodes"]:
        complete(thread["comments"], f"PR #{number} review thread on {thread['path']}")
    return pr


def paged(query, path, **variables):
    nodes, after, total = [], None, None
    while True:
        conn = graphql(query, after=after, **variables)
        for key in path:
            conn = conn[key]
        total = conn.get("totalCount", conn.get("issueCount"))
        nodes += conn["nodes"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        after = conn["pageInfo"]["endCursor"]
    if total is not None and total > len(nodes):
        fail(f"{'/'.join(path)}: {total} items, only {len(nodes)} fetched")
    return nodes


def all_issues(owner, name):
    q = f"query($owner:String!,$name:String!,$after:String){{repository(owner:$owner,name:$name){{issues(first:50,after:$after,orderBy:{{field:CREATED_AT,direction:ASC}}){{totalCount pageInfo{{hasNextPage endCursor}} nodes{{{ISSUE_FIELDS}}}}}}}}}"
    issues = paged(q, ["repository", "issues"], owner=owner, name=name)
    for issue in issues:
        complete(issue["comments"], f"issue #{issue['number']} comments")
    return issues


def all_prs_index(owner, name):
    q = "query($owner:String!,$name:String!,$after:String){repository(owner:$owner,name:$name){pullRequests(first:100,after:$after,orderBy:{field:CREATED_AT,direction:ASC}){totalCount pageInfo{hasNextPage endCursor} nodes{number title state mergedAt labels(first:20){nodes{name}}}}}}"
    return paged(q, ["repository", "pullRequests"], owner=owner, name=name)


def merged_since(repo, base, since):
    day = (since or "1970-01-01")[:10]
    q = "query($q:String!,$after:String){search(query:$q,type:ISSUE,first:100,after:$after){issueCount pageInfo{hasNextPage endCursor} nodes{... on PullRequest{number mergedAt}}}}"
    nodes = paged(q, ["search"], q=f"repo:{repo} is:pr is:merged base:{base} merged:>={day}")
    if len(nodes) >= 1000:
        fail("the search returns at most 1000 PRs: pass a later --since or --prs")
    hits = [n for n in nodes if n.get("mergedAt") and (not since or n["mergedAt"] > since)]
    return [n["number"] for n in sorted(hits, key=lambda n: n["mergedAt"])]


def cursor_from(issues):
    marks = []
    for issue in issues:
        if "loose-ends" not in [l["name"] for l in issue["labels"]["nodes"]]:
            continue
        for text in [issue["body"]] + [c["body"] for c in issue["comments"]["nodes"]]:
            marks += CURSOR.findall(text or "")
    return max(marks) if marks else None


def who(node):
    return f"{(node.get('author') or {}).get('login', 'ghost')} ({node.get('authorAssociation', '?')})"


def quote(text):
    """Verbatim text in a fence longer than any backtick run inside it, so its headings stay its own."""
    text = (text or "").rstrip()
    if not text:
        return "_(empty)_"
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    fence = "`" * max(4, longest + 1)
    return f"{fence}markdown\n{text}\n{fence}"


def git_side(repo_dir, pr, docs, logs):
    oid = (pr.get("mergeCommit") or {}).get("oid")
    if not oid:
        fail(f"PR #{pr['number']} has no merge commit")
    if subprocess.run(["git", "-C", repo_dir, "cat-file", "-e", f"{oid}^{{commit}}"]).returncode != 0:
        fail(f"merge commit {oid} of PR #{pr['number']} is not in {repo_dir}: clone with full history")
    parents = git(repo_dir, "rev-list", "--parents", "-n1", oid).split()[1:]
    if not parents:
        fail(f"merge commit {oid} of PR #{pr['number']} has no parent")
    base = parents[0]
    files = git(repo_dir, "diff", "--name-status", base, oid).splitlines()
    changed = [line.split("\t")[-1] for line in files]
    doc_paths = [p for p in changed if any(p == d or p.startswith(d.rstrip("/") + "/") for d in docs)]
    out = {"files": files, "commits": git(repo_dir, "log", "--reverse", "--format=%h %an %ad%n%s%n%b%n---", "--date=short", f"{base}..{oid}") if len(parents) > 1 else git(repo_dir, "log", "-1", "--format=%h %an %ad%n%s%n%b", "--date=short", oid)}
    out["doc_diff"] = git(repo_dir, "diff", base, oid, "--", *doc_paths) if doc_paths else ""
    out["doc_log"] = git(repo_dir, "log", "--reverse", "--format=%h %an %ad %s", "--date=short", f"{base}..{oid}", "--", *doc_paths) if doc_paths else ""
    out["logs"] = []
    for line in files:
        status, path = line.split("\t")[0], line.split("\t")[-1]
        if path.startswith(logs.rstrip("/") + "/") and path.endswith(".md") and not status.startswith("D"):
            out["logs"].append((path, git(repo_dir, "show", f"{oid}:{path}")))
    return out


def render_pr(pr, side=None):
    lines = [f"# PR #{pr['number']}: {pr['title']}", "",
             f"- url: {pr['url']}", f"- state: {pr['state']}, merged {pr.get('mergedAt') or 'never'}",
             f"- author: {who(pr)}", f"- branch: {pr.get('headRefName')} into {pr.get('baseRefName')}",
             f"- labels: {', '.join(l['name'] for l in pr['labels']['nodes']) or 'none'}", "",
             "## Body", "", quote(pr["body"]), "", "## Comments", ""]
    for c in pr["comments"]["nodes"]:
        lines += [f"### {who(c)}, {c['createdAt']}", "", quote(c["body"]), ""]
    if not pr["comments"]["nodes"]:
        lines += ["None.", ""]
    lines += ["## Reviews", ""]
    for r in pr["reviews"]["nodes"]:
        lines += [f"### {who(r)}, {r['state']}, {r['createdAt']}", "", quote(r["body"]), ""]
    if not pr["reviews"]["nodes"]:
        lines += ["None.", ""]
    lines += ["## Review threads", ""]
    for t in pr["reviewThreads"]["nodes"]:
        state = "resolved" if t["isResolved"] else "UNRESOLVED"
        lines += [f"### {state}{', outdated' if t['isOutdated'] else ''}: {t['path']}:{t.get('line') or '?'}", ""]
        for c in t["comments"]["nodes"]:
            lines += [f"**{who(c)}, {c['createdAt']}**", "", quote(c["body"]), ""]
    if not pr["reviewThreads"]["nodes"]:
        lines += ["None.", ""]
    if side is not None:
        lines += ["## Files changed", "", "```text", *side["files"], "```", "",
                  "## Commits", "", "```text", side["commits"].rstrip(), "```", ""]
        lines += ["## Work logs", ""]
        for path, text in side["logs"]:
            lines += [f"### {path} (as merged)", "", quote(text), ""]
        if not side["logs"]:
            lines += ["None committed.", ""]
        lines += ["## Glossary and decision record changes", ""]
        if side["doc_diff"]:
            lines += ["Commits that touched them:", "", "```text", side["doc_log"].rstrip(), "```", "",
                      "```diff", side["doc_diff"].rstrip(), "```", ""]
        else:
            lines += ["None.", ""]
    return "\n".join(lines)


def render_issue(issue):
    lines = [f"# Issue #{issue['number']}: {issue['title']}", "", f"- url: {issue['url']}",
             f"- state: {issue['state']}{' (' + issue['stateReason'] + ')' if issue.get('stateReason') else ''}",
             f"- author: {who(issue)}, opened {issue['createdAt']}, closed {issue.get('closedAt') or 'no'}",
             f"- labels: {', '.join(l['name'] for l in issue['labels']['nodes']) or 'none'}", "",
             "## Body", "", quote(issue["body"]), "", "## Comments", ""]
    for c in issue["comments"]["nodes"]:
        lines += [f"### {who(c)}, {c['createdAt']}", "", quote(c["body"]), ""]
    if not issue["comments"]["nodes"]:
        lines += ["None.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.environ.get("GH_REPO"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--since")
    ap.add_argument("--prs")
    ap.add_argument("--base", default="main")
    ap.add_argument("--git", default=".")
    ap.add_argument("--docs", nargs="*", default=["GLOSSARY.md", "CONTEXT.md", "documentation/decisions", "docs/adr", "docs/decisions"])
    ap.add_argument("--logs", default=".agent-logs")
    ap.add_argument("--max", type=int, default=0)
    a = ap.parse_args()
    if not a.repo or "/" not in a.repo:
        fail("--repo OWNER/NAME is required (or set GH_REPO)")
    owner, name = a.repo.split("/", 1)
    out = Path(a.out)
    for sub in ("prs", "tracker", "raw"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    issues = None
    since, source = a.since, "--since"
    if a.prs:
        numbers, source = [int(n) for n in a.prs.split()], "--prs"
    else:
        if not since:
            issues = all_issues(owner, name)
            since, source = cursor_from(issues), "the newest loose-ends cursor"
            if not since:
                source = "no cursor: every merged PR"
        numbers = merged_since(a.repo, a.base, since)
    cut = []
    if a.max and len(numbers) > a.max:
        numbers, cut = numbers[:a.max], numbers[a.max:]

    if not numbers:
        (out / "index.md").write_text(f"# Loose-ends brief\n\n- repo: {a.repo}\n- window: {source}, merged after {since}\n- PRs: none\n")
        (out / "prs.txt").write_text("")
        return
    if issues is None:
        issues = all_issues(owner, name)
    index = all_prs_index(owner, name)
    prs = {}
    for n in numbers:
        pr = fetch_pr(owner, name, n)
        if pr["state"] != "MERGED":
            fail(f"PR #{n} is {pr['state']}, not merged")
        prs[n] = pr
        (out / "prs" / f"{n}.md").write_text(render_pr(pr, git_side(a.git, pr, a.docs, a.logs)))

    # Every #N the window's PRs mention, so step 3 can read what they point at.
    mentioned = set()
    for pr in prs.values():
        texts = [pr["body"]] + [c["body"] for c in pr["comments"]["nodes"]] + [r["body"] for r in pr["reviews"]["nodes"]]
        texts += [c["body"] for t in pr["reviewThreads"]["nodes"] for c in t["comments"]["nodes"]]
        for text in texts:
            mentioned |= {int(m) for m in REF.findall(text or "")}
        mentioned |= {int(m) for m in REF.findall((out / "prs" / f"{pr['number']}.md").read_text())}
    issue_numbers = {i["number"] for i in issues}
    pr_numbers = {p["number"] for p in index}
    for issue in issues:
        (out / "tracker" / f"{issue['number']}.md").write_text(render_issue(issue))
    others = {}
    for n in sorted(mentioned & pr_numbers - set(prs)):
        others[n] = fetch_pr(owner, name, n)
        (out / "tracker" / f"{n}.md").write_text(render_pr(others[n]))

    rows = [("issue", i["number"], i["state"], i["title"], [l["name"] for l in i["labels"]["nodes"]]) for i in issues]
    rows += [("pr", p["number"], p["state"], p["title"], [l["name"] for l in p["labels"]["nodes"]]) for p in index]
    tracker = ["# Tracker", "", "Every issue and PR, one line each. Issues, and PRs the window mentions, have a file "
               "beside this one: `<number>.md`.", "", "| # | Kind | State | Title | Labels | File |", "|---|---|---|---|---|---|"]
    for kind, n, state, title, labels in sorted(rows, key=lambda r: r[1]):
        has = n in issue_numbers or n in others
        tracker.append(f"| {n} | {kind} | {state} | {title.replace('|', '/')} | {', '.join(labels)} | {f'[{n}.md]({n}.md)' if has else ''} |")
    (out / "tracker" / "index.md").write_text("\n".join(tracker) + "\n")

    newest = max((p["mergedAt"] for p in prs.values()), default=None)
    lines = ["# Loose-ends brief", "", f"- repo: {a.repo}, base `{a.base}`",
             f"- window: {source}" + (f", merged after {since}" if since and not a.prs else ""),
             f"- PRs: {len(prs)}, oldest first" + (f"; {len(cut)} newer ones left for the next sweep (--max {a.max}): {' '.join('#%d' % n for n in cut)}" if cut else ""),
             f"- cursor for the ticket: {newest or 'none'}", "",
             "Each PR's file holds its body, comments, reviews and review threads verbatim (author association "
             "beside each author), then the files changed, its commits, every work log it committed as merged, "
             "and its glossary and decision-record diffs with the commits that made them. `tracker/` holds every "
             "issue with its comments, the PRs these mention, and an index of all issues and PRs: Grep it to "
             "search the tracker. `raw/` holds the fetched JSON.", "",
             "| PR | Merged | Author | Title | File |", "|---|---|---|---|---|"]
    for n in numbers:
        p = prs[n]
        lines.append(f"| #{n} | {p['mergedAt']} | {who(p)} | {p['title'].replace('|', '/')} | [prs/{n}.md](prs/{n}.md) |")
    (out / "index.md").write_text("\n".join(lines) + "\n")
    for key, value in (("prs", prs), ("mentioned", others), ("issues", issues), ("index", index)):
        (out / "raw" / f"{key}.json").write_text(json.dumps(value, indent=1))
    (out / "prs.txt").write_text(" ".join(map(str, numbers)))
    print(" ".join(map(str, numbers)))


if __name__ == "__main__":
    main()
