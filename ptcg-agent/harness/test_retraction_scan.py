"""Fixtures for scripts/retraction_scan.py — the retraction firewall.

Properties: a retracted decimal is found only as a whole token (7.82 is not inside 17.82; 46.2 is not
inside 46.21); a retracted hash prefix is found; a clean file yields no hits and a non-certificate
message; --allow suppresses a token; .docx is read. On pre-fix source this file fails at import.
"""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import retraction_scan as rs  # noqa: E402
import retraction_register as rr  # noqa: E402


def run(args: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = rs.main(args)
    return rc, buf.getvalue()


class Scan(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rows = rr.value_rows()
        cls.num = next(n for r in rows for n in r.numbers)          # a real retracted decimal
        cls.hash = next(h for r in rows for h in r.hashes)           # a real retracted hash

    def test_whole_token_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "doc.md"
            f.write_text(f"the gain was +{self.num}pp; and hash {self.hash} was retracted; but 1{self.num}7 is another number\n", encoding="utf-8")
            rc, out = run([str(f)])
            self.assertEqual(rc, 1)
            self.assertIn(f"`{self.num}`", out)
            self.assertIn(self.hash[:12], out)
            self.assertEqual(out.count("L1:"), 2)                  # two hits on the line, not three

    def test_clean_file_is_not_a_certificate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "clean.md"
            f.write_text("nothing retracted here: 12345 and 0.5\n", encoding="utf-8")
            rc, out = run([str(f)])
            self.assertEqual(rc, 0)
            self.assertIn("not a certificate", out)

    def test_allow_and_docx(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "paper.docx"
            xml = (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f'<w:body><w:p><w:r><w:t>result {self.num} pp</w:t></w:r></w:p></w:body></w:document>'
            )
            with zipfile.ZipFile(d, "w") as z:
                z.writestr("word/document.xml", xml)
            rc, out = run([str(d)])
            self.assertEqual(rc, 1)
            rc2, _ = run(["--allow", self.num, str(d)])
            self.assertEqual(rc2, 0)

    def test_missing_requested_path_is_an_inspection_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing.md"
            rc, out = run([str(missing)])
            self.assertNotEqual(rc, 0)
            self.assertIn("[INSPECTION_FAILED]", out)
            self.assertIn(str(missing), out)
            self.assertIn("scanned 0 file(s)", out)

    def test_unreadable_requested_file_is_an_inspection_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "unreadable.md"
            f.write_text("content", encoding="utf-8")
            original_read_text = Path.read_text

            def selective_read_text(path: Path, *args, **kwargs) -> str:
                if path == f:
                    raise OSError("denied")
                return original_read_text(path, *args, **kwargs)

            with patch.object(Path, "read_text", autospec=True, side_effect=selective_read_text):
                rc, out = run([str(f)])
            self.assertNotEqual(rc, 0)
            self.assertIn("[INSPECTION_FAILED]", out)
            self.assertIn("denied", out)
            self.assertIn("scanned 0 file(s)", out)

    def test_malformed_docx_is_not_counted_as_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            broken = Path(td) / "broken.docx"
            broken.write_text("not a Word archive", encoding="utf-8")
            rc, out = run([str(broken)])
            self.assertNotEqual(rc, 0)
            self.assertIn("[INSPECTION_FAILED]", out)
            self.assertIn("scanned 0 file(s)", out)

    def test_malformed_document_xml_is_not_counted_as_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            broken = Path(td) / "broken.docx"
            with zipfile.ZipFile(broken, "w") as z:
                z.writestr("word/document.xml", "not XML at all")
            rc, out = run([str(broken)])
            self.assertEqual(rc, 2)
            self.assertIn("[INSPECTION_FAILED]", out)
            self.assertIn("scanned 0 file(s)", out)

    def test_mixed_batch_preserves_hits_and_file_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            hit = Path(td) / "hit.md"
            hit.write_text(f"historical value {self.num}\n", encoding="utf-8")
            broken = Path(td) / "broken.docx"
            broken.write_text("not a Word archive", encoding="utf-8")
            rc, out = run([str(hit), str(broken)])
            self.assertNotEqual(rc, 0)
            self.assertIn("[RETRACTED]", out)
            self.assertIn(f"`{self.num}`", out)
            self.assertIn("[INSPECTION_FAILED]", out)
            self.assertIn("scanned 1 file(s)", out)
            self.assertIn("1 inspection failure(s)", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
