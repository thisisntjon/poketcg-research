"""Read research memory in small, source-bound pieces. No engines or providers.

Consumer: a harness asking what was tried, why, how, what happened and what to reuse.
The experiment ledger and compact register remain authoritative source records. This
reader extracts them from one Git snapshot; optional review notes add interpretation
without replacing original text. It does not create another mutable search database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXPERIMENTS = "ptcg-agent/docs/experiments/"
RESEARCH = "workflow/research/"
INBOX = "workflow/inbox-2026-09/"
COMPACT = "workflow/inventories/TRIED-RESULTS-COMPACT.json"
NOTES = "workflow/knowledge-register/records/"
AUDITS = "workflow/knowledge-register/audits/"
RETRACTIONS = "workflow/canon/RETRACTIONS.md"
CATALOG = "workflow/inventories/MASTER-INVENTORY-INDEX.json"
CATALOG_DOCUMENT_IDS = {"LOSS_MODES", "ASSET_INDEX", "IMPROVEMENT", "REPLAY_STORES", "STRATEGY_ATLAS",
                        "KNOWLEDGE", "MEASUREMENTS_INDEX", "NUMBERS_INVENTORY"}
HISTORY = {
    "attempt": "workflow/ATTEMPTS-LEDGER.md",
    "deadend": "workflow/DEAD-ENDS.md",
    "retraction": RETRACTIONS,
    "equation": "workflow/canon/EQUATIONS.md",
    "lesson": "workflow/LESSONS.md",
    "measured": "workflow/canon/MEASURED-2026-08-06.md",
    "supersession": "workflow/canon/SUPERSESSION-REGISTER.md",
}
REGISTERS = {
    "consumer": ("workflow/inventories/CONSUMER-72H-LEDGER.json", "rows"),
    "graveyard": ("workflow/canon/GRAVEYARD-INDEX.json", "cards"),
    "tool": ("workflow/inventories/TOOLS-OUTPUT-EXISTS.json", "tools"),
    "hypothesis": ("workflow/inventories/HYPOTHESIS-KILL-CARDS.json", "hypotheses"),
    "metric": ("workflow/inventories/METRICS-INVENTORY.json", "metrics"),
    "domain_term": ("workflow/inventories/DOMAIN-TERM-FIXTURE-REGISTER.json", "rows"),
    "trace_source": ("workflow/inventories/OWNED-TRACE-MANIFEST.json", "candidate_sources"),
}
LINKS = "workflow/knowledge-register/relationships.json"
SCHEMA = "ptcg.research_memory/v1"
FINDING_SCHEMA = "ptcg.research_finding/v1"


class MemoryError(ValueError):
    """Unavailable or inconsistent evidence; never interpreted as an empty result."""


def validate_finding(record: dict) -> None:
    """Explicit standalone records; legacy notes still require an existing target."""
    if not isinstance(record, dict) or record.get("schema") != FINDING_SCHEMA:
        raise MemoryError("Standalone finding needs the research_finding/v1 schema")
    for key in ("id", "question", "why", "methodology", "result", "learn", "reopen_when", "producer_seat"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise MemoryError(f"Standalone finding needs nonempty text: {key}")
    if record.get("evidence_status") not in {"source_assertion", "observed_artifact"}:
        raise MemoryError("Standalone finding needs an explicit evidence_status; no automatic certification")
    limits, refs, related = record.get("limitations"), record.get("source_refs"), record.get("related_ids")
    if not isinstance(limits, list) or not limits or any(not isinstance(x, str) or not x.strip() for x in limits):
        raise MemoryError("Standalone finding needs nonempty limitations")
    if not isinstance(refs, list) or not refs or any(not isinstance(x, dict) for x in refs):
        raise MemoryError("Standalone finding needs source_refs")
    if not isinstance(related, list) or any(not isinstance(x, str) or not x for x in related):
        raise MemoryError("Standalone finding needs a related_ids list")


def git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    try:
        p = subprocess.run(["git", *args], cwd=root, input=data, capture_output=True,
                           timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise MemoryError(f"Git evidence unavailable: {type(exc).__name__}") from exc
    if p.returncode:
        raise MemoryError(f"Git evidence unavailable ({args[0]}, exit {p.returncode})")
    return p.stdout


class Snapshot:
    def __init__(self, root: Path, ref: str):
        self.root = root
        self.commit = git(root, "rev-parse", "--verify", "--end-of-options",
                          ref + "^{commit}").decode().strip()
        self.tree: dict[str, str] = {}
        for entry in git(root, "ls-tree", "-rz", self.commit).split(b"\0"):
            if not entry:
                continue
            metadata, path = entry.split(b"\t", 1)
            mode, kind, oid = metadata.decode().split()
            if kind == "blob" and mode in {"100644", "100755"}:
                self.tree[path.decode("utf-8")] = oid
        self.cache: dict[str, bytes] = {}

    def preload(self, paths: list[str]) -> None:
        paths = list(dict.fromkeys(p for p in paths if p not in self.cache))
        missing = [p for p in paths if p not in self.tree]
        if missing:
            raise MemoryError(f"Source absent at {self.commit}: {missing[0]}")
        if not paths:
            return
        raw = git(self.root, "cat-file", "--batch",
                  data=("\n".join(self.tree[p] for p in paths) + "\n").encode())
        cursor = 0
        for path in paths:
            end = raw.index(b"\n", cursor)
            oid, kind, size = raw[cursor:end].decode().split()
            size = int(size)
            if oid != self.tree[path] or kind != "blob":
                raise MemoryError(f"Unexpected source object: {path}")
            cursor = end + 1
            self.cache[path] = raw[cursor:cursor + size]
            cursor += size + 1
        if cursor != len(raw):
            raise MemoryError("Unexpected trailing Git object data")

    def read(self, path: str) -> bytes:
        self.preload([path])
        return self.cache[path]

    def source(self, path: str, start: int = 1, end: int | None = None) -> dict:
        raw = self.read(path)
        return {"commit": self.commit, "path": path, "blob": self.tree[path],
                "sha256": hashlib.sha256(raw).hexdigest(),
                "line_start": start, "line_end": end or len(raw.splitlines())}


def decode(raw: bytes, path: str) -> str:
    try:
        return raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise MemoryError(f"Source is not UTF-8: {path}") from exc


def research_text(raw: bytes, path: str) -> tuple[str, str]:
    """Decode explicit Unicode BOMs, without guessing a legacy code page."""
    encoding = ("utf-32" if raw.startswith((b"\xff\xfe\0\0", b"\0\0\xfe\xff")) else
                "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    try:
        return raw.decode(encoding), encoding
    except UnicodeError as exc:
        raise MemoryError(f"Source is not valid {encoding.upper()}: {path}") from exc


def sections(text: str) -> list[dict]:
    """Keep original labels/text/line spans. Labels do not adjudicate a claim."""
    found: list[dict] = []
    fence: str | None = None
    for i, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        match = None if fence else re.match(r"^\s*-\s+\*\*([^*]+)\*\*:?\s*(.*)$", line)
        if match:
            found.append({"label": match[1].rstrip(":"), "text": match[2],
                          "line_start": i, "line_end": i})
        elif found:
            found[-1]["text"] += "\n" + line
            found[-1]["line_end"] = i
    for part in found:
        part["text"] = part["text"].strip()
    return found


def json_doc(raw: bytes, path: str, expected: type) -> object:
    try:
        doc = json.loads(decode(raw, path))
    except ValueError as exc:
        raise MemoryError(f"Invalid JSON source: {path}") from exc
    if not isinstance(doc, expected):
        raise MemoryError(f"Wrong JSON shape: {path}")
    return doc


def table_cells(line: str) -> list[str]:
    """Locate cell boundaries without splitting escaped or inline-code pipes.

    Text is never reconstructed from these cells: records keep the original row.
    """
    cells, start, tick, i = [], 1, 0, 1
    line = line.strip()
    while i < len(line):
        char = line[i]
        if char == "\\":
            i += 2
            continue
        if char == "`":
            end = i + 1
            while end < len(line) and line[end] == "`":
                end += 1
            width = end - i
            tick = width if tick == 0 else (0 if tick == width else tick)
            i = end
            continue
        if char == "|" and tick == 0:
            cells.append(line[start:i].strip())
            start = i + 1
        i += 1
    if line[start:].strip():
        cells.append(line[start:].strip())
    return cells


def history_cards(snap: Snapshot, family: str, path: str) -> list[dict]:
    """Derive row/section views while carrying all direct ancestral prose.

    Surrounding prose is deliberately conservative context, not an assertion that
    every sentence qualifies every row. Sibling tables remain separate evidence.
    """
    lines = decode(snap.read(path), path).splitlines()
    nodes = [{"key": "intro", "title": path, "level": 0,
              "heading": 1, "direct": [], "ancestors": []}]
    stack, fence = [0], None
    keys = {"intro"}
    for number, line in enumerate(lines, 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        fenced = fence is not None or marker is not None
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        heading = None if fenced else re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            level, title = len(heading[1]), heading[2]
            while len(stack) > 1 and nodes[stack[-1]]["level"] >= level:
                stack.pop()
            explicit = re.match(r"^(?:§\s*)?(\d+[a-z]?\d*)(?=[.\s:—–-]|$)", title, re.I)
            key = explicit[1].lower() if explicit else "s-" + hashlib.sha256(title.encode()).hexdigest()[:16]
            if key in keys:
                raise MemoryError(f"Ambiguous history section identity: {path} / {key}")
            keys.add(key)
            nodes.append({"key": key, "title": title, "level": level,
                          "heading": number, "direct": [], "ancestors": stack.copy()})
            stack.append(len(nodes) - 1)
        else:
            nodes[stack[-1]]["direct"].append((number, line, fenced))

    # Identify headers even when an explanatory paragraph interrupts a table.
    for node in nodes:
        prose, rows, header = [], [], None
        direct = node["direct"]
        i = 0
        while i < len(direct):
            number, line, fenced = direct[i]
            is_row = not fenced and line.strip().startswith("|")
            if is_row and i + 1 < len(direct):
                _, following, in_fence = direct[i + 1]
                cells = table_cells(following) if following.strip().startswith("|") else []
                if not in_fence and cells and all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    header = (number, line)
                    i += 2
                    continue
            if is_row:
                rows.append((number, line, header))
            else:
                prose.append((number, line))
            i += 1
        node["prose"], node["rows"] = prose, rows

    def spans(numbered: list[tuple[int, str]], label: str) -> list[dict]:
        chunks: list[dict] = []
        for number, line in numbered:
            if chunks and chunks[-1]["line_end"] + 1 == number:
                chunks[-1]["text"] += "\n" + line
                chunks[-1]["line_end"] = number
            else:
                chunks.append({"label": label, "text": line,
                               "line_start": number, "line_end": number})
        return [p for p in chunks if p["text"].strip()]

    cards = []
    for node in nodes:
        context = []
        for parent in [nodes[i] for i in node["ancestors"]] + [node]:
            if parent["key"] != "intro":
                context.extend(spans([(parent["heading"], lines[parent["heading"] - 1])],
                                     "Ancestral heading"))
            context.extend(spans(parent["prose"], "Surrounding source: " + parent["title"]))
        base = {"basis": "historical source assertion; context retained, no new ruling or reproduction",
                "context_scope": "All direct prose in this section and its ancestors; sibling rows are separate. Cross-source contradictions require review.",
                "section_identity": node["key"]}
        for number, line, header in node["rows"]:
            cells = table_cells(line)
            first = cells[0] if cells else line
            # Several legacy tables use a dash in column one and name the finding
            # in column two. Preserve that identity instead of merging placeholders.
            identity = cells[1] if first in {"", "-", "—", "–"} and len(cells) > 1 else first
            plain = first.strip(" *`~")
            explicit = re.match(r"^(GR-\d+|[A-Z]\d+)(?=$|[\s:.*`(—–-])", plain)
            if family == "lesson":
                explicit = re.fullmatch(r"(\d+)", plain)
            key = explicit[1] if explicit else "r-" + hashlib.sha256(identity.encode()).hexdigest()[:16]
            if family == "supersession":
                # Dates repeat, and corrected destinations may repeat an old path.
                # Preserve each complete historical assertion as a distinct row.
                identity = cells[1] if len(cells) > 1 else first
                key = "r-" + hashlib.sha256(line.encode()).hexdigest()[:16]
            parts = list(context)
            if header:
                parts.append({"label": "Original table header", "text": header[1],
                              "line_start": header[0], "line_end": header[0]})
            parts.append({"label": "Original table row", "text": line,
                          "line_start": number, "line_end": number})
            cards.append({**base, "id": f"{family}:{node['key']}:{key}",
                          "kind": family + "_row", "title": identity + " — " + (cells[1] if explicit and len(cells) > 1 else node["title"]),
                          "source": snap.source(path, number, number), "sections": parts,
                          "original_label": first})
        if node["key"] != "intro" or any(line.strip() for _, line in node["prose"]):
            cards.append({**base, "id": f"{family}:{node['key']}",
                          "kind": family + "_section", "title": node["title"],
                          "source": snap.source(path, node["heading"], max([node["heading"]] + [n for n, _ in node["prose"]])),
                          "sections": context,
                          "row_ids": [c["id"] for c in cards if c.get("section_identity") == node["key"] and c["kind"].endswith("_row")]})
    return cards


def anchor_check(anchor: dict, snap: Snapshot, snapshots: dict[str, Snapshot]) -> None:
    ref = anchor.get("git_commit", snap.commit)
    if ref != snap.commit and not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise MemoryError("Review anchors must pin a full Git commit")
    if ref not in snapshots:
        snapshots[ref] = Snapshot(snap.root, ref)
    source = snapshots[ref]
    path = anchor.get("path", "")
    raw = source.read(path)
    if hashlib.sha256(raw).hexdigest() != anchor.get("sha256"):
        raise MemoryError(f"Review anchor bytes changed: {path}")
    loc = anchor.get("locator", {})
    if "json_pointer" in loc:
        ptr = loc["json_pointer"]
        if not isinstance(ptr, str) or (ptr and not ptr.startswith("/")):
            raise MemoryError(f"Invalid JSON pointer: {path}")
        try:
            # Evidence links and interactive field reads must interpret the
            # same bytes identically, including duplicate keys and array indices.
            select_source_json({"_document_text": decode(raw, path), "source": {}}, ptr)
        except MemoryError as exc:
            raise MemoryError(f"Review locator does not resolve: {path}") from exc
    else:
        start, end = loc.get("line_start"), loc.get("line_end")
        line_count = (len(research_text(raw, path)[0].splitlines())
                      if path.startswith(RESEARCH) and path.lower().endswith(".md") else len(raw.splitlines()))
        if not (type(start) is int and type(end) is int and
                1 <= start <= end <= line_count):
            raise MemoryError(f"Review line span does not resolve: {path}")


def attach_relationships(cards: dict[str, dict], snap: Snapshot,
                         snapshots: dict[str, Snapshot]) -> dict:
    """Attach reviewed links before original assertions, never overwrite them."""
    if LINKS not in snap.tree:
        return {"status": "NO_REVIEWED_LINKS_AT_SNAPSHOT", "count": 0, "stale": 0}
    doc = json_doc(snap.read(LINKS), LINKS, dict)
    if not isinstance(doc.get("relationships"), list):
        raise MemoryError("Relationship register unavailable")
    seen, stale = set(), 0
    for i, row in enumerate(doc["relationships"]):
        required = {"id", "source_id", "target_id", "relation", "statement", "basis", "source_refs"}
        if not isinstance(row, dict) or not required <= row.keys():
            raise MemoryError("Incomplete reviewed relationship")
        if row["id"] in seen or not isinstance(row["statement"], str) or not row["statement"].strip():
            raise MemoryError("Duplicate or empty reviewed relationship")
        seen.add(row["id"])
        if row["relation"] not in {"supports", "contradicts", "qualifies", "supersedes", "uses", "generated_by"} or row["basis"] not in {"source_assertion", "interpretation"}:
            raise MemoryError("Unknown relationship semantics")
        endpoints = [row["source_id"], row["target_id"]]
        if endpoints[0] == endpoints[1]:
            raise MemoryError(f"Self-referential reviewed relationship: {row['id']}")
        if any(rid not in cards for rid in endpoints):
            raise MemoryError(f"Relationship endpoint absent: {row['id']}")
        if not row["source_refs"]:
            raise MemoryError(f"Relationship needs evidence: {row['id']}")
        for anchor in row["source_refs"]:
            anchor_check(anchor, snap, snapshots)
        support = expanded_support(row["source_refs"], list(cards.values()))
        current = not changed_sources(snap, support)
        for rid in endpoints:
            source = cards[rid]["source"]
            anchors = [a for a in row["source_refs"] if a["path"] == source["path"]]
            if not anchors:
                raise MemoryError(f"Relationship does not bind endpoint source: {rid}")
            matching = [a for a in anchors if a["sha256"] == source["sha256"]]
            if matching and not any(anchor_covers_record(a, source) for a in matching):
                raise MemoryError(f"Relationship locator does not cover endpoint record: {rid}")
            # Old positions need not cover a moved row in a changed source. Retain
            # that history as STALE; never claim it binds the current record.
            current &= bool(matching)
        stale += not current
        for rid, other in zip(endpoints, reversed(endpoints)):
            cards[rid].setdefault("linked_context", []).append({
                **row, "other_id": other,
                "currentness": "SOURCE_VERSIONS_MATCH" if current else "STALE_LINK_FOR_CHANGED_SOURCE; retained as history, review required",
                "link_source": {**snap.source(LINKS), "json_pointer": f"/relationships/{i}"}})
    return {"status": "REVIEWED_LINKS_PRESENT", "count": len(seen), "stale": stale}


def anchor_covers_record(anchor: dict, source: dict) -> bool:
    """Same-file hashes alone cannot bind adjacent rows or JSON siblings."""
    loc = anchor["locator"]
    if "json_pointer" in loc:
        # anchor_check already validated the same source bytes as JSON. Its
        # root includes the entire document, including line-addressed findings.
        if loc["json_pointer"] == "":
            return True
        if "json_pointer" not in source:
            return False
        parent, child = loc["json_pointer"], source["json_pointer"]
        return not parent or child == parent or child.startswith(parent + "/")
    return (loc["line_start"] <= source["line_start"] and
            loc["line_end"] >= source["line_end"])


def changed_sources(snap: Snapshot, anchors: list[dict]) -> list[dict]:
    """Compare all supporting versions, without certifying unchanged conclusions."""
    changed = {}
    for anchor in anchors:
        path = anchor["path"]
        current = hashlib.sha256(snap.read(path)).hexdigest() if path in snap.tree else None
        if current != anchor["sha256"]:
            key = (path, anchor.get("git_commit", snap.commit), anchor["sha256"])
            changed[key] = {"path": path, "pinned_commit": key[1],
                            "pinned_sha256": key[2], "current_sha256": current,
                            "current_blob": snap.tree.get(path),
                            "state": "SOURCE_CHANGED" if current else "SOURCE_ABSENT_AT_SNAPSHOT"}
    return [changed[k] for k in sorted(changed)]


def expanded_support(anchors: list[dict], cards: list[dict]) -> list[dict]:
    """Follow explicitly bound annotation dependencies; cycles cannot erase drift.

    Whole-file references conservatively inherit annotations in that file. This
    is dependency review, not a claim that one sentence proves another.
    """
    annotations = []
    for card in cards:
        refs = card.get("knowledge", {}).get("source_refs", [])
        if refs:
            annotations.append((card["source"], refs))
        if "review_note" in card:
            refs = card["review_note"]["source_refs"]
            annotations.extend([(card["source"], refs), (card["review_source"], refs)])
    pending, seen, result = list(anchors), set(), []
    while pending:
        anchor = pending.pop()
        identity = json.dumps(anchor, sort_keys=True)
        if identity in seen:
            continue
        seen.add(identity)
        result.append(anchor)
        for source, refs in annotations:
            if (anchor["path"], anchor["sha256"]) != (source["path"], source["sha256"]):
                continue
            loc = anchor["locator"]
            if "json_pointer" in loc and "json_pointer" in source:
                a, b = loc["json_pointer"], source["json_pointer"]
                overlaps = not a or not b or a == b or a.startswith(b + "/") or b.startswith(a + "/")
            elif "line_start" in loc:
                overlaps = loc["line_start"] <= source["line_end"] and source["line_start"] <= loc["line_end"]
            else:
                overlaps = True  # A JSON member within a whole-file annotation.
            if overlaps:
                pending.extend(refs)
    return result


def maintenance_queue(cards: list[dict], snap: Snapshot) -> list[dict]:
    """A derived review queue; never a second store or automatic factual repair."""
    items = {}
    for card in cards:
        annotations = []
        if "review_note" in card:
            annotations.append(("note:" + card["id"], [card["id"]],
                                card["review_note"], card["review_source"]))
        if card.get("knowledge", {}).get("source_refs"):
            annotations.append(("knowledge:" + card["id"], [card["id"]],
                                card["knowledge"], card["source"]))
        for link in card.get("linked_context", []):
            annotations.append(("link:" + link["id"], [link["source_id"], link["target_id"]],
                                link, link["link_source"]))
        for aid, ids, annotation, source in annotations:
            drift = changed_sources(snap, expanded_support(annotation["source_refs"], cards))
            if drift:
                items[aid] = {"id": aid, "record_ids": ids, "annotation_source": source,
                              "changed_sources": drift,
                              "next_action": "Compare the pinned and current sources, review the conclusion and its limits, then bank a justified replacement or retain the stale annotation. No automatic re-certification."}
    return [items[k] for k in sorted(items)]


def load(snap: Snapshot) -> tuple[list[dict], dict]:
    paths = sorted(p for p in snap.tree if
                   (p.startswith(EXPERIMENTS) and p.endswith(".md") and
                    p.rsplit("/", 1)[-1] != "INDEX.md") or
                   (p.startswith(NOTES) and p.endswith(".json")) or
                   (p.startswith(AUDITS) and p.endswith("/knowledge.jsonl")))
    research_paths = sorted(p for p in snap.tree if p.startswith(RESEARCH))
    markdown = [p for p in research_paths if p.lower().endswith(".md")]
    inbox_paths = sorted(p for p in snap.tree if p.startswith(INBOX))
    inbox_text = [p for p in inbox_paths if Path(p).suffix.lower() in {".md", ".txt"}]
    snap.preload(paths + markdown + inbox_text + [COMPACT, RETRACTIONS] +
                 [p for p in [*HISTORY.values(), LINKS, *(v[0] for v in REGISTERS.values())] if p in snap.tree])
    cards: dict[str, dict] = {}
    notes: list[tuple[str, dict]] = []
    snapshots = {snap.commit: snap}

    # Source checks still happen below. Group the immutable reads by commit so
    # one query does not launch a new Git process for every supporting file.
    anchors = []
    for path in paths:
        if path.startswith(NOTES):
            rows = [json_doc(snap.read(path), path, dict)]
        elif path.startswith(AUDITS):
            rows = [json_doc(line.encode(), path, dict)
                    for line in decode(snap.read(path), path).splitlines() if line.strip()]
        else:
            continue
        anchors.extend(a for row in rows for a in row.get("source_refs", []) if isinstance(a, dict))
    if LINKS in snap.tree:
        doc = json_doc(snap.read(LINKS), LINKS, dict)
        anchors.extend(a for row in doc.get("relationships", []) if isinstance(row, dict)
                       for a in row.get("source_refs", []) if isinstance(a, dict))
    grouped = {}
    for anchor in anchors:
        ref, path = anchor.get("git_commit", snap.commit), anchor.get("path")
        if isinstance(ref, str) and re.fullmatch(r"[0-9a-f]{40}", ref) and isinstance(path, str):
            grouped.setdefault(ref, []).append(path)
    for ref, pending in grouped.items():
        if ref not in snapshots:
            snapshots[ref] = Snapshot(snap.root, ref)
        source = snapshots[ref]
        source.preload([p for p in pending if p in source.tree])
    snap.preload([a["path"] for a in anchors if isinstance(a.get("path"), str) and a["path"] in snap.tree])

    def add(card: dict) -> None:
        if card["id"] in cards:
            raise MemoryError(f"Duplicate research identity: {card['id']}")
        cards[card["id"]] = card

    unreadable = 0
    unreadable_inbox = 0
    for path in markdown + inbox_text:
        is_inbox = path.startswith(INBOX)
        identity = ("inbox:2026-09/" + path[len(INBOX):] if is_inbox
                    else "research:" + path[len(RESEARCH):])
        card = {"id": identity, "kind": "research_document",
                "title": path.rsplit("/", 1)[-1] if is_inbox else path[len(RESEARCH):], "source": snap.source(path),
                "basis": "Historical source document, not semantically certified; proposals and instructions are not current authority.",
                "document_role": "raw archived source" if "/sources/" in path else "research document"}
        try:
            text, encoding = research_text(snap.read(path), path)
            heading = next((line.lstrip("# ") for line in text.splitlines() if line.startswith("# ")), None)
            card.update(title=heading or card["title"], _document_text=text, source_encoding=encoding)
            card["source"]["line_end"] = len(text.splitlines())
        except MemoryError as exc:
            card["read_error"] = str(exc)
            if is_inbox:
                unreadable_inbox += 1
            else:
                unreadable += 1
        add(card)
    inbox_other = {}
    for path in inbox_paths:
        if path not in inbox_text:
            suffix = Path(path).suffix.lower() or "[no extension]"
            inbox_other[suffix] = inbox_other.get(suffix, 0) + 1
    inbox_coverage = {"root": INBOX, "tracked_files": len(inbox_paths),
                      "text_documents": len(inbox_text), "unreadable_text": unreadable_inbox,
                      "unconsumed_file_types": dict(sorted(inbox_other.items())),
                      "scope": "Banked Markdown and plain-text memos, including historical instructions, are searchable source assertions, not current authority. Other formats are counted but not consumed. No semantic certification."}
    other_types = {}
    for path in research_paths:
        if path not in markdown:
            suffix = Path(path).suffix.lower() or "[no extension]"
            other_types[suffix] = other_types.get(suffix, 0) + 1
    research_coverage = {"root": RESEARCH, "tracked_files": len(research_paths),
                         "markdown_documents": len(markdown), "unreadable_markdown": unreadable,
                         "other_file_types": dict(sorted(other_types.items())),
                         "scope": "All committed Markdown under this root, including raw source archives, is indexed as historical text. Other file types are counted, not consumed by this adapter. Other roots, branches, hosts and semantic completeness remain outside this census."}

    # Expand measured coverage gaps through the existing catalog's paths and warnings.
    # These are source documents, not newly adjudicated scientific records.
    catalog_coverage = {cid: {"status": "CATALOG_ENTRY_ABSENT"}
                        for cid in sorted(CATALOG_DOCUMENT_IDS)}
    if CATALOG in snap.tree:
        catalog = json_doc(snap.read(CATALOG), CATALOG, dict)
        if not isinstance(catalog.get("inventories"), list):
            raise MemoryError("Master catalog rows unavailable")
        for row in catalog["inventories"]:
            if not isinstance(row, dict) or row.get("id") not in CATALOG_DOCUMENT_IDS:
                continue
            cid, path = row["id"], row.get("path")
            if catalog_coverage[cid]["status"] != "CATALOG_ENTRY_ABSENT":
                raise MemoryError("Duplicate catalog document identity: " + cid)
            if not isinstance(path, str) or path not in snap.tree:
                catalog_coverage[cid] = {"path": path, "status": "SOURCE_ABSENT_AT_SNAPSHOT"}
                continue
            card = {"id": "catalog:" + cid, "kind": "research_document", "title": cid,
                    "source": snap.source(path),
                    "basis": "Historical catalog source, not semantically certified; old rulings and proposed work are not current permission.",
                    "catalog_context": {"source": snap.source(CATALOG), "row": row,
                                        "warnings": {k: v for k, v in catalog.items() if k != "inventories"}}}
            try:
                text, encoding = research_text(snap.read(path), path)
                heading = next((line.lstrip("# ") for line in text.splitlines() if line.startswith("# ")), None)
                card.update(title=heading or cid, _document_text=text, source_encoding=encoding)
                card["source"]["line_end"] = len(text.splitlines())
                status = "FULL_TEXT_INDEXED_NOT_SEMANTICALLY_CERTIFIED"
            except MemoryError as exc:
                card["read_error"] = str(exc)
                status = "SOURCE_UNREADABLE"
            add(card)
            catalog_coverage[cid] = {"source": card["source"], "status": status, "id": card["id"]}

    history_coverage = {}
    for family, path in HISTORY.items():
        if path not in snap.tree:
            history_coverage[family] = {"path": path, "status": "SOURCE_ABSENT_AT_SNAPSHOT", "records": 0}
            continue
        extracted = history_cards(snap, family, path)
        for card in extracted:
            add(card)
        history_coverage[family] = {"source": snap.source(path), "status": "EXTRACTED_NOT_SEMANTICALLY_CERTIFIED", "records": len(extracted)}

    register_coverage = {}
    for family, (path, key) in REGISTERS.items():
        if path not in snap.tree:
            register_coverage[family] = {"path": path, "status": "SOURCE_ABSENT_AT_SNAPSHOT", "records": 0}
            continue
        doc = json_doc(snap.read(path), path, dict)
        if not isinstance(doc.get(key), list):
            raise MemoryError(f"Register rows unavailable: {path}")
        for i, row in enumerate(doc[key]):
            if not isinstance(row, dict) or not row.get("id"):
                raise MemoryError(f"Invalid register row: {path}:{i}")
            add({"id": family + ":" + row["id"], "kind": family + "_register_assertion",
                 "title": row.get("name", row.get("term", row.get("path", row.get("path_hint", row["id"])))),
                 "basis": "historical source assertion; registered availability is not current usability",
                 "source": {**snap.source(path), "json_pointer": f"/{key}/{i}"},
                 "knowledge": row, "register_context": {k: v for k, v in doc.items() if k != key}})
        register_coverage[family] = {"source": snap.source(path), "status": "EXTRACTED_NOT_SEMANTICALLY_CERTIFIED", "records": len(doc[key])}

    for path in paths:
        raw = snap.read(path)
        text = decode(raw, path)
        if path.startswith(EXPERIMENTS):
            title = next((s.lstrip("# ") for s in text.splitlines() if s.startswith("#")), path)
            eid = re.match(r"(E\d+)(?:-|\.)", path.rsplit("/", 1)[-1])
            rid = eid[1] if eid else "report:" + path.rsplit("/", 1)[-1][:-3]
            parts = sections(text)
            preamble_end = parts[0]["line_start"] - 1 if parts else len(text.splitlines())
            add({"id": rid, "kind": "experiment_report", "title": title,
                 "basis": "historical source assertion; not re-executed or re-certified",
                 "source": snap.source(path), "sections": parts,
                 "preamble": {"text": "\n".join(text.splitlines()[:preamble_end]),
                              "line_start": 1, "line_end": preamble_end},
                 "references": sorted(set(re.findall(r"\bE\d{3}\b", text)) - {rid})})
        elif path.startswith(NOTES):
            note = json_doc(raw, path, dict)
            if note.get("schema") == FINDING_SCHEMA:
                validate_finding(note)
                for anchor in note["source_refs"]:
                    anchor_check(anchor, snap, snapshots)
                add({"id": note["id"], "kind": "finding", "title": note["question"],
                     "basis": note["evidence_status"], "source": snap.source(path),
                     "knowledge": note, "references": note["related_ids"]})
            else:
                notes.append((path, note))
        else:
            for i, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                row = json_doc(line.encode(), f"{path}:{i}", dict)
                if not row.get("source_refs") or not row.get("id"):
                    raise MemoryError(f"Missing knowledge evidence: {path}:{i}")
                for anchor in row["source_refs"]:
                    anchor_check(anchor, snap, snapshots)
                add({"id": row["id"], "kind": row.get("kind", "knowledge"),
                     "title": row.get("title", row["id"]),
                     "basis": row.get("evidence_status", "unknown"),
                     "source": snap.source(path, i, i), "knowledge": row})

    compact = json_doc(snap.read(COMPACT), COMPACT, dict)
    if not isinstance(compact.get("rows"), list):
        raise MemoryError("Compact register rows unavailable")
    for i, row in enumerate(compact["rows"]):
        if not isinstance(row, dict) or not row.get("id"):
            raise MemoryError(f"Invalid compact register row {i}")
        add({"id": "tried:" + row["id"], "kind": "compact_register_assertion",
             "title": row.get("tried", row["id"]),
             "basis": "source assertion; class is inherited, not a new ruling",
             "source": {**snap.source(COMPACT), "json_pointer": f"/rows/{i}"},
             "knowledge": row, "open_conflicts": compact.get("open_conflicts", [])})

    required = {"id", "question", "why", "methodology", "result", "learn",
                "limitations", "reopen_when", "source_refs", "related_ids"}
    for path, note in notes:
        if not required <= note.keys() or note["id"] not in cards:
            raise MemoryError(f"Review note is incomplete or its target is absent: {path}")
        if not note["source_refs"]:
            raise MemoryError(f"Review note needs evidence: {path}")
        for anchor in note["source_refs"]:
            anchor_check(anchor, snap, snapshots)
        target = cards[note["id"]]["source"]
        target_anchors = [a for a in note["source_refs"] if a["path"] == target["path"]]
        if not target_anchors:
            raise MemoryError(f"Review note does not bind its target report: {path}")
        for rid in note["related_ids"]:
            if rid not in cards:
                raise MemoryError(f"Review relationship unresolved: {rid}")
        if "review_note" in cards[note["id"]]:
            raise MemoryError(f"Duplicate review note: {note['id']}")
        cards[note["id"]]["review_note"] = note
        cards[note["id"]]["review_source"] = snap.source(path)
    for card in cards.values():
        if "review_note" in card:
            card["review_note_currentness"] = (
                "SOURCE_VERSION_MATCHES" if not changed_sources(snap, expanded_support(card["review_note"]["source_refs"], list(cards.values())))
                else "STALE_NOTE_FOR_CHANGED_SOURCE; retained as history, review required")
        if card.get("knowledge", {}).get("source_refs"):
            card["knowledge_currentness"] = (
                "SOURCE_VERSIONS_MATCH" if not changed_sources(snap, expanded_support(card["knowledge"]["source_refs"], list(cards.values())))
                else "STALE_KNOWLEDGE_FOR_CHANGED_SOURCE; retained as history, review required")
        refs = card.get("references", [])
        card["unresolved_references"] = [rid for rid in refs if rid not in cards]
    relationship_coverage = attach_relationships(cards, snap, snapshots)
    meta = {"schema": SCHEMA, "snapshot": snap.commit,
            "records": len(cards), "review_notes": len(notes),
            "by_kind": {k: sum(c["kind"] == k for c in cards.values())
                        for k in sorted({c["kind"] for c in cards.values()})},
            "reports_without_structured_sections": sum(c["kind"] == "experiment_report" and not c["sections"] for c in cards.values()),
            "stale_review_notes": sum(c.get("review_note_currentness", "").startswith("STALE") for c in cards.values()),
            "stale_knowledge_records": sum(c.get("knowledge_currentness", "").startswith("STALE") for c in cards.values()),
            "retraction_source": snap.source(RETRACTIONS),
            "history_sources": history_coverage,
            "register_sources": register_coverage,
            "research_documents": research_coverage,
            "inbox_documents": inbox_coverage,
            "catalog_documents": catalog_coverage,
            "relationships": relationship_coverage,
            "coverage_limit": "Selected loss-mode, asset, improvement, replay-store, strategy-atlas, knowledge, measurement-index and numbers-inventory catalog documents; experiment and workflow/research Markdown, banked September 2026 inbox Markdown/plain text, compact rows, historical attempts/dead ends/retractions/equations/lessons/measurement summaries/supersessions, graveyard/tool/hypothesis/metric/domain-term/trace-source/dated-consumer-status registers, reviewed links, notes and audit knowledge. Other research formats/roots, raw runs, tools, branches, hosts and transcripts are not exhaustively covered. Extraction is not complete semantic reconciliation.",
            "verification_limit": "Source versions and anchors checked; scientific truth, current tool usability and raw-run reproduction not certified."}
    return list(cards.values()), meta


WORDS = re.compile(r"[\w]+", re.UNICODE)
STOP = set("what why how did does have has the a an we our was were is it and or of to in for this".split())


def rank(cards: list[dict], query: str) -> list[dict]:
    terms = {t.lower() for t in WORDS.findall(query)} - STOP
    # A standalone artifact basename is an identity lookup, not a bag of suffix words.
    filename = query.strip().casefold()
    literal_file = bool(re.fullmatch(
        r"[^\s/\\]+\.(?:md|txt|json|jsonl|py|csv|tsv|yaml|yml|toml|parquet|npz|pt|pth)", filename))
    file_pattern = re.compile(r"(?<![\w.-])" + re.escape(filename) + r"(?![\w-]|\.[\w.-])") if literal_file else None
    def string_values(value):
        if isinstance(value, str):
            yield value.casefold()
        elif isinstance(value, dict):
            for item in value.values():
                yield from string_values(item)
        elif isinstance(value, list):
            for item in value:
                yield from string_values(item)

    scored = []
    for card in cards:
        if query.casefold() == card["id"].casefold():
            scored.append((10000, card))
            continue
        if query.strip() and query.casefold() == card.get("original_label", "").strip(" *`~").casefold():
            scored.append((9000, card))
            continue
        text = json.dumps({k: v for k, v in card.items() if k not in {"source", "review_source"}}).lower()
        title = (card["id"] + " " + card["title"]).lower()
        if file_pattern is not None:
            source_path = card.get("source", {}).get("path", "").replace("\\", "/").casefold()
            if file_pattern.search(title):
                scored.append((100, card))
            elif file_pattern.search(source_path):
                scored.append((80, card))
            elif any(file_pattern.search(value) for value in string_values(card)):
                scored.append((60, card))
            continue
        note = json.dumps(card.get("review_note", {})).lower()
        def contains(term: str, content: str) -> bool:
            # Numeric fragments in hashes or larger counts are not the requested number.
            return (bool(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", content))
                    if term.isdecimal() else term in content)

        score = sum(5 if contains(t, title) else 3 if contains(t, note)
                    else 1 if contains(t, text) else 0 for t in terms)
        phrase = query.strip().casefold()
        numeric_expression = any(t.isdecimal() for t in terms)

        def phrase_in(content: str) -> bool:
            return (bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", content))
                    if numeric_expression else phrase in content)

        if len(terms) >= 2 and phrase_in(title):
            score += 40
        elif len(terms) >= 2 and phrase_in(text):
            # An exact expression in evidence outranks scattered title terms.
            score += 20
        if score:
            scored.append((score, card))
    return [c for _, c in sorted(scored, key=lambda p: (-p[0], p[1]["id"]))]


def brief(card: dict) -> dict:
    return {"id": card["id"], "title": card["title"], "basis": card["basis"],
            "source": card["source"], "reviewed_context": "review_note" in card,
            "review_note_currentness": card.get("review_note_currentness", "NOT_REVIEWED"),
            "knowledge_currentness": card.get("knowledge_currentness", "NO_BOUND_KNOWLEDGE_ANNOTATION"),
            "linked_context": [{k: link[k] for k in ("other_id", "relation", "statement", "basis", "currentness")}
                               for link in card.get("linked_context", [])],
            "fields_available": ["source document pages"] if card["kind"] == "research_document" else list(card.get("review_note", {}).keys()) or
                                [p["label"] for p in card.get("sections", [])],
            "next": "show " + card["id"]}


def document_page(card: dict, offset: int, count: int) -> dict:
    """Explicit, contiguous source pages; never call a partial page a full result."""
    if "read_error" in card:
        raise MemoryError(card["read_error"])
    lines = card["_document_text"].splitlines()
    if offset and offset >= len(lines):
        raise MemoryError("Document offset is outside this source snapshot")
    end = min(offset + count, len(lines))
    out = {k: v for k, v in card.items() if k != "_document_text"}
    out["sections"] = [{"label": "source document page", "text": "\n".join(lines[offset:end]),
                        "line_start": offset + 1 if lines else 0, "line_end": end}]
    out["document_page"] = {"line_start": offset + 1 if lines else 0, "line_end": end,
                            "total_lines": len(lines), "next_offset": end if end < len(lines) else None,
                            "complete_document": offset == 0 and end == len(lines)}
    out["context_scope"] = ("Complete source document; its historical assertions still require review."
                            if out["document_page"]["complete_document"] else
                            "PARTIAL source page. Other pages can contain corrections, limitations or contradictory results. Read those before citing a conclusion; no completeness or scientific verdict is implied.")
    return out


def source_document(snap: Snapshot, path: str, cards: list[dict]) -> dict:
    """Open an exact committed text source without executing it or indexing it as a finding."""
    if path not in snap.tree:
        raise MemoryError("Source path absent from this committed snapshot")
    size = int(git(snap.root, "cat-file", "-s", snap.tree[path]))
    if size > 8 * 1024 * 1024:
        raise MemoryError("Source exceeds 8 MiB text-reader limit; use its dataset/asset consumer")
    text, encoding = research_text(snap.read(path), path)
    if "\0" in text:
        raise MemoryError("Source contains binary NUL characters; not a text document")
    related, links = [], []
    for card in cards:
        refs = (card.get("knowledge", {}).get("source_refs", []) +
                card.get("review_note", {}).get("source_refs", []))
        if card["source"]["path"] == path or any(ref["path"] == path for ref in refs):
            related.append(card["id"])
            for link in card.get("linked_context", []):
                if link not in links:
                    links.append(link)
    source = snap.source(path)
    source.update(line_start=1 if text.splitlines() else 0, line_end=len(text.splitlines()))
    return {"id": "source:" + path, "kind": "source_document", "title": path,
            "basis": "Original source text, not semantically certified or executed. Read related records and corrections before interpreting it.",
            "source": source, "source_encoding": encoding, "_document_text": text,
            "related_record_ids": sorted(related), "linked_context": links}


def select_source_json(card: dict, pointer: str) -> dict:
    """Select a complete JSON value while retaining document identity and qualifications."""
    if pointer and (not pointer.startswith("/") or re.search(r"~(?![01])", pointer)):
        raise MemoryError("Invalid JSON pointer; use empty root or slash-separated escaped tokens")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate object key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("non-finite JSON number")

    def finite_float(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError("JSON number exceeds finite float range")
        return value

    try:
        value = json.loads(card["_document_text"], object_pairs_hook=unique_object,
                           parse_constant=invalid_constant, parse_float=finite_float)
    except (ValueError, RecursionError) as exc:
        raise MemoryError("JSON field reading requires valid, unambiguous JSON") from exc
    for token in pointer.split("/")[1:] if pointer else []:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and token in value:
            value = value[token]
        elif isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", token):
            index = int(token)
            if index >= len(value):
                raise MemoryError("JSON pointer does not resolve in this source")
            value = value[index]
        else:
            raise MemoryError("JSON pointer does not resolve in this source")
    out = {k: v for k, v in card.items() if k != "_document_text"}
    out.update(kind="source_json_value", selected_json=value,
               source={**card["source"], "json_pointer": pointer},
               context_scope="Selected decoded JSON value only; fields outside this pointer are unread. Original whitespace is not reproduced. Inspect surrounding decisions and linked corrections before interpreting this value.")
    return out


def outline_source_json(card: dict, pointer: str, offset: int, limit: int) -> dict:
    """List immediate child paths/types, never their values or implied evidence coverage."""
    out = select_source_json(card, pointer)
    value = out.pop("selected_json")
    def kind(item):
        if item is None: return "null"
        if isinstance(item, bool): return "boolean"
        if isinstance(item, dict): return "object"
        if isinstance(item, list): return "array"
        if isinstance(item, str): return "string"
        return "number"
    count = len(value) if isinstance(value, (dict, list)) else 0
    children = []
    if isinstance(value, dict):
        entries = ((k, value[k]) for k in list(value)[offset:offset + limit])
    elif isinstance(value, list):
        entries = ((str(i), value[i]) for i in range(offset, min(count, offset + limit)))
    else:
        entries = iter(())
    for key, child in entries:
        escaped = key.replace("~", "~0").replace("/", "~1")
        children.append({"pointer": pointer + "/" + escaped, "type": kind(child),
                         "children": len(child) if isinstance(child, (dict, list)) else None})
    out.update(kind="source_json_outline", json_outline={"type": kind(value),
               "total_children": count, "offset": offset, "children": children,
               "next_offset": offset + limit if offset + limit < count else None},
               context_scope="JSON structure only; values remain unread. Listed child paths are navigation, not evidence that their contents or unlisted siblings were consumed. Use --pointer without --outline to read a value.")
    return out


def catalog_sources(cards: list[dict], snap: Snapshot) -> list[dict]:
    """Reconcile the existing master catalog with this reader; never infer completeness."""
    doc = json_doc(snap.read(CATALOG), CATALOG, dict)
    if not isinstance(doc.get("inventories"), list):
        raise MemoryError("Master catalog rows unavailable")
    direct: dict[str, list[str]] = {}
    support: dict[str, set[str]] = {}
    for card in cards:
        direct.setdefault(card["source"]["path"], []).append(card["id"])
        for field in ("review_note", "knowledge"):
            for anchor in card.get(field, {}).get("source_refs", []):
                if isinstance(anchor, dict) and isinstance(anchor.get("path"), str):
                    support.setdefault(anchor["path"], set()).add(card["id"])
    rows, seen = [], set()
    for i, row in enumerate(doc["inventories"]):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k]
                                            for k in ("id", "path", "topic")):
            raise MemoryError(f"Invalid master catalog row: {i}")
        if row["id"] in seen:
            raise MemoryError("Duplicate master catalog identity")
        seen.add(row["id"])
        path = row["path"]
        present = path in snap.tree
        ids = sorted(direct.get(path, []))
        bound = sorted(support.get(path, []))
        state = ("SOURCE_ABSENT_AT_SNAPSHOT" if not present else
                 "DIRECT_RECORDS_PARTIAL" if ids else
                 "BOUND_REFERENCES_ONLY" if bound else "NOT_IN_READER")
        rows.append({"id": row["id"], "path": path, "topic": row["topic"],
                     "disposition": state, "direct_records": len(ids),
                     "bound_reference_records": len(bound),
                     "example_record_ids": ids[:2],
                     "source": snap.source(path) if present else None,
                     "catalog_pointer": f"/inventories/{i}",
                     "catalog_context": {k: v for k, v in row.items() if k not in {"id", "path", "topic"}}})
    return sorted(rows, key=lambda r: r["id"])


def source_line(source: dict) -> str:
    locator = (source["json_pointer"] or 'JSON root ""') if "json_pointer" in source else f"L{source['line_start']}-L{source['line_end']}"
    return (f"{source['path']}#{locator} @ {source['commit']} "
            f"blob={source['blob']} sha256={source['sha256']}")


def render_text(output: dict) -> str:
    """Compact reading view; retain original text, interpretation and evidence scope."""
    meta = output["meta"]
    lines = [f"Research memory @ {meta['snapshot']}",
             f"Coverage: {meta['records']} records; {meta['review_notes']} explanatory notes; "
             f"{meta['stale_review_notes']} stale notes.",
             "Scope: " + meta["coverage_limit"],
             "Evidence: " + meta["verification_limit"],
             "Retractions: " + source_line(meta["retraction_source"])]
    if "matches" in output:
        lines.append(f"Query: {output['query']}; {output['total_matches']} matches; showing {len(output['matches'])}")
        for hit in output["matches"]:
            lines.extend(["", f"{hit['id']}: {hit['title']}", hit["basis"],
                          "Source: " + source_line(hit["source"]),
                          "Context note: " + hit["review_note_currentness"],
                          "Read: " + hit["next"]])
            if hit["knowledge_currentness"].startswith("STALE"):
                lines.append("Knowledge: " + hit["knowledge_currentness"])
            # Repeat an identical qualification once, retaining every navigation target.
            # Different evidence bases or stale states must never collapse together.
            context_groups: dict[tuple[str, str, str], list[str]] = {}
            for link in hit["linked_context"]:
                key = (link["basis"], link["currentness"], link["statement"])
                context_groups.setdefault(key, []).append(link["other_id"])
            for (basis, currentness, statement), targets in context_groups.items():
                reads = "; ".join("show " + target for target in targets)
                lines.append(f"Linked context ({basis}; {currentness}): {statement} Read: {reads}")
    elif "record" in output:
        card = output["record"]
        lines.extend(["", f"{card['id']}: {card['title']}", card["basis"],
                      "Source: " + source_line(card["source"])])
        # A source can inherit the same qualification through several related records.
        # State the identical qualification once, but retain every edge and source.
        # Different evidence bases/currentness states remain separate groups.
        record_context: dict[tuple[str, str, str], list[dict]] = {}
        for link in card.get("linked_context", []):
            key = (link["basis"], link["currentness"], link["statement"])
            record_context.setdefault(key, []).append(link)
        for (basis, currentness, statement), links in record_context.items():
            lines.extend(["", f"Linked context ({basis}; {currentness}):", statement])
            for link in links:
                lines.extend([f"{link['source_id']} {link['relation']} {link['target_id']}",
                              "Link source: " + source_line(link["link_source"]),
                              "Read: show " + link["other_id"]])
        if "review_note" in card:
            lines.extend(["", "Explanatory note: " + card["review_note_currentness"],
                          "Note source: " + source_line(card["review_source"])])
            # Preserve unknown future fields as well as the current note schema.
            for key, value in card["review_note"].items():
                lines.append(f"{key}: " + (value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)))
        if "catalog_context" in card:
            lines.extend(["Catalog context (historical warnings, not a current ruling):",
                          json.dumps(card["catalog_context"], ensure_ascii=False)])
        if card.get("preamble", {}).get("text"):
            lines.extend(["", "Original introduction:", card["preamble"]["text"]])
        if card.get("context_scope"):
            lines.append("Context: " + card["context_scope"])
        if "json_outline" in card:
            lines.extend(["", "JSON structure (values unread):", json.dumps(card["json_outline"], ensure_ascii=False, indent=2)])
        if "selected_json_values" in card:
            lines.extend(["", "Selected JSON values (explicit pointers):",
                          json.dumps(card["selected_json_values"], ensure_ascii=False, indent=2)])
        if "selected_json" in card:
            lines.extend(["", "Selected JSON value:", json.dumps(card["selected_json"], ensure_ascii=False, indent=2)])
        for part in card.get("sections", []):
            lines.extend(["", f"Original {part['label']} [L{part['line_start']}-L{part['line_end']}]:", part["text"]])
        if "knowledge" in card:
            if "knowledge_currentness" in card:
                lines.append("Knowledge support: " + card["knowledge_currentness"])
            lines.extend(["", "Original structured record:", json.dumps(card["knowledge"], ensure_ascii=False)])
        if "register_context" in card:
            lines.extend(["", "Original register context (historical, not current instructions):",
                          json.dumps(card["register_context"], ensure_ascii=False)])
        if card.get("open_conflicts"):
            lines.extend(["", "Unresolved register conflicts:", *card["open_conflicts"]])
        if card.get("references"):
            lines.append("Referenced experiment IDs (mentions, not support): " + ", ".join(card["references"]))
        if card.get("unresolved_references"):
            lines.append("Unresolved in this inventory: " + ", ".join(card["unresolved_references"]))
        if card.get("row_ids"):
            lines.append("Rows in this section: " + ", ".join(card["row_ids"]))
        if "related_record_ids" in card:
            lines.append("Related inventory records (open with show; source references are not proof): " +
                         ", ".join(card["related_record_ids"]))
        if "document_page" in card:
            page = card["document_page"]
            lines.append(f"Document page: L{page['line_start']}-L{page['line_end']} of {page['total_lines']} lines.")
            if page["next_offset"] is not None:
                action, query = (("source", card["source"]["path"]) if card["kind"] == "source_document"
                                 else ("show", card["id"]))
                lines.append(f"Continue: {action} {json.dumps(query, ensure_ascii=False)} --ref {meta['snapshot']} --offset {page['next_offset']}")
    elif "catalog_sources" in output:
        lines.extend(["Catalog: " + source_line(output["catalog_source"]),
                      "Original catalog context (not verified): " + json.dumps(output["catalog_context"], ensure_ascii=False),
                      "All listed dispositions: " + json.dumps(output["dispositions"], sort_keys=True),
                      f"Listed sources: {output['total_catalog_sources']}; query matches: {output['total_matches']}; offset {output['offset']}."])
        for item in output["catalog_sources"]:
            lines.extend(["", f"{item['id']}: {item['topic']} — {item['disposition']}",
                          f"{item['path']}; direct records={item['direct_records']}; bound references={item['bound_reference_records']}"])
            if item["source"]:
                lines.append("Source: " + source_line(item["source"]))
            for rid in item["example_record_ids"]:
                lines.append("Read: show " + rid)
            if item["catalog_context"]:
                lines.append("Original catalog context (not verified): " + json.dumps(item["catalog_context"], ensure_ascii=False))
        if output["next_offset"] is not None:
            lines.append(f"More: sources with the same query, --ref {meta['snapshot']} --offset {output['next_offset']}")
    elif "review_items" in output:
        lines.extend(["Status: " + output["status"],
                      f"Review queue: {output['total_review_items']} items; showing offset {output['offset']}, {len(output['review_items'])} items."])
        for item in output["review_items"]:
            lines.extend(["", item["id"], "Affected: " + ", ".join(item["record_ids"]),
                          "Annotation: " + source_line(item["annotation_source"])])
            for source in item["changed_sources"]:
                lines.extend([source["state"] + ": " + source["path"],
                              f"Pinned: {source['pinned_commit']} sha256={source['pinned_sha256']}",
                              f"Current: {meta['snapshot']} blob={source['current_blob']} sha256={source['current_sha256']}"])
            lines.append(item["next_action"])
        if output["next_offset"] is not None:
            lines.append(f"More: maintenance --ref {meta['snapshot']} --offset {output['next_offset']}")
    else:
        lines.extend(["Status: " + output["status"],
                      "Kinds: " + json.dumps(meta["by_kind"], sort_keys=True),
                      f"Reports without structured sections (retained whole): {meta['reports_without_structured_sections']}"])
        lines.append("Research document coverage: " + json.dumps(meta["research_documents"], ensure_ascii=False))
        lines.append("Banked inbox coverage: " + json.dumps(meta["inbox_documents"], ensure_ascii=False))
        lines.append("Selected catalog document coverage: " + json.dumps(meta["catalog_documents"], ensure_ascii=False))
        for family, coverage in meta["history_sources"].items():
            lines.append(f"History {family}: {coverage['status']}; {coverage['records']} records")
        for family, coverage in meta["register_sources"].items():
            lines.append(f"Register {family}: {coverage['status']}; {coverage['records']} records")
        links = meta["relationships"]
        lines.append(f"Reviewed links: {links['count']}; stale: {links['stale']}")
        lines.append(f"Knowledge records with changed support: {meta['stale_knowledge_records']}")
    if "note" in output:
        lines.extend(["", output["note"]])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("search", "show", "source", "coverage", "verify", "maintenance", "sources"))
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--ref", default="HEAD", help="Pinned Git snapshot, never live working-file semantics")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--offset", type=int, default=0, help="Page offset for maintenance/sources or zero-based research-document line offset")
    parser.add_argument("--lines", type=int, default=80, help="Maximum lines per research-document page; output budget may reduce this")
    parser.add_argument("--pointer", action="append", default=None,
                        help="On source only: select a complete JSON value; repeat for up to32 distinct pointers. Empty string selects root")
    parser.add_argument("--outline", action="store_true", help="On source: page immediate JSON child paths/types without values; optionally give one --pointer")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="Compact reading view (default) or structured transport")
    parser.add_argument("--max-bytes", type=int, default=14000, help="Hard UTF-8 output budget, including metadata")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    try:
        if args.limit < 1 or args.max_bytes < 1500 or args.offset < 0 or args.lines < 1:
            raise MemoryError("Use limit/lines >= 1, offset >= 0 and max-bytes >= 1500")
        if args.offset and args.action not in {"maintenance", "sources", "show", "source"}:
            raise MemoryError("--offset is supported only for maintenance, sources, source or research-document show")
        if args.pointer is not None and (args.action != "source" or (args.offset and not args.outline) or args.lines != 80):
            raise MemoryError("--pointer requires source and cannot combine with line pagination")
        if args.pointer is not None and (len(args.pointer) > 32 or len(set(args.pointer)) != len(args.pointer)):
            raise MemoryError("Use at most32 distinct JSON pointers")
        if args.outline and (args.action != "source" or args.lines != 80 or len(args.pointer or []) > 1):
            raise MemoryError("--outline requires source, at most one pointer, and no line pagination")
        snap = Snapshot(args.root, args.ref)
        cards, meta = load(snap)
        output: dict = {"meta": meta}
        if args.action == "search":
            hits = rank(cards, args.query)
            output.update(query=args.query, total_matches=len(hits),
                          matches=[brief(c) for c in hits[:args.limit]],
                          note="Retrieval matches, not support. No match does not prove the work was never done.")
        elif args.action == "show":
            card = next((c for c in cards if c["id"] == args.query), None)
            if card is None:
                raise MemoryError("Record absent from this scoped inventory; not evidence it was never tried")
            if args.offset and card["kind"] != "research_document":
                raise MemoryError("--offset on show requires a research document")
            output["record"] = card
            output["note"] = "Historical decisions are evidence, not current instructions. Read caveats and linked corrections before reuse."
        elif args.action == "source":
            output["record"] = source_document(snap, args.query, cards)
            if args.outline:
                output["record"] = outline_source_json(output["record"], (args.pointer or [""])[0], args.offset, args.limit)
            elif args.pointer is not None:
                original = output["record"]
                if len(args.pointer) == 1:
                    output["record"] = select_source_json(original, args.pointer[0])
                else:
                    # All selections must resolve before emitting any result. Preserve
                    # caller order and explicit pointers; never infer a common parent read.
                    values = [{"json_pointer": pointer,
                               "value": select_source_json(original, pointer)["selected_json"]}
                              for pointer in args.pointer]
                    output["record"] = {k: v for k, v in original.items() if k != "_document_text"}
                    output["record"].update(kind="source_json_values", selected_json_values=values,
                        context_scope="Selected decoded JSON values only; fields outside the listed pointers are unread. Original whitespace is not reproduced. Inspect surrounding decisions and linked corrections before interpreting these values.")
            output["note"] = "Committed source identity retained; JSON selection is decoded, not verbatim text. This does not expand indexed coverage or certify current validity. Missing related records do not prove absence of corrections."
        elif args.action == "sources":
            sources = catalog_sources(cards, snap)
            catalog = json_doc(snap.read(CATALOG), CATALOG, dict)
            terms = args.query.casefold().split()
            hits = [s for s in sources if all(t in (s['id'] + ' ' + s['path'] + ' ' + s['topic']).casefold() for t in terms)]
            end = args.offset + args.limit
            output.update(catalog_source=snap.source(CATALOG),
                          catalog_context={k: v for k, v in catalog.items() if k not in {"inventories", "by_topic"}},
                          query=args.query,
                          total_catalog_sources=len(sources), total_matches=len(hits), offset=args.offset,
                          dispositions={state: sum(s['disposition'] == state for s in sources)
                                        for state in sorted({s['disposition'] for s in sources})},
                          catalog_sources=hits[args.offset:end], next_offset=end if end < len(hits) else None,
                          note="Only sources listed in the existing master catalog are reconciled. Direct records are partial extraction, not complete understanding. Bound references count note/knowledge references and can be historical or stale. NOT_IN_READER can include routing-only files; it is not automatically missing scientific work. Other branches, hosts and unlisted sources remain outside this denominator.")
        elif args.action == "maintenance":
            queue = maintenance_queue(cards, snap)
            end = args.offset + args.limit
            output.update(status="REVIEW_REQUIRED" if queue else "NO_SOURCE_DRIFT_IN_CHECKED_REFERENCES",
                          total_review_items=len(queue), offset=args.offset,
                          review_items=queue[args.offset:end],
                          next_offset=end if end < len(queue) else None,
                          note="Checks only explicitly bound notes, knowledge records and reviewed links in this snapshot. A clear queue does not prove complete coverage, correct conclusions or current runtime usability. No source or conclusion is rewritten.")
        else:
            output["status"] = "SOURCE_ANCHORS_VALID" if args.action == "verify" else "SCOPED_COVERAGE"
        if args.action in {"search", "show", "maintenance"} or output.get("record", {}).get("kind") in {
                "research_document", "source_document", "source_json_value", "source_json_values", "source_json_outline"}:
            # Keep source-specific warnings and links on the record. The global
            # catalog census is on demand, not a fixed cost on every source page.
            output["meta"] = {key: meta[key] for key in (
                "schema", "snapshot", "records", "review_notes", "stale_review_notes",
                "stale_knowledge_records", "retraction_source", "coverage_limit", "verification_limit")}
            output["meta"]["metadata_scope"] = "Compact retrieval metadata; full catalog census via coverage at this snapshot"
        def render() -> str:
            return (render_text(output) if args.format == "text" else
                    json.dumps(output, ensure_ascii=False, indent=2) + "\n")

        if output.get("record", {}).get("kind") in {"research_document", "source_document"}:
            original = output["record"]
            count = min(args.lines, max(1, len(original.get("_document_text", "").splitlines()) - args.offset))
            while True:
                output["record"] = document_page(original, args.offset, count)
                rendered = render()
                if len(rendered.encode("utf-8")) <= args.max_bytes or count == 1:
                    break
                count -= 1
        else:
            rendered = render()
        if len(rendered.encode("utf-8")) > args.max_bytes:
            # Never silently truncate a result while dropping its caveats or retractions.
            raise MemoryError(f"Output needs {len(rendered.encode('utf-8'))} bytes; increase --max-bytes or reduce --limit")
        print(rendered, end="")
        return 0
    except (MemoryError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "MEMORY_UNAVAILABLE", "reason": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
