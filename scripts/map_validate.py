#!/usr/bin/env python3
"""map_validate.py - validator for workflow/answer-map/MAP.json.

Implements the V-check list of workflow/answer-map/SCHEMA.md §5 plus the §8 M2
addenda (V21 anti-theater/one-experiment, V22 train-lock). Output is one line per
check - `V<n> PASS|FAIL|SKIP <count-or-reason>` - never a bare summary word (the
PREFLIGHT lesson: the run report states how many checks actually ran), followed by
the machine-counted totals (the ONLY citable totals, F4).

Modes:
    python scripts/map_validate.py            # receipts vs LOCAL committed bytes (HEAD)
    python scripts/map_validate.py --origin   # receipts vs origin/main (CI mode; refuses
                                              # to run on a shallow clone - SKIP-FATAL)
    python scripts/map_validate.py --wake     # read-only: frontier top-3 + totals

Exit codes: 0 = all executed checks passed, 1 = any FAIL (or SKIP-FATAL).
Law #21: every check has a red fixture in scripts/test_map_validate.py.

Serialization is stdlib JSON (SCHEMA.md §1a) - no third-party parser is
importable on the wake path, so parsing can never be "unavailable".
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import map_render  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
MAP_FILE = REPO / "workflow" / "answer-map" / "MAP.json"
ANSWER_MAP_DIR = REPO / "workflow" / "answer-map"
VIEWS_DIR = ANSWER_MAP_DIR / "views"

TOP_KEYS = {"schema_version", "updated", "owners", "nodes"}
REQUIRED_NODE_KEYS = {"id", "text", "type", "status", "suspect", "owner",
                      "last_verified", "receipt"}
OPTIONAL_NODE_KEYS = {"notes", "supportedBy", "inContextOf", "challenges",
                      "supersedes", "superseded_by", "requires", "tests",
                      "unlocks", "export_owed"}
NODE_KEYS = REQUIRED_NODE_KEYS | OPTIONAL_NODE_KEYS
RECEIPT_KEYS = {"path", "sha256", "kind", "producer"}

STATUSES = {"MEASURED", "MEASURED-OFFREPO", "LAW", "PARTIAL", "OPEN", "KILLED", "GUESS"}
TYPES = {"goal", "strategy", "solution", "context", "assumption", "defeater"}
KINDS = {"repo-file", "bus-comment", "offrepo-file"}
RECEIPTED = {"MEASURED", "MEASURED-OFFREPO", "LAW", "PARTIAL"}
HOLDS = {"MEASURED", "LAW"}  # what satisfies a `requires` edge (SCHEMA §2)

ID_RE = re.compile(r"^n-[a-z0-9]+(-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
BUS_RE = re.compile(r"^bus#\d+#issuecomment-\d+$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EDGE_LISTS = ("supportedBy", "inContextOf", "challenges", "supersedes",
              "requires", "tests", "unlocks")

# Hand-written totals are forbidden outside generated views (F4 / V15).
TOTAL_RES = [
    re.compile(r"\b\d+\s*(?:x\s*)?(?:MEASURED-OFFREPO|MEASURED|PARTIAL|KILLED|GUESS|LAW|OPEN)\b"),
    re.compile(r"\b(?:MEASURED-OFFREPO|MEASURED|PARTIAL|KILLED|GUESS|LAW|OPEN)\s*[:=]\s*\d+"),
    re.compile(r"\b\d+\s+(?:deduplicated\s+)?nodes\b", re.IGNORECASE),
]

TRAIN_LOCK_ID = "n-train-lock"
LIVE_ROSTER = {"Jon", "STRATEGIST", "SKYNET", "ROACH"}

results: list[tuple[str, str, str]] = []  # (check, level, message)


def emit(check: str, level: str, msg: str) -> None:
    results.append((check, level, msg))


class Ctx:
    """Everything a check needs; tests rebind fields to fixture values."""

    def __init__(self, map_path: Path, repo: Path, ref: str | None,
                 baseline_text: str | None = None):
        self.map_path = map_path
        self.repo = repo
        self.ref = ref  # git ref for receipt basis; None => working-dir bytes (fixtures)
        self.baseline_text = baseline_text  # prior MAP.json bytes for V17 (None = none)
        self.raw = map_path.read_text(encoding="utf-8")
        self.data: dict | None = None
        self.nodes: dict[str, dict] = {}


def _git(ctx: Ctx, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ctx.repo,
                                   stderr=subprocess.DEVNULL)


def committed_blob(ctx: Ctx, rel: str) -> bytes | None:
    """Receipt-basis bytes: git blob at ctx.ref, or working-dir bytes when no git."""
    if ctx.ref is None:
        p = ctx.repo / rel
        return p.read_bytes() if p.is_file() else None
    try:
        return _git(ctx, "cat-file", "blob", f"{ctx.ref}:{rel}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def check_v1(ctx: Ctx) -> None:
    try:
        data = json.loads(ctx.raw)
    except json.JSONDecodeError as exc:
        emit("V1", "FAIL", f"MAP.json does not parse: {exc}")
        return
    if not isinstance(data, dict):
        emit("V1", "FAIL", f"expected one JSON object, got {type(data).__name__}")
        return
    bad = []
    extra = set(data) - TOP_KEYS
    missing = TOP_KEYS - set(data)
    if extra:
        bad.append(f"unknown top-level keys {sorted(extra)}")
    if missing:
        bad.append(f"missing top-level keys {sorted(missing)}")
    nodes = data.get("nodes") or []
    if not isinstance(nodes, list):
        bad.append("nodes is not a list")
        nodes = []
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            bad.append(f"node[{i}] is not a mapping")
            continue
        unk = set(n) - NODE_KEYS
        mis = REQUIRED_NODE_KEYS - set(n)
        if unk:
            bad.append(f"{n.get('id', f'node[{i}]')}: unknown keys {sorted(unk)}")
        if mis:
            bad.append(f"{n.get('id', f'node[{i}]')}: missing keys {sorted(mis)}")
        r = n.get("receipt")
        if r is not None and (not isinstance(r, dict) or set(r) != RECEIPT_KEYS):
            bad.append(f"{n.get('id', f'node[{i}]')}: receipt keys must be exactly "
                       f"{sorted(RECEIPT_KEYS)}")
    if bad:
        emit("V1", "FAIL", "; ".join(bad[:6]))
        return
    ctx.data = data
    ctx.nodes = {n["id"]: n for n in nodes if isinstance(n.get("id"), str)}
    emit("V1", "PASS", f"1 JSON object, {len(nodes)} node records, key sets conform")


def check_v2(ctx: Ctx) -> None:
    ids = [n.get("id") for n in (ctx.data or {}).get("nodes", [])]
    bad_fmt = [i for i in ids if not isinstance(i, str) or not ID_RE.match(i)]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if bad_fmt or dupes:
        emit("V2", "FAIL", f"bad id format {bad_fmt[:5]}; duplicates {dupes[:5]}")
    else:
        emit("V2", "PASS", f"{len(ids)} unique well-formed ids")


def check_v3(ctx: Ctx) -> None:
    dangling = []
    for i, n in ctx.nodes.items():
        refs = []
        for key in EDGE_LISTS:
            refs.extend(n.get(key) or [])
        for key in ("export_owed", "superseded_by"):
            if n.get(key):
                refs.append(n[key])
        for r in refs:
            if r not in ctx.nodes:
                dangling.append(f"{i} -> {r}")
    if dangling:
        emit("V3", "FAIL", f"{len(dangling)} dangling reference(s): {dangling[:5]}")
    else:
        emit("V3", "PASS", "all edge/export_owed/superseded_by references resolve")


def check_v4(ctx: Ctx) -> None:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in ctx.nodes}
    cycle: list[str] = []

    def dfs(i: str, stack: list[str]) -> bool:
        color[i] = GRAY
        stack.append(i)
        for k in (ctx.nodes[i].get("requires") or []) + (ctx.nodes[i].get("supportedBy") or []):
            if k not in ctx.nodes:
                continue
            if color[k] == GRAY:
                cycle.extend(stack[stack.index(k):] + [k])
                return True
            if color[k] == WHITE and dfs(k, stack):
                return True
        stack.pop()
        color[i] = BLACK
        return False

    for i in sorted(ctx.nodes):
        if color[i] == WHITE and dfs(i, []):
            emit("V4", "FAIL", f"cycle in requires+supportedBy: {' -> '.join(cycle)}")
            return
    emit("V4", "PASS", "requires+supportedBy union is acyclic")


def check_v5(ctx: Ctx) -> None:
    supported = set()
    for n in ctx.nodes.values():
        supported.update(n.get("supportedBy") or [])
    roots = sorted(i for i, n in ctx.nodes.items()
                   if n.get("type") == "goal" and i not in supported)
    if len(roots) == 1:
        emit("V5", "PASS", f"single root goal: {roots[0]}")
    else:
        emit("V5", "FAIL", f"expected exactly one unsupported goal node, got "
                           f"{len(roots)}: {roots[:6]}")


def check_v6(ctx: Ctx) -> None:
    bad = []
    for i, n in ctx.nodes.items():
        if n.get("status") not in STATUSES:
            bad.append(f"{i}: status {n.get('status')!r}")
        if n.get("type") not in TYPES:
            bad.append(f"{i}: type {n.get('type')!r}")
        if not isinstance(n.get("suspect"), bool):
            bad.append(f"{i}: suspect not bool")
        r = n.get("receipt")
        if isinstance(r, dict) and r.get("kind") not in KINDS:
            bad.append(f"{i}: receipt.kind {r.get('kind')!r}")
    if bad:
        emit("V6", "FAIL", "; ".join(bad[:6]))
    else:
        emit("V6", "PASS", "status/type/kind enums and suspect bools conform")


def _receipt_kind_ok(r: dict) -> str | None:
    kind = r.get("kind")
    if kind in ("repo-file", "offrepo-file"):
        if not isinstance(r.get("sha256"), str) or not SHA_RE.match(r["sha256"]):
            return "sha256 must be 64 lowercase hex"
    elif kind == "bus-comment":
        if r.get("sha256") is not None:
            return "bus-comment sha256 must be null"
        if not isinstance(r.get("path"), str) or not BUS_RE.match(r["path"]):
            return "bus-comment path must look like bus#<n>#issuecomment-<id>"
    return None


def check_v7(ctx: Ctx) -> None:
    bad = []
    for i, n in ctx.nodes.items():
        st, r = n.get("status"), n.get("receipt")
        if st in RECEIPTED:
            if not isinstance(r, dict):
                bad.append(f"{i}: {st} without a receipt")
                continue
            err = _receipt_kind_ok(r)
            if err:
                bad.append(f"{i}: {err}")
            if st == "MEASURED" and r.get("kind") != "repo-file":
                bad.append(f"{i}: MEASURED requires kind repo-file")
            if st == "LAW" and r.get("kind") != "bus-comment":
                bad.append(f"{i}: LAW requires kind bus-comment")
            if st == "MEASURED-OFFREPO":
                if r.get("kind") != "offrepo-file":
                    bad.append(f"{i}: MEASURED-OFFREPO requires kind offrepo-file")
                child = ctx.nodes.get(n.get("export_owed") or "")
                if not child or child.get("type") != "solution" or \
                        child.get("status") not in ("OPEN", "PARTIAL"):
                    bad.append(f"{i}: MEASURED-OFFREPO needs export_owed -> an "
                               f"OPEN/PARTIAL solution node")
        elif st in ("OPEN", "GUESS") and r is not None:
            bad.append(f"{i}: {st} must carry receipt: null")
    if bad:
        emit("V7", "FAIL", "; ".join(bad[:6]))
    else:
        emit("V7", "PASS", "status<->receipt conformance holds on every node")


def check_v8(ctx: Ctx) -> None:
    checked, bad = 0, []
    for i, n in ctx.nodes.items():
        r = n.get("receipt")
        if n.get("status") not in ("MEASURED", "PARTIAL") or not isinstance(r, dict):
            continue
        if r.get("kind") != "repo-file":
            continue
        checked += 1
        blob = committed_blob(ctx, r.get("path", ""))
        if blob is None:
            continue  # reachability is V9's finding
        digest = hashlib.sha256(blob).hexdigest()
        if digest != r.get("sha256"):
            bad.append(f"{i}: {r.get('path')} re-hashes {digest[:12]}… != recorded "
                       f"{str(r.get('sha256'))[:12]}… (set suspect: true; owner reviews)")
    if bad:
        emit("V8", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V8", "PASS", f"{checked} repo-file receipt(s) re-hash clean")


def check_v9(ctx: Ctx, origin_mode: bool) -> None:
    if origin_mode:
        try:
            shallow = _git(ctx, "rev-parse", "--is-shallow-repository").decode().strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            emit("V9", "FAIL", "SKIP-FATAL: cannot interrogate git for shallowness")
            return
        if shallow != "false":
            emit("V9", "FAIL", "SKIP-FATAL: shallow clone - refusing origin-mode "
                               "receipt checks (the 8-22 shallow-hub misread); "
                               "run git fetch --unshallow first")
            return
    checked, missing = 0, []
    for i, n in ctx.nodes.items():
        r = n.get("receipt")
        if not isinstance(r, dict) or r.get("kind") != "repo-file":
            continue
        checked += 1
        if committed_blob(ctx, r.get("path", "")) is None:
            missing.append(f"{i}: {r.get('path')}")
    basis = ctx.ref or "working-dir"
    if missing:
        emit("V9", "FAIL", f"receipt path(s) absent from {basis}: {missing[:4]}")
    else:
        emit("V9", "PASS", f"{checked} repo-file receipt path(s) reachable at {basis}")


def check_v10(ctx: Ctx) -> None:
    bad = []
    for i, n in ctx.nodes.items():
        for target in n.get("challenges") or []:
            t = ctx.nodes.get(target)
            if t and t.get("status") in ("MEASURED", "MEASURED-OFFREPO", "LAW") \
                    and n.get("status") != "KILLED":
                bad.append(f"{target} holds {t.get('status')} under unresolved "
                           f"challenger {i}")
    if bad:
        emit("V10", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V10", "PASS", "no node holds MEASURED/MEASURED-OFFREPO/LAW under an "
                            "unresolved challenger")


def check_v11(ctx: Ctx) -> None:
    bad = []
    for i, n in ctx.nodes.items():
        if n.get("status") != "KILLED":
            continue
        defeaters = [m for m in ctx.nodes.values()
                     if m.get("type") == "defeater"
                     and i in (m.get("challenges") or [])
                     and isinstance(m.get("receipt"), dict)
                     and _receipt_kind_ok(m["receipt"]) is None]
        if not defeaters:
            bad.append(f"{i}: no receipted defeater challenges it")
        if "reopening condition" not in str(n.get("notes", "")).lower():
            bad.append(f"{i}: notes lack a written REOPENING CONDITION")
    if bad:
        emit("V11", "FAIL", "; ".join(bad[:4]))
    else:
        killed = sum(1 for n in ctx.nodes.values() if n.get("status") == "KILLED")
        emit("V11", "PASS", f"every KILLED node ({killed}) has a receipted defeater "
                            f"and a reopening condition")


def check_v12(ctx: Ctx) -> None:
    owners = (ctx.data or {}).get("owners") or []
    bad = []
    rogue = sorted(set(owners) - LIVE_ROSTER)
    if rogue:
        bad.append(f"owners not in the live roster {sorted(LIVE_ROSTER)}: {rogue}")
    for i, n in ctx.nodes.items():
        if n.get("owner") not in owners:
            bad.append(f"{i}: owner {n.get('owner')!r} not in top-level owners")
    if bad:
        emit("V12", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V12", "PASS", f"owners {owners} live; every node owner is listed")


def check_v13(ctx: Ctx) -> None:
    now = datetime.now(timezone.utc) + timedelta(minutes=5)
    bad = []
    stamps = [("updated", (ctx.data or {}).get("updated"))]
    stamps += [(f"{i}.last_verified", n.get("last_verified"))
               for i, n in ctx.nodes.items()]
    for label, ts in stamps:
        # JSON has no date type, so every stamp arrives as a string and the
        # UTC (Z) basis is enforced by TS_RE - no parser-dependent coercion.
        if isinstance(ts, str) and TS_RE.match(ts):
            when = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        else:
            bad.append(f"{label}: {ts!r} not YYYY-MM-DDTHH:MM:SSZ")
            continue
        if when > now:
            bad.append(f"{label}: {ts} is in the future")
    if bad:
        emit("V13", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V13", "PASS", f"{len(stamps)} timestamp(s) well-formed and not in the future")


def check_v14(ctx: Ctx) -> None:
    emit("V14", "SKIP", "spec-only in M2: suspect-clear author=owner is a PR-mode "
                        "diff audit; enforced by review until M3 lands it")


def check_v15(ctx: Ctx) -> None:
    hits = []
    surfaces = [ctx.map_path]
    am_dir = ctx.map_path.parent
    if am_dir.is_dir():
        surfaces += sorted(p for p in am_dir.glob("*.md"))
    for p in surfaces:
        for lineno, line in enumerate(p.read_text(encoding="utf-8",
                                                  errors="replace").splitlines(), 1):
            if "retract" in line.lower():
                continue  # quoting a retracted figure to mark it false is allowed
            for rex in TOTAL_RES:
                if rex.search(line):
                    hits.append(f"{p.name}:{lineno}")
                    break
    if hits:
        emit("V15", "FAIL", f"hand-written total(s) on non-generated surface(s): "
                            f"{hits[:5]} (totals are validator-printed only, F4)")
    else:
        emit("V15", "PASS", f"no hand-written totals in {len(surfaces)} "
                            f"non-generated surface(s)")


def check_v16(ctx: Ctx) -> None:
    views_dir = ctx.map_path.parent / "views"
    view = views_dir / "MAP-VIEW.md"
    if not view.is_file():
        emit("V16", "FAIL", f"generated view missing: {view}")
        return
    bad = []
    for p in sorted(views_dir.glob("*")):
        if p.is_file():
            head = p.read_text(encoding="utf-8", errors="replace").lstrip()[:120]
            if not head.startswith("<!-- GENERATED"):
                bad.append(f"{p.name}: missing GENERATED banner")
    expected = map_render.render(ctx.data or {})
    actual = view.read_text(encoding="utf-8").replace("\r\n", "\n")
    if actual != expected:
        bad.append("MAP-VIEW.md differs from regeneration (hand-edit drift; "
                   "run python scripts/map_render.py)")
    if bad:
        emit("V16", "FAIL", "; ".join(bad[:3]))
    else:
        emit("V16", "PASS", "views carry the GENERATED banner and match regeneration")


def check_v17(ctx: Ctx) -> None:
    if ctx.baseline_text is None:
        emit("V17", "PASS", "no prior MAP.json at the baseline ref (first landing)")
        return
    try:
        old = json.loads(ctx.baseline_text) or {}
        old_ids = {n.get("id") for n in old.get("nodes", []) if isinstance(n, dict)}
    except json.JSONDecodeError:
        emit("V17", "FAIL", "baseline MAP.json unparseable - cannot prove no deletion")
        return
    gone = sorted(i for i in old_ids if i and i not in ctx.nodes)
    if gone:
        emit("V17", "FAIL", f"node id(s) deleted (ids are permanent; supersede "
                            f"instead): {gone[:5]}")
    else:
        emit("V17", "PASS", f"all {len(old_ids)} baseline ids still present")


def check_v18(ctx: Ctx) -> None:
    bad = []
    for i, n in ctx.nodes.items():
        for old in n.get("supersedes") or []:
            t = ctx.nodes.get(old)
            if t and t.get("superseded_by") != i:
                bad.append(f"{i} supersedes {old} but its superseded_by is "
                           f"{t.get('superseded_by')!r}")
        sb = n.get("superseded_by")
        if sb:
            s = ctx.nodes.get(sb)
            if not s or i not in (s.get("supersedes") or []):
                bad.append(f"{i} superseded_by {sb} without the forward edge")
    if bad:
        emit("V18", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V18", "PASS", "supersedes/superseded_by pairs consistent "
                            "(PR-mode grep sweep is review-enforced in M2)")


def check_v19(ctx: Ctx) -> None:
    bad = []
    for i, n in ctx.nodes.items():
        if n.get("status") not in ("MEASURED", "MEASURED-OFFREPO", "LAW"):
            continue
        for r in n.get("requires") or []:
            child = ctx.nodes.get(r)
            if child and child.get("status") not in HOLDS:
                bad.append(f"{i} ({n['status']}) requires {r} "
                           f"({child.get('status')})")
    if bad:
        emit("V19", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V19", "PASS", "no held node has an unheld requires child")


def check_v20(ctx: Ctx) -> None:
    bad = []
    guesses = {i for i, n in ctx.nodes.items() if n.get("status") == "GUESS"}
    for i, n in ctx.nodes.items():
        hit = guesses & set(n.get("requires") or [])
        if hit:
            bad.append(f"{i} requires GUESS node(s) {sorted(hit)}")
    # supportedBy closure of every MEASURED node must be GUESS-free
    def closure(start: str) -> set[str]:
        seen, stack = set(), [start]
        while stack:
            cur = stack.pop()
            for k in ctx.nodes.get(cur, {}).get("supportedBy") or []:
                if k not in seen:
                    seen.add(k)
                    stack.append(k)
        return seen
    for i, n in ctx.nodes.items():
        if n.get("status") == "MEASURED":
            hit = guesses & closure(i)
            if hit:
                bad.append(f"MEASURED {i} has GUESS in its supportedBy closure: "
                           f"{sorted(hit)}")
    if bad:
        emit("V20", "FAIL", "; ".join(bad[:4]))
    else:
        emit("V20", "PASS", f"{len(guesses)} GUESS node(s) contained (no requires "
                            f"use, no MEASURED support closure)")


def check_v21(ctx: Ctx) -> None:
    bad, warns = [], []
    incoming_tests: dict[str, int] = {}
    for i, n in ctx.nodes.items():
        if n.get("type") == "solution" and not (n.get("tests") or []):
            bad.append(f"{i}: solution with empty tests list (anti-theater rule)")
        for t in n.get("tests") or []:
            incoming_tests[t] = incoming_tests.get(t, 0) + 1
    for i, n in ctx.nodes.items():
        if n.get("type") == "goal" and n.get("status") == "OPEN":
            k = incoming_tests.get(i, 0)
            if k != 1:
                warns.append(f"{i} has {k} deciding experiment(s)")
    if bad:
        emit("V21", "FAIL", "; ".join(bad[:4]))
    else:
        msg = "every solution names what it tests"
        if warns:
            msg += (f"; WARN (A2, non-fatal in M2): {len(warns)} OPEN goal(s) "
                    f"without exactly one deciding experiment: {warns[:3]}")
        emit("V21", "PASS", msg)


def check_v22(ctx: Ctx) -> None:
    if TRAIN_LOCK_ID not in ctx.nodes:
        emit("V22", "PASS", "no n-train-lock node in this map (lock not applicable)")
        return
    unlockers = [i for i, n in ctx.nodes.items()
                 if TRAIN_LOCK_ID in (n.get("unlocks") or [])]
    lifted = bool(unlockers) and all(
        ctx.nodes[u].get("status") == "MEASURED" and not ctx.nodes[u].get("suspect")
        for u in unlockers)
    tagged = [i for i, n in ctx.nodes.items()
              if TRAIN_LOCK_ID in (n.get("inContextOf") or [])]
    bad = []
    if not lifted:
        for i in tagged:
            if ctx.nodes[i].get("status") in RECEIPTED:
                bad.append(f"{i} holds {ctx.nodes[i]['status']} while the "
                           f"train-lock is engaged (unlockers: {unlockers or 'none'})")
    if bad:
        emit("V22", "FAIL", "; ".join(bad[:4]))
    else:
        state = "lifted" if lifted else "engaged"
        emit("V22", "PASS", f"train-lock {state}; {len(tagged)} tagged "
                            f"student-training node(s) conform")


def print_totals(data: dict) -> None:
    st, ty = map_render.totals(data)
    parts = [f"{k}={st[k]}" for k in map_render.STATUS_ORDER if k in st]
    parts += [f"{k}={st[k]}" for k in sorted(st) if k not in map_render.STATUS_ORDER]
    print(f"\nTOTALS (machine-counted, the only citable counts): "
          f"nodes={sum(st.values())} " + " ".join(parts))
    print("TOTALS by type: " + " ".join(f"{k}={ty[k]}" for k in sorted(ty)))


def print_frontier(data: dict, top: int = 3) -> None:
    rows = map_render.frontier_nodes(data)[:top]
    print(f"\nOPEN FRONTIER top-{top} (requires-satisfied, nearest the root):")
    if not rows:
        print("  (empty - no OPEN node has all requires children held)")
    for n in rows:
        print(f"  {n['id']} [{n.get('owner')}]: {n.get('text', '')[:100]}")


def run_checks(ctx: Ctx, origin_mode: bool) -> list[tuple[str, str, str]]:
    """Fill and return `results` without printing (tests drive this directly)."""
    results.clear()
    check_v1(ctx)
    if ctx.data is None:
        # Cannot proceed structurally; report the rest as SKIP so the run
        # states what did not execute (PREFLIGHT lesson).
        for n in range(2, 23):
            emit(f"V{n}", "SKIP", "not run: MAP.json failed V1")
    else:
        check_v2(ctx)
        check_v3(ctx)
        check_v4(ctx)
        check_v5(ctx)
        check_v6(ctx)
        check_v7(ctx)
        check_v8(ctx)
        check_v9(ctx, origin_mode)
        check_v10(ctx)
        check_v11(ctx)
        check_v12(ctx)
        check_v13(ctx)
        check_v14(ctx)
        check_v15(ctx)
        check_v16(ctx)
        check_v17(ctx)
        check_v18(ctx)
        check_v19(ctx)
        check_v20(ctx)
        check_v21(ctx)
        check_v22(ctx)
    return results


def run_all(ctx: Ctx, origin_mode: bool) -> int:
    run_checks(ctx, origin_mode)
    fails = 0
    for check, level, msg in results:
        print(f"{check} {level} {msg}")
        if level == "FAIL":
            fails += 1
    ran = sum(1 for _, lvl, _ in results if lvl != "SKIP")
    skipped = len(results) - ran
    print(f"\n{ran} check(s) ran, {skipped} skipped, {fails} FAIL(s).")
    if ctx.data is not None:
        print_totals(ctx.data)
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", default=str(MAP_FILE))
    ap.add_argument("--origin", action="store_true",
                    help="validate receipts against origin/main (CI mode)")
    ap.add_argument("--wake", action="store_true",
                    help="read-only: print frontier top-3 + totals")
    args = ap.parse_args()

    map_path = Path(args.map)
    if not map_path.is_file():
        print(f"V1 FAIL MAP.json missing: {map_path}")
        return 1

    ref = "origin/main" if args.origin else "HEAD"
    repo = map_path.resolve().parent.parent.parent
    if not (repo / ".git").exists():
        ref = None  # fixture mode: working-dir bytes are the basis

    if args.wake:
        try:
            data = map_render.load_map(map_path)
        except Exception as exc:
            print(f"V1 FAIL MAP.json unparseable at wake: {exc}")
            return 1
        print_frontier(data)
        print_totals(data)
        return 0

    baseline = None
    if ref is not None:
        try:
            rel = map_path.resolve().relative_to(repo.resolve()).as_posix()
            baseline = subprocess.check_output(
                ["git", "cat-file", "blob", f"{ref}:{rel}"], cwd=repo,
                stderr=subprocess.DEVNULL).decode("utf-8")
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            baseline = None

    ctx = Ctx(map_path, repo, ref, baseline_text=baseline)
    code = run_all(ctx, origin_mode=args.origin)
    if code == 0:
        print_frontier(ctx.data or {})
    return code


if __name__ == "__main__":
    sys.exit(main())
