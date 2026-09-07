# Reproducing

## What you can reproduce with nothing but this repository

The inventory — 2,333 records across 10 registers — is **generated**, not written
by hand. Exactly one file in it is authored:
`workflow/inventories/sri/CURATED.json`, which holds the project summary and the
short curated lists. Everything else is built from the source documents in this
repository.

```
python scripts/build_sri.py            # regenerate the inventory from source documents
python scripts/build_sri.py --check    # exit 1 if the committed inventory differs from a rebuild
```

The `--check` form is the gate. If it exits non-zero, a committed register has
drifted from the documents it claims to summarise, and the register is wrong. Run
it before trusting any register row.

Two more scripts run offline and need no game engine:

```
python scripts/prior_art.py "<question>"        # has this already been tried, and what happened
python scripts/retraction_scan.py <file-or-dir> # does this document cite a retracted number
```

`retraction_scan.py` is the publication check. It reads the retraction register and
flags any retracted numeric token or hash prefix in a document, together with the
"use instead" value. A clean run is not a certificate — the register can be
incomplete — and the tool says so.

## What you cannot reproduce here

**The games.** The competition game engine and the card data are supplied by the
competition organisers under their own terms. They are not ours to redistribute
and are excluded from this repository by design. Without them, no comparison in
this repository can be re-run end to end.

That is a real limitation and we state it plainly. What is published instead, for
every result, is: the sample size, the interval, the exact arms compared, the
opponent identities and their hashes, and the script that produced the numbers. A
reader with engine access can rebuild any run from that. A reader without it can
still check the arithmetic and the reasoning.

**Raw game logs.** Hundreds of thousands of games produced trace files far too
large to publish, and they contain match records involving other competitors'
agents. Aggregates are published; traces are not.

**Third-party kernels.** Other people's Kaggle notebooks used as fixed opponents
are not republished here. Their provenance — author, source URL, licence, pull
date, and a SHA-256 per file — is recorded in
`workflow/PUBLIC-KERNELS-PROVENANCE.md` so a reader can fetch them from the
original source.

## Where the receipts live

- `workflow/inventories/sri/INDEX.md` — the map. Read this first, then open at
  most two registers.
- `workflow/inventories/sri/registers/CLAIMS.md` — every number, where it can be
  read, and whether it has been retracted. Each row carries a verification status
  that says where the number can be *read*, which is a separate question from
  whether it is true.
- `workflow/inventories/sri/registers/METHODS.md` — the sizing arithmetic, the
  noise measurements, and where each is implemented.
- `workflow/inventories/sri/registers/TOOLS.md` — every script, how to run it, and
  whether it has ever produced output.
- `workflow/canon/RETRACTIONS.md` — what not to cite, and why.
- `workflow/DEAD-ENDS.md` — closed lines, each with the claim it does not support.

Every register row names its source document and a line locator, so a row can be
traced back to the text it came from. The registers are summaries. The documents
they cite are the source of truth, and on any disagreement the document wins.
