# Evidence map for the current report

References **[1]–[7]** match [From Research Agents to Better Pokémon TCG Decisions](STRATEGY-WRITEUP.md). The current [report PDF](downloads/FINAL-REPORT.pdf), [guide](downloads/EVIDENCE-GUIDE.pdf), and [evidence ZIP](downloads/PTCG-EVIDENCE.zip) are available together.

| Reference | What it supports | Source |
|---|---|---|
| 1 | Submitted public product and September 6 score | [Provenance](../workflow/research/owned-learning-roadmap-20260813/lane-s-c61-provenance-receipt.json), [score](../workflow/writeup/visuals-2026-09-06/COMPETITION-VERIFICATION.json) |
| 2 | Implemented experimental learner, legal choices, STOP and teacher interface | [Source excerpts and their hashes](learner-evidence/README.md) |
| 3 | Earlier August student checkpoint evaluation | [Learning verification](../workflow/writeup/visuals-2026-09-06/LEARNING-VERIFICATION.json), [training](../workflow/writeup/visuals-2026-09-06/learning-evidence/training-receipt.json), [games](../workflow/writeup/visuals-2026-09-06/learning-evidence/screen-receipt.json) |
| 4 | Submitted deck and game mechanics | [Recovered-source verification](../workflow/writeup/visuals-2026-09-06/SOURCE-VERIFICATION.json); the ZIP's SOURCE-NOTES.md also records the Mega Lucario ex card-678 mechanics read |
| 5 | Card/targeting factorial and replication | [Experiment](../workflow/research/2026-09-03-xerosic-sniper-factorial.md), [ablation arithmetic](../workflow/writeup/visuals-2026-09-06/ABLATION-VERIFICATION.json) |
| 6 | Seven-opponent evaluation and mixture calculation | [8,400 game rows](../workflow/research/2026-09-03-strike3-rows.csv), [cell estimates and variances](../workflow/writeup/visuals-2026-09-06/counterplay-data.json) |
| 7 | Research records and continuing learning architecture | [Research-memory interface](../workflow/knowledge-register/README.md), [architecture excerpt](learner-evidence/architecture.md.excerpt.txt) |

The v2 excerpts describe implementation. The historical August student's game result evaluates its named checkpoint, and the Lucario counter evaluates a separate rules-pilot branch. A completed autonomous improvement cycle is a continuing objective. The guide describes coverage and missing dependencies; hashes identify the source bytes rather than certifying every claim.

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

## The current report figures

The current figures are supplied with the revised article. Earlier figures under workflow/writeup/visuals-2026-09-06/ remain historical evidence. The underlying seven-opponent data are unchanged.

- Figure 1: [01-meaningful-choices.png](current-figures/01-meaningful-choices.png); SHA-256 `2f9979a7d19629d3615cfb16cf4307e7c79a72e1871e210ef586d933b9438f67`.
- Figure 2: [02-matchup-results.png](current-figures/02-matchup-results.png); SHA-256 `707015722b5579a51a7def76d284fe4f6228a274e13abae223381a6b90e85061`.
- Figure 3: [03-opponent-mixture.png](current-figures/03-opponent-mixture.png); SHA-256 `eb7cfb4c39719ba9a3e9b1a7a0ce8c94c3c86efdf99d721c6f63824edd9c8424`.

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
- **Public visibility.** GitHub reports this repository as public as of September 8, 2026. Downloadable evidence and source routes are linked above.
- **A blanket MIT label does not clear every included asset.** The imported verification
  records, the method-recovery audit and the historical registers were authored inside a
  private working repository and have not been individually reviewed for release.
- **Provenance strings retain local paths.** They explain where evidence came from; they
  are not downloadable assets and were not scrubbed, because scrubbing them would break
  provenance. The one credential *location* found has been redacted.
- **No licence audit or automated dependency security scan has been performed.**
