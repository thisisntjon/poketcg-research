# Historical sensitivity after excluding the overlapping deck

The report's broader-benefit sentence has a separate historical analysis behind it.
Excluding the one implementation whose deck appeared in development under another
pilot leaves six implementations and 7,200 saved games, 600 per arm per implementation.
The historical DerSimonian–Laird random-effects calculation gives **+2.72 percentage
points [−3.29, +8.74]**. Its interval permits benefit and harm; it does not establish
absence of benefit, equivalence, or performance against an unknown competitive field.

The excluded implementation is **P01** in the existing numerical package. Its full
deck hash is recorded in [the manifest](SOURCE-MANIFEST.json); the sibling
`numerical/opponents.json` preserves the implementation and development-overlap mapping.
The other Alakazam implementation remains in the six. This is therefore a different
summary from the article's equal-weight average of the five non-Alakazam opponents.

## Reproduce without running players

When this folder is installed at `review-supplement/` beside `numerical/`, run:

```text
python review-supplement/verify_historical_sensitivity.py
```

For a differently located numerical folder:

```text
python verify_historical_sensitivity.py --rows PATH/panel-outcomes.csv --opponents PATH/opponents.json
```

Python 3.10+ and its standard library suffice. The verifier reads all 8,400 panel
records, checks their hashes and balance, applies the declared exclusion, and
reproduces the historical number. It executes no engine, model, network request,
training or game. [Saved output](verified-historical-sensitivity.json) is provided.

## Preserve the estimator distinction

Both this calculation and Figure 2 score wins as 1, draws as ½ and losses as 0.
This historical analysis uses the original **p(1−p)/n** approximation for each arm's
variance before random-effects pooling. Fractional draw scores are not Bernoulli
observations. The current figure instead uses the **unbiased sample variance of
game scores divided by n**, as documented in the sibling numerical methods.
The source formula is preserved in [the estimator excerpt](HISTORICAL-ESTIMATOR.excerpt.txt).
This supplement reproduces the historical analysis rather than changing any of
the current figure's intervals or silently substituting one convention for another.
The approximate intervals condition on the named implementations and independent
game/arm estimates; they do not account for all possible dependencies or new opponents.

## What was declared, and when

The original GitHub declaration was posted at **20:03:27 UTC on September 3**.
It named the overlapping implementation, the six-cell sensitivity and both
fixed- and random-effects estimators. Crucially, it also said the initial trial
was already about 20% through, with approximately 850 games per arm completed.
A subsequent message records that this initial run was discarded for missing
replays and the retained run restarted at **20:06 UTC**, with the analysis retained.

The declaration therefore followed the initial run's start and preceded the retained
repeat. This packet uses **historical sensitivity analysis**, not an unqualified
preregistration claim. The metadata and minimal quotations in
[chronology sources](CHRONOLOGY.json) document this scope.
The source repository is private; the relevant bounded
evidence is included here and the public reader need not access that repository.

The [result excerpt](HISTORICAL-RESULT.excerpt.txt) supplies the overlap identity
and the subsequently corrected draw convention. A nearby, unreproducible historical
power target is intentionally omitted: reproducing this sensitivity does not
validate that target or the original sample-size justification.

## Scope and provenance

These are project-authored source excerpts, aggregate outcome arithmetic and a
small verifier. No organizer engine, card data, artwork, raw observations, player
weights or third-party policy implementation is added. Original source paths,
Git identities, source hashes, excerpt ranges and export hashes are in the
manifest. Source hashes bind bytes, not experimental truth. Saved terminal
records and chronology do not reconstruct every historical runtime condition.
No new games or training were performed for this supplement.
