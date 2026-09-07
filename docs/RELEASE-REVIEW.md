# Release review

A pre-publication review of this repository, recorded so a reader can see what was
checked, what was found, and what is still open. **This is a scan and a set of
judgements. It is not a security certification, a legal clearance, or a licence audit.**

Reviewed: 2026-09-07T01:46:08Z, at branch `codex/judge-repo-repair`.
Scope: all tracked files in this repository. Method: pattern scan over every tracked
text file, plus manual reading of the attribution and provenance surfaces.

## Findings — clean

| Checked for | Result |
|---|---|
| Private-key blocks (`-----BEGIN … PRIVATE KEY-----`) | **0** |
| AWS-style access keys (`AKIA…`) | **0** |
| GitHub tokens (`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`) | **0** |
| `api_key` / `secret` / `password` assignments with a literal value | **0** |
| Competition engine, organiser card database, episode dumps, model weights | **0 — none present** |
| Third-party kernel source | **0 — none present**; only the attribution register |
| Real email addresses | **0** — the 24 matches are test fixtures (`@example.com`, `@example.invalid`) and synthetic seat names (`master@fleet.local`, `skynet@ptcg.local`) |

Repository size: 141 tracked files, ~13 MB working tree, 2.74 MiB packed. Two commits
(squashed public import).

## Findings — acted on

**Credential locations redacted — 8 places in 3 files.** The record named the absolute
path at which a Kaggle API credential file had been provisioned, and in one case named it
next to the token's environment-variable name. **No key material was present** — only the
location.

| File | Redactions |
|---|---|
| `workflow/DECISIONS.md` | 5 |
| `workflow/inventories/sri/registers/DECISIONS.md` | 2 |
| `workflow/inventories/sri/MANIFEST.jsonl` | 1 (`KAGGLE_API_TOKEN@…`) |

Replaced with `[REDACTED credential path]`, `[REDACTED drive]` or `[REDACTED]`. Only the
path tokens changed; the surrounding text — which is the historical record of a credential
incident and its resolution — is unchanged, and line endings were preserved.

Note that the third file is part of the **generated inventory snapshot**. The snapshot is
otherwise published exactly as it stood; this one redaction is the sole deliberate
deviation, and it is recorded here so the deviation is not silent. `~/.kaggle/kaggle.json`
still appears in the record: that is the tool's documented default location on every
machine, not a disclosure.

**Attribution overstatement corrected.** `NOTICE` previously said every opponent kernel
was recorded in `workflow/PUBLIC-KERNELS-PROVENANCE.md`. It is not. See the open item
below; `NOTICE` now states the gap and names the affected authors.

**Provenance register's basis clarified.** That register's historical dispositions were
written about the private working repository and reason explicitly from its being
private. An export note at its head now states that publishing the register does not
redistribute any kernel, and that those dispositions are not a clearance for this export.

## Open items — not resolved here

**1. Five opponent authors have no licence-and-provenance row.**

The published seven-opponent panel names `plamen06`, `llccqq624`, `raunakdey07`,
`zoli800` and `harukiharada` in its results. None has a row in the provenance register.
Their kernel source is not redistributed here, and this repository makes no claim about
their licence terms — but it does publish measured outcomes against their agents without
the recorded provenance that `NOTICE` promises for the others.

*Decisive check:* for each of the five, open the kernel page, read the licence verbatim,
and record author / source URL / licence / public flag / pull date / per-file SHA-256 as a
register row. Licence verification in this project has always been done by a human
reading the page; it is not delegated.

*Note on prior exposure:* these identifiers and results are already published in the
evidence package attached to the competition submission. Making this repository public
does not newly disclose them. That reduces the urgency; it does not close the item.

**2. Signed-out access is unverified.**

This repository is private at the time of review, so public readability has not been
demonstrated. *Decisive check, to run after any visibility change:* fetch the repository
URL with no credentials and confirm HTTP 200 rather than 404, then confirm that
`README.md`, `docs/STRATEGY-WRITEUP.md` and one evidence JSON each render for a
signed-out visitor.

**3. Provenance strings retain local paths.**

29 Windows paths under `C:\Users\thisi\…` and 103 references to a `D:/ptcg_archive`
local archive remain across 19 files. These are deliberate: they identify where evidence
was produced, and removing them would break traceability without making anything safer.
They are not downloadable assets and no credential path remains among them.

**4. No licence audit or automated security scan of dependencies.**

None was run and none is claimed. The pattern scan above covers secrets and obvious
leakage; it is not a substitute for either.

**5. The Kaggle project link.**

Still needs to point at this companion repository rather than promising access to the
private working repository. Outside this repository's control.

## What this review does not establish

A clean pattern scan is not proof that nothing sensitive is present — the patterns are
finite and the reviewer is the author's agent, not an independent auditor. Hash matches
establish byte identity, not scientific validity. Nothing here certifies that publishing
this repository is legally cleared; items 1 and 4 remain open and are the reason that
statement is made rather than avoided.
