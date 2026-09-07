#!/usr/bin/env python
"""Run the gates CI will run on your PR, before you push.

WHY THIS EXISTS
---------------
Two seats failed CI on 2026-09-03 for mechanical, predictable reasons:

  #3206  a module-level `import rules_lucario` pulled `cg.api` into engine-free CI
  #3219  four pre-regs were missing their `PRIOR_ART:` lines

Both were caught by gates that already existed as scripts, and both were missed
because the documented pre-PR checklist in `START-HERE.md` §6 did not list them.
A checklist that omits two of the four gates is not a checklist you can follow and
still be safe -- so this runs the actual set instead of asking anyone to remember it.

WHAT IT IS NOT
--------------
This is NOT "CI passed". `ci.yml` also runs non-Python steps this does not attempt
(diff hygiene, receipts/manifest coherence, py_compile sweep, the engine-free unit
test suite, tracked-artifact compliance, the lint_silent ratchet, and more), plus
three other workflows. A green run here means *these listed gates* pass. It is a
cheap filter against the failures actually seen, not a proof.

Usage:
    python scripts/ci_gates.py            # run them all, report each
    python scripts/ci_gates.py --list     # print the commands, run nothing
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Kept in the order ci.yml runs them. Each entry is (ci step name, argv).
# If you change ci.yml's python gate steps, change this list in the same commit --
# the whole point is that the two do not drift.
GATES: list[tuple[str, list[str]]] = [
    ("generated inventory content and history",
     ["python", "scripts/build_sri.py", "--check", "--require-complete-history"]),
    ("bank_lint (changed analysis / BANKED artifacts)",
     ["python", "ptcg-agent/harness/bank_lint.py", "--changed", "--json"]),
    ("board linter (status.py)",
     ["python", "ptcg-agent/harness/status.py"]),
    ("onboarding truth gate (onboard_check.py)",
     ["python", "scripts/onboard_check.py"]),
    ("prior-art gate on new pre-regs (leg C item 7)",
     ["python", "scripts/prereg_prior_art_lint.py", "--changed-vs", "origin/main"]),
]


def verdict_gate(pr_body: str) -> tuple[bool, str]:
    """Run ci.yml's `exactly one verdict token in the PR body` lint.

    This gate reads the PR BODY, not the tree, so it cannot run from the working copy
    alone -- which is exactly why it was missing here and why it kept biting. On
    2026-09-03 four PRs opened in one session (#3255, #3257, #3258, #3259) went red on
    it after this script had reported a clean run, because a body-scoped gate is
    invisible to a tree-scoped checklist.

    Reporting matters as much as running: when no body is supplied this is announced as
    NOT CHECKED rather than skipped silently. A count of passing gates that quietly
    omits one is the same failure as `PREFLIGHT PASSED` over checks that never ran.
    """
    import os  # noqa: PLC0415 -- only needed on this path
    env = dict(os.environ, PR_BODY=pr_body)
    p = subprocess.run(["python", "scripts/verdict_lint.py", "--env", "PR_BODY"],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return p.returncode == 0, ((p.stdout or "") + (p.stderr or "")).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="print the commands and exit")
    ap.add_argument("--pr-body-file", metavar="PATH",
                    help="file holding the PR body, to check the verdict-token gate")
    ap.add_argument("--pr", metavar="N",
                    help="PR number; fetches the body with gh to check the verdict gate")
    args = ap.parse_args()

    if args.list:
        for name, argv in GATES:
            print(f"{name}\n    {' '.join(argv)}")
        return 0

    width = max(len(n) for n, _ in GATES)
    failed: list[tuple[str, int, str]] = []
    for name, argv in GATES:
        try:
            p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
        except FileNotFoundError as e:
            print(f"  {name:<{width}}  TOOL MISSING ({e})")
            failed.append((name, -1, str(e)))
            continue
        if p.returncode == 0:
            print(f"  {name:<{width}}  PASS")
        else:
            print(f"  {name:<{width}}  FAIL (exit {p.returncode})")
            tail = (p.stdout or "") + (p.stderr or "")
            failed.append((name, p.returncode, tail.strip()[-1200:]))

    # The body-scoped gate, reported explicitly either way.
    body = None
    if args.pr_body_file:
        body = Path(args.pr_body_file).read_text(encoding="utf-8")
    elif args.pr:
        g = subprocess.run(["gh", "pr", "view", args.pr, "--json", "body", "-q", ".body"],
                           cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        body = g.stdout if g.returncode == 0 else None
        if body is None:
            print(f"  {'verdict token in PR body':<{width}}  COULD NOT FETCH #{args.pr}")
    if body is not None:
        ok, detail = verdict_gate(body)
        if ok:
            print(f"  {'verdict token in PR body':<{width}}  PASS")
        else:
            print(f"  {'verdict token in PR body':<{width}}  FAIL")
            failed.append(("verdict token in PR body", 1, detail))

    print()
    if not failed:
        print(f"{len(GATES)}/{len(GATES)} tree gates pass"
              + (", plus the verdict gate." if body is not None else "."))
        if body is None:
            print("VERDICT GATE NOT CHECKED -- it reads the PR body, which this run was "
                  "not given. Re-run with --pr <n> or --pr-body-file <path>; four PRs "
                  "went red on it in one session after a clean run here.")
        print("This is NOT 'CI passed' -- ci.yml runs further non-Python steps and there "
              "are three other workflows.")
        return 0

    # Total is the tree gates plus the verdict gate when a body was supplied -- otherwise
    # a failure line would report "3/4" while five checks actually ran.
    total = len(GATES) + (1 if body is not None else 0)
    print(f"{total - len(failed)}/{total} gates pass; {len(failed)} FAILED\n")
    for name, code, tail in failed:
        print(f"--- {name} (exit {code}) ---")
        print(tail or "(no output)")
        print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
