#!/usr/bin/env python3
"""test_archive_desktop.py -- verify atomic manifest writing, interruption safety, and recovery.

Tests four scenarios in isolated temporary fixtures (zero touches to real Desktop or archive):
  1. Normal success: copy, verify, write COPIED_VERIFIED, remove source, write ARCHIVED atomically.
  2. Interruption before atomic replacement: prior manifest record survives intact.
  3. Interruption after source removal (COPIED_VERIFIED state): restore check succeeds against saved hashes.
  4. Corrupted archived bytes: restore check correctly refuses and fails.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import scripts.archive_desktop as ad


class TestArchiveDesktopAtomic(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.desktop = self.root / "Desktop"
        self.archive = self.root / "archive"
        self.desktop.mkdir(parents=True)
        self.archive.mkdir(parents=True)

        self.patch_desktop = patch.object(ad, "DESKTOP", self.desktop)
        self.patch_archive = patch.object(ad, "ARCHIVE", self.archive)
        self.patch_index = patch.object(ad, "INDEX", self.desktop / "DESKTOP-ARCHIVE-INDEX.md")
        self.patch_desktop.start()
        self.patch_archive.start()
        self.patch_index.start()

    def tearDown(self):
        self.patch_index.stop()
        self.patch_archive.stop()
        self.patch_desktop.stop()
        self.temp_dir.cleanup()

    def test_normal_success(self):
        src_file = self.desktop / "notes.txt"
        src_file.write_text("hello world", encoding="utf-8")

        res = ad.archive_one("notes.txt", "2026-09-05", dry=False)
        self.assertTrue(res["result"].startswith("ARCHIVED"))
        self.assertFalse(src_file.exists())
        dst_file = self.archive / "2026-09-05" / "notes.txt"
        self.assertTrue(dst_file.exists())

        # Check manifest
        man = ad._load_manifest("2026-09-05")
        self.assertEqual(len(man["rows"]), 1)
        self.assertTrue(man["rows"][0]["result"].startswith("ARCHIVED"))

        # Restore test
        rc = ad.main(["--restore-test", "2026-09-05/notes.txt"])
        self.assertEqual(rc, 0)

    def test_inert_git_file_does_not_block_but_links_and_repos_do(self):
        """Census 2026-09-06 (#3482) class A: uv writes an empty `.git` FILE into sdists-v9 caches.
        Three cases: empty .git file → archived; `.git` file with a gitdir: line (a worktree link,
        even a stranded one) → REFUSED; `.git` DIRECTORY → REFUSED. On pre-fix source the first
        case is REFUSED and this test fails."""
        cache = self.desktop / "uv-cache" / "sdists-v9"
        cache.mkdir(parents=True)
        (cache / ".git").write_text("", encoding="utf-8")
        (cache / "pkg.tar.gz").write_bytes(b"x" * 10)
        def portable_directory_copy(src, dst):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return 0

        # Production uses Windows robocopy for directories. Keep this fixture
        # platform-neutral while still exercising copy verification and removal.
        with patch.object(ad, "robocopy", side_effect=portable_directory_copy):
            res = ad.archive_one("uv-cache", "2026-09-06", dry=False)
        self.assertTrue(res["result"].startswith("ARCHIVED"), res["result"])
        self.assertFalse((self.desktop / "uv-cache").exists())

        link = self.desktop / "wt"
        link.mkdir()
        (link / ".git").write_text("gitdir: C:/nowhere/.git/worktrees/wt\n", encoding="utf-8")
        (link / "f.txt").write_text("x", encoding="utf-8")
        res2 = ad.archive_one("wt", "2026-09-06", dry=False)
        self.assertTrue(res2["result"].startswith("REFUSED: contains a git checkout"), res2["result"])
        self.assertTrue((link / "f.txt").exists())

        repo = self.desktop / "repo"
        (repo / ".git").mkdir(parents=True)
        (repo / "g.txt").write_text("x", encoding="utf-8")
        res3 = ad.archive_one("repo", "2026-09-06", dry=False)
        self.assertTrue(res3["result"].startswith("REFUSED: contains a git checkout"), res3["result"])

    def test_repo_move_requires_the_flag_and_verifies_identity(self):
        """Census 2026-09-06 (#3482) class B: six full repositories sit inside the hub. A full repo
        carries its own `.git` DIRECTORY, so a whole-tree move keeps it intact — but only with
        --allow-repo-move, only when nothing deeper is a checkout, and only if HEAD/branch/origin/
        dirty match at the destination. On pre-fix source the flag does not exist and the move is
        REFUSED."""
        import subprocess
        repo = self.desktop / "clone"
        repo.mkdir()
        def git(*a, cwd=None):
            subprocess.run(["git", "-C", str(cwd or repo), *a], check=True, capture_output=True)
        git("init", "-q")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "t")
        (repo / "a.txt").write_text("x", encoding="utf-8")
        git("add", "a.txt")
        git("commit", "-q", "-m", "one")
        before = ad.repo_identity(repo)
        self.assertIsNotNone(before)
        self.assertNotIn("(", before["head"])

        # without the flag the repository refuses, exactly as before
        res = ad.archive_one("clone", "2026-09-06", dry=False)
        self.assertTrue(res["result"].startswith("REFUSED: contains a git checkout"), res["result"])
        self.assertTrue((repo / "a.txt").exists())

        def portable_copy(src, dst):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return 0
        with patch.object(ad, "ALLOW_REPO_MOVE", True), patch.object(ad, "robocopy", side_effect=portable_copy):
            res2 = ad.archive_one("clone", "2026-09-06", dry=False)
        self.assertTrue(res2["result"].startswith("ARCHIVED"), res2["result"])
        self.assertFalse(repo.exists())
        moved = self.archive / "2026-09-06" / "clone"
        after = ad.repo_identity(moved)
        self.assertEqual(after["head"], before["head"])
        self.assertEqual(res2["repo_identity_after"]["head"], before["head"])

        # a checkout BELOW the entry root still refuses even with the flag
        outer = self.desktop / "outer"
        (outer / ".git").mkdir(parents=True)
        inner = outer / "nested"
        inner.mkdir()
        (inner / ".git").write_text("gitdir: C:/nowhere\n", encoding="utf-8")
        with patch.object(ad, "ALLOW_REPO_MOVE", True):
            res3 = ad.archive_one("outer", "2026-09-06", dry=False)
        self.assertTrue(res3["result"].startswith("REFUSED: a further git checkout"), res3["result"])
        self.assertTrue(inner.exists())

    def test_refuses_git_tracked_entries_and_archives_untracked_ones(self):
        """SKYNET 2026-09-06: 16 tracked hub files were archived as 'untracked' off a `find` listing.
        Inside a real checkout the tool must refuse an entry with tracked files and still archive
        an untracked sibling. On pre-fix source the tracked entry is ARCHIVED and this test fails."""
        import subprocess
        def git(*a):
            subprocess.run(["git", "-C", str(self.desktop), *a], check=True, capture_output=True)
        git("init", "-q")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "t")
        tracked_dir = self.desktop / "pkg"
        tracked_dir.mkdir()
        (tracked_dir / "a.md").write_text("tracked", encoding="utf-8")
        git("add", "pkg/a.md")
        git("commit", "-q", "-m", "add")
        (self.desktop / "loose.txt").write_text("untracked", encoding="utf-8")

        res = ad.archive_one("pkg", "2026-09-06", dry=False)
        self.assertTrue(res["result"].startswith("REFUSED: 1 file(s) under this entry are tracked by git"), res["result"])
        self.assertTrue((tracked_dir / "a.md").exists())          # nothing moved
        self.assertFalse((self.archive / "2026-09-06" / "pkg").exists())

        res2 = ad.archive_one("loose.txt", "2026-09-06", dry=False)
        self.assertTrue(res2["result"].startswith("ARCHIVED"), res2["result"])
        self.assertFalse((self.desktop / "loose.txt").exists())
        # the dry run refuses the same way, before touching anything
        res3 = ad.archive_one("pkg", "2026-09-06", dry=True)
        self.assertTrue(res3["result"].startswith("REFUSED"), res3["result"])

    def test_interruption_before_atomic_replacement(self):
        # Establish prior valid manifest
        prior_row = {"entry": "prior.txt", "stamp": "2026-09-05", "result": "ARCHIVED", "sha256_index": {}}
        ad._upsert_manifest_row("2026-09-05", prior_row)
        man_before = ad._load_manifest("2026-09-05")
        self.assertEqual(len(man_before["rows"]), 1)

        def crash_replace(src, dst):
            raise KeyboardInterrupt("Simulated crash right before os.replace")

        with patch("os.replace", side_effect=crash_replace):
            new_row = {"entry": "new.txt", "stamp": "2026-09-05", "result": "ARCHIVED"}
            with self.assertRaises(KeyboardInterrupt):
                ad._upsert_manifest_row("2026-09-05", new_row)

        # Verify prior manifest survived completely uncorrupted
        man_after = ad._load_manifest("2026-09-05")
        self.assertEqual(len(man_after["rows"]), 1)
        self.assertEqual(man_after["rows"][0]["entry"], "prior.txt")

    def test_interruption_after_source_removal(self):
        # Simulate: source was removed, manifest holds COPIED_VERIFIED, but final ARCHIVED write did not happen
        src_file = self.desktop / "important.doc"
        src_file.write_text("confidential draft", encoding="utf-8")
        h = ad.sha256_file(src_file)

        dst_file = self.archive / "2026-09-05" / "important.doc"
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        src_file.unlink()

        copied_row = {
            "entry": "important.doc",
            "stamp": "2026-09-05",
            "result": "COPIED_VERIFIED: manifest row written; source removal pending",
            "sha256_index": {"important.doc": h}
        }
        ad._upsert_manifest_row("2026-09-05", copied_row)

        # Restore check must recognize COPIED_VERIFIED and pass against saved hash
        rc = ad.main(["--restore-test", "2026-09-05/important.doc"])
        self.assertEqual(rc, 0)

    def test_corrupted_archived_bytes(self):
        src_file = self.desktop / "audit.log"
        src_file.write_text("valid log content", encoding="utf-8")
        ad.archive_one("audit.log", "2026-09-05", dry=False)

        # Corrupt the archived file
        dst_file = self.archive / "2026-09-05" / "audit.log"
        dst_file.write_text("corrupted content", encoding="utf-8")

        # Restore check must refuse and fail
        rc = ad.main(["--restore-test", "2026-09-05/audit.log"])
        self.assertEqual(rc, 1)

    def test_restore_test_covers_directory_entries(self):
        """SKYNET 2026-09-06 11:1xZ: --restore-test required the target to resolve to a single FILE,
        so EVERY directory entry — which is almost everything archived on 09-05/09-06 — answered
        "no saved hash or archived file" and read as a broken archive. The existing fixtures only
        ever exercised one-file entries. A directory is restore-tested by its whole index: every
        archived file re-hashed against the record, then the tree copied out and re-hashed, so both
        the record and a real restore are proven. On pre-fix source the PASS case returns 1."""
        d = self.desktop / "bundle"
        (d / "inner").mkdir(parents=True)
        (d / "a.txt").write_text("alpha", encoding="utf-8")
        (d / "inner" / "b.txt").write_text("beta", encoding="utf-8")

        def portable_copy(src, dst):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return 0

        with patch.object(ad, "robocopy", side_effect=portable_copy):
            res = ad.archive_one("bundle", "2026-09-06", dry=False)
            self.assertTrue(res["result"].startswith("ARCHIVED"), res["result"])
            self.assertEqual(ad.main(["--restore-test", "2026-09-06/bundle"]), 0)
            # a single corrupted file inside the tree must fail the whole restore test
            (self.archive / "2026-09-06" / "bundle" / "inner" / "b.txt").write_text("tampered", encoding="utf-8")
            self.assertEqual(ad.main(["--restore-test", "2026-09-06/bundle"]), 1)
            # naming one file inside the entry still works through the single-file path
            self.assertEqual(ad.main(["--restore-test", "2026-09-06/bundle/a.txt"]), 0)



class TestManifestEncoding(unittest.TestCase):
    """A byte-order mark must not make an archive manifest unreadable.

    _load_manifest runs on every archive operation through _upsert_manifest_row, so a
    manifest json.loads() refuses is not a cosmetic problem: it breaks archiving into
    that stamp directory entirely. Two manifests under D:/ptcg_archive were measured
    carrying a BOM on 2026-09-06.
    """

    def _with_archive(self, root: Path):
        return patch.object(ad, "ARCHIVE", root)

    def test_manifest_with_a_bom_is_readable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "2026-09-06").mkdir(parents=True)
            (root / "2026-09-06" / "manifest.json").write_bytes(
                b"\xef\xbb\xbf" + b'{"schema": "ptcg.archive_desktop/v1", "rows": [{"a": 1}]}'
            )
            with self._with_archive(root):
                man = ad._load_manifest("2026-09-06")
            self.assertEqual(man["rows"], [{"a": 1}],
                             "a BOM must not hide the rows this manifest records")

    def test_manifest_without_a_bom_still_reads(self):
        """Positive control: the encoding change must not break the normal case."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "2026-09-06").mkdir(parents=True)
            (root / "2026-09-06" / "manifest.json").write_bytes(
                b'{"schema": "ptcg.archive_desktop/v1", "rows": [{"b": 2}]}'
            )
            with self._with_archive(root):
                man = ad._load_manifest("2026-09-06")
            self.assertEqual(man["rows"], [{"b": 2}])

    def test_absent_manifest_still_returns_an_empty_shell(self):
        with tempfile.TemporaryDirectory() as td:
            with self._with_archive(Path(td)):
                man = ad._load_manifest("2026-09-06")
            self.assertEqual(man["rows"], [])
            self.assertEqual(man["schema"], "ptcg.archive_desktop/v1")

if __name__ == "__main__":
    unittest.main()
