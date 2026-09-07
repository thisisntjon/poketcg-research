#!/usr/bin/env python3
"""The merge-head guard must be proven to REFUSE, not just to pass.

5080 supplied the piece both our proposals were missing (bus #2274, 2026-08-02
03:06Z): evidence the check discriminates. A guard demonstrated only on the happy
path is the defect it exists to prevent -- I shipped exactly that an hour earlier
in `ci_inc_fault_correlation --check`, which computed a `missing` list and then
ignored it, and it merged onto main.

So every disagreement mode gets a test that asserts BOTH the refusal and WHICH
pair is named. A guard that fails for the wrong reason is a guard whose message
will be misread under time pressure.

Lives under ptcg-agent/harness/ so ci_discover_suites.py runs it by existence.
Pure comparison logic -- no network, no gh, no git.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from merge_head_guard import compare  # noqa: E402

OLD = "f3bef2e7d1111111111111111111111111111111"
NEW = "76a5f743f2222222222222222222222222222222"


class AllAgree(unittest.TestCase):
    def test_no_problems_when_everything_matches(self):
        self.assertEqual(compare(NEW, NEW, NEW), [])

    def test_short_dispatch_sha_matches_full_oid(self):
        """Dispatches quote 9-char shas. A guard that only accepts full oids
        would be bypassed by every real dispatch, which is worse than none."""
        self.assertEqual(compare(NEW[:9], NEW, NEW), [])

    def test_no_expect_supplied_still_checks_api_vs_remote(self):
        self.assertEqual(compare(None, NEW, NEW), [])


class TheObservedFailure(unittest.TestCase):
    """Instance 5, reproduced: #2423 was dispatched at f3bef2e7d, the author
    pushed 76a5f743f and announced it, and the merge took the old head."""

    def test_dispatched_old_while_branch_moved_is_REFUSED(self):
        problems = compare(OLD[:9], OLD, NEW)
        self.assertTrue(problems, "a stale dispatch must refuse")
        joined = " ".join(problems)
        self.assertIn("branch remote tip", joined)

    def test_it_names_the_right_pair(self):
        problems = compare(OLD[:9], OLD, NEW)
        self.assertTrue(any("API head" in p and "remote tip" in p for p in problems),
                        f"expected the API-vs-remote disagreement to be named: {problems}")

    def test_api_stale_against_remote_is_caught_without_expect(self):
        """The third source earns its place: even with no dispatched sha, an API
        read behind the branch is a refusal."""
        self.assertTrue(compare(None, OLD, NEW))


class EachDisagreementMode(unittest.TestCase):
    def test_dispatch_disagrees_with_api(self):
        problems = compare(OLD[:9], NEW, NEW)
        self.assertTrue(any("reviewed sha is not what would be merged" in p
                            for p in problems), problems)

    def test_dispatch_disagrees_with_remote(self):
        problems = compare(NEW[:9], NEW, OLD)
        self.assertTrue(any("author pushed after the dispatch" in p or
                            "remote tip" in p for p in problems), problems)

    def test_every_source_differing_reports_more_than_one_problem(self):
        third = "aaaaaaaaa3333333333333333333333333333333"
        self.assertGreater(len(compare(third[:9], OLD, NEW)), 1)


class ItCannotMerge(unittest.TestCase):
    """Master owns fire. A tool that can merge is a tool that eventually merges
    unasked, so the absence is asserted rather than trusted.

    Asserted over the AST, not over the source text: the first version scanned for
    the substring "pr merge" and flagged the module's own docstring, which says
    there is no such call. A guard that fires on prose is a guard people learn to
    ignore -- and this suite exists precisely because a guard nobody trusts is
    worth nothing.
    """

    def _command_argv(self):
        """Strings passed to a COMMAND call only -- `_run([...])` or
        `subprocess.run([...])`. Scoped there deliberately: the first version
        scanned every Call and flagged a print() that says "what would merge",
        and the version before that flagged the module docstring. What can
        actually execute is argv, and nothing else. A test that fires on prose
        trains people to ignore it.
        """
        import ast
        src = (Path(__file__).resolve().parents[2] / "scripts"
               / "merge_head_guard.py").read_text(encoding="utf-8")
        out = []
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            is_cmd = (isinstance(f, ast.Name) and f.id == "_run") or (
                isinstance(f, ast.Attribute) and f.attr == "run")
            if not is_cmd or not node.args:
                continue
            for sub in ast.walk(node.args[0]):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    out.append(sub.value)
        return out

    def test_no_command_can_merge(self):
        argv = self._command_argv()
        self.assertTrue(argv, "found no command argv to inspect -- scan is vacuous")
        for s in argv:
            low = s.lower()
            for forbidden in ("merge", "--squash", "--admin", "--rebase", "--delete"):
                self.assertNotIn(forbidden, low,
                                 f"guard must not be able to merge; argv has {s!r}")

    def test_the_only_gh_subcommand_is_a_read(self):
        argv = self._command_argv()
        if "gh" in argv:
            self.assertIn("view", argv, "the only gh call must be a read (pr view)")

    def test_the_scan_would_catch_a_real_merge_call(self):
        """Guard the guard: prove the AST scan fails on a module that CAN merge,
        so passing is evidence rather than an artefact of scanning nothing."""
        import ast
        bad = ast.parse('subprocess.run(["gh", "pr", "merge", "2425"])')
        found = [n.value for n in ast.walk(bad)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn("merge", found)


class DeletedBranch(unittest.TestCase):
    """A merged PR's branch is deleted, so ls-remote finds nothing.

    The first version raised a bare RuntimeError and printed a TRACEBACK, which
    to whoever is mid-merge is indistinguishable from "the tool is broken" -- and
    a guard that looks broken is a guard that gets bypassed. Found by running the
    guard on main against a real merged PR (#2410) rather than by reading it.

    It still FAILS CLOSED. The point of the fix is that it says WHY.

    MUST sit above ``if __name__ == "__main__"``: ci_discover_suites.py runs this
    file as a script (`python path/to/test_….py`), so classes defined after
    unittest.main() are never collected under the path that matters (Master
    REQUEST CHANGES on #2431).
    """

    def test_branch_gone_is_its_own_exception(self):
        import merge_head_guard as g
        self.assertTrue(issubclass(g.BranchGone, Exception))
        self.assertIsNot(g.BranchGone, g.HeadMismatch,
                         "a deleted branch is not a head mismatch; the operator "
                         "needs to know which situation they are in")

    def test_remote_tip_raises_BranchGone_on_empty_output(self):
        import merge_head_guard as g
        original = g._run
        g._run = lambda *a, **k: ""          # ls-remote finds nothing
        try:
            with self.assertRaises(g.BranchGone):
                g.remote_tip("some/deleted-branch")
        finally:
            g._run = original

    def test_main_returns_nonzero_when_branch_is_gone(self):
        """Fail-closed is exercised, not grepped. A vacuous source-scan that
        rebuilt the string it asserted would pass even if BranchGone returned 0.
        """
        import merge_head_guard as g
        orig_facts = g.pr_facts
        orig_tip = g.remote_tip
        g.pr_facts = lambda pr, repo=g.REPO: (NEW, "already/merged-branch")
        g.remote_tip = lambda branch, repo=g.REPO: (_ for _ in ()).throw(
            g.BranchGone(branch))
        try:
            # argparse reads sys.argv; point it at a fake PR number.
            old_argv = sys.argv
            sys.argv = ["merge_head_guard.py", "2410"]
            try:
                rc = g.main()
            finally:
                sys.argv = old_argv
        finally:
            g.pr_facts = orig_facts
            g.remote_tip = orig_tip
        self.assertEqual(rc, 1, f"BranchGone path must refuse (rc=1), got {rc}")

    def test_this_class_is_collected_when_run_as_a_script(self):
        """Guard the placement: if someone moves us below __main__ again, CI
        (script path) silently drops us while import-path discovery still green.
        """
        src = Path(__file__).read_text(encoding="utf-8")
        main_at = src.index('if __name__ == "__main__"')
        class_at = src.index("class DeletedBranch")
        self.assertLess(
            class_at, main_at,
            "DeletedBranch must be defined BEFORE if __name__ so "
            "ci_discover script invocation collects it")


if __name__ == "__main__":
    unittest.main()
