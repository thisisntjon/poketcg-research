# Reproduce the checks behind the report

Run these commands from the extracted evidence ZIP folder. In a GitHub clone, prefix each script path with `docs/current-evidence/`.

| Check | Command | Requirements |
|---|---|---|
| Historical game-result arithmetic | `python numerical/verify_results.py --output verified-results.json` | Python 3.10+, standard library |
| Historical representation arithmetic | `python factory/proofs/representation/verify.py` | Python 3.10+, standard library |
| Generic selection mechanics | `python factory/proofs/selection/selection_demo.py` | Python 3.10+ and PyTorch; CPU |
| Curated evidence integrity | `python factory/cases/verify_curated.py` | Python 3.10+, standard library |

The numerical command checks hashes, unique records, cohorts and seats before recounting 28,000 development, 8,400 panel, 16,000 exact-c61 follow-up and 1,203 student records. [Methods](numerical/METHODS.md) define the contrasts, draw conventions and approximate intervals. [Expected results](numerical/verified-results.json) preserve the reference output.

The [representation check](factory/proofs/representation/README.md) validates supplied bytes and retained metric rows; it does not reconstruct validation split assignments or rerun training. The [selection check](factory/proofs/selection/README.md) uses prescribed scores with the exact training-side decoder; it demonstrates seven component cases without a trained model, engine, network or GPU. These are different levels of verification, not substitutes for a fresh game experiment.

[Factory in action](factory/cases/FACTORY-IN-ACTION.md) and [original components](factory/proofs/ORIGINAL-COMPONENTS.md) explain why these artifacts exist. [Source notes](SOURCE-NOTES.md) map all eight report references to their evidence and limits.

Original games and training require complete historical policies, decks, engine/runtime versions, seeds, inputs and weights. This export does not supply that full environment. Organizer materials, third-party policies and original teacher-label decisions are excluded. Available identities and unresolved provenance are recorded in [opponents.json](numerical/opponents.json), [SOURCE-NOTES.md](SOURCE-NOTES.md) and [NOTICE.txt](NOTICE.txt). Conditional winner-code delivery is a separate obligation.
