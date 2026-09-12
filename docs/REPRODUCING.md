# Reproduce the checks behind the report

Run these commands from the root of a GitHub clone. For the extracted evidence ZIP, remove the `docs/current-evidence/` prefix.

| Check | Command | Requirements |
|---|---|---|
| Historical game-result arithmetic | `python docs/current-evidence/numerical/verify_results.py --output verified-results.json` | Python 3.10+, standard library |
| Historical representation arithmetic | `python docs/current-evidence/factory/proofs/representation/verify.py` | Python 3.10+, standard library |
| Generic selection mechanics | `python docs/current-evidence/factory/proofs/selection/selection_demo.py` | Python 3.10+ and PyTorch; CPU |
| Curated evidence integrity | `python docs/current-evidence/factory/cases/verify_curated.py` | Python 3.10+, standard library |

The numerical command checks hashes, unique records, cohorts and seats before recounting 28,000 development, 8,400 panel, 16,000 exact-c61 follow-up and 1,203 student records. [Methods](current-evidence/numerical/METHODS.md) define the contrasts, draw conventions and approximate intervals. [Expected results](current-evidence/numerical/verified-results.json) preserve the reference output.

The [representation check](current-evidence/factory/proofs/representation/README.md) validates supplied bytes and retained metric rows; it does not reconstruct validation split assignments or rerun training. The [selection check](current-evidence/factory/proofs/selection/README.md) uses prescribed scores with the exact training-side decoder; it demonstrates seven component cases without a trained model, engine, network or GPU. These are different levels of verification, not substitutes for a fresh game experiment.

[Factory in action](current-evidence/factory/cases/FACTORY-IN-ACTION.md) and [original components](current-evidence/factory/proofs/ORIGINAL-COMPONENTS.md) explain why these artifacts exist. [Source notes](current-evidence/SOURCE-NOTES.md) map all eight report references to their evidence and limits.

Original games and training require complete historical policies, decks, engine/runtime versions, seeds, inputs and weights. This export does not supply that full environment. Organizer materials, third-party policies and original teacher-label decisions are excluded. Available identities and unresolved provenance are recorded in [opponents.json](current-evidence/numerical/opponents.json), [SOURCE-NOTES.md](current-evidence/SOURCE-NOTES.md) and [NOTICE.txt](current-evidence/NOTICE.txt). Conditional winner-code delivery is a separate obligation.

## Search the wider research record

Run `python -X utf8 scripts/prior_art.py "Xerosic" --limit 2`. Git should be on PATH; the tool falls back to a directory walk. A hit is a source pointer, and a miss does not establish absence. The SRI is a historical snapshot; complete regeneration, onboarding and other old full-suite commands depend on private inputs absent here. Preserved tools are not blanket promises of executability.
