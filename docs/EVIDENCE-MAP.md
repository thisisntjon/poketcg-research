# Evidence map

The report's numbered references 1–8 point here. Every row names the file in this
repository, its SHA-256 as packaged in the submitted `PTCG-EVIDENCE.zip`, and what
the file does **not** establish.

Hashes identify bytes. They do not establish scientific validity, native execution or
reproducibility. Read each record's own `limits` field alongside its result.

> **Hashing note.** The SHA-256 values below are of the files as stored in Git (LF line
> endings) and as packaged in the evidence ZIP. A Git checkout on Windows may convert
> text files to CRLF in the working tree, which changes the on-disk hash without changing
> the content. To check a text file against this table, hash the committed blob:
> `git cat-file -p HEAD:<path> | sha256sum`.

## References 1–8

| # | What the report cites it for | File in this repository | SHA-256 | What it does not establish |
|---|---|---|---|---|
| 1 | Submitted-product provenance | [`workflow/research/owned-learning-roadmap-20260813/lane-s-c61-provenance-receipt.json`](../workflow/research/owned-learning-roadmap-20260813/lane-s-c61-provenance-receipt.json) | `4e9801ee993d33b709ab0740ef59acfc8de1cd146de2f328ee597bc023e871fb` | Identifies the submitted product as a credited public policy. It does not explain why that policy was chosen, and it is not an original trained policy from this project. |
| 2 | Factorial design and replication | [`workflow/research/2026-09-03-xerosic-sniper-factorial.md`](../workflow/research/2026-09-03-xerosic-sniper-factorial.md) | `1b45e70cfd8fefcc8a2e8fe07af33bffff90109543ecd61113de427b87890eaa` | The design record, not an independent reconstruction of every batch. |
| 2 | Separate-ablation arithmetic | [`workflow/writeup/visuals-2026-09-06/ABLATION-VERIFICATION.json`](../workflow/writeup/visuals-2026-09-06/ABLATION-VERIFICATION.json) | `b59c74086c7532cfbd32960277ac78068a9b69c1b4000a29cf250a44d1a74c5c` | Recomputes the card-only and rule-only contrasts. The **combined** arm changes both the list and the rule; this file does not attribute its gain to either component. |
| 2 | Development outcome rows | [`workflow/research/2026-09-03-xerosic-sniper-rows.csv`](../workflow/research/2026-09-03-xerosic-sniper-rows.csv) | `e39d5d54bc51c7b430e4d9ade8cf7a149634d8ef244e32f517e5e8fabf0525aa` | The three-comparison combined headline includes a second-host comparison whose independent raw rows are **not** included here. |
| 3 | Owned student | [`workflow/writeup/visuals-2026-09-06/LEARNING-VERIFICATION.json`](../workflow/writeup/visuals-2026-09-06/LEARNING-VERIFICATION.json) | `3eefa8895eef2483f76efa93ece4214d819701fc70105416089ecd046d66f552` | Links checkpoint identity and recorded validation loss to complete-game outcomes. Checkpoint bytes were checked in the recorded review but are **not** packaged; tensor state was not independently rehashed by loading the model. |
| 3 | Training receipt | [`.../learning-evidence/training-receipt.json`](../workflow/writeup/visuals-2026-09-06/learning-evidence/training-receipt.json) | `fab7750232057596c50f96fae70c1a2f7f8e4b085f23812bb050584356a8322a` | Historical training cannot be fully reproduced from these receipts alone. |
| 3 | Complete-game screen receipt | [`.../learning-evidence/screen-receipt.json`](../workflow/writeup/visuals-2026-09-06/learning-evidence/screen-receipt.json) | `e02921d92ff2f0a0c8c774fdc38f460d5953ebf0d51a6865f77a0d3d8a602a26` | An outcome record, not a rerunnable evaluation. |
| 4 | Fresh-opponent panel rows (8,400 games) | [`workflow/research/2026-09-03-strike3-rows.csv`](../workflow/research/2026-09-03-strike3-rows.csv) | `e5a4ae3461f6f9c80261e3ffd22d60a0a66ca5b11fee7e7f1a708318bdad792d` | Win = 1, draw = ½, loss = 0 here; development results use decided games. The two conventions are not pooled. |
| 4 | Generalisation report | [`workflow/research/2026-09-03-strike3-generalisation.md`](../workflow/research/2026-09-03-strike3-generalisation.md) | `62871e274783a31708aabaff64a1ed0b1acdc92054873df6bb7d32e63e184334` | One Alakazam deck overlaps development under another pilot. The panel's Grimmsnarl implementation is **not** the submitted c61. |
| 4 | Plotted arithmetic and assumptions | [`workflow/writeup/visuals-2026-09-06/counterplay-data.json`](../workflow/writeup/visuals-2026-09-06/counterplay-data.json) | `8dc89872395e8d87f7d776254b798c7b74d02006fbfad30c8b507598138a5cab` | Intervals assume independent games and condition on these implementations. |
| 4 | Figure analysis source | [`workflow/writeup/visuals-2026-09-06/build_counterplay.py`](../workflow/writeup/visuals-2026-09-06/build_counterplay.py) | `d858444b36ec83207bd73177b974144f7692cceb6ab1897eb36345cff2243ea6` | Retains repository-relative assumptions from its original checkout and may need dependencies and path adaptation. **Not a one-click reproduction**, and not run as part of this export. |
| 5 | Research-memory interface | [`workflow/knowledge-register/README.md`](../workflow/knowledge-register/README.md) | `3a95a8c7ea857d2ae5eb6f4ddfeef2b156cb1ca7420bd35cfb4d382da653aa8b` | Documents the reader and its limits. It describes commands requiring the original working repository; that tool and all its source objects are **not** included. It does not certify onboarding acceptance or improved agent decisions. |
| 6 | Recovered product, deck and mechanics | [`workflow/writeup/visuals-2026-09-06/SOURCE-VERIFICATION.json`](../workflow/writeup/visuals-2026-09-06/SOURCE-VERIFICATION.json) | `dcb3c2ffd41f1635f6d7d0b9ab42d6e1e1ee73b126c5924de27eef27f8f06703` | **Static source and card-text review, no engine execution.** No claim about actual branch frequencies, optimal decisions, completed learning or terminal rank. Card data itself is not redistributed, and packaged card text is not proof of engine implementation parity. |
| 7 | Dated competition result | [`workflow/writeup/visuals-2026-09-06/COMPETITION-VERIFICATION.json`](../workflow/writeup/visuals-2026-09-06/COMPETITION-VERIFICATION.json) | `bb7621cfdd123257aefa9bc07962ec0a4405b5ddd6046b916690c35e53c81a1d` | A dated API observation, not a final grading certificate. The entry flag does not certify every eligibility requirement. |
| 8 | Two original replay choices | [`workflow/writeup/visuals-2026-09-06/REPLAY-CHOICE-VERIFICATION.json`](../workflow/writeup/visuals-2026-09-06/REPLAY-CHOICE-VERIFICATION.json) | `26758706eba1af95fac2f79d5e9ebf26210e700550fc9f62f6e9efd658fce5fa` | Records two checked seat-visible decisions and the original file identities. **Original episode dumps are not redistributed**, and neither terminal outcome establishes the counterfactual value of the alternative action. |

The submitted evidence package's own guide, unmodified, is at
[docs/EVIDENCE-PACKAGE-GUIDE.md](EVIDENCE-PACKAGE-GUIDE.md)
(SHA-256 `d68d4bdc0d67233b78bb0932f791ba0f66fd6a8a7cdde159820264d8014f013a`). Its
limitations apply to every file above and are not superseded by this page.

## If you recompute the headline, you will get a different number. Here is why.

**This is the first thing to read before checking our arithmetic.** A reader who pools the
combined-arm contrasts in the shipped rows gets **+8.26 pp**, not the report's +7.82 — and
`python scripts/retraction_register.py 8.26` will tell them +8.26 is **RETRACTED**. That is
not a contradiction, but it needs the bridge below, and without it the headline looks
unverifiable.

The headline pools **three** within-batch comparisons across two machines. Only **two** of
the three ship here:

| Comparison | Contrast | In this repo? |
|---|---|---|
| `factorial`, `D_both` − `A_baseline` | 872/1997 vs 686/1999 = **+9.35 pp** | yes |
| `combined_replicate`, `D_both` − `A_baseline` | 845/1999 vs 701/1997 = **+7.17 pp** | yes |
| Independent reproduction on the second machine (4070) | **+6.94 pp [+3.93, +9.94]** | **no — raw rows not included** |
| Inverse-variance pool of the **two** shipped | **+8.26 pp [+6.13, +10.39]** | reproducible here |
| Inverse-variance pool of **all three** — the published headline | **+7.82 pp [+6.08, +9.56]** | **not reproducible here** |

Both intermediate values are in the retraction register, and the reasons are recorded
there rather than in hindsight:

- **`+9.35`** — a single-batch estimate. Quoting it presents one batch as the result and
  drops the replication.
- **`+8.26`** — the *pre-reproduction* figure. Superseded once the second-machine
  reproduction folded in.

Note the direction: the number **went down** when it was replicated, from +9.35 to +8.26
to +7.82. That is what a working correction process looks like, and it is why the earlier
values are marked retracted rather than quietly dropped.

**What this means for a reader.** The +7.82 headline is **not independently verifiable
from this repository alone** — one of its three inputs is missing. What *is* verifiable
here: the two shipped contrasts recompute exactly, the panel results recompute exactly
(see below), and the retraction register correctly flags the superseded values. We would
rather state that plainly than let a judge discover it by hitting a RETRACTED banner on
their own arithmetic.

## What does recompute exactly, from these rows

Independently recomputed from `2026-09-03-strike3-rows.csv`, scoring win = 1, draw = ½,
loss = 0, candidate minus baseline, 600 games per arm per cell:

| Cell | Recomputed | Report |
|---|---|---|
| `llccqq624` (Alakazam) | **+20.42** [+14.89, +25.94] | +20.42 |
| `raunakdey07` (Alakazam) | **+18.75** [+13.68, +23.82] | +18.75 |
| equal-weight mean, other five | **−0.4667** [−2.64, +1.71] | −0.47 |
| Alakazam mean (the `q` coefficient) | **19.5833** | 19.583 |
| Δ(q) at q = 0.25 | **+4.5458** | +4.55 |

`ABLATION-VERIFICATION.json` also recomputes exactly: rule-only **+3.6188** [+1.516,
+5.722] over 2 contrasts; card-only **+5.0231** [+3.296, +6.750] over 3.

### One convention difference to be aware of

The generalisation report,
[`2026-09-03-strike3-generalisation.md`](../workflow/research/2026-09-03-strike3-generalisation.md),
prints **+20.17** and **+18.50** for the two Alakazam cells, where Figure 2 and the table
above give +20.42 and +18.75. Both are correct under their own convention, and both
reproduce from the same rows:

- the generalisation report counts **wins ÷ all games** (a draw counts as a loss);
- Figure 2 and the current report score **win = 1, draw = ½, loss = 0**.

There are only **12 draws in 8,400 games**, so the two differ by 0.17–0.25 pp. The current
report's convention is the one in force. The report already notes that its panel
convention differs from the development analysis; it does not mention this third
difference, so it is recorded here.

## The three report figures

The report's figures are the exact bytes submitted with it. In this repository they carry
their original packaged names:

| Report figure | File here | SHA-256 |
|---|---|---|
| Figure 1 — source-level decision paths | [`.../03-decision-paths.png`](../workflow/writeup/visuals-2026-09-06/03-decision-paths.png) | `837d6d6738503b2bfe4a376e1429f78e875f09ec906aa31f6074814ef8cadc31` |
| Figure 2 — matchup differences | [`.../01-matchup-evidence.png`](../workflow/writeup/visuals-2026-09-06/01-matchup-evidence.png) | `63e931a10ac99ce58ac0074bc0758b4829847a01988567a4163549f21d713f31` |
| Figure 3 — opponent-mixture sensitivity | [`.../02-mixture-sensitivity.png`](../workflow/writeup/visuals-2026-09-06/02-mixture-sensitivity.png) | `a427d80cc299a9b31af34d257304dea5ad61a8d46aaf8b3c7c1f8de82e935207` |

SVG sources for all three sit beside them. These three hashes match the submitted
`FIGURE-1-DECISION-PATHS.png`, `FIGURE-2-MATCHUP-RESULTS.png` and
`FIGURE-3-OPPONENT-MIX.png` byte for byte.

The seven images in [`figures/`](../figures/) are **historical**: they belong to earlier
drafts, they are not the submitted figures, and no current page links to them. They are
kept because this project does not delete evidence. See
[`figures/README.md`](../figures/README.md).

## Method corrections applied to the supporting pages

[`workflow/knowledge-register/audits/2026-09-06-method-recovery/REVIEW.md`](../workflow/knowledge-register/audits/2026-09-06-method-recovery/REVIEW.md)
is the source-verified audit behind the statistical qualifications in
[What we learned](WHAT-WE-LEARNED.md). Its eighteen supporting records are imported
alongside it, so its internal links resolve from this export.

## What this repository classifies as what

| Class | Where |
|---|---|
| **Current conclusions** | [docs/STRATEGY-WRITEUP.md](STRATEGY-WRITEUP.md), this page, [README](../README.md), [HOW-IT-PLAYS](HOW-IT-PLAYS.md), [WHAT-WE-LEARNED](WHAT-WE-LEARNED.md) |
| **Historical records and superseded drafts** | [docs/historical/](historical/), [figures/](../figures/), `workflow/` registers and ledgers, which retain their original wording and dates |
| **Runnable tools** | `scripts/prior_art.py`, `scripts/retraction_scan.py`, `scripts/retraction_register.py` — see [REPRODUCING](REPRODUCING.md) |
| **Preserved snapshots (not regenerable here)** | `workflow/inventories/sri/` — see [REPRODUCING](REPRODUCING.md#the-inventory-is-a-preserved-snapshot-not-a-rebuild) |
| **Missing external dependencies** | the competition engine and card data; original episode dumps; model weights; `workflow/ARTIFACT-CATALOG.jsonl`; `workflow/curation/labels.csv`; the `D:/ptcg_archive` local archive; the unsquashed Git history |

## Open release questions

A pre-publication scan has now been run and recorded in
**[docs/RELEASE-REVIEW.md](RELEASE-REVIEW.md)** — what was checked, what was found, what
was fixed, and what is still open. It found no credentials, no organiser material and no
third-party kernel source. It is a scan, not a clearance.

Still unresolved, listed rather than asserted as cleared:

- **Five opponent authors named in the published panel have no licence-and-provenance
  row** (`plamen06`, `llccqq624`, `raunakdey07`, `zoli800`, `harukiharada`). See
  [NOTICE](../NOTICE) and the release review.
- **This repository is private.** Judge access has not been demonstrated. Signed-out
  viewing must be verified after any authorised visibility change; that change is not
  made here.
- **A blanket MIT label does not clear every included asset.** The imported verification
  records, the method-recovery audit and the historical registers were authored inside a
  private working repository and have not been individually reviewed for release.
- **Provenance strings retain local paths.** They explain where evidence came from; they
  are not downloadable assets and were not scrubbed, because scrubbing them would break
  provenance. The one credential *location* found has been redacted.
- **No licence audit or automated dependency security scan has been performed.**
