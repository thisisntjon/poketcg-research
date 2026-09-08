# Experimental learner: selected source evidence

These excerpts document the project-developed v2 model, semantic encoder, legal sequential decoder, runtime, and interface to the credited public c61 teacher. Each excerpt names the original source, its full-source hash, and the selected line numbers. MANIFEST.json hashes the LF-normalized excerpts stored here.

They explain implemented design, not a complete runnable software release. The August checkpoint's 23/1,200 result and the separate Lucario counter are different evidence. The architecture excerpt describes the continuing objective; repeated retained improvement is not claimed complete.

- [Entity-linked recurrent model](model_v2.py.excerpt.txt)
- [Sequential selection and STOP](action_decoder.py.excerpt.txt)
- [Actor-visible semantics](semantic_encoder.py.excerpt.txt)
- [Teacher interface](c61_teacher_bridge.py.excerpt.txt)
- [Runtime recurrence](lf_v2_policy.py.excerpt.txt)
- [Continuing architecture](architecture.md.excerpt.txt)

The project uses established recurrent and imitation-learning methods. The teacher implementation itself, engine, card data and training weights are not included in these excerpts. Project-authored excerpts follow the repository license; see [NOTICE](../../NOTICE) for public baseline attribution.
