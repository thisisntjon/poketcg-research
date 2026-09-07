# A measured counter-strategy for Pokémon TCG, and the evidence behind it

This repository is the research record supporting the Kaggle Strategy-track report
**[Building and Testing a Pokémon TCG Counter-Strategy](docs/STRATEGY-WRITEUP.md)**
by Jonathan Simone (Simone Systems Research).

**The result.** A card substitution (one Carmine replaced by Xerosic) together with a
targeting rule (prefer a visible Abra or Kadabra when an Alakazam line is detected)
improved an **experimental Mega Lucario product** by **+7.82 percentage points
[+6.08, +9.56]** on a development panel containing 40% Alakazam, across three
within-batch comparisons on two computers.

**Where that gain lives.** A later 8,400-game panel — seven opponent implementations,
600 games per arm per opponent — located it. The two Alakazam cells gained **+20.42**
and **+18.75** points. The equal-weight mean of the other five is **−0.47 points
[−2.64, +1.71]**, an interval that leaves both modest benefit and modest harm plausible.

[![Combined intervention minus baseline, by opponent](workflow/writeup/visuals-2026-09-06/01-matchup-evidence.png)](docs/STRATEGY-WRITEUP.md)

This is a real, scoped gain on a specific experimental product against specific tested
opponents. It is **not** a universal upgrade, and it is **not** evidence that an agent
retained anything it learned on its own. The scope is the finding.

## Four ways in

1. **[Read the report](docs/STRATEGY-WRITEUP.md)** — the submitted manuscript, with its
   three figures and its eight numbered evidence routes.
2. **[Inspect the evidence](docs/EVIDENCE-MAP.md)** — references 1–8 mapped to the actual
   files in this repository, with hashes and with what each one does not establish.
3. **[Try a verified offline example](docs/REPRODUCING.md)** — one command, no game engine,
   recorded output shape and limits.
4. **[Explore the inventory and the corrections](workflow/inventories/sri/INDEX.md)** — the
   record of what was tried and what it taught, plus
   [the retraction register](workflow/canon/RETRACTIONS.md) of numbers this project
   published and later withdrew, and [the dead-ends register](workflow/DEAD-ENDS.md),
   where every closed line carries the claim its evidence does *not* support.

Mechanics: **[How it plays](docs/HOW-IT-PLAYS.md)**. Method and failures:
**[What we learned](docs/WHAT-WE-LEARNED.md)**.

## Three different products, which must not be conflated

| | What it is | Where it appears |
|---|---|---|
| **Submitted Grimmsnarl agent** | tetsutani's public Grimmsnarl ex Damage-Transfer Control kernel, used unmodified. Policy hash `c61e540b`, deck hash `92b92bac`. Not written by this project. | The Simulation-track submission. Leaderboard 2026-09-06: 834.0, rank 840 of 6,807 ([receipt](workflow/writeup/visuals-2026-09-06/COMPETITION-VERIFICATION.json)). |
| **Experimental Lucario product** | A separate derivative of makthanithin's Apache-2.0 `community_1084` sample policy. The counter-strategy was built and measured **on this**, never on the submitted agent. | Every experiment in this repository. Its control arm is a Lucario baseline — **not** the submitted c61. |
| **Owned student** | A policy trained on this project's own data. Improved held-out imitation loss; won **23 of 1,200** decided games (1.92% [1.22, 2.86]) against exact c61. | [LEARNING-VERIFICATION.json](workflow/writeup/visuals-2026-09-06/LEARNING-VERIFICATION.json). Not fielded. |

The submitted c61 later appears as an *opponent* in the student comparison. That is a
choice made after the fact for a fixed, identified referent; it does not establish why
c61 was originally submitted, and this repository makes no claim about that rationale.

## What the experiment actually separated

The design is a 2×2 over the experimental Lucario product:

| | Original list | One Carmine replaced by Xerosic |
|---|---|---|
| Targeting disabled | Control | Card change alone |
| Targeting enabled | Rule change alone | Combined product |

- **Card change alone: +5.02 points [+3.30, +6.75]** across three contrasts.
- **Rule change alone: +3.62 points [+1.52, +5.72]** across two contrasts.
- **Combined arm: +7.82 points [+6.08, +9.56]** across three contrasts.

The single-arm contrasts each change one thing against their own batch control. **The
combined arm changes both the card list and the targeting rule**, so its +7.82 is the
value of the pair, not of either component. We tested for an interaction and could not
distinguish it from zero. **Failing to detect an interaction is not evidence of
additivity** — the test simply does not resolve one at this sample size. Arithmetic and
per-contrast counts: [ABLATION-VERIFICATION.json](workflow/writeup/visuals-2026-09-06/ABLATION-VERIFICATION.json).

The panel and the development replication also use different scoring conventions — the
panel scores a win as 1, a draw as ½ and a loss as 0; the development contrasts use
decided games only — so their summaries are reported separately and should not be pooled.

## What else is in the record

- **A sign flip.** A tactical rule that always prefers an available knockout measured
  about **+12 points** against one opponent deck and about **−10** against a deck close to
  our own. Pooled across the panel it looked like nothing. The average of two opposite
  effects is not a null. ([What we learned](docs/WHAT-WE-LEARNED.md))
- **A learned agent that lost.** Better imitation loss, 1.92% of decided games won. Kept
  in the record rather than dropped.
- **The instruments that lied.** Measurement tools that each produced at least one
  confident, wrong verdict before they were caught — an opponent pool made of our own
  agent, an experiment path that never carried the setting under test, sample sizes that
  could not resolve the effects being claimed, a broken log schema.
- **The corrections.** [RETRACTIONS.md](workflow/canon/RETRACTIONS.md) lists numbers this
  project published and later found to be wrong, each with the reason and what to use
  instead.

## What is not here

- **The competition engine and the organiser card data.** Supplied by the competition
  organisers under their own terms; not ours to redistribute. **Nothing in this
  repository will play a game.** Every source check recorded here is a static inspection,
  not an execution.
- **Raw episode dumps and model weights.** Not redistributed. Aggregated outcome rows,
  sample sizes, intervals and the analysis script are published instead.
- **The full working repository and its Git history.** This is a squashed public import.
  Objects that are not in this tree are not reachable here, and a file's first appearance
  in *this* repository's history is an import artifact — it is not the date the work was
  run, the date it was implemented, or an explanation of why it was built.
- **Third-party kernel source.** Public, licensed and attributed in [NOTICE](NOTICE), to
  be fetched from the original source.

## Licence and attribution

Code and documents authored by this project are MIT-licensed ([LICENSE](LICENSE)).
Third-party work — makthanithin's Apache-2.0 sample kernel, tetsutani's fielded kernel —
is credited in [NOTICE](NOTICE). **The MIT file does not clear every included asset**:
imported verification records, third-party attribution and release clearance are tracked
in [docs/EVIDENCE-MAP.md](docs/EVIDENCE-MAP.md), which lists the release questions that
remain open. No security or legal clearance is asserted here.
