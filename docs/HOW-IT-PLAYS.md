> Current factory-centered report: [read it](STRATEGY-WRITEUP.md). Its references [1]–[8] are mapped in [the current evidence notes](current-evidence/SOURCE-NOTES.md). This page preserves supporting source context; earlier figure/reference numbering is historical.

# How it plays

This page explains the submitted public Grimmsnarl player and the experimental Lucario pilot. For the project-developed recurrent learner, see the [current report](STRATEGY-WRITEUP.md#give-decisions-enough-meaning) and [source excerpts](learner-evidence/README.md).

Everything on this page comes from **static inspection of source and supplied card
text**, recorded in
[SOURCE-VERIFICATION.json](../workflow/writeup/visuals-2026-09-06/SOURCE-VERIFICATION.json).
No game was executed to produce it. A path the source permits is not a measured
frequency and not a demonstration that the path is the best available.

## The fielded agent

The agent on the leaderboard is tetsutani's public Grimmsnarl kernel, used
unmodified. Its decision procedure is **not** a search. At each decision the game
engine hands it a menu of legal options; the kernel scores every option using
gradient-boosted-tree ensembles — five sub-models, selected by the *kind* of
decision being made — wraps that in a cascade of hand-written guards and a
rules-based fallback, and takes the highest-scoring option. One ply. No lookahead,
no timer, no model of the opponent's hidden hand.

The recovered `main.py` and `deck.csv` match the archived submission provenance hashes
(`c61e540b`, `92b92bac`), and the deck matches the `EXPECTED_DECK` constant asserted at
load in the inspected source.

## The deck's game plan

The 60-card list is a Marnie's Grimmsnarl ex damage-transfer package: 4 Impidimp,
3 Morgrem, 3 Grimmsnarl ex, 4 Munkidori, a 2/2 Snorunt–Froslass line, 10 Basic
Darkness Energy, and a consistency shell. Three printed effects carry the plan:

- **Punk Up** (Grimmsnarl ex): when it evolves one of your Pokémon from hand,
  search the deck for up to five Basic Darkness Energy and attach them **to your
  Marnie's Pokémon** in any way you like. This is why ten Energy is enough for a
  deck that wants a fully fuelled 320-HP attacker.
- **Adrena-Brain** (Munkidori): once per turn, *if Munkidori has Darkness attached*,
  move up to three damage counters from one of your Pokémon to one of your
  opponent's — any of them, not only the Active.
- **Freezing Shroud** (Froslass): during each checkup, put one damage counter on
  every Pokémon that has an Ability, on **both** sides — **except Froslass itself**.
  The exclusion matters: the Snorunt–Froslass line is what supplies counters for
  Munkidori to move, and Froslass does not pay for that supply out of its own HP.

Read together: Froslass manufactures damage counters on your own board, Munkidori
launders them onto the opponent's, and Grimmsnarl ex's Shadow Bullet (180 damage,
plus 30 to a benched Pokémon) converts the result into prizes. Boss's Orders drags
a chosen target into the Active spot to finish it.

## The allocation problem

Punk Up attaches only to Marnie's Pokémon. **Munkidori is not a Marnie's Pokémon.**
So the five free Energy that arrive on the evolve cannot switch on the damage
mover. Adrena-Brain has to be paid for with the ordinary one-attachment-per-turn
from hand — the same attachment the deck wants to spend on reaching a second
Shadow Bullet.

That is the deck's real decision, and it recurs every turn: turn on the transfer
engine now, or build toward the next attack. (This exclusion is a reading of Punk
Up's "your Marnie's Pokémon" clause, not a sentence printed on the card; we mark
it as an inference because it is one.)

## The experimental pilot

Controlled experiments were run with a second, deliberately simple agent, derived
from a public Mega Lucario ex sample kernel. **It is a separate product from the
submitted Grimmsnarl agent.** The counter-strategy experiments modified and measured
this pilot only; the submitted agent was never their subject. It appears elsewhere in
this repository as a fixed *opponent* — in the owned-student comparison — which is a
different role.

It scores every legal option and takes the best. The scores are a fixed ladder:
abilities 30000, playing a Pokémon 20000, an unrecognised trainer card 10000,
attaching energy about 8000, Switch 6000, Boss's Orders 3200, attacking 1000.

Target choice sits inside that. For each attack and each possible target it starts
from a value for the target; if the attack does not knock the target out, it
multiplies by `damage / target HP`, so a non-lethal hit is worth the fraction of
the target it removes. A lethal hit gets a large flat bonus instead.

This agent exists because a rule change in it is a few lines and its effect is
traceable.

## The targeting intervention

Against Alakazam decks, the threat is the attack **Powerful Hand**. In the supplied
card data it **places two damage counters for each card in the Alakazam player's
hand**. Damage counters are *placed*, not dealt as attack damage — the distinction is
in the card text and is preserved here because placement and damage are different
operations in this game. A seven-card hand is fourteen counters. (It is not a bench
snipe; we published that description and withdrew it.) Card 742, Kadabra, has a
different attack, Super Psy Bolt.

Two changes were tested.

**The card.** Xerosic's Machinations **reduces the opposing hand to three cards when it
resolves**. That is a one-time discard on resolution, not a persistent cap: the opponent
can replenish the hand on later turns, and Powerful Hand scales with whatever the hand
holds at the moment it is used.

The pilot ends up playing the card for an accidental reason worth reporting. Xerosic has
no case of its own in the scoring ladder, so it falls through to the unrecognised-trainer
default of 10000 — above Switch at 6000, Boss's Orders at 3200 and Carmine at 3000. Where
it is legal and those are its competitors, the ladder ranks it above them, whether or not
it would discard anything.

Two limits on that sentence. First, the ranking is read from the pilot's scoring code at
`rules_lucario.py:292-296`; **that source file is not included in this export**, so the
reading cannot be checked here. Second, the associated measurement is
**reachable ≈ 0.980 times per game** — an availability rate, not a count of plays and not
a claim that the card was the option taken. Both come from the GR-91 row of
[`workflow/ATTEMPTS-LEDGER.md`](../workflow/ATTEMPTS-LEDGER.md), which is the exact source
and is in this repository; the ladder constants there are not otherwise verifiable from
this tree.

**The rule.** A targeting rule adds a bonus to attacking Abra or Kadabra, the
50-HP and 80-HP stages before Alakazam, both of which the pilot can one-shot. The
mechanism, as read from the code, is indirect: bench targets are only scored when the
pilot can force a switch, which is exactly when it holds Boss's Orders — and the plan
naming a bench target is what makes Boss's Orders worth playing.

So the rule is **not** a bench snipe. What it does is **raise the score of a
gust-and-attack plan** — pull the pre-evolution into the Active spot with Boss's Orders,
then attack it there — so that plan is more likely to outrank the alternatives. Whether it
is actually chosen on any given turn depends on the legal options the engine offers and
on the board state: the rule has to have a visible Abra or Kadabra to name, the pilot has
to hold one of the deck's two Boss's Orders, and the resulting plan still has to score
above everything else available. This is a change in preference, not a guaranteed
sequence, and we have not measured how often the plan is taken.

A first attempt to measure the rule looked at bench damage events, found zero in 400
games, and was wrong about the zone rather than about the effect.

## What the panel does and does not say about the mechanism

The measured advantage concentrates in the two Alakazam cells of the seven-opponent
panel. That is consistent with the hand-and-development mechanism described above, and
it is why the mechanism is worth stating.

It is **not** a demonstration that either change helps *only* where Powerful Hand exists.
The panel tested seven implementations; the five non-Alakazam cells average −0.47 points
[−2.64, +1.71] — an interval that leaves modest benefit and modest harm both plausible.
"Indistinguishable from zero on five tested opponents" is a much weaker statement than
"inert wherever the attack is absent", and the panel supports only the first. Nor do
terminal wins alone establish how often the Xerosic-then-attack sequence actually caused
the advantage.

*No cleared replay exists of our own agents piloting the fielded 60-card list, so
any turn-by-turn line above should be read as schematic: it follows from the
printed card text and the scoring code, not from an observed game.*
