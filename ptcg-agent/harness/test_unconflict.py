"""Tests for scripts/unconflict.py.

The load-bearing property is the REFUSAL: a conflict outside the generated set must never
be resolved in main's favour. These tests build real throwaway git repos so the refusal is
exercised against git itself, not a mock.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "unconflict.py"


def load_module():
    spec = importlib.util.spec_from_file_location("unconflict", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run(cwd: Path, *args: str) -> str:
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"{' '.join(args)}\n{r.stderr}")
    return r.stdout


class TestScriptShape(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists(), f"missing {SCRIPT}")

    def test_generated_set_is_the_committed_generated_files(self):
        mod = load_module()
        self.assertIn("workflow/HARNESS-INDEX.json", mod.GENERATED)
        self.assertIn("workflow/HARNESS-INDEX-FULL.json", mod.GENERATED)
        self.assertIn("workflow/ARTIFACT-CATALOG.jsonl", mod.GENERATED)
        self.assertIn("workflow/ARTIFACT-CATALOG.md", mod.GENERATED)

    def test_generated_set_holds_no_source_paths(self):
        """A source file must never be auto-resolved. Guards against careless widening."""
        mod = load_module()
        for p in mod.GENERATED:
            self.assertTrue(
                p.startswith("workflow/"),
                f"{p} is outside workflow/; auto-resolving it would discard real work",
            )
            self.assertFalse(p.endswith(".py"), f"{p} is source, not a generated inventory")

    def test_requires_a_target(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=REPO
        )
        self.assertEqual(r.returncode, 2, "no --branch/--all-mine must exit 2")


class TestConflictClassification(unittest.TestCase):
    """Exercise the refusal against a real git repo with a real conflict."""

    def _repo(self, tmp: Path, conflict_path: str) -> Path:
        wd = tmp / "r"
        wd.mkdir()
        run(wd, "git", "init", "-q", "-b", "main")
        run(wd, "git", "config", "user.email", "t@t")
        run(wd, "git", "config", "user.name", "t")
        f = wd / conflict_path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("base\n")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "base")

        run(wd, "git", "checkout", "-q", "-b", "side")
        f.write_text("side\n")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "side")

        run(wd, "git", "checkout", "-q", "main")
        f.write_text("main\n")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "main")

        run(wd, "git", "checkout", "-q", "side")
        subprocess.run(["git", "merge", "main", "--no-edit"], cwd=wd, capture_output=True)
        return wd

    def test_generated_conflict_is_classified_safe(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            wd = self._repo(Path(td), "workflow/HARNESS-INDEX.json")
            r = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=wd, capture_output=True, text=True,
            )
            conflicts = [p for p in r.stdout.split("\n") if p.strip()]
            self.assertEqual(conflicts, ["workflow/HARNESS-INDEX.json"])
            self.assertEqual([p for p in conflicts if p not in mod.GENERATED], [])

    def test_source_conflict_is_classified_unsafe(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            wd = self._repo(Path(td), "ptcg-agent/agent/rules_lucario.py")
            r = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=wd, capture_output=True, text=True,
            )
            conflicts = [p for p in r.stdout.split("\n") if p.strip()]
            unexpected = [p for p in conflicts if p not in mod.GENERATED]
            self.assertEqual(
                unexpected,
                ["ptcg-agent/agent/rules_lucario.py"],
                "a source conflict MUST be flagged unexpected, never auto-resolved",
            )


class TestSriLayerBoundary(unittest.TestCase):
    """The SRI directory mixes generated OUTPUT with hand-written INPUT.

    A prefix rule over `workflow/inventories/sri/` would resolve CURATED.json with main's
    copy and then "regenerate" it, silently destroying curated prose that no generator can
    reproduce. These tests pin the boundary in both directions, so a future widening to a
    prefix fails here rather than in someone's lost work.
    """

    def test_generated_outputs_are_allowlisted(self):
        mod = load_module()
        for path in (
            "workflow/inventories/sri/MANIFEST.jsonl",
            "workflow/inventories/sri/INDEX.md",
            "workflow/inventories/sri/BUILD.json",
            "workflow/inventories/sri/INVENTORY.md",
            "workflow/inventories/sri/registers/TIMELINE.md",
            "workflow/inventories/sri/registers/TOOLS.md",
        ):
            self.assertIn(path, mod.GENERATED, f"{path} is build_sri.py output")

    def test_curated_input_is_not_allowlisted(self):
        mod = load_module()
        self.assertNotIn(
            "workflow/inventories/sri/CURATED.json",
            mod.GENERATED,
            "CURATED.json is hand-written input; resolving it with main's copy loses work",
        )

    def test_run_records_are_not_allowlisted(self):
        mod = load_module()
        for path in (
            "workflow/inventories/sri/runs/2026-09-05/COLD-START.md",
            "workflow/inventories/sri/runs/2026-09-05/DANGLING-MENTIONS.md",
        ):
            self.assertNotIn(path, mod.GENERATED, f"{path} is a run record, not output")

    def test_allowlist_holds_no_directory_prefix_entry(self):
        mod = load_module()
        for entry in mod.GENERATED:
            self.assertFalse(
                entry.endswith("/") or entry.endswith("*"),
                f"{entry} is a prefix/glob; the allowlist must name exact files",
            )


class TestCuratedConflictIsRefused(TestConflictClassification):
    """A CURATED.json conflict must reach the refusal path, like any source conflict."""

    def test_curated_conflict_is_classified_unsafe(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            wd = self._repo(Path(td), "workflow/inventories/sri/CURATED.json")
            r = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=wd, capture_output=True, text=True,
            )
            conflicts = [p for p in r.stdout.split("\n") if p.strip()]
            self.assertEqual(conflicts, ["workflow/inventories/sri/CURATED.json"])
            self.assertEqual(
                [p for p in conflicts if p not in mod.GENERATED],
                ["workflow/inventories/sri/CURATED.json"],
                "a CURATED.json conflict MUST be refused, never auto-resolved",
            )

    def test_a_generated_sri_conflict_is_still_classified_safe(self):
        """Positive control beside the negative one: the allowlist is not simply empty."""
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            wd = self._repo(Path(td), "workflow/inventories/sri/MANIFEST.jsonl")
            r = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=wd, capture_output=True, text=True,
            )
            conflicts = [p for p in r.stdout.split("\n") if p.strip()]
            self.assertEqual(conflicts, ["workflow/inventories/sri/MANIFEST.jsonl"])
            self.assertEqual([p for p in conflicts if p not in mod.GENERATED], [])


class TestGeneratorFailureBlocksPush(unittest.TestCase):
    """A generator that runs and fails must stop the repair before commit and push."""

    def test_generators_are_declared_in_run_order(self):
        mod = load_module()
        self.assertEqual(mod.GENERATORS, ("regen_indexes.py", "build_sri.py"))

    def test_failure_path_returns_before_commit_and_push(self):
        source = SCRIPT.read_text(encoding="utf-8")
        marker = "REFUSED: {name} failed"
        self.assertIn(
            marker.replace("{name}", "{name}"),
            source,
            "the generator-failure refusal message must exist",
        )
        # The refusal must return before the commit and the push, not merely print.
        fail_at = source.index("failed (exit")
        commit_at = source.index('"chore(inventories): regenerate against main"')
        push_at = source.rindex('git("push", "-q", "origin", branch')
        self.assertLess(fail_at, commit_at, "refusal must precede the regenerate commit")
        self.assertLess(fail_at, push_at, "refusal must precede the push")
        tail = source[fail_at:commit_at]
        self.assertIn("return 1", tail, "the failure path must return non-zero, not fall through")

    def test_no_unscoped_workflow_sweep_remains(self):
        """The one source assertion worth keeping: the blanket sweep must not come back.

        `git add -A workflow/` committed whatever else the caller had under workflow/.
        Its ABSENCE cannot be observed behaviourally without a fixture that happens to
        carry unrelated changes, so it is asserted here. What the staging DOES is covered
        by TestRegenerationStateTransitions against real repos — asserting the presence of
        a source string is precisely how the two state defects went unnoticed.
        """
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn('git("add", "-A", "workflow/"', source,
                         "the unscoped sweep commits files this tool does not own")

    def _repair_repo(self, tmp: Path, generator: str) -> tuple[object, Path, str]:
        wd = tmp / "r"
        wd.mkdir()
        run(wd, "git", "init", "-q", "-b", "main")
        run(wd, "git", "config", "user.email", "t@t")
        run(wd, "git", "config", "user.name", "t")
        output = wd / "workflow/inventories/sri/INDEX.md"
        output.parent.mkdir(parents=True)
        output.write_text("base\n", encoding="utf-8")
        script = wd / "scripts/build_sri.py"
        script.parent.mkdir()
        script.write_text(generator, encoding="utf-8")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "base")

        run(wd, "git", "checkout", "-q", "-b", "side")
        output.write_text("side\n", encoding="utf-8")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "side")
        side_head = run(wd, "git", "rev-parse", "HEAD").strip()
        run(wd, "git", "update-ref", "refs/remotes/origin/side", side_head)

        run(wd, "git", "checkout", "-q", "main")
        output.write_text("main\n", encoding="utf-8")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "main")
        main_head = run(wd, "git", "rev-parse", "HEAD").strip()
        run(wd, "git", "update-ref", "refs/remotes/origin/main", main_head)
        run(wd, "git", "checkout", "-q", "side")

        mod = load_module()
        mod._CWD = str(wd)
        mod.GENERATORS = ("build_sri.py",)
        mod.GENERATED = (
            "workflow/inventories/sri/INDEX.md",
            "workflow/HARNESS-INDEX-FULL.json",  # optional and absent
        )
        return mod, wd, side_head

    def test_failed_generator_is_not_forgotten_on_retry(self):
        with tempfile.TemporaryDirectory() as td:
            mod, wd, side_head = self._repair_repo(
                Path(td), "import sys\nsys.exit(7)\n"
            )
            self.assertEqual(mod._unconflict_here("side", False, False), 1)
            self.assertEqual(run(wd, "git", "rev-parse", "HEAD").strip(), side_head)
            self.assertEqual(mod._unconflict_here("side", False, False), 1)
            self.assertEqual(run(wd, "git", "rev-parse", "HEAD").strip(), side_head)

    def test_absent_optional_output_does_not_block_staging(self):
        with tempfile.TemporaryDirectory() as td:
            mod, wd, side_head = self._repair_repo(
                Path(td),
                "from pathlib import Path\n"
                "Path('workflow/inventories/sri/INDEX.md').write_text('rebuilt\\n')\n",
            )
            self.assertEqual(mod._unconflict_here("side", False, False), 0)
            self.assertNotEqual(run(wd, "git", "rev-parse", "HEAD").strip(), side_head)
            self.assertEqual(
                (wd / "workflow/inventories/sri/INDEX.md").read_text(encoding="utf-8"),
                "rebuilt\n",
            )
            self.assertEqual(run(wd, "git", "status", "--porcelain"), "")



class TestRegenerationStateTransitions(unittest.TestCase):
    """Behavioural witnesses for the two state defects ASTRA reproduced on #3511.

    These build real repos with a real remote and run the real entry point. The earlier
    tests for this change asserted the ORDER OF STATEMENTS IN THE SOURCE, which is why
    they passed while both defects were live: source order says nothing about what happens
    on the second invocation, or about a git command whose exit code is discarded.
    """

    def _fixture(self, tmp: Path, generator_body: str, generated=("workflow/GEN.txt",)):
        remote = tmp / "remote.git"
        run(tmp, "git", "init", "-q", "--bare", str(remote))
        wd = tmp / "wd"
        run(tmp, "git", "clone", "-q", str(remote), str(wd))
        run(wd, "git", "config", "user.email", "t@t")
        run(wd, "git", "config", "user.name", "t")
        run(wd, "git", "config", "commit.gpgsign", "false")

        (wd / "scripts").mkdir(parents=True, exist_ok=True)
        (wd / "scripts" / "gen.py").write_text(generator_body, encoding="utf-8")
        for rel in generated:
            p = wd / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("stale\n", encoding="utf-8")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "base")
        run(wd, "git", "branch", "-M", "main")
        run(wd, "git", "push", "-q", "-u", "origin", "main")
        return wd

    def _load_bound(self, wd: Path, generated, generators=("gen.py",)):
        mod = load_module()
        mod._CWD = str(wd)
        mod.GENERATED = tuple(generated)
        mod.GENERATORS = tuple(generators)
        return mod

    def test_missing_optional_output_still_commits_what_was_rebuilt(self):
        """Defect 2: an absent allowlisted path made `git add` fail, unchecked.

        The generator succeeds and rewrites GEN.txt, but the allowlist also names a file
        this branch does not have. Pre-fix, `git add -- <both>` failed, nothing was staged,
        no commit was made, and the function still reported success.
        """
        body = (
            "import pathlib\n"
            "p = pathlib.Path('workflow/GEN.txt')\n"
            "p.parent.mkdir(parents=True, exist_ok=True)\n"
            "p.write_text('rebuilt\\n', encoding='utf-8')\n"
        )
        with tempfile.TemporaryDirectory() as td:
            wd = self._fixture(Path(td), body)
            mod = self._load_bound(
                wd, ("workflow/GEN.txt", "workflow/NOT-ON-THIS-BRANCH.json")
            )
            before = run(wd, "git", "rev-parse", "HEAD").strip()
            rc = mod.regenerate_and_commit()
            after = run(wd, "git", "rev-parse", "HEAD").strip()

            self.assertEqual(rc, 0, "a successful rebuild must not report refusal")
            self.assertNotEqual(
                before, after,
                "the rebuilt output MUST be committed; a missing optional allowlist entry "
                "must not silently skip the commit while returning success",
            )
            committed = run(wd, "git", "show", "HEAD:workflow/GEN.txt")
            self.assertEqual(committed.strip(), "rebuilt")

    def test_generator_failure_refuses_and_leaves_nothing_committed(self):
        body = "import sys\nsys.exit(7)\n"
        with tempfile.TemporaryDirectory() as td:
            wd = self._fixture(Path(td), body)
            mod = self._load_bound(wd, ("workflow/GEN.txt",))
            before = run(wd, "git", "rev-parse", "HEAD").strip()
            rc = mod.regenerate_and_commit()
            after = run(wd, "git", "rev-parse", "HEAD").strip()
            self.assertEqual(rc, 1, "a failing generator must refuse")
            self.assertEqual(before, after, "nothing may be committed on the failure path")

    def test_retry_after_generator_failure_regenerates_instead_of_pushing_stale(self):
        """Defect 1: the retry took the merges-clean path and published unregenerated output.

        First run: the generator fails, so the tool refuses -- but the merge resolution is
        already committed. Second run: the merge probe is clean and local is ahead of the
        remote, so control reaches the 'push the existing resolution' path. Pre-fix that
        path pushed without regenerating and returned 0.
        """
        failing = "import sys\nsys.exit(7)\n"
        working = (
            "import pathlib\n"
            "p = pathlib.Path('workflow/GEN.txt')\n"
            "p.parent.mkdir(parents=True, exist_ok=True)\n"
            "p.write_text('rebuilt-on-retry\\n', encoding='utf-8')\n"
        )
        with tempfile.TemporaryDirectory() as td:
            wd = self._fixture(Path(td), failing)

            # A conflicting change on main and on the branch, confined to the allowlist.
            run(wd, "git", "checkout", "-q", "-b", "side")
            (wd / "workflow" / "GEN.txt").write_text("side\n", encoding="utf-8")
            run(wd, "git", "commit", "-qam", "side")
            run(wd, "git", "push", "-q", "-u", "origin", "side")

            run(wd, "git", "checkout", "-q", "main")
            (wd / "workflow" / "GEN.txt").write_text("main\n", encoding="utf-8")
            run(wd, "git", "commit", "-qam", "main")
            run(wd, "git", "push", "-q", "origin", "main")
            run(wd, "git", "checkout", "-q", "side")
            run(wd, "git", "fetch", "-q", "origin")

            mod = self._load_bound(wd, ("workflow/GEN.txt",))
            first = mod.unconflict_one("side", dry_run=False, push=False)
            self.assertEqual(first, 1, "the failing generator must refuse on the first run")

            # Repair the generator and retry, exactly as an operator would.
            (wd / "scripts" / "gen.py").write_text(working, encoding="utf-8")
            run(wd, "git", "commit", "-qam", "fix generator")

            second = mod.unconflict_one("side", dry_run=False, push=False)
            self.assertEqual(second, 0, "the retry should complete once the generator works")
            self.assertEqual(
                run(wd, "git", "show", "HEAD:workflow/GEN.txt").strip(),
                "rebuilt-on-retry",
                "the retry MUST regenerate; publishing the unregenerated layer and "
                "reporting success is the defect this test exists for",
            )


class TestHistoryDerivedFreshness(unittest.TestCase):
    """Witness for the defect ASTRA found on #3514.

    The generators are HISTORY-DERIVED: build_sri.py's first_adds() walks
    `git log --diff-filter=A` over HEAD, and registers/TIMELINE.md is built from it. When
    the merge was staged but NOT committed, HEAD did not contain the merged commits, so
    the register was rebuilt against the wrong history and the tool still returned 0.

    The fixture below reproduces that exactly: its generator writes the COMMIT COUNT
    reachable from HEAD, which differs before and after the merge commit.
    """

    # Writes whether the MERGE is present in the committed history. A commit count would
    # also expose the defect but shifts by one when the regeneration itself commits, so it
    # measures bookkeeping rather than the property under test.
    HISTORY_GEN = (
        "import pathlib, subprocess\n"
        "rc = subprocess.run(['git', 'merge-base', '--is-ancestor',\n"
        "                     'origin/main', 'HEAD']).returncode\n"
        "p = pathlib.Path('workflow/GEN.txt')\n"
        "p.parent.mkdir(parents=True, exist_ok=True)\n"
        "p.write_text(('contains-main' if rc == 0 else 'missing-main') + chr(10),\n"
        "             encoding='utf-8')\n"
    )

    def _fixture(self, tmp: Path):
        remote = tmp / "remote.git"
        run(tmp, "git", "init", "-q", "--bare", str(remote))
        wd = tmp / "wd"
        run(tmp, "git", "clone", "-q", str(remote), str(wd))
        run(wd, "git", "config", "user.email", "t@t")
        run(wd, "git", "config", "user.name", "t")
        run(wd, "git", "config", "commit.gpgsign", "false")
        (wd / "scripts").mkdir(parents=True, exist_ok=True)
        (wd / "scripts" / "gen.py").write_text(self.HISTORY_GEN, encoding="utf-8")
        gen = wd / "workflow" / "GEN.txt"
        gen.parent.mkdir(parents=True, exist_ok=True)
        gen.write_text("0\n", encoding="utf-8")
        run(wd, "git", "add", "-A")
        run(wd, "git", "commit", "-q", "-m", "base")
        run(wd, "git", "branch", "-M", "main")
        run(wd, "git", "push", "-q", "-u", "origin", "main")
        return wd

    def test_history_derived_output_is_generated_against_the_merged_history(self):
        with tempfile.TemporaryDirectory() as td:
            wd = self._fixture(Path(td))

            run(wd, "git", "checkout", "-q", "-b", "side")
            (wd / "workflow" / "GEN.txt").write_text("side\n", encoding="utf-8")
            run(wd, "git", "commit", "-qam", "side")
            run(wd, "git", "push", "-q", "-u", "origin", "side")

            run(wd, "git", "checkout", "-q", "main")
            (wd / "workflow" / "GEN.txt").write_text("main\n", encoding="utf-8")
            run(wd, "git", "commit", "-qam", "main")
            run(wd, "git", "push", "-q", "origin", "main")
            run(wd, "git", "checkout", "-q", "side")
            run(wd, "git", "fetch", "-q", "origin")

            mod = load_module()
            mod._CWD = str(wd)
            mod.GENERATED = ("workflow/GEN.txt",)
            mod.GENERATORS = ("gen.py",)

            rc = mod.unconflict_one("side", dry_run=False, push=False)
            self.assertEqual(rc, 0, "the repair should complete")

            committed = run(wd, "git", "show", "HEAD:workflow/GEN.txt").strip()
            self.assertEqual(
                committed, "contains-main",
                "the history-derived output must be generated against the history that is "
                "COMMITTED. Regenerating while the merge is only staged makes the generator "
                "read a HEAD without it, and the tool then reports success on stale "
                "content -- the defect ASTRA found on #3514.",
            )


class TestFreshnessGuard(unittest.TestCase):
    """The tool must ask whether its own output is correct, not assume it."""

    def test_absent_checker_is_not_treated_as_stale(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            mod._CWD = td
            self.assertFalse(
                mod.generated_content_is_stale(),
                "a branch without the checker must not be refused on a condition it "
                "cannot clear",
            )

    def test_checker_failure_is_reported_as_stale(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "scripts").mkdir()
            (root / "scripts" / "build_sri.py").write_text(
                "import sys\nprint('SRI_CHECK CONTENT DRIFT: registers/TIMELINE.md differs')\n"
                "print('SRI_CHECK FAIL: 1 file(s) differ in content')\nsys.exit(1)\n",
                encoding="utf-8",
            )
            mod._CWD = str(root)
            self.assertTrue(mod.generated_content_is_stale())

    def test_clean_checker_is_not_stale(self):
        mod = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "scripts").mkdir()
            (root / "scripts" / "build_sri.py").write_text(
                "print('SRI_CHECK OK (12 file(s) stale-stamp only)')\n", encoding="utf-8")
            mod._CWD = str(root)
            self.assertFalse(mod.generated_content_is_stale())

if __name__ == "__main__":
    unittest.main()
