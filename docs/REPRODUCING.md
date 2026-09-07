# Reproducing

This page states only what a reader can actually run in a fresh clone of this
repository, and names what cannot be run here and why.

## A verified offline example

**Prerequisites:** Python 3.10 or later, and `git` on `PATH` (the tool shells out to
`git ls-files`; it degrades to a directory walk without it). No third-party packages, no
game engine, no network access, no credentials.

```
git clone https://github.com/thisisntjon/poketcg-research.git
cd poketcg-research
python -X utf8 scripts/prior_art.py "Xerosic" --limit 2
```

**Expected output shape** — a header line naming the query, the corpus size and the
retrieval path, then the hit count and elapsed time, then up to `--limit` scored rows
(score, date, path, title, state), then a summary line:

```
PRIOR ART: "Xerosic"
  terms ['xerosic']  corpus 29 files  via tracked tree (catalog absent)
  7 hits in 0.282s

   7.66  2026-09-03  workflow/research/2026-09-03-xerosic-sniper-factorial.md
         Xerosic × Sniper — an INDEPENDENTLY REPRODUCED improvement (2026-09-03, SKYNET)  [state: UNKNOWN]  (keywords only: banked, null)
   7.66  2026-09-03  workflow/research/2026-09-03-xerosic-sniper-rows.csv
         run,arm,opponent,outcome,seat,prize_margin,...  [state: UNKNOWN]

  PRIOR_ART: "Xerosic" -> 7 hits -> no-catalog
```

Exit code 0. That transcript is from a fresh clone of this commit; elapsed time varies,
and the scores are corpus-relative, so they shift whenever the corpus changes. Try any
other query in place of `"Xerosic"`.

**Actual scope and known limitations.**

- `via tracked tree (catalog absent)` is not an error and not a fallback failure — it is
  the honest state of this export. The tool prefers `workflow/ARTIFACT-CATALOG.jsonl`,
  which is **not** included here (see below), so it searches the tracked tree instead.
  The corpus is therefore this repository's documents, **not** the full working
  repository's corpus.
- The hit count and corpus size depend on what is committed. They will change as this
  repository changes; the shape of the output will not.
- `[state: UNKNOWN]` means the tool could not resolve a banked state for that row from
  the records present here. It is not a judgement about the finding.
- **A hit is not a verdict, and a miss is not proof that work never happened.** A missing
  search result is a coverage limitation of this corpus.

## Two more offline tools

```
python -X utf8 scripts/retraction_scan.py <file-or-directory>
python -X utf8 scripts/retraction_register.py <number>
```

`retraction_scan.py` is the publication check: it reads
[the retraction register](../workflow/canon/RETRACTIONS.md) and flags any retracted
numeric token or hash prefix in a document, with the value to use instead.
`retraction_register.py <number>` answers the same question for one value.

Run plainly over this repository's own pages, it **exits 1 with 15 hits**:

```
$ python -X utf8 scripts/retraction_scan.py README.md NOTICE docs
[RETRACTED] docs\EVIDENCE-MAP.md
  L44: `8.26` -> use instead: **`+7.82pp [+6.08, +9.56]`**
  …
scanned 10 file(s) against 16 retracted tokens: 15 hit(s); 0 inspection failure(s). FIX BEFORE PUBLISHING.
```

**That is the firewall working, not a defect.** Every hit is in one of the four pages
that quote `+8.26` and `+9.35` deliberately (`README.md`, `docs/EVIDENCE-MAP.md`,
`docs/RELEASE-REVIEW.md` and this page), in order to *explain* why recomputing the
headline from the shipped rows produces a superseded value. The tool cannot tell
"citing a retracted number as fact" from "citing it to retract it", and it should not
try to.

The tool's own documented escape is `--allow`, one token at a time, so an exemption is
always visible in the command:

```
$ python -X utf8 scripts/retraction_scan.py --allow 8.26 --allow 9.35 README.md NOTICE docs
scanned 10 file(s) against 14 retracted tokens: 0 hit(s); 0 inspection failure(s).
```

Two tokens allowed, fourteen still enforced. We are not suppressing the check — the plain
form above is printed here precisely so the exemption cannot be mistaken for a clean bill.
**A clean run is not a certificate** either way: the register can be incomplete, and the
tool says so in its own output.

Both are read-only. (`retraction_register.py --census` writes a census file; that form is
not part of the advertised path here.)

## The inventory is a preserved snapshot, not a rebuild

`workflow/inventories/sri/` — 2,333 records across ten registers — is a **frozen
historical snapshot**, published as it stood in the working repository. It is evidence,
and its rows name their source documents.

**It cannot be regenerated from this export, and this repository no longer promises that
it can.** Running the generator here fails, by design of the export rather than by defect
of the generator:

```
$ python -X utf8 scripts/build_sri.py --check
CURATED.json names a missing A asset: START-HERE.md
$ echo $?
1
```

That first message is not the whole problem, and supplying the one named file would not
fix it. The generator's full dependency closure is missing from this export:

| Missing dependency | What the generator needs it for |
|---|---|
| `START-HERE.md`, `workflow/NOW.md`, `workflow/canon/EQUATIONS-AND-BOUNDS.md`, `workflow/writeup/APPENDIX.md`, `scripts/context_pack.py` | five of the twenty A assets named in `CURATED.json`; the check fails on the first one it reaches |
| `workflow/ARTIFACT-CATALOG.jsonl` | the artifact census behind `MANIFEST.jsonl` and the TOOLS register |
| `workflow/curation/labels.csv` | the curation labels behind the same two registers |
| `D:/ptcg_archive` | a local external archive on the original workstation, used for the TOMBSTONES register |
| the unsquashed Git history | first-add dates for the TIMELINE register, and the `main` hash stamped into each generated header |

The last two cannot be shipped at all: the archive is a local disk on one machine, and
**this repository is a squashed import with two commits — the objects behind the original
history are not in this tree and are not reachable from it.**

We deliberately did **not** regenerate a smaller inventory against this reduced tree.
Doing so would have produced a new census with less coverage while overwriting historical
records that carry their original identities and dates. The snapshot is preserved instead,
and the generator is kept beside it as the source that produced it, unrunnable here.

### If you run the test suite or the onboarding checker

Both are present and both will run. Neither passes here, and the numbers are stated up
front so nothing is a surprise:

```
$ python -X utf8 -m pytest -q
11 failed, 179 passed, 24 errors, 10 subtests passed
```

All 35 failures and errors are in three files, and every one is an **export-scope**
failure rather than a code defect — the assertions reference corpus files and inventory
dependencies that are not in this repository:

| File | Failures + errors | Why |
|---|---|---|
| `test_build_sri.py` | 24 | needs the generator's dependency closure (see above) |
| `test_prior_art.py` | 9 | asserts specific documents rank in the top 5 for a query; those documents are not in this corpus |
| `test_dock.py` | 2 | same cause |

The other **179 tests pass**, which is what the export can honestly support. We did not
delete or skip the failing files to make the run green: a suite that is made to pass by
removing the check is worth less than one that fails legibly.

```
$ python -X utf8 scripts/onboard_check.py
… 21 error(s), 15 warning(s).
ONBOARD CHECK FAILED - a harness reading START-HERE.md would be misled.
$ echo $?
1
```

That banner is **correct and expected**. The checker validates the *private working
repository's* onboarding path — `START-HERE.md`, `workflow/NOW.md`, `DEADLINES.json`, the
answer map — none of which is part of this export. It is preserved as source, not
advertised as a check that passes here.

`scripts/build_sri.py`, `scripts/onboard_check.py`, `scripts/dock.py`,
`scripts/research_memory.py`, `scripts/map_validate.py`, `scripts/archive_desktop.py`,
`scripts/unconflict.py`, `scripts/merge_head_guard.py`, `scripts/ci_gates.py` and the
suites under `ptcg-agent/harness/` are in the same position: preserved source, dependent
on the private working repository, **not** advertised as runnable here. Do not run the
cleanup or migration scripts among them merely because they were exported.

## What cannot be reproduced anywhere in this repository

**The games.** The competition game engine and the card data are supplied by the
competition organisers under their own terms. They are not ours to redistribute and are
excluded by design. **No comparison in this repository can be re-run end to end**, and
nothing here executes a game. What is published instead, for every result, is the sample
size, the interval, the exact arms compared, the opponent identities and their hashes,
and — where it exists — the analysis script. A reader with engine access can rebuild a
run from that; a reader without it can still check the arithmetic and the reasoning.

`workflow/writeup/visuals-2026-09-06/build_counterplay.py` is the analysis source behind
the report's figures. It retains repository-relative assumptions from its original
checkout, may need dependencies and path adaptation, and was **not** run as part of
preparing this export. It is not a one-click reproduction.

**Raw episode dumps and model weights.** Not published: too large, and they contain match
records involving other competitors' agents. Aggregates are published; traces are not.
The two replay decisions cited by the report were checked in their original seat-visible
records and the check is preserved in
[REPLAY-CHOICE-VERIFICATION.json](../workflow/writeup/visuals-2026-09-06/REPLAY-CHOICE-VERIFICATION.json);
**a recorded inspection is not a publicly runnable reproduction.**

**Third-party kernels.** Other people's Kaggle notebooks used as fixed opponents are not
republished. Their provenance — author, source URL, licence, pull date, and a SHA-256 per
file — is in `workflow/PUBLIC-KERNELS-PROVENANCE.md` so a reader can fetch them from the
original source.

## Where the receipts live

- [docs/EVIDENCE-MAP.md](EVIDENCE-MAP.md) — the report's references 1–8, mapped to files
  here with hashes and limits. Start here.
- `workflow/inventories/sri/INDEX.md` — the snapshot map. Read it, then open at most two
  registers.
- `workflow/inventories/sri/registers/CLAIMS.md` — every number and where it can be
  *read*, which is a separate question from whether it is true.
- `workflow/canon/RETRACTIONS.md` — what not to cite, and why.
- `workflow/DEAD-ENDS.md` — closed lines, each with the claim it does not support.

Every register row names its source document and a line locator. The registers are
summaries; the documents they cite are the source of truth, and on any disagreement the
document wins.
