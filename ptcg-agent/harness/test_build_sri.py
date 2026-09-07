"""Fixtures for scripts/build_sri.py — the generated SRI inventory layer (Jon 2026-09-05).

Properties:
  - deterministic: two builds in one process agree byte for byte;
  - INDEX.md stays a map: <= 150 lines; every A asset in CURATED.json exists on disk;
  - every LEARNINGS / CLAIMS / OPEN row carries provenance (a backticked path + blob or UNTRACKED);
  - every retracted value in the register appears as a RETRACTED claim row (banned from citation);
  - the instruments-that-lied list, the dead-ends A-rows and the graveyard cards are all harvested;
  - a claim's source path is rendered alone inside backticks so validate.py can resolve it;
  - --check reports DRIFT when a generated file is altered.
On pre-fix source this file fails at import. Discovered by ci_discover_suites.
"""
from __future__ import annotations

import json
import os
import re
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import build_sri as bs  # noqa: E402
import retraction_register as rr  # noqa: E402

PROV = re.compile(r"`[^`]+`( L\d+)? \((blob [0-9a-f]{10}|UNTRACKED)\)")


class ClaimQualification(unittest.TestCase):
    def test_path_history_date_does_not_depend_on_walk_order(self):
        rows = ["1788680192", "1788500000"]
        with patch.object(bs, "history_is_complete", return_value=True):
            for ordered in (rows, list(reversed(rows))):
                with patch.object(bs, "sh", return_value="\n".join(ordered)) as query:
                    self.assertEqual(bs.latest_nonmerge_path_date("record.json"), "2026-09-06")
                    self.assertIn("--full-history", query.call_args.args[0])
                    self.assertIn("--no-merges", query.call_args.args[0])
            with patch.object(bs, "sh", return_value=""):
                self.assertEqual(bs.latest_nonmerge_path_date("record.json"), "—")
        with patch.object(bs, "history_is_complete", return_value=False), patch.object(bs, "sh") as query:
            self.assertEqual(bs.latest_nonmerge_path_date("record.json"), bs.UNKNOWN_HISTORY)
            query.assert_not_called()

    def test_qualification_preserves_claim_and_refuses_stale_support(self):
        import hashlib
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "review.md").write_bytes(b"reviewed\nlimits")
            q = dict(target_path="numbers.md", target_line=3, expected_claim="size",
                     expected_value="7pp", evidence_path="review.md",
                     evidence_sha256_lf=hashlib.sha256(b"reviewed\nlimits").hexdigest(),
                     note="Calibration unresolved")
            row = dict(source="`numbers.md` L3 (blob abc)", claim="size", value="7pp",
                       status="RECEIPT-WEAK", method="original method")
            with patch.object(bs, "REPO", root):
                (root / "review.md").write_bytes(b"reviewed\r\nlimits")
                rows = [dict(row)]
                bs.qualify_claims(rows, {"claim_qualifications": [q]}, {"numbers.md": "abc"})
                self.assertEqual("7pp", rows[0]["value"])
                self.assertEqual("RECEIPT-WEAK", rows[0]["status"])
                self.assertIn("Calibration unresolved", rows[0]["method"])
                self.assertIn("review.md", rows[0]["source"])
                with self.assertRaises(ValueError):
                    bs.qualify_claims([dict(row, value="8pp")], {"claim_qualifications": [q]}, {"numbers.md": "abc"})
                (root / "review.md").write_bytes(b"changed")
                with self.assertRaises(ValueError):
                    bs.qualify_claims([dict(row)], {"claim_qualifications": [q]}, {"numbers.md": "abc"})


class Sri(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.out = bs.build()
        cls.cur = json.loads(bs.CURATED.read_text(encoding="utf-8"))

    def test_deterministic(self) -> None:
        again = bs.build()
        for k in self.out:
            if k != "BUILD.json":
                self.assertEqual(self.out[k], again[k], k)

    def test_index_is_a_map(self) -> None:
        self.assertLessEqual(len(self.out["INDEX.md"].splitlines()), 150)
        for f in self.cur["five_things"]:
            self.assertIn(f["path"], self.out["INDEX.md"])
        for d in self.cur["d_do_not_resume"]:
            self.assertIn(d["thing"], self.out["INDEX.md"])

    def test_a_assets_exist_and_are_canonical_A(self) -> None:
        rows = [json.loads(l) for l in self.out["MANIFEST.jsonl"].splitlines()]
        by_path = {r["path"]: r for r in rows}
        for a in self.cur["a_assets"]:
            self.assertTrue((REPO / a["path"]).exists(), a["path"])
            self.assertEqual(by_path[a["path"]]["value"], "A")
            self.assertEqual(by_path[a["path"]]["status"], "canonical")
            self.assertTrue(by_path[a["path"]].get("next_action"))

    def test_every_register_row_has_provenance(self) -> None:
        for reg in ("LEARNINGS.md", "CLAIMS.md", "OPEN.md", "DECISIONS.md"):
            body = self.out[f"registers/{reg}"]
            rows = [l for l in body.splitlines() if l.startswith("| ") and not l.startswith("| #") and not l.startswith("| id") and not l.startswith("| date")]
            self.assertTrue(rows, reg)
            missing = [l[:80] for l in rows if not PROV.search(l)]
            self.assertEqual(missing, [], f"{reg}: rows without provenance")

    def test_retracted_values_are_claim_rows(self) -> None:
        claims = self.out["registers/CLAIMS.md"]
        for v in rr.value_rows():
            for n in v.numbers[:1]:
                self.assertIn(n, claims)
        self.assertGreaterEqual(claims.count("| RETRACTED |"), len(rr.value_rows()))

    def test_learnings_harvest_the_load_bearing_sources(self) -> None:
        learn = self.out["registers/LEARNINGS.md"]
        self.assertIn("## instrument-that-lied", learn)
        self.assertIn("Band pool self-similarity", learn)
        self.assertIn("| A1 |", learn)          # dead-end with scope guard
        self.assertIn("| G01 |", learn)         # graveyard card
        if (REPO / "workflow" / "LESSONS.md").exists():   # ASTRA 2026-09-06: the missing family
            self.assertIn("## lesson (", learn)
            self.assertIn("| LESSON-21 |", learn)
            self.assertIn("became mechanism:", learn)
        self.assertIn("SCOPE GUARD", learn.upper())

    def test_claim_source_path_alone_in_backticks(self) -> None:
        for line in self.out["registers/CLAIMS.md"].splitlines():
            if line.startswith("| c-"):
                for tok in re.findall(r"`([^`]+)`", line):
                    self.assertNotIn("#L", tok, line[:80])

    def test_knowledge_record_pointer_and_full_record(self) -> None:
        """ASTRA CONNECTION_FAIL 2026-09-06 (E065): the navigation row dropped the result and the
        control-label-distribution caveat. The row must be marked a pointer and carry the first
        limitation verbatim; the full register must carry the complete result and every limitation."""
        rec_path = REPO / "workflow" / "knowledge-register" / "records" / "E065.json"
        if not rec_path.exists():
            self.skipTest("E065 record not on this checkout")
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        learn = self.out["registers/LEARNINGS.md"]
        row = next(l for l in learn.splitlines() if l.startswith("| L-") and "| E065 |" in l)
        self.assertIn("POINTER (incomplete by design)", row)
        self.assertIn(rec["limitations"][0][:60], row)
        self.assertIn("KNOWLEDGE-RECORDS.md", row)
        full = self.out["registers/KNOWLEDGE-RECORDS.md"]
        self.assertIn("## E065", full)
        self.assertIn(rec["result"], full)                       # complete result, not a prefix
        for lim in rec["limitations"]:
            self.assertIn(lim, full)                             # every limitation verbatim
        self.assertIn("Different control label distributions", full)
        for s in rec["source_refs"]:
            self.assertIn(s["path"], full)
            self.assertIn(s["git_commit"], full)

    def test_tags_and_retest_queue(self) -> None:
        """Jon 2026-09-06: typed retrieval keys and a generated retest queue."""
        learn = self.out["registers/LEARNINGS.md"]
        self.assertIn("| tags |", learn)
        self.assertIn("family:search", learn)                  # A1/A2 rows carry it
        self.assertIn("instrument:power", learn)               # the underpowered-n rows
        rq = self.out["registers/RETEST-QUEUE.md"]
        self.assertIn("| A1 |", rq)                            # a named reopen condition
        self.assertNotIn("| LIED-1 |", rq)                     # "never as primary instrument" is not a queue item
        self.assertIn("nothing here is authorised", rq)
        self.assertIn("RETEST-QUEUE.md", self.out["INDEX.md"])

    def test_every_catalogued_markdown_surface_is_harvested(self) -> None:
        """Coverage ratchet (Jon 2026-09-05: everything we have done is in the inventory). A markdown
        surface catalogued in MASTER-INVENTORY-INDEX.json that is neither a routing page nor an SRI
        output must be read by the harvest (SRC or SURFACES). On 2026-09-06 there were 22 such holes."""
        cov = bs.surface_coverage()
        self.assertEqual(cov["unharvested_markdown"], [], "catalogued markdown surfaces the harvest does not read")
        self.assertGreaterEqual(cov["harvested"], 35)
        self.assertIn("surface_coverage", json.loads(self.out["BUILD.json"]))

    def test_surface_rows_carry_provenance_and_retraction_marks(self) -> None:
        learn = self.out["registers/LEARNINGS.md"]
        self.assertIn("## surface:loss-modes (", learn)
        self.assertIn("## surface:mu-strategy (", learn)           # prose-only file: heading rows
        self.assertIn("## History and canon surfaces", learn)
        # a surface row that quotes a retracted value is marked, not dropped
        banned = [n for v in rr.value_rows() for n in v.numbers]
        marked = [l for l in learn.splitlines() if l.startswith("| L-") and "QUOTES RETRACTED" in l]
        self.assertTrue(marked, "no surface row carries a retraction mark although history quotes banned values")
        for l in marked:
            self.assertTrue(any(n in l for n in banned), l[:120])
        self.assertIn("surface:", self.out["INDEX.md"])

    def test_timeline_register(self) -> None:
        """Jon 2026-09-05: timelines for when we created tools and why.

        Two worlds, and the register must be honest in both. On a COMPLETE checkout every tool row
        carries a date, a commit and the first commit's subject as the why. On a TRUNCATED one —
        which this repo's CI is, per its own 2026-09-04 diagnostic in ci.yml: shallow at test time
        despite fetch-depth 0 — every path appears to be added at the graft boundary, so the date
        and reason must read UNKNOWN rather than name the boundary commit as the reason a tool
        exists. ROACH's CI failures of 10:35Z and 11:01Z were that wrong attribution, twice, with
        the answer following whatever had most recently landed on main."""
        tl = self.out["registers/TIMELINE.md"]
        self.assertIn("TIMELINE.md", self.out["INDEX.md"])
        whole = bs.history_is_complete()
        self.assertEqual(json.loads(self.out["BUILD.json"])["history_complete"], whole)
        if not whole:
            self.assertIn("TRUNCATED checkout", tl)
            self.assertIn(bs.UNKNOWN_HISTORY, tl)
            marked = [l for l in tl.splitlines() if l.startswith("| ") and "`scripts/build_sri.py`" in l]
            self.assertTrue(marked and all(bs.UNKNOWN_HISTORY in l for l in marked), marked[:1])
            return
        self.assertIn("## 2026-", tl)
        rows = [l for l in tl.splitlines() if l.startswith("| 20")]
        self.assertGreaterEqual(len(rows), 400)
        self.assertTrue(all(re.match(r"\| \d{4}-\d{2}-\d{2} \| (tool|knowledge-record) \| `", l) for l in rows), rows[:2])
        me = next(l for l in rows if "`scripts/build_sri.py`" in l)
        self.assertRegex(me, r"\| [0-9a-f]{7,12} \|")                # commit
        self.assertIn("inventory", me.lower())                        # the why is the commit subject
        self.assertEqual(json.loads(self.out["BUILD.json"])["counts"]["timeline"], len(rows))

    def test_mixed_format_surface_keeps_initiative_bullets(self) -> None:
        """ASTRA 2026-09-06 08:23Z CHANGES_REQUESTED: STRATEGY-ATLAS has 18 table rows AND 26
        initiative bullets (T1..T6, L*, A*, G*: what, USE, LESSON, dates); 'tables else headings'
        dropped all 26. Every initiative must be a row whose body keeps its USE/LESSON text."""
        learn = self.out["registers/LEARNINGS.md"]
        atlas = [l for l in learn.splitlines() if l.startswith("| L-") and "workflow/canon/STRATEGY-ATLAS.md" in l]
        self.assertGreaterEqual(len(atlas), 44, "18 table rows + 26 initiative bullets expected")
        inits = [l for l in atlas if re.search(r"\| [TLAG]\d+ [A-Z]", l)]
        self.assertGreaterEqual(len(inits), 26, [l[:60] for l in inits])
        t3 = next(l for l in inits if "| T3 " in l)
        self.assertIn("LESSON:", t3)                      # the qualification survives, not just the title
        self.assertIn("USE:", t3)
        self.assertRegex(t3, r"STRATEGY-ATLAS\.md` L\d+ \(blob")   # a line locator, not a file pointer
        # mixed format elsewhere: a table-bearing file still yields bullet rows when it has them
        kinds_with_both = 0
        for sid, rel in bs.SURFACES.items():
            rows = [l for l in learn.splitlines() if l.startswith("| L-") and f"`{rel}`" in l]
            if any(re.search(r"` L\d+ ", l) for l in rows) and len(rows) > 0:
                kinds_with_both += 1
        self.assertGreaterEqual(kinds_with_both, 20)

    def test_tombstones_have_two_truthful_states(self) -> None:
        """ASTRA 2026-09-06 08:23Z: a retired file is not 'in place'. Rows whose successor cell begins
        ARCHIVED-COPY-IN-BAG must read REMOVED FROM TREE with the real destination from the row;
        the original supersession rows stay IN PLACE. No row may carry both."""
        tomb = self.out["registers/TOMBSTONES.md"]
        removed = [l for l in tomb.splitlines() if "REMOVED FROM TREE" in l]
        kept = [l for l in tomb.splitlines() if "IN PLACE, marked" in l]
        self.assertGreaterEqual(len(removed), 58)          # #3477's rows at least
        self.assertGreaterEqual(len(kept), 9)
        for l in removed:
            self.assertNotIn("IN PLACE", l)
            self.assertRegex(l, r"REMOVED FROM TREE → `D:/")          # destination read from the row
            self.assertRegex(l, r"\(blob [0-9a-f]{12} at origin/main [0-9a-f]{10}\)")  # git identity kept
        self.assertNotIn("in place (marked)", tomb)        # the old single label is gone

    def test_check_separates_stale_stamp_from_content_drift(self) -> None:
        """2026-09-06: main carried registers whose rows pointed at blobs a merge had replaced, but
        every merge and every midnight also moves the banner's main commit and build date, so the
        old undifferentiated "advisory" line hid real drift among stamp noise. A banner-only
        difference must report and exit 0; an altered register row must exit 1."""
        idx = bs.OUT / "INDEX.md"
        rq = bs.OUT / "registers" / "RETEST-QUEUE.md"
        if not idx.exists() or not rq.exists():
            self.skipTest("layer not written in this checkout")
        # The committed layer on any given checkout may ALREADY carry content drift (main did on
        # 2026-09-06), so asserting on it directly would test the checkout, not the classifier.
        # Snapshot every file, regenerate so the layer matches its sources, assert, restore exactly.
        snapshot = {p: p.read_bytes() for p in bs.OUT.rglob("*") if p.is_file()}
        try:
            bs.main([])
            self.assertEqual(bs.main(["--check"]), 0, "a freshly generated layer must be clean")
            fresh_idx = idx.read_text(encoding="utf-8")
            idx.write_text(re.sub(r"at main [0-9a-f]{12}", "at main 0123456789ab", fresh_idx, count=1),
                           encoding="utf-8", newline="\n")
            self.assertNotEqual(fresh_idx, idx.read_text(encoding="utf-8"), "the banner edit must change the file")
            self.assertEqual(bs.main(["--check"]), 0, "a stale banner must not fail the check")
            idx.write_text(fresh_idx, encoding="utf-8", newline="\n")
            rq.write_text(rq.read_text(encoding="utf-8") + "\n| L-9999 | tampered row |\n",
                          encoding="utf-8", newline="\n")
            self.assertEqual(bs.main(["--check"]), 1, "an altered register row must fail the check")
        finally:
            for p, b in snapshot.items():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b)
            for p in list(bs.OUT.rglob("*")):
                if p.is_file() and p not in snapshot:
                    p.unlink()

    def test_stamp_normalisation_cannot_hide_content_drift(self) -> None:
        """ASTRA 2026-09-06 11:15Z reproduced this: the first version ran ONE regex over the whole
        file, so an ordinary sentence differing only in a date or a main reference normalised equal
        and real drift was reported stamp-only. Its two exact counterexamples must read as CONTENT."""
        ban = "<!-- GENERATED by scripts/build_sri.py from canonical sources on 2026-09-{d} at main {m}. Do not edit; edit the source it cites. -->"
        body = "\n| c-001 | a claim | 1.23 pp |"
        for a, b in [("The run completed on 2026-09-04; result remains unconfirmed.",
                      "The run completed on 2026-09-05; result remains unconfirmed."),
                     ("Evidence was verified at main abcdef1234.",
                      "Evidence was verified at main deadbeef99.")]:
            self.assertFalse(bs.stamp_only_difference("registers/CLAIMS.md", a, b),
                             f"content drift reported as stamp-only: {a!r}")
        # …while a genuine banner-only change stays stamp-only
        self.assertTrue(bs.stamp_only_difference("registers/CLAIMS.md",
                                                 ban.format(d="05", m="aaaaaaaaaaaa") + body,
                                                 ban.format(d="06", m="bbbbbbbbbbbb") + body))
        # a banner change PLUS a row change is content
        self.assertFalse(bs.stamp_only_difference("registers/CLAIMS.md",
                                                  ban.format(d="05", m="aaaaaaaaaaaa") + body,
                                                  ban.format(d="06", m="bbbbbbbbbbbb") + body.replace("1.23", "4.56")))
        # added or removed lines are content, never stamp
        self.assertFalse(bs.stamp_only_difference("registers/CLAIMS.md", "x\ny", "x\ny\nz"))

    def test_classifier_scope_boundaries(self) -> None:
        """ASTRA 2026-09-06 11:33Z, second round, AST-extracted: the per-line rule still forgave a
        JSON-shaped metadata line appearing inside a MARKDOWN register, and forgave a changed
        hex-like token elsewhere on the "Last inventory" line, because it blanked every date/hex on
        a line it had decided to trust. Position is now fixed and only captured values are permitted."""
        ban = "<!-- GENERATED by scripts/build_sri.py from canonical sources on 2026-09-05 at main aaaaaaaaaaaa. Do not edit; edit the source it cites. -->"
        # 1. a JSON-shaped metadata line inside a markdown register is CONTENT, not metadata
        md_a = ban + '\n  "main": "abcdef123456",\n| row |'
        md_b = ban + '\n  "main": "deadbeef9999",\n| row |'
        self.assertFalse(bs.stamp_only_difference("registers/KNOWLEDGE-RECORDS.md", md_a, md_b))
        self.assertFalse(bs.stamp_only_difference("registers/KNOWLEDGE-RECORDS.md",
                                                  ban + '\n  "digest": "aaaa",\n| row |',
                                                  ban + '\n  "digest": "bbbb",\n| row |'))
        # 2. the Last-inventory line: the DATE may move; anything else on it may not
        li = "**Last inventory:** 2026-09-0{d} · **Gate:** PASS — records: {n} | fails: 0 · digest {h}"
        idx_a = ban + "\n\n\n" + li.format(d="5", n="2333", h="abcdef123456")
        self.assertTrue(bs.stamp_only_difference("INDEX.md", idx_a,
                                                 ban + "\n\n\n" + li.format(d="6", n="2333", h="abcdef123456")))
        self.assertFalse(bs.stamp_only_difference("INDEX.md", idx_a,
                                                  ban + "\n\n\n" + li.format(d="6", n="2333", h="deadbeef9999")))
        self.assertFalse(bs.stamp_only_difference("INDEX.md", idx_a,
                                                  ban + "\n\n\n" + li.format(d="5", n="9999", h="abcdef123456")))
        # 3. the same Last-inventory shape in a file that is not INDEX.md is CONTENT
        self.assertFalse(bs.stamp_only_difference("registers/OPEN.md", ban + "\n\n\n" + li.format(d="5", n="2333", h="abcdef123456"),
                                                  ban + "\n\n\n" + li.format(d="6", n="2333", h="abcdef123456")))
        # 4. a banner-shaped line that is NOT line 0 is CONTENT
        self.assertFalse(bs.stamp_only_difference("registers/CLAIMS.md", "| row |\n" + ban,
                                                  "| row |\n" + ban.replace("2026-09-05", "2026-09-06")))
        # 5. ASTRA 11:41Z: the Last-inventory SHAPE in INDEX.md's BODY is content — only the real
        #    header position (index 3, per render_index) may have its date forgiven
        body_a = ban + "\n\n\n" + li.format(d="5", n="2333", h="abcdef123456") + "\n\n## Notes\n" + li.format(d="1", n="1", h="abcdef123456")
        body_b = ban + "\n\n\n" + li.format(d="5", n="2333", h="abcdef123456") + "\n\n## Notes\n" + li.format(d="2", n="1", h="abcdef123456")
        self.assertFalse(bs.stamp_only_difference("INDEX.md", body_a, body_b),
                         "a Last-inventory-shaped line in the BODY must not have its date forgiven")

    def test_history_completeness_requires_an_explicit_false(self) -> None:
        """ASTRA 2026-09-06 11:15Z: the first version returned `sh(...) != "true"`, and sh() returns
        "" on a non-zero exit, so a FAILED git query read as complete history and the register
        printed provenance it could not know. Only a successful explicit "false" means complete."""
        def result(rc: int, out: str):
            return subprocess.CompletedProcess(args=[], returncode=rc, stdout=out, stderr="")
        cases = [(0, "false\n", True), (0, "true\n", False), (0, "\n", False),
                 (1, "", False), (128, "fatal: not a git repository\n", False), (0, "maybe\n", False)]
        for rc, out, expected in cases:
            with patch.object(bs.subprocess, "run", return_value=result(rc, out)), \
                 patch.object(Path, "exists", lambda self: False):
                self.assertEqual(bs.history_is_complete(), expected, f"rc={rc} out={out!r}")

    def test_required_history_refuses_before_reading_or_building(self) -> None:
        with patch.object(bs, "history_is_complete", return_value=False), \
             patch.object(bs, "build") as build:
            self.assertEqual(bs.main(["--check", "--require-complete-history"]), 2)
            build.assert_not_called()

    def test_knowledge_records_use_portable_path_order(self) -> None:
        rows = bs.harvest_learnings({})
        paths = [r["record_path"] for r in rows if r.get("record_path")]
        self.assertGreater(len(paths), 1)
        self.assertEqual(paths, sorted(paths))

    def test_timeline_commit_display_ignores_git_abbrev_config(self) -> None:
        outputs = []
        for width in (7, 12):
            with patch.dict(os.environ, {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.abbrev",
                                         "GIT_CONFIG_VALUE_0": str(width)}):
                outputs.append(bs.first_adds())
        self.assertTrue(outputs[0])
        self.assertEqual(outputs[0], outputs[1])

    def test_tombstones_ignore_ambient_archive_volume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "holding" / "2026-09-06" / "manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text('{"items": ["fixture"]}', encoding="utf-8")
            with patch.object(bs, "ARCHIVE_ROOT", root):
                present = bs.harvest_tombstones({})
            with patch.object(bs, "ARCHIVE_ROOT", root / "absent"):
                absent = bs.harvest_tombstones({})
            self.assertEqual(present, absent)

    def test_required_history_is_check_only(self) -> None:
        with self.assertRaises(SystemExit) as refusal:
            bs.main(["--require-complete-history"])
        self.assertEqual(refusal.exception.code, 2)

    def test_check_detects_drift(self) -> None:
        idx = bs.OUT / "INDEX.md"
        if not idx.exists():
            self.skipTest("layer not written in this checkout")
        original = idx.read_text(encoding="utf-8")
        try:
            idx.write_text(original + "\ntampered\n", encoding="utf-8")
            self.assertEqual(bs.main(["--check"]), 1)
        finally:
            idx.write_text(original, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
