# Authored source receipts

These compact transcriptions and configuration summaries supply the exported case. They preserve the original counts and distinguish reported quantities from new arithmetic. Source IDs refer to the original historical documents listed in [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json). Original full deck files, organizer card data, private filesystem locators and raw replays are not included. Exact original file SHA-256 and Git blob identities are provenance, not a runtime certification.

## R01 — Stage 1 preregistration

Historical document: September 3 STEP 2 Stage 1 preregistration. It names control A as deck D/Parent 1 and E as deck D with one Poké Pad replaced by one Energy Recycler. Both arms set `PTCG_ALAKAZAM_SNIPER=1`. Target: `kernel_prvsiyan_844_router`. Planned attempts: 1,000 per arm; alternating first/second seats. Primary estimand: E minus A win rate. A positive interval excluding zero advances to Stage 2. Either Alakazam cell below −5.26 percentage points stops the Stage 2 lever. The document states that outcomes must be interpreted from `outcome`, not the engine's numeric `result` field.

Its authored rationale selects Energy recovery because it could extend the deck and restore a scarce resource. Sacred Ash was the Pokémon-recovery alternative. Poké Pad was chosen as the cut because its search restriction excludes Mega Lucario ex, while other search remained. Neither this rationale nor its historical diagnostics establishes a causal mechanism for the observed win difference.

## R02 — First target-batch result

Historical document: September 3 STEP 2 Stage 1 result. Counts transcribed from its first two tables:

| Quantity | A control | E Recycler |
|---|---:|---:|
| Attempts | 1,000 | 1,000 |
| Decided games | 1,000 | 1,000 |
| Wins | 335 | 408 |
| Undecided games | 0 | 0 |
| Reported errors | 0 | 0 |
| Deckout losses | 664 | 592 |
| All deckout endings | 665 | 595 |
| Prize wins | 202 | 253 |

Reported difference: +7.30 percentage points, 95% interval [3.08, 11.52]. These inputs are recounted by the checker. The original causal sentence about every avoided deckout becoming a win is not supported by these marginal counts and is not adopted. The historical result refers to saved outcomes and replay sidecars, but those files were not recovered for this export.

## R03 — Stage 2 wider panel and target follow-up

Historical document: September 3 STEP 2 Stage 2 result. Total 10,000 attempts, five opponent implementations × 1,000 attempts per arm; zero errors reported. Panel inputs are explicitly 2,135 wins / 4,996 decided for A and 2,081 / 4,996 for E, with four undecided outcomes in each arm. Draws are not separately classified. Reported panel difference is −1.08 percentage points [−3.02, 0.86]. These aggregate inputs are recounted by the checker.

The following are **rounded historical receipt assertions**, not recovered per-cell observations:

| Stage 2 opponent | Control % | Recycler % | Reported difference pp | Reported 95% interval pp |
|---|---:|---:|---:|---:|
| aristophanivan_940 | 43.60 | 43.79 | +0.19 | [−4.16, +4.54] |
| prvsiyan_844_router | 36.14 | 39.20 | +3.06 | [−1.18, +7.31] |
| prvsiyan_alakazam_v12 | 52.85 | 50.55 | −2.30 | [−6.68, +2.08] |
| prvsiyan_alakazam_v8 | 35.44 | 32.80 | −2.64 | [−6.79, +1.52] |
| romanrozen_v13 | 45.65 | 41.94 | −3.70 | [−8.05, +0.64] |

This transcribes the original section 1 table; later sections differ by 0.01 at some interval endpoints. No per-cell count or new numerical claim is reconstructed from these rounded values. The target is measured in both stages and its Stage 2 subset also belongs to the wider panel. The historical two-batch target pool is reported as 3,999 decided games, rates 34.82% and 40.00%, difference +5.18 points [2.19, 8.18]. A later adjudication uses equal weights and reports [2.19, 8.17], SE 1.526 points; its second-batch denominator notation is `999/1000 per arm`. Exact target wins and complete pooling inputs are not enumerated in the original receipt. These figures remain historical-only.

The historical decision did not promote the swap as a general improvement. Its later correction explicitly states that the panel interval and the non-target intervals contain zero: apparent distributed cost is an interpretation of point estimates, not demonstrated harm. Nor does failure to reject a batch difference prove batch equivalence or independently significant replication.

## R04 and R05 — Inspected deck identities

The original A and E files each have 60 card entries. Direct inspection found exactly the following difference, with every other count equal: Poké Pad `1152` changes 2 to 1; Energy Recycler `1139` changes 0 to 1. Both have 14 Basic Fighting Energy. Treatment retains one Poké Pad, four Dusk Ball and four Fighting Gong. The compact summary is in [identities.json](identities.json), with the exact file hashes. Full lists are not exported. This verifies the authored comparison of the retained files, not historical execution custody.

## R06 — September 11 source review

The subsequent source review confirms the same deck hashes and describes control as already containing Xerosic and the targeting intervention. It states that historical runtime activation proof was not found in the original result directory and that its limited row searches did not recover the raw games. It also states candidate pooled totals of 696/1,999 versus 800/2,000 while citing the original historical documents. Since those exact totals are not independently enumerated in those originals, this release does not adopt them as recovered observations. The absence of rows in those searches is host- and coverage-limited.

## R07 — Attempt-ledger attribution

The project's GR-43 attempt record attributes the 2,000-game Stage 1 result to MASTER and records STRATEGIST's decision boundary. This is historical credit, not a recovered runner manifest or host attestation. Its stronger mechanism and replication language is not adopted; the limitations and corrected accounting in this case govern.
