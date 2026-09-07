# Xerosic × Sniper — an INDEPENDENTLY REPRODUCED improvement (2026-09-03, SKYNET)

**The first candidate in this project's history to survive a concurrent replicate.**

Every estimate here is built from **within-batch** contrasts — each treatment against a
control launched in the same minute. **No win rate is ever compared across batches**, because
the control arms themselves moved 35.77% → 33.73% → 34.32% → 35.10% across the four batches
below: the τ≈1.18pp between-batch effect, visible and cancelled by design rather than
assumed away.

Where several batches measure the same contrast, they are **combined as a fixed-effect pool
of those within-batch deltas** (inverse-variance weighted, with Cochran Q reported so
disagreement between batches is visible rather than averaged away). That is a different
operation from pooling raw rates across batches, which would be wrong here.

Denominator is **decided games** everywhere. Rows: `2026-09-03-xerosic-sniper-rows.csv`
(**24,000, one per game — this bank**). Full `games.jsonl` artifacts are pinned by sha256 in
`2026-09-03-artifact-manifest.json`.

**The independent 4070 reproduction's 4,000 games are NOT in this CSV** — they are MASTER's
and are banked by MASTER. The combined `D−A` below therefore draws on **28,000 games across
two banks**, while the rows committed *here* are 24,000. Said explicitly because a headline
count that silently includes someone else's rows is exactly the kind of number that cannot
be recomputed from the artifact carrying it.

## Headline

| lever | batches | combined | 95% CI | Cochran Q |
|---|---|---|---|---|
| Xerosic ×1 (deck mutation, no agent bytes) | 3 | **+5.03pp** | [+3.30, +6.75] | 2.28 / 2 df — agree |
| `RULE_ALAKAZAM_SNIPER` (code, default OFF) | 2 | **+3.62pp** | [+1.52, +5.72] | 0.24 / 1 df — agree |
| **Combined product (both)** | **3, on 2 boxes** | **+7.82pp** | [+6.08, +9.56] | 1.50 / 2 df — agree |

> ### SCOPE — added 2026-09-03T21:15Z. Read before quoting the number.
>
> **+7.82pp is a DEVELOPMENT-PANEL figure and it does NOT generalise.** Strike 3 measured this
> same product against **seven independent third-party opponents** (8,400 games, 0 errors) and
> the pre-registered headline came back **+2.71pp [−3.22, +8.63] — containing zero.**
>
> The reason is that the effect **separates by archetype**. The two opponents carrying the
> Alakazam line returned **+20.17pp** and **+18.50pp**, each excluding zero on its own; the five
> that did not returned **+0.67, +0.33, +0.33, −0.67, −2.83**. **Not a ceiling artefact** —
> three of those five nulls had baselines of 31–59%, with ample room to improve.
>
> **So +7.82pp is what a ~40%-Alakazam panel returns when the intervention is worth ≈ +19pp
> against one archetype and ≈ 0 against the rest.** It is correct as a panel measurement and
> **wrong as a claim about the agent.** Quote it only with its panel composition attached.
>
> Full result, rows and caveats: `2026-09-03-strike3-generalisation.md`.

### INDEPENDENTLY REPRODUCED — quote +7.82pp, not +8.26 or +9.35

**MASTER reproduced it on the 4070** — hardware nobody who produced the original screens had
touched, run by a seat that ran none of them, against a criterion fixed before they saw a
number: **+6.94pp [+3.93, +9.94]**, 4,000 games, 0 errors, both arms rc=0.

| batch | box | `D−A` | 95% CI |
|---|---|---|---|
| factorial | 5080 | +9.35pp | [+6.33, +12.37] |
| replicate | 5080 | +7.17pp | [+4.15, +10.19] |
| independent reproduction | **4070** | +6.94pp | [+3.94, +9.94] |
| **combined, 12,000 games** | both | **+7.82pp** | **[+6.08, +9.56]** |

Cochran Q = **1.50 on 2 df** (threshold 5.99) — the three agree.

**Box check**, the whole reason to run elsewhere: 5080 pooled **+8.26** (SE 1.09) vs 4070
**+6.94** (SE 1.53) → difference **−1.32pp, 95% CI [−5.00, +2.36]**: **no detectable box
effect.** *"No detectable" is not "none"* — at SE ≈1.9pp this rules out a large box effect,
not one below ~2.6pp.

**Read it as MASTER did, not more warmly.** +6.94 sits *below* +9.35 and its interval
overlaps the earlier band without being contained by it. **The effect travels; this design
cannot separate +6.94 from +9.35.** Citing the reproduction as confirming +9.35
specifically is overreading it.

**Superseded — do not quote again:** `+9.35pp` (one batch, one box) and `+8.26pp` (two
batches, one box). This number moved **down because the evidence got better**.

**Unchanged by the reproduction:** the panel is 40% Alakazam and the gain concentrates
there — MASTER measured alakazam_v8 **+18.50pp**, alakazam_v12 **+13.65pp**, the mechanism
holding exactly as pre-registered. **An independent reproduction makes the effect real; it
does not make it general.** See the ladder-weighting section.

The combined product's `D−A` was **+9.35pp on one batch**, flagged in the terminal receipt
as single-batch and therefore a candidate. **The replicate reproduced it: +7.17pp
[+4.16, +10.18]**, satisfying the criterion fixed before that run (positive point estimate,
interval overlapping the factorial's). I also predicted before launch that it would land
**lower**, in +6..+9, because +9.35 was the largest contrast of the night and drew attention
for being large. It landed at +7.17.

**Combined `D−A` per opponent, 8,000 games:**

| opponent | plays Alakazam | combined `D−A` | 95% CI | Q (1 df) |
|---|---|---|---|---|
| `prvsiyan_alakazam_v12` | yes ×4 | **+22.96pp** | [+18.22, +27.69] | 1.71 |
| `prvsiyan_alakazam_v8` | yes ×4 | **+20.41pp** | [+16.33, +24.49] | 0.08 |
| `844_router` | no | +1.95pp | [−2.71, +6.61] | **4.86** |
| `romanrozen_v13` | no | −0.93pp | [−5.82, +3.96] | 0.10 |
| `aristophanivan_940` | no | −2.77pp | [−7.61, +2.08] | **6.24** |

## The per-cell floor we have all been reading is the wrong floor

**Stated as an observation that needs its own measurement, not as an established number.**

The replicate alone showed `aristophanivan_940` at **−9.00pp** — outside the 5.26pp
envelope, and under the pre-registration that is a reportable **harm**. Combined across
both batches it is **−2.77pp with an interval containing zero**. It was not harm. It was
one cell moving in one batch, **and it would have been reported as harm had that batch been
run alone.**

Two of the five cells show between-batch heterogeneity beyond chance (Q = 6.24 and 4.86 vs
a 3.84 threshold). The clearest way to see it is the **unchanged baseline arm** on the same
opponent across the two batches:

```
aristophanivan_940   arm A: 39.75%  ->  51.50%   (+11.75pp)
844_router           arm A: 39.75%  ->  29.00%   (-10.75pp)
```
Binomial SE for such a difference at n=400/cell is ≈3.5pp, so each is roughly **3σ** in an
arm that did not change.

**The 5.26pp envelope was measured WITHIN a batch** (an A/A with both arms launched
together), yet single-batch per-cell rows have been read against that within-batch floor
all night, including by me.

### Amendment — I first stated this too broadly, then measured it

**The first version of this section claimed that cross-batch "a single cell evidently moves
much further", as a general property. That is wrong. The correction is recorded here rather
than silently applied, because the overstated version was posted to the bus and another seat
amended a fence on the strength of it.**

Three arms run tonight are the **same configuration in three separate batches** —
`sniper_screen1 OFF`, `factorial A_baseline`, `combined_rep A_baseline`, same tree, same
deck `2a541d7bf3d9`, rule OFF. That is a cross-batch A/A/A already on disk, costing
**0 new games**:

| opponent | b1 | b2 | b3 | spread | ≈σ |
|---|---|---|---|---|---|
| `aristophanivan_940` | 45.00 | 39.75 | 51.50 | **11.75pp** | 3.3 |
| `844_router` | 32.75 | 39.75 | 29.00 | **10.75pp** | 3.2 |
| `alakazam_v12` | 32.25 | 30.83 | 34.50 | 3.67pp | 1.1 |
| `alakazam_v8` | 14.00 | 13.25 | 14.79 | **1.54pp** | 0.6 |
| `romanrozen_v13` | 46.62 | 48.00 | 45.73 | 2.27pp | 0.6 |

A second triad (the two xerosic controls, on a byte-different `rules_lucario`) gives spreads
of 2.50 / 5.00 / 5.59 / 3.25 / 5.29pp — **largest ratio 1.66σ, no excess variance anywhere.**

**So cells do not wander across batches. Two of five opponents are unstable; three are
steady** — `alakazam_v8` reads 14.00 / 13.25 / 14.79 across three separate batches. With
five opponents, a max-over-cells statistic, and a second triad showing nothing, the status
is **unresolved and concentrated — not a general property of the floor.**

### Second amendment — the instability claim is WITHDRAWN

**Even the narrowed version above does not survive. Recorded here because another seat had
already amended a fence on it.**

The flagged cells came from a **k=3** group compared against **k=2** groups, which have one
pairwise comparison each and could not have disagreed. I ran a third batch of the closures
configuration (2,000 games, config sha-asserted identical, rc=0, 0 errors) so **both groups
are k=3** and Cochran Q is read at the same df and threshold (5.99):

| opponent | sniper triad Q | closures triad Q |
|---|---|---|
| `aristophanivan_940` | **11.31** | 1.83 |
| `844_router` | **10.56** | 2.73 |
| `alakazam_v12` | 1.24 | 2.79 |
| `alakazam_v8` | 0.39 | 3.60 |
| `romanrozen_v13` | 0.42 | 2.35 |

**The closures triad flags nothing**, and the two accused opponents are among its quietest
(45.00 / 47.50 / 42.75 and 35.25 / 30.25 / 30.75).

**H1 is not reproduced. "These two opponents are unstable across batches" is withdrawn.**
What survives: one batch set showed excess spread in two cells that did not reproduce in a
second set at equal power. That is a property of *those batches*. **The cause is
unidentified and I am not inventing one** — the two configurations differ only by dead code,
and 2 flags in 10 tests at p<0.05 is close to what chance produces.

**Still standing, because it never depended on the withdrawn story:** a single-batch
per-cell harm flag is not sufficient to declare harm. The −9.00pp cell dissolved to −2.77pp
whatever caused it.

Consequences, limited to what actually follows:
- **Pooled contrasts are unaffected**: they are within-batch by construction.
- **The Alakazam cells are unaffected**, and are among the *most stable* cells measured:
  Q = 0.08 and 1.71 on `D−A`, spreads of 1.54pp and 3.67pp across three batches.
- **The operational rule stands**: a single-batch per-cell harm flag is not sufficient to
  declare harm — the cell that faked −9.00pp is one of the two unstable ones.
- **Do NOT widen 5.26pp for everyone.** That would also erase the genuine precision of the
  +20pp Alakazam cells. Flag `aristophanivan_940` and `844_router` as unstable instead.
- The clean answer still needs an A/A run as two *deliberately separated* batches
  (4,000 games). This triad is a sighting shot, not that measurement.

## What the levers are

- **Xerosic's Machinations (card 1197)** — 1 copy in, 1 Carmine (1192) out, still 60 cards.
  The card was **already named in `rules_lucario.py:69` and absent from the shipped
  `deck.csv`**. `main.py:781` intercepts the deck declaration and returns
  `read_deck_csv()`, so `deck.csv` ships and `rules_lucario.my_deck` is dead code —
  verified, not assumed. **No agent bytes are modified by this lever.**
- **`RULE_ALAKAZAM_SNIPER`** (STRATEGIST) — a target-selection bonus of +4000 on benched
  Abra/Kadabra, seated below the KO rung (+100000) and the game-ending rung (50000) so it
  reorders only non-lethal targets. Default OFF; flipped per-arm by `PTCG_ALAKAZAM_SNIPER=1`.

## The mechanism, found before the games

Alakazam's attack **Powerful Hand** places 2 damage counters per card in the attacker's
hand for one Psychic energy. Xerosic caps the opponent's hand at 3. STRATEGIST's trace
census on 400 games measured the opportunity side: a benched Abra or Kadabra is present
during our turn 2–4 decisions in **95.8%** of games, we hold Boss's Orders at the same
time in **63.5%**, and the Alakazam line completes in **92.0%**.

For contrast, the two levers this project retired the same week fired **0.000** and
**0.00** times per game. Dose was the discriminator, and it was measured at zero games.

## Results

### Xerosic ×1, three independent batches

| batch | control | variant | Δ | 95% CI |
|---|---|---|---|---|
| screen 1 | 35.77% | 40.62% | +4.85pp | [+1.84, +7.86] |
| replicate | 33.73% | 40.46% | +6.73pp | [+3.74, +9.72] |
| factorial `C−A` | 34.32% | 37.82% | +3.50pp | [+0.53, +6.48] |

The earlier two-batch figure of +5.80pp was **revised down to +5.03pp** when the third
batch landed lower. Recorded here because the friendlier number was posted first.

### The 2×2 factorial (8,000 games, one batch, four arms)

```
A  shipped deck, rule OFF     B  shipped deck, rule ON
C  xerosic deck, rule OFF     D  xerosic deck, rule ON
```
`rules_lucario.py` and `main.py` byte-identical across all four arms; only `deck.csv` and
one env var vary. All four flag states proven inside a child process **before game 1**.

| contrast | Δ | 95% CI |
|---|---|---|
| `B−A` sniper alone | +4.14pp | [+1.16, +7.12] |
| `C−A` xerosic alone | +3.50pp | [+0.53, +6.48] |
| `D−A` both | +9.35pp | [+6.34, +12.36] |
| `D−C` sniper on top of xerosic | **+5.85pp** | [+2.80, +8.89] |

Per-opponent, A → D:

| opponent | plays Alakazam | A | D |
|---|---|---|---|
| `prvsiyan_alakazam_v8` | yes (×4) | 13.25% | **34.25%** |
| `prvsiyan_alakazam_v12` | yes (×4) | 30.83% | **56.89%** |
| `aristophanivan_940` | no | 39.75% | 43.11% |
| `romanrozen_v13` | no | 48.00% | 47.87% |
| `844_router` | no | 39.75% | 36.25% |

**Harm channel in THIS batch: none** — no opponent at any treatment arm is worse than
−5.26pp vs baseline. The replicate batch *did* show one cell at −9.00pp; combined across
both batches it is −2.77pp with an interval containing zero. See the cross-batch section
above, and note that a single batch was not enough to tell those two situations apart.

## The headline is a PANEL number, and the panel is 40% Alakazam + 40% MIRROR

> **This section's arithmetic was computed on the TWO-batch 5080 figure, `+8.26pp`, which is
> SUPERSEDED by `+7.82pp` (three batches, two boxes) — see the headline. The re-weighting
> below is still correct FOR ITS OWN DATA (the 8,000 factorial + replicate rows) and the
> shape of the conclusion is unchanged, but `+8.26pp` must not be read here as the current
> result.** Left as computed rather than silently rescaled, because rewriting a number that
> was measured on one dataset to look like it came from another is worse than a stale label.
>
> **Sharper composition, verified from the registry after this section was written:**
> `aristophanivan_940` and `romanrozen_v13` **both play `deck.csv = 2a541d7b` — our own
> control deck.** So the panel is **40% Alakazam · 40% mirror of ourselves · 20% mill**. On
> the two mirror cells we changed our deck and the opponent did not, and got **+3.36 and
> −0.13** — inside the envelope. **That is the mechanism behind the concentration: the
> product is anti-Alakazam TECH, not a deck improvement.**

**This qualification is load-bearing and it was missing from the first version of this
document.** "No opponent is harmed beyond the envelope" is true, and it is a much weaker
statement than "the product is free elsewhere." **It is not free.**

Combined `D−A` across both batches, per opponent:

| opponent | plays Alakazam | A | D | Δ |
|---|---|---|---|---|
| `prvsiyan_alakazam_v12` | yes | 32.67% | 55.57% | **+22.90** |
| `prvsiyan_alakazam_v8` | yes | 14.02% | 34.42% | **+20.40** |
| `844_router` | no | 34.38% | 36.12% | +1.75 |
| `romanrozen_v13` | no | 46.87% | 45.93% | **−0.93** |
| `aristophanivan_940` | no | 45.62% | 42.80% | **−2.82** |

Mean Δ on the two Alakazam kernels **+21.65pp**; mean Δ on the other three **−0.67pp**.

The panel gives each kernel 1/5, so it implies a **40% Alakazam ladder**. Re-weighting:

| assumed ladder Alakazam share | expected gain |
|---|---|
| 40% (what the panel implies) | **+8.26pp** |
| 30% | +6.03pp |
| 20% | +3.80pp |
| 10% | +1.56pp |
| 5% | +0.45pp |
| 0% | **−0.67pp** |

**On a ladder with no Alakazam this product is slightly WORSE than what we ship today.**
The pooled headline is a counter to one archetype that happens to occupy 40% of our test
panel — **panel fitness is not ladder Elo**, and the honest reading of `+8.26pp` is
"+21.65pp against Alakazam, ~flat-to-negative against everything else we have measured."

Consequence for the next cycle: the ladder-weighted value sits in the **non-Alakazam**
cells, not in squeezing more out of an archetype already moved +21.65pp. (Note this is the
right reason to go there — `alakazam_v8` at 34.42% is still our single worst matchup, ahead
of `844_router` at 36.12%, so "go where the worst cell is" would point back at Alakazam.)

## The promotion rule, and a prediction that was refuted

Jon's rule (02:39Z): `D − A ≥ (C − A) + 1.5pp` → CASE 1 promote combined; else CASE 2
promote the deck alone. **Locked at 02:41:52Z with the arm counts stamped and no arm read.**

Before the terminal I flagged that the rule simplifies to `D − C ≥ 1.5pp` and that
`SE(D−C) ≈ 1.58pp` — **the threshold sits under one standard error of the quantity it
thresholds**, so a boundary result would have been a coin flip. It did not land near the
boundary: `D−C = +5.85pp` with a lower bound of **+2.80**, so the verdict is **CASE 1,
RESOLVED at this n**.

**I pre-registered SUB-ADDITIVITY — that these two levers were largely redundant — and the
data refutes it.** They add. The textbook interaction is +1.71pp against a ~3pp SE, so the
correct word is **additive, not synergistic**.

## Read against the measured noise floor

A same-agent A/A on this panel (4,000 games) gave pooled **+1.63pp, CI [−1.30, +4.57]**,
per-opponent envelope **max |Δ| 5.26pp**, pooled SE 1.50pp. The A/A **would have failed**
the lower-bound-above-zero bar. The two Alakazam cells here are 2–5× the largest excursion
the A/A produced.

## Known limitation, and it is upside

`rules_lucario.py:705` scores any trainer without an explicit case at **10000**. Xerosic
has no case. **`rules_lucario.py:743` scores Carmine at 3000**, and `all_card_data()` gives
`cardType=3` (Supporter) for both — one supporter per turn.

**So Xerosic outranks our own primary draw supporter more than 3:1 and takes the slot every
turn it is in hand, regardless of the opponent's hand size.** Every number in this document
was measured with that happening. **That displacement is real and was later measured at
~0.95 plays per game.**

> **RETRACTED 2026-09-03 14:05Z — both claims in the next sentence are refuted. Kept visible
> rather than deleted so the supersession is auditable.**
>
> ~~*The banked figures are a floor, not a ceiling, and a hand-size gate is untested upside.*~~
>
> **Neither holds. TWO independent gates tried to reclaim the supporter slot and both failed:**
> the **hand-size gate is INERT** (0 fires in 900 games — the opponent is never under 4 when
> Xerosic is playable), and the **Carmine-conflict gate is HARMFUL** (pooled-3 −3.55pp
> [−7.51, +0.41], four of five cells down, banked in `#3264`).
>
> **So the lockout is real and is NOT a loss — it is what the product is buying.** Xerosic is
> not worthless against non-Alakazam decks: its disruption outvalues the draw it displaces
> even where there is no Powerful Hand to blunt. **Do not quote +7.82pp as a floor.**
>
> The reusable error: *verifying that a lever CAN act is not evidence that acting HELPS.*

Corollary prediction, recorded before the run exists: **×2 Xerosic may be WORSE than ×1
under the current scorer**, because a second copy steals a second supporter turn. That a
competitor kernel (`prvsiyan_844_router/main.py:110`, `_ARCHIVE_DECK`) runs ×4 is not
evidence against this — it scores its own plays differently.

## Two more runs are in the rows but were missing from this prose

**Both are banked in the CSV and both were described only in a commit message — which
squash-merge discards. Written into the file so the caveats survive with the numbers.**

### `RULE_XEROSIC_CONDITIONAL` (Jon IMPERATIVE 4) — NULL, and NOT closed

The hand-size gate — fire Xerosic only when the opponent holds ≥4 cards — measures
**−0.59pp, 95% CI [−3.66, +2.48]** over 4,000 games. Every per-opponent cell inside the
5.26pp envelope. 0 errors, both arms proven in child processes before game 1, both arms the
promoted product with only `PTCG_XEROSIC_CONDITIONAL` differing.

**I called this "the cheapest untested upside on the board" after verifying its mechanism in
code** (Xerosic scores 10000, Carmine 3000, both Supporters, one per turn).
**Verifying that a lever CAN act is not evidence that acting HELPS.** The mechanism is real;
the inference from it was not.

**Reported as "no detectable effect at ×1, dose unmeasured" — NOT as closed.** I did not
measure dose before spending 4,000 games. The deck runs ×1 Xerosic in 60 and the gate only
fires when it is in hand *and* the opponent is under 4 cards. **If that state is rare this is
a CANNOT-ACT null, not a DOES-NOT-HELP null**, and those are different findings. A zero-game
instrumented fire-count settles which.

### Sealed holdout audit (Jon TRACK 2) — NON-INFERIORITY, not superiority

Against `kernel_prvsiyan_control_v11_portfolio`, a lineage no screen touched: baseline
345-655 = **34.50%**, Parent 1 381-619 = **38.10%**, **Δ +3.60pp [−0.61, +7.81]**, 2,000
games, 0 errors.

**The superiority bar (pooled lower bound > 0) is NOT met.** What the run establishes is that
meaningful harm is excluded — worst case **−0.61pp** against a 5.26pp envelope. That is what
"zero negative transfer" actually asks, and it is a weaker, truer claim than "it also wins on
unseen decks."

**`+3.60pp` MUST NOT be quoted as an effect size.** At 1,000/arm the SE is **2.15pp** — enough
to clear a 5-point non-inferiority margin, not enough to resolve a 3-point gain.

**Track 2 has ONE sealed holdout, not two.** `prvsiyan_rmy_grimmsnarl_hybrid` is extractable
(base64 `PAYLOADS`, not `%%writefile`) but **not runnable**: its runtime needs a `model.pt`
that is not in the payloads and exists nowhere in the repository. **Extractable ≠ runnable —
do not build a PAYLOADS extractor expecting a second archetype.**

## Where the arm decks actually live — read this before reproducing

**This document records the two arm decks by sha256 and NOT by content, and that is a
reproducibility defect.** A hash lets a reader *verify* a deck they already hold; it does
not let them *produce* one. MASTER hit this while attempting the 4070 reproduction and had
to reconstruct a 60-card list by trying plausible edits and keeping the one that hashed
right. That worked, and it should not have been necessary.

The bytes are banked by STRATEGIST rather than duplicated here — one copy, one owner:

```
workflow/research/2026-09-03-panel-improvement/arms/control.deck.csv   sha 2a541d7bf3d9…
workflow/research/2026-09-03-panel-improvement/arms/variant.deck.csv   sha 2186cf7be6cf…
workflow/research/2026-09-03-panel-improvement/arms/ARMS-MANIFEST.json
```

**Verified here, not assumed:** both files were extracted from that branch and hashed, and
they match the two arm decks used by **every run in this document** — `2a541d7bf3d9` is the
control / `A` / `OFF` deck, `2186cf7be6cf` the variant / `C` / `D` deck. The entire
24,000-game bank rests on exactly those two 60-card lists.

**Dependency:** those files arrive with PR #3216. Until it merges, a reproducer needs
`git fetch origin pull/3216/head` to reach them.

**The general rule this cost us:** a bank that records an artifact's hash but not its bytes
is only reproducible by someone who already has the artifact. Bank the bytes, or name
exactly where the bytes are banked.

## Provenance

Pre-registrations written before each run:
`D:/ptcg_strategist/scratch/{xerosic,factorial}/PREREG.md` and
`factorial/PREREG-ADDENDUM-promotion-rule.md`.

All twelve arms: `rc=0`, **0 errors**, ≥99.8% of requested games, `--per-game-isolation`,
`--allow-random-fallback` never passed. Bus receipts: #3132 comments 5519343961,
5519368319, 5519460710, 5519541875, 5519563417.

**The banked CSV reproduces all seven reported contrasts to within 0.02pp**, checked from
the CSV alone without reading the source jsonl.
