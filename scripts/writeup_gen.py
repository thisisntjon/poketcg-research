#!/usr/bin/env python3
"""writeup_gen.py -- the Strategy write-up APPENDIX generated from records (inventory Phase 2).

Jon 2026-09-05 (21:33Z): a records-generated appendix is allowed; no agent-authored prose
thesis. B4 measured ~40-45% of the write-up as generable today. This tool generates what the
records support, prints a coverage line per section, and writes an explicit NO_RECORD line
where nothing exists (thesis, final leaderboard number, the fielded deck's concept, figures).
Nothing is invented; nothing is summarised in the tool's own words beyond field labels.

Sources (all parsed report-only; a parse failure is reported, never fatal):
  workflow/inventories/IDENTITY.json            product card = the SUBMITTED product (live_ladder)
  workflow/canon/RETRACTIONS.md                 via scripts/retraction_register.py (values + claims)
  workflow/ATTEMPTS-LEDGER.md                   GR-* rows: id, finding, evidence (n / effect / CI / sha presence)
  workflow/inventories/TRIED-RESULTS-COMPACT.json rows {id, tried, result, class, reuse}
  workflow/research/2026-09-02-closures-for-the-writeup.md  section-1 table: the closed lines with numbers
  workflow/DECISIONS.md                          rows (UTC, decision, basis, confidence, reverse_if); last date
  git log --diff-filter=A on scripts/ + harness/  tool timeline: first commit date, PR #, subject (run time)
  workflow/answer-map/MAP.json                   claim binding: SUPPORTED / DISPUTED / UNBOUND (read-only)

    python scripts/writeup_gen.py            # writes workflow/writeup/APPENDIX.md + APPENDIX.json
    python scripts/writeup_gen.py --check    # exit 1 if the committed appendix drifted from the records
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
sys.path.insert(0, str(REPO / "scripts"))
import retraction_register as rr  # noqa: E402

IDENTITY = REPO / "workflow" / "inventories" / "IDENTITY.json"
LEDGER = REPO / "workflow" / "ATTEMPTS-LEDGER.md"
TRIED = REPO / "workflow" / "inventories" / "TRIED-RESULTS-COMPACT.json"
CLOSURES = REPO / "workflow" / "research" / "2026-09-02-closures-for-the-writeup.md"
DECISIONS = REPO / "workflow" / "DECISIONS.md"
MAP = REPO / "workflow" / "answer-map" / "MAP.json"
OUT_MD = REPO / "workflow" / "writeup" / "APPENDIX.md"
OUT_JSON = REPO / "workflow" / "writeup" / "APPENDIX.json"

RUBRIC = "Model 70 / Deck 20 / Report 10; one Kaggle Writeup <= 2,000 words; due 2026-09-13 23:59 UTC (workflow/research/phase-live-rules.md)"

# The submission card's required fields. Coverage = how many of these the identity file carries.
S0_REQUIRED = ("name", "main_py_sha256", "deck_csv_sha256", "archive_sha256", "provenance")

NUM_RE = re.compile(r"(?<![\w.])([+\-−]?\d+(?:\.\d+)?)(pp|%|mu|μ)?(?![\w.])")
CI_RE = re.compile(r"\[\s*[+\-−]?\d+(?:\.\d+)?\s*,\s*[+\-−]?\d+(?:\.\d+)?\s*\]")
N_RE = re.compile(r"(?:n\s*=\s*|(?<!\d))(\d{1,3}(?:,\d{3})+|\d{2,6})\s*(?:/arm|per arm|games|cells|rows)", re.I)
EFFECT_RE = re.compile(r"[+\-−]\d+(?:\.\d+)?\s*pp")
SHA_RE = re.compile(r"\b[0-9a-f]{8,64}\b")


def sh(args: list[str]) -> str:
    r = subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    return r.stdout if r.returncode == 0 else ""


def cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


# ---------------------------------------------------------------- parsers (report-only)
def parse_ledger() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    if not LEDGER.exists():
        return rows, {"error": "ATTEMPTS-LEDGER.md missing"}
    for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| GR-"):
            continue
        c = cells(line)
        if len(c) < 4:
            continue
        ev = c[2]
        rows.append({
            "id": c[0].strip("*` "), "finding": c[1][:200], "evidence": ev[:300], "status": c[3][:160],
            "has_n": bool(N_RE.search(ev)), "has_effect": bool(EFFECT_RE.search(ev)),
            "has_ci": bool(CI_RE.search(ev)), "has_sha": bool(SHA_RE.search(ev)),
        })
    n = len(rows) or 1
    cov = {"rows": len(rows), "n_pct": round(100 * sum(r["has_n"] for r in rows) / n),
           "effect_pct": round(100 * sum(r["has_effect"] for r in rows) / n),
           "ci_pct": round(100 * sum(r["has_ci"] for r in rows) / n),
           "sha_pct": round(100 * sum(r["has_sha"] for r in rows) / n)}
    return rows, cov


def parse_tried() -> list[dict]:
    if not TRIED.exists():
        return []
    try:
        return list(json.loads(TRIED.read_text(encoding="utf-8")).get("rows", []))
    except ValueError:
        return []


def parse_closures() -> list[dict]:
    out: list[dict] = []
    if not CLOSURES.exists():
        return out
    in_s1 = False
    for line in CLOSURES.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("## 1."):
            in_s1 = True
            continue
        if in_s1 and line.startswith("## "):
            break
        if in_s1 and re.match(r"\|\s*\d+\s*\|", line):
            c = cells(line)
            if len(c) >= 5:
                out.append({"n": c[0], "line": c[1][:160], "screen": c[2][:120], "confirmation": c[3][:160], "verdict": c[4][:60],
                            "interval": (CI_RE.search(c[3]) or CI_RE.search(c[2]) or re.match(r"", ""))})
                out[-1]["interval"] = out[-1]["interval"].group(0) if out[-1]["interval"] else None
    return out


def parse_decisions() -> dict:
    if not DECISIONS.exists():
        return {"rows": 0}
    rows = [cells(l) for l in DECISIONS.read_text(encoding="utf-8", errors="replace").splitlines()
            if l.startswith("| ") and not l.startswith("| UTC") and not l.startswith("|--")]
    # DECISIONS.md is not date-ordered (newest rows were prepended in August); report min/max.
    dates = sorted(m.group(0) for r in rows if r for m in [re.match(r"\d\d-\d\d", r[0])] if m)
    return {"rows": len(rows), "first": dates[0] if dates else None, "last": dates[-1] if dates else None,
            "sample_last": [r[1][:140] for r in rows[:3]] if rows else []}


def tool_history_complete() -> bool:
    """Only verified complete history can establish file-addition attribution."""
    return read_tool_timeline()[0]


def tool_timeline() -> list[dict]:
    return read_tool_timeline()[1]


def read_tool_timeline() -> tuple[bool, list[dict]]:
    """Bind coverage to the same successful traversal that produced the events."""
    try:
        if (sh(["git", "rev-parse", "--is-shallow-repository"]).strip() != "false"
                or not sh(["git", "rev-parse", "--verify", "origin/main^{commit}"]).strip()):
            return False, []
        result = subprocess.run(
            ["git", "log", "origin/main", "--diff-filter=A", "--date=short",
             "--format=COMMIT|%ad|%h|%s", "--name-only", "--", "scripts/*.py", "ptcg-agent/harness/*.py"],
            cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return False, []
    if result.returncode != 0:
        return False, []
    out = result.stdout
    events: list[dict] = []
    cur: dict | None = None
    for line in out.splitlines():
        if line.startswith("COMMIT|"):
            _, d, h, s = line.split("|", 3)
            m = re.search(r"\(#(\d+)\)\s*$", s)
            cur = {"date": d, "commit": h, "pr": int(m.group(1)) if m else None, "why": s[:140], "tools": []}
            events.append(cur)
        elif line.strip() and cur is not None and line.endswith(".py"):
            cur["tools"].append(line.strip())
    events = [e for e in events if e["tools"]]
    events.sort(key=lambda e: (e["date"], e["commit"]))
    return True, events


def map_nodes() -> list[dict]:
    if not MAP.exists():
        return []
    try:
        d = json.loads(MAP.read_text(encoding="utf-8"))
    except ValueError:
        return []
    return list(d.get("nodes", []))


def nodes_naming(number: str, nodes: list[dict]) -> list[dict]:
    """Answer-map nodes whose text or id contains `number` as a whole numeric token.

    ASTRA 2026-09-05 (#3455 finding 1): the previous substring test let `7.8` match `17.82`.
    A token match is bounded by non-digit, non-point characters on both sides.
    """
    q = rr.normalise(number)
    if not q:
        return []
    pat = re.compile(r"(?<![\d.])" + re.escape(q) + r"(?![\d.])")
    return [n for n in nodes if pat.search(json.dumps(n.get("text", "")) + " " + json.dumps(n.get("id", "")))]


def check_claim(number: str, nodes: list[dict]) -> str:
    """Read-only binding of one printed number.

    RETRACTED comes from the register and is a verdict. Everything else is a NOMINATION: the
    answer-map nodes that name the number, each with the status the node itself declares. A
    lexical match can nominate evidence; it never adjudicates it, so this function never prints
    SUPPORTED (ASTRA #3455 finding 1: an OPEN node and an unrelated number both rendered
    SUPPORTED(OPEN)). The reviewed inference lives on the node; read it there.
    """
    try:
        if rr.lookup(number):
            return "RETRACTED"
    except rr.RegisterUnavailable:
        return "REGISTER_UNAVAILABLE"
    hits = nodes_naming(number, nodes)
    if not hits:
        return "NOT_RETRACTED, UNBOUND"
    named = sorted(f"{n.get('id')}:{n.get('status')}" for n in hits)
    return "NOT_RETRACTED, NAMED_BY(" + ",".join(named)[:160] + ")"


def claim_for(text: str, nodes: list[dict]) -> str:
    """check-claim verdict for the first effect-size number in a cell, or '-' when there is none."""
    m = EFFECT_RE.search(text)
    if not m:
        return "-"
    n = NUM_RE.search(m.group(0))
    return check_claim(n.group(1), nodes) if n else "-"


# ---------------------------------------------------------------- sections
def build() -> dict:
    ident = json.loads(IDENTITY.read_text(encoding="utf-8")) if IDENTITY.exists() else {}
    roles = ident.get("roles", {})
    sub = roles.get("submitted_product", {})
    live = sub.get("live_ladder") or {}
    ledger, ledger_cov = parse_ledger()
    tried = parse_tried()
    closures = parse_closures()
    decisions = parse_decisions()
    values = [r for r in rr.parse() if r.section == "values"]
    claims = [r for r in rr.parse() if r.section == "claims"]
    history_complete, tools = read_tool_timeline()
    nodes = map_nodes()

    sections: list[dict] = []

    def sec(sid: str, title: str, coverage: str, body: list[str], no_record: list[str] | None = None) -> None:
        sections.append({"id": sid, "title": title, "coverage": coverage, "body": body, "no_record": no_record or []})

    # S0 product card -- the SUBMITTED product, never the experimental Parent.
    # ASTRA #3455 finding 3: coverage is verified-required-fields / required-fields, never "100%"
    # when the identity file is absent. Finding 4: the PRODUCT-PASSPORT describes a laboratory
    # candidate and says it is not a submission claim, so it is rendered as a separate record,
    # not joined into the submission card.
    present = [k for k in S0_REQUIRED if live.get(k)]
    passport = sub.get("passport") or {}
    s0_body = [
        f"name: `{live.get('name')}` · role: `{live.get('role')}` · kind: `{live.get('kind')}` · licence: {live.get('licence')} · modification: {live.get('modification')}",
        f"main.py sha256 `{live.get('main_py_sha256')}` · deck.csv sha256 `{live.get('deck_csv_sha256')}` · archive `{live.get('archive_sha256')}`",
        f"provenance: `{live.get('provenance')}`",
        f"experimental Parent (NOT the submitted product): repo main.py `{((roles.get('experimental_parent') or {}).get('repo_tuple') or {}).get('ptcg-agent/agent/main.py', {}).get('sha256')}` — see IDENTITY.json",
    ] if IDENTITY.exists() else []
    if passport:
        s0_body.append(
            f"separate record, NOT joined to the submission: PRODUCT-PASSPORT `{passport.get('product_id')}` "
            f"status {passport.get('status')} stamped {passport.get('stamped_utc')} — the passport describes a laboratory "
            f"candidate and declares itself not a submission claim; no evidence-backed relation to the submitted bytes is recorded")
    s0_missing = [k for k in S0_REQUIRED if not live.get(k)]
    sec("S0", "Submission card (the submitted product)",
        f"{len(present)}/{len(S0_REQUIRED)} required fields present in IDENTITY.json"
        f" ({'file present' if IDENTITY.exists() else 'FILE ABSENT'}); extraction coverage, not scientific review",
        s0_body,
        (["NO_RECORD: IDENTITY.json absent — no submitted-product identity available"] if not IDENTITY.exists() else [])
        + ([f"NO_RECORD: submitted-product fields missing: {', '.join(s0_missing)}"] if s0_missing and IDENTITY.exists() else []))

    sec("S1", "Thesis / why this strategy", "0% (no thesis-of-record decision exists; four incompatible drafts — B4)",
        [], ["NO_RECORD: thesis_of_record — a `decision` tagged thesis_of_record does not exist; not generated, not invented"])

    sec("S3", "Hypotheses tested, incl. negatives (ATTEMPTS-LEDGER GR rows + closures table)",
        f"GR rows {ledger_cov.get('rows')}: n {ledger_cov.get('n_pct')}% · effect {ledger_cov.get('effect_pct')}% · CI {ledger_cov.get('ci_pct')}% · sha {ledger_cov.get('sha_pct')}%; closures table {len(closures)} rows; TRIED-RESULTS {len(tried)} rows",
        ["| id | finding | status | n | effect | CI | sha |", "|---|---|---|---|---|---|---|"]
        + [f"| {r['id']} | {r['finding'][:110]} | {r['status'][:60]} | {'y' if r['has_n'] else '-'} | {'y' if r['has_effect'] else '-'} | {'y' if r['has_ci'] else '-'} | {'y' if r['has_sha'] else '-'} |" for r in ledger]
        + ["", "**Closed lines with the number that closes them** (`2026-09-02-closures-for-the-writeup.md` §1):", "| # | line | screen | confirmation | verdict | check-claim |", "|---|---|---|---|---|---|"]
        + [f"| {c['n']} | {c['line'][:100]} | {c['screen'][:60]} | {c['confirmation'][:90]} | {c['verdict']} | {claim_for(c['confirmation'], nodes)} |" for c in closures]
        + ["", "**TRIED-RESULTS-COMPACT** (class discipline: PHYSICS / SCARCITY / UNREAD):", "| id | tried | result | class | reuse |", "|---|---|---|---|---|"]
        + [f"| {t.get('id')} | {str(t.get('tried'))[:60]} | {str(t.get('result'))[:60]} | {t.get('class')} | {t.get('reuse', '')} |" for t in tried])

    sec("S6", "Performance within the track (final leaderboard)", "0%",
        [], ["NO_RECORD: final leaderboard rank/mu/date — no dated record exists on main (ladder closed 2026-08-16; ladder_log.csv re-emits a retracted value and is not citable)"])

    sec("S7", "Deck concept and key cards (20% of the rubric)", "identity only (deck sha256 known; concept and key-card rationale absent)",
        [f"submitted deck.csv sha256 `{live.get('deck_csv_sha256')}` (tetsutani's deck; all deck-chapter drafts on main are Lucario-era and describe a different product)"],
        ["NO_RECORD: deck concept / key cards / deck-policy co-optimisation for the submitted product"])

    months: dict[str, dict] = {}
    for e in tools:
        m = months.setdefault(e["date"][:7], {"events": 0, "tools": 0, "with_pr": 0})
        m["events"] += 1
        m["tools"] += len(e["tools"])
        m["with_pr"] += 1 if e["pr"] else 0
    recent = tools[-60:]
    sec("S8", "Timeline: tools — when created and why (from git, at run time)",
        f"{sum(len(e['tools']) for e in tools)} .py file-addition events over {len(tools)} commits (a count of files added under scripts/ and harness/, not of useful tools); PR number present on {sum(1 for e in tools if e['pr'])}/{len(tools)} events; 'why' = the commit subject (no PR body read); the complete list is persisted as APPENDIX.json `tool_events`; the last {len(recent)} events below",
        ["**Per month:**", "| month | first-commit events | tools added | events with a PR # |", "|---|---|---|---|"]
        + [f"| {k} | {v['events']} | {v['tools']} | {v['with_pr']} |" for k, v in sorted(months.items())]
        + ["", f"**Most recent {len(recent)} events:**", "| date | commit | PR | tools added | why (commit subject) |", "|---|---|---|---|---|"]
        + [f"| {e['date']} | {e['commit']} | {('#' + str(e['pr'])) if e['pr'] else '-'} | {', '.join(Path(t).name for t in e['tools'][:4])}{' …' if len(e['tools']) > 4 else ''} | {e['why'][:90]} |" for e in recent])

    if not history_complete:
        timeline = sections[-1]
        timeline["coverage"] = ("UNKNOWN_HISTORY: truncated or unavailable Git history; "
                                "tool_events withheld, not evidence of zero tools")
        timeline["body"] = []
        timeline["no_record"] = ["NO_RECORD: verified tool creation dates, commits and reasons"]

    sec("S9", "Instruments that lied; self-correction (retraction register)",
        f"100% — {len(values)} value rows, {len(claims)} claim rows parsed by retraction_register.py",
        ["| value | use instead | why | retracted |", "|---|---|---|---|"]
        + [f"| {', '.join(v.numbers + tuple(h[:12] for h in v.hashes)) or v.raw[:40]} | {v.use_instead[:70]} | {v.why[:90]} | {v.retracted} |" for v in values]
        + ["", "| claim | why | retracted |", "|---|---|---|"]
        + [f"| {c.raw[:100]} | {c.why[:90]} | {c.retracted} |" for c in claims])

    sec("S10", "Figures", "0%", [], ["NO_RECORD: figure specs bound to records — two figures are needed and neither exists as a record"])

    sec("S11", "Honest limits / open problems (decisions register + open attempts)",
        f"DECISIONS.md {decisions.get('rows')} rows, first {decisions.get('first')} → last {decisions.get('last')} (post-08-13 decisions have no source file — B4); GR rows with OPEN status: {sum(1 for r in ledger if 'OPEN' in r['status'].upper())}",
        [f"- last decisions: {d}" for d in decisions.get("sample_last", [])]
        + [f"- open: {r['id']} — {r['finding'][:120]}" for r in ledger if "OPEN" in r["status"].upper()][:12])

    doc = {
        "schema": "ptcg.writeup_appendix/v1",
        "rubric": RUBRIC,
        "generated_from": {"main": sh(["git", "rev-parse", "origin/main"]).strip(),
                           "identity": ident.get("generated_from"), "tool": "scripts/writeup_gen.py"},
        "sections": sections,
        # ASTRA #3455 finding 5: the text promised the full event list in APPENDIX.json while
        # build() kept only the last 60 as section text. The complete list is persisted here.
        "tool_events": tools,
        "tool_history_status": "COMPLETE" if history_complete else "UNKNOWN_HISTORY",
        "no_record_total": sum(len(s["no_record"]) for s in sections),
    }
    doc["digest"] = hashlib.sha256(json.dumps({k: v for k, v in doc.items() if k != "digest"}, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return doc


def render(doc: dict) -> str:
    lines = ["# Strategy write-up — APPENDIX generated from records", "",
             f"Rubric: {doc['rubric']}. This appendix is an attachment, not the 2,000-word body. Every row comes from a record named in its section; `NO_RECORD` lines are where nothing exists and nothing was invented. Generated from main `{doc['generated_from']['main'][:12]}`; digest `{doc['digest'][:16]}`.", ""]
    for s in doc["sections"]:
        lines.append(f"## {s['id']} — {s['title']}")
        lines.append(f"*coverage: {s['coverage']}*")
        lines.append("")
        lines += s["body"]
        lines += [f"- **{nr}**" for nr in s["no_record"]]
        lines.append("")
    lines.append(f"NO_RECORD lines: {doc['no_record_total']}. check-claim column legend: RETRACTED (register verdict) · NAMED_BY(node:status) (answer-map nodes naming the number, each with its own declared status — a nomination, not an adjudication) · UNBOUND (no node names the number).")
    return "\n".join(lines) + "\n"


def check_outputs(doc: dict, md: str) -> list[str]:
    """Every way the stored appendix can disagree with the regenerated one. Empty = consistent."""
    problems: list[str] = []
    if not OUT_JSON.exists():
        problems.append(f"{OUT_JSON.name} missing")
    else:
        try:
            old = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        except ValueError:
            old = None
            problems.append(f"{OUT_JSON.name} is not valid JSON")
        if not isinstance(old, dict):
            problems.append(f"{OUT_JSON.name} must contain a JSON object")
        elif old != doc:
            problems.append(f"{OUT_JSON.name} content differs from the regenerated document")
    if not OUT_MD.exists():
        problems.append(f"{OUT_MD.name} missing")
    elif OUT_MD.read_text(encoding="utf-8").replace("\r\n", "\n") != md:
        problems.append(f"{OUT_MD.name} content differs from the rendered document")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    doc = build()
    md = render(doc)
    if a.check:
        # ASTRA #3455 finding 2: comparing only the stored digest field accepted altered JSON that
        # kept its digest, and an entirely replaced Markdown. Compare the stored CONTENT against
        # the regenerated content, both files.
        problems = check_outputs(doc, md)
        if problems:
            for p in problems:
                print(f"APPENDIX_CHECK DRIFT (advisory): {p}")
            print("APPENDIX_CHECK DRIFT (advisory): regenerate with python scripts/writeup_gen.py")
            return 1
        print("APPENDIX_CHECK OK", doc["digest"][:16])
        return 0
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    shown = OUT_MD.relative_to(REPO).as_posix() if OUT_MD.is_relative_to(REPO) else str(OUT_MD)
    print(f"APPENDIX written: {shown} {len(md.encode('utf-8'))} bytes; sections {len(doc['sections'])}; "
          f"NO_RECORD {doc['no_record_total']}; digest {doc['digest'][:16]}")
    for s in doc["sections"]:
        print(f"  {s['id']}: {s['coverage'][:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
