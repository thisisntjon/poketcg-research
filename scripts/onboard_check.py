#!/usr/bin/env python3
"""onboard_check.py - verify the onboarding path is still TRUE.

The onboarding docs in this repo rot in a specific, repeatable way: a statement is
correct when written, reality moves, and the statement is never deleted. Nothing
catches it, so a fresh harness reads a confident sentence and works on the wrong
thing. Measured 2026-08-06: AGENTS.md sent every harness to attack "the final three
RED rows" in RELIABILITY-MANIFEST.json, which had zero RED rows; the prescribed read
order terminated in a document whose first line says "Do not rely on this document";
and three named strategy surfaces each disclaimed the others.

Every check here corresponds to a defect that actually shipped. Adding a claim to
START-HERE.md that this script cannot verify is how the next one ships.

    python scripts/onboard_check.py            # full check, exit 1 on any FAIL
    python scripts/onboard_check.py --quiet    # only FAIL/WARN lines
    python scripts/onboard_check.py --strict   # WARN also exits 1 (CI-tightening mode)

Exit codes: 0 = all checks passed (warnings allowed), 1 = at least one FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

ENTRY = REPO / "START-HERE.md"
BUS = REPO / "workflow" / "BUS.md"
MANIFEST = REPO / "workflow" / "RELIABILITY-MANIFEST.json"
RETRACTIONS = REPO / "workflow" / "canon" / "RETRACTIONS.md"
ACTIVE_COMMS = REPO / "workflow" / "ACTIVE-COMMS.md"
AGENTS = REPO / "AGENTS.md"
DEADLINES = REPO / "workflow" / "DEADLINES.json"
ROADMAP = REPO / "workflow" / "OWNED-LEARNING-LOOP-ROADMAP.md"
MAP_FILE = REPO / "workflow" / "answer-map" / "MAP.json"

# External platform walls are the only calendar authority. Internal work is
# dependency/event gated and must never be reintroduced as a dated command.
EXTERNAL_WALLS = {
    "sim-close": (
        "2026-08-16",
        "2026-08-16T23:59:00Z",
        "workflow/research/01-competition-mechanics.md",
    ),
    "strategy-merger": (
        "2026-09-06",
        "2026-09-06T23:59:00Z",
        "workflow/research/phase-live-rules.md",
    ),
    "strategy-report": (
        "2026-09-13",
        "2026-09-13T23:59:00Z",
        "workflow/research/phase-live-rules.md",
    ),
}

# Fleet-ratified plan pin. Tests rebind these to dummy identities.
PLAN_OF_RECORD = "workflow/WINNING-STRATEGY-ARCHITECTURE.md"
PLAN_BLOB_OID = "e104a18b03ad1bc5f70f8efd85ceb2301bf43e9e"
PLAN_SHA256 = "94c57e89e07c515bb9178cdef07d04fa3f2773ed695af546246fa6c56a51af42"

# Paths that are git-ignored on purpose (compliance) or are host-absolute / globs.
# Their absence from a fresh checkout is CORRECT and must never fail this check.
PATH_EXEMPT = {
    ".env",
    "kaggle.json",
    "ptcg-agent/agent/cg/",
    "ptcg-agent/agent/cg",
    "ptcg-agent/experiments/public_kernels/",
    "ptcg-agent/experiments/public_kernels",
    "pokemon-tcg-ai-battle/",
    "cg.dll",
}

WORD_NUM = {
    "zero": 0, "no": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

results: list[tuple[str, str, str]] = []  # (level, check, message)


def ok(check: str, msg: str) -> None:
    results.append(("PASS", check, msg))


def warn(check: str, msg: str) -> None:
    results.append(("WARN", check, msg))


def fail(check: str, msg: str) -> None:
    results.append(("FAIL", check, msg))


def strip_fences(text: str) -> str:
    """Remove fenced code blocks - shell commands are not path claims."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


# --------------------------------------------------------------------------
# 1. Entry point exists and is reachable from the files a harness opens first.
# --------------------------------------------------------------------------
def check_entrypoint() -> None:
    if not ENTRY.exists():
        fail("entrypoint", "START-HERE.md is missing - there is no onboarding path")
        return
    ok("entrypoint", f"START-HERE.md present ({len(ENTRY.read_text(encoding='utf-8').splitlines())} lines)")

    for pointer in (AGENTS, REPO / "README.md", REPO / "CLAUDE.md"):
        if not pointer.exists():
            continue
        text = pointer.read_text(encoding="utf-8", errors="replace")
        if "START-HERE.md" in text:
            ok("entrypoint", f"{pointer.name} points at START-HERE.md")
        else:
            fail(
                "entrypoint",
                f"{pointer.name} does not mention START-HERE.md - a harness opening it "
                f"will never find the onboarding path",
            )


def check_layered_entry() -> None:
    """Bound initial reading cost and validate the explicit drill-down routes.

    This checks structure and budgets, not semantic completeness of instructions.
    The independent entry review remains necessary when moving binding procedures.
    """
    docs = {
        "START-HERE.md": 12000,
        "workflow/knowledge-register/README.md": 4500,
        "workflow/knowledge-register/REFERENCE.md": None,
        "workflow/canon/ONBOARDING-PROCEDURES.md": None,
    }
    for name, limit in docs.items():
        path = REPO / name
        if not path.is_file():
            fail("entry-context", f"required entry/reference file missing: {name}")
            continue
        raw = path.read_bytes()
        if limit is not None and len(raw) > limit:
            fail("entry-context", f"{name}: {len(raw)} bytes exceeds {limit}-byte entry budget")
        body = raw.decode("utf-8-sig")
        for href in re.findall(r"\]\(([^)\s]+)\)", strip_fences(body)):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target, _, fragment = href.partition("#")
            resolved = (path.parent / target).resolve() if target else path.resolve()
            if not resolved.is_relative_to(REPO.resolve()) or not resolved.exists():
                fail("entry-context", f"{name}: unresolved local link {href}")
                continue
            if fragment:
                if not resolved.is_file():
                    fail("entry-context", f"{name}: heading anchor on non-file link {href}")
                    continue
                headings = re.findall(r"^#{1,6}\s+(.+)$", resolved.read_text(encoding="utf-8-sig"), re.M)
                slugs = {re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                         for heading in headings}
                if fragment not in slugs:
                    fail("entry-context", f"{name}: unresolved heading anchor {href}")
    if ENTRY.is_file():
        body = ENTRY.read_text(encoding="utf-8-sig")
        for required in ("workflow/NOW.md", "workflow/knowledge-register/README.md",
                         "workflow/canon/ONBOARDING-PROCEDURES.md#corrections",
                         "Gameplay experiments and training remain paused"):
            if required not in body:
                fail("entry-context", f"START-HERE.md missing required scope/route: {required}")
    if not any(level == "FAIL" and name == "entry-context" for level, name, _ in results):
        ok("entry-context", "entry budgets and explicit reference links resolve; semantic acceptance is separate")


# --------------------------------------------------------------------------
# 2. Every repo-relative path the entry doc names actually resolves.
# --------------------------------------------------------------------------
def extract_paths(text: str) -> set[str]:
    body = strip_fences(text)
    found: set[str] = set()
    # markdown links: ](workflow/FOO.md)
    found.update(re.findall(r"\]\(([^)\s#]+)\)", body))
    # backticked path-ish tokens
    for tok in re.findall(r"`([^`\n]+)`", body):
        tok = tok.strip()
        if re.fullmatch(r"[\w./-]+", tok) and (
            "/" in tok or tok.endswith((".md", ".py", ".json", ".csv"))
        ):
            found.add(tok)
    return found


def check_paths() -> None:
    if not ENTRY.exists():
        return
    bad: list[str] = []
    checked = 0
    for raw in sorted(extract_paths(ENTRY.read_text(encoding="utf-8", errors="replace"))):
        p = raw.strip()
        if not p or p.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if "<" in p or ">" in p or "*" in p or "\\" in p:  # placeholders, globs, host paths
            continue
        if re.match(r"^(origin|upstream|refs)/", p):  # git refs are not filesystem paths
            continue
        if p in PATH_EXEMPT or p.rstrip("/") in PATH_EXEMPT:
            continue
        checked += 1
        if not (REPO / p).exists():
            bad.append(p)
    if bad:
        fail("paths", f"{len(bad)} referenced path(s) do not exist: {', '.join(bad)}")
    else:
        ok("paths", f"all {checked} referenced repo paths resolve")


# --------------------------------------------------------------------------
# 3. The bus pointer. START-HERE must NOT hardcode a number; docs that do must match.
# --------------------------------------------------------------------------
def current_bus() -> str | None:
    if not BUS.exists():
        return None
    m = re.search(r"CURRENT BUS:\s*`?#?(\d+)`?", BUS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def check_bus() -> None:
    bus = current_bus()
    if bus is None:
        fail("bus", "workflow/BUS.md missing or has no 'CURRENT BUS:' line - the bus is unresolvable")
        return
    ok("bus", f"workflow/BUS.md resolves the current bus to #{bus}")

    if ENTRY.exists():
        body = strip_fences(ENTRY.read_text(encoding="utf-8", errors="replace"))
        hard = re.findall(r"(?:bus|issue)\s*#(\d{3,})", body, flags=re.IGNORECASE)
        if hard:
            fail(
                "bus",
                f"START-HERE.md hardcodes bus number(s) {sorted(set(hard))} - the bus rotates; "
                f"it must only tell seats to resolve workflow/BUS.md",
            )
        else:
            ok("bus", "START-HERE.md hardcodes no bus number (resolves the pointer instead)")

    # Any other doc that names a bus number should name the live one.
    if ACTIVE_COMMS.exists():
        text = ACTIVE_COMMS.read_text(encoding="utf-8", errors="replace")
        nums = set(re.findall(r"(?:bus|issue)\s*(?:number\s*)?[`*]*#(\d{3,})", text, flags=re.IGNORECASE))
        stale = {n for n in nums if n != bus}
        # A number explicitly labelled ARCHIVE is fine to mention.
        stale = {n for n in stale if not re.search(rf"#{n}[^\n]*ARCHIVE", text)}
        if stale:
            warn(
                "bus",
                f"ACTIVE-COMMS.md names bus #{', #'.join(sorted(stale))} but the live bus is "
                f"#{bus} - a seat reading it will post into a dead channel",
            )
        else:
            ok("bus", "ACTIVE-COMMS.md names no stale live-bus number")


# --------------------------------------------------------------------------
# 4. Prose claims about RELIABILITY-MANIFEST row states must match the JSON.
#    This is the exact defect that sent every harness at three already-GREEN rows.
# --------------------------------------------------------------------------
def check_manifest() -> None:
    if not MANIFEST.exists():
        fail("manifest", "workflow/RELIABILITY-MANIFEST.json missing")
        return
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        fail("manifest", f"RELIABILITY-MANIFEST.json is not valid JSON: {exc}")
        return

    rows = data.get("rows", [])
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.get("state", "?")] = counts.get(row.get("state", "?"), 0) + 1
    red = counts.get("RED", 0)
    ok("manifest", f"row states: {', '.join(f'{v} {k}' for k, v in sorted(counts.items()))}")

    pat = re.compile(r"\b(\w+)\s+RED\s+rows?\b", flags=re.IGNORECASE)
    for doc in (ENTRY, AGENTS, ACTIVE_COMMS, REPO / "workflow" / "PLAN.md"):
        if not doc.exists():
            continue
        for lineno, line in enumerate(doc.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in pat.finditer(line):
                tok = m.group(1).lower()
                claimed = WORD_NUM.get(tok, int(tok) if tok.isdigit() else None)
                if claimed is None:
                    continue
                if claimed != red:
                    msg = (
                        f"{doc.relative_to(REPO).as_posix()}:{lineno} claims {claimed} RED row(s); "
                        f"the manifest has {red}. Harnesses are being sent at finished work."
                    )
                    if ("FAIL", "manifest", msg) not in results:
                        fail("manifest", msg)


# --------------------------------------------------------------------------
# 5. The strategy pointer must exist AND must not be self-disclaiming.
#    START-HERE naming a quarantined doc is worse than naming none.
# --------------------------------------------------------------------------
DISCLAIMERS = (
    "QUARANTINE",
    "do not rely on this document",
    "superseded banners",
    "read for history, not for strategy",
    "historical, not current truth",
)


def check_strategy_pointer() -> None:
    if not ENTRY.exists():
        return
    m = re.search(r"\*\*The plan of record\*\*\s*\|\s*\[`([^`]+)`\]", ENTRY.read_text(encoding="utf-8", errors="replace"))
    if not m:
        warn("strategy", "could not locate the 'plan of record' row in START-HERE.md - check the table format")
        return
    target = m.group(1)
    tp = REPO / target
    if not tp.exists():
        fail("strategy", f"START-HERE.md names {target} as the plan of record, but it does not exist")
        return
    head = "\n".join(tp.read_text(encoding="utf-8", errors="replace").splitlines()[:20])
    hit = [d for d in DISCLAIMERS if d.lower() in head.lower()]
    if hit:
        fail(
            "strategy",
            f"the named plan of record ({target}) disclaims itself in its first 20 lines "
            f"({hit[0]!r}). The read order must not terminate in a quarantined document.",
        )
    else:
        ok("strategy", f"plan of record = {target}, no self-disclaimer in its header")


def git_blob_oid(data: bytes) -> str:
    """Git blob SHA-1 of raw bytes (no repo required)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _has_ratification_clause(text: str) -> bool:
    return bool(
        re.search(
            r"ratification supersedes.{0,160}(Status:\s*PROPOSED|historical)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    )


CANON_LABEL = "workflow/WINNING-STRATEGY-ARCHITECTURE.md"
CANON_LOCAL_HREF = "WINNING-STRATEGY-ARCHITECTURE.md"
_PIN_LINK_RE = re.compile(
    r"\[`(workflow/WINNING-STRATEGY-ARCHITECTURE\.md)`\]\(([^)]+)\)",
    flags=re.IGNORECASE,
)
_AUTHORITY_RE = re.compile(
    r"plan of record|strategy now|strategy day-to-day|current strategy|"
    r"authoritative strategy|authoritative plan|strategy\s*=",
    flags=re.IGNORECASE,
)
_RETIRED_MD_RE = re.compile(
    r"(?:STRATEGY-NOW|CURRENT-PLAN|STRATEGY-OF-RECORD)\.md",
    flags=re.IGNORECASE,
)
_HISTORICAL_MARKS = (
    "historical", "not the live", "quarantine", "superseded",
    "not plan.md / strategy-now", "era fences", "not the live pointer",
)


def _line_has_historical_mark(line: str) -> bool:
    lower = line.lower()
    return any(mark in lower for mark in _HISTORICAL_MARKS)


def _resolve_href(href: str, source: str) -> str | None:
    """Resolve href relative to the source document. Reject URL/fragment/traversal."""
    href = href.strip().replace("\\", "/")
    if href.startswith(("http://", "https://", "//", "mailto:")):
        return None
    if "#" in href or "?" in href or href.startswith("/"):
        return None
    parts = [] if source.lower().startswith("start-here") else (
        ["workflow"] if source.lower().startswith("active-comms") else []
    )
    for p in href.split("/"):
        if p in ("", "."):
            continue
        if p == "..":
            return None
        parts.append(p)
    return "/".join(parts) or None


def _required_href(source: str) -> str:
    if source.lower().startswith("active-comms"):
        return CANON_LOCAL_HREF
    return CANON_LABEL


def _pin_link_on_line(line: str) -> tuple[str, str] | None:
    m = _PIN_LINK_RE.search(line)
    if not m:
        return None
    return m.group(1), m.group(2).strip()


def _same_line_complete(line: str, source: str) -> bool:
    pin = _pin_link_on_line(line)
    if not pin:
        return False
    label, href = pin
    if label != CANON_LABEL or href != _required_href(source):
        return False
    if _resolve_href(href, source) != PLAN_OF_RECORD:
        return False
    blob = re.search(r"Git blob `([0-9a-f]{40})`", line, flags=re.I)
    sha = re.search(r"SHA-256 `([0-9a-f]{64})`", line, flags=re.I)
    if not blob or blob.group(1).lower() != PLAN_BLOB_OID.lower():
        return False
    if not sha or sha.group(1).lower() != PLAN_SHA256.lower():
        return False
    if not _hex_identity_ok(line):
        return False
    return _has_ratification_clause(line)


def _hex_identity_ok(line: str) -> bool:
    """Canonical line may carry only the expected blob and SHA tokens."""
    blobs = re.findall(r"(?<![0-9a-fA-F])([0-9a-fA-F]{40})(?![0-9a-fA-F])", line)
    shas = re.findall(r"(?<![0-9a-fA-F])([0-9a-fA-F]{64})(?![0-9a-fA-F])", line)
    if [b.lower() for b in blobs] != [PLAN_BLOB_OID.lower()]:
        return False
    if [s.lower() for s in shas] != [PLAN_SHA256.lower()]:
        return False
    return True


def _negated_md_tokens(line: str) -> set[str]:
    found: set[str] = set()
    for m in re.finditer(
        r"(?:not|never|historical|superseded)\s+`?([\w./-]+\.md)`?",
        line,
        flags=re.IGNORECASE,
    ):
        found.add(m.group(1))
    for m in re.finditer(
        r"not\s+((?:`?[\w./-]+\.md`?(?:\s*/\s*)?)+)",
        line,
        flags=re.IGNORECASE,
    ):
        found.update(re.findall(r"[\w./-]+\.md", m.group(1), flags=re.I))
    return found


def _canonical_line_offsets(text: str, source: str) -> list[tuple[int, int]]:
    covered: list[tuple[int, int]] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\n")
        if _same_line_complete(body, source):
            covered.append((offset, offset + len(body)))
        offset += len(line)
    return covered


def _conflicting_live_strategy_pointers(text: str) -> list[str]:
    """Retired plan names presented as live, not historical provenance."""
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not _RETIRED_MD_RE.search(line):
            continue
        if _line_has_historical_mark(line):
            continue
        hits.append(f"line {lineno}: {line.strip()[:120]}")
    return hits


def _live_md_targets(line: str) -> list[str]:
    """Markdown hrefs and every remaining bare token ending .md."""
    targets = [href.strip() for _, href in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", line)]
    stripped = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", " ", line)
    negated = _negated_md_tokens(line)
    for tok in re.findall(r"[\w./-]+\.md", stripped):
        if tok in negated:
            continue
        targets.append(tok)
    return targets


def _live_authority_failures(text: str, source: str) -> list[str]:
    """Reject live-authority lines whose targets are not the canonical architecture."""
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not _AUTHORITY_RE.search(line):
            continue
        tail = line[_AUTHORITY_RE.search(line).start():]
        for raw in _live_md_targets(tail):
            resolved = _resolve_href(raw, source)
            if resolved == PLAN_OF_RECORD:
                continue
            if raw in _negated_md_tokens(line):
                continue
            if _RETIRED_MD_RE.search(raw) and _line_has_historical_mark(line):
                continue
            hits.append(f"line {lineno}: {raw}")
    return hits


def _decoy_pin_tokens(text: str, source: str) -> list[str]:
    covered = _canonical_line_offsets(text, source)
    decoys: list[str] = []
    lower = text.lower()
    for kind, token in (("blob", PLAN_BLOB_OID), ("sha256", PLAN_SHA256)):
        start = 0
        needle = token.lower()
        while True:
            idx = lower.find(needle, start)
            if idx < 0:
                break
            if not any(a <= idx < b for a, b in covered):
                decoys.append(f"{kind} at offset {idx}")
            start = idx + len(needle)
    return decoys


def _line_ending_only_diff(rel: str) -> bool:
    def _out(args: list[str]) -> bytes:
        return subprocess.check_output(args, cwd=REPO, stderr=subprocess.DEVNULL)

    raw = _out(["git", "diff", "--", rel]) + _out(["git", "diff", "--cached", "--", rel])
    if not raw.strip():
        return True
    ign = _out(["git", "diff", "--ignore-cr-at-eol", "--", rel]) + _out(
        ["git", "diff", "--cached", "--ignore-cr-at-eol", "--", rel]
    )
    return not ign.strip()


def _require_canonical_record(text: str, source: str) -> bool:
    src = source.lower()
    if src.startswith("start-here"):
        complete = [ln for ln in text.splitlines() if _same_line_complete(ln, source)]
        if len(complete) != 1:
            fail("strategy", f"{source} must contain exactly one same-line canonical plan record")
            return False
    elif src.startswith("active-comms"):
        day = [ln for ln in text.splitlines() if re.search(r"strategy day-to-day:", ln, flags=re.I)]
        if len(day) != 1:
            fail("strategy", f"{source} must contain exactly one Strategy day-to-day: line")
            return False
        if not _same_line_complete(day[0], source):
            fail("strategy", f"{source} Strategy day-to-day: line is not a complete same-line canonical record")
            return False
    else:
        fail("strategy", f"{source} has no bound canonical architecture pin record")
        return False
    decoys = _decoy_pin_tokens(text, source)
    if decoys:
        fail("strategy", f"{source} has decoy/free-floating pin tokens ({decoys[0]})")
        return False
    authority = _live_authority_failures(text, source)
    if authority:
        fail("strategy", f"{source} has a live authority target that is not canonical ({authority[0]})")
        return False
    conflicts = _conflicting_live_strategy_pointers(text)
    if conflicts:
        fail("strategy", f"{source} has a conflicting live strategy pointer: {conflicts[0]}")
        return False
    return True


def _architecture_identities(path: Path) -> tuple[str, str] | None:
    """Git mode fail-closed. Non-git fixtures hash working-tree bytes."""
    rel = path.relative_to(REPO).as_posix()
    if not (REPO / ".git").exists():
        data = path.read_bytes()
        return git_blob_oid(data), hashlib.sha256(data).hexdigest()
    try:
        oid = subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{rel}"],
            cwd=REPO,
            stderr=subprocess.DEVNULL,
        ).decode("ascii").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        fail("strategy", f"Git mode: HEAD:{rel} resolution failed")
        return None
    try:
        unstaged = subprocess.check_output(
            ["git", "diff", "--name-only", "--", rel], cwd=REPO, stderr=subprocess.DEVNULL
        )
        staged = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--", rel],
            cwd=REPO, stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        fail("strategy", f"Git mode: could not inspect drift for {rel}")
        return None
    if (unstaged.strip() or staged.strip()) and not _line_ending_only_diff(rel):
        fail("strategy", f"Git mode: staged or unstaged drift in {rel} (not line-ending-only)")
        return None
    try:
        blob = subprocess.check_output(
            ["git", "cat-file", "blob", oid], cwd=REPO, stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        fail("strategy", f"Git mode: cat-file blob {oid} failed")
        return None
    return oid, hashlib.sha256(blob).hexdigest()


def check_architecture_pin() -> None:
    """Bound pin record in START-HERE + ACTIVE-COMMS; Git identity fail-closed."""
    if not ENTRY.exists():
        return
    entry = ENTRY.read_text(encoding="utf-8", errors="replace")
    if not _require_canonical_record(entry, "START-HERE.md"):
        return
    if not ACTIVE_COMMS.exists():
        fail("strategy", "ACTIVE-COMMS.md missing; cannot confirm architecture pin agreement")
        return
    comms = ACTIVE_COMMS.read_text(encoding="utf-8", errors="replace")
    if not _require_canonical_record(comms, "ACTIVE-COMMS.md"):
        return
    tp = REPO / PLAN_OF_RECORD
    if not tp.exists():
        fail("strategy", f"{PLAN_OF_RECORD} does not exist")
        return
    ident = _architecture_identities(tp)
    if ident is None:
        return
    oid, digest = ident
    if oid != PLAN_BLOB_OID:
        fail("strategy", f"{PLAN_OF_RECORD} git blob OID {oid} != pinned {PLAN_BLOB_OID}")
        return
    if digest != PLAN_SHA256:
        fail("strategy", f"{PLAN_OF_RECORD} SHA-256 {digest} != pinned {PLAN_SHA256}")
        return
    ok(
        "strategy",
        f"architecture pin {PLAN_OF_RECORD} blob {PLAN_BLOB_OID} "
        f"sha256 {PLAN_SHA256[:12]}… MATCH",
    )


# --------------------------------------------------------------------------
# 6. Retracted numbers. The entry doc must be clean; the repo gets a census.
# --------------------------------------------------------------------------
def retracted_values() -> list[tuple[str, str]]:
    """(value, replacement) for every numeric token in the register's values table.

    Delegates to scripts/retraction_register.py -- the single parser shared with
    query_inventory.py. The previous inline regex accepted only a bare-backticked
    decimal as the whole first cell and so saw 6 of 11 rows (`+9.35pp`, `46.2%`, the
    Fisher/CP row and the hash rows were invisible to the census).
    """
    if not RETRACTIONS.exists():
        return []
    import retraction_register as rr  # local: keeps the checker importable standalone
    return rr.banned_numbers(RETRACTIONS)


def check_retractions() -> None:
    if not RETRACTIONS.exists():
        fail(
            "retractions",
            "workflow/canon/RETRACTIONS.md missing - retracted figures are cited across the repo "
            "with nothing marking them false",
        )
        return
    vals = retracted_values()
    if not vals:
        warn("retractions", "RETRACTIONS.md has no parseable value rows (expected '| `753.1` | ... |')")
        return
    ok("retractions", f"register lists {len(vals)} retracted value(s)")

    if ENTRY.exists():
        dirty: list[str] = []
        for lineno, line in enumerate(ENTRY.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "retract" in line.lower():
                continue
            for val, _ in vals:
                if re.search(rf"(?<![\d.]){re.escape(val)}(?![\d.])", line):
                    dirty.append(f"{val} at START-HERE.md:{lineno}")
        if dirty:
            fail("retractions", f"START-HERE.md cites retracted value(s) unmarked: {', '.join(dirty)}")
        else:
            ok("retractions", "START-HERE.md cites no retracted value")

    # Repo-wide census - informational pressure, never a merge blocker.
    for val, repl in vals:
        try:
            res = subprocess.run(
                ["git", "grep", "-l", "--", val, "--", "*.md"],
                cwd=REPO, capture_output=True, text=True, timeout=60,
            )
            n = len([x for x in res.stdout.splitlines() if x.strip()])
        except (subprocess.SubprocessError, OSError):
            continue
        if n:
            warn("retractions", f"retracted {val} still cited in {n} tracked .md file(s) (use {repl or 'the register'})")


# --------------------------------------------------------------------------
# 7. The tools START-HERE tells seats to run must exist and be invocable.
# --------------------------------------------------------------------------
REQUIRED_TOOLS = [
    "ptcg-agent/harness/status.py",
    "ptcg-agent/harness/preflight.py",
    "ptcg-agent/harness/active_comms_lint.py",
    "scripts/new_harness.py",
    "scripts/inventory_validate.py",
]


def check_tools() -> None:
    missing = [t for t in REQUIRED_TOOLS if not (REPO / t).exists()]
    if missing:
        fail("tools", f"commands named in START-HERE.md do not exist: {', '.join(missing)}")
    else:
        ok("tools", f"all {len(REQUIRED_TOOLS)} named tools exist")

    pf = REPO / "ptcg-agent" / "harness" / "preflight.py"
    if pf.exists():
        src = pf.read_text(encoding="utf-8", errors="replace")
        if "PREFLIGHT PASSED" in src and "games_fence" in src:
            ok("tools", "preflight still emits an unqualified PASS under the games fence "
                        "(START-HERE.md ss6 warns about this - keep the warning)")



# --------------------------------------------------------------------------
# 8b. The inventory pack CLAUDE.md tells harnesses to load on wake must be
#     present ON MAIN and machine-valid. A wake surface that exists only in
#     one working tree is not a wake surface (see: hub-green-does-not-speak-
#     for-main). Added 2026-08-14 alongside first custody of the pack.
# --------------------------------------------------------------------------
REQUIRED_INVENTORIES = [
    "workflow/inventories/HARNESS-CONTEXT.json",
    "workflow/inventories/MASTER-INVENTORY-INDEX.json",
    "workflow/inventories/P0-SLA-BOARD.json",
    "workflow/inventories/PRODUCT-PASSPORT.json",
    "workflow/NOW.md",
    "workflow/canon/CURRENT-TRUTH.json",
]


def check_inventory_pack() -> None:
    missing = [f for f in REQUIRED_INVENTORIES if not (REPO / f).exists()]
    if missing:
        fail("inventory", f"wake surfaces missing: {', '.join(missing)}")
        return
    ok("inventory", f"all {len(REQUIRED_INVENTORIES)} inventory wake surfaces exist")

    hc = REPO / "workflow" / "inventories" / "HARNESS-CONTEXT.json"
    try:
        ctx = json.loads(hc.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("inventory", f"HARNESS-CONTEXT.json is not valid JSON: {exc}")
        return

    north = ctx.get("mission", {}).get("north_star", "")
    if "OWNED-CORE" not in north:
        fail("inventory", f"HARNESS-CONTEXT north_star does not name OWNED-CORE: {north!r}")
    else:
        ok("inventory", "HARNESS-CONTEXT north_star names OWNED-CORE")

    # Every in-repo path the wake object points at must resolve.
    auth = ctx.get("authority", {})
    for key in ("hub_now", "hub_truth", "repo_plan_of_record"):
        val = auth.get(key)
        if val and not (REPO / val).exists():
            fail("inventory", f"HARNESS-CONTEXT authority.{key} missing on disk: {val}")
        elif val:
            ok("inventory", f"HARNESS-CONTEXT {key} = {val}")

    # Host-local pointers must be labelled as such, not left to look repo-relative.
    if auth.get("plan_worktree") and not auth.get("plan_worktree_note"):
        fail("inventory", "authority.plan_worktree is host-local but carries no "
                          "plan_worktree_note - a fresh clone cannot reach it")
    elif auth.get("plan_worktree"):
        ok("inventory", "host-local authority pointer is labelled")

    for f in REQUIRED_INVENTORIES:
        if f.endswith(".json"):
            try:
                json.loads((REPO / f).read_text(encoding="utf-8"))
            except Exception as exc:
                fail("inventory", f"{f} is not valid JSON: {exc}")

    entry_src = ENTRY.read_text(encoding="utf-8", errors="replace")
    claude = REPO / "CLAUDE.md"
    claude_src = claude.read_text(encoding="utf-8", errors="replace") if claude.exists() else ""
    if "inventories/" not in entry_src and "inventories/" not in claude_src:
        fail("inventory", "neither START-HERE.md nor CLAUDE.md routes through the inventory pack")
    else:
        ok("inventory", "wake path routes through the inventory pack")


# --------------------------------------------------------------------------
# 8c. Live product identity. START-HERE §2.1 shipped for weeks claiming
#     FIELDED = v000_baseline while the live pair was tetsutani c61.
# --------------------------------------------------------------------------
def check_product_identity() -> None:
    if not ENTRY.exists():
        return
    text = ENTRY.read_text(encoding="utf-8", errors="replace")
    if re.search(
        r"FIELDED\s+ptcg-agent/ship_kernels/copies/v000_baseline",
        text,
    ):
        fail(
            "product",
            "START-HERE.md presents v000_baseline as FIELDED; the live pair is tetsutani c61",
        )
        return
    if "**2.1" in text or "2.1 —" in text or "2.1 -" in text:
        if "c61e540b" not in text.lower() and "tetsutani" not in text.lower():
            fail(
                "product",
                "START-HERE.md field-facts section does not name tetsutani c61 as the live ladder product",
            )
            return
        ok("product", "START-HERE.md names tetsutani c61; v000 is not presented as FIELDED")
        return
    ok("product", "START-HERE.md has no field-facts block (skeleton ok)")


# --------------------------------------------------------------------------
# 8. Mailbox surfaces named in the comms policy must exist for active seats.
# --------------------------------------------------------------------------
ACTIVE_SEATS = ["skynet", "roach"]
MAILBOX_ALIASES = {"skynet": "master"}


def check_mailbox() -> None:
    mb = REPO / "workflow" / "mailbox"
    if not mb.is_dir():
        fail("mailbox", "workflow/mailbox/ missing - the assignment surface does not exist")
        return
    missing = [
        s for s in ACTIVE_SEATS
        if not (mb / f"INBOX-{MAILBOX_ALIASES.get(s, s)}.md").exists()
    ]
    if missing:
        fail("mailbox", f"active seat(s) have no inbox: {', '.join(missing)}")
    else:
        ok("mailbox", f"all {len(ACTIVE_SEATS)} active seats have an inbox")

    proto = mb / "PROTOCOL.md"
    if proto.exists():
        text = proto.read_text(encoding="utf-8", errors="replace")
        if re.search(r"only\s+fable-lead\s+writes", text, flags=re.IGNORECASE):
            warn(
                "mailbox",
                "mailbox/PROTOCOL.md still says only fable-lead writes inboxes; ACTIVE-COMMS.md "
                "retired that seat - SKYNET writes them now",
            )


# --------------------------------------------------------------------------
# 9. Calendar authority is external-only; internal execution is event-gated.
# --------------------------------------------------------------------------
def check_date_authority() -> None:
    if not DEADLINES.exists():
        fail("date-authority", "workflow/DEADLINES.json is missing")
        return
    try:
        data = json.loads(DEADLINES.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        fail("date-authority", f"DEADLINES.json is not valid JSON: {exc}")
        return

    rows = data.get("deadlines", [])
    if not isinstance(rows, list):
        fail("date-authority", "DEADLINES.json deadlines must be a list")
        return

    by_id: dict[str, dict] = {}
    duplicate_ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            fail("date-authority", "every deadline must be an object")
            return
        row_id = str(row.get("id", ""))
        if row_id in by_id:
            duplicate_ids.append(row_id)
        by_id[row_id] = row

    expected_ids = set(EXTERNAL_WALLS)
    actual_ids = set(by_id)
    unknown = sorted(actual_ids - expected_ids)
    missing = sorted(expected_ids - actual_ids)
    if unknown:
        fail("date-authority", f"internal/unknown dated directives are forbidden: {', '.join(unknown)}")
    if missing:
        fail("date-authority", f"external platform wall(s) missing: {', '.join(missing)}")
    if duplicate_ids:
        fail("date-authority", f"duplicate wall id(s): {', '.join(sorted(set(duplicate_ids)))}")

    for row_id, (expected_date, expected_utc, expected_source) in EXTERNAL_WALLS.items():
        row = by_id.get(row_id)
        if row is None:
            continue
        if row.get("date") != expected_date or row.get("utc") != expected_utc:
            fail(
                "date-authority",
                f"{row_id} drifted: expected {expected_date} / {expected_utc}, "
                f"got {row.get('date')} / {row.get('utc')}",
            )
        source = str(row.get("source", "")).strip()
        if source != expected_source:
            fail(
                "date-authority",
                f"{row_id} source drifted: expected {expected_source}, got {source or '(missing)'}",
            )
            continue
        source_path = REPO / expected_source
        if not source_path.is_file():
            fail("date-authority", f"{row_id} source artifact is missing: {expected_source}")
            continue
        source_text = source_path.read_text(encoding="utf-8", errors="replace")
        if expected_date not in source_text or not re.search(r"23:59\s*(?:UTC|Z)", source_text):
            fail(
                "date-authority",
                f"{row_id} source does not support {expected_date} 23:59 UTC: {expected_source}",
            )

    recurring = data.get("recurring", [])
    if recurring:
        fail("date-authority", "internal recurring calendar schedules are forbidden; use event gates")

    allowed_dates = {date for date, _, _ in EXTERNAL_WALLS.values()}
    directive = re.compile(r"\b(mandatory|deadline|ceiling|checkpoint|freeze|lock|target)\b", re.IGNORECASE)
    imperative = re.compile(
        r"^\s*(?:[-*]\s*)?(?:\*\*)?"
        r"(fire|submit|freeze|lock|review|decide|ship|run|start|stop|complete|finish|"
        r"deliver|merge|train|generate|launch|execute|field|promote)(?![-\w])|"
        r"\b(?:must|shall|will)\s+"
        r"(?:fire|submit|freeze|lock|review|decide|ship|run|start|stop|complete|finish|"
        r"deliver|merge|train|generate|launch|execute|field|promote)(?![-\w])",
        re.IGNORECASE,
    )
    date_pattern = re.compile(r"\b2026-\d{2}-\d{2}\b")
    for doc in (ENTRY, ROADMAP):
        if not doc.exists():
            continue
        for lineno, line in enumerate(doc.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            dates = set(date_pattern.findall(line))
            forbidden = sorted(dates - allowed_dates)
            if forbidden and (directive.search(line) or imperative.search(line)):
                fail(
                    "date-authority",
                    f"{doc.relative_to(REPO).as_posix()}:{lineno} presents internal date(s) "
                    f"{', '.join(forbidden)} as an execution control",
                )

    if not any(level == "FAIL" and check == "date-authority" for level, check, _ in results):
        ok("date-authority", "only the three source-bound external platform walls remain; execution is event-gated")


# --------------------------------------------------------------------------
# 10. Answer-map wake frontier (M2, 2026-08-23). The map is the work picker;
#     printing the OPEN-frontier top-3 at every wake is the anti-Nimrod line
#     (SCHEMA.md §5). Informational: a missing map only WARNs, but a map that
#     exists and does not parse is a FAIL (a broken wake surface must never
#     look healthy). Full validation lives in scripts/map_validate.py.
#     Serialization is stdlib JSON (SCHEMA.md §1a): the wake check must not
#     depend on a third-party parser, so parsing is never "unavailable".
# --------------------------------------------------------------------------
def check_map_frontier() -> None:
    if not MAP_FILE.exists():
        warn("answer-map", "workflow/answer-map/MAP.json not present in this checkout "
                           "(frontier unavailable; see scripts/map_validate.py)")
        return
    try:
        data = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail("answer-map", f"MAP.json does not parse: {exc}")
        return
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        fail("answer-map", "MAP.json must be one JSON object with a nodes list")
        return
    by_id = {n.get("id"): n for n in data["nodes"]
             if isinstance(n, dict) and isinstance(n.get("id"), str)}

    # Depth from the root over supportedBy+requires (same order as map_render).
    supported = set()
    for n in by_id.values():
        supported.update(n.get("supportedBy") or [])
    roots = sorted(i for i, n in by_id.items()
                   if n.get("type") == "goal" and i not in supported)
    depth = {i: 99 for i in by_id}
    frontier_ids, seen, d = list(roots), set(roots), 0
    for r in roots:
        depth[r] = 0
    while frontier_ids:
        nxt = []
        for i in frontier_ids:
            kids = (by_id[i].get("supportedBy") or []) + (by_id[i].get("requires") or [])
            for k in sorted(kids):
                if k in by_id and k not in seen:
                    seen.add(k)
                    depth[k] = d + 1
                    nxt.append(k)
        frontier_ids, d = nxt, d + 1

    holds = {"MEASURED", "LAW"}
    open_frontier = sorted(
        (n for n in by_id.values()
         if n.get("status") == "OPEN"
         and all(by_id.get(r, {}).get("status") in holds
                 for r in (n.get("requires") or []))),
        key=lambda n: (depth.get(n["id"], 99), n["id"]))
    ok("answer-map", f"MAP.json parses ({len(by_id)} nodes); OPEN frontier top-3:")
    for n in open_frontier[:3]:
        ok("answer-map", f"  -> {n['id']} [{n.get('owner', '?')}]: "
                         f"{str(n.get('text', ''))[:90]}")
    if not open_frontier:
        ok("answer-map", "  (frontier empty - no OPEN node has all requires held)")


def check_orphan_audit() -> None:
    """Audit empirical artifact reachability against inventory surfaces."""
    audit_script = REPO / "scripts" / "audit_repo_orphans.py"
    if not audit_script.is_file():
        fail("orphan-audit", "scripts/audit_repo_orphans.py missing")
        return
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        import audit_repo_orphans
        total, routed, orphans = audit_repo_orphans.audit_orphans()
        cov = (routed / total * 100.0) if total > 0 else 100.0
        ok("orphan-audit", f"artifact inventory coverage: {routed}/{total} routed ({cov:.1f}%), {len(orphans)} unreferenced")
    except Exception as exc:
        warn("orphan-audit", f"orphan audit check failed: {exc}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true", help="show only FAIL and WARN lines")
    ap.add_argument("--strict", action="store_true", help="exit 1 on WARN as well as FAIL")
    args = ap.parse_args()
    # The retraction register carries μ/σ in its "use instead" cells; a cp1252 console
    # (Windows default) raised UnicodeEncodeError on the 7th census warn and the checker
    # died mid-report. Never let the printer be the thing that fails.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    for fn in (
        check_entrypoint, check_layered_entry, check_paths, check_bus, check_manifest,
        check_strategy_pointer, check_architecture_pin, check_retractions,
        check_tools, check_inventory_pack, check_product_identity,
        check_mailbox, check_date_authority, check_map_frontier,
        check_orphan_audit,
    ):
        try:
            fn()
        except Exception as exc:  # a broken check must never look like a pass
            fail(fn.__name__, f"check crashed: {exc!r}")

    print(f"onboard_check: {ENTRY.relative_to(REPO).as_posix()} + comms/inventory claims\n")
    for level, check, msg in results:
        if args.quiet and level == "PASS":
            continue
        mark = {"PASS": "ok  ", "WARN": "!!  ", "FAIL": "XX  "}[level]
        print(f"  {mark}[{check}] {msg}")

    fails = sum(1 for lvl, _, _ in results if lvl == "FAIL")
    warns = sum(1 for lvl, _, _ in results if lvl == "WARN")
    print(f"\n{fails} error(s), {warns} warning(s).")
    if fails:
        print("ONBOARD CHECK FAILED - a harness reading START-HERE.md would be misled.")
        return 1
    if warns and args.strict:
        print("ONBOARD CHECK FAILED (--strict: warnings are errors).")
        return 1
    print("ONBOARD CHECK PASSED" + (" (with warnings)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
