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
