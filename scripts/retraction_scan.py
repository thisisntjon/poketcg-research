#!/usr/bin/env python3
"""retraction_scan.py -- the retraction firewall: scan any document (md, txt, json, docx) for numbers
and hashes the register has retracted, before it leaves the building.

Jon 2026-09-06 (repurposing the inventory): "a retraction firewall for publications". The register
(workflow/canon/RETRACTIONS.md, read by retraction_register.py) is the only source of truth; this
tool adds nothing to it. A hit is reported with the file, the line, the token and the register's
"use instead" value. A miss is NOT a certificate (the register can be incomplete); the tool says so.

    python scripts/retraction_scan.py <file-or-dir> [...]      # exit 1 on any hit
    python scripts/retraction_scan.py --allow 5.45 <paths>     # tokens to ignore (e.g. a number that is
                                                               # also a legitimate different quantity)

Matching: each retracted decimal must appear as a whole numeric token (so 7.82 does not match 17.82,
and 46.2 does not match 46.21); each retracted hash matches by 12+ hex prefix. .docx is read from its
word/document.xml; no external packages.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import retraction_register as rr  # noqa: E402

TEXT_EXT = {".md", ".txt", ".json", ".jsonl", ".csv", ".rst", ".html", ".tex"}


class InspectionError(Exception):
    """A requested candidate could not be inspected."""


def read_text(p: Path) -> str:
    if p.suffix.lower() == ".docx":
        try:
            with zipfile.ZipFile(p) as z:
                root = ET.fromstring(z.read("word/document.xml"))
        except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            raise InspectionError(str(exc) or exc.__class__.__name__) from exc
        paragraphs = []
        for paragraph in (node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "p"):
            paragraphs.append(
                "".join(
                    node.text or ""
                    for node in paragraph.iter()
                    if node.tag.rsplit("}", 1)[-1] == "t"
                )
            )
        return "\n".join(paragraphs)
    if p.suffix.lower() in TEXT_EXT:
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise InspectionError(str(exc) or exc.__class__.__name__) from exc
    return ""


def patterns(allow: set[str]) -> list[tuple[re.Pattern, str, str]]:
    """(compiled pattern, token, use-instead) for every retracted value token."""
    out = []
    for row in rr.require_rows():
        for n in row.numbers:
            if n in allow:
                continue
            out.append((re.compile(r"(?<![\d.])" + re.escape(n) + r"(?![\d.])"), n, row.use_instead))
        for h in row.hashes:
            if h in allow:
                continue
            out.append((re.compile(r"(?<![0-9a-f])" + re.escape(h[:12]) + r"[0-9a-f]*(?![0-9a-f])", re.I), h[:12], row.use_instead))
    return out


def scan_file(p: Path, pats) -> list[tuple[int, str, str, str]]:
    hits = []
    text = read_text(p)
    if not text:
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        for pat, tok, instead in pats:
            if pat.search(line):
                hits.append((i, tok, instead, line.strip()[:160]))
    return hits


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--allow", action="append", default=[], help="token to ignore (repeatable)")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    try:
        pats = patterns(set(a.allow))
    except rr.RegisterUnavailable as exc:
        print(f"[REGISTER_UNAVAILABLE] cannot scan: {exc}")
        return 2
    files: list[Path] = []
    failures: list[tuple[Path, str]] = []
    for raw in a.paths:
        p = Path(raw)
        if p.is_dir():
            files += [f for f in sorted(p.rglob("*")) if f.is_file() and (f.suffix.lower() in TEXT_EXT or f.suffix.lower() == ".docx")]
        elif p.is_file():
            files.append(p)
        else:
            failures.append((p, "requested path does not exist or is not a file/directory"))
    total = 0
    scanned = 0
    for f in files:
        try:
            hits = scan_file(f, pats)
        except InspectionError as exc:
            failures.append((f, str(exc)))
            continue
        scanned += 1
        if hits:
            total += len(hits)
            print(f"[RETRACTED] {f}")
            for ln, tok, instead, line in hits:
                print(f"  L{ln}: `{tok}` -> use instead: {instead[:80] or '(see register)'}\n        {line}")
    for path, reason in failures:
        print(f"[INSPECTION_FAILED] {path}: {reason}")
    summary = f"scanned {scanned} file(s) against {len(pats)} retracted tokens: {total} hit(s); {len(failures)} inspection failure(s). "
    if failures:
        summary += "INSPECTION INCOMPLETE; DO NOT TREAT AS CLEAR."
    elif total:
        summary += "FIX BEFORE PUBLISHING."
    else:
        summary += "no retracted token found (not a certificate: the register can be incomplete)."
    print(summary)
    return 2 if failures else (1 if total else 0)


if __name__ == "__main__":
    sys.exit(main())
