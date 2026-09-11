# Evidence map for the current report

The report's seven reference groups are mapped below. Paths in the [complete source notes](current-evidence/SOURCE-NOTES.md) are relative to docs/current-evidence/ or the extracted evidence ZIP. The [contribution map](current-evidence/CONTRIBUTIONS.md) explains original work and credited foundations.

| Reference | Evidence route |
|---|---|
| [1] Submitted product and retention | [Provenance](current-evidence/source-evidence/receipts/submission-provenance.json), [dated score](current-evidence/source-evidence/receipts/competition-verification.json), [August retention review](current-evidence/source-evidence/research/retention-decision.excerpt.txt) |
| [2] Learner design | [Learner excerpts](learner-evidence/README.md), [selection objective](current-evidence/source-evidence/research/behavior-objective.excerpt.txt), [semantic features](current-evidence/source-evidence/research/semantic-features-v2.excerpt.txt) |
| [3] Historical teaching | [Training summary](current-evidence/numerical/learning-summary.json), [training receipt](current-evidence/source-evidence/receipts/training-receipt.json), [student outcomes](current-evidence/numerical/student-outcomes.csv) |
| [4] Deck and mechanics | [Source verification](current-evidence/source-evidence/receipts/source-verification.json), [bounded mechanics notes](current-evidence/SOURCE-NOTES.md) |
| [5] Components and combination | [All selected development outcomes](current-evidence/numerical/development-outcomes.csv), [exact contrasts and methods](current-evidence/numerical/METHODS.md) |
| [6] Matchups and follow-up | [Seven-opponent outcomes](current-evidence/numerical/panel-outcomes.csv), [c61 follow-up](current-evidence/numerical/anchor-outcomes.csv), [opponent identity map](current-evidence/numerical/opponents.json) |
| [7] Research memory | [Source-bound retrieval](current-evidence/source-evidence/research/research-memory.excerpt.txt), [recovered-audit account](current-evidence/source-evidence/research/recovered-audit.excerpt.txt), [execution-identity incident](current-evidence/source-evidence/research/execution-identity.excerpt.txt) |

## Recompute the current numbers

```text
python docs/current-evidence/numerical/verify_results.py --output verified-results.json
```

Only Python 3.10 or newer is required. [Saved output](current-evidence/numerical/VERIFICATION.txt) and [methods](current-evidence/numerical/METHODS.md) make the expected values and conventions explicit. All three combined development comparisons are included; the earlier missing-input boundary is closed for arithmetic. The directly rounded combined interval is [6.08, 9.55].

Development and exact-c61 follow-up exclude draws. The seven-opponent panel uses half-draw scores and unbiased sample variance/n. The mixture is a sensitivity calculation from that same panel. Outcome recounting does not reconstruct historical execution or prove a per-move mechanism. The 1,358 teacher-label count remains a training-receipt assertion. [Full limits](current-evidence/REPRODUCING.md).

Earlier reports, figures and conventions are preserved in the evidence ZIP under historical/. They are provenance, not additional independent experiments. The current article uses two figures. Neither the archived replay illustrations nor the old inventory counts are current main-report performance claims.
