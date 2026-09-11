# Learning Which Pokémon TCG Decisions Are Worth Teaching

**Sixty days of meaningful action design, teacher-guided learning, and controlled deck-policy experiments.**

I am Jonathan Simone. As a solo developer directing AI coding and research agents, I investigated how a player can represent a meaningful choice, learn it, and establish that it helps in complete games. This archive supports my [Pokémon TCG Strategy entry](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/measure-everything).

## Start here

- [Read the report](docs/STRATEGY-WRITEUP.md), or [download its four-page PDF](docs/downloads/FINAL-REPORT.pdf).
- [Inspect the contributions and hypotheses](docs/current-evidence/CONTRIBUTIONS.md).
- [Follow references 1–7](docs/EVIDENCE-MAP.md), or download the [one-page guide](docs/downloads/EVIDENCE-GUIDE.pdf) and [portable evidence ZIP](docs/downloads/PTCG-EVIDENCE.zip).
- [Recompute the numerical results](docs/REPRODUCING.md) with Python and no game engine.
- [Inspect opponent provenance](docs/OPPONENT-PROVENANCE.md), including retained-file identities and unresolved historical license/version records.

## Three connected research questions

**Give choices meaning.** My experimental learner represents actor-visible state and action source/target features, uses 256-unit recurrence, and makes sequential selections with a learned STOP. The interface can express choosing fewer than the maximum. [Source evidence](docs/learner-evidence/README.md).

**Teach on visited positions.** An August experiment mixed 1,358 recorded learner-state teacher labels into training over ten epochs. Selected validation loss improved, while the student won only 23 of 1,200 decided games against c61. The result makes the distinction between prediction metrics and useful play concrete. It evaluates that historical checkpoint/runtime, not the current implementation. [Training and comparison](docs/current-evidence/SOURCE-NOTES.md#3-historical-teaching-and-student-comparison).

**Test the behavior and its conditions.** I replaced one Carmine with Xerosic in a public-derived Lucario pilot and separately changed targeting to prefer visible Abra/Kadabra when an Alakazam line is detected. A four-arm experiment separated the card, policy and combination; repeated complete-game comparisons measured their value.

[![Absolute scores and effects across all seven tested opponents](docs/current-figures/02-matchup-results.png)](docs/STRATEGY-WRITEUP.md)

The combination improved game score by **20.42 and 18.75 percentage points against two tested Alakazam implementations**. The other five averaged **−0.47 [−2.64, +1.71]**, leaving broader benefit unresolved. These are results for fixed implementations, not a measured competitive metagame. The panel has 8,400 games and uses win 1, draw 0.5, loss 0.

Development comparisons give **+7.82 [6.08, 9.55]** using decided games, within-batch controls and inverse-variance pooling on a panel containing 40% Alakazam. All three pooled combined inputs are supplied: factorial and replicate on the 5080, and a separate 4,000-record reproduction on the 4070. The 28,000 selected development records include the complete 8,000-game factorial. A 16,000-game follow-up compares the same Lucario intervention with its baseline against exact c61. [Methods and verification](docs/current-evidence/numerical/METHODS.md).

## Attribution and scope

| Artifact | Role |
|---|---|
| Submitted Grimmsnarl | Tetsutani's unmodified public Damage-Transfer Control, policy c61e540b, deck 92b92bac; September 6 score 834.0, rank 840/6,807. Teacher and comparator as well as submitted entry. |
| Experimental learner | My encoder, recurrent policy, sequential decoder and teacher/training integration, using established learning methods. Historical training and current source are distinguished. |
| Experimental Lucario | My card substitution, targeting changes and comparisons on a derivative of makthanithin's Apache-2.0 community_1084 policy. The counter results belong to this branch. |

The broader research inventory records questions, findings, corrections and conditions for reopening a hypothesis. It supports recovering lessons across research sessions; it is distinct from within-game memory and learned weights. Repeated retained improvement in an integrated player remains the next test.

[Research inventory](workflow/inventories/sri/INDEX.md) · [Research methods](docs/FOR-RESEARCHERS.md) · [Corrections](workflow/canon/RETRACTIONS.md) · [Evidence scope](docs/RELEASE-REVIEW.md)

This is selected research evidence. The numerical command recounts saved outcomes; it does not rerun games or training. Organizer materials, complete player weights and third-party policy implementations are excluded. Some historical attribution records remain incomplete. Project-authored materials use the [MIT license](LICENSE), with [third-party credits](NOTICE) and competition-use restrictions preserved. The current report and numerical methods identify what was implemented, tested and left unresolved.
