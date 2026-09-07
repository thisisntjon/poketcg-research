#!/usr/bin/env python3
"""dock.py -- the two-way harness dock over the inventory: receive a bounded context packet, add a
validated finding, and check the layer. One command in, one command out, both source-bound.

Jon 2026-09-06: "I literally want them to be able to dock into it and be able to receive and add
information - I want it sophisticated." Research basis, each applied narrowly:
  - bounded active context + on-demand retrieval (Packer et al., MemGPT 2023; Liu et al., Lost in
    the Middle, TACL 2024): `dock in` returns a byte-capped packet and names what it omitted;
  - claims with falsifiers and receipts that live in git (SEED protocol, Simone Systems Research
    2026): `dock out` refuses a finding without sources, hashes, limitations and a reopen condition;
  - provenance as entity / activity / agent (W3C PROV-DM 2013): every finding names its source
    refs by path + commit + sha256 + locator, the producing seat, and the reviewed-at time;
  - one canonical representation per record (ASTRA 2026-09-05): a finding lands as a
    workflow/knowledge-register/records/<id>.json with an explicit standalone-finding schema, so the reader
    and the SRI registers both see it after `build_sri.py` -- no second store.

    python scripts/dock.py in  --task "<what you are about to do>" [--budget 12000] [--json]
    python scripts/dock.py out --finding finding.json [--dry-run]
    python scripts/dock.py check
    python scripts/dock.py template > finding.json      # a finding skeleton to fill in

`dock in` = INDEX head (what/state/five things) + the do-not-resume list + prior-art hits for the
task + open items touching it + the retraction reminder, cut to --budget bytes with an OMITTED line.
`dock out` = validate (schema, sources exist at the named commit with the named sha256, every number
checked against the retraction register, duplicate id refused, prior-art overlap reported), stage
the record, rebuild the SRI layer, run its --check. Committed retrieval is a separate check.
Nothing here runs games or calls a provider.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import retraction_register as rr  # noqa: E402
import research_memory as memory  # noqa: E402

SRI = REPO / "workflow" / "inventories" / "sri"
INDEX = SRI / "INDEX.md"
CURATED = SRI / "CURATED.json"
LEARN = SRI / "registers" / "LEARNINGS.md"
OPEN = SRI / "registers" / "OPEN.md"
RECORDS = REPO / "workflow" / "knowledge-register" / "records"

REQUIRED = ("id", "question", "why", "methodology", "result", "learn", "limitations", "reopen_when", "source_refs", "producer_seat")
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{1,63}$")
NUM_RE = re.compile(r"(?<![\w.])[+\-−]?\d+(?:\.\d+)?(?=\s*(?:pp|%|mu|μ)\b)")


def sh(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)


def utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass


# ---------------------------------------------------------------- dock in
def index_sections() -> dict[str, str]:
    text = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    out: dict[str, str] = {}
    cur = "head"
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = ""
            continue
        out[cur] = out.get(cur, "") + line + "\n"
    return out


def prior_art(task: str, limit: int = 6) -> str:
    r = sh([sys.executable, "scripts/prior_art.py", task, "--limit", str(limit)])
    lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    return "\n".join(lines[-(limit * 2 + 3):]) if lines else "(prior_art returned nothing)"


def register_rows(path: Path, terms: list[str], limit: int) -> list[str]:
    if not path.exists():
        return []
    hits = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and any(t in line.lower() for t in terms):
            hits.append(line[:400])
            if len(hits) >= limit:
                break
    return hits


def dock_in(task: str, budget: int, as_json: bool) -> int:
    secs = index_sections()
    terms = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", task)][:8]
    packet = {
        "schema": "ptcg.dock_packet/v1",
        "task": task,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "main": (sh(["git", "rev-parse", "origin/main"]).stdout or "").strip()[:12],
        "what_this_is": secs.get("What this is", "").strip(),
        "current_state": secs.get("Current state", "").strip(),
        "five_things": secs.get("The five things that matter", "").strip(),
        "do_not_resume": secs.get("Do NOT resume", "").strip(),
        "prior_art": prior_art(task),
        "learnings_touching_task": register_rows(LEARN, terms, 8),
        "open_items_touching_task": register_rows(OPEN, terms, 5),
        "rules": ["check every number: python scripts/retraction_register.py <number>",
                  "games = 0 and training = 0 until Jon lifts the pause (2026-09-05)",
                  "a finding is not banked until `dock out` accepts it and the PR is pushed",
                  "never edit generated registers; edit the record or the source and rebuild"],
        "omitted": [],
    }
    # byte cap: drop the largest optional sections until it fits, and say so
    order = ["prior_art", "learnings_touching_task", "open_items_touching_task", "do_not_resume", "five_things"]
    def size() -> int:
        return len(json.dumps(packet, ensure_ascii=False).encode("utf-8"))
    while size() > budget and order:
        k = order.pop(0)
        packet["omitted"].append(f"{k} (packet over {budget} bytes; open the register directly)")
        packet[k] = "" if isinstance(packet[k], str) else []
    if as_json:
        print(json.dumps(packet, ensure_ascii=False, indent=1))
    else:
        print(f"# DOCK IN — {task}\n(main {packet['main']}, {size():,} bytes of {budget:,})\n")
        for k in ("what_this_is", "current_state", "five_things", "do_not_resume"):
            if packet[k]:
                print(f"## {k}\n{packet[k]}\n")
        if packet["prior_art"]:
            print(f"## prior art for this task\n{packet['prior_art']}\n")
        for k in ("learnings_touching_task", "open_items_touching_task"):
            if packet[k]:
                print(f"## {k}\n" + "\n".join(packet[k]) + "\n")
        print("## rules\n- " + "\n- ".join(packet["rules"]))
        if packet["omitted"]:
            print("\n## OMITTED\n- " + "\n- ".join(packet["omitted"]))
    return 0


# ---------------------------------------------------------------- dock out
def template() -> dict:
    return {
        "schema": memory.FINDING_SCHEMA,
        "evidence_status": "source_assertion",
        "id": "E0xx-or-topic-slug",
        "question": "the one question this finding answers",
        "why": "why it was asked (what it unblocks or which assumption it tests)",
        "methodology": "exact design: arms, n per arm, opponents, engine, seeds, scoring, continuation rule",
        "result": "what was measured, with the numbers and their intervals; what it does NOT establish",
        "learn": "the reusable lesson, scoped",
        "limitations": ["every caveat a reader needs before reusing the result"],
        "reopen_when": "the named condition that would reopen this line",
        "related_ids": [],
        "source_refs": [{"path": "ptcg-agent/experiments/analysis/<receipt>.json", "git_commit": "<40-hex commit on origin>", "sha256": "<sha256 of the file at that commit>",
                         "locator": {"line_start": 1, "line_end": 1}}],
        "producer_seat": "SKYNET|ASTRA|ROACH|MISTY",
        "interpretation_basis": "author receipt | independent review | source-context review",
        "games_run": 0,
    }


def validate(rec: dict) -> list[str]:
    problems: list[str] = []
    if not isinstance(rec, dict):
        return ["finding must be a JSON object"]
    try:
        memory.validate_finding(rec)
    except memory.MemoryError as exc:
        problems.append(str(exc))
    for k in REQUIRED:
        if not rec.get(k):
            problems.append(f"missing required field: {k}")
    if rec.get("id") and not ID_RE.match(str(rec["id"])):
        problems.append("id must be a short slug (letters, digits, _ . -)")
    if rec.get("id") and (RECORDS / f"{rec['id']}.json").exists():
        problems.append(f"duplicate id: records/{rec['id']}.json exists (use a new id or a correction record that names it in related_ids)")
    if not isinstance(rec.get("limitations"), list) or not rec.get("limitations"):
        problems.append("limitations must be a non-empty list")
    refs = rec.get("source_refs") or []
    if not isinstance(refs, list) or not refs:
        problems.append("source_refs must be a non-empty list")
    try:
        snap = memory.Snapshot(REPO, "HEAD")
        cards, _ = memory.load(snap)
        ids = {c["id"] for c in cards}
        if rec.get("id") in ids:
            problems.append(f"duplicate id: {rec['id']} already exists in research memory")
    except memory.MemoryError as exc:
        return problems + [f"existing research memory unavailable: {exc}"]
    snapshots = {snap.commit: snap}
    for i, a in enumerate(refs if isinstance(refs, list) else []):
        if not isinstance(a, dict) or not a.get("path") or not a.get("git_commit") or not a.get("sha256"):
            problems.append(f"source_refs[{i}] needs path, git_commit, sha256")
            continue
        if not re.fullmatch(r"[0-9a-f]{40}", str(a["git_commit"])):
            problems.append(f"source_refs[{i}].git_commit must be a full 40-hex commit")
            continue
        try:
            memory.anchor_check(a, snap, snapshots)
        except (memory.MemoryError, ValueError, TypeError) as exc:
            problems.append(f"source_refs[{i}]: invalid locator or sha256 mismatch: {exc}")
    # every number with a unit in result/learn is checked against the retraction register
    text = " ".join(str(rec.get(k, "")) for k in ("result", "learn", "methodology"))
    for tok in sorted(set(NUM_RE.findall(text))):
        try:
            if rr.lookup(tok):
                problems.append(f"RETRACTED number in the finding: {tok} — see workflow/canon/RETRACTIONS.md")
        except rr.RegisterUnavailable as exc:
            problems.append(f"retraction register unavailable: {exc}")
            break
    if rec.get("games_run", 0) and not any("game" in str(x).lower() for x in [rec.get("methodology", "")]):
        problems.append("games_run > 0 but methodology does not describe the games")
    return problems


def dock_out(path: Path, dry: bool) -> int:
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"DOCK_OUT REFUSED: cannot read finding: {exc}")
        return 2
    if not isinstance(rec, dict):
        print("DOCK_OUT REFUSED: finding must be a JSON object")
        return 1
    # The writer creates an explicit standalone record, never an orphan annotation.
    rec.setdefault("schema", memory.FINDING_SCHEMA)
    rec.setdefault("evidence_status", "source_assertion")
    rec.setdefault("related_ids", [])
    problems = validate(rec)
    overlap = prior_art(str(rec.get("question", "")), limit=3)
    if problems:
        print("DOCK_OUT REFUSED:")
        for p in problems:
            print(f"  - {p}")
        print("prior-art overlap for the question (informational):\n" + overlap)
        return 1
    rec.setdefault("recorded_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    rec.setdefault("interpretation_basis", "author receipt (dock out); not independently reviewed")
    dest = RECORDS / f"{rec['id']}.json"
    if dry:
        print(f"DOCK_OUT DRY-RUN: finding valid; would write {dest.relative_to(REPO).as_posix()} and rebuild the SRI layer")
        print("prior-art overlap for the question (informational):\n" + overlap)
        return 0
    RECORDS.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for stage, argv in (("rebuild", [sys.executable, "scripts/build_sri.py"]),
                        ("check", [sys.executable, "scripts/build_sri.py", "--check"])):
        try:
            result = sh(argv)
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"DOCK_OUT INCOMPLETE: {stage} failed: {exc}; pending record retained at {dest}")
            return 2
        if result.returncode:
            print(f"DOCK_OUT INCOMPLETE: {stage} exited {result.returncode}; pending record retained at {dest}")
            print((result.stdout or "") + (result.stderr or ""))
            return result.returncode
    print(f"DOCK_OUT STAGED: wrote {dest.relative_to(REPO).as_posix()}; source checks and SRI rebuild/check passed. Not yet banked.")
    print("prior-art overlap for the question (informational):\n" + overlap)
    print(f"NEXT: commit on your branch, then run python scripts/research_memory.py show {rec['id']} and verify; push and request review. HEAD retrieval ignores uncommitted records.")
    return 0


# ---------------------------------------------------------------- dock ask
REGISTERS = ["LEARNINGS.md", "KNOWLEDGE-RECORDS.md", "CLAIMS.md", "METHODS.md", "OPEN.md", "RETEST-QUEUE.md", "TOOLS.md", "DECISIONS.md"]
STOP = frozenset("the a an and or of to is are was were be been for on in at by with from this that it its as we our us not no do did what why how which when have has had".split())


def dock_ask(question: str, kind: str | None, tag: str | None, limit: int) -> int:
    """Rank register rows by term hits; print each with its id, register, tags and source so the
    answer is one hop from its evidence. Lexical: a hit nominates, it never adjudicates."""
    terms = [t for t in re.findall(r"[a-z0-9][a-z0-9_.+-]{2,}", question.lower()) if t not in STOP]
    if not terms:
        print("DOCK_ASK: no searchable terms in the question")
        return 1
    hits: list[tuple[int, str, str, int, str]] = []
    for reg in REGISTERS:
        p = SRI / "registers" / reg
        if not p.exists():
            continue
        section = ""
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
            if line.startswith("## "):
                section = line[3:].split(" (")[0].strip()
                continue
            if not line.startswith("| ") or line.startswith("| #") or line.startswith("| id") or line.startswith("| date") or line.startswith("| tool"):
                continue
            if kind and reg == "LEARNINGS.md" and section != kind:
                continue
            if tag and reg in ("LEARNINGS.md", "RETEST-QUEUE.md") and tag not in line:
                continue
            low = line.lower()
            score = sum(low.count(t) for t in terms)
            if score:
                hits.append((score, reg, line, line_number, digest))
    hits.sort(key=lambda h: -h[0])
    print(f"# DOCK ASK — {question}\nterms {terms}" + (f" · kind {kind}" if kind else "") + (f" · tag {tag}" if tag else "") + f" · {len(hits)} row(s) hit; top {min(limit, len(hits))}\n")
    for score, reg, line, line_number, digest in hits[:limit]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rid = cells[0] if cells else "?"
        label = "display label" if re.fullmatch(r"L-\d+", rid) else "row label"
        print(f"[{reg}] {label} {rid} (score {score})\n  {line[:600]}")
        if len(line) > 600:
            print("  PREVIEW TRUNCATED: later evidence and qualifications may be omitted.")
        print(f"  Register: workflow/inventories/sri/registers/{reg}:{line_number} sha256={digest}\n")
    print("A hit is a lexical nomination. Register locators identify the local file bytes read, not a Git snapshot or primary evidence. "
          "An L-number is a display label, not a persistent record ID. Open the full row and follow its source before relying on it; "
          "check every number with retraction_register.py.")
    return 0 if hits else 1


def dock_check() -> int:
    c = sh([sys.executable, "scripts/build_sri.py", "--check"])
    print((c.stdout or "").strip())
    v = Path.home() / ".claude" / "skills" / "inventory" / "scripts" / "validate.py"
    if v.exists():
        g = sh([sys.executable, str(v), "--manifest", str(SRI / "MANIFEST.jsonl"), "--root", str(REPO), "--claims", str(SRI / "registers" / "CLAIMS.md")])
        print((g.stdout or "").strip().splitlines()[-1] if g.stdout else "validator produced no output")
    return c.returncode


def main(argv: list[str] | None = None) -> int:
    utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_in = sub.add_parser("in")
    p_in.add_argument("--task", required=True)
    p_in.add_argument("--budget", type=int, default=12000)
    p_in.add_argument("--json", action="store_true")
    p_out = sub.add_parser("out")
    p_out.add_argument("--finding", required=True)
    p_out.add_argument("--dry-run", action="store_true")
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("question")
    p_ask.add_argument("--kind", help="LEARNINGS section: dead-end, lesson, instrument-that-lied, knowledge-record, tried-result, graveyard, kill-card, ledger")
    p_ask.add_argument("--tag", help="retrieval tag, e.g. family:deck, instrument:power, process:review")
    p_ask.add_argument("--limit", type=int, default=12)
    sub.add_parser("check")
    sub.add_parser("template")
    a = ap.parse_args(argv)
    if a.cmd == "ask":
        return dock_ask(a.question, a.kind, a.tag, a.limit)
    if a.cmd == "in":
        return dock_in(a.task, a.budget, a.json)
    if a.cmd == "out":
        return dock_out(Path(a.finding), a.dry_run)
    if a.cmd == "check":
        return dock_check()
    print(json.dumps(template(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
