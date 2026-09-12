# Bounded excerpt from the August 13 implementation roadmap

Project-authored source: `workflow/research/owned-learning-roadmap-20260813/implementation-readiness.md`.

- Source commit: `4d6bd0b931a820464ccc69f2fff77569f7d583fd`, 2026-08-13.
- Full source SHA-256: `3b6d8d82dadced34d45d806fcd60d45c8f58d6d4fdf62a8b64b217947cfebe2f`.
- Original lines 7–18 contain the readiness matrix. The four rows reproduced below are original lines 12–15, with their original headers restored.
- These are historical plans and reuse decisions, not evidence that every listed run subsequently completed. Historical role names designate the project's code and compute lanes.

| Slice | Reuse / rebuild ruling | Likely exclusive lock | Execution lane |
|---|---|---|---|
| Explicit v2 tensorizer | Rebuild from the final architecture; no adequate implementation exists | `semantic_features_v2.py`, test/shim, FULL index, schema artifact | ROACH |
| V2 model/runtime | Reuse recurrent/autoregressive patterns; build entity/option-aware v2 wiring | `model_v2.py`, test/shim, narrowly runtime wiring if required, FULL index | ROACH; SKYNET parity readback |
| Corpus | Reuse only #2798's isolation, atomic shard, split, recovery, and clustered-metric patterns | rematerializer/bootstrap adapter, test/shim, FULL index, compact manifest | ROACH code; SKYNET data-local run |
| Trainer/G1 | Reuse batching/recovery patterns; rebuild all v2 identities and inference-only freeze | trainer, G1 verifier, tests/shims, generated indexes | ROACH code; SKYNET 5080 training |
