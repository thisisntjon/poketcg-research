"""Behavioral checks for historical research retrieval; no engine or provider."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("research_memory", ROOT / "scripts/research_memory.py")
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


class ResearchMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.write(memory.COMPACT, json.dumps({"rows": [
            {"id": "OLD", "tried": "fallback", "result": "null", "class": "UNKNOWN"}],
            "open_conflicts": ["Two quantities remain unresolved"]}))
        self.write(memory.RETRACTIONS, "# Retractions\nHistorical assertions are not current authority.\n")
        self.path = memory.EXPERIMENTS + "E001-fallback.md"
        self.write(self.path, "## E001: Fallback\n- **Setup**: original method\n"
                   "- **Result**: 2/4 wins\n- **Decision**: historical decision\n"
                   "- **CAVEATS**: no general strength claim; see E002\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, check=True).stdout.decode().strip()

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")

    def commit(self):
        self.git("add", ".")
        self.git("-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-qm", "fixture")

    def invoke(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = memory.main([*args, "--root", str(self.root), "--format", "json"])
        return rc, json.loads(output.getvalue())

    def test_consumer_status_preserves_dated_open_closed_and_unknown_fields(self):
        path = "workflow/inventories/CONSUMER-72H-LEDGER.json"
        doc = {"schema": "ptcg.consumer_72h_ledger/v1", "stamped": "2026-08-15",
               "rule": "Historical consumer allocation, not present execution authority",
               "rows": [{"id": "C72-007", "result": "product_passport", "status": "CLOSED",
                         "owner": "historical-owner", "closed": True, "consumer_path": "passport.json"},
                        {"id": "C72-003", "result": "value_model", "status": "OPEN",
                         "owner": None, "closed": False, "deadline_utc": None}]}
        self.write(path, json.dumps(doc))
        self.commit()
        rc, out = self.invoke("show", "consumer:C72-007")
        self.assertEqual(rc, 0)
        self.assertEqual(out["record"]["knowledge"], doc["rows"][0])
        self.assertEqual(out["record"]["register_context"]["stamped"], "2026-08-15")
        self.assertEqual(out["record"]["source"]["json_pointer"], "/rows/0")
        _, open_row = self.invoke("show", "consumer:C72-003")
        self.assertEqual(open_row["record"]["knowledge"], doc["rows"][1])
        _, found = self.invoke("search", "C72-007", "--limit", "3")
        self.assertEqual(found["matches"][0]["id"], "consumer:C72-007")

    def test_supersession_discovery_retains_same_date_rows_and_corrections(self):
        path = "workflow/canon/SUPERSESSION-REGISTER.md"
        self.write(path, "# Supersessions\nHistorical locations, not restore authorization.\n"
                   "## Retired\n| Date | Old | New | Notes |\n|---|---|---|---|\n"
                   "| 2026-09-06 | `lost-plan.md` | D:/bag/lost-plan.md | restore: oldref; unverified |\n"
                   "| 2026-09-06 | `other-plan.md` | in place | superseded |\n"
                   "| 2026-09-06 | `lost-plan.md` | D:/corrected/lost-plan.md | correction; old location retained as history |\n")
        self.commit()
        rc, found = self.invoke("search", "lost-plan.md", "--limit", "10")
        self.assertEqual(rc, 0)
        self.assertEqual(len(found["matches"]), 2)
        ids = [row["id"] for row in found["matches"]]
        self.assertEqual(len(set(ids)), 2)
        contents = []
        for rid in ids:
            rc, out = self.invoke("show", rid)
            self.assertEqual(rc, 0)
            self.assertEqual(out["record"]["source"]["path"], path)
            content = json.dumps(out["record"])
            self.assertIn("not restore authorization", content)
            contents.append(content)
        self.assertTrue(any("D:/bag/lost-plan.md" in x for x in contents))
        self.assertTrue(any("D:/corrected/lost-plan.md" in x for x in contents))
        _, other = self.invoke("search", "other-plan.md")
        self.assertEqual(len(other["matches"]), 1)

    def test_banked_inbox_text_is_retrievable_without_certifying_or_reading_binary(self):
        path = "workflow/inbox-2026-09/AUDITOR-POST-MORTEM-2026-09-05.md"
        original = "# Natural-root post-mortem\nTwelve comparisons; no established positive.\nHistorical instructions are not permission.\n"
        self.write(path, original)
        self.write("workflow/inbox-2026-09/teamloop.txt", "Old loop instructions; no current authority.\n")
        self.write("workflow/inbox-2026-09/roadmap.docx", "not a text document")
        self.commit()
        rc, hits = self.invoke("search", "AUDITOR-POST-MORTEM-2026-09-05.md")
        self.assertEqual(rc, 0)
        self.assertEqual([r["id"] for r in hits["matches"]], ["inbox:2026-09/AUDITOR-POST-MORTEM-2026-09-05.md"])
        _, out = self.invoke("show", hits["matches"][0]["id"])
        self.assertEqual(out["record"]["source"]["path"], path)
        self.assertEqual(out["record"]["source"]["sha256"], hashlib.sha256(original.encode()).hexdigest())
        self.assertEqual(out["record"]["sections"][0]["text"], original.rstrip("\n"))
        self.assertIn("not semantically certified", out["record"]["basis"])
        _, txt = self.invoke("show", "inbox:2026-09/teamloop.txt")
        self.assertIn("no current authority", txt["record"]["sections"][0]["text"])
        _, coverage = self.invoke("coverage")
        self.assertEqual(coverage["meta"]["inbox_documents"]["text_documents"], 2)
        self.assertEqual(coverage["meta"]["inbox_documents"]["unconsumed_file_types"], {".docx": 1})

    def test_filename_query_requires_complete_basename(self):
        cards = [
            {"id": "A", "title": "Other md document", "sections": [{"text": "runbook restart"}]},
            {"id": "B", "title": "Retired file", "sections": [{"text": "See 01_RESTART_RUNBOOK.md for history"}]},
            {"id": "C", "title": "prefix01_RESTART_RUNBOOK.md.bak", "sections": []},
        ]
        self.assertEqual([c["id"] for c in memory.rank(cards, "01_RESTART_RUNBOOK.md")], ["B"])

    def test_json_root_covers_line_record_but_field_does_not(self):
        source = {"line_start": 1, "line_end": 12}
        self.assertTrue(memory.anchor_covers_record({"locator": {"json_pointer": ""}}, source))
        self.assertFalse(memory.anchor_covers_record({"locator": {"json_pointer": "/result"}}, source))
        self.assertFalse(memory.anchor_covers_record(
            {"locator": {"json_pointer": "/a"}}, {"json_pointer": "/adjacent"}))

    def test_review_json_anchors_reject_ambiguous_nonfinite_and_bad_indices(self):
        path = "evidence/anchor.json"
        for raw, pointer in [('{"a":NaN}', ''), ('{"a":1e400}', ''),
                             ('{"a":1,"a":2}', ''), ('[1,2]', '/-1'),
                             ('[1,2]', '/01'), ('{"a~2":1}', '/a~2')]:
            with self.subTest(raw=raw, pointer=pointer):
                self.write(path, raw)
                self.git("add", path)
                self.git("-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                         "commit", "--allow-empty", "-qm", "anchor case")
                snap = memory.Snapshot(self.root, "HEAD")
                anchor = {"path": path, "git_commit": snap.commit,
                          "sha256": hashlib.sha256(raw.encode()).hexdigest(),
                          "locator": {"json_pointer": pointer}}
                with self.assertRaises(memory.MemoryError):
                    memory.anchor_check(anchor, snap, {})

    def test_filename_query_handles_sentence_punctuation_and_newlines(self):
        cards = [
            {"id": "A", "title": "Evidence", "sections": [{"text": "See receipt.json."}]},
            {"id": "B", "title": "Evidence", "sections": [{"text": "Sources:\nreceipt.json is primary"}]},
            {"id": "C", "title": "Evidence", "sections": [{"text": "receipt.json.bak"}]},
        ]
        self.assertEqual([c["id"] for c in memory.rank(cards, "receipt.json")], ["A", "B"])

    def test_filename_query_can_find_original_source_path(self):
        cards = [{"id": "A", "title": "Historical result", "source": {"path": "workflow/research/receipt.json"}}]
        self.assertEqual([c["id"] for c in memory.rank(cards, "RECEIPT.JSON")], ["A"])
        self.assertEqual(memory.rank(cards, "absent.json"), [])

    def test_exact_numeric_expression_beats_unordered_title_terms(self):
        cards = [
            {"id": "A", "title": "96 unrelated notes and 101 checks", "sections": []},
            {"id": "B", "title": "Loss census", "sections": [
                {"label": "Result", "text": "96/101 unresolved endings are an instrument limitation."}]},
        ]
        self.assertEqual(memory.rank(cards, "96/101")[0]["id"], "B")

    def test_numeric_expression_does_not_match_larger_expression(self):
        cards = [
            {"id": "A", "title": "196/1010 unrelated observations", "sections": []},
            {"id": "B", "title": "Loss census", "sections": [
                {"label": "Result", "text": "96/101 unresolved endings"}]},
        ]
        self.assertEqual([c["id"] for c in memory.rank(cards, "96/101")], ["B"])

    def test_numeric_query_does_not_match_hash_or_larger_number(self):
        cards = [
            {"id": "A", "title": "Unrelated", "knowledge": {"sha256": "ab96cd101ef"}},
            {"id": "B", "title": "196 observations", "sections": []},
            {"id": "C", "title": "Loss census", "sections": [
                {"label": "Result", "text": "96 unresolved endings"}]},
        ]
        self.assertEqual([c["id"] for c in memory.rank(cards, "96")], ["C"])

    def test_source_outline_pages_escaped_paths_without_exposing_values(self):
        self.write("analysis/tree.json", '{"a/b":{"~key":["PRIVATE_VALUE",false]},"end":null}\n')
        self.commit()
        rc, out = self.invoke("source", "analysis/tree.json", "--outline", "--limit", "1")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("catalog_documents", out["meta"])
        outline = out["record"]["json_outline"]
        self.assertEqual(outline["children"], [{"pointer": "/a~1b", "type": "object", "children": 1}])
        self.assertEqual(outline["next_offset"], 1)
        self.assertNotIn("PRIVATE_VALUE", json.dumps(out))
        self.assertNotIn("selected_json", out["record"])
        rc, child = self.invoke("source", "analysis/tree.json", "--outline", "--pointer", "/a~1b/~0key", "--offset", "1")
        self.assertEqual(rc, 0, child)
        self.assertEqual(child["record"]["json_outline"]["children"], [{"pointer": "/a~1b/~0key/1", "type": "boolean", "children": None}])
        self.assertIn("values remain unread", child["record"]["context_scope"])
        self.assertEqual(child["record"]["source"]["json_pointer"], "/a~1b/~0key")

    def test_source_outline_refuses_ambiguous_json_and_mixed_modes(self):
        self.write("analysis/tree.json", '{"x":1,"x":2}\n')
        self.commit()
        for args in [("--outline",), ("--outline", "--pointer", "/x", "--pointer", "/y"), ("--outline", "--lines", "2")]:
            rc, out = self.invoke("source", "analysis/tree.json", *args)
            self.assertEqual(rc, 2, out)

    def test_source_json_pointer_preserves_value_and_full_identity(self):
        path = "analysis/receipt.json"
        raw = '{"a/b":{"~key":[null,{"label":"日本語","ok":false}]},"unread":"context"}\n'
        self.write(path, raw)
        self.commit()
        old = self.git("rev-parse", "HEAD")
        self.write(path, '{"dirty":true}')
        rc, out = self.invoke("source", path, "--pointer", "/a~1b/~0key/1", "--ref", old)
        self.assertEqual(rc, 0, out)
        card = out["record"]
        self.assertEqual(card["selected_json"], {"label": "日本語", "ok": False})
        self.assertEqual(card["source"]["sha256"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(card["source"]["json_pointer"], "/a~1b/~0key/1")
        self.assertNotIn("_document_text", card)
        self.assertIn("outside", card["context_scope"])

    def test_source_json_pointer_default_text_retains_verification_caveat(self):
        self.write("analysis/p.json", '{"x":null,"y":7}')
        self.commit()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = memory.main(["source", "analysis/p.json", "--pointer", "/y", "--root", str(self.root)])
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("Selected JSON value:\n7", buf.getvalue())
        self.assertIn("outside this pointer are unread", buf.getvalue())

    def test_source_json_pointer_null_root_and_invalid_paths(self):
        self.write("analysis/p.json", '{"items":[null],"":7}')
        self.commit()
        for ptr, expected in [("/items/0", None), ("/", 7), ("", {"items": [None], "": 7})]:
            rc, out = self.invoke("source", "analysis/p.json", "--pointer", ptr)
            self.assertEqual(rc, 0, out)
            self.assertEqual(out["record"]["selected_json"], expected)
        for ptr in ["/missing", "/items/-1", "/items/01", "/items/1", "/items/-", "/bad~2", "items", "/items/0/child"]:
            rc, out = self.invoke("source", "analysis/p.json", "--pointer", ptr)
            self.assertEqual(rc, 2, (ptr, out))

    def test_source_json_pointer_refuses_ambiguous_and_oversized_values(self):
        self.write("analysis/nonfinite.json", '{"x":1e400}')
        self.write("analysis/dupe.json", '{"x":1,"x":2}')
        self.write("analysis/big.json", json.dumps({"x": "z" * 16000}))
        self.commit()
        for path in ["analysis/dupe.json", "analysis/big.json", "analysis/nonfinite.json"]:
            rc, out = self.invoke("source", path, "--pointer", "/x")
            self.assertEqual(rc, 2, out)
        rc, out = self.invoke("search", "x", "--pointer", "/x")
        self.assertEqual(rc, 2, out)
        rc, out = self.invoke("source", "analysis/big.json", "--pointer", "/x", "--offset", "1")
        self.assertEqual(rc, 2, out)

    def test_primary_json_source_is_pinned_and_preserves_fields(self):
        path = "analysis/unindexed receipt.json"
        text = '{"result": "provisional", "caveat": "no strength claim", "unicode": "日本語"}\n'
        self.write(path, text)
        self.commit()
        old = self.git("rev-parse", "HEAD")
        self.write(path, '{"result": "dirty false claim"}\n')
        rc, out = self.invoke("source", path, "--ref", old)
        self.assertEqual(rc, 0, out)
        card = out["record"]
        self.assertEqual(card["kind"], "source_document")
        self.assertEqual(card["sections"][0]["text"], text.rstrip("\n"))
        self.assertEqual(card["source"]["sha256"], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(card["source"]["commit"], old)
        self.assertIn("not semantically certified", card["basis"])

    def test_repeated_pointers_preserve_order_null_values_and_identity(self):
        raw = '{"a/b":null,"items":[false,7],"unread":"large evidence"}'
        self.write("analysis/multi.json", raw)
        self.commit()
        rc, out = self.invoke("source", "analysis/multi.json", "--pointer", "/items/1",
                              "--pointer", "/a~1b", "--pointer", "/items/0")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["record"]["selected_json_values"], [
            {"json_pointer": "/items/1", "value": 7},
            {"json_pointer": "/a~1b", "value": None},
            {"json_pointer": "/items/0", "value": False}])
        self.assertEqual(out["record"]["source"]["sha256"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertNotIn("selected_json", out["record"])

    def test_repeated_pointers_refuse_whole_request_on_missing_duplicate_or_oversize(self):
        self.write("analysis/multi.json", json.dumps({"a": 1, "big": "z" * 15000}))
        self.commit()
        for pointers in [["/missing", "/a"], ["/a", "/missing"], ["/a", "/a"], ["/a", "/big"]]:
            with self.subTest(pointers=pointers):
                args = [x for pointer in pointers for x in ["--pointer", pointer]]
                rc, out = self.invoke("source", "analysis/multi.json", *args)
                self.assertEqual(rc, 2, out)
                self.assertNotIn("record", out)

    def test_repeated_pointers_default_text_shows_every_pointer(self):
        self.write("analysis/multi.json", '{"x":null,"y":7}')
        self.commit()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = memory.main(["source", "analysis/multi.json", "--pointer", "/y",
                              "--pointer", "/x", "--root", str(self.root)])
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn('"json_pointer": "/y"', buf.getvalue())
        self.assertIn('"json_pointer": "/x"', buf.getvalue())

    def test_primary_source_code_is_text_and_binary_or_untracked_refuses(self):
        self.write("analysis/source.py", "raise RuntimeError('must never execute')\n")
        (self.root / "analysis/binary.bin").write_bytes(b"binary\x00payload")
        self.commit()
        rc, out = self.invoke("source", "analysis/source.py")
        self.assertEqual(rc, 0, out)
        self.assertIn("must never execute", out["record"]["sections"][0]["text"])
        self.write("analysis/untracked.txt", "must not read this working file")
        for path in ["analysis/binary.bin", "analysis/untracked.txt", "../outside.txt"]:
            rc, out = self.invoke("source", path)
            self.assertEqual(rc, 2, out)

    def test_primary_source_large_text_refuses_before_reading_payload(self):
        self.write("analysis/large.txt", "x" * (8 * 1024 * 1024 + 1))
        self.commit()
        snap = memory.Snapshot(self.root, "HEAD")
        with self.assertRaisesRegex(memory.MemoryError, "8 MiB"):
            memory.source_document(snap, "analysis/large.txt", [])
        self.assertNotIn("analysis/large.txt", snap.cache)

    def test_primary_source_pages_preserve_late_correction_and_related_record(self):
        rc, out = self.invoke("source", self.path, "--lines", "2")
        self.assertEqual(rc, 0, out)
        card = out["record"]
        self.assertEqual(card["related_record_ids"], ["E001"])
        self.assertFalse(card["document_page"]["complete_document"])
        self.assertIn("PARTIAL", card["context_scope"])
        rc, rest = self.invoke("source", self.path, "--offset", "2")
        self.assertEqual(rc, 0, rest)
        self.assertEqual(rest["record"]["document_page"]["line_start"], 3)
        self.assertIn("no general strength claim", rest["record"]["sections"][0]["text"])
        self.assertIn("Continue: source", memory.render_text(out))

    def test_source_method_result_caveat_and_unresolved_reference_survive(self):
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        card = out["record"]
        self.assertEqual([s["text"] for s in card["sections"]],
                         ["original method", "2/4 wins", "historical decision",
                          "no general strength claim; see E002"])
        self.assertEqual(card["unresolved_references"], ["E002"])
        self.assertIn("not re-executed", card["basis"])

    def test_dirty_checkout_cannot_change_snapshot_answer(self):
        _, before = self.invoke("show", "E001")
        self.write(self.path, "## E001: fabricated\n- **Result**: 4/4 wins\n")
        rc, after = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertEqual(before, after)

    def test_new_commit_changes_identity_and_answer_old_ref_retains_history(self):
        old = self.git("rev-parse", "HEAD")
        self.write(self.path, "## E001: corrected\n- **Result**: 1/4 wins\n")
        self.commit()
        _, current = self.invoke("show", "E001")
        _, historical = self.invoke("show", "E001", "--ref", old)
        self.assertNotEqual(current["record"]["source"]["sha256"], historical["record"]["source"]["sha256"])
        self.assertEqual(historical["record"]["sections"][1]["text"], "2/4 wins")

    def test_non_git_is_unavailable_never_no_matches(self):
        with tempfile.TemporaryDirectory() as nonrepo:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = memory.main(["search", "nonexistent", "--root", nonrepo])
            out = json.loads(output.getvalue())
        self.assertEqual(rc, 2)
        self.assertEqual(out["status"], "MEMORY_UNAVAILABLE")
        self.assertNotIn("matches", out)

    def test_no_match_is_scoped_not_novelty_claim(self):
        rc, out = self.invoke("search", "zxqvunknown")
        self.assertEqual(rc, 0)
        self.assertEqual(out["total_matches"], 0)
        self.assertIn("does not prove", out["note"])

    def test_empty_query_does_not_match_records_with_absent_labels(self):
        self.assertEqual(memory.rank([{"id": "E001", "title": "Fallback"}], ""), [])

    def test_catalog_loss_source_is_searchable_with_staleness_and_late_context(self):
        path = "workflow/LOSS-MODES.md"
        self.write(memory.CATALOG, json.dumps({"warning": "Catalog is not truth", "inventories": [
            {"id": "LOSS_MODES", "path": path, "topic": "loss_taxonomy", "staleness": "Historical working draft"}]}))
        text = "# Loss modes\n96 unresolved endings were not TURN_LIMIT.\nLate qualification: resolving action missing.\n"
        self.write(path, text)
        self.commit()
        rc, hits = self.invoke("search", "resolving action missing")
        self.assertEqual(rc, 0)
        self.assertIn("catalog:LOSS_MODES", [c["id"] for c in hits["matches"]])
        rc, out = self.invoke("show", "catalog:LOSS_MODES")
        self.assertEqual(rc, 0)
        self.assertEqual(out["record"]["sections"][0]["text"], text.rstrip("\n"))
        self.assertEqual(out["record"]["catalog_context"]["row"]["staleness"], "Historical working draft")
        rendered = memory.render_text(out)
        self.assertLess(rendered.index("Historical working draft"), rendered.index("96 unresolved"))
        self.assertIn("Catalog is not truth", rendered)
        self.assertTrue(out["record"]["document_page"]["complete_document"])

    def test_catalog_document_absence_is_explicit_not_empty_success(self):
        self.write(memory.CATALOG, json.dumps({"inventories": [
            {"id": "LOSS_MODES", "path": "workflow/missing.md", "topic": "loss_taxonomy"}]}))
        self.commit()
        _, out = self.invoke("coverage")
        self.assertEqual(out["meta"]["catalog_documents"]["LOSS_MODES"]["status"], "SOURCE_ABSENT_AT_SNAPSHOT")
        rc, missing = self.invoke("show", "catalog:LOSS_MODES")
        self.assertEqual(rc, 2)

    def test_replay_and_strategy_catalogs_keep_full_text_and_late_cautions(self):
        rows = [{"id": "REPLAY_STORES", "path": "workflow/REPLAY-STORES.md", "topic": "data"},
                {"id": "STRATEGY_ATLAS", "path": "workflow/canon/STRATEGY-ATLAS.md", "topic": "strategy"}]
        self.write(memory.CATALOG, json.dumps({"warning": "Historical source assertions", "inventories": rows}))
        for row in rows:
            self.write(row["path"], "# Source history\n| Old result |\n|---|\n| promising |\n\n"
                       "- Initiative: zephyrrecovery was attempted.\nLate caveat: no retained strength.\n")
        self.commit()
        _, hits = self.invoke("search", "zephyrrecovery")
        self.assertEqual({r["id"] for r in hits["matches"]}, {"catalog:" + r["id"] for r in rows})
        for row in rows:
            _, out = self.invoke("show", "catalog:" + row["id"])
            self.assertEqual(out["record"]["sections"][0]["text"], (self.root / row["path"]).read_text().rstrip())
            self.assertIn("not semantically certified", out["record"]["basis"])
            self.assertNotIn("catalog_documents", out["meta"])
            self.assertIn("verification_limit", out["meta"])
            self.assertIn("Historical source assertions", json.dumps(out["record"]["catalog_context"]))
        _, coverage = self.invoke("coverage")
        self.assertIn("REPLAY_STORES", coverage["meta"]["catalog_documents"])

    def test_knowledge_and_measurement_catalogs_retain_historical_context(self):
        rows = [{"id": "KNOWLEDGE", "path": "workflow/KNOWLEDGE.md", "staleness": "Historical assertions"},
                {"id": "MEASUREMENTS_INDEX", "path": "workflow/measurements/INDEX.md", "staleness": "Recorded measurements, not current strength"},
                {"id": "NUMBERS_INVENTORY", "path": "workflow/NUMBERS-INVENTORY.md", "staleness": "Historical quantities; corrections and missing receipts apply"}]
        self.write(memory.CATALOG, json.dumps({"warning": "Verify source claims", "inventories": rows}))
        for row in rows:
            self.write(row["path"], "# Historical evidence\nuniquerecoverychain measurement\nLate limit: off-box calibration not banked.\n")
        self.commit()
        _, hits = self.invoke("search", "uniquerecoverychain")
        self.assertEqual({r["id"] for r in hits["matches"]}, {"catalog:" + r["id"] for r in rows})
        for row in rows:
            code, result = self.invoke("show", "catalog:" + row["id"])
            self.assertEqual(code, 0)
            record = result["record"]
            self.assertIn("not semantically certified", record["basis"])
            self.assertEqual(record["catalog_context"]["row"]["staleness"], row["staleness"])
            self.assertIn("off-box calibration not banked", record["sections"][0]["text"])

    def test_search_metadata_defers_global_census_without_losing_evidence_scope(self):
        rc, out = self.invoke("search", "fallback", "--limit", "1")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("research_documents", out["meta"])
        for field in ["snapshot", "retraction_source", "coverage_limit", "verification_limit",
                      "stale_review_notes", "stale_knowledge_records"]:
            self.assertIn(field, out["meta"])
        self.assertIn("matches", out)
        self.assertIn("not support", out["note"])
        _, census = self.invoke("coverage")
        self.assertIn("research_documents", census["meta"])

    def test_show_experiment_keeps_evidence_but_defers_global_census(self):
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertIn("source", out["record"])
        self.assertIn("sections", out["record"])
        self.assertNotIn("history_sources", out["meta"])
        self.assertIn("verification_limit", out["meta"])
        self.assertIn("retraction_source", out["meta"])
        _, coverage = self.invoke("coverage")
        self.assertIn("history_sources", coverage["meta"])

    def test_unindexed_research_documents_are_found_without_promoting_their_claims(self):
        path = "workflow/research/unindexed/refinement.md"
        self.write(path, "# Zephyr refinement\nHistorical proposal, not authorization.\n"
                   "The weak leaf result does not refute the mechanism class.\n")
        self.write("workflow/research/refinement.md", "# Different study\nSeparate identity.\n")
        self.write("workflow/research/raw.json", '{"unread": true}\n')
        self.commit()
        rc, hits = self.invoke("search", "Zephyr")
        self.assertEqual(rc, 0)
        self.assertEqual(hits["matches"][0]["id"], "research:unindexed/refinement.md")
        _, out = self.invoke("show", hits["matches"][0]["id"])
        self.assertEqual(out["record"]["source"]["path"], path)
        self.assertIn("Historical proposal, not authorization.", out["record"]["sections"][0]["text"])
        self.assertIn("not semantically certified", out["record"]["basis"])
        self.assertTrue(out["record"]["document_page"]["complete_document"])
        self.assertIn("full catalog census via coverage", out["meta"]["metadata_scope"])
        _, census = self.invoke("coverage")
        coverage = census["meta"]["research_documents"]
        self.assertEqual(coverage["markdown_documents"], 2)
        self.assertEqual(coverage["other_file_types"], {".json": 1})

    def test_specific_research_filename_phrase_beats_generic_title_terms(self):
        cards = [{"id": "research:earlier.md", "title": "Search and synthesis", "kind": "research_document"},
                 {"id": "research:2026-07-27-SEARCH-SYNTHESIS.md", "title": "Refinement", "kind": "research_document"}]
        self.assertEqual(memory.rank(cards, "SEARCH-SYNTHESIS")[0]["id"], cards[1]["id"])

    def test_bom_marked_utf16_research_preserves_text_and_raw_byte_identity(self):
        path = self.root / "workflow/research/foreign.md"
        path.parent.mkdir(parents=True)
        text = "# Strategy\nMéthode 日本語 العربية\nUnverified source assertion.\n"
        raw = text.encode("utf-16")
        path.write_bytes(raw)
        self.commit()
        rc, out = self.invoke("show", "research:foreign.md")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["record"]["sections"][0]["text"], text.rstrip("\n"))
        self.assertEqual(out["record"]["source"]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(out["record"]["source_encoding"], "utf-16")
        self.assertEqual(out["record"]["source"]["line_end"], 3)
        snap = memory.Snapshot(self.root, "HEAD")
        with self.assertRaises(memory.MemoryError):
            memory.anchor_check({"path": "workflow/research/foreign.md", "sha256": hashlib.sha256(raw).hexdigest(),
                                 "locator": {"line_start": 4, "line_end": 4}}, snap, {snap.commit: snap})

    def test_research_pages_preserve_every_line_and_late_caveat_with_a_hard_budget(self):
        path = "workflow/research/long.md"
        lines = ["# Long study", "PROVISIONAL: read the later correction."]
        lines += [f"Measured row {i}: " + "évidence " * 30 for i in range(80)]
        lines += ["CORRECTION: this was an unexecuted proposal, not a successful run."]
        self.write(path, "\n".join(lines) + "\n")
        self.commit()
        offset, recovered = 0, []
        while True:
            rc, out = self.invoke("show", "research:long.md", "--offset", str(offset),
                                  "--lines", "100", "--max-bytes", "10000")
            self.assertEqual(rc, 0, out)
            self.assertLessEqual(len((json.dumps(out, ensure_ascii=False, indent=2) + "\n").encode()), 10000)
            page = out["record"]["document_page"]
            self.assertEqual(page["line_start"], offset + 1)
            recovered.extend(out["record"]["sections"][0]["text"].splitlines())
            if page["next_offset"] is None:
                break
            self.assertIn("partial", out["record"]["context_scope"].lower())
            self.assertGreater(page["next_offset"], offset)
            offset = page["next_offset"]
        self.assertEqual(recovered, lines)
        self.assertFalse(page["complete_document"])
        rc, error = self.invoke("show", "research:long.md", "--offset", "9999")
        self.assertEqual(rc, 2)
        self.assertIn("outside", error["reason"])

    def test_research_source_changes_preserve_old_snapshot_and_ignore_dirty_text(self):
        path = "workflow/research/changed.md"
        self.write(path, "# Study\nOld result is provisional.\n")
        self.commit()
        old = self.git("rev-parse", "HEAD")
        _, before = self.invoke("show", "research:changed.md")
        self.write(path, "# Study\nCorrected result.\n")
        _, dirty = self.invoke("show", "research:changed.md")
        self.assertEqual(before, dirty)
        self.commit()
        _, after = self.invoke("show", "research:changed.md")
        _, historical = self.invoke("show", "research:changed.md", "--ref", old)
        self.assertEqual(before, historical)
        self.assertNotEqual(before["record"]["source"]["sha256"], after["record"]["source"]["sha256"])

    def test_non_utf8_research_is_explicitly_unavailable_without_poisoning_other_records(self):
        path = self.root / "workflow/research/bad.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"# Bad\n\xff\n")
        self.commit()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        _, out = self.invoke("coverage")
        self.assertEqual(out["meta"]["research_documents"]["unreadable_markdown"], 1)
        rc, out = self.invoke("show", "research:bad.md")
        self.assertEqual(rc, 2)
        self.assertIn("UTF-8", out["reason"])

    def test_lesson_preserves_number_root_cause_receipts_and_advisory_banner(self):
        self.write("workflow/LESSONS.md", "# Lessons\nStatus: ADVISORY; verify-me.\n\n"
                   "| # | lesson | root cause | became mechanism | receipts |\n"
                   "|---|---|---|---|---|\n"
                   "| 21 | Dormant suite exited 0 | no __main__ | ci_discover_suites | #3135 |\n")
        self.commit()
        rc, hits = self.invoke("search", "Dormant suite")
        self.assertEqual(rc, 0)
        rid = hits["matches"][0]["id"]
        self.assertTrue(rid.startswith("lesson:"))
        self.assertTrue(rid.endswith(":21"))
        _, out = self.invoke("show", rid)
        text = "\n".join(p["text"] for p in out["record"]["sections"])
        for expected in ("Status: ADVISORY; verify-me.", "root cause", "no __main__",
                         "ci_discover_suites", "#3135"):
            self.assertIn(expected, text)
        self.assertIn("no new ruling", out["record"]["basis"])

    def test_sources_distinguishes_extraction_unread_and_missing_and_ignores_dirty_file(self):
        self.write(memory.CATALOG, json.dumps({'inventories': [
            {'id': 'A', 'path': self.path, 'topic': 'experiment'},
            {'id': 'B', 'path': 'workflow/unread.md', 'topic': 'research'},
            {'id': 'C', 'path': 'workflow/missing.md', 'topic': 'research'}]}))
        self.write('workflow/unread.md', 'Existing research outside the reader')
        self.commit()
        self.write('workflow/missing.md', 'Dirty file is not snapshot evidence')
        rc, out = self.invoke('sources')
        self.assertEqual(rc, 0)
        self.assertEqual([r['disposition'] for r in out['catalog_sources']],
                         ['DIRECT_RECORDS_PARTIAL', 'NOT_IN_READER', 'SOURCE_ABSENT_AT_SNAPSHOT'])
        self.assertEqual(out['catalog_sources'][0]['example_record_ids'], ['E001'])
        self.assertIsNone(out['catalog_sources'][2]['source'])
        self.assertIn('unlisted sources', out['note'])
        _, filtered = self.invoke('sources', 'research', '--limit', '1')
        self.assertEqual(filtered['total_matches'], 2)
        self.assertEqual(filtered['next_offset'], 1)
        _, second = self.invoke('sources', 'research', '--limit', '1', '--offset', '1')
        self.assertEqual(second['catalog_sources'][0]['id'], 'C')
        self.assertIsNone(second['next_offset'])

    def test_sources_missing_catalog_is_unavailable_not_zero_coverage(self):
        rc, out = self.invoke('sources')
        self.assertEqual(rc, 2)
        self.assertEqual(out['status'], 'MEMORY_UNAVAILABLE')
        self.assertNotIn('total_catalog_sources', out)

    def test_research_registers_preserve_hypotheses_missing_assets_and_visibility_limits(self):
        rows = [
            ('hypothesis', 'hypotheses', {'id': 'HYP-B', 'claim': 'Improve after transfer',
             'status': 'FROZEN_FOR_ABLATION', 'max_compute_budget': 'TBD', 'kill_if': ['no consumer']},
             {'rule': 'Historical proposal, not measured gain'}),
            ('domain_term', 'rows', {'id': 'DT-02', 'term': 'ko_trade', 'status': 'SPEC_ONLY',
             'fixture_path': None, 'code_path': None}, {'stamped': '2026-08-15'}),
            ('metric', 'metrics', {'id': 'M-AUC', 'example_value': 0.86, 'use': 'leaf_only'},
             {'rule': 'Read retractions before use'}),
            ('trace_source', 'candidate_sources', {'id': 'SRC-C61', 'match_owned_product': 'NO',
             'status': 'CONTROL_TEACHER_ONLY'}, {'do_not_use_for': ['clairvoyant_BC_on_hidden_union'],
             'decision': {'matching_corpus_found': None}}),
        ]
        for family, key, row, context in rows:
            self.write(memory.REGISTERS[family][0], json.dumps({**context, key: [row]}))
        self.commit()
        for family, key, row, context in rows:
            rc, out = self.invoke('show', family + ':' + row['id'])
            self.assertEqual(rc, 0)
            card = out['record']
            self.assertEqual(card['knowledge'], row)
            self.assertEqual(card['register_context'], context)
            self.assertEqual(card['source']['json_pointer'], f'/{key}/0')
            self.assertIn('not current usability', card['basis'])
            self.assertIn('not current instructions', memory.render_text(out))

    def test_measurement_summary_preserves_design_population_and_scaling_caveat(self):
        self.write(memory.HISTORY['measured'], '# Measurements\nHistorical report only.\n'
                   '## 2. Screening\nMirror policy; N games PER ARM.\n'
                   '| n | sigma_delta |\n|---|---|\n| 400 | 3.529pp |\n'
                   '## Dispute\nNo raw manifest recovered; do not join another population.\n')
        self.commit()
        rc, out = self.invoke('show', 'measured:2')
        self.assertEqual(rc, 0)
        text = memory.render_text(out)
        self.assertIn('Historical report only.', text)
        self.assertIn('N games PER ARM.', text)
        _, hits = self.invoke('search', 'raw manifest')
        self.assertTrue(any(x['id'].startswith('measured:') for x in hits['matches']))

    def test_sources_preserves_catalog_freshness_warning_and_row_stamp(self):
        warning = 'This stamp dates the catalog, not the targets; their freshness is unaudited.'
        self.write(memory.CATALOG, json.dumps({'stamped': '2026-08-23', 'note': warning,
            'inventories': [{'id': 'OLD', 'path': self.path, 'topic': 'science',
                            'stamped': '2026-07-18', 'staleness': 'Known old; verify before use'}]}))
        self.commit()
        rc, out = self.invoke('sources')
        self.assertEqual(rc, 0)
        self.assertEqual(out['catalog_context']['note'], warning)
        self.assertEqual(out['catalog_sources'][0]['catalog_context']['stamped'], '2026-07-18')
        text = memory.render_text(out)
        for expected in (warning, '2026-07-18', 'Known old; verify before use', 'not verified'):
            self.assertIn(expected, text)

    def test_sources_bound_reference_is_not_direct_extraction(self):
        self.write(memory.CATALOG, json.dumps({'inventories': [
            {'id': 'SUPPORT', 'path': 'workflow/support.md', 'topic': 'control'}]}))
        self.write('workflow/support.md', 'A support reference is not full recovery')
        self.commit()
        snap = memory.Snapshot(self.root, 'HEAD')
        rows = memory.catalog_sources([{'id': 'review', 'source': {'path': 'review.jsonl'},
                                       'knowledge': {'source_refs': [{'path': 'workflow/support.md'}]}}], snap)
        self.assertEqual(rows[0]['disposition'], 'BOUND_REFERENCES_ONLY')
        self.assertEqual(rows[0]['direct_records'], 0)
        self.assertEqual(rows[0]['bound_reference_records'], 1)

    def test_no_scientific_promotion_for_compact_class(self):
        rc, out = self.invoke("show", "tried:OLD")
        self.assertEqual(rc, 0)
        self.assertEqual(out["record"]["knowledge"]["class"], "UNKNOWN")
        self.assertEqual(out["record"]["open_conflicts"], ["Two quantities remain unresolved"])
        self.assertIn("not a new ruling", out["record"]["basis"])

    def test_malformed_json_refuses_instead_of_empty_corpus(self):
        self.write(memory.COMPACT, "[]")
        self.commit()
        rc, out = self.invoke("coverage")
        self.assertEqual(rc, 2)
        self.assertIn("shape", out["reason"])

    def test_duplicate_id_refuses(self):
        self.write(memory.EXPERIMENTS + "E001-another.md", "## E001: other\n")
        self.commit()
        rc, out = self.invoke("verify")
        self.assertEqual(rc, 2)
        self.assertIn("Duplicate", out["reason"])

    def test_missing_source_refuses(self):
        self.git("rm", memory.RETRACTIONS)
        self.git("-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "commit", "-qm", "missing")
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 2)
        self.assertIn("absent", out["reason"])

    def test_budget_does_not_silently_remove_caveat(self):
        self.write(self.path, "## E001: Fallback\n- **Result**: " + "x" * 5000 + "\n- **CAVEATS**: essential limit\n")
        self.commit()
        rc, out = self.invoke("show", "E001", "--max-bytes", "2000")
        self.assertEqual(rc, 2)
        self.assertIn("Output needs", out["reason"])
        self.assertNotIn("record", out)

    def test_fenced_mock_result_does_not_become_section(self):
        parts = memory.sections("- **Setup**: real\n```text\n- **Result**: fake\n```\n- **Result**: actual\n")
        self.assertEqual([s["label"] for s in parts], ["Setup", "Result"])
        self.assertEqual(parts[1]["text"], "actual")

    def test_preamble_retraction_is_visible_and_searchable(self):
        self.write(self.path, "## E001: Fallback\nRETRACTED: zebrasentinel result belongs to the wrong arm; do not reuse.\n\n- **Result**: 4/4 wins\n")
        self.commit()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertIn("RETRACTED: zebrasentinel", out["record"]["preamble"]["text"])
        self.assertEqual(out["record"]["preamble"]["line_end"], 3)
        rc, found = self.invoke("search", "zebrasentinel")
        self.assertEqual(rc, 0)
        self.assertEqual([r["id"] for r in found["matches"]], ["E001"])

    def test_unstructured_report_is_retained_whole(self):
        self.write(self.path, "## E001: Fallback\nNo formatted sections.\nA critical caution.\n")
        self.commit()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertIn("A critical caution.", out["record"]["preamble"]["text"])
        self.assertEqual(out["record"]["sections"], [])

    def test_invalid_review_evidence_refuses(self):
        note = {key: "unknown" for key in ("question", "why", "methodology", "result", "learn", "reopen_when")}
        note.update(id="E001", limitations=["unknown"], related_ids=[], source_refs=[
            {"path": self.path, "sha256": "0" * 64, "locator": {"line_start": 1, "line_end": 1}}])
        self.write(memory.NOTES + "E001.json", json.dumps(note))
        self.commit()
        rc, out = self.invoke("verify")
        self.assertEqual(rc, 2)
        self.assertIn("anchor bytes changed", out["reason"])

    def test_changed_report_marks_pinned_note_stale_without_losing_history(self):
        old = self.git("rev-parse", "HEAD")
        raw = subprocess.check_output(["git", "show", old + ":" + self.path], cwd=self.root)
        note = {key: "historical interpretation" for key in
                ("question", "why", "methodology", "result", "learn", "reopen_when")}
        note.update(id="E001", limitations=["raw run not reviewed"], related_ids=[], source_refs=[
            {"path": self.path, "git_commit": old, "sha256": hashlib.sha256(raw).hexdigest(),
             "locator": {"line_start": 1, "line_end": 1}}])
        self.write(memory.NOTES + "E001.json", json.dumps(note))
        self.commit()
        rc, before = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertEqual(before["record"]["review_note_currentness"], "SOURCE_VERSION_MATCHES")
        rendered = memory.render_text(before)
        self.assertLess(rendered.index("historical interpretation"), rendered.index("2/4 wins"))
        self.write(self.path, "## E001: Fallback\nRETRACTED: source corrected.\n")
        self.commit()
        rc, after = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertTrue(after["record"]["review_note_currentness"].startswith("STALE"))
        self.assertEqual(after["record"]["review_note"], note)
        self.assertEqual(after["meta"]["stale_review_notes"], 1)
        rendered = memory.render_text(after)
        self.assertLess(rendered.index("Explanatory note: STALE"), rendered.index("RETRACTED: source corrected."))

    def test_reading_view_keeps_results_caveats_source_and_scope(self):
        self.write(self.path, "## E001: Fallback\nRETRACTED: wrong arm.\n- **Result**: 4/4 wins\n- **CAVEATS**: cannot generalize\n")
        self.commit()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = memory.main(["show", "E001", "--root", str(self.root)])
        text = output.getvalue()
        self.assertEqual(rc, 0)
        for expected in ["RETRACTED: wrong arm", "4/4 wins", "cannot generalize",
                         self.path, "sha256=", "not re-executed", "not exhaustively covered"]:
            self.assertIn(expected, text)

    def add_supported_note(self):
        self.write("evidence/control.md", "# Control\nMatched control established.\n")
        self.commit()
        old = self.git("rev-parse", "HEAD")
        refs = [{"path": p, "git_commit": old,
                 "sha256": hashlib.sha256((self.root / p).read_bytes()).hexdigest(),
                 "locator": {"line_start": 1, "line_end": 1}}
                for p in [self.path, "evidence/control.md"]]
        note = {k: "historical interpretation" for k in
                ("question", "why", "methodology", "result", "learn", "reopen_when")}
        note.update(id="E001", limitations=["no new run"], related_ids=[], source_refs=refs)
        self.write(memory.NOTES + "E001.json", json.dumps(note))
        self.commit()
        return old

    def test_changed_support_marks_note_stale_even_when_target_unchanged(self):
        self.add_supported_note()
        self.write("evidence/control.md", "# Control\nRETRACTED: wrong comparator.\n")
        self.commit()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertTrue(out["record"]["review_note_currentness"].startswith("STALE"))
        rc, queue = self.invoke("maintenance")
        self.assertEqual(rc, 0)
        self.assertEqual(queue["status"], "REVIEW_REQUIRED")
        self.assertEqual(queue["total_review_items"], 1)
        item = queue["review_items"][0]
        self.assertEqual(item["record_ids"], ["E001"])
        self.assertEqual(item["changed_sources"][0]["path"], "evidence/control.md")
        self.assertEqual(item["changed_sources"][0]["state"], "SOURCE_CHANGED")
        self.assertNotEqual(item["changed_sources"][0]["pinned_sha256"],
                            item["changed_sources"][0]["current_sha256"])

    def test_dirty_support_is_ignored_and_missing_committed_support_is_queued(self):
        self.add_supported_note()
        self.write("evidence/control.md", "uncommitted edit\n")
        rc, queue = self.invoke("maintenance")
        self.assertEqual(rc, 0)
        self.assertEqual(queue["total_review_items"], 0)
        (self.root / "evidence/control.md").unlink()
        self.commit()
        rc, queue = self.invoke("maintenance")
        self.assertEqual(rc, 0)
        item = queue["review_items"][0]
        self.assertEqual(item["changed_sources"][0]["state"], "SOURCE_ABSENT_AT_SNAPSHOT")
        self.assertIsNone(item["changed_sources"][0]["current_sha256"])
        rc, old = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertEqual(old["record"]["review_note"]["result"], "historical interpretation")

    def test_maintenance_one_item_fits_without_dropping_stale_evidence(self):
        self.add_supported_note()
        self.write("evidence/control.md", "# Control\nRETRACTED\n")
        self.commit()
        rc, full = self.invoke("maintenance", "--limit", "1", "--max-bytes", "50000")
        self.assertEqual(rc, 0)
        rc, bounded = self.invoke("maintenance", "--limit", "1", "--max-bytes", "4000")
        self.assertEqual(rc, 0, bounded)
        for key in ("review_items", "total_review_items", "next_offset", "note"):
            self.assertEqual(bounded[key], full[key])
        self.assertEqual(bounded["meta"]["snapshot"], full["meta"]["snapshot"])
        self.assertIn("verification_limit", bounded["meta"])
        self.assertIn("retraction_source", bounded["meta"])

    def test_maintenance_pages_notes_and_knowledge_explicitly(self):
        self.add_supported_note()
        self.write("evidence/control.md", "# Control\nRETRACTED\n")
        self.commit()
        # A real source-bound knowledge record shares this same dependency.
        snap = memory.Snapshot(self.root, "HEAD")
        cards, _ = memory.load(snap)
        note = next(c for c in cards if c["id"] == "E001")["review_note"]
        self.write(memory.AUDITS + "fixture/knowledge.jsonl", json.dumps({
            "id": "finding:control", "title": "Historical control finding",
            "evidence_status": "source_assertion", "source_refs": note["source_refs"]}) + "\n")
        self.commit()
        rc, first = self.invoke("maintenance", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(first["total_review_items"], 2)
        self.assertEqual(len(first["review_items"]), 1)
        self.assertEqual(first["next_offset"], 1)
        rc, last = self.invoke("maintenance", "--limit", "1", "--offset", "1")
        self.assertEqual(rc, 0)
        self.assertIsNone(last["next_offset"])
        self.assertNotEqual(first["review_items"][0]["id"], last["review_items"][0]["id"])
        rc, found = self.invoke("show", "finding:control")
        self.assertEqual(rc, 0)
        self.assertTrue(found["record"]["knowledge_currentness"].startswith("STALE"))

    def test_stale_knowledge_support_reaches_linked_target_and_queue(self):
        old = self.add_supported_note()
        raw = subprocess.check_output(["git", "show", old + ":evidence/control.md"], cwd=self.root)
        support = {"path": "evidence/control.md", "git_commit": old,
                   "sha256": hashlib.sha256(raw).hexdigest(), "locator": {"line_start": 1, "line_end": 2}}
        kp = memory.AUDITS + "fixture/knowledge.jsonl"
        self.write(kp, json.dumps({"id": "finding:control", "title": "Control correction",
                                   "source_refs": [support]}) + "\n")
        self.commit()
        snap = memory.Snapshot(self.root, "HEAD")
        refs = [{"path": p, "git_commit": snap.commit,
                 "sha256": snap.source(p)["sha256"],
                 "locator": {"line_start": 1, "line_end": len(snap.read(p).splitlines())}}
                for p in [kp, self.path]]
        self.write(memory.LINKS, json.dumps({"relationships": [{
            "id": "control-qualifies-E001", "source_id": "finding:control", "target_id": "E001",
            "relation": "qualifies", "statement": "Historical control qualification",
            "basis": "source_assertion", "source_refs": refs}]}))
        self.commit()
        self.write("evidence/control.md", "# Control\nRETRACTED: wrong comparator.\n")
        self.commit()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        self.assertTrue(out["record"]["linked_context"][0]["currentness"].startswith("STALE"))
        rc, queue = self.invoke("maintenance")
        self.assertEqual(rc, 0)
        links = [q for q in queue["review_items"] if q["id"] == "link:control-qualifies-E001"]
        self.assertEqual(len(links), 1)
        self.assertIn("E001", links[0]["record_ids"])
        self.assertEqual(links[0]["changed_sources"][0]["path"], "evidence/control.md")

    def test_colliding_guess_numbers_keep_section_identity(self):
        self.write(memory.HISTORY["attempt"], "# Attempts\nHistorical scope.\n"
                   "## 8. GUESS REGISTER\n| # | Finding |\n|---|---|\n| GR-33 | architecture |\n"
                   "### §8b REOPENING QUEUE\n| # | Finding |\n|---|---|\n| GR-33 | portability |\n")
        self.commit()
        for rid, expected in [("attempt:8:GR-33", "architecture"), ("attempt:8b:GR-33", "portability")]:
            rc, out = self.invoke("show", rid)
            self.assertEqual(rc, 0)
            self.assertIn(expected, out["record"]["sections"][-1]["text"])
        rc, out = self.invoke("search", "GR-33", "--limit", "2")
        self.assertEqual(rc, 0)
        self.assertEqual({r["id"] for r in out["matches"]}, {"attempt:8:GR-33", "attempt:8b:GR-33"})

    def test_pre_and_post_table_qualifiers_survive_interrupted_rows(self):
        self.write(memory.RETRACTIONS, "# Retractions\nHistorical assertions.\n## Values\n"
                   "BEFORE: controls uncertain.\n| Old | Replacement |\n|---|---|\n| 9.35 | 7.82 |\n"
                   "> ### SCOPE\n> 40% Alakazam; pooled fresh interval contains zero.\n\n"
                   "| 8.26 | 7.82 |\nAFTER: no general improvement.\n")
        self.commit()
        cards, _ = memory.load(memory.Snapshot(self.root, "HEAD"))
        rows = [c for c in cards if c["kind"] == "retraction_row"]
        self.assertEqual(len(rows), 2)
        for card in rows:
            text = "\n".join(p["text"] for p in card["sections"])
            for phrase in ["BEFORE", "40% Alakazam", "contains zero", "AFTER", "| Old | Replacement |"]:
                self.assertIn(phrase, text)
            for part in card["sections"]:
                source = (self.root / memory.RETRACTIONS).read_text().splitlines()
                self.assertEqual(part["text"], "\n".join(source[part["line_start"]-1:part["line_end"]]))

    def test_fenced_tables_and_headings_are_context_not_records(self):
        self.write(memory.HISTORY["attempt"], "# History\n## 8. Actual\n"
                   "```md\n## 99. Example\n| GR-33 | fake |\n```\n"
                   "| # | Finding |\n|---|---|\n| GR-7 | real |\n")
        self.commit()
        cards, _ = memory.load(memory.Snapshot(self.root, "HEAD"))
        rows = [c for c in cards if c["kind"] == "attempt_row"]
        self.assertEqual([c["id"] for c in rows], ["attempt:8:GR-7"])
        self.assertIn("## 99. Example", "\n".join(p["text"] for p in rows[0]["sections"]))

    def test_pipe_cells_preserve_code_and_escape_boundaries(self):
        self.assertEqual(memory.table_cells(r"| `max|diff|` | a\|b | c |"),
                         ["`max|diff|`", r"a\|b", "c"])
        self.assertEqual(memory.table_cells("| ``a`|b`` | c |"), ["``a`|b``", "c"])

    def test_placeholder_ids_use_named_findings_and_duplicate_names_refuse(self):
        path = memory.HISTORY["attempt"]
        self.write(path, "# History\n## 4a. Findings\n| # | Name | Result |\n|---|---|---|\n"
                   "| — | Eliminated | null |\n| — | Survived | unknown |\n")
        self.commit()
        cards, _ = memory.load(memory.Snapshot(self.root, "HEAD"))
        rows = [c for c in cards if c["kind"] == "attempt_row"]
        self.assertEqual(len({c["id"] for c in rows}), 2)
        self.assertTrue(any(c["title"].startswith("Survived") for c in rows))
        with (self.root / path).open("a", encoding="utf-8") as f:
            f.write("| — | Survived | different result |\n")
        self.commit()
        rc, out = self.invoke("verify")
        self.assertEqual(rc, 2)
        self.assertIn("Duplicate research identity", out["reason"])

    def test_missing_optional_history_is_explicit_gap(self):
        rc, out = self.invoke("coverage")
        self.assertEqual(rc, 0)
        self.assertEqual(out["meta"]["history_sources"]["attempt"]["status"], "SOURCE_ABSENT_AT_SNAPSHOT")
        self.assertIn("not complete semantic reconciliation", out["meta"]["coverage_limit"])

    def test_heading_only_retraction_is_source_bound_in_row_and_search(self):
        path = memory.HISTORY["attempt"]
        heading = "# RETRACTED: zebrasentinel result belongs to the wrong arm; do not reuse."
        self.write(path, heading + "\n| # | Result |\n|---|---|\n| GR-7 | 4/4 wins |\n")
        self.commit()
        cards, _ = memory.load(memory.Snapshot(self.root, "HEAD"))
        row = next(c for c in cards if c["kind"] == "attempt_row")
        rc, out = self.invoke("show", row["id"])
        self.assertEqual(rc, 0)
        headings = [p for p in out["record"]["sections"] if p["label"] == "Ancestral heading"]
        self.assertEqual(headings, [{"label": "Ancestral heading", "text": heading,
                                     "line_start": 1, "line_end": 1}])
        rc, out = self.invoke("search", "zebrasentinel")
        self.assertEqual(rc, 0)
        self.assertIn(row["id"], [r["id"] for r in out["matches"]])
        self.assertTrue(any(c["kind"] == "attempt_section" and c["title"].startswith("RETRACTED") for c in cards))

    def put_link(self, **overrides):
        self.write(memory.EXPERIMENTS + "E002-correction.md", "## E002: Correction\n- **Result**: earlier estimate withdrawn\n")
        self.commit()
        snap = memory.Snapshot(self.root, "HEAD")
        row = {"id": "correction-1", "source_id": "E002", "target_id": "E001",
               "relation": "qualifies", "statement": "The earlier estimate was withdrawn; no general gain is established.",
               "basis": "source_assertion", "source_refs": [
                   {"path": path, "git_commit": snap.commit,
                    "sha256": hashlib.sha256(snap.read(path)).hexdigest(),
                    "locator": {"line_start": 1, "line_end": len(snap.read(path).splitlines())}}
                   for path in [self.path, memory.EXPERIMENTS + "E002-correction.md"]]}
        row.update(overrides)
        self.write(memory.LINKS, json.dumps({"relationships": [row]}))
        self.commit()
        return row

    def test_correction_is_visible_before_result_and_in_search(self):
        self.put_link()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = memory.main(["show", "E001", "--root", str(self.root)])
        self.assertEqual(rc, 0)
        text = output.getvalue()
        self.assertLess(text.index("earlier estimate was withdrawn"), text.index("2/4 wins"))
        rc, out = self.invoke("search", "E001", "--limit", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(out["matches"][0]["linked_context"][0]["other_id"], "E002")
        rc, out = self.invoke("show", "E002")
        self.assertEqual(out["record"]["linked_context"][0]["other_id"], "E001")

    def test_search_groups_identical_context_without_losing_targets_or_status(self):
        self.put_link()
        rc, out = self.invoke("search", "E001", "--limit", "1")
        self.assertEqual(rc, 0)
        hit = out["matches"][0]
        original = hit["linked_context"][0]
        hit["linked_context"] = [
            dict(original, other_id="E002"),
            dict(original, other_id="E003"),
            dict(original, other_id="E004", currentness="STALE_SOURCE"),
            dict(original, other_id="E005", basis="reviewer_interpretation"),
            dict(original, other_id="E006", statement="Different qualification."),
        ]
        before = json.dumps(out, sort_keys=True)
        text = memory.render_text(out)
        self.assertEqual(text.count(original["statement"]), 3)
        for target in ["E002", "E003", "E004", "E005", "E006"]:
            self.assertIn("show " + target, text)
        self.assertIn("STALE_SOURCE", text)
        self.assertIn("reviewer_interpretation", text)
        self.assertIn("Different qualification.", text)
        self.assertEqual(json.dumps(out, sort_keys=True), before)

    def test_record_groups_repeated_qualification_preserving_each_source_and_edge(self):
        self.put_link()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        card = out["record"]
        original = card["linked_context"][0]
        links = []
        for i, overrides in enumerate([
                {}, {}, {"currentness": "STALE_SOURCE"},
                {"basis": "reviewer_interpretation"},
                {"statement": "Different qualification."}]):
            link = dict(original, other_id=f"E10{i}", target_id=f"E10{i}",
                        relation=f"relation{i}", **overrides)
            link["link_source"] = dict(original["link_source"], json_pointer=f"/relationships/{i}")
            links.append(link)
        card["linked_context"] = links
        before = json.dumps(out, sort_keys=True)
        text = memory.render_text(out)
        self.assertEqual(text.count(original["statement"]), 3)
        for link in links:
            self.assertIn(f"{link['source_id']} {link['relation']} {link['target_id']}", text)
            self.assertIn("show " + link["other_id"], text)
            self.assertIn(memory.source_line(link["link_source"]), text)
        self.assertIn("STALE_SOURCE", text)
        self.assertIn("reviewer_interpretation", text)
        self.assertIn("Different qualification.", text)
        self.assertLess(text.index("Different qualification."), text.index("2/4 wins"))
        self.assertEqual(json.dumps(out, sort_keys=True), before)

    def test_missing_link_endpoint_refuses(self):
        self.put_link(target_id="E999")
        rc, out = self.invoke("verify")
        self.assertEqual(rc, 2)
        self.assertIn("endpoint absent", out["reason"])

    def test_link_must_bind_both_endpoint_sources(self):
        row = self.put_link()
        row["source_refs"] = row["source_refs"][:1]
        self.write(memory.LINKS, json.dumps({"relationships": [row]})); self.commit()
        rc, out = self.invoke("verify")
        self.assertEqual(rc, 2)
        self.assertIn("does not bind endpoint", out["reason"])

    def test_changed_support_marks_link_stale_without_dropping_history(self):
        self.put_link()
        self.write(memory.EXPERIMENTS + "E002-correction.md", "## E002: Changed\nNew qualification.\nAdditional line shifts the old end.\n")
        self.commit()
        rc, out = self.invoke("show", "E001")
        self.assertEqual(rc, 0)
        link = out["record"]["linked_context"][0]
        self.assertTrue(link["currentness"].startswith("STALE"))
        self.assertIn("withdrawn", link["statement"])
        _, census = self.invoke("coverage")
        self.assertEqual(census["meta"]["relationships"]["stale"], 1)

    def test_same_file_wrong_row_cannot_bind_correction(self):
        path, key = memory.REGISTERS["tool"]
        self.write(path, json.dumps({key: [{"id": "T-ONE"}, {"id": "T-TWO"}]}))
        self.commit(); snap = memory.Snapshot(self.root, "HEAD")
        wrong = {"path": path, "git_commit": snap.commit,
                 "sha256": hashlib.sha256(snap.read(path)).hexdigest(),
                 "locator": {"json_pointer": "/tools/0"}}
        row = {"id": "wrong-row", "source_id": "tool:T-ONE", "target_id": "tool:T-TWO",
               "relation": "qualifies", "statement": "A correction attached to the wrong row",
               "basis": "source_assertion", "source_refs": [wrong]}
        self.write(memory.LINKS, json.dumps({"relationships": [row]})); self.commit()
        rc, out = self.invoke("verify")
        self.assertEqual(rc, 2)
        self.assertIn("locator does not cover endpoint record", out["reason"])
        row["source_refs"].append({**wrong, "locator": {"json_pointer": "/tools/1"}})
        self.write(memory.LINKS, json.dumps({"relationships": [row]})); self.commit()
        rc, out = self.invoke("show", "tool:T-TWO")
        self.assertEqual(rc, 0)
        self.assertEqual(out["record"]["linked_context"][0]["currentness"], "SOURCE_VERSIONS_MATCH")

    def test_structured_register_keeps_scope_and_missing_source_is_gap(self):
        path, key = memory.REGISTERS["tool"]
        self.write(path, json.dumps({"schema": "fixture", "rule": "Code is not execution",
                   key: [{"id": "T-ONE", "path": "tool.py", "output_status": "UNKNOWN"}]}))
        self.commit()
        rc, out = self.invoke("show", "tool:T-ONE")
        self.assertEqual(rc, 0)
        self.assertEqual(out["record"]["register_context"]["rule"], "Code is not execution")
        self.assertEqual(out["record"]["source"]["json_pointer"], "/tools/0")
        _, out = self.invoke("coverage")
        self.assertEqual(out["meta"]["register_sources"]["graveyard"]["status"], "SOURCE_ABSENT_AT_SNAPSHOT")


if __name__ == "__main__":
    unittest.main()
