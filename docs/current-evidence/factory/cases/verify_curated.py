"""Verify delivered curation bytes; does not execute models, games or source code."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "SOURCE-MANIFEST.json").read_text(encoding="utf-8"))
    records = (
        manifest["excerpts"]
        + manifest["derived_artifacts"]
        + manifest.get("documents", [])
    )
    seen = set()
    for record in records:
        target = (root / record["path"]).resolve()
        if not target.is_relative_to(root) or record["path"] in seen:
            raise ValueError("Invalid or repeated delivered path: " + record["path"])
        seen.add(record["path"])
        data = target.read_bytes()
        if len(data) != record["bytes"]:
            raise ValueError("Byte count mismatch: " + record["path"])
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError("SHA-256 mismatch: " + record["path"])
    print(json.dumps({
        "status": "PASS",
        "delivered_files_checked": len(records),
        "source_identities": len(manifest["sources"]),
        "scope": "Delivered byte identities only; no scientific or runtime certification.",
    }, indent=2))


if __name__ == "__main__":
    main()
