#!/usr/bin/env python3
"""archive_desktop.py -- move Desktop clutter into the archive root, verified, never lossy.

Jon 2026-09-05: "please make sure they are archived as they are causing clutter and confusion."
Archive-cleanup plan rule: nothing is deleted; a physical move happens only after a verified
copy. For each named Desktop entry this tool:
  1. refuses if the entry is (or contains) a git checkout (.git file/dir) -- those are moved by
     the Phase 5 worktree protocol with `git worktree repair`, never by a file copy;
  2. refuses the private-key directory by name;
  3. copies the entry with robocopy /E /COPY:DAT (timestamps preserved), then hashes EVERY file
     on both sides and compares counts and sha256;
  4. only if every hash matches, removes the source tree and appends a row to
     <archive>/manifest.json; otherwise leaves the source untouched and reports;
  5. maintains Desktop\\DESKTOP-ARCHIVE-INDEX.md -- one line per archived entry with its new path,
     file count, bytes and the manifest it is recorded in (one file on the Desktop replaces many).

    python scripts/archive_desktop.py --dry-run  <entry> [...]
    python scripts/archive_desktop.py --run      <entry> [...]
    python scripts/archive_desktop.py --restore-test <archived-relative-path>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

DESKTOP = Path(r"C:\Users\thisi\Desktop")
ARCHIVE = Path(r"D:\ptcg_archive\desktop")
INDEX = DESKTOP / "DESKTOP-ARCHIVE-INDEX.md"
KEY_DIR = "D0-production-keys-20260825"
# Jon 2026-09-06 ("why does the project folder still look so messy?"): the same verified move is
# needed for the hub's top level. --source-root / --archive-root / --index rebind the three
# module paths; every refusal (git checkout inside, key material) and every verification step is
# unchanged. The hub's tracked files are never touched by this tool (they move only through git).
NEVER_ARCHIVE = {".git", ".claude", ".codex", ".private-runtime", "PK-squads", ".codex-worktrees"}


def configure_roots(source_root: str | None, archive_root: str | None, index: str | None) -> None:
    global DESKTOP, ARCHIVE, INDEX
    if source_root:
        DESKTOP = Path(source_root)
    if archive_root:
        ARCHIVE = Path(archive_root)
    if index:
        INDEX = Path(index)
    elif source_root:
        INDEX = DESKTOP / "ARCHIVE-INDEX.md"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inert_git_file(g: Path) -> bool:
    """Census 2026-09-06 (#3482, class A): `uv` writes an EMPTY `.git` file into `sdists-v9` cache
    folders; git cannot read it (rc 128) and nothing points at it. Such a file is not a checkout and
    must not block an archive. A `.git` file that carries a `gitdir:` line IS a worktree link
    (resolvable or stranded) and still refuses: a stranded link is repaired with `git worktree
    repair`, never moved. A `.git` DIRECTORY is a full repository and always refuses."""
    try:
        head = g.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return False
    return "gitdir:" not in head


def contains_git(p: Path) -> str | None:
    if p.is_file():
        return None
    for root, dirs, files in os.walk(p):
        if ".git" in dirs:
            return root
        if ".git" in files and not inert_git_file(Path(root) / ".git"):
            return root
    return None


def contains_git_below_root(p: Path) -> str | None:
    """A git checkout strictly below the entry root (the root's own `.git` is expected when the
    entry IS a repository). Inert `.git` files never count."""
    root_git = str((p / ".git").resolve()) if (p / ".git").exists() else ""
    for r, dirs, files in os.walk(p):
        for cand in ([".git"] if ".git" in dirs else []) + ([".git"] if ".git" in files else []):
            g = Path(r) / cand
            if str(g.resolve()) == root_git:
                continue
            if g.is_file() and inert_git_file(g):
                continue
            return r
    return None


def lp(p: Path) -> Path:
    """Long-path form on Windows (\\\\?\\ prefix) so files deeper than 260 characters can be read.
    The hub's scratch trees exceed the limit (LongPathsEnabled=0); robocopy copies them but a plain
    os.walk cannot hash them, which read as a verification mismatch on 2026-09-06."""
    s = str(p)
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        return Path("\\\\?\\" + os.path.abspath(s))
    return p


def walk_files(p: Path) -> list[Path]:
    if p.is_file():
        return [p]
    out: list[Path] = []
    for root, _dirs, files in os.walk(lp(p)):
        for f in files:
            out.append(Path(root) / f)
    return out


def hash_tree(base: Path) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    lbase = lp(base)
    for f in walk_files(base):
        rel = f.name if base.is_file() else Path(str(f)).relative_to(lbase).as_posix()
        result[rel] = (f.stat().st_size, sha256_file(f))
    return result


def robocopy(src: Path, dst: Path) -> int:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return 0
    r = subprocess.run(["robocopy", str(src), str(dst), "/E", "/COPY:DAT", "/R:1", "/W:1", "/NFL", "/NDL", "/NJH", "/NJS"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode  # robocopy: < 8 means success


def tracked_by_git(src: Path) -> int:
    """How many files under src are tracked by the enclosing git checkout (0 if none, or if src is
    not inside a checkout). SKYNET 2026-09-06 06:42Z: the tool archived 16 TRACKED hub files whose
    `find` listing had been read as 'untracked', leaving the shared hub's working tree disagreeing
    with HEAD for two minutes. A tracked file leaves only through a reviewed `git rm` PR with
    tombstones; this tool moves untracked bytes only."""
    try:
        r = subprocess.run(["git", "-C", str(src.parent), "ls-files", "--", src.name],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return 0
    if r.returncode != 0:
        return 0
    return len([ln for ln in r.stdout.splitlines() if ln.strip()])


ALLOW_REPO_MOVE = False


def _clear_readonly(func, path, _exc):
    """git writes its loose objects read-only, so removing a verified repository source raises
    WinError 5 halfway through and leaves a half-deleted tree. Clear the bit and retry once; if it
    still fails, let the error propagate so the caller reports rather than silently half-removing."""
    os.chmod(path, 0o700)
    func(path)


def repo_identity(p: Path) -> dict | None:
    """HEAD, branch, origin and dirty count of a full repository directory, or None if the
    directory is not a readable repository. Census 2026-09-06 (#3482, class B): six full
    repositories sit inside the hub (four Leela Chess Zero clones, one with no remote, one owned by
    the Codex sandbox user). A full repository carries its own `.git` DIRECTORY, so a whole-tree
    move keeps it intact — the stranding rule is about `.git` link FILES, which still refuse. The
    identity is read before the move and re-read after, and a mismatch fails the archive."""
    if not (p / ".git").is_dir():
        return None
    def g(*args: str) -> str:
        try:
            r = subprocess.run(["git", "-C", str(p), *args], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=300)
        except (OSError, subprocess.SubprocessError):
            return "(error)"
        return r.stdout.strip() if r.returncode == 0 else f"(rc {r.returncode})"
    porcelain = g("status", "--porcelain")
    return {"head": g("rev-parse", "HEAD"), "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
            "origin": g("remote", "get-url", "origin"),
            "dirty": 0 if porcelain.startswith("(") else len([l for l in porcelain.splitlines() if l.strip()])}


def archive_one(name: str, stamp: str, dry: bool) -> dict:
    src = DESKTOP / name
    row: dict = {"entry": name, "source": str(src), "stamp": stamp}
    if not src.exists():
        row["result"] = "SKIPPED: source missing"
        return row
    if KEY_DIR in name:
        row["result"] = "REFUSED: private key material is flag-only"
        return row
    ident = repo_identity(src) if ALLOW_REPO_MOVE else None
    if ident is not None:
        # A full repository at the top of this entry, moved whole under --allow-repo-move. Its own
        # `.git` directory travels with it; identity is verified at the destination below. Nested
        # checkouts DEEPER than the entry root still refuse, so a repo containing a worktree link
        # is not moved by this path.
        deeper = contains_git_below_root(src)
        if deeper:
            row["result"] = f"REFUSED: a further git checkout at {deeper} below the repository root -- worktree protocol, not a file move"
            return row
        row["repo_identity_before"] = ident
    else:
        g = contains_git(src)
        if g:
            row["result"] = f"REFUSED: contains a git checkout at {g} -- Phase 5 worktree protocol, not a file move"
            return row
    tracked = tracked_by_git(src)
    if tracked:
        row["result"] = f"REFUSED: {tracked} file(s) under this entry are tracked by git -- retire them by a reviewed `git rm` PR with tombstones, never by a file move"
        return row
    files = walk_files(src)
    row["files"] = len(files)
    row["bytes"] = sum(f.stat().st_size for f in files)
    dst = ARCHIVE / stamp / name
    row["destination"] = str(dst)
    if dry:
        row["result"] = "DRY-RUN: would copy, verify, then remove source"
        return row
    if src.is_dir() and not files:
        # An empty directory holds no bytes; the ITEM is still recorded: the destination is created
        # empty, the manifest row names it, and only then is the empty source removed.
        lp(dst).mkdir(parents=True, exist_ok=True)
        row["sha256_index"] = {}
        row["result"] = "COPIED_VERIFIED: empty directory recorded; source removal pending"
        _upsert_manifest_row(stamp, row)
        try:
            for root, dirs, _files in os.walk(lp(src), topdown=False):
                for d in dirs:
                    os.rmdir(os.path.join(root, d))
            os.rmdir(lp(src))
            row["result"] = "ARCHIVED: empty directory recorded in the archive; source removed"
        except OSError as exc:
            row["result"] = f"ARCHIVED_COPY_ONLY: empty directory recorded; source removal denied ({exc.__class__.__name__}); left in place"
        _upsert_manifest_row(stamp, row)
        return row
    if dst.exists():
        # A previous run copied but could not verify (long paths). Verify the existing copy now;
        # remove the source only if every file matches; otherwise leave both and report.
        a = hash_tree(src)
        b = hash_tree(dst)
        missing_or_diff = [k for k in a if a[k] != b.get(k)]
        extras = [k for k in b if k not in a]
        if not missing_or_diff:
            # every source file is present in the destination with the same bytes; extra files in
            # the destination (left by an earlier interrupted copy) are recorded, never a refusal
            row["sha256_index"] = {k: v[1] for k, v in a.items()}
            if extras:
                row["destination_extras"] = extras[:20]
                row["destination_extras_count"] = len(extras)
            row["result"] = "COPIED_VERIFIED: pre-existing destination verified; source removal pending"
            _upsert_manifest_row(stamp, row)
            try:
                shutil.rmtree(lp(src)) if src.is_dir() else lp(src).unlink()
                row["result"] = "ARCHIVED: pre-existing copy verified by sha256 on every file; source removed"
            except OSError as exc:
                row["result"] = f"ARCHIVED_COPY_ONLY: verified copy exists; source removal denied ({exc.__class__.__name__}); left in place"
            _upsert_manifest_row(stamp, row)
            return row
        row["result"] = f"REFUSED: destination exists and differs ({len([k for k in a if a[k] != b.get(k)])} differ); both left in place"
        return row
    rc = robocopy(src, dst)
    if rc >= 8:
        row["result"] = f"FAILED: robocopy rc {rc}; source untouched"
        return row
    a = hash_tree(src)
    b = hash_tree(dst)
    mismatch = [k for k in a if a[k] != b.get(k)]
    extra = [k for k in b if k not in a]
    if mismatch or extra or len(a) != len(b):
        row["result"] = f"FAILED: verification mismatch ({len(mismatch)} differ, {len(extra)} extra); source untouched"
        row["mismatch_sample"] = mismatch[:5]
        return row
    if row.get("repo_identity_before") is not None:
        # A repository is more than its bytes: re-read HEAD, branch, origin and dirty count at the
        # destination and refuse on any drift. Byte equality alone would pass a copy whose .git
        # failed to open there (permissions, long paths, an unreadable object store).
        after = repo_identity(dst)
        before = row["repo_identity_before"]
        if after is None or any(after.get(k) != before.get(k) for k in ("head", "branch", "origin", "dirty")):
            row["result"] = f"FAILED: repository identity differs at the destination (before {before}, after {after}); source untouched"
            row["repo_identity_after"] = after
            return row
        row["repo_identity_after"] = after
    row["sha256_index"] = {k: v[1] for k, v in a.items()}
    # ASTRA bulletin 2026-09-05 21:29Z: the manifest row must exist BEFORE the source is removed,
    # so an interruption between the two leaves a hashed record of what was verified.
    row["result"] = "COPIED_VERIFIED: manifest row written; source removal pending"
    _upsert_manifest_row(stamp, row)
    if src.is_file():
        src.unlink()
    else:
        shutil.rmtree(src, onerror=_clear_readonly)
    row["result"] = "ARCHIVED: copy verified by sha256 on every file; source removed"
    _upsert_manifest_row(stamp, row)
    return row


def _manifest_path(stamp: str) -> Path:
    return ARCHIVE / stamp / "manifest.json"


def _load_manifest(stamp: str) -> dict:
    mp = _manifest_path(stamp)
    if mp.exists():
        # utf-8-sig, not utf-8: a BOM makes json.loads raise "Unexpected UTF-8 BOM"
        # outright, and this function runs on EVERY archive operation via
        # _upsert_manifest_row, so one marked manifest would break archiving into that
        # stamp directory entirely. Measured 2026-09-06: two manifests under
        # D:/ptcg_archive carry a BOM. utf-8-sig reads unmarked files identically, so
        # this costs nothing and there is a test for both cases.
        return json.loads(mp.read_text(encoding="utf-8-sig"))
    return {"schema": "ptcg.archive_desktop/v1", "rows": []}


def _upsert_manifest_row(stamp: str, row: dict) -> None:
    manifest_dir = ARCHIVE / stamp
    manifest_dir.mkdir(parents=True, exist_ok=True)
    man = _load_manifest(stamp)
    rows = [r for r in man["rows"] if not (r.get("entry") == row["entry"] and r.get("stamp") == row["stamp"])]
    rows.append(row)
    man["rows"] = rows

    # Atomic write: write to temporary file in the same directory, flush & fsync, then replace
    final_path = _manifest_path(stamp)
    tmp_path = manifest_dir / f".manifest.json.tmp.{os.getpid()}"
    content = json.dumps(man, indent=1)
    with open(tmp_path, "w", encoding="utf-8") as fh:
        fh.write(content)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, final_path)


def write_index(rows: list[dict], stamp: str) -> None:
    lines = []
    if INDEX.exists():
        lines = INDEX.read_text(encoding="utf-8").splitlines()
    if not lines:
        lines = ["# DESKTOP ARCHIVE INDEX", "",
                 "Entries moved off this Desktop into `D:\\ptcg_archive\\desktop\\<date>\\` by `scripts/archive_desktop.py`",
                 "(archive-cleanup plan, never delete: every file was copied, hashed on both sides, and only then removed here).",
                 "Restore: copy the entry back from the path below; hashes are in that date's `manifest.json`.", "",
                 "| archived | entry | files | bytes | now at |", "|---|---|---|---|---|"]
    for r in rows:
        if r.get("result", "").startswith("ARCHIVED"):
            lines.append(f"| {stamp} | `{r['entry']}` | {r['files']} | {r['bytes']:,} | `{r['destination']}` |")
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entries", nargs="*")
    ap.add_argument("--entries-file", help="one entry name per line (for long lists)")
    ap.add_argument("--source-root", help="directory whose top-level entries are archived (default: the Desktop)")
    ap.add_argument("--archive-root", help="archive root (default: D:\\ptcg_archive\\desktop)")
    ap.add_argument("--index", help="index markdown to maintain (default: <source-root>\\ARCHIVE-INDEX.md)")
    ap.add_argument("--allow-repo-move", action="store_true",
                    help="move an entry that IS a full git repository (its own .git DIRECTORY travels with it); "
                         "HEAD/branch/origin/dirty are verified at the destination. Worktree link files and "
                         "checkouts below the entry root still refuse.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--restore-test", metavar="REL")
    a = ap.parse_args(argv)
    global ALLOW_REPO_MOVE
    ALLOW_REPO_MOVE = bool(a.allow_repo_move)
    configure_roots(a.source_root, a.archive_root, a.index)
    if a.entries_file:
        a.entries += [ln.strip() for ln in Path(a.entries_file).read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    refused_names = [e for e in a.entries if e in NEVER_ARCHIVE]
    a.entries = [e for e in a.entries if e not in NEVER_ARCHIVE]
    for e in refused_names:
        print(f"REFUSED by name (tool-local state, live runtime, or squad container): {e}")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    stamp = time.strftime("%Y-%m-%d")
    if a.restore_test:
        # <stamp>/<entry>[/<rel path inside the entry>] -- compare a fresh copy against the SAVED
        # hash in that stamp's manifest (ASTRA: a copy-vs-copy check proves nothing about the record).
        parts = Path(a.restore_test).parts
        if len(parts) < 2:
            print("RESTORE_TEST FAIL: give <stamp>/<entry>[/<path inside entry>]")
            return 1
        stamp_r, entry, inner = parts[0], parts[1], "/".join(parts[2:])
        man = _load_manifest(stamp_r)
        # Allow ARCHIVED or COPIED_VERIFIED (if source removal finished or crashed before terminal record)
        row = next((r for r in man["rows"] if r.get("entry") == entry and str(r.get("result", "")).startswith(("ARCHIVED", "COPIED_VERIFIED"))), None)
        if row is None:
            print("RESTORE_TEST FAIL: no ARCHIVED or COPIED_VERIFIED manifest row for", entry)
            return 1
        index = row.get("sha256_index", {})
        src = ARCHIVE / a.restore_test
        if src.is_dir() and not inner:
            # SKYNET 2026-09-06 11:1xZ: this branch did not exist. `--restore-test` required the
            # target to resolve to a single FILE, so EVERY directory entry — which is almost
            # everything archived on 09-05/09-06 — answered "no saved hash or archived file" and
            # looked like a broken archive. The fixture only ever exercised a one-file entry. A
            # directory is restore-tested by its whole index: re-hash every archived file against
            # the hash recorded at archive time, then copy the tree out and re-hash the copy, so
            # both the record and a real restore are proven rather than a copy compared to itself.
            if not index:
                print("RESTORE_TEST FAIL: manifest row for", entry, "carries no sha256_index")
                return 1
            tmp = ARCHIVE / "_restore_test" / entry
            if tmp.exists():
                shutil.rmtree(lp(tmp), onerror=_clear_readonly)
            tmp.parent.mkdir(parents=True, exist_ok=True)
            rc_copy = robocopy(src, tmp)
            if rc_copy >= 8:
                print(f"RESTORE_TEST FAIL: could not copy the archived tree out (robocopy rc {rc_copy})")
                return 1
            arch_bad = [k for k, want in index.items()
                        if not lp(src / k).exists() or sha256_file(lp(src / k)) != want]
            rest_bad = [k for k, want in index.items()
                        if not lp(tmp / k).exists() or sha256_file(lp(tmp / k)) != want]
            extra = [str(Path(str(f)).relative_to(lp(src)).as_posix()) for f in walk_files(src)
                     if Path(str(f)).relative_to(lp(src)).as_posix() not in index]
            shutil.rmtree(lp(tmp), onerror=_clear_readonly)
            ok_all = not arch_bad and not rest_bad
            print("RESTORE_TEST", "PASS" if ok_all else "FAIL", a.restore_test,
                  f"files={len(index)} archived_matches={len(index) - len(arch_bad)} "
                  f"restored_copy_matches={len(index) - len(rest_bad)} unrecorded_extras={len(extra)}")
            for k in (arch_bad + rest_bad)[:5]:
                print("   MISMATCH", k)
            return 0 if ok_all else 1
        key = inner or Path(entry).name
        saved = index.get(key)
        if saved is None or not src.is_file():
            print("RESTORE_TEST FAIL: no saved hash or archived file for", a.restore_test)
            return 1
        tmp = ARCHIVE / "_restore_test" / src.name
        tmp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, tmp)
        archived_ok = sha256_file(src) == saved
        restored_ok = sha256_file(tmp) == saved
        print("RESTORE_TEST", "PASS" if (archived_ok and restored_ok) else "FAIL", a.restore_test,
              f"saved={saved[:16]} archived_matches={archived_ok} restored_copy_matches={restored_ok}")
        return 0 if (archived_ok and restored_ok) else 1
    rows = [archive_one(e, stamp, a.dry_run) for e in a.entries]
    if not a.dry_run:
        # rows were upserted into the manifest by archive_one before each removal;
        # only the Desktop index remains to write.
        write_index(rows, stamp)
    for r in rows:
        print(f"{r['entry']}: {r.get('result')}  files={r.get('files', '-')} bytes={r.get('bytes', '-')}")
    return 0 if all(str(r.get("result", "")).startswith(("ARCHIVED", "DRY-RUN")) for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
