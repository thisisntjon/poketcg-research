# The research factory in action

Five cases show how the Fleet turned questions about Pokémon TCG into tools, experiments, and subsequent decisions. Jonathan Simone directed the work; AI contributors investigated, implemented, ran local tools, and reviewed evidence. The roles and tools changed during the campaign.

The factory was an operated research process. Its intended endpoint—successive learned players that retained the discoveries—remained unfinished. These cases explain the work that actually happened and what each result justified.

## 1. Turn a public policy into hypotheses we could test

**Question.** Where did a credited public player choose differently from our working pilot?

**Work.** A researcher compared decisions recorded from Roman Rozen's V13 policy with the project's pilot. The analysis grouped disagreements by decision context, then proposed three behaviors to isolate: prioritize the developing Riolu line, promote Mega Lucario ex, and change evolution timing. Project-authored code additions made these three hypotheses independently switchable and default-off.

**Finding.** The disagreement clusters supplied specific candidate interventions. They also exposed an implementation detail: a vague instruction such as “evolve earlier” needed an exact scoring or guard change to alter a real decision.

**Changed decision.** The next unit of work became a named policy module with an explicit activation condition, rather than an undifferentiated copy of the teacher.

**Limit.** A teacher choosing differently does not establish a better action. The mine used teacher-visited states and a deck differing by one card; winner-seat associations are not causal effects. This case demonstrates hypothesis generation and modular implementation, not a successful winning transplant.

[Original disagreement analysis](sources/04-policy-disagreement-mine.txt) · [Project-authored module fragments](sources/05-project-policy-modules.txt)

## 2. Build the instrument needed to test an alternative move

**Question.** Could a recorded position be reconstructed well enough to compare a different legal action?

**Work.** A local proof of concept reconstructed a research state and checked the recorded successor through an actor-visible semantic projection. Two fresh roots produced matching successors for the recorded action; a forced alternative changed the successor. Continuing the recorded sequence matched seven transitions.

**Finding.** A later shuffle changed menu positions. Reusing the old option number could therefore select something different, even when equivalent semantic choices remained available.

**Changed decision.** A scalable continuation tool would need to resolve action meaning and target identity after shuffles. Raw option-index reuse and raw serialized-state equality were insufficient contracts.

**Limit.** This was a small feasibility demonstration. It did not establish general continuation fidelity, hidden-world robustness, or that an alternative improved the game. Full research-state reconstruction did not authorize hidden information in a live policy.

[Original proof of concept and its unproved steps](sources/06-replay-state-proof-of-concept.txt)

## 3. Make labels useful to the trainer that would consume them

**Question.** Would more model-generated labels add a learning signal, or merely produce more descriptions?

**Work.** Parallel investigations examined the training consumer, local models, representation, and failure cases. Source inspection showed that labels routed through the existing weighted-loss interface became one relative scalar per row. A deterministic pass and a model-derived weight map made that consumer relationship inspectable.

**Finding.** An initial batch of 46 quarantined model drafts all mapped to the default weight. The team then built a richer evidence projection and reran eight previously inconclusive episodes on the second machine. Five produced non-abstaining outputs. Recounting the retained files gives:

| Retained artifact | Observed result |
|---|---:|
| Initial model-derived weight map | 46 of 46 at weight 1.0 |
| Enriched eight-episode outputs | 5 non-abstaining; 3 insufficient-evidence |
| Enriched outputs under the original mapping | 8 of 8 at weight 1.0 |
| Enriched outputs under the alternate interpretation | 6 at 1.0; 2 at an illustrative 1.5 |

**Changed decision.** The next work concerned the evidence supplied to the model and the mapping into training. The team kept both interpretations visible instead of presenting changed explanations as an automatically improved learning signal.

**Limit.** Non-abstention is not semantic accuracy. The alternative 1.5 weight was illustrative, and the outputs remained quarantined. Neither the output change nor the alternate mapping demonstrated a training benefit. The original eight-case all-abstention baseline is reported in the historical summary; its original raw outputs were not recounted for this release.

[Consumer derivation](sources/07-label-consumer-derivation.txt) · [Initial map and provisional status](sources/08-initial-label-map.txt) · [Enriched comparison, both mappings, and failures](sources/09-enriched-labeling-comparison.txt) · [Recomputed aggregate counts](labeling-aggregates.json)

## 4. Make a promising counter survive independent execution

**Question.** Would the combined hand-disruption and evolution-targeting intervention still help when another operator reconstructed it on the second computer?

**Work.** The strategist requested a reproduction. Before games ran, the second-computer operator checked the actual deck and intervention settings. The first attempt stopped: three opponents were present as source files but absent from the committed registry. Running only the available opponents would have excluded both Alakazam implementations. A changed environment default could also have enabled the intervention in both arms unless the control was set explicitly.

**Finding.** After repairing the registry handoff and checking the extracted source identities, the second computer completed 4,000 games with zero recorded errors. On that five-implementation development panel, containing 40% Alakazam, its within-batch decided-game gain was **+6.94 percentage points [3.93, 9.94]**. The larger changes appeared in the two Alakazam cells, consistent with the prediction.

**Changed decision.** The counter had support beyond its first machine and first comparison. The record preserved the initial failed reconstruction, the exact repair, and the second result. The article's later pooled headline includes this reproduction; this case is not an additional experiment.

**Limit.** This result concerns the experimental Lucario product and specified development panel. It establishes neither a broad-field benefit nor a gain in the frozen c61 Simulation submission. The cross-machine comparison does not isolate hardware effects, and terminal outcomes do not identify which individual sequences caused each win.

[Initial reconstruction failure](sources/02-counter-reconstruction-stop.txt) · [Completed comparison and disclosed repair](sources/03-counter-reconstruction-result.txt)

## 5. Make the next investigator inherit the correction

**Question.** How could accumulated research inform the next decision after its details no longer fit in working context?

**Work.** On September 2, an investigator proposed repeating a lethal-search audit, then found the July audit already on disk and withdrew the request. That manual discovery helped motivate better inventory routing. The later memory reader connected questions and findings to their original methods and qualifications.

**Finding.** Independent review found a subtle memory failure: a document's source hash was correct, yet an introductory retraction disappeared from retrieval and search. The reader was repaired to retain the preamble, and a synthetic regression case checked that the retraction remained visible and searchable.

**Changed decision.** Retaining a source file or matching its hash was no longer treated as sufficient evidence that the reader preserved its meaning. The correction became a testable part of the research tool.

**Limit.** The later reader did not produce the earlier manual recovery. The recovered audit concerned a coarse trigger and did not refute the full lethal verifier. The reader's overall coverage remained incomplete; this case establishes a repair, not perfect memory or a measured productivity multiplier.

[Manual recovery and withdrawn request](sources/10-manual-audit-recovery.txt) · [Independent review and remaining limits](sources/11-memory-reader-review.txt) · [Reader implementation fragments](sources/12-memory-reader-implementation.txt) · [Synthetic regression test](sources/13-memory-reader-regression.txt)

## How to read the evidence

The [recorded review roles](sources/01-cross-vendor-roles.txt) illustrate how different contributors participated. They do not establish that vendor diversity caused better results or that every review rule was enforced without failure.

These excerpts are project-authored records and selected code additions. They preserve historical wording alongside current limits; they are not new game or model executions. [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json) gives original paths, source hashes, selected line ranges and excerpt hashes. [README.md](README.md) maps the cases to the article's reference groups and explains verification and attribution.
