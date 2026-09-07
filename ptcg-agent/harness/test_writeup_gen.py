"""Inventory Phase 2 fixtures: scripts/writeup_gen.py (the records-generated appendix).

Properties (Jon 2026-09-05: appendix allowed; no agent-authored thesis; ASTRA audit: product card
must describe the SUBMITTED product; reviewer: timelines derived at run time, NO_RECORD explicit):
  - deterministic; the product card names the submitted product's sha, never the experimental
    Parent's; the thesis, final number, deck concept and figures are NO_RECORD lines, never text;
  - coverage lines are printed per section; the retraction section parses every register row;
  - check-claim marks a retracted number RETRACTED; the tool timeline comes from git.
ASTRA #3455 CHANGES REQUIRED (2026-09-05), five independent counterexamples, each a fixture here:
  1. check-claim never adjudicates: an OPEN node renders NAMED_BY(..:OPEN), never SUPPORTED; a
     number that is only a substring of a larger number is UNBOUND;
  2. --check compares CONTENT: altered JSON keeping its digest, and a replaced Markdown, both DRIFT;
  3. S0 coverage is verified/required fields; with IDENTITY.json absent it is 0/5 + NO_RECORD;
  4. the PRODUCT-PASSPORT is a separate record, never joined into the submission card;
  5. the full tool-event list is persisted in APPENDIX.json (`tool_events`).
On pre-fix source fixtures 1-5 fail. Discovered by ci_discover_suites.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import writeup_gen as wg  # noqa: E402
import retraction_register as rr  # noqa: E402


class Appendix(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = wg.build()
        cls.md = wg.render(cls.doc)
        cls.by_id = {s["id"]: s for s in cls.doc["sections"]}

    def test_deterministic(self) -> None:
        self.assertEqual(self.doc["digest"], wg.build()["digest"])

    def test_product_card_is_the_submitted_product(self) -> None:
        s0 = self.by_id["S0"]
        body = "\n".join(s0["body"])
        ident = json.loads(wg.IDENTITY.read_text(encoding="utf-8"))
        live = ident["roles"]["submitted_product"]["live_ladder"]
        self.assertIn(live["main_py_sha256"], body)
        parent = ident["roles"]["experimental_parent"]["repo_tuple"]["ptcg-agent/agent/main.py"]["sha256"]
        self.assertIn("NOT the submitted product", body)
        self.assertNotEqual(live["main_py_sha256"], parent)

    def test_no_record_lines_where_nothing_exists(self) -> None:
        for sid in ("S1", "S6", "S7", "S10"):
            self.assertTrue(self.by_id[sid]["no_record"], sid)
        self.assertEqual(self.by_id["S1"]["body"], [])  # no invented thesis text

    def test_every_section_has_a_coverage_line(self) -> None:
        for s in self.doc["sections"]:
            self.assertTrue(s["coverage"], s["id"])
            self.assertIn(f"*coverage: {s['coverage']}*", self.md)

    def test_retractions_fully_parsed(self) -> None:
        values = [r for r in rr.parse() if r.section == "values"]
        body = "\n".join(self.by_id["S9"]["body"])
        for v in values:
            for n in v.numbers[:1]:
                self.assertIn(n, body)

    def test_check_claim_marks_retracted(self) -> None:
        self.assertEqual(wg.check_claim("9.35", wg.map_nodes()), "RETRACTED")
        self.assertTrue(wg.check_claim("7.82", wg.map_nodes()).startswith("NOT_RETRACTED"))

    def test_tool_timeline_comes_from_git(self) -> None:
        events = wg.tool_timeline()
        if wg.tool_history_complete():
            self.assertTrue(events)
            self.assertTrue(all(len(e["commit"]) >= 7 and e["date"][:2] == "20" for e in events))
            # PR attribution is optional in real history; the controlled fixture tests parsing.
            self.assertTrue(all(e["pr"] is None or isinstance(e["pr"], int) for e in events))
        else:
            self.assertEqual(events, [])
            self.assertEqual(self.doc["tool_history_status"], "UNKNOWN_HISTORY")

    # ---- ASTRA #3455 counterexamples
    def test_check_claim_never_adjudicates(self) -> None:
        nodes = [{"id": "N1", "status": "OPEN", "text": "screen +4.10pp, unread"},
                 {"id": "N2", "status": "CONFIRMED", "text": "the 14.10pp figure is elsewhere"}]
        v = wg.check_claim("4.10", nodes)
        self.assertNotIn("SUPPORTED", v)
        self.assertIn("NAMED_BY(N1:OPEN)", v)          # the node's own word, not a promotion
        self.assertNotIn("N2", v)                       # 4.10 inside 14.10 is not a match
        self.assertEqual(wg.check_claim("4.1", [nodes[1]]), "NOT_RETRACTED, UNBOUND")
        self.assertNotIn("SUPPORTED", self.md)          # the rendered appendix never says it

    def test_check_detects_altered_outputs(self) -> None:
        saved = (wg.OUT_JSON, wg.OUT_MD)
        try:
            with tempfile.TemporaryDirectory() as td:
                wg.OUT_JSON, wg.OUT_MD = Path(td) / "A.json", Path(td) / "A.md"
                self.assertEqual(wg.main([]), 0)
                self.assertEqual(wg.main(["--check"]), 0)
                # altered JSON that keeps its digest field
                d = json.loads(wg.OUT_JSON.read_text(encoding="utf-8"))
                d["sections"][0]["body"].append("an inserted sentence")
                wg.OUT_JSON.write_text(json.dumps(d), encoding="utf-8")
                self.assertEqual(wg.main(["--check"]), 1)
                wg.main([])
                self.assertEqual(wg.main(["--check"]), 0)
                # replaced Markdown, JSON intact
                wg.OUT_MD.write_text("# a different document\n", encoding="utf-8")
                self.assertEqual(wg.main(["--check"]), 1)
                # missing Markdown
                wg.OUT_MD.unlink()
                self.assertEqual(wg.main(["--check"]), 1)
                # ASTRA delta-2339: a stored JSON that is not an object ([] / null / 0) must refuse,
                # never pass as "nothing to compare"
                wg.main([])
                for shape in ("[]", "null", "0"):
                    wg.OUT_JSON.write_text(shape, encoding="utf-8")
                    self.assertEqual(wg.main(["--check"]), 1, shape)
        finally:
            wg.OUT_JSON, wg.OUT_MD = saved

    def test_s0_coverage_is_a_fraction_and_absent_identity_is_no_record(self) -> None:
        self.assertRegex(self.by_id["S0"]["coverage"], r"^\d/5 required fields present")
        self.assertNotIn("100%", self.by_id["S0"]["coverage"])
        saved = wg.IDENTITY
        try:
            wg.IDENTITY = Path(tempfile.gettempdir()) / "no-such-IDENTITY.json"
            s0 = {s["id"]: s for s in wg.build()["sections"]}["S0"]
            self.assertTrue(s0["coverage"].startswith("0/5"))
            self.assertIn("FILE ABSENT", s0["coverage"])
            self.assertTrue(any("IDENTITY.json absent" in nr for nr in s0["no_record"]))
            self.assertEqual(s0["body"], [])
        finally:
            wg.IDENTITY = saved

    def test_passport_is_not_joined_into_the_submission(self) -> None:
        body = self.by_id["S0"]["body"]
        joined = [ln for ln in body if "passport" in ln.lower()]
        self.assertTrue(joined)
        self.assertTrue(all("NOT joined" in ln for ln in joined))
        sha_line = [ln for ln in body if "main.py sha256" in ln][0]
        self.assertNotIn("passport", sha_line.lower())

    def test_full_tool_events_persisted(self) -> None:
        self.assertEqual(len(self.doc["tool_events"]), len(wg.tool_timeline()))
        self.assertIn("tool_events", self.by_id["S8"]["coverage"])


class TimelineHistory(unittest.TestCase):
    def test_complete_and_truncated_history_keep_distinct_meanings(self):
        saved = wg.REPO
        try:
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                def git(*args):
                    return subprocess.check_output(["git", *args], cwd=root,
                                                   stderr=subprocess.STDOUT, text=True).strip()
                git("init", "-q", "-b", "main")
                git("config", "user.name", "Fixture")
                git("config", "user.email", "fixture@example.invalid")
                (root / "scripts").mkdir()
                (root / "scripts/tool.py").write_text("pass\n", encoding="utf-8")
                git("add", ".")
                git("commit", "-qm", "original tool (#123)")
                original = git("rev-parse", "HEAD")
                (root / "note.md").write_text("later note\n", encoding="utf-8")
                git("add", ".")
                git("commit", "-qm", "unrelated boundary")
                boundary = git("rev-parse", "HEAD")
                git("update-ref", "refs/remotes/origin/main", boundary)
                wg.REPO = root
                events = wg.tool_timeline()
                self.assertEqual(len(events), 1)
                self.assertTrue(original.startswith(events[0]["commit"]))
                self.assertEqual(events[0]["pr"], 123)
                # A resolvable tip and shallow=false do not prove ancestors are readable.
                parent_object = root / ".git/objects" / original[:2] / original[2:]
                parked_object = root / "parked-parent"
                parent_object.rename(parked_object)
                try:
                    self.assertFalse(wg.tool_history_complete())
                    self.assertEqual(wg.tool_timeline(), [])
                    broken = wg.build()
                    self.assertEqual(broken["tool_history_status"], "UNKNOWN_HISTORY")
                    self.assertTrue(next(s for s in broken["sections"] if s["id"] == "S8")["no_record"])
                finally:
                    parked_object.rename(parent_object)
                (root / ".git/shallow").write_bytes((boundary + "\n").encode())
                self.assertEqual(wg.tool_timeline(), [])
                doc = wg.build()
                self.assertEqual(doc["tool_history_status"], "UNKNOWN_HISTORY")
                section = next(s for s in doc["sections"] if s["id"] == "S8")
                self.assertTrue(section["no_record"])
                self.assertIn("UNKNOWN_HISTORY", section["coverage"])
                self.assertIn("not evidence of zero tools", section["coverage"])
        finally:
            wg.REPO = saved

    def test_unavailable_git_history_is_unknown(self):
        saved = wg.REPO
        try:
            with tempfile.TemporaryDirectory() as td:
                wg.REPO = Path(td)
                self.assertFalse(wg.tool_history_complete())
                self.assertEqual(wg.tool_timeline(), [])
        finally:
            wg.REPO = saved


if __name__ == "__main__":
    unittest.main(verbosity=2)
