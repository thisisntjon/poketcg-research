# From Research Agents to Better Pokémon TCG Decisions

**60 days of player design, deck-policy experiments, and a tested Alakazam counter.**

I am Jonathan Simone, a solo developer working toward TCG players that can keep improving. During this project, AI coding and research agents helped me investigate two connected questions: **how to teach useful behavior, and how to identify behavior worth teaching.** We called them "The Fleet".

This repository shares selected research, results and implementation evidence behind the [Kaggle Strategy article](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/measure-everything).

## Start here

- **[Read the current report](docs/STRATEGY-WRITEUP.md)** — the approach, game mechanics, experiments and next objective.
- **[Download the report](docs/downloads/FINAL-REPORT.pdf)** — a readable five-page version with three figures.
- **[Follow the evidence](docs/EVIDENCE-MAP.md)** — the article's seven reference groups, source excerpts and experiment records.
- **[Get the evidence package](docs/downloads/PTCG-EVIDENCE.zip)** and its [guide](docs/downloads/EVIDENCE-GUIDE.pdf).
- **[Try an offline research example](docs/REPRODUCING.md)** — search the published records without a game engine.

## What I developed

**A player needs meaningful choices.** The experimental v2 learner links legal actions to their source and target, scores them with recurrent context, and supports sequential selections with a learned STOP. Selecting "up to three" items can mean choosing one and stopping. [Inspect the design](docs/learner-evidence/README.md).

**Practice creates teaching opportunities.** Teacher-query tooling provides a route to advice on positions reached by a developing player. State representation, training, checkpoints and inference are separate components. The implemented components are steps toward repeated retained improvement; that full cycle remains the next objective.

**Deck and policy changes can be tested separately.** On a community_1084-derived Lucario pilot, I replaced one Carmine with Xerosic and changed targeting to prefer visible Abra/Kadabra when an Alakazam line is detected. A four-arm experiment separated the card, the targeting change, and their combination.

## A counter with a measured strategic role

In an 8,400-game, seven-opponent panel, the combined intervention improved mean game score by **20.42 and 18.75 percentage points against two tested Alakazam implementations**. The other five averaged **−0.47 points [−2.64, +1.71]**. These results locate the counter's advantage and support evaluating its value under different opponent mixtures.

[![Counter results across all seven opponents](docs/current-figures/02-matchup-results.png)](docs/STRATEGY-WRITEUP.md)

Earlier development comparisons gave **+7.82 points [6.08, 9.56]** across three within-batch comparisons on two computers, on a panel containing 40% Alakazam. The repository includes raw rows for two of those comparisons; [the evidence map explains the third input and the exact reproducibility boundary](docs/EVIDENCE-MAP.md#if-you-recompute-the-headline-you-will-get-a-different-number-here-is-why). Development uses decided games; the later panel scores win 1, draw 0.5, loss 0.

## The three gameplay artifacts

| Artifact | Role and evidence |
|---|---|
| **Submitted public Grimmsnarl** | Tetsutani's unmodified implementation, policy `c61e540b`, deck `92b92bac`. September 6: 834.0, rank 840/6,807. [Provenance and score](docs/EVIDENCE-MAP.md). |
| **Experimental learned player** | Project-developed representation, recurrent model and selection tooling. An earlier August checkpoint won 23/1,200 decided games against c61; that result does not evaluate the entire current v2 design. [Sources and historical evaluation](docs/EVIDENCE-MAP.md). |
| **Experimental Lucario counter** | Project modifications to makthanithin's Apache-2.0 community_1084 policy. The measured counter gains belong to this branch, not to the submitted product or recurrent learner. [Experiment](workflow/research/2026-09-03-xerosic-sniper-factorial.md). |

## Continue exploring

[Game mechanics](docs/HOW-IT-PLAYS.md) · [Research findings](docs/WHAT-WE-LEARNED.md) · [Reusable research assets](docs/FOR-RESEARCHERS.md) · [Inventory](workflow/inventories/sri/INDEX.md) · [Corrections](workflow/canon/RETRACTIONS.md)

The continuing objective is a modular system where practice produces teaching material, strategic discoveries inform the player, and fresh games establish which improvements it retains. The public records preserve useful work for that next step.

## Scope and attribution

This is selected research evidence, not a complete runnable game agent. The competition engine, organizer card data, raw episode dumps and training weights are not included. Source excerpts explain design; historical records retain their original context. Earlier article versions remain in Git history.

Project-authored code and documents use the [MIT license](LICENSE). Public baselines and other contributions are credited in [NOTICE](NOTICE); the original [release review](docs/RELEASE-REVIEW.md) records its scope and open attribution questions. The inspected source and experiment evidence remain distinguishable from the future learning objective.
