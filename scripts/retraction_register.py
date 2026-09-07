#!/usr/bin/env python3
"""retraction_register.py -- the machine-readable view of workflow/canon/RETRACTIONS.md.

The register's "Retracted values" table is the ONLY source of truth for which numbers
are banned from citation. Before this module, two consumers each carried their own
copy: `onboard_check.retracted_values()` parsed only rows whose first cell is a single
bare-backticked decimal (6 of 11 rows), and `query_inventory.py` read a hand-maintained
JSON quarantine holding the same 6. Both certified `+9.35pp`, `+8.26pp`, `46.2%`, the
Fisher/Clopper-Pearson row and the two hash rows as clean. This module parses every
row of the table and every numeric / hash token inside its first cell, so a new
retraction row is banned the moment it lands in canon -- no second file to update.

    python scripts/retraction_register.py            # list every parsed row
    python scripts/retraction_register.py 9.35       # exit 1 if retracted
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
RETRACTIONS = REPO / "workflow" / "canon" / "RETRACTIONS.md"

VALUES_HEADING = "## retracted values"
CLAIMS_HEADING = "## retracted claims"

_BACKTICK = re.compile(r"`([^`]+)`")
# Decimals only. Integer tokens inside the value cell (`51/63`, `n=400`) are descriptive
# counts the register tells you to quote INSTEAD; the banned figures all carry a point.
_DECIMAL = re.compile(r"(?<![\d.])[+-]?(\d+\.\d+)(?![\d.])")
# 12..64 lowercase hex = short/long sha256 or git oid; shorter runs are ambiguous.
_HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{12,64}(?![0-9a-f])")


@dataclass(frozen=True)
class Row:
    section: str            # "values" | "claims"
    raw: str                # first cell, verbatim
    use_instead: str        # second cell for values rows; "" for claims rows
    why: str
    retracted: str          # the date cell
    numbers: tuple[str, ...]   # normalised decimal tokens from backticked spans of `raw`
    hashes: tuple[str, ...]    # hex tokens (>=12 chars) from backticked spans of `raw`


def _cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


def _is_separator(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c) and any(cells)


def _tokens(cell: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    numbers: list[str] = []
    hashes: list[str] = []
    for span in _BACKTICK.findall(cell):
        for m in _DECIMAL.finditer(span):
            tok = m.group(1)
            if tok not in numbers:
                numbers.append(tok)
        for m in _HEX.finditer(span):
            tok = m.group(0)
            if tok not in hashes:
                hashes.append(tok)
    return tuple(numbers), tuple(hashes)


def _path(path: Path | None) -> Path:
    """Resolve the register path at CALL time so tests can rebind `RETRACTIONS`."""
    return Path(path) if path is not None else RETRACTIONS


def parse(path: Path | None = None) -> list[Row]:
    """Every body row of the values and claims tables, in file order."""
    path = _path(path)
    if not path.exists():
        return []
    rows: list[Row] = []
    section = ""
    header_seen = False
    saw_heading = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        low = line.strip().lower()
        if low.startswith("## "):
            saw_heading = True
            section = "values" if low.startswith(VALUES_HEADING) else (
                "claims" if low.startswith(CLAIMS_HEADING) else "")
            header_seen = False
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if not section:
            # Heading-less register (test fixtures, early drafts): a table whose header
            # row reads `| Value | Use instead | ... |` IS the values table.
            if (not saw_heading and len(cells) >= 4 and cells[0].lower() == "value"
                    and cells[1].lower().startswith("use")):
                section, header_seen = "values", True
            continue
        if not header_seen:
            header_seen = True          # column-name row
            continue
        if _is_separator(cells):
            continue
        if section == "values":
            if len(cells) < 4:
                continue
            raw, use_instead, why, retracted = cells[0], cells[1], cells[2], cells[3]
        else:
            if len(cells) < 3:
                continue
            raw, use_instead, why, retracted = cells[0], "", cells[1], cells[2]
        numbers, hashes = _tokens(raw) if section == "values" else ((), ())
        rows.append(Row(section, raw, use_instead, why, retracted, numbers, hashes))
    return rows


def value_rows(path: Path | None = None) -> list[Row]:
    return [r for r in parse(path) if r.section == "values"]


def normalise(query: str) -> str:
    """`+9.35pp` -> `9.35`; `46.2%` -> `46.2`; `ba51cc..` unchanged; whitespace stripped."""
    q = str(query).strip()
    q = re.sub(r"^[+\-−]", "", q)
    q = re.sub(r"(pp|%|mu|μ)$", "", q, flags=re.IGNORECASE).strip()
    return q


class RegisterUnavailable(RuntimeError):
    """The register file is absent or parses to zero value rows.

    ASTRA audit 2026-09-05: with the register absent the CLI printed `[CLEAN] ... (0 rows
    checked)` and exited 0 -- an empty register was silently a clean bill of health. An
    absent or empty register is an error, never an answer.
    """


def require_rows(path: Path | None = None) -> list[Row]:
    path = _path(path)
    if not path.exists():
        raise RegisterUnavailable(f"retraction register missing: {path}")
    rows = value_rows(path)
    if not rows:
        raise RegisterUnavailable(f"retraction register has no parseable value rows: {path}")
    return rows


NOT_A_CERTIFICATE = ("not in the retracted-values table -- this says only that the register "
                     "does not retract it; it is not a validity certificate")


def lookup(query: str, path: Path | None = None) -> list[Row]:
    """Rows that ban `query`. Decimals match exactly after normalisation; hex matches by
    prefix in either direction once >= 8 chars are given. Raises RegisterUnavailable when
    there is no register to consult."""
    q = normalise(query)
    hits: list[Row] = []
    for row in require_rows(path):
        if q in row.numbers:
            hits.append(row)
            continue
        ql = q.lower()
        if len(ql) >= 8 and re.fullmatch(r"[0-9a-f]+", ql):
            if any(h.startswith(ql) or ql.startswith(h) for h in row.hashes):
                hits.append(row)
    return hits


def banned_numbers(path: Path | None = None) -> list[tuple[str, str]]:
    """(number, use_instead) pairs -- the shape onboard_check's census consumes."""
    out: list[tuple[str, str]] = []
    for row in value_rows(path):
        for n in row.numbers:
            out.append((n, row.use_instead))
    return out


def format_rows(rows: Iterable[Row]) -> str:
    lines: list[str] = []
    for r in rows:
        head = ", ".join(r.numbers + r.hashes) or r.raw[:60]
        lines.append(f"[{r.section.upper()}] {head}  (retracted {r.retracted})")
        if r.use_instead:
            lines.append(f"    use instead: {r.use_instead}")
        lines.append(f"    why: {r.why[:200]}")
    return "\n".join(lines)


def utf8_stdout() -> None:
    """The register carries μ/σ; a cp1252 console (Windows default) must not crash on it."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass


ONBOARDING_SET = ("START-HERE.md", "AGENTS.md", "workflow/PLAN.md", "workflow/NOW.md",
                  "workflow/ACTIVE-COMMS.md", "workflow/canon/RETRACTIONS.md")
CENSUS_OUT = REPO / "workflow" / "inventories" / "RETRACTION-CENSUS.md"


def census(path: Path | None = None) -> tuple[str, dict]:
    """A GENERATED report of where each retracted token is still cited (tracked *.md), grouped by
    top-level directory, with the onboarding set separated. Report only: no citing file is edited
    (ARCHIVE-POLICY Why #3 keeps the false claim findable) and no gate is added before 2026-09-13
    (inventory roadmap Phase 3; adversarial review B-3)."""
    rows = require_rows(path)
    out_lines = ["# RETRACTION CENSUS (generated by scripts/retraction_register.py --census; do not hand-edit)", "",
                 "Per retracted token: tracked `*.md` files that still contain it, grouped by top-level directory. "
                 "The onboarding set is listed separately because it is what a fresh seat reads. Report only: nothing here is edited "
                 "(the register's rule is that a false claim stays findable); no count is a gate before 2026-09-13.", "",
                 "| token | use instead | total files | onboarding-set files | by top-level dir |", "|---|---|---|---|---|"]
    summary: dict = {"tokens": {}, "onboarding_set_total": 0}
    for row in rows:
        for tok in row.numbers + row.hashes:
            r = subprocess.run(["git", "grep", "-l", "-F", "--", tok, "--", "*.md"], cwd=str(REPO),
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
            files = [f.strip() for f in r.stdout.splitlines() if f.strip()]
            files = [f for f in files if f != "workflow/canon/RETRACTIONS.md"]
            by_top: dict[str, int] = {}
            for f in files:
                top = f.split("/", 1)[0] if "/" in f else "(root)"
                by_top[top] = by_top.get(top, 0) + 1
            onb = [f for f in files if f in ONBOARDING_SET]
            summary["tokens"][tok] = {"total": len(files), "onboarding_set": onb, "by_top": by_top}
            summary["onboarding_set_total"] += len(onb)
            top_txt = ", ".join(f"{k} {v}" for k, v in sorted(by_top.items(), key=lambda kv: -kv[1])[:6])
            out_lines.append(f"| `{tok[:16]}` | {row.use_instead[:50]} | {len(files)} | {len(onb)}{(' (' + ', '.join(onb) + ')') if onb else ''} | {top_txt} |")
    out_lines += ["", f"Onboarding-set citations in total: **{summary['onboarding_set_total']}** (target 0; reported, not gated). "
                  f"Tokens: {len(summary['tokens'])}. Tokens like `88.7` match unrelated numbers in prose; the count is a ceiling, not a defect count."]
    return "\n".join(out_lines) + "\n", summary


def main(argv: list[str]) -> int:
    utf8_stdout()
    if argv and argv[0] == "--census":
        try:
            text, summary = census()
        except RegisterUnavailable as exc:
            print(f"[REGISTER_UNAVAILABLE] census impossible: {exc}")
            return 2
        CENSUS_OUT.parent.mkdir(parents=True, exist_ok=True)
        CENSUS_OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"CENSUS written: {CENSUS_OUT.relative_to(REPO).as_posix()} tokens={len(summary['tokens'])} "
              f"onboarding_set_citations={summary['onboarding_set_total']}")
        return 0
    if not argv:
        rows = parse()
        print(f"{RETRACTIONS}: {len(rows)} rows "
              f"({sum(r.section == 'values' for r in rows)} values, "
              f"{sum(r.section == 'claims' for r in rows)} claims)")
        print(format_rows(rows))
        return 0
    rc = 0
    for q in argv:
        try:
            hits = lookup(q)
        except RegisterUnavailable as exc:
            print(f"[REGISTER_UNAVAILABLE] {q!r} cannot be checked: {exc}")
            return 2
        if hits:
            rc = 1
            print(f"[RETRACTED] {q!r}")
            print(format_rows(hits))
        else:
            print(f"[NOT_RETRACTED] {q!r} {NOT_A_CERTIFICATE} ({len(value_rows())} rows checked)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
