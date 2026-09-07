# Selective Counterplay: One Rule, One Archetype, and the Arithmetic of Where a Win Rate Comes From

### An opponent-conditioned play rule is worth +19 points against the archetype it detects and nothing against five others — and that sentence, with its intervals, is the whole result.

*Kaggle Strategy track · ≤2,000 words · every number carries its interval and its convention (`eval.py:1271`: win rate = (wins + 0.5·draws) / (wins + losses + draws)). Draft v18, 2026-09-04. Replaces every prior draft, all of which describe a product we are not submitting.*

---

## MODEL

### 1. The claim, stated at its true size

We built a single opponent-conditioned play rule for a fixed Mega Lucario ex deck and measured what it is worth. Against two independent third-party Alakazam pilots it is worth **+20.42pp [+14.89, +25.94]** and **+18.75pp [+13.67, +23.83]** — each interval excluding zero on its own. Against five other archetypes, all out of sample, it is worth nothing we can resolve: the pooled random-effects estimate is **+2.72pp [−3.29, +8.74]**.

That is not a general improvement, and we do not claim one. It is one confirmed instance of a mechanism — *counterplay that declines to act where its condition is not met* — with its value measured, its boundary measured, and its dependence on opponent composition measured. We think the arithmetic of that last part is the most useful thing in this report.

### 2. What we built, and the class it belongs to

Our agent is a scored-action heuristic (`rules_lucario.py`): every legal option receives a score, the highest plays. We classify interventions on it by one property — **whether the lever can decline to act where it does not help**. Deck composition cannot (a card is in the list or it is not). An unconditioned play rule will not (it fires everywhere). An **opponent-conditioned rule** does.

The rule (`RULE_ALAKAZAM_SNIPER`) detects an Alakazam line on the opponent's board from card IDs and adds a bonus to attacking a benched Abra or Kadabra. Because bench targets are scored only when we hold Boss's Orders, the rule causes the gust: it prefers a pre-evolution now over an evolved threat later. And because the bonus (4,000) exceeds the scored value of most single knockouts (~1,000–4,000 in the shipped configuration), it can decline an available KO to make that chip — a trade of a prize now for denying the evolved attacker. That trade is what the code permits; how often the rule actually takes it is not yet measured. It is 30 lines, default-off, and reads the opponent's revealed board only.

Only this class has ever produced a durable gain here. The deck-composition and unconditioned-rule classes were each tested this cycle and each measured as failures — a deck slot swap gained +5.18pp on its target and leaked −2.11pp across four other cells (net −1.08pp [−3.02, +0.86]); a hand-size guard fired 0 times in 900 games; a Carmine-conflict gate was harmful at −3.85pp [−6.91, −0.79].

### 3. Why it works: conditioning is necessary and not sufficient

We ran a three-arm ablation, same batch, same tree, arms proven distinct in child processes before game one (6,000 games, 2,000/arm, zero errors). Arm 2 removed the target filter and bonused every benched target — sniping 100% of 51,110 opportunities against the champion's 12.88%.

**Unconditioned sniping buys nothing.** It sits at or below baseline in four of five cells and is −2.00pp against baseline on the one cell where the conditioned rule earns +9.50pp. Removing the condition does not dilute the effect; it erases it. *Conditioning is necessary.* (Figure 2.)

It is also **not sufficient**. On a second Alakazam pilot the rule fires 56.5 times per game in 91.9% of games and returns −1.00pp [−7.93, +5.93]. We measured every channel that could explain the difference from the +11.50pp pilot: target exposure (96.5% vs 95.0%, indistinguishable), gust conversion (0.297 vs 0.310 Boss's Orders per game, intervals overlapping), and firing frequency — where the rates *do* differ, 40.45% vs 35.72% of scored targets with disjoint intervals, but the difference is 8.9 acts per game asked to explain a 12.5-point outcome gap while the 56.5 acts the weaker cell already makes produce nothing. A real difference in rate that cannot be the cause. Four channels excluded by direct measurement; the remaining variation is conditional on the opponent and is not explained by exposure, frequency, or affordability. (Figure 3.) We do not have the mechanism for the residual and say so.

### 4. Where it stops: the out-of-sample trial

Our development panel was 40% Alakazam and 40% our own deck under other pilots. A headline measured there is partly a statement about the panel. So we pre-registered a generalisation trial before any game — panel selected by content hash with the holdout, every development opponent, our own deck, and near-mirrors excluded; a 10%-win-rate competence bar against a neutral referee fixed before screening; random-effects primary with Cochran Q and I² reported; the falsifying outcome written down in advance.

Seven out-of-sample pilots, 600 games per arm per cell, 8,400 games, zero errors. **The effect separates perfectly by archetype.** Both Alakazam cells at ~+19; all five non-Alakazam cells inside noise of zero — at baseline win rates of 31–59%, so there was room to move and nothing moved. Panel-wide heterogeneity is I² = 92.9% (Q = 84.14 on 6 df); within the two Alakazam cells it is I² = 0.0% — a low-power 1-df test that could not have seen a difference below 7.51pp, which we state rather than dress up. Together those say: *something moderates the effect, and its name is archetype.* (Figure 5.)

Seat does not: both first-seat (+6.71 [+3.70, +9.73]) and second-seat (+3.71 [+0.70, +6.73]) effects exclude zero, and their difference (+3.00 [−1.26, +7.26]) does not. The rule works whether we go first or second.

### 5. What the headline actually was

The development-panel figure — **+7.82pp [+6.08, +9.56]**, reproduced across three batches on two machines — is correct and is not retracted. It is also a property of the panel. Write the field value as

> Δ_field(w) = w · A + (1 − w) · N,  A = +19.51 [+15.77, +23.25],  N = −0.32 [−2.40, +1.75]

where *w* is Alakazam's share of the opposition. Two things follow. **The decomposition reproduces the headline**: at the panel's 40–45% Alakazam it predicts +7.61 to +8.60pp, bracketing the measured +7.82. And the value is a function of the meta: the expected effect turns positive at **w = 1.6%** and becomes demonstrable at this sample size at **w = 11.2%**. The gap between those is the width of our own uncertainty, not a property of the rule. *Any reported panel win rate without its weights is an arbitrary point on that curve.* (Figure 6.)

### 6. How we know these numbers

Every figure was recomputed by two seats from the same banked rows through independent code; every difference between them — pooled effect, per-cell effects, detection floor, seat gaps — traced to one convention (draw scoring), which turned out to be already implemented in the evaluator and is now cited rather than declared. A third implementation, runnable by anyone from the repository, reproduces all published values and refuses to compute on incomplete data. The factorial's two levers were measured separately (+5.03, +3.62) and the product directly (+7.82); the parts do not sum to the whole, the interaction is +1.71 against SE 2.64, and we draw no stacked bar. (Figure 1.)

## DECK

### 7. The deck and the one change

The list is a Mega Lucario ex aggro shell — Riolu/Lucario line, Makuhita/Hariyama, fighting energy, Boss's Orders, draw supporters — chosen because a scored-action heuristic needs a deck whose correct play is legible from board state. The single change this cycle: **−1 Carmine, +1 Xerosic's Machinations.**

### 8. Why that card: the mechanism, not the intuition

Alakazam's *Powerful Hand* does 20 damage per card in its controller's hand for one energy — the attack scales with hand size. Xerosic's Machinations forces the opponent to discard to three cards, capping the attack at 60 instead of 140. The hypothesis is one a competent player would form unaided; what we add is the measurement: Xerosic fires in 68–73% of games at a mean hand size of 6.85–7.24, its contribution measured at +5.03pp on the development panel, and its cost — it takes the supporter slot ~0.95 times per game, stranding Carmine — measured too. Two reclaim gates were tried and both failed.

### 9. What the deck cannot do

The list has zero elasticity. Carmine was the only card with surplus copies (stranded in hand after turn 5 in 70–88% of games); every other slot is load-bearing, and any added trainer defaults to the top scoring rung and outranks our own draw engine. Our worst matchup, a Crustle wall, loses by our own deckout in 100% of losses, and a draw-throttle rule that acted 2.5 times per game did not prevent one (+2.40pp [−1.77, +6.57]; 640/640 losses still deckouts). That wall is a damage deficit no play rule reaches. We report it as the boundary of this deck, not as a task deferred.

## HONEST LIMITS

The sealed holdout shares an archetype with our worst matchup. The panel covers six archetypes across seven cells (two cells share a Steel deck under different pilots). One Alakazam cell reuses a development opponent's deck under a different policy — reported as a sensitivity, with the within-archetype difference at +1.67pp [−5.84, +9.17]. The replication is of *pilots*: one fully clean cell and one policy-held-out, deck-exposed cell — not two fully held-out decks. The Xerosic copy count was never independently optimised. A latent scoring defect exists in two default-off flag paths (`:614`) and is documented, not patched, because a behaviour change to the shipped policy cannot be validated at zero games. And the Simulation ladder locked on Aug 16, so nothing here was fielded; this is an account of a method and its measured boundary.

## Evidence index

Figures 1–5: `workflow/strategy-report/figures/`, regenerable byte-identical from `origin/main` via `make_figures.py`; Figure 6 via `make_figure6.py` in the same directory. Rows: `#3289` (8,400 Strike 3 games), `#3275` (6,000 Phase 1), `#3279` (2,000 Strike 2). Pre-registration: `workflow/canon/PHASE3-PREREG.md`, merged before the rows. Recompute: `#3302`. Lever taxonomy: `workflow/canon/LEVER-CLASSES.md`. Retractions and superseded figures: `workflow/canon/RETRACTIONS.md`.
