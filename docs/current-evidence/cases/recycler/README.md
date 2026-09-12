# Energy Recycler: a target result and a wider-panel limit

Replacing one search card with recovery improved the **first target batch**, while the later wider panel did not establish a gain. This is a historical aggregate-count case: the included checker recomputes arithmetic from authored exports of retained receipts. It does not replay games or certify the historical runtime.

Run `python -X utf8 verify.py` in this directory, or run that file by its relative path from the evidence archive root. Python's standard library is sufficient. [CHECK-OUTPUT.json](CHECK-OUTPUT.json) records the author's execution; it is not independent review.

## Question and intervention

The experiment asked whether recovery could improve the experimental Lucario player's results against the specific `kernel_prvsiyan_844_router` opponent implementation. Historical loss diagnostics motivated two competing approaches: return discarded Energy, which could both extend the deck and replenish an attack resource, or return Pokémon with Sacred Ash. These were design rationales; this package does not reproduce the earlier diagnostic statistics or prove which mechanism caused any win.

The chosen change was exactly **one Poké Pad removed and one Energy Recycler added**. The inspected originals each contain 60 cards and 14 Basic Fighting Energy. The multiset difference is Poké Pad `1152: 2 → 1` and Energy Recycler `1139: 0 → 1`; every other card count is unchanged. The retained search configuration includes one Poké Pad, four Dusk Ball and four Fighting Gong. The opportunity cost is one fewer search card in every matchup. Poké Pad's restricted search cannot fetch Mega Lucario ex; this explains the historical choice of cut without proving that the cut is free. [R01, R04, R05](SOURCES.md)

The recorded control is deck D/Parent 1; treatment changes that one slot. **Both arms explicitly specify `PTCG_ALAKAZAM_SNIPER=1`.** This is a deck experiment on the same reported targeting setting, not an on/off test of that rule. The control already contains Xerosic and the targeting intervention. These products are separate from the entered public c61 player and from any learner. The exact deck hashes and a compact authored configuration comparison appear in [identities.json](identities.json); full deck lists and organizer data are not redistributed. [R01, R04, R05, R06](SOURCES.md)

## Counts that can be recounted

| Population | Control wins / decided | Recycler wins / decided | Difference, percentage points | 95% normal interval |
|---|---:|---:|---:|---:|
| Stage 1: first target batch | 335 / 1,000 | 408 / 1,000 | +7.30 | [+3.08, +11.52] |
| Stage 2: five-implementation wider panel | 2,135 / 4,996 | 2,081 / 4,996 | −1.08 | [−3.02, +0.86] |

These are the only effect sizes in this case approved as **new recountable numerical headlines or plotted values**. The first line must always be labeled **first target batch / Stage 1** and accompanied by the later-batch and wider-panel limits below. It is not the final pooled target estimate. [R02, R03](SOURCES.md)

Stage 1 has 2,000 attempted and decided games, 1,000 per arm, with zero reported errors or undecided games. Stage 2 has 10,000 attempted games, five implementations × 1,000 per arm, with 4,996 decided and four undecided per arm; zero errors are reported. The original Stage 2 receipt calls the eight exclusions **undecided** and does not separately enumerate draws versus other undecided outcomes. We preserve that label. Undecided outcomes are excluded, not scored as half-wins. The total across the stages is 12,000 attempts and 11,992 decided games. [R02, R03](SOURCES.md)

The estimator is treatment win proportion minus control win proportion among decided games. For each arm, `p = wins / decided` and `var(p) = p*(1-p)/decided`; the difference's standard error is the square root of the summed arm variances. Intervals use `difference ± 1.96*SE`, converted to percentage points. This unpaired normal approximation reproduces the retained first-batch and panel intervals. The design reports balanced, alternating seats; we do not assume game-level pairing covariance from that statement. The panel interval uses its aggregate binomial approximation, not a recovered per-cell or cluster variance. Intervals are nominal and do not establish absence of smaller effects. [aggregates.json](aggregates.json), [expected-results.json](expected-results.json)

## The second batch and historical pooled assertion

The later target batch is **inside the Stage 2 wider panel**. Therefore the historical two-batch target pool and the wider panel overlap; they are not independent supporting studies. The wider panel contains `aristophanivan_940`, `prvsiyan_844_router`, `prvsiyan_alakazam_v12`, `prvsiyan_alakazam_v8` and `romanrozen_v13`. Names identify the tested implementations, not five independently sampled archetypes. [R03](SOURCES.md)

The original later target result is **reported**, rather than recounted here, as +3.06 points with interval [−1.18, +7.31]; its interval crosses zero. The receipt gives rounded arm rates and the denominator notation `999/1000 per arm`, but no explicit exact wins for this target subset. Its pooled target headline reports 3,999 decided games and +5.18 points [2.19, 8.18]; a later equal-weight adjudication gives the same rounded difference with [2.19, 8.17]. The distinction matters because concatenating counts and equally averaging stage effects are different estimators when denominators differ. [R03](SOURCES.md)

A September 11 review states candidate pooled totals of 696/1,999 and 800/2,000. Those would reproduce the first pooled interval under concatenation, but that review cites the same original receipts rather than separately recovered exact target observations. We have not elevated those candidate counts to recovered evidence. Rounded rates are not reverse-engineered into observations. **The pooled value and all Stage 2 per-cell values remain receipt-only historical assertions in the supporting export, excluded from numerical headlines and plots.** This is an evidence-level restriction, not a claim that the old estimate is false. [R03, R06](SOURCES.md)

## Outcome accounting and decision

In Stage 1, deckout losses fell from 664 to 592 (**72 fewer**), all deckout endings from 665 to 595 (**70 fewer**), and prize wins rose from 202 to 253 (**51 more**). Total wins rose by 73 and total losses fell by 73. Counts come from the receipt; the checker subtracts them directly. Different endings and different games must not be treated as matched counterfactual outcomes. The historical phrase “every deckout avoided became a win” is unsupported and is explicitly rejected here. These counts also cannot distinguish deck extension from improved Energy availability. [R02](SOURCES.md)

The historical Stage 1 pass triggered the panel check. The source reports neither Alakazam implementation crossed its −5.26-point stopping threshold. Those per-cell inputs are rounded, receipt-only evidence here; passing that screen is not proof of no harm. The wider-panel interval crosses zero: the result demonstrates neither overall improvement nor distributed harm, and does not establish equivalence. The evidence did not justify promotion as a general product improvement. [R01, R03](SOURCES.md)

Permitted body wording is in [BODY-PARAGRAPH.md](BODY-PARAGRAPH.md). The strategic lesson is to measure the entire comparison relevant to a deck change: an encouraging first matchup result is insufficient for a card slot shared across opponents. The decision is bounded to this tested player, deck change, opponent panel and outcome convention.

## Identity and custody limits

The project attempt ledger attributes the experiment to the MASTER research seat, under STRATEGIST's direction. [R07](SOURCES.md) The original receipts refer to saved outcomes and replays; those rows, per-game sidecars and a run-start/end manifest were not recovered for this export. A missing local asset does not prove absence on another host. The exact historical execution host is not established in this source set; runner attribution is not independently re-established by this package. A deck hash establishes inspected deck identity; it does not prove those bytes executed in every historical game.

The exact historical candidate code hash, opponent executable hash, engine hash, seed schedule, per-cell Stage 2 counts and arm activation traces are unavailable in the inspected source set. Consequently this is **portable verification of exported historical aggregate arithmetic**, not clean-room game reproduction, independent runtime certification, a ladder result or measured learner improvement. No new games, training, engine execution or network operations are used. The [source manifest](SOURCE-MANIFEST.json) pins original source identities and exported files; [SOURCES.md](SOURCES.md) makes the required authored receipts accessible within the case. Source hashes establish identity, not truth.
