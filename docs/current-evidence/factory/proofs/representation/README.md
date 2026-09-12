# Recalculate the retained representation result

```text
python verify.py
```

Python 3.10+; standard library only. The script locates its inputs beside itself, so it also works when invoked from another directory. A successful run prints JSON and exits with status 0. Changed source bytes, missing/duplicate arm-seed rows, inconsistent summaries or invalid counts cause a nonzero exit.

`repr_probe_01_summary.json` and `cache_meta.json` are byte-for-byte copies of retained historical aggregate records. The verifier checks their pinned hashes, reads the six arm/seed rows, and recomputes the means and sample standard deviations. The primary comparison is the unweighted mean across three paired seed/split experiments, **not** a pooled count treating their overlapping validation sets as independent observations. It reproduces **48.62%** baseline and **74.25%** identity-condition mean raw validation agreement, a difference of **25.63 percentage points**. The cache metadata records 44,343 examples.

The original source implementation assigned approximately 10% of whole games to validation from a seeded shuffle. For each seed, both conditions used that split. The retained record confirms matching seeds and validation counts; these files do not contain the actual split assignments or raw cached rows, so this verifier cannot independently prove their identities.

## What changed in the experiment

The baseline option scorer consumed four legacy numeric features. The variant appended a learned 16-dimensional identity embedding, with IDs reduced modulo 4,096. This also expanded the option layer's input from 4 to 20 and added 69,632 parameters. **This was not a capacity-matched isolation of identity alone.** Approximately 88.6% of valid option slots resolved to identities in the retained cache metadata.

Training source inspection found three epochs, Adam at 0.001, batches of 256 and a shared state/scorer design. The original trainer was committed at `49e3c405d496ae6d648ca0387582d768e272a6fd` on July 31, 2026; checkpoint persistence followed in `0b41008f87fedaa88c72e8f3ac54e5cb7707ecb1`. The later source preserves the training core. These are source-history observations, **not cryptographic bindings of the historical execution to that source or environment**.

## What the check does not establish

- It recomputes saved arithmetic; it does not rerun training or validate the original cache contents.
- The receipt lacks complete original environment, trainer-source and checkpoint pins. Retained elapsed times do not establish end-to-end throughput.
- Matching seed/count metadata does not independently prove split identity, prevent all leakage, or establish generalization to other games or opponents.
- The result measures imitation of recorded decisions. It does not measure game strength, teacher correctness, or a completed self-improvement cycle.
- This probe and the later current-v2 learning components are separate artifacts. A direct causal chronology between them is not claimed.

The [manifest](MANIFEST.json) records exact source hashes, provenance and scope. [CHECK-RESULT.json](CHECK-RESULT.json) is the captured arithmetic-check output from this release candidate, not a newly executed training result. The checker and documentation are project-authored and MIT-licensed under [../LICENSE](../LICENSE).
