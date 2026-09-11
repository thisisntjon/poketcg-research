# Contributions and hypotheses

The article follows a research question: how can a player represent a meaningful choice, learn it, and establish that it is useful in complete games? This map separates original work from credited foundations and future work.

| Question | Design or intervention | Evidence | Lesson and current status |
|---|---|---|---|
| What does a choice mean when the legal menu changes? | Encode the acting player's visible state and associate each offered option with source and target entities; combine context with recurrence. | Learner source excerpts [2]. | Implemented representation. Playing-strength benefit of this specific design is not isolated. |
| How should a player choose fewer than the maximum? | Sequential selection without replacement, context updates, learned STOP after the minimum, ordered/unordered objectives. | Decoder and objective excerpts [2]. | Implemented expressive interface; an illustrative sequence is not evidence of optimal choice. |
| Can teaching address positions the learner itself reaches? | Query c61 on learner-visited states and mix 1,358 recorded labeled decisions into ten training epochs. | Training receipt and source inspection [3]. | Executed historical experiment; selected validation NLL improved, but the student won only 23/1,200 decided games against c61. No parent-child strength or labels-on/off causal comparison. |
| Is hand disruption worth a draw-Supporter slot? | Replace one Carmine with Xerosic in the Lucario derivative. | Three within-batch development comparisons [5]. | +5.02 points [3.30, 6.75] on the specified development panel. It spends the Supporter opportunity and may slow development. |
| Does pressure on the evolution line help? | Prefer visible Abra/Kadabra when the Alakazam line is detected. | Two development comparisons [5]. | +3.62 [1.52, 5.72]. A preference can require gusting and forgo another prize. |
| Does the combination help, and where? | Combine the card and targeting changes; inspect all seven matchup cells and an exact-c61 follow-up. | Three combined comparisons, 8,400 panel rows, 16,000 follow-up rows [5–6]. | +7.82 [6.08, 9.55] development. Large benefits against the two tested Alakazam implementations; broader benefit unresolved. Positive interaction is not established. |
| Can research recover and retain the conditions behind a result? | Source-linked inventory, retrieval with provenance, retraction records, execution-identity and activation checks. | Research excerpts and one recovered-audit account [7]. | Implemented record/retrieval work and a documented changed research decision. Neither global completeness nor a productivity/game-strength gain is inferred. |

## Credited foundations

The Simulation submission is Tetsutani's unmodified public Grimmsnarl Damage-Transfer Control. That credited player also supplied a teacher and an exact comparator. The Lucario experiment derives from makthanithin's Apache-2.0 community_1084 policy. Established recurrent networks, imitation learning, legal masking and learner-state teacher querying are methods used by this project; originality is in the implementation, questions, integration and controlled strategic investigation described here.

## Connection to the submitted entry

The submitted Grimmsnarl product provides the concrete deck-policy strategy, retained entry, teacher and comparison point. The experimental learner explores how its decisions might be learned; the Lucario branch tests a specific behavior and the conditions under which it helps. The report does not attribute the submitted ladder score to either experimental branch.

## Next test

Train a student on decisions from a successful deck-policy product. Compare the student and parent in fresh games on the same deck, then repeat the process and evaluate retention. A card substitution alone cannot be taught as an in-game action; the deck must be specified alongside the policy. This is a proposed experiment, not an already completed repeated-improvement cycle.
