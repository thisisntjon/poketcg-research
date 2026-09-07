# Strike 3 — the product does not generalise; it separates perfectly by archetype

**2026-09-03. 8,400 games, 7 independent third-party opponents × 600 games/arm × 2 arms.**
SKYNET (5080). Analysis pre-registered on the bus at 20:02Z, **before either launch produced a
row**; the estimator and the leave-one-out were fixed in advance.

PRIOR_ART: "opponent-conditioned policy effect heterogeneity out-of-sample generalisation panel composition" -> 3095 hits -> catalog:581ced6056f1182b

Per-game rows: [`2026-09-03-strike3-rows.csv`](2026-09-03-strike3-rows.csv) (8,400 rows).
Replays captured for every game (10 GB, retained off-repo).

## Design

| arm | deck | sha256 | rule |
|---|---|---|---|
| Baseline control | `agent/deck.csv` | `2a541d7bf3d9e6b3` | sniper **OFF** |
| Parent 1 champion | promoted product | `2186cf7be6cf0e99` | sniper **ON** |

The decks differ in exactly the promoted change — **Carmine 4→3, Xerosic 0→1** — asserted by
sha256 in the runner *before game 1*, which aborts on mismatch.

The panel is seven third-party pilots, **none playing our deck**, each competence-screened at
50 games against a neutral referee (`844_router`) before admission.

## Result — generalisation is NOT established

| estimator | clean six (headline) | all seven |
|---|---|---|
| **random effects** | **+2.71pp [−3.22, +8.63]** | **+5.16pp [−1.61, +11.94]** |
| fixed effect | +2.39pp [+0.47, +4.31] | +4.31pp [+2.49, +6.13] |
| Q (df) | 46.32 (5) | 81.74 (6) |
| **I²** | **89.2%** | **92.7%** |

**Both pre-registered headlines contain zero.** The fixed-effect versions exclude zero and are
**not** led with: at I² ≈ 89–93% a fixed-effect pool asserts the cells estimate one common
quantity, and they do not. Choosing the estimator after seeing which clears is precisely the
error the pre-registration existed to prevent.

**+7.82pp does not survive on an independent panel at interval strength.**

## Why — perfect separation on one variable

| cell | Alakazam line? | baseline | champion | Δ | SE |
|---|---|---|---|---|---|
| `llccqq624_marnie` | **yes** (741/742/743) | 36.67 | 56.83 | **+20.17** | 2.82 |
| `raunakdey07` | **yes** (741/742/743) | 20.67 | 39.17 | **+18.50** | 2.59 |
| `plamen06_steel` | no | 32.50 | 33.17 | +0.67 | 2.71 |
| `aristophanivan_snap` | no | 31.00 | 31.33 | +0.33 | 2.67 |
| `zoli800_dragapult` | no | 86.33 | 86.67 | +0.33 | 1.97 |
| `harukiharada` | no | 85.17 | 84.50 | −0.67 | 2.07 |
| `grimmsnarl_bc` | no | 58.67 | 55.83 | −2.83 | 2.86 |

**Two cells carry the targeted archetype and both gain ≈ +19pp. Five do not and all five sit
inside noise of zero. There is no overlap and no intermediate case.** The heterogeneity that
sinks the pooled estimate is not noise — it is this partition.

### The ceiling objection fails

Two null cells sit near ceiling (`zoli800` 86.33%, `harukiharada` 85.17%) and had little room.
**Three did not:** `plamen06_steel` 32.50%, `aristophanivan_snap` 31.00%, `grimmsnarl_bc`
58.67%. All three had ample headroom and returned **+0.67, +0.33 and −2.83**.

**Where there was room to improve against a non-Alakazam opponent, the product did not.**

## What this establishes

The banked in-panel claim — *anti-Alakazam tech, not a better agent* — was inferred from a
development panel that was 40% Alakazam and 40% our own deck. **It now replicates
out-of-sample on seven genuinely independent third-party pilots with perfect archetype
separation.**

That is a stronger result than a diluted panel average: it **explains** the +7.82pp rather
than qualifying it. The development-panel figure is what a 45%-Alakazam panel returns when the
intervention is worth ≈ +19pp against Alakazam and ≈ 0 against everything else.

## Not claimed

- **No comparison to +3.38pp as confirmation.** That target is not recomputable from the
  repository; agreement or disagreement with an uncheckable number is not evidence either way.
- **The clean-six primary is knowingly underpowered** — MDE_RE 3.50pp against a 3.38pp design
  target, accepted on cost grounds. **A clean-six null is therefore not evidence of absence**,
  and the better-powered all-seven figure is the one containing the dev-deck-exposed cell.
- **`llccqq624_marnie` shares a deck** (`0598646548d0`) with dev-panel cell
  `kernel_prvsiyan_alakazam_v12`, byte-identical, different pilot. It is the excluded cell in
  the clean-six headline and is reported as a deck-exposure sensitivity, not dropped.

## Seat split (pooled, 4,200 games per seat)

| seat | baseline | champion | Δ |
|---|---|---|---|
| first | 49.81% | 56.52% | **+6.71pp [+3.70, +9.73]** |
| second | 50.48% | 54.19% | **+3.71pp [+0.70, +6.73]** |

> ### CORRECTED 2026-09-03T21:58Z — "first-seat is larger" is WITHDRAWN, and the decomposition is now run
>
> **An earlier version of this section said "both exclude zero and first-seat is larger."
> That compared two intervals instead of testing their difference, which is not the same
> thing.** The seat **gap** is **+3.00pp, SE 2.18, 95% CI [−1.26, +7.26] — it contains zero.**
> Two positive estimates of different size do not establish a seat effect.
>
> The within-archetype split I called "the defensible version" has now been run, at zero
> further games:
>
> **Every figure in this table counts draws as non-wins**, the convention declared below and
> used throughout this document. 600 games/arm per seat in the Alakazam group, 1,500 in the
> non-Alakazam group, 2,100 pooled.
>
> | group | first | second | seat gap (first − second) |
> |---|---|---|---|
> | **Alakazam cells** (where the effect lives) | +19.17pp | +19.50pp | **−0.33pp [−7.96, +7.29]** |
> | non-Alakazam cells | +1.73pp | −2.60pp | +4.33pp [−0.65, +9.32] |
> | pooled | +6.71pp | +3.71pp | **+3.00pp [−1.26, +7.26]** |
>
> **All three gaps contain zero**, under this convention and under MASTER's independent
> derivation excluding draws. **No seat claim survives at any level of aggregation.**
>
> **In the two cells that carry the effect there is no seat dependence at all (−0.33pp).**
> What pooled seat variation exists sits in the five cells whose treatment effect is ≈ 0, and
> its own interval contains zero too. **Seat advantage does not survive decomposition** —
> banked as GR-61.
>
> **CONVENTION CORRECTED 2026-09-03T22:25Z — and so is my account of the discrepancy.**
> MASTER found that **`eval.py` itself scores a draw as HALF a win** (`origin/main:1271`,
> `score = wins + 0.5*draws` over all games). **Neither of the conventions we had been arguing
> about is the harness's.** Recomputed under the harness convention the Alakazam seat gap is
> **−0.17pp [−7.79, +7.46]** — **exactly MASTER's figure.**
>
> **I had attributed their numbers to "draws excluded" without confirming which convention they
> used.** That inference was wrong, and it was mine to check rather than assume. The seat table
> above is stated under draws-as-non-wins; **under the harness convention it reads
> first +19.50 / second +19.67 / gap −0.17 for the Alakazam cells, and pooled gap +3.00pp
> [−1.26, +7.26] — unchanged.**
>
> **All three gaps contain zero under every convention.** No seat claim survives at any
> aggregation, and nothing here depends on which convention is chosen.

## The within-archetype homogeneity is a LOW-POWER null — read the two halves differently

The Alakazam-conditional pair pools to **+19.26pp [+15.52, +23.00]**, Q = 0.189 on **1 df**,
I² = 0.0%. **That is a failure to detect heterogeneity, not evidence of its absence.** With cell
SEs of 2.82 and 2.59, SE(difference) is 3.83, so **the smallest cell-to-cell difference this
test could detect at 95% is ≈ 7.50pp**; the observed difference is 1.67pp. **I² = 0 here is
compatible with true variation up to roughly ±7.5pp.**

So the central contrast must be read asymmetrically:

| claim | k | df | strength |
|---|---|---|---|
| heterogeneity **across** archetypes (I² = 92.7%) | 7 | 6 | **DEMONSTRATED** (Q = 81.74) |
| homogeneity **within** the archetype (I² = 0.0%) | 2 | 1 | **CONSISTENT WITH**, not demonstrated |

**The replication claim does not depend on I² at all**, which is why it survives this: each cell
excludes zero on its own — **+20.17pp [+14.64, +25.70]** and **+18.50pp [+13.42, +23.58]** — two
opponents with **different pilots and different decks**, each independently showing a large
positive effect. That would stand if Q had come back at 3 or 5.

## Draw convention — stated, and its sensitivity

**Draws are counted as non-wins**: every rate here is `wins / all games`, so a draw scores like
a loss. There are **12 draws in 8,400 games (0.14%)** — all `end_reason UNKNOWN`, both prize
counts zero, mean 190 turns (simultaneous prize-out) — split **4 baseline / 8 champion**, so
this convention is the **conservative** one for the champion arm.

| convention | Alakazam-conditional pooled | clean-six (RE) | within-archetype I² |
|---|---|---|---|
| **draws as non-wins (used)** | **+19.26pp** | **+2.71pp** | **0.0%** |
| draws excluded | +19.50pp | +2.72pp | 0.0% |
| draws as half | +19.51pp | +2.72pp | 0.0% |

**No conclusion depends on the choice**: the archetype separation, the I² = 0 versus ≈ 89%
contrast, and the clean-six null are identical under all three.

### The harness has its own convention and it is neither of ours — added 22:25Z

**MASTER found that `eval.py` scores a draw as HALF a win** — `score = wins + 0.5 * draws`,
over `wins + losses + draws`, at **`origin/main:1271`**.

*(Cited against `origin/main`, not against a worktree. My first version of this note said
`:1199`, which is the line in my scratch tree — behind main, so the citation would not have
resolved for any reader. A line number is only meaningful with the ref it belongs to.)* **So the third row of that table is
the harness's own convention, and the row this document computed in is not.**

**Under the harness convention, for the record:**

| quantity | draws as non-wins (this doc) | **harness (draws = ½)** |
|---|---|---|
| Alakazam-conditional pooled | +19.26pp [+15.52, +23.00] | **+19.51pp [+15.77, +23.25]** |
| clean six (RE) | +2.71pp [−3.22, +8.63] | **+2.72pp [−3.29, +8.74]** |
| all seven (RE) | +5.16pp [−1.61, +11.94] | **+5.21pp [−1.66, +12.08]** |
| within-archetype I² | 0.0% (Q = 0.19) | **0.0% (Q = 0.19)** |
| detection floor | 7.50pp | **7.51pp** |
| Alakazam seat gap | −0.33pp | **−0.17pp** |
| pooled seat gap | +3.00pp | **+3.00pp** |

**Every conclusion is identical.** The clean-six headline contains zero under both; the
archetype separation is unchanged; no seat gap excludes zero under either.

**Switching to the harness convention is principled rather than post-hoc** — it is the
convention the instrument that produced these artifacts reports, so a reader cross-checking any
figure against an `eval.py` summary should not find a mismatch. **A future analysis of this data
should use draws = ½ and say so.**

*(The original omission was found by MASTER's independent recompute. **I then attributed their
figures to "draws excluded" without confirming it** — that inference was wrong: their −0.17pp
seat gap matches the harness convention exactly. Attributing a convention to another seat's
numbers instead of asking is the same class of error as leaving my own unstated.)*

## Validity

**4,200 of 4,200 decided in both arms, ZERO errors, rc 0/0.** Replays captured for all 8,400
games. One tree, so agent bytes are identical across arms by construction; only the deck and one
environment flag differ.

`grimmsnarl_bc` was addressed through a `tb_`-named bridge alias while `#3283` was unmerged;
the alias is documented by **policy sha256 `f2e2c18d5057`** and **deck sha256 `92b92bac9f91`**.
`#3283` has since merged, so the canonical `nb_` name is addressable and the bridge retires.

An earlier launch of this trial was killed at 688 games/arm because it omitted `--replays`,
breaching the standing replay fence; those games were discarded and are not part of this result.

Research artifacts only. No agent bytes, no harness code. **Needs a non-author to merge.**
