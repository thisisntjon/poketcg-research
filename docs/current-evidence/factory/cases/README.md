# Evidence: the Fleet's research cycles

Start with [The research factory in action](FACTORY-IN-ACTION.md), a five-case walkthrough of questions, work, findings, changed decisions, and limits. Each case links directly to its supporting excerpts in this directory.

This collection supports references **[1], [2], [3], and [8]** of *The Fleet: Building a Research Factory for Pokémon TCG* by Jonathan Simone. It supplements the numerical counter evidence, learner evidence, and representation study supplied elsewhere in the accompanying package.

| Article reference | Evidence available here |
|---|---|
| [1] Operated research and independent review | [Recorded review roles](sources/01-cross-vendor-roles.txt), [counter reconstruction stop](sources/02-counter-reconstruction-stop.txt), [repaired second-machine comparison](sources/03-counter-reconstruction-result.txt) |
| [2] Policy study and search tools | [Disagreement mine](sources/04-policy-disagreement-mine.txt), [project-authored modules](sources/05-project-policy-modules.txt), [seven-transition replay proof of concept](sources/06-replay-state-proof-of-concept.txt) |
| [3] Consumer-driven labeling | [Consumer derivation](sources/07-label-consumer-derivation.txt), [initial map](sources/08-initial-label-map.txt), [enriched comparison](sources/09-enriched-labeling-comparison.txt), [aggregate recount](labeling-aggregates.json) |
| [8] Memory and corrections | [Manual audit recovery](sources/10-manual-audit-recovery.txt), [reader review](sources/11-memory-reader-review.txt), [implementation](sources/12-memory-reader-implementation.txt), [regression test](sources/13-memory-reader-regression.txt) |

## Provenance and verification

[SOURCE-MANIFEST.json](SOURCE-MANIFEST.json) identifies 17 original sources. For each excerpt it records the full original source hash, source path, selected inclusive line ranges, and exported byte hash. The manual-recovery source is a preserved JSONL message: the manifest records the source row, decoded `body` field, body-line ranges and message identity. Last-modifying Git commits are provenance dates, not necessarily experiment dates.

The excerpts retain exact decoded source lines, with explicit gap markers and UTF-8/LF formatting. Their opening context notes are new explanatory text. `labeling-aggregates.json` was recomputed from retained weight-map files and quarantined outputs; it exports only aggregate counts. Full source hashes identify the private originals without requiring a reader to obtain them to inspect this collection.

Run the standard-library verifier from this directory:

```text
python verify_curated.py
```

It checks the delivered file hashes and sizes against the manifest. It does not rerun games, models, training, original-source extraction or historical code tests. Checksums establish file identity, not scientific truth or complete runtime reconstruction. No new games or local-model calls were made to prepare this collection.

## Scope and attribution

The collection contains project-authored prose, aggregate findings, and selected project-authored code additions. It includes no organizer engine or card-table files, original game replays, model weights, secrets, or third-party policy files. Source excerpts are inspection artifacts; partial code fragments are not runnable releases.

The public V13 teacher is credited to Roman Rozen (`romanrozen`). The Lucario pilot derives from makthanithin's Apache-2.0 `community_1084` policy. The exported module fragments are additions traced to project commit `abed09b270f7bc41b3487bf8dddc4e70e7e96a28`; the surrounding third-party policy is not reproduced here. The package's existing license and attribution notices continue to govern their respective materials. Nothing here claims ownership of public teachers or organizer materials.

Historical documents sometimes express stronger interpretations than the present article. The context notes and case limits specify what this collection supports. It does not claim a first-ever AI fleet, a causal speed multiplier, universal vendor superiority, perfect review enforcement, or a completed self-improving player.
