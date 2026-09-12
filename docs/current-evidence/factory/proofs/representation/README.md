# Recalculate two retained representation experiments

From this directory:

```text
python -X utf8 verify.py
```

Python 3.10+; standard library only. The script locates all inputs beside itself, so invoking it by its path works from another directory. It requires no network, engine, raw game rows or model. Success prints JSON and exits with status 0; changed input bytes, incomplete or duplicate arm/seed rows, inconsistent summaries or invalid counts fail with a nonzero exit.

| Recorded experiment | Cached examples | Baseline agreement | Identity-condition agreement | Difference |
|---|---:|---:|---:|---:|
| First cache | 44,343 | 48.62% | 74.25% | +25.63 pp |
| Second public-teacher cache | 66,030 | 47.33% | 77.26% | +29.93 pp |

These are **raw validation agreement with recorded decisions**, averaged equally over three recorded seed comparisons per cache. They are not accuracy from pooling validation rows. Each summary contains six rows: baseline and identity conditions for seeds 0, 1 and 2. The checker validates all six per cache, matching arm counts, all three retained agreement metrics, rounded means and sample standard deviations, and the headline differences. Every recorded seed difference is positive in both caches. The second producer's 66,074 generated rows reconcile to 66,030 cached examples plus 44 skipped rows.

The original aggregate summaries and cache metadata are copied byte for byte. The first inputs retain their earlier release filenames; second-cache inputs are in [second/](second/). [MANIFEST.json](MANIFEST.json) pins all input hashes and sources. [CHECK-RESULT.json](CHECK-RESULT.json) is the captured recount output, not newly generated training evidence.

## What the experiment changed

The baseline scorer consumed four legacy numeric option features. The variant appended a learned 16-dimensional identity embedding, with identities reduced modulo 4,096. It also expanded the option layer's input from 4 to 20, adding **69,632 parameters**. This was not a capacity-matched isolation of identity alone. Approximately 88.6% and 88.3% of valid option slots resolved to identities in the first and second cache metadata.

Contemporary trainer source uses a seeded split by whole game, approximately 10% for validation, with both conditions sharing that seed's split. Each seed changes initialization and split membership. The retained files establish matching seeds and counts; they do not contain actual split memberships. Validation sets from different seeds can overlap, so seed results are not pooled as independent row observations.

Source inspection found three epochs, Adam at 0.001, batches of 256 and a shared state/scorer design. The initial trainer commit is `49e3c405d496ae6d648ca0387582d768e272a6fd`; checkpoint persistence followed in `0b41008f87fedaa88c72e8f3ac54e5cb7707ecb1`. These source observations do not cryptographically bind historical execution to a complete environment, exact trainer or checkpoints.

## Attribution and interpretation

The second producer receipt identifies **Roman Rozen's public V13 teacher**, key `romanrozen_strongstart_v13`. Its source and deck hashes, loader name and producer counts are retained in the clean [provenance excerpt](second/CORPUS-PROVENANCE-EXCERPT.json). Those are recorded identities; this recount does not rerun that loader or certify teacher correctness. The excerpt deliberately excludes an unrelated historical assertion about teacher strength. The full producer receipt and raw shard are not included.

Different recorded construction paths and recipes establish two experiments. **No raw overlap or deduplication audit was performed; this is not a claim of disjoint data or independent replication.** Neither comparison measures game strength, retained improvement or a completed self-improvement cycle. This representation probe and the later current-v2 learning components remain separate artifacts. The evidence supports improving the decision interface as a research direction, while gameplay benefit remains a separate question.

The verifier and documentation are project-authored and MIT-licensed under [LICENSE](LICENSE). The supplied small aggregates contain no raw gameplay rows, organizer engine/data, trained weights or third-party player source.
