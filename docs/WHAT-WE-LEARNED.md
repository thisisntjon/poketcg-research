# What we learned

Alongside a measured, scoped counter-strategy, this project produced a long list of
ways a measurement can be wrong while looking right. This page is that list. If you
read one supporting page here, read this one.

The statistical qualifications below are grounded in the source-verified audit at
[`workflow/knowledge-register/audits/2026-09-06-method-recovery/REVIEW.md`](../workflow/knowledge-register/audits/2026-09-06-method-recovery/REVIEW.md),
imported with its supporting records so its internal links resolve.

## The instruments lied first

Ten separate measurement tools each produced at least one confident, wrong verdict
before we caught them. Four are worth stating in full, because each one is a
mistake a competent team makes.

**The opponent pool was made of us.** For weeks we screened changes against a pool
of "field decks". The decks were real. The player driving them was our own
heuristic. So we were measuring how similar a candidate was to us, not how strong
it was. Our own lineage scored 97–99% against that pool. A mechanically
independent agent scored 82–92% against it — and beat both of our kernels head to
head. Every verdict from that pool is void as a strength measurement.

**The setting under test never reached the game.** We ran eleven screens comparing
different values of a configuration flag. The submitted bundle read no
configuration file, no environment variable and no flag. All eleven arms were
byte-equivalent programs. The 39.75%–50.25% spread we observed was the noise of
shuffled decks. The correct conclusion is not "those settings do nothing"; it is
"those settings are untested".

**The sample sizes could not resolve the effects we were claiming.** This is the
finding that most needs its own qualification, because our statement of it was itself
partly wrong.

The historical table this project relied on reports standard deviations of 3.529, 2.520
and 1.626 percentage points at 400, 1,200 and 2,400 games per arm, and attributes them to
a 120,000-game `rules_lucario` mirror calibration. **That calibration's primary provenance
is unresolved in the recovered evidence.** The 2026-09-06 method-recovery audit could not
recover its manifest, its evaluation-index row or its producer, and it records a
conflicting scaling correction. Failure to recover a manifest does not prove the run never
happened — but the number should not be cited as a directly measured result of ours.

Two further cautions from the same audit:

- The table's values and its own declared scaling law **disagree**. The law
  `2.520·√(1200/n)` gives 4.36pp at n=400 where the table gives 3.529pp. These are
  distinct quantities and neither is a substitute for the other.
- The nearby A/A receipt is a *different* experiment — 6,000 `v000_baseline` games in
  60 blocks of 100, with a design effect later marked unread because module load order
  was confounded. It does not supply the missing 120k measurement.

**A logging schema broke and nobody noticed.** 607 of 637 rows in a rating log
were written against the wrong header, producing one published claim that was
simply false.

## Sample size is a design question, not a constant

We used to state a rule: *an n=400 screen can kill and can never confirm; admitting a
5–8 point effect needs n ≥ 1,200 per arm.* That was a useful operational habit, and it
came from real pain — we had routinely announced 3–6 point effects from 400-game screens.

**It is not a universal statistical guarantee, and we no longer present it as one.**
Neither n=400 nor n ≥ 1,200 is adequate or inadequate on its own. Adequacy depends on the
target effect size, the design, the dependence structure between games, and the declared
error criterion. For independent Bernoulli arms with N observations each,
`Var(p̂ₐ − p̂_b) = pₐ(1−pₐ)/N + p_b(1−p_b)/N`, which at p = 0.5 gives
`SE = 100·√(0.5/N)` percentage points — 3.54pp at N = 400. Correlated arms need the
covariance subtracted, and within-arm dependence changes each mean's variance too. The
absence of a public seed-setting interface does not imply zero covariance, and
finite-sample agreement cannot prove independence.

One more distinction the audit insists on, and we adopt: **stopping a line for cost or
lack of promise is an operational decision, not evidence of inferiority.** The two must
keep their separate rationales in the record.

## The average of two opposite effects is not a null

The most useful single finding in this repository came from a rule that looked
worthless.

We added a tactical rule: when a knockout is available, always take it over
chipping damage. Pooled across a six-opponent panel it measured −1.38 percentage
points, 95% CI [−3.87, +1.10] — a textbook null.

Broken out by opponent, at 1,800 games per arm per cell, three cells excluded zero
in *opposite directions*: **−10.17 [−13.34, −6.99]**, **−11.03 [−14.20, −7.86]**,
and **+13.99 [+10.82, +17.16]**. Heterogeneity I² = 98.7%.

The two harmed cells run the *same deck* under two different players; the helped cells
share a different deck. That pattern is what motivated the deck-level reading. But the
comparison is **not fully crossed** — not every deck was run under every pilot — so it
cannot isolate deck causation. What it supports is that the effect varies by opponent
cell and that the variation tracks deck identity in the cells we ran; it does not
establish that the pilot contributes nothing. Roughly: *the rule is worth about +12
points against one deck and about −10 against a deck like ours, in these cells.*

Two sibling rules run through the identical panel as negative controls both gave
I² = 0.0% and effects indistinguishable from zero, so the heterogeneity belongs to
the knockout rule and is not an artifact of the panel.

The honest limit: six opponents out of forty-four registered ones, on one panel, and the
supporting evidence here is aggregate — it is weaker than a fully bound executable-run
claim. We found a candidate mechanism for the harm — that deck holds a 340-HP attacker
our best attack cannot one-shot, so forcing knockouts on small targets is wrong — and it
explains the harm but **not** the +14. We wrote that down rather than inventing a story
for the other half.

## The learned agent lost, and we kept the result

We trained a policy on our own play data. The checkpoint-selection validation loss improved from
**1.07178 to 1.04176**. This validation set selected the checkpoint; it was not an untouched holdout. Fielded against
exact c61 on the same Grimmsnarl list, it won **23 of 1,200 decided games**: 1.92%,
95% CI [1.22, 2.86].
([LEARNING-VERIFICATION.json](../workflow/writeup/visuals-2026-09-06/LEARNING-VERIFICATION.json))

We originally explained this with an argument that an imitation student's ceiling is its
teacher. **That is not a mathematical ceiling** and we withdraw it as stated. A student
trained to imitate can differ from its teacher in either direction on game outcomes:
imitation loss and win rate are different objectives, the student's errors are not
uniformly distributed across states, and nothing in the training objective bounds play
strength by the teacher's.

We also do not know *why* the gap is this large. Better imitation loss with weak gameplay
is consistent with distribution shift — the student meeting states its training data did
not cover — but it is equally consistent with the loss improvement being concentrated on
decisions that do not matter, or with an evaluation or training-identity defect. We did
not run the experiment that would separate these, so we name the possibilities rather
than choosing one.

What the result *does* support: better prediction metrics did not produce a competitive
replacement here, and learned policies should be assessed in fresh complete games
alongside imitation metrics.

## Dead ends carry a scope guard

A register of failures that overstates them is worse than one that understates
them, because the damage is invisible: you close a door that was never shut. So
every closed line in [the dead-ends register](../workflow/DEAD-ENDS.md) records
two things — the exact claim the evidence supports, and the claim it does not.

For example: a search-based agent we built lost 24–0 to its own fallback. That row
may be cited only as *this implementation, as enabled, loses to its own fallback*.
It is not evidence that search is a bad idea for this game. Both of our negative
search results used a weak position evaluator — the part most likely to be at
fault.

When the pool and flag defects came to light we re-audited the whole register and
marked each row VOID, UNKNOWN or SOUND. Most rows survived. One had closed the
exact lane we were about to work in, on the weakest evidence in the file.

## The retracted numbers

[The retraction register](../workflow/canon/RETRACTIONS.md) lists numbers this project
published and later found to be wrong, each with the reason and what to use instead. A
sample: a "best score" that was a frozen reading of a leaderboard entry that had stopped
updating; a rating spread computed by subtracting one non-observation from another; a win
rate produced by two people independently dividing the endpoints of a *rating range* as
if they were wins and losses.

The register exists because this project corrects by appending. The wrong number
keeps its original confident sentence and usually sits *above* the correction, so
a text search finds the wrong value more often than the right one. The register is
the one place that says which is which, and `scripts/retraction_scan.py` checks a
document against it before publication — a clean run being a check, not a certificate.
