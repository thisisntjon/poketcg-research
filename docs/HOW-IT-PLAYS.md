# How it plays

Two agents appear throughout this repository. They are different programs and they
must not be confused.

## The fielded agent

The agent on the leaderboard is tetsutani's public Grimmsnarl kernel, used
unmodified. Its decision procedure is **not** a search. At each decision the game
engine hands it a menu of legal options; the kernel scores every option using
gradient-boosted-tree ensembles — five sub-models, selected by the *kind* of
decision being made — wraps that in a cascade of hand-written guards and a
rules-based fallback, and takes the highest-scoring option. One ply. No lookahead,
no timer, no model of the opponent's hidden hand. Tens of thousands of lines of
machinery ending in a single argmax over scored options.

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
  every Pokémon that has an Ability, on **both** sides.

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
from a public Mega Lucario ex sample kernel. It scores every legal option and
takes the best. The scores are a fixed ladder: abilities 30000, playing a Pokémon
20000, an unrecognised trainer card 10000, attaching energy about 8000, Switch
6000, Boss's Orders 3200, attacking 1000.

Target choice sits inside that. For each attack and each possible target it starts
from a value for the target; if the attack does not knock the target out, it
multiplies by `damage / target HP`, so a non-lethal hit is worth the fraction of
the target it removes. A lethal hit gets a large flat bonus instead.

This agent exists because a rule change in it is a few lines and its effect is
traceable.

## The targeting intervention

Against Alakazam decks, the threat is the attack **Powerful Hand**: 20 damage for
each card in the Alakazam player's hand, for one energy. A seven-card hand is 140
damage. (It is not a bench snipe; we published that description and withdrew it.)

Two changes were tested.

**The card.** Xerosic's Machinations makes the opponent discard down to three
cards, which caps Powerful Hand at 60 instead of 140. The pilot plays it for an
accidental reason worth reporting: the card has no case in the scoring ladder, so
it falls through to the unrecognised-trainer default of 10000 — the highest rung
in that block — and is played at the first legal opportunity, whether or not it
discards anything. Measured: legal on 0.980 occasions per game.

**The rule.** A targeting rule adds a bonus to attacking Abra or Kadabra, the
50-HP and 80-HP stages before Alakazam, both of which the pilot can one-shot. The
mechanism turned out to be indirect: bench targets are only scored when the pilot
can force a switch, which is exactly when it holds Boss's Orders — and the plan
naming a bench target is what makes Boss's Orders worth playing. So the rule does
not snipe the bench. **It gusts the pre-evolution into the Active spot and kills it
there**, spending one of the deck's two Boss's Orders to do so. A first attempt to
measure it looked at bench damage events, found zero in 400 games, and was wrong
about the zone rather than the effect.

Both changes help only where Powerful Hand exists. Against opponents without it,
they measure nothing.

*No cleared replay exists of our own agents piloting the fielded 60-card list, so
any turn-by-turn line above should be read as schematic: it follows from the
printed card text and the scoring code, not from an observed game.*
