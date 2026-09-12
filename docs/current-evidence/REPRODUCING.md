# Reproduce the portable evidence checks

Extract the entire evidence ZIP and run the following from its root with Python 3.10 or newer. All six checks use the standard library, read supplied evidence and run no games or training. In a public checkout, first change directory to `docs/current-evidence`.

```text
python -X utf8 numerical/verify_results.py --json
python -X utf8 factory/proofs/representation/verify.py
python -X utf8 factory/cases/verify_curated.py
python -X utf8 review-supplement/verify_historical_sensitivity.py
python -X utf8 cases/recycler/verify.py
python -X utf8 cases/ko/verify.py
```

The [counter methods](numerical/METHODS.md), [Recycler case](cases/recycler/README.md), [KO case](cases/ko/README.md), [representation proof](factory/proofs/representation/README.md) and [source notes](SOURCE-NOTES.md) define the different populations, outcome conventions and custody limits. Recounting retained rows or aggregates does not reproduce historical execution. The separate [selection demonstration](factory/proofs/selection/README.md) requires PyTorch and uses prescribed scores, without trained weights or a game engine.
