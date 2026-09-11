# What a reader can reproduce

## Report arithmetic

From a clone of this repository, run:

```text
python docs/current-evidence/numerical/verify_results.py --output verified-results.json
```

Python 3.10 or newer; no extra packages, network, engine, account or GPU. This checks input hashes, unique records, cohorts, seats and the reported arithmetic from 28,000 development, 8,400 panel, 16,000 c61-follow-up and 1,203 student records. All pooled combined development inputs are included. A missing or altered input returns an error.

[Exact formulas and contrast selection](current-evidence/numerical/METHODS.md) · [Expected summary](current-evidence/numerical/VERIFICATION.txt) · [Source manifest](current-evidence/numerical/SOURCE-MANIFEST.json)

The main panel includes half-valued draws and uses unbiased sample variance/n. The older strike3 script used a different variance approximation and additional estimands; it is preserved as historical analysis. The current figures use the current verifier's values. The former 9.56 combined interval endpoint is corrected to 9.55 by direct rounding.

## A research-record search

```text
python -X utf8 scripts/prior_art.py "Xerosic" --limit 2
```

The search reads the public export's tracked documents when the private catalog is absent. Git should be on PATH; without it the tool can use a directory walk. Counts and rankings vary with the corpus. A hit is a source pointer, not a verdict; a miss does not establish that work never happened. This example was checked on the inspected September 11 public snapshot and is separate from gameplay.

## Preserved inventory and other tools

The SRI inventory is a historical snapshot of a larger working repository. Its full input closure, external archive and original unsquashed Git objects are not included. It cannot be regenerated completely from this export. Providing one missing file does not restore those dependencies.

Older full-suite and onboarding transcripts describe particular earlier exports, not a current passing test suite. The onboarding checker and several research tools depend on the private working repository. Their preserved source is not a promise that they can run here. Do not run cleanup or migration tools merely because their source is present.

## What this package does not execute

The original games and training require exact historical policies, decks, engine/runtime versions, seeds, training inputs and weights. This export does not supply that complete environment. Organizer materials and third-party opponent policies are excluded. The learner source excerpts support design inspection, not standalone inference or training.

The August checkpoint/runtime and current v2 implementation are different artifacts. The experimental Lucario candidate and submitted c61 player are different artifacts. The teacher-label count is preserved from a receipt; original labeled decisions are not recounted by this command. Available opponent identities and remaining gaps are explicitly recorded in [opponents.json](current-evidence/numerical/opponents.json) and [NOTICE](../NOTICE).

The [evidence map](EVIDENCE-MAP.md) follows current references [1]–[7]. Full training/game reproduction and conditional winner-code delivery remain distinct from the portable arithmetic check.
