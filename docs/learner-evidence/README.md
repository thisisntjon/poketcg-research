> Current factory-centered report: [read it](../STRATEGY-WRITEUP.md). Its references [1]–[8] are mapped in [the current evidence notes](../current-evidence/SOURCE-NOTES.md). This page preserves supporting source context; earlier figure/reference numbering is historical.

# Experimental learner: source evidence

The current report describes actor-visible semantic features, 256-unit recurrence, source/target action links, legal sequential selection with STOP, and an ordered/unordered training objective. These are participant implementation choices using established learning methods.

- [Model](../current-evidence/source-evidence/learner/model_v2.py.excerpt.txt)
- [Decoder and STOP](../current-evidence/source-evidence/learner/action_decoder.py.excerpt.txt)
- [Actor-visible encoding](../current-evidence/source-evidence/learner/semantic_encoder.py.excerpt.txt)
- [Source/target features](../current-evidence/source-evidence/research/semantic-features-v2.excerpt.txt)
- [Training objective](../current-evidence/source-evidence/research/behavior-objective.excerpt.txt)
- [Teacher interface](../current-evidence/source-evidence/learner/c61_teacher_bridge.py.excerpt.txt)
- [Runtime recurrence](../current-evidence/source-evidence/learner/lf_v2_policy.py.excerpt.txt)

The historical August training receipt records 1,358 learner-state teacher labels, ten epochs and checkpoint selection by validation loss. Its 23/1,200 decided-game comparison is not a test of later runtime changes, an extra-labels ablation or evidence of strength versus the parent. [Exact sources and limits](../current-evidence/SOURCE-NOTES.md).

These excerpts are inspection evidence, not a complete runnable learner. Each directory has a source manifest. The old files beside this page remain preserved excerpts from the previous publication. Complete weights, teacher implementation and organizer materials are excluded. The proposed repeated retained-improvement cycle remains future work.

## Run a bounded component demonstration

[Seven prescribed-score checks](../current-evidence/factory/proofs/selection/README.md) exercise the exact training-side decoder on CPU with PyTorch. No trained model or game engine is loaded. [Original component reasoning](../current-evidence/factory/proofs/ORIGINAL-COMPONENTS.md) explains the design and the hash-v1-to-v2 change.
