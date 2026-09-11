# Reproducing the reported arithmetic

Extract the full evidence ZIP, then run:

```text
python numerical/verify_results.py --output numerical/verified-results.json
```

Use Python 3.10 or newer. The script uses only the standard library and resolves its inputs beside itself. It does not require installation of the repository, access to Kaggle, the game engine, model weights or a GPU. `--json` emits machine-readable output; the default output is a concise human summary.

## What the command checks

Input hashes, valid outcome values, unique record keys, expected cohorts and seat counts; 28,000 applicable development records, 8,400 opponent-panel records, 16,000 exact-c61-follow-up records and 1,203 student attempts; the stated differences, intervals, pools, interaction, seats and illustrative opponent mixture. See numerical/METHODS.md for formulas and the exact contrast selection.

The student outcome file is independently countable. The 1,358 teacher-label count and training metrics are assertions in the preserved training receipt. Reading a manifest checks consistency with the supplied source identity; it does not independently certify the historical experiment that produced a file.

## What needs the original competition environment

Rerunning the original games or training requires exact historical policy/deck identities, runtime and engine versions, seeds, original training inputs and checkpoints. Those are not supplied as a complete executable environment here. Source excerpts support inspection of the described learner; they cannot train or execute the full agent alone.

The current v2 source description and the historical August learner screen refer to different runtime states. The experimental Lucario candidate and the submitted c61 player are distinct. No public, organizer-free package is claimed to deliver every artifact needed for winner verification.

## File integrity and history

PACKAGE-MANIFEST.json hashes each other member of the ZIP. numerical/SOURCE-MANIFEST.json binds numerical exports to inspected originals. Other source manifests bind selected excerpts to source hashes and ranges. Original files retained under historical/ remain unchanged, including obsolete prose and figures; use the current SOURCE-NOTES.md and numerical/METHODS.md when conventions differ.

No game execution, training, network request or account mutation occurs when running the verifier. The optional output path is the only file it writes.
