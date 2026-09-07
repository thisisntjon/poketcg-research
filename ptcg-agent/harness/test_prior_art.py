"""Tests for scripts/prior_art.py.

Law 21 shape: a search tool that returns rows for everything is as useless as one that
returns nothing, so the negative control matters as much as the positive ones. Field
fact 2.4 -- before believing a null result, prove the mechanism can fire -- is why the
known-answer cases below assert on SPECIFIC banked artifacts rather than on hit counts.

The known-answer fixtures are the two artifacts MASTER rediscovered by hand on
2026-09-02 after they had sat committed and unrouted for six weeks. If this tool cannot
find them, it does not solve the problem it was built for.
"""
from __future__ import annotations

import subprocess
import sys
import time
import unittest
from pathlib import Path

# This suite lives under ptcg-agent/harness/ so scripts/ci_discover_suites.py runs it by
# existence (#2253) -- registering it in ci.yml instead would edit the one shared anchor
# every registering PR touches. The module under test lives in scripts/.
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import prior_art  # noqa: E402

LETHAL_AUDIT = "ptcg-agent/experiments/analysis/2026-07-22-lethal-suite-audit-5080.json"
POSITION_SUITE = "ptcg-agent/experiments/analysis/2026-07-22-position-suite-v1-5080.json"


def paths(rows) -> list[str]:
    return [r["path"] for r in rows]


class KnownAnswers(unittest.TestCase):
    """The mechanism must fire on artifacts we KNOW are banked."""

    def test_finds_the_lethal_audit_that_was_rediscovered_by_hand(self):
        rows, meta = prior_art.search("lethal trigger", limit=5)
        self.assertIn(LETHAL_AUDIT, paths(rows),
                      "the 2026-07-22 lethal audit must rank in the top 5 for 'lethal trigger'")
        self.assertGreater(meta["total_hits"], 0)

    def test_finds_the_position_suite(self):
        rows, _ = prior_art.search("position suite", limit=5)
        self.assertIn(POSITION_SUITE, paths(rows))

    def test_filename_hit_outranks_a_body_mention(self):
        """A file NAMED for the query beats one that merely mentions it in passing."""
        rows, _ = prior_art.search("position suite", limit=10)
        self.assertTrue(rows, "expected hits")
        top = rows[0]["path"].lower()
        self.assertIn("position", top)
        self.assertIn("suite", top)

    def test_coverage_matters_but_no_longer_strictly_dominates(self):
        """Superseded the strict "ordered by terms_matched" assertion, deliberately.

        That assertion encoded the pre-IDF model where score was `matched*100 + weights`,
        which is exactly what flattened every ranking to the same maximum and let the
        aggregators win. Under IDF a single RARE term can and should outrank two common
        ones, so strict monotonicity in terms_matched is now the wrong invariant. What
        must still hold: the top hit covers the query well.
        """
        rows, _ = prior_art.search("lethal trigger", limit=25)
        self.assertGreaterEqual(rows[0]["terms_matched"], 2)
        top5 = [r["terms_matched"] for r in rows[:5]]
        self.assertGreaterEqual(sum(top5) / len(top5), 1.5,
                                "top hits should still cover most query terms")


class CatalogTitlesAreNotTrustedBlindly(unittest.TestCase):
    """Found by running against SKYNET's real ARTIFACT-CATALOG (#3154).

    The catalog derives a title from the first line of a file, which for a JSON artifact
    is "{" or whichever key sorted first. Printing that is worse than the schema we can
    extract ourselves, so a useless catalog title must fall through.
    """

    def test_punctuation_titles_are_rejected(self):
        for bad in ("{", "[", '{"games": [', "  {  "):
            self.assertTrue(prior_art._is_useless_title(bad), f"{bad!r} should be rejected")

    def test_real_titles_are_kept(self):
        for good in ("Test-position suite v1 - fixed-state baseline",
                     "R2 lethal resolver - fixed-position audit",
                     "ptcg.lethal_suite_audit/v1"):
            self.assertFalse(prior_art._is_useless_title(good), f"{good!r} should be kept")

    def test_json_artifact_still_describes_itself_by_schema(self):
        """The lethal audit must not render as '{' whether or not a catalog exists."""
        _, title, _ = prior_art.describe(LETHAL_AUDIT, {})
        self.assertNotIn(title.strip()[:1], "{[")
        self.assertIn("lethal", title.lower())

    def test_a_useless_catalog_title_falls_through_to_the_file(self):
        fake = {LETHAL_AUDIT: {"title": "{", "first_commit": "2026-07-22", "state_hints": []}}
        _, title, _ = prior_art.describe(LETHAL_AUDIT, fake)
        self.assertNotEqual(title.strip(), "{")


class RankingDiscriminates(unittest.TestCase):
    """SKYNET's 2026-09-02T10:05Z acceptance test: 2 of 5 named repeats, 0 of 2 real ones.

    Cause was named and reproduced four times: no length normalisation, so the long
    aggregators (ATTEMPTS-LEDGER, DECISIONS) contained every term and topped every query
    at the same maximum score -- "listing, not ranking". These tests are those cases.
    """

    AGGREGATORS = ("workflow/ATTEMPTS-LEDGER.md", "workflow/DECISIONS.md")

    def test_aggregators_do_not_top_an_unrelated_query(self):
        for q in ("tempo verb attach bias", "energy option discrimination deck",
                  "shallow clone timestamp fingerprint"):
            rows, _ = prior_art.search(q, limit=3)
            top = paths(rows)
            for agg in self.AGGREGATORS:
                self.assertNotIn(agg, top, f"{agg} still tops {q!r}")

    def test_finds_the_tempo_verb_package_skynet_found_by_hand(self):
        """The miss that cost two hours: 'tempo-verb' is in this file's TITLE."""
        rows, _ = prior_art.search("tempo verb attach bias", limit=5)
        self.assertIn("workflow/research/k1-batch1/BATCH1-MANIFEST.md", paths(rows))

    def test_bulk_data_does_not_outrank_findings(self):
        """A 610 KB replay dump mentions every term in the game. It is not prior art."""
        rows, _ = prior_art.search("energy option discrimination deck", limit=5)
        for p in paths(rows):
            self.assertNotIn("replays_utf8", p, f"bulk replay dump ranked: {p}")

    def test_scores_separate_rather_than_flatten(self):
        """1,963 hits at a flat 205 tells a seat nothing about whether to trust the list."""
        rows, _ = prior_art.search("seat control", limit=5)
        self.assertGreaterEqual(len(rows), 3)
        scores = [r["score"] for r in rows]
        self.assertGreater(scores[0], scores[-1],
                           f"top-5 scores are flat: {scores}")

    def test_a_rare_term_outweighs_a_ubiquitous_one(self):
        """IDF: a term in 3,000 files carries no information; one in 5 files is the answer."""
        rows, _ = prior_art.search("lethal trigger", limit=5)
        self.assertTrue(any("lethal" in p.lower() for p in paths(rows)))


class CodeLiveness(unittest.TestCase):
    """SKYNET's 08:25Z requirement: a ranked list LOOKS like an answer.

    `tv-attach_bias/main.py` "looked like a ready patch for two hours". Its project-local
    imports resolve to nothing in the current agent -- it is from an older architecture.
    A two-second import check says so.
    """

    STALE_FILE = "workflow/research/k1-batch1/tv-attach_bias/main.py"

    def test_the_two_hour_candidate_is_reported_stale(self):
        verdict, missing = prior_art.code_liveness(self.STALE_FILE)
        self.assertEqual(verdict, "STALE")
        self.assertGreaterEqual(len(missing), 5)
        for expected in ("policy_features", "strategic_policy", "matchup_router"):
            self.assertIn(expected, missing)

    def test_engine_import_does_not_produce_a_false_stale(self):
        """`cg` is the Pokemon engine: git-ignored by policy, present at runtime.

        Before the RUNTIME_MODULES allowlist this called r2_verify.py STALE -- flagging
        our most important agent code on an import that is SUPPOSED to be absent from the
        tree. A checker that cries wolf on core code is worse than no checker.
        """
        verdict, missing = prior_art.code_liveness("ptcg-agent/agent/r2_verify.py")
        self.assertNotEqual(verdict, "STALE", f"false STALE on engine import: {missing}")

    def test_live_agent_code_reports_live_or_abstains(self):
        for path in ("ptcg-agent/agent/search.py", "ptcg-agent/agent/r2_lethal.py"):
            verdict, missing = prior_art.code_liveness(path)
            self.assertIn(verdict, ("LIVE", ""), f"{path} -> {verdict} {missing}")

    def test_non_python_files_are_not_judged(self):
        for path in ("workflow/research/k1-batch1/BATCH1-MANIFEST.md",
                     "workflow/ATTEMPTS-LEDGER.md"):
            self.assertEqual(prior_art.code_liveness(path), ("", []))

    def test_missing_file_does_not_raise(self):
        self.assertEqual(prior_art.code_liveness("no/such/file_xyz.py"), ("", []))

    def test_search_rows_carry_the_verdict(self):
        rows, _ = prior_art.search("tempo verb attach bias", limit=5)
        hit = [r for r in rows if r["path"] == self.STALE_FILE]
        self.assertTrue(hit, "the stale candidate should still rank")
        self.assertEqual(hit[0]["code"], "STALE")
        self.assertTrue(hit[0]["missing_imports"])


class NegativeControls(unittest.TestCase):
    """Prove it can report ABSENCE. A tool that always finds something is a bad tool."""

    def test_nonsense_query_returns_nothing(self):
        rows, meta = prior_art.search("zzqqxx_not_a_real_token_9182 zzwwvv_also_fake_4471")
        self.assertEqual(rows, [], "a genuinely novel query must return NO prior art")
        self.assertEqual(meta["total_hits"], 0)

    def test_stopwords_only_is_refused_not_answered(self):
        rows, meta = prior_art.search("the a of and is")
        self.assertEqual(rows, [])
        self.assertEqual(meta["terms"], [],
                         "stopword-only queries carry no signal and must not be run")

    def test_short_tokens_are_dropped(self):
        _, meta = prior_art.search("ab cd")
        self.assertEqual(meta["terms"], [])


class Contract(unittest.TestCase):
    def test_runs_without_the_catalog(self):
        """Leg C must not be blocked on SKYNET's catalog PR landing."""
        rows, meta = prior_art.search("lethal trigger", limit=3)
        self.assertIsInstance(meta["catalog"], bool)
        self.assertTrue(rows, "must work against the tracked tree when catalog is absent")

    def test_fast_enough_to_be_mandatory(self):
        """If the query step is slow, seats will route around it."""
        started = time.time()
        prior_art.search("seat control", limit=10)
        self.assertLess(time.time() - started, 5.0)

    def test_rows_carry_the_fields_the_dispatch_asked_for(self):
        rows, _ = prior_art.search("position suite", limit=3)
        for row in rows:
            for key in ("path", "date", "title", "state", "score"):
                self.assertIn(key, row)

    def test_cli_exits_zero_and_prints_the_prior_art_line(self):
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "prior_art.py"), "position suite",
             "--limit", "3"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("PRIOR_ART:", out.stdout)

    def test_json_mode_is_parseable(self):
        import json
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "prior_art.py"), "lethal trigger",
             "--limit", "2", "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        payload = json.loads(out.stdout)
        self.assertEqual(payload["query"], "lethal trigger")
        self.assertIn("rows", payload)


if __name__ == "__main__":
    unittest.main()
