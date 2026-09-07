"""Ask "have we already done this?" before doing it. Leg C of the R-MEM build.

Root cause 7 of the 2026-09-02 guess audit: 87.4% of 2,641 tracked artifacts are
referenced from ZERO of the 91 declared routing surfaces, by design -- the
HARNESS-INDEX ``archive`` block counts files instead of indexing them. A seat cannot
consult a surface that does not exist, so tonight the same questions were investigated
twice within twenty minutes by the seat writing the report on that exact failure.

This is the query step. It does not ask the seat to remember anything; it searches the
artifacts themselves.

    python scripts/prior_art.py "lethal trigger"
    python scripts/prior_art.py "seat control" --limit 5
    python scripts/prior_art.py "position suite" --json

CATALOG-OPTIONAL BY DESIGN. When ``workflow/ARTIFACT-CATALOG.jsonl`` exists (SKYNET's
R-MEM PR 1) it is used as the fast path for titles/dates/leads. When it does not, the
same answer is derived from the tracked tree directly, so this tool is testable and
useful before the catalog lands and does not duplicate the catalog builder's work.

Content search is delegated to ``git grep``, which is memory-mapped C and searches the
8 MB banked JSONL files without loading them into Python. Only the handful of rows that
actually rank get opened for a title and a lead.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

# Field weights. A hit in the filename is the strongest signal a corpus like ours offers;
# a hit in the body of a 94 KB aggregator is the weakest. Ordering matters more than the
# exact values -- these are the ranks SKYNET's 10:05Z acceptance test asked for.
W_BASENAME = 5.0
W_PATH = 4.0
W_TITLE = 4.0
W_LEAD = 2.0
W_BODY = 1.0

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "workflow" / "ARTIFACT-CATALOG.jsonl"

# Where banked findings live. Ordered: earlier globs are the artifact bodies, the
# registers at the end are routing surfaces that carry adjudicated state.
ARTIFACT_DIRS = (
    "ptcg-agent/experiments/analysis/",
    "workflow/research/",
    "workflow/artifacts/",
    "workflow/reports/",
    "workflow/receipts/",
    "ptcg-agent/docs/experiments/",
    "ptcg-agent/experiments/design/",
    "ptcg-agent/experiments/eval/",
    # Inventory Phase 3 (2026-09-05): tools are artifacts too. "what tools exist and why" scored
    # PARTIAL because scripts/ and harness/ were outside the corpus (B2 five-question test).
    "scripts/",
    "ptcg-agent/harness/",
)
REGISTERS = (
    "workflow/ATTEMPTS-LEDGER.md",
    "workflow/DEAD-ENDS.md",
    "workflow/canon/RETRACTIONS.md",
    "workflow/DECISIONS.md",
    "workflow/IMPROVEMENT-INVENTORY.md",
    "workflow/NUMBERS-INVENTORY.md",
    "workflow/canon/GRAVEYARD-INDEX.json",
    "workflow/canon/SUPERSESSION-REGISTER.md",
)

# Adjudicated-state words. A hit carrying one of these is worth more than a raw mention:
# it means someone already ruled on it.
STATE_HINTS = (
    "RETRACTED", "SUPERSEDED", "VOID", "KILLED", "FALSIFIED", "CLOSED",
    "BANKED", "CONFIRMED", "DISPUTED", "INCONCLUSIVE", "NO_EDGE", "NULL",
    "UNREAD", "HARM", "GO", "OPEN GUESS",
)
DATE_RE = re.compile(r"(20\d\d-\d\d-\d\d)")
WORD_RE = re.compile(r"[A-Za-z0-9_]+")

# Phase 0b (archive-cleanup, 2026-09-05): a STATE is an explicit finding -- a top-level
# `status`/`verdict`/`state` key in a JSON artifact, or a `Verdict:` / `Status:` line in a
# markdown head. STATE_HINTS above stay a RANKING signal only. Measured defect (ASTRA,
# context-roadmap-review.json): the empty-bench receipt was rendered `[CONFIRMED NULL HARM GO]`
# from four words in its prose while its own status field read COMPLETE_ZERO_REACH_PARK_RULE.
# ASTRA audit 2026-09-05 (cleanup-implementation-audit.json): a code-fenced `Status: PASS`
# followed by `Verdict: REJECTED`, and a blockquoted historical `> Verdict: PASS` followed by
# `Verdict: RETRACTED`, both returned PASS; a truncated nested JSON object returned PASS via a
# regex fallback. Rules now: fenced blocks are not the document's finding; a blockquote is a
# quotation, not a declaration; two different declarations are a conflict (no state); JSON is
# parsed whole or yields no state -- never a regex guess.
_MD_STATE_RE = re.compile(
    r"^\s*\**\s*(?:Verdict|Status|State)\s*\**\s*:\s*\**\s*([^\n*]+?)\s*\**\s*$",
    re.IGNORECASE | re.MULTILINE,
)
# CommonMark fences are ``` or ~~~ (SKYNET-CODEX counterexample: a ~~~-fenced Status: PASS).
_FENCE_RE = re.compile(r"(```|~~~).*?(?:\1|\Z)", re.S)


def _json_state(doc: object) -> str:
    """Top-level status/verdict/state must AGREE; two different declarations are a conflict
    (SKYNET-CODEX counterexample 2026-09-05: {"status":"PASS","verdict":"FAIL"} returned PASS)."""
    if not isinstance(doc, dict):
        return ""
    found: list[str] = []
    for key in ("status", "verdict", "state"):
        val = doc.get(key)
        if isinstance(val, str) and val.strip():
            v = val.strip()[:60]
            if v not in found:
                found.append(v)
    return found[0] if len(found) == 1 else ""


def explicit_state(path: str, text: str) -> str:
    """The artifact's OWN declared state, or '' when it declares none (or declares two).

    Declared state is kept separate from any independent verification: this reads what
    the document says about itself and nothing more.
    """
    if path.endswith(".jsonl"):
        first = text.split("\n", 1)[0].strip()
        try:
            return _json_state(json.loads(first)) if first else ""
        except (ValueError, TypeError):
            return ""
    if path.endswith(".json"):
        try:
            return _json_state(json.loads(text))
        except (ValueError, TypeError):
            return ""          # invalid or truncated JSON declares nothing
    body = _FENCE_RE.sub("", text[:6000])
    lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith(">")]
    found: list[str] = []
    for m in _MD_STATE_RE.finditer("\n".join(lines)):
        val = m.group(1).strip()[:60]
        if val and val not in found:
            found.append(val)
    return found[0] if len(found) == 1 else ""


def keyword_hints(text: str) -> list[str]:
    """Adjudication words present in the head -- a retrieval hint, never a label."""
    upper = text.upper()
    return [h for h in STATE_HINTS if h in upper]

# Terms too common in this repo to carry signal; matching them alone is noise.
STOPWORDS = frozenset(
    "the a an and or of to is are was were be been for on in at by with from this that "
    "it its as we our us not no yes do does did run runs ran new old all any one two".split()
)


def sh(args: list[str], cwd: Path = REPO) -> str:
    try:
        out = subprocess.run(
            args, cwd=str(cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=60,
        )
        return out.stdout
    except (subprocess.SubprocessError, OSError):
        return ""


def _is_artifact(path: str) -> bool:
    """Test files and fixtures are not banked findings: with harness/ in the corpus a test's own
    nonsense-query string would match itself (negative control, 2026-09-05)."""
    name = path.rsplit("/", 1)[-1]
    return not (name.startswith("test_") or name.startswith("conftest"))


def tracked_corpus() -> list[str]:
    """Every tracked file under the artifact dirs, plus the registers."""
    files = [f for f in sh(["git", "ls-files", "--", *ARTIFACT_DIRS]).splitlines() if f and _is_artifact(f)]
    files += [r for r in REGISTERS if (REPO / r).is_file()]
    return files


def grep_files(term: str, corpus: set[str]) -> set[str]:
    """Files whose CONTENT contains term. git grep does the heavy lifting."""
    out = sh(["git", "grep", "-il", "--fixed-strings", term, "--", *ARTIFACT_DIRS])
    hits = {ln.strip() for ln in out.splitlines() if ln.strip()}
    for reg in REGISTERS:
        if (REPO / reg).is_file() and sh(
            ["git", "grep", "-il", "--fixed-strings", term, "--", reg]
        ).strip():
            hits.add(reg)
    return hits & corpus


def load_catalog() -> dict[str, dict]:
    """SKYNET's generated catalog, when it exists. Never required."""
    if not CATALOG.is_file():
        return {}
    rows: dict[str, dict] = {}
    try:
        with CATALOG.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict) and row.get("path"):
                    rows[row["path"]] = row
    except OSError:
        return {}
    return rows


def catalog_fingerprint() -> str:
    """Which corpus snapshot this search ran against.

    THE PRIOR_ART LINE IS A CLAIM, AND A CLAIM NEEDS A DENOMINATOR. "1781 hits" is not
    reproducible on its own: the same query over a corpus that has since grown returns a
    different number, and a reviewer cannot tell a stale line from a fresh one. Pinning the
    catalog fingerprint makes the line checkable against the tree it was produced from.

    `load_catalog()` cannot supply this -- it skips the header, which carries no "path".
    """
    if not CATALOG.is_file():
        return "no-catalog"
    try:
        with CATALOG.open(encoding="utf-8") as fh:
            head = json.loads(fh.readline() or "{}")
    except (OSError, json.JSONDecodeError, ValueError):
        return "no-catalog"
    fp = str(head.get("fingerprint") or "") if isinstance(head, dict) else ""
    return f"catalog:{fp[:16]}" if len(fp) >= 8 else "no-catalog"


def head_of(path: str, limit: int = 3000) -> str:
    try:
        with (REPO / path).open(encoding="utf-8", errors="replace") as fh:
            return fh.read(limit)
    except (OSError, ValueError):
        return ""


def describe(path: str, catalog: dict[str, dict]) -> tuple[str, str, str]:
    """(date, title, state) -- from the catalog when present, else from the file."""
    is_json = path.endswith((".json", ".jsonl"))
    # JSON keys are often emitted sorted, so "schema" can sit well past a 3 KB window --
    # the lethal audit is 3,416 B and its schema is in the last quarter. Read a wider
    # window for JSON; it is only ever done for the handful of rows that actually rank.
    text = head_of(path, 200_000 if is_json else 3000)
    # The state comes from the artifact's own explicit finding, never from the catalog's
    # keyword `state_hints` and never from words in the prose.
    state = explicit_state(path, text)

    row = catalog.get(path)
    if row:
        date = str(row.get("first_commit") or row.get("date") or "")[:10]
        title = str(row.get("title") or "")[:100]
        # The catalog takes a title from the first line of the file, which for a JSON
        # artifact is "{" or whichever key sorted first -- useless to a reader. Fall
        # through to our own schema extraction rather than print punctuation.
        if title and not _is_useless_title(title):
            return date or _date_from_path(path), title, state

    title = ""
    if is_json:
        # A JSON artifact's schema/tag identifies it; its first line is usually just
        # whichever key sorted first, which tells a reader nothing.
        m = re.search(r'"(?:schema|tag|name)"\s*:\s*"([^"]+)"', text)
        if m:
            title = m.group(1)[:100]
            games = re.search(r'"games_run"\s*:\s*(\d+)', text)
            if games:
                title += f"  (games_run={games.group(1)})"
    if not title:
        for line in text.splitlines():
            line = line.strip().lstrip("#").strip()
            if not line:
                continue
            if line.startswith(("{", "[", "---", "```")):
                continue
            title = line[:100]
            break
    return _date_from_path(path), title or "(no title)", state


def _is_useless_title(title: str) -> bool:
    """A title that identifies nothing. Seen in the wild on JSON rows: "{", '"games": ['."""
    stripped = title.strip()
    if len(stripped) < 3:
        return True
    return stripped[0] in "{[" and len(stripped) < 24


def _date_from_path(path: str) -> str:
    m = DATE_RE.search(path)
    return m.group(1) if m else ""


AGENT_DIR = REPO / "ptcg-agent" / "agent"
# Where a project-local import may legitimately resolve.
MODULE_DIRS = (AGENT_DIR, REPO / "ptcg-agent" / "harness", REPO / "scripts", REPO)
# Provided at runtime and never committed, so absence from the tree proves nothing.
# `cg` is the Pokemon-supplied engine -- git-ignored by policy (CLAUDE.md), imported by
# r2_verify and the harness. Without this the checker calls our most important agent code
# STALE, which is worse than saying nothing.
RUNTIME_MODULES = frozenset({"cg", "numpy", "np", "torch", "yaml", "requests", "pytest"})
IMPORT_RE = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w.]*)\s+import|import\s+([A-Za-z_][\w.]*))",
                       re.MULTILINE)


def code_liveness(path: str) -> tuple[str, list[str]]:
    """Do this code file's project-local imports still exist in ptcg-agent/agent/?

    A ranked hit that is code LOOKS like a ready patch. `tv-attach_bias/main.py` looked
    like one to SKYNET for two hours; its nine project-local imports -- policy_features,
    strategic_policy, coalition_expert, matchup_router, human_controller, residual_guard,
    advisor_guard, tactical_guard, experts -- resolve to NOTHING in the current agent. It
    is from a different architecture and could never have been applied.

    Returns (verdict, missing) where verdict is LIVE / STALE / "" (not code or no local
    imports to check). Stdlib and third-party imports are ignored: only modules that ought
    to resolve inside the agent package are evidence either way.
    """
    if not path.endswith(".py"):
        return "", []
    try:
        text = (REPO / path).read_text(encoding="utf-8", errors="replace")[:20000]
    except OSError:
        return "", []

    local: list[str] = []
    for m in IMPORT_RE.finditer(text):
        mod = (m.group(1) or m.group(2) or "").split(".")[0]
        if not mod or mod == "__future__":
            continue
        if mod in sys.stdlib_module_names or mod in RUNTIME_MODULES:
            continue
        local.append(mod)
    if not local:
        return "", []

    missing = []
    for mod in dict.fromkeys(local):          # dedupe, keep order
        if any((d / f"{mod}.py").exists() or (d / mod).is_dir() for d in MODULE_DIRS):
            continue
        missing.append(mod)
    if not missing:
        return "LIVE", []
    return "STALE", missing


def _size_of(path: str, catalog: dict[str, dict]) -> int:
    """Bytes, from the catalog when it has the row, else from disk. Used only to damp
    body hits in long documents, so a rough number is sufficient."""
    row = catalog.get(path)
    if row and isinstance(row.get("size"), int):
        return row["size"]
    try:
        return (REPO / path).stat().st_size
    except OSError:
        return 1000


def search(query: str, limit: int = 20) -> tuple[list[dict], dict]:
    started = time.time()
    terms = [t.lower() for t in WORD_RE.findall(query) if t.lower() not in STOPWORDS]
    terms = [t for t in terms if len(t) > 2]
    if not terms:
        return [], {"terms": [], "elapsed_s": 0.0, "corpus": 0, "catalog": False}

    corpus = tracked_corpus()
    corpus_set = set(corpus)
    catalog = load_catalog()

    # score[path] -> {term -> best FIELD WEIGHT for that term}
    scored: dict[str, dict[str, float]] = {}
    doc_freq: dict[str, int] = {}

    def bump(path: str, term: str, weight: float) -> None:
        slot = scored.setdefault(path, {})
        if weight > slot.get(term, 0.0):
            slot[term] = weight

    for term in terms:
        hit_paths: set[str] = set()
        for path in corpus:
            low = path.lower()
            if term in low:
                base = low.rsplit("/", 1)[-1]
                bump(path, term, W_BASENAME if term in base else W_PATH)
                hit_paths.add(path)
        # The catalog already holds a title and a lead for every artifact. Scoring them
        # was the gap SKYNET's 10:05Z acceptance test found: "tempo-verb" sits in
        # BATCH1-MANIFEST's TITLE, so the ranking never saw it and the doc never surfaced.
        for path, row in catalog.items():
            if path not in corpus_set:
                continue
            # For kind=data the catalog's title/lead are the first line and first 300 bytes
            # of a raw blob -- `[{"select":{"type":"YesNo"...`. Scoring that is scoring
            # noise, and it let 610 KB replay dumps escape the body-only damp by "matching"
            # a lead. Titles and leads are meaningful for prose and code, not for dumps.
            if row.get("kind") == "data":
                continue
            if term in str(row.get("title", "")).lower():
                bump(path, term, W_TITLE)
                hit_paths.add(path)
            elif term in str(row.get("lead", "")).lower():
                bump(path, term, W_LEAD)
                hit_paths.add(path)
        for path in grep_files(term, corpus_set):
            bump(path, term, W_BODY)
            hit_paths.add(path)
        doc_freq[term] = len(hit_paths)

    n_docs = max(len(corpus), 1)
    # IDF. A term in 3,000 files carries no information; a term in 5 files is the answer.
    # Without this, ATTEMPTS-LEDGER and DECISIONS max out EVERY query because they contain
    # every term -- four unrelated queries returned the same two files at the same score.
    idf = {t: math.log(1.0 + n_docs / (1.0 + doc_freq.get(t, 0))) for t in terms}

    rows: list[dict] = []
    for path, per_term in scored.items():
        matched = len(per_term)
        base = sum(w * idf[t] for t, w in per_term.items())
        # Length normalisation. A body hit in a 94 KB aggregator is far weaker evidence
        # than the same hit in a 4 KB memo; title/path hits are already length-independent
        # so only the body-weighted part is damped.
        size = _size_of(path, catalog)
        if max(per_term.values()) <= W_BODY:
            # NOTHING matched in the filename, path, title or lead -- every hit is a
            # passing mention in the body. A 610 KB replay dump mentions every term in the
            # game, which is how bulk data outranked findings on "energy option deck".
            # `kind` cannot separate these (the lethal audit is `data` too, at 3 KB);
            # only SIZE can, and a log damp is far too gentle across a 180x span.
            base /= math.sqrt(max(size, 1000) / 1000.0)
        else:
            # A filename/title hit is real evidence regardless of length, so damp only the
            # body-mention share of a mixed match.
            damp = 1.0 + math.log10(max(size, 1000) / 1000.0)
            body_share = sum(w * idf[t] for t, w in per_term.items() if w <= W_BODY)
            base -= body_share * (1.0 - 1.0 / damp)
        # Coverage still dominates -- a file matching every query word is what is wanted --
        # but it now scales the evidence rather than replacing it, so scores separate
        # instead of flattening at matched*100.
        score = base * (matched ** 1.5) / len(terms)
        rows.append({"path": path, "score": round(score, 2), "terms_matched": matched})

    rows.sort(key=lambda r: (-r["score"], r["path"]))
    top = rows[:limit]
    for row in top:
        date, title, state = describe(row["path"], catalog)
        verdict, missing = code_liveness(row["path"])
        crow = catalog.get(row["path"]) or {}
        hints = list(crow.get("state_hints") or []) or keyword_hints(
            head_of(row["path"], 3000))
        row.update(date=date, title=title, state=state, hints=hints,
                   code=verdict, missing_imports=missing)

    meta = {
        "terms": terms,
        "elapsed_s": round(time.time() - started, 3),
        "corpus": len(corpus),
        "catalog": bool(catalog),
        "total_hits": len(rows),
    }
    return top, meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Search banked artifacts before starting work. Zero games."
    )
    ap.add_argument("query", help="keywords, e.g. \"lethal trigger\"")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)

    # Windows consoles default stdout to cp1252. Three of the first five real queries (SKYNET,
    # 2026-09-02) crashed with UnicodeEncodeError on a hit title containing "→" BEFORE the
    # PRIOR_ART line printed -- so the gate's author path failed on the platform every seat on
    # the 5080 uses. Never let a title glyph stop the line the lint requires.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass

    rows, meta = search(args.query, args.limit)

    if args.as_json:
        print(json.dumps({"query": args.query, "meta": meta, "rows": rows}, indent=2))
        return 0

    src = "ARTIFACT-CATALOG" if meta["catalog"] else "tracked tree (catalog absent)"
    print(f'PRIOR ART: "{args.query}"')
    print(f"  terms {meta['terms']}  corpus {meta['corpus']} files  via {src}")
    print(f"  {meta['total_hits']} hits in {meta['elapsed_s']}s\n")
    if not rows:
        print("  NO PRIOR ART FOUND. Nothing banked matches -- this looks genuinely new.")
        return 0
    for row in rows:
        # [state] is the artifact's OWN finding. Keywords are shown as what they are.
        flag = f"  [{row['state']}]" if row["state"] else "  [state: UNKNOWN]"
        kw = f"  (keywords only: {', '.join(row['hints'][:4]).lower()})" if row.get("hints") else ""
        print(f"  {row['score']:>5}  {row['date'] or '----------'}  {row['path']}")
        print(f"         {row['title']}{flag}{kw}")
        # A code hit reads as a ready patch. Say whether it could even be applied.
        if row.get("code") == "STALE":
            miss = ", ".join(row["missing_imports"][:4])
            more = f" +{len(row['missing_imports']) - 4} more" if len(row["missing_imports"]) > 4 else ""
            print(f"         !! STALE CODE -- {len(row['missing_imports'])} import(s) "
                  f"do not exist in ptcg-agent/agent/: {miss}{more}")
        elif row.get("code") == "LIVE":
            print("         .. code: all project-local imports resolve in ptcg-agent/agent/")
    # MUST satisfy prereg_prior_art_lint.LINE_RE. The lint's own failure message tells the
    # author to paste "the PRIOR_ART line it prints", so if these two drift the gate rejects
    # its own instructions -- which is exactly what shipped: this line emitted no fingerprint
    # segment and every pre-reg written from it would have failed CI.
    print(f"\n  PRIOR_ART: \"{args.query}\" -> {meta['total_hits']} hits "
          f"-> {catalog_fingerprint()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
