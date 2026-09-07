# Ten instruments that lied

Every tool below produced at least one confident, wrong verdict before we caught it. None
of them crashed. Each returned a plausible number, and we acted on it.

This is the most transferable thing this project produced, so it is restated here without
the internal shorthand. The source rows are §3d of
[`workflow/ATTEMPTS-LEDGER.md`](../workflow/ATTEMPTS-LEDGER.md), which carries the ticket
ids and dates — and which is dense with references you cannot resolve from outside. Nothing
here needs those references.

The pattern worth taking: **a measurement tool fails silently, in the direction you want.**
Every one of these was caught late, by accident or by a second person, never by the tool
reporting a problem.

---

### 1. The opponent pool was made of us

We screened candidate agents against a pool of "field decks". The decks were real. The
**player driving all of them was our own heuristic**. So the pool measured how similar a
candidate was to us, not how strong it was.

Our own lineage scored **97–99%** against that pool. A mechanically independent agent scored
**82–92%** — and beat both of our kernels head-to-head. Every verdict from that pool is void
as a strength measurement.

**Generic form:** if you generate your opponents, check what they are piloted by. A
self-play pool with varied *configurations* is still one player.

### 2. The setting under test never reached the game

Eleven screens compared values of a configuration flag. The submitted bundle read **no
configuration file, no environment variable and no flag**. All eleven arms were
byte-equivalent programs. The 39.75%–50.25% spread was the noise of shuffled decks.

The correct conclusion is not "those settings do nothing". It is **"those settings are
untested"** — a different and much less useful state of knowledge.

**Generic form:** prove the knob reaches the code under test before you spend games on it.
Diff the actual bytes of two arms, or assert the value from inside the running program.

### 3. Sample sizes that could not resolve the effects being claimed

At n=400 per arm the minimum detectable effect is roughly **9.9 percentage points**. We were
routinely announcing 3–6 point effects from 400-game screens. **34 of 34** declared sample
sizes in the early record were too small for the claim attached to them.

The rule we adopted — *an n=400 screen can kill but can never confirm* — was useful
operationally and is **not a universal guarantee**; a later audit of our own calibration
found its provenance unresolved. Both halves matter: size for the effect you are claiming,
and do not treat a house rule as statistics. See
[WHAT-WE-LEARNED](WHAT-WE-LEARNED.md#sample-size-is-a-design-question-not-a-constant).

### 4. The deck-clobber confound

The evaluation harness dealt the variant deck to the engine while the agent's own deck
belief read a **different, clobbered file**. Three experiment lanes became uninterpretable.
An apparent "deck moves 5–12 pp" result was an artifact of the two paths disagreeing.

**Generic form:** when a change has to arrive through two paths, assert they agree at
runtime. A deck experiment must edit the constant the agent actually reads.

### 5. A logging schema broke and nobody noticed

**607 of 637 rows** in a rating log were written against the wrong header. It produced one
published claim that was simply false. A related parser bug silently dropped **95%** of rows
across two CSV schemas and reported "zero moving trajectories"; there were eleven references
polled and six moving.

**Generic form:** a parser that silently drops malformed rows will eventually report a
confident zero. Count what you dropped and fail if it is not zero.

### 6. Simulation rank did not predict ladder rank

Correlation between our local simulation ranking and real ladder placement was
**ρ = −0.50** — negative, and confounded. Local evaluation is a **brokenness screen only**:
useful for detecting that something is badly wrong, useless for ordering things that work.

One textbook case: a change measured **+15.2 pp** locally against one opponent and landed on
the ladder at a rating around 466.

### 7. Attestations that passed on nothing

A cluster of checks that reported success without examining anything:

- a soak test returned `PASS` on **empty input**
- a 420-game screen ran **the wrong agent** and reported clean
- a green fence passed a **uniformly-random** bundle
- a pull request showing `MERGEABLE` with skipped checks was read as "CI ran"

**Generic form:** every check needs a **positive control** — a known-bad input it must
reject. A check that has never failed has not been tested.

### 8. The Elo-400 conversion was wrong for this ladder

We used the standard Elo-400 rule to convert rating gaps into win probabilities. The fitted
constant for this ladder is **217.55**, making targets roughly **25% harder** than the naive
estimate said.

The corrected model — fitted on 9,483,374 rows, R² = 0.999997, with three curves for three
different questions — is in
[`workflow/canon/EQUATIONS.md`](../workflow/canon/EQUATIONS.md).

### 9. "Identical bytes converge" is false

Two submissions of **byte-identical products** settle roughly **50 rating points apart**,
with a persistent per-draw standard deviation of 27.5. We had been reading small rating
differences between near-identical products as signal.

**Generic form:** measure your platform's noise floor by submitting the same thing twice
before you interpret any gap.

### 10. Home-grown liveness and staleness detectors

Four separate attempts to infer whether a worker or a submission was still alive — silent
seat inference, days-since-last-submit, substring matching on status text, reading another
worker's checkout directory — were each wrong twice and retired. State is read from the
shared source of truth or it is not read.

---

## The one that generalises furthest

Not on the original list, because it was found later, and it is the cheapest to adopt:

**Two people produced two different numbers from one dataset, four times in one day** — and
the disagreement was always the draw convention. Each had hand-rolled a denominator over
rows the evaluation harness had *already summarised*, and picked differently. The harness
had decided it all along: `wins + 0.5·draws` over all games.

The resolution was not a preference but **matching the instrument**, so that a number in a
paragraph and a number in a results file cannot disagree.

The measured impact is the interesting part: **12 draws in 8,400 games**, maximum spread
across all three conventions **0.29 pp**, against interval half-widths of 2.5–5 pp. The
disputed quantity was an order of magnitude smaller than the uncertainty it sat inside. Four
disagreements, four reconciliations, and **no conclusion would have changed under any
convention**.

**Generic form:** state the convention once beside the first figure, take it from the
instrument rather than inventing it, and check whether the thing you are arguing about is
larger than your error bars before you argue about it.

---

## How these were actually caught

Worth stating plainly, because it is not flattering: **none was caught by the tool
reporting a problem.** They were caught by a second person recomputing a number, by an
audit run for an unrelated reason, or by someone noticing that a result was too good. The
practical conclusion we drew is that a research system needs a **cheap way for a second
party to recompute a headline from raw rows** — which is why the published game-level rows
in this repository are rows, not summaries. See
[FOR-RESEARCHERS](FOR-RESEARCHERS.md#1-the-data--44400-game-records-you-can-re-analyse-today).
