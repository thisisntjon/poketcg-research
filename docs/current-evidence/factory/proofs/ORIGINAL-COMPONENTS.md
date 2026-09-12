# Original components and the design choices behind them

The project explored how to represent a game decision, obtain useful supervision, and test whether changed behavior improved whole games. Jonathan Simone directed the implementation with AI research and coding assistance. The mathematical methods are established; the contribution described here is their project implementation, experimental use, and resulting lessons.

## A choice should retain its meaning as the menu changes

An option's current array index does not describe its strategic meaning. The representation experiment compared a four-feature option scorer with a variant receiving an identity embedding. The retained six-run summary supplies a positive **cached-imitation** result, while the parameter increase prevents interpreting it as a capacity-matched test of identity alone. The [standard-library check](representation/README.md) makes its reported arithmetic independently inspectable without supplying training data or executing a model.

The current v2 design separately represents global context, visible entities, public history and legal options. Options link to available source and target entities; a 256-unit recurrent core can retain context within the game. This is implemented capacity, not evidence that a trained v2 agent has learned the intended tactics. The July identity probe is not claimed as a directly demonstrated precursor to current v2. See the accompanying [architecture excerpt](../../source-evidence/learner/architecture.md.excerpt.txt), [model excerpt](../../source-evidence/learner/model_v2.py.excerpt.txt) and [source manifest](../../source-evidence/learner/SOURCE-MANIFEST.json).

## A failed representation changed the next architecture

The August 13 [hash-v1 closure record](learning-design/HASH-V1-CLOSED-20260813.json) binds four terminal offline fidelity failures and the exact architecture document that specified the next representation. One retained run improved on a weak baseline but still fell below a simple majority lookup. The architecture closed that hash-based class and called for explicit state, entity and legal-option blocks; the implementation roadmap specified what to rebuild and which recurrent, replay and recovery mechanics to reuse. The [bounded source excerpts and aggregate receipt](learning-design/README.md) preserve that documented decision chain. This is separate from July's identity-embedding probe and does not establish game strength for the new design.

## Optional selections need an explicit stopping decision

Selecting several items is a sequence of decisions. The original [decoder source](selection/action_decoder.py) masks unavailable options, prevents selecting an item twice, and enables STOP only after the minimum. A caller supplies new scores based on what has already been selected. This lets a model express early stopping while keeping the selection contract enforceable. The [seven CPU checks](selection/README.md) demonstrate those constraints using prescribed scores. They do not load learned parameters or prove that stopping improves play.

The current training objective also handles unordered targets by summing the probabilities of their supported valid selection orders. That objective is a separate component and is not covered by these seven decoder checks. Its implementation enumerates orders within a bounded supported size; it is not an unrestricted or novel dynamic-programming algorithm.

## Teaching and acting have different information boundaries

Teacher tooling reconstructs the learner's available positions and maps teacher choices back to semantic selections. The acting model receives its player-visible projection. Keeping those responsibilities distinct makes source/target identity, missing information and legal actions inspectable. The accompanying [teacher-bridge excerpt](../../source-evidence/learner/c61_teacher_bridge.py.excerpt.txt) and [semantic-encoder excerpt](../../source-evidence/learner/semantic_encoder.py.excerpt.txt) document the relevant interface. These relative links use the same evidence layout in the ZIP and the public repository's `docs/current-evidence/factory/proofs/` directory.

Historical collection, labeling, training and complete-game evaluation did run in a separate student branch. Current v2 components, the historical student and the submitted public policy are distinct artifacts. Neither a callable decoder nor lower imitation loss establishes a completed self-improving player. The writeup's complete-game strategic counter remains separately attributed to its experimental Lucario branch.

The demonstrations here expose original implementation and saved-result arithmetic in a small form a reader can run. They intentionally supply no public teacher implementation, organizer engine, card data, replay content or trained checkpoint.
