"""Fixtures for scripts/dock.py — the two-way harness dock over the inventory (Jon 2026-09-06).

Properties:
  - `dock in` returns a packet under its byte budget, names the task, carries the do-not-resume
    list and the rules, and lists what it omitted when cut;
  - `dock out` REFUSES a finding that lacks required fields, has no limitations, cites a source
    whose sha256 does not match the bytes at the named commit, or quotes a RETRACTED number;
  - `dock out --dry-run` ACCEPTS a well-formed finding whose source ref is real, without writing;
  - `template` is itself refused (it is a skeleton, not a finding).
On pre-fix source this file fails at import. Discovered by ci_discover_suites.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import dock  # noqa: E402


def real_ref() -> dict:
    """A source ref that is true: RETRACTIONS.md at origin/main with its actual sha256."""
    commit = subprocess.run(["git", "rev-parse", "origin/main"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    path = "workflow/canon/RETRACTIONS.md"
    blob = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=REPO, capture_output=True, text=True, encoding="utf-8").stdout
    return {"path": path, "git_commit": commit, "sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(), "locator": {"line_start": 1, "line_end": 3}}


def good_finding() -> dict:
    t = dock.template()
    t.update({"id": "DOCK-TEST-finding", "question": "does the dock accept a well-formed finding?", "why": "fixture",
              "methodology": "no games; a fixture record with one real source ref", "result": "accepted in dry-run; nothing established about play",
              "learn": "a finding needs sources, hashes and limitations to bank", "limitations": ["fixture only"],
              "reopen_when": "never", "source_refs": [real_ref()], "producer_seat": "SKYNET", "games_run": 0})
    return t


class Dock(unittest.TestCase):
    def test_in_packet_is_bounded_and_names_omissions(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dock.main(["in", "--task", "empty bench intervention reach", "--budget", "3000", "--json"])
        self.assertEqual(rc, 0)
        pkt = json.loads(buf.getvalue())
        self.assertLessEqual(len(json.dumps(pkt, ensure_ascii=False).encode("utf-8")), 3000 + 600)  # omitted-list slack
        self.assertEqual(pkt["task"], "empty bench intervention reach")
        self.assertTrue(pkt["omitted"])                       # a 3 KB budget must cut something
        self.assertIn("games = 0", " ".join(pkt["rules"]))

    def test_in_full_packet_carries_do_not_resume(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            dock.main(["in", "--task", "search evaluator leaf", "--json"])
        pkt = json.loads(buf.getvalue())
        self.assertIn("belief-PIMC", pkt["do_not_resume"])

    def test_out_refuses_template_and_missing_limitations(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "t.json"
            f.write_text(json.dumps(dock.template()), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dock.main(["out", "--finding", str(f), "--dry-run"])
            self.assertEqual(rc, 1)
            self.assertIn("REFUSED", buf.getvalue())
            g = good_finding()
            g["limitations"] = []
            f.write_text(json.dumps(g), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dock.main(["out", "--finding", str(f), "--dry-run"])
            self.assertEqual(rc, 1)
            self.assertIn("limitations", buf.getvalue())

    def test_out_refuses_bad_hash_and_retracted_number(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "t.json"
            g = good_finding()
            g["source_refs"][0]["sha256"] = "0" * 64
            f.write_text(json.dumps(g), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dock.main(["out", "--finding", str(f), "--dry-run"])
            self.assertEqual(rc, 1)
            self.assertIn("sha256 mismatch", buf.getvalue())
            g = good_finding()
            g["result"] = "the combined product gains +9.35pp on the panel"
            f.write_text(json.dumps(g), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dock.main(["out", "--finding", str(f), "--dry-run"])
            self.assertEqual(rc, 1)
            self.assertIn("RETRACTED", buf.getvalue())

    def test_out_accepts_well_formed_finding_in_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "t.json"
            f.write_text(json.dumps(good_finding()), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dock.main(["out", "--finding", str(f), "--dry-run"])
            self.assertEqual(rc, 0, buf.getvalue())
            self.assertIn("DRY-RUN: finding valid", buf.getvalue())
            self.assertFalse((dock.RECORDS / "DOCK-TEST-finding.json").exists())

    def test_ask_returns_ids_and_filters(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dock.main(["ask", "band pool self-similarity strength gate", "--limit", "5"])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        labels = re.findall(r"\[LEARNINGS\.md\] display label (L-\d+)", out)
        self.assertTrue(labels)
        locators = re.findall(
            r"\[LEARNINGS\.md\] display label (L-\d+).*?\n  Register: ([^\n]+?):(\d+) sha256=([0-9a-f]{64})",
            out, re.S)
        self.assertEqual([row[0] for row in locators], labels)
        for label, path, line, digest in locators:
            raw = (REPO / path).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
            self.assertIn(f"| {label} |", raw.decode("utf-8").splitlines()[int(line) - 1])
        self.assertIn("not a persistent record ID", out)
        self.assertIn("nomination", out)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dock.main(["ask", "deck swap probe", "--kind", "dead-end", "--tag", "family:deck", "--limit", "3"])
        self.assertEqual(rc, 0)
        self.assertIn("A7", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
