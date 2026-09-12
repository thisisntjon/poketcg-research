# KO-priority case: one bonus, opposite observed effects

This is a portable recount of a retrospective seven-implementation experiment from September 4, 2026. All **8,400** authored outcome records are included. No games or training were run to make this export. The candidate was the project’s experimental Lucario rules policy; tetsutani c61 is one opponent here and a different product from that candidate.

## Question and intervention

Would favoring a projected knockout improve the complete player? The default scorer values the target and scales a nonlethal hit by damage divided by target HP, so a valuable partial hit can outrank a projected knockout. The dedicated ON switch adds **100,000** to the projected-knockout target score; OFF leaves it absent. This is a large preference in the scorer, not a guarantee about all actual knockouts or all possible choices. The game-ending premium remains additive in both arms.

The intended opportunity cost is the alternative target or damage plan. The outcome records do not identify which choices caused each win or loss. The historical authored scorer and flag were inspected at the exact Git identities in [identities.json](identities.json); no source snapshot or opponent code is copied here.

## Complete result

The score is 1 for a win, 0.5 for a draw and 0 for a loss. Every cell has 600 games in each arm, with 300 in each seat. Effects are ON minus OFF, in percentage points.

| Opponent implementation | OFF W/L/D | ON W/L/D | Difference (pp) | Approximate 95% interval |
|---|---:|---:|---:|---:|
| tetsutani c61 | 256/340/4 | 251/348/1 | -1.08 | [-6.67, +4.50] |
| prvsiyan Static-Deck Tusk v24 | 197/403/0 | 283/317/0 | +14.33 | [+8.84, +19.82] |
| dedquoc Rule-Based Engine | 584/16/0 | 581/19/0 | -0.50 | [-2.41, +1.41] |
| raunakdey07 Advanced Heuristic | 241/358/1 | 238/361/1 | -0.50 | [-6.04, +5.04] |
| penguin069 Public Scores 915 | 287/312/1 | 217/381/2 | -11.58 | [-17.13, -6.04] |
| aristophanivan 2plyexpectimax | 245/354/1 | 201/399/0 | -7.42 | [-12.87, -1.96] |
| pixiux Mega Lucario v62 | 259/340/1 | 212/386/2 | -7.75 | [-13.26, -2.24] |

The same rule produced opposite observed effects across implementations. This does not justify promoting the bonus as a universal improvement. Whether a reliable condition can select when to use it remains unresolved. The three intervals that cross zero do not establish equivalence. A fixed-mixture average would still describe that specified mixture, but it would not replace these different cell results.

## Method and verification

Run from this directory, or pass the script path from any working directory:

```text
python -X utf8 verify.py
```

The standard-library checker reads only this directory, changes no files, and checks all row indices, 300/seat balance, outcome categories, counts, means, sample variances, differences, intervals, complete figure membership and local file hashes. It exits nonzero on a mismatch. [Saved output](verification-output.txt) records the release preparation run. The checker reproduces arithmetic and exported receipt consistency; it does not rerun the historical experiment.

For n games, mean m = (W + D/2)/n; sample score variance s² = (W + D/4 − n·m²)/(n−1). The difference is 100·(m_ON−m_OFF). Its approximate interval is that difference ± 1.96·100·sqrt(s²_ON/n_ON + s²_OFF/n_OFF). These are independent-game normal approximations for fixed implementations, without multiplicity correction. Seed independence and extra variation are not established; use the intervals as exploratory uncertainty summaries.

## Identity and custody limits

The first c61 OFF metadata names commit `2745012525ee624df3833483590a788cd7d1f9da`; the other 13 arm/cell records name `6bb1c5b3a660ee531300c49f667a739fa0f11750`. Direct Git comparison on September 12 confirmed the entire tracked agent tree and eval.py are identical. Only a runner, receipt tool and preregistration document were added. No agent or eval.py path is recorded dirty. Config and candidate-deck hashes agree in all 14 records; the dedicated flag is the only recorded environment difference within each pair.

The original 14 JSONL files were re-read on SKYNET and matched the recovered hashes and all exported outcomes: 600 distinct worker tokens per arm/cell, no recorded errors, rules_lucario dispatch, and no decision traces. This supports retained outcome identity and recorded execution settings. It does not recreate engine bytes, untracked imports, every historical process or random seeds. The historical pool hash covers alias/selfcheck text; it is not an opponent-source hash. Full main/deck hashes in the identity file are hashes of currently retained opponent files inspected September 12, with main prefixes matching recorded aliases.

The related preregistration describes 4,000 games per arm against c61 followed conditionally by 300 per arm on a panel. The recovered panel contains 600 per arm in all seven cells. The document and runtime timestamp labels do not establish prospective custody for this design. This case makes no prospective claim.

## Opponent attribution and release boundary

These are third-party implementations, played with their own staged decks. Their authors retain credit. The following links identify recorded historical notebook slugs; current source bytes and licenses were not independently verified for this export. First-four page titles resolved during preparation; the last three page requests failed, so current availability is unverified. No third-party code, deck lists, archives, engine, organizer material, decision traces or secrets are redistributed.
- [tetsutani c61](https://www.kaggle.com/code/tetsutani/grimmsnarl-ex-damage-transfer-control) — `tetsutani`.
- [prvsiyan Static-Deck Tusk v24](https://www.kaggle.com/code/prvsiyan/ptcg-ai-battle-static-deck-tusk-1208-v24) — `prvsiyan`.
- [dedquoc Rule-Based Engine](https://www.kaggle.com/code/dedquoc/the-pok-mon-rule-based-engine) — `dedquoc`.
- [raunakdey07 Advanced Heuristic](https://www.kaggle.com/code/raunakdey07/pok-mon-tcg-advanced-heuristic-agent) — `raunakdey07`.
- [penguin069 Public Scores 915](https://www.kaggle.com/code/penguin069/public-scores-915) — `penguin069`.
- [aristophanivan 2plyexpectimax](https://www.kaggle.com/code/aristophanivan/2plyexpectimax) — `aristophanivan`.
- [pixiux Mega Lucario v62](https://www.kaggle.com/code/pixiux/ptcg-mega-lucario-ex-v62) — `pixiux`.

The public material is project-authored explanations, derived outcome categories, aggregates, source identifiers and arithmetic code. [Source manifest](SOURCE-MANIFEST.json) pins the originals consulted and the exported files. Original local absolute paths are omitted; hash identities and logical source locators preserve the chain without a private-path dependency. Hashes establish identity rather than historical truth.

## Use this case without mixing studies

[Claim contract](CLAIM-CONTRACT.json) freezes the dataset, arms, included cells, estimator, allowed narrative and all downstream consumers. [Body paragraph](BODY-PARAGRAPH.md), [aggregates](aggregates.json), [outcome rows](outcomes.csv), [figure input](figure-input.json) and [identities](identities.json) belong to this one panel.

Do not combine it with the older two-deck/two-pilot grouping, the overlapping +12.33-point pilot and +13.33-point favorable pool, the −10.60-point older group, the 20,400-game older denominator, the conditional KO-race follow-up, or the counter’s separate 8,400 records. The old grouping is replaced for this writeup; its historical source bytes are not rewritten. No causal deck explanation, individual-knockout attribution, learned routing or improvement to the entered c61 player follows from this case.

Reopen if source identities, row membership, outcome convention, runtime evidence, interpretation or the proposed wording changes.
