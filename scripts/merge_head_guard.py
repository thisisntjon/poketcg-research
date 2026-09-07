#!/usr/bin/env python3
"""Refuse a merge whose head is not the thing that was reviewed.

Authorised by Master 2026-08-02T03:15Z ALARM (instance 5). MASTER OWNS FIRE: this
script CHECKS and REFUSES. It never merges. There is no `gh pr merge` call in it,
deliberately -- a tool that can merge is a tool that eventually merges unasked.

WHY IT EXISTS. Five PRs merged at a head that was not the branch tip:

    #2415 (roach)  #2416 (5080)  #2422 (5080)  #2423 (roach)  ... instance 5

Each dropped work that had been pushed and ANNOUNCED on the bus minutes earlier.
#2422 dropped the evidence for an open alarm. #2423 shipped a knowingly-vacuous
guard onto main. The failure is silent by construction: the PR closes green and
the defect ships, and because the PR is closed nothing re-surfaces it except a
post-merge read of main.

It is not an attention problem. Instance 5 happened AFTER a Master ALARM on
instance 4, and after the author wrote "head moved -- check it at MERGE time, not
dispatch time" in the receipt on that exact PR five minutes before it merged at
the old head. A targeted, timely, specific warning did not prevent it. That is
what makes it tooling rather than diligence.

THREE SOURCES, ALL MUST AGREE:

    --expect        the sha the DISPATCH named (what a reviewer looked at)
    PR API head     headRefOid (what a merge would actually take)
    git ls-remote   the branch's LIVE remote tip (what the author last pushed)

Two-way catches the observed failure. The third catches an API read that is stale
relative to the branch -- a different failure that looks identical from outside.

    python scripts/merge_head_guard.py 2425 --expect 3f0a1b2c3
    python scripts/merge_head_guard.py 2425            # no --expect: API vs remote
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

REPO = "thisisntjon/poketcg"


class BranchGone(Exception):
    """The PR branch no longer exists on the remote -- normally because the PR is
    already merged and the branch was deleted. Distinguished from a mismatch so
    the operator is told which situation they are in."""


class HeadMismatch(Exception):
    """Raised when the sources disagree. Never caught inside this module -- the
    caller must see a non-zero exit."""


def _run(cmd: list[str], timeout: int = 120) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {(r.stderr or r.stdout).strip()[:200]}")
    return (r.stdout or "").strip()


def pr_facts(pr: int, repo: str = REPO) -> tuple[str, str]:
    """(headRefOid, headRefName) as the API reports them."""
    out = _run(["gh", "pr", "view", str(pr), "--repo", repo,
                "--json", "headRefOid,headRefName"])
    d = json.loads(out)
    return d["headRefOid"], d["headRefName"]


def remote_tip(branch: str, repo: str = REPO) -> str:
    """The branch's live tip, straight from the remote. Not a local ref: a stale
    local ref is exactly the kind of thing this guard exists to distrust."""
    out = _run(["git", "ls-remote", f"https://github.com/{repo}.git",
                f"refs/heads/{branch}"])
    if not out:
        # The branch is gone from the remote. Overwhelmingly this means the PR is
        # already merged and the branch was deleted -- there is nothing left to
        # guard. Raising a bare RuntimeError here produced a TRACEBACK, which is
        # indistinguishable from "the tool is broken" to whoever is mid-merge, and
        # a guard that looks broken is a guard that gets bypassed.
        raise BranchGone(branch)
    return out.split()[0]


def compare(expect: str | None, api_head: str, tip: str) -> list[str]:
    """Return a list of disagreements. Empty list means safe to merge.

    Compares on the shortest supplied prefix so a 9-char dispatch sha can be
    checked against a 40-char oid -- dispatches quote short shas, and a guard
    that only accepts full oids would be bypassed by every real dispatch.
    """
    problems = []
    if api_head != tip:
        problems.append(
            f"PR API head {api_head[:9]} != branch remote tip {tip[:9]} -- "
            "the branch moved after the API read; merging takes the OLD head"
        )
    if expect:
        n = min(len(expect), 40)
        if api_head[:n] != expect[:n]:
            problems.append(
                f"dispatched head {expect[:9]} != PR API head {api_head[:9]} -- "
                "the reviewed sha is not what would be merged"
            )
        if tip[:n] != expect[:n]:
            problems.append(
                f"dispatched head {expect[:9]} != branch remote tip {tip[:9]} -- "
                "the author pushed after the dispatch"
            )
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pr", type=int)
    ap.add_argument("--expect", help="sha the dispatch named (short or full)")
    ap.add_argument("--repo", default=REPO)
    args = ap.parse_args()

    api_head, branch = pr_facts(args.pr, args.repo)
    try:
        tip = remote_tip(branch, args.repo)
    except BranchGone:
        print(f"PR #{args.pr}  branch {branch}")
        print(f"  API head   : {api_head[:12]}")
        print("  remote tip : GONE -- branch deleted on the remote")
        print(chr(10) + "REFUSE -- nothing to guard.")
        print("  The branch no longer exists, which normally means this PR is")
        print("  ALREADY MERGED. There is no live head to compare against, so this")
        print("  tool cannot tell you whether the right sha landed. Verify by")
        print("  CONTENT on main instead -- read or run the merged artefact.")
        return 1
    tip = tip
    problems = compare(args.expect, api_head, tip)

    print(f"PR #{args.pr}  branch {branch}")
    print(f"  dispatched : {args.expect or '(not supplied)'}")
    print(f"  API head   : {api_head[:12]}")
    print(f"  remote tip : {tip[:12]}")
    if problems:
        print("\nREFUSE -- do not merge:")
        for p in problems:
            print(f"  * {p}")
        print("\n  Re-read the head and re-dispatch. Five PRs have merged at a stale")
        print("  head; each closed green and shipped the defect anyway.")
        return 1
    print("\nOK -- all supplied sources agree; the reviewed sha is what would merge.")
    print("  (This tool does NOT merge. Master owns fire.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
