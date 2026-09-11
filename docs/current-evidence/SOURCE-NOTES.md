# Source notes

Learning Which Pokémon TCG Decisions Are Worth Teaching — Jonathan Simone

These notes follow article references [1]–[7]. Paths below are relative to the extracted evidence ZIP. The main report is self-contained; this package supports closer inspection. No new games or training were run for this revision.

## [1] Submitted product and retention decision

`source-evidence/receipts/submission-provenance.json` identifies Tetsutani's unmodified public Grimmsnarl Damage-Transfer Control, policy c61e540b and deck 92b92bac. `source-evidence/receipts/competition-verification.json` records score 834.0 and rank 840/6,807 on September 6. This is a dated observation, not a final-ranking claim.

`source-evidence/research/retention-decision.excerpt.txt` records the August 10 review recommending retention because the reviewed alternatives had not qualified as a stronger replacement. The review standard required a complete deck-policy product with reliable execution and independently reproduced whole-game benefit, among other gates. This describes that standard and the reviewed alternatives, not exhaustive testing of every possible replacement or an invented original adoption story. The submitted agent's score does not measure the experimental learner or Lucario changes.

## [2] Implemented learner

`source-evidence/learner/` contains selected source excerpts for model_v2.py, action_decoder.py, semantic_encoder.py, c61_teacher_bridge.py and lf_v2_policy.py, plus the intended architecture. `source-evidence/research/behavior-objective.excerpt.txt` and `semantic-features-v2.excerpt.txt` add the ordered/unordered objective and source/target encoding.

The excerpts support 256-unit recurrence, actor-visible state projection, action features associated with source and target entities, legal selection without replacement, context updates, and STOP after the required minimum. In behavior-objective.excerpt.txt, lines 88–111 sum probabilities over permutations for an unordered selected set; lines 170–183 preserve sequence scoring for ordered choices and call the set objective otherwise. The article's A-then-B/B-then-A example explains this implemented objective, not a new playing-strength result. The runtime's recurrent state and its observation-history encoder are distinct mechanisms. Figure 1 is a schematic of capabilities and research branches, not a game trace or a measurement of tactical quality.

Each source directory has a manifest of source hashes and selected ranges. These are inspection excerpts, not a complete executable release. Established recurrent and imitation-learning methods are credited as methods used, not inventions of this project. The proposed transfer from tested strategic behavior into repeated retained learning remains uncompleted.

## [3] Historical teaching and student comparison

`source-evidence/receipts/training-receipt.json` records 1,358 learner-visited teacher-labeled decisions, ten completed epochs, seed 101, and selection of epoch eight. `numerical/learning-summary.json` preserves those fields and checkpoint identities. The teacher-label count is a receipt assertion; the original labeled decisions are not redistributed here.

The selected validation negative log-likelihood is 1.0417600870132446, compared with 1.0717802047729492 initially. This was the checkpoint-selection validation set, not an untouched holdout. The selected model-state hash starts 6ef49e2ee697; its saved checkpoint-file hash starts e072ae4c4555. The screen receipt identifies the same selected model state.

`numerical/student-outcomes.csv` contains all 1,203 historical attempts: 23 wins, 1,177 losses, and three draws. The comparison excludes draws and has 600 decided games in each seat. The exact c61 opponent uses the same Grimmsnarl list. The result does not isolate the contribution of the extra labels or establish improvement over the parent, and it does not evaluate later v2 runtime changes. See `source-evidence/receipts/learning-verification.json` for the recorded historical boundary.

## [4] Deck and mechanics

`source-evidence/receipts/source-verification.json` records inspected policy, deck and card-data identities. The submitted deck has 18 Pokémon, 32 Trainers and ten Basic Darkness Energy, with the development and damage-placement counts stated in the article. The credited submitted policy combines learned option scoring, tactical checks and specialist fallback policies.

Mechanics were checked against the local organizer card file, SHA256 a0ea63cf7adcb65d35436ce0eb390de6e2e35654a7c67c065a45f4abaa00f373. The report paraphrases the Grimmsnarl, Froslass, Munkidori, Alakazam and Xerosic interactions. A bounded additional inspection of Mega Lucario ex, card 678, supports Aura Jab's one-Fighting cost, 130 damage and up-to-three discarded Basic Fighting Energy attachments to Benched Pokémon; Mega Brave costs two Fighting, deals 270, and cannot be used by that Pokémon next turn. Organizer card data, engine and artwork are not included.

The experimental treatment is one Carmine replaced by Xerosic in the evaluated deck. A historical hardcoded list elsewhere in a policy module is not substituted for that treatment. Preferring Abra or Kadabra may require bringing the target Active; the described Lucario attacks do not themselves damage a Benched target. Disruption and targeting costs are strategic rationales, not individually proven causes of the observed wins.

## [5] Separate card, targeting and combination

`numerical/development-outcomes.csv` supplies 28,000 applicable records: 24,000 selected from the original development CSV and the formerly omitted separate 4,000-record reproduction. The three combined comparisons ran across two computers: the factorial and replicate on the 5080, and the separate reproduction on the 4070. The 28,000 records include the complete 8,000-game factorial experiment. These are selected cohorts supporting the stated estimates, not a new experiment. `numerical/METHODS.md` maps every contrast to its within-batch control. `numerical/SOURCE-MANIFEST.json` identifies originals and exports, including documented historical CRLF hash correspondence.

The verifier recomputes card-only +5.02 [3.30, 6.75], rule-only +3.62 [1.52, 5.72], and combined +7.82 [6.08, 9.55] percentage points. These use decided games and fixed inverse-variance pooling on the stated 40%-Alakazam development panel. Card and combined each pool three comparisons; rule pools two. Their use of shared factorial arms means the three pooled estimates are not independent of each other.

The four-arm interaction interval includes zero. Neither positive synergy nor exact additivity is established. The combined interval's exact upper endpoint is 9.554363678201325; direct rounding gives 9.55. Earlier documents printed 9.56 from intermediate rounding. Historical files retained under `historical/` are unchanged provenance; the current calculation and article use 9.55.

## [6] Matchups, seats, follow-up and mixture

`numerical/panel-outcomes.csv` contains all 8,400 records, seven opponent implementations, 600 per arm/opponent, 300 per seat. Scores are win 1, draw 0.5, loss 0. Figure 2 uses `numerical/verified-results.json`, regenerated by the verifier. Both absolute scores and score differences come from these rows.

The two Alakazam cells improve by 20.42 and 18.75 points; the other five have equal-weight mean −0.47 [−2.64, +1.71]. Normal 95% intervals use unbiased sample variance divided by n for fractional game scores, conditioning on fixed implementations and independent games, arms and cells. This matches the earlier article's figure-data convention. A former public script used a different variance approximation; see METHODS for the distinction. Matchup and seat analyses are descriptive follow-ups without multiplicity adjustment. Both-seat gains do not establish seat independence.

One Alakazam deck overlaps development under another pilot; this is not an entirely unseen-deck panel. The panel's Grimmsnarl alias is not submitted c61. `numerical/opponents.json` records available aliases and historical identities. The seventh alias lacked a full-hash inventory row; `numerical/retained-opponent-identity.json` now records a September 11 retained-file inspection matching the historical report's prefixes. Its deck matches c61 and its policy differs. This strengthens file identity without independently reconstructing historical execution.

`numerical/anchor-outcomes.csv` adds the separate 16,000-game follow-up against exact c61. The candidate is still the experimental Lucario derivative. Baseline: 3,463 wins, 4,508 losses, 29 draws; combined: 3,457 wins, 4,526 losses, 17 draws. Excluding draws gives −0.14 [−1.68, +1.40] points. This does not establish equivalence or absence of a cost. Saved activation checks document historical flags and deck prefixes; they do not reconstruct every historical execution condition.

The mixture formula equally weights implementations within Alakazam and other-opponent groups. At an assumed 25% Alakazam share, it gives +4.55 points. It reuses this panel and measures neither the competitive metagame nor a new replication. The suggested testing policy is an inference from these conditional results: compare plausible mixtures and require fresh whole-game evidence before promoting a specialist. It is not a claim of an implemented metagame selector or an additional completed evaluation. Terminal outcomes do not reveal which move sequences caused each win.

## [7] Execution identity and research memory

`source-evidence/research/execution-identity.excerpt.txt` records the July 25 configuration/import incident: an incomplete candidate copy caused the repository's existing policy to execute under a clone label. Missing activation keys helped reveal the mismatch. The source explicitly distinguishes absent instrumentation from a recorded zero. Correct execution is necessary for the intended comparison; a nonzero behavioral effect is not a universal validity requirement. A verified intervention with no changed choices can supply an informative null or coverage finding. This is a historical incident record; the article does not infer that every later execution path was universally certified.

`source-evidence/research/research-memory.excerpt.txt` documents source-bound retrieval of research records. `recovered-audit.excerpt.txt` preserves section 3 of a historical message withdrawing a proposed lethal-audit rerun after recovery of an earlier audit. Its manifest identifies the source snapshot and message. This demonstrates one recorded recovery affecting a research decision, not a measured general productivity gain.

The inventory links questions, methods, outcomes, limitations and reopening conditions. Generated inventory counts are not counts of validated discoveries. Research-session memory, within-game recurrent state and trained model weights remain separate concepts. Architecture plans are evidence of intent, not evidence that the complete improvement loop worked.

## Reproduction and release scope

Run `python numerical/verify_results.py --output numerical/verified-results.json` after extracting the ZIP. This standard-library command validates supplied input hashes and structure, recounts saved terminal outcomes and reproduces the reported arithmetic. Full details are in `numerical/METHODS.md` and `REPRODUCING.md`.

The package does not include full training weights, runnable third-party policies, the original teacher-label records, all research tooling or organizer materials. Recounting outcomes is distinct from rerunning games or training a model. `source-evidence/research/public-notebook-status-20260911.json` records five current public notebook references through read-only Kaggle metadata; licenses, historical pull dates and exact historical notebook-version linkage remain unresolved. This listing observation is not rights clearance. `PACKAGE-MANIFEST.json` covers current archive members; any older manifests apply only to their historical contents. Credits and release boundaries are in `NOTICE.txt`.
