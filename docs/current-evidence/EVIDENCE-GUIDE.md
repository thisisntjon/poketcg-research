# Evidence guide

Learning Which Pokémon TCG Decisions Are Worth Teaching

Jonathan Simone

## Read, inspect, reproduce

Read [FINAL-REPORT.pdf](FINAL-REPORT.pdf) for the complete article. Extract PTCG-EVIDENCE.zip, open INDEX.html, and choose a claim below. SOURCE-NOTES.md provides its precise scope and provenance. The [public research repository](https://github.com/thisisntjon/poketcg-research) provides the report, current evidence and wider research context.

| Article reference | Start here inside the ZIP | What it establishes |
|---|---|---|
| [1] Submission | source-evidence/receipts/submission-provenance.json; source-evidence/research/retention-decision.excerpt.txt | Credited submitted product, dated performance, reason to retain it |
| [2] Learner | source-evidence/learner/; source-evidence/research/behavior-objective.excerpt.txt | Implemented action representation, recurrence and selection objective |
| [3] Teaching | numerical/learning-summary.json; numerical/student-outcomes.csv | Historical training receipt and 23/1,200 decided-game result |
| [4] Deck | source-evidence/receipts/source-verification.json; SOURCE-NOTES.md | Submitted deck identities and inspected mechanics |
| [5] Components | numerical/development-outcomes.csv; numerical/METHODS.md | Separate card, targeting and combined effects, including all pooled batches |
| [6] Matchups | numerical/panel-outcomes.csv; numerical/anchor-outcomes.csv | Seven-opponent results, seat breakdown, c61 follow-up and mixture |
| [7] Research memory | source-evidence/research/research-memory.excerpt.txt; recovered-audit.excerpt.txt in that directory | Source-bound retrieval and one documented decision affected by recovery |

## One command to check the arithmetic

From the extracted ZIP folder: **python numerical/verify_results.py --output numerical/verified-results.json**

Python 3.10 or newer; no extra packages, network, engine, account or GPU. The command checks the supplied files and prints a summary. It recounts 28,000 development, 8,400 panel, 16,000 c61-follow-up and 1,203 historical student records. A missing or altered input produces an error. The exported rows contain outcomes and source locators, without game-state observations or organizer assets.

## How to read the evidence

The submitted public c61 player, experimental recurrent learner and modified public-derived Lucario pilot are distinct artifacts. Implementation, recorded training and measured game results are labeled separately. The original contribution is mapped in CONTRIBUTIONS.md; REPRODUCING.md explains verification limits.

The command reproduces arithmetic from saved outcomes; it does not rerun training or gameplay. The 1,358 teacher-label count is a training-receipt assertion. Source excerpts document design, while the historical student screen evaluates a particular August checkpoint/runtime. The proposed repeated retained-improvement loop remains future work.

Current results and methods take precedence over documents retained under historical/. The combined interval now rounds directly to [6.08, 9.55]. PACKAGE-MANIFEST.json identifies archive members; source manifests identify the evidence they came from. Full models, third-party policy implementations and organizer materials are not redistributed here.
