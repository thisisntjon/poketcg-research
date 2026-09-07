# For researchers working on similar problems

If you are building or evaluating a game-playing agent, this page is the honest inventory
of what you can take from here — and what you cannot. It is ordered by how reusable each
thing actually is, not by how much work it took us.

## 1. The data — 44,400 game records you can re-analyse today

Two CSVs, one row per completed game, no engine required.

| File | Rows | What it is |
|---|---|---|
| [`2026-09-03-strike3-rows.csv`](../workflow/research/2026-09-03-strike3-rows.csv) | 8,400 | Seven opponent implementations × 600 games × 2 arms. The generalisation panel. |
| [`2026-09-03-xerosic-sniper-rows.csv`](../workflow/research/2026-09-03-xerosic-sniper-rows.csv) | 36,000 | Nine development runs, including a full 2×2 factorial at 2,000 games/arm. |

**The two files do not share a schema.** That is the first thing to trip over.

### Columns present in both

| Column | Values | Notes |
|---|---|---|
| `outcome` | `win`, `loss`, `draw` | **This is the result field. Use it.** |
| `arm` | see below | Treatment label, meaningful only within its run. |
| `opponent` | 6 distinct (dev), 7 distinct (panel) | Opponent implementation identity. |
| `seat` | `first`, `second` | Exactly balanced 50/50 in both files. |
| `turns` | 10–222 (dev), 11–261 (panel) | Game length. |
| `end_reason` | `PRIZES`, `DECKOUT`, `NO_BENCH`, `UNKNOWN` | How the game ended. `UNKNOWN` co-occurs with every `draw`. |
| `game_index` | 0-based within cell | Not a global id. |

### Development file only

`prize_margin` (−5…+6), `prize_taken_by_candidate`, `prize_taken_by_opponent` (0–6 each),
`error` (empty in all 36,000 rows).

### Panel file only

`candidate_prize_remaining`, `opponent_prize_remaining` (0–6 each). Note this is
*remaining*, the inverse sense of the development file's *taken*. Do not join the two
files on prize columns without converting.

### Run → arm map (development file)

```
factorial            A_baseline, B_sniper, C_xerosic, D_both   <- the 2x2, 2000/arm
combined_replicate   A_baseline, D_both
xerosic_screen1      control, variant
xerosic_replicate    control, variant
sniper_screen1       OFF, ON
carmine_gate         OFF, ON
xerosic_gate         OFF_blind, ON_gated
sealed_holdout       BASELINE, PARENT1
aa_third_closures    batch3            <- single arm, an A/A closure, not a contrast
```

### Two conventions that will change your answer

Draws are rare (34 in 36,000; 12 in 8,400) but the convention is not free:

- **win = 1, draw = ½, loss = 0** — used by the current report and its Figure 2.
- **wins ÷ decided games** (draws dropped) — used by the development analysis.
- **wins ÷ all games** (draw counts as a loss) — used by the generalisation report.

All three appear in this repository on the same data and they differ by up to 0.25 pp.
[EVIDENCE-MAP](EVIDENCE-MAP.md#one-convention-difference-to-be-aware-of) reconciles them.
Pick one and say which.

## 2. The statistical methods — the most transferable thing here

- **[`workflow/canon/EQUATIONS.md`](../workflow/canon/EQUATIONS.md)** — a TrueSkill rating
  model fitted on 9,483,374 rows (R² = 0.999997), with the μ↔win-probability conversion and
  **three different b-curves for three different questions**, each with an explicit
  approval status. If you are working in any TrueSkill-rated competition, this is probably
  the single most reusable file in the repository. Note the retired Elo-400 conversion: the
  real constant was 217.55, which made targets ~25% harder than the naive estimate.
- **[`workflow/canon/MEASURED-2026-08-06.md`](../workflow/canon/MEASURED-2026-08-06.md)** —
  measured noise floors and the sizing arithmetic that follows from them.
- **[`.../2026-09-06-method-recovery/REVIEW.md`](../workflow/knowledge-register/audits/2026-09-06-method-recovery/REVIEW.md)**
  — the audit that found our own sizing rules were partly unsupported. Read it *with* the
  two files above; it is the correction to them. Its 18 supporting records are included, so
  its internal links resolve.

Both of the first two are written in plain terms and need no context from this project.

## 3. The negative results — what we closed, and what that does *not* prove

**[`workflow/DEAD-ENDS.md`](../workflow/DEAD-ENDS.md)** is the file we would most want
another team to read. Every closed line carries an explicit **scope guard**: the claim the
evidence supports, and the claim it does not. Example: a search agent lost 24–0 to its own
fallback, and the row states that this may be cited *only* as "this implementation, as
enabled, loses to its own fallback" — never as evidence against search as a class, because
both of our negative search results used a weak position evaluator.

The transferable idea is the scope guard itself. A dead-end register that overstates its
negatives closes doors that were never shut, and that failure is invisible.

## 4. The instrument failures — highest value, hardest to read

**[`workflow/ATTEMPTS-LEDGER.md`](../workflow/ATTEMPTS-LEDGER.md)** catalogues ten
measurement tools that each produced at least one confident, wrong verdict before we caught
them. That catalogue is, in our view, the most original thing this project produced.

**It is also the least readable file here** — roughly 0.7 internal references per line
(ticket ids, seat names, PR numbers). See the decoder below. If you want the findings
without the archaeology, [WHAT-WE-LEARNED](WHAT-WE-LEARNED.md) states the four most
important ones in plain language, and it is written for an outside reader.

## 5. Decoding the internal references

This repository is an export of a working repository that ran with several agents and its
own vocabulary. When you hit these:

| You see | It means | Can you follow it? |
|---|---|---|
| `#1897`, `#3289` | A pull request or issue in the private working repository | **No.** Private. Treat as an unresolvable citation. |
| `SK-294`, `GR-91`, `GO-6` | An internal work item id | No, but the row usually restates the finding. |
| `seq-113` | A numbered internal ruling | No. |
| `SKYNET`, `MISTY`, `ROACH`, `ASTRA`, `MASTER`, `STRATEGIST` | Agent/worker seats, not people | Names only. |
| `JON-DIRECT` | A decision by the human researcher | The decision is usually quoted inline. |
| `E031`, `E062` | An experiment record id | Mostly not present in this export. |

**188 links in `registers/LEARNINGS.md` do not resolve**, for the same reason — they point
at documents in the private repository. The row text carries the finding; the link is only
a pointer. That register is bannered accordingly.

## 6. What you cannot get here

- **The game engine and card data.** Organiser-supplied, not ours to redistribute. Nothing
  here plays a game.
- **Raw episode traces and model weights.** Not published.
- **The +7.82 headline, independently.** One of its three inputs is not in this export;
  [the bridge is written out](EVIDENCE-MAP.md#if-you-recompute-the-headline-you-will-get-a-different-number-here-is-why).
- **A regenerable inventory.** The registers are a frozen snapshot; the generator's
  dependency closure is not shippable. See [REPRODUCING](REPRODUCING.md).
- **Licence provenance for five of the opponent kernels.** Named in [NOTICE](../NOTICE).

## 7. If you only take one thing

Separate the deck change from the policy change, measure each against its own control in
the same batch, then test whether the combined result holds against opponents you did not
develop against. Our combined intervention measured +7.82 pp on a development panel and
then split almost perfectly by opponent archetype — **+20.4 and +18.8** on two Alakazam
implementations, **−0.47 [−2.64, +1.71]** averaged across five others.

A panel average is a property of the panel. If we had stopped at the first number, we would
have published a general improvement that does not exist.
