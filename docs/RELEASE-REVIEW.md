# Release review

A pre-publication review of this repository, recorded so a reader can see what was
checked, what was found, and what is still open. **This is a scan and a set of
judgements. It is not a security certification, a legal clearance, or a licence audit.**

Reviewed: 2026-09-07T01:46:08Z, at branch `codex/judge-repo-repair`; re-run after
publication against the public repository, **including every object in its history**.
Method: pattern scan over every text blob reachable from any ref — not only the checked-out
tree — plus manual reading of the attribution and provenance surfaces.

Scanning history rather than the working tree matters here, and it changed one conclusion:
see [the note on the redaction](#the-redaction-does-not-remove-the-path-from-this-repositorys-history).

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
| Slack / OpenAI / Anthropic API keys, bearer headers, private IP addresses | **0** |
| CI workflows, `setup.py`, git hooks, shell scripts — anything that executes on clone | **none present** |

The rows above were checked across **all 205 text blobs in the public history**, not only
the current tree.

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

### The redaction does not remove the path from this repository's history

**Stated plainly because the paragraph above, on its own, overstates what was achieved.**
The redaction is a commit. The commits before it are public. The pre-redaction bytes are
therefore still readable by anyone:

```
$ git show 7d57d58:workflow/DECISIONS.md | grep -o 'V:.Pokemon.kaggle.json'
V:\Pokemon\kaggle.json
```

Redacting at `HEAD` changes what a reader sees in the checked-out tree. It does not remove
an object from a public repository, and no later commit can.

**What that does and does not expose.** A file path and drive letter on one workstation,
plus the name of an environment variable. **No key material is exposed, and none ever
was** — a scan of all 205 text blobs across the full public history found zero private-key
blocks, zero cloud or platform access tokens, and zero credential assignments carrying a
literal value. The disclosure is that a credential file once lived at a particular local
path on a machine that is not reachable from the internet.

**Why the history was not rewritten.** Rewriting would invalidate the merge commits and the
pull-request references that document how this repository was prepared, and it would not
recall anything already cloned, forked or cached. For a local path with no key material,
that trade is not worth taking. The honest record is better than a clean-looking one.

**The decisive mitigation, if this is ever judged to matter, is rotating the credential** —
not editing this repository. That is outside this repository's control and is not claimed
here.

**Attribution overstatement corrected.** `NOTICE` previously said every opponent kernel
was recorded in `workflow/PUBLIC-KERNELS-PROVENANCE.md`. It is not. See the open item
below; `NOTICE` now states the gap and names the affected authors.

**Provenance register's basis clarified.** That register's historical dispositions were
written about the private working repository and reason explicitly from its being
private. An export note at its head now states that publishing the register does not
redistribute any kernel, and that those dispositions are not a clearance for this export.

## Adversarial pass — what a sceptical reader finds

Separately from the security scan, the repository was read the way a judge who trusts
nothing would read it: recompute the numbers, run the commands, click the links. Findings
and their disposition:

| Finding | Disposition |
|---|---|
| Pooling the combined-arm contrasts that ship gives **+8.26**, not +7.82 — and the retraction register flags +8.26 as superseded | **Explained up front** in [EVIDENCE-MAP](EVIDENCE-MAP.md#if-you-recompute-the-headline-you-will-get-a-different-number-here-is-why); the third input is the second-machine reproduction whose rows are not shipped. The headline is **not independently verifiable from this repository alone**, and that is now stated rather than left to be discovered. |
| `pytest` reports **11 failed, 179 passed, 24 errors** | **Documented with exact counts** in [REPRODUCING](REPRODUCING.md). All 35 are export-scope, in three files. Not silenced or skipped. |
| **206 broken relative links** across the tracked Markdown, 188 in `registers/LEARNINGS.md` | **Bannered at the top of that register** with the count and the reason. It is the largest navigation gap here. |
| `scripts/onboard_check.py` exits 1 printing `ONBOARD CHECK FAILED` | **Documented**; it validates the private repository's onboarding path, which is not part of this export. |
| The generalisation report prints **+20.17 / +18.50** where Figure 2 gives **+20.42 / +18.75** | **Explained**: wins-÷-all-games versus win = 1 / draw = ½. Both reproduce; 12 draws in 8,400 games. The report notes one convention difference but not this one. |
| `ATTEMPTS-LEDGER` GR-91 says *"the whole net gain is a one-card deck swap"* | Left as written. It is a different experiment (10,800 games, a different policy pair), and the same row goes on to say explicitly that "the policy contributes nothing" is FALSE. Quotable out of context; the correction is in the row. |

What did reproduce exactly: both Alakazam panel cells, the five-cell mean, the mixture
equation's coefficient and its value at q = 0.25, and both ablation pools. See
[EVIDENCE-MAP](EVIDENCE-MAP.md#what-does-recompute-exactly-from-these-rows).

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

**2. Signed-out access — CLOSED 2026-09-07T05:00Z.**

The repository is public and the decisive check has been run. With no credentials
supplied, `https://github.com/thisisntjon/poketcg-research` returned HTTP 200, and each
of `README.md`, `docs/STRATEGY-WRITEUP.md` and
`workflow/writeup/visuals-2026-09-06/ABLATION-VERIFICATION.json` returned HTTP 200 over
`raw.githubusercontent.com`. That establishes anonymous readability of those three paths
on that date. It does not establish that every path renders, and it is not a permanent
property: any later visibility change voids it.

**3. Provenance strings retain local paths.**

29 Windows paths under `C:\Users\thisi\…` and 103 references to a `D:/ptcg_archive`
local archive remain across 19 files. These are deliberate: they identify where evidence
was produced, and removing them would break traceability without making anything safer.
They are not downloadable assets, and no credential path remains among them **at `HEAD`** —
see [the note above](#the-redaction-does-not-remove-the-path-from-this-repositorys-history)
for what the history still contains.

**4. Two third parties are named in full, not only by handle.**

`workflow/PUBLIC-KERNELS-PROVENANCE.md` records `aristophanivan (Ivan Ternovskiy)` and
`romanrozen (Roman Rozen)`. The names were read from their public Kaggle pages during
licence verification. The handle alone would serve the attribution purpose, so the full
names are additional personal information published without those authors' involvement.

*Decisive check:* confirm each name is still self-published on the author's own public
profile. If it is not, reduce the row to the handle. Either way, removal on request.

**5. No licence audit or automated security scan of dependencies.**

None was run and none is claimed. The pattern scan above covers secrets and obvious
leakage; it is not a substitute for either.

**6. Fifty-one links point at the private working repository and return 404.**

Fifty-one `github.com/thisisntjon/poketcg/...` URLs remain in this tree. Verified
2026-09-07T05:00Z: an anonymous fetch of one of them returns **HTTP 404**, because that
repository is private. They are provenance stamps naming where a record was produced,
not reader routes, and they are **not** the same class as the local filesystem paths in
item 3 — a reader can tell a `C:\Users\...` path is not fetchable, but a GitHub URL
invites a click that fails.

They are confined to machine-readable records, and **no user-facing page carries one**:
`README.md` and all seven `docs/*.md` pages scan clean.

| File | Links | Form |
|---|---|---|
| `workflow/knowledge-register/audits/2026-09-06-method-recovery/independent-review.json` | 20 | `/blob/d5aa5073…` permalinks |
| `workflow/inventories/sri/MANIFEST.jsonl` | 11 | `/pull/NNN`, inside `why_it_matters` prose |
| `workflow/knowledge-register/audits/2026-09-06-method-recovery/original-review-envelope.json` | 1 | `/blob/d5aa5073…` permalink |

Not rewritten here, deliberately. The two audit files are review envelopes: editing a
record after the fact to improve how it reads is the failure this project's registers
exist to prevent. `MANIFEST.jsonl` is generated by `scripts/build_sri.py`, so a hand
edit would desync it from its generator. *Decisive check, if this is closed later:*
regenerate the manifest with the URLs rendered as `poketcg#NNN (private)`, and leave the
audit envelopes as written with this disclosure standing.

**7. The Kaggle project link.**

Still needs to point at this companion repository rather than promising access to the
private working repository. Outside this repository's control.

## What this review does not establish

A clean pattern scan is not proof that nothing sensitive is present — the patterns are
finite and the reviewer is the author's agent, not an independent auditor. Hash matches
establish byte identity, not scientific validity. Nothing here certifies that publishing
this repository is legally cleared; items 1 and 4 remain open and are the reason that
statement is made rather than avoided.
