# What we learned

Most of this project's output is not a stronger agent. It is a list of ways a
measurement can be wrong while looking right. This page is the honest version of
that list. If you read one page here, read this one.

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

**The sample sizes could not resolve the effects we were claiming.** We measured
the noise directly: in 120,000 mirror games, the standard deviation of the
difference between two arms is 3.529 percentage points at n=400 per arm and 2.520
at n=1,200. The minimum detectable effect at 80% power is therefore **9.88
percentage points at n=400**. We were routinely announcing 3–6 point effects from
400-game screens. Thirty-four of thirty-four declared sample sizes in the early
record were too small for the claim attached to them.

**A logging schema broke and nobody noticed.** 607 of 637 rows in a rating log
were written against the wrong header, producing one published claim that was
simply false.

The consequence is a rule we now apply everywhere: **an n=400 screen can kill and
can never confirm.** If a 400-game arm shows a large negative, that is enough to
stop work. If it shows a promising positive, it has told you nothing you can
publish. Admitting a 5–8 point effect needs n ≥ 1,200 per arm, and the number that
matters is the interval, not the point.

## The average of two opposite effects is not a null

The most useful single finding in this repository came from a rule that looked
worthless.

We added a tactical rule: when a knockout is available, always take it over
chipping damage. Pooled across a six-opponent panel it measured −1.38 percentage
points, 95% CI [−3.87, +1.10] — a textbook null.

Broken out by opponent, at 1,800 games per arm per cell, three cells excluded zero
in *opposite directions*: **−10.17 [−13.34, −6.99]**, **−11.03 [−14.20, −7.86]**,
and **+13.99 [+10.82, +17.16]**. Heterogeneity I² = 98.7%.

The two harmed cells run the *same deck* under two different players. The helped
cells share a different deck. So the effect is determined by the opponent's deck,
not by the opponent's policy — and the deck it harms against is close to our own.
Roughly: **the rule is worth about +12 points against one deck and about −10
against a deck like ours.**

Two sibling rules run through the identical panel as negative controls both gave
I² = 0.0% and effects indistinguishable from zero, so the heterogeneity belongs to
the knockout rule and is not an artifact of the panel.

The honest limit: six opponents out of forty-four registered ones, on one panel.
We found a candidate mechanism for the harm — that deck holds a 340-HP attacker
our best attack cannot one-shot, so forcing knockouts on small targets is wrong —
and it explains the harm but **not** the +14. We wrote that down rather than
inventing a story for the other half.

## The learned agent lost, and we kept the result

We trained a policy on our own play data. The held-out loss improved from
**1.07178 to 1.04176** — a real, reproducible improvement in the training
objective. Fielded against the actual agent, it won **23 of 1,200 decided games**:
1.92%, 95% CI [1.22, 2.86].

That is not a near miss. It is a characterisation of how far imitation was from
competitive, and it is why we stopped spending on it. The arithmetic was checked
before the games: an imitation student's ceiling is its teacher, and the teacher
was well below the score we needed. A better loss could not close that gap.

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

## The 16 retracted numbers

[The retraction register](../workflow/canon/RETRACTIONS.md) lists sixteen numbers this
project published and later found to be wrong, each with the reason. A sample: a
"best score" that was a frozen reading of a leaderboard entry that had stopped
updating; a rating spread computed by subtracting one non-observation from
another; a win rate produced by two people independently dividing the endpoints of
a *rating range* as if they were wins and losses.

The register exists because this project corrects by appending. The wrong number
keeps its original confident sentence and usually sits *above* the correction, so
a text search finds the wrong value more often than the right one. The register is
the one place that says which is which, and a script checks every document against
it before publication.
