# The Fleet: Building a Research Factory for Pokémon TCG

**Sixty days of solo-directed AI research into hand disruption, Energy recovery, and the whole-game cost of a good move.**

I am Jonathan Simone. I directed AI research and coding agents across vendors to turn strategic questions into explicit interventions, test complete games, challenge the conclusions and preserve what should change next. This repository makes the research method and its concrete outputs inspectable.

[**Read the current report**](docs/STRATEGY-WRITEUP.md) · [Report PDF](docs/downloads/FINAL-REPORT.pdf) · [Evidence guide](docs/downloads/EVIDENCE-GUIDE.pdf) · [Portable evidence ZIP](docs/downloads/PTCG-EVIDENCE.zip)

## Three decisions, with evidence

| Strategic question | What the experiment established | Inspect it |
|---|---|---|
| Can disruption and targeting weaken Alakazam's resources? | Separate card and targeting changes; combined gains of 20.42 and 18.75 percentage points against two tested Alakazam implementations. The other five averaged −0.47 [−2.64,+1.71], leaving broader benefit unresolved. | [Counter methods and rows](docs/current-evidence/numerical/METHODS.md) |
| Does recovery earn a slot taken from search? | One Poké Pad becomes Energy Recycler. The first target batch gained +7.30 points; the later wider panel was −1.08 with an interval crossing zero. General promotion was unsupported. | [Recovery case and aggregate recount](docs/current-evidence/cases/recycler/README.md) |
| Should projected knockouts receive a dominant preference? | The same bonus produced opposite observed effects across seven implementations. This challenges a universal default; it does not establish a successful conditional selector. | [Knockout case and all 8,400 rows](docs/current-evidence/cases/ko/README.md) |

The report explains the card mechanics, competing choices, outcome conventions and limitations behind each decision. Its [source notes](docs/EVIDENCE-MAP.md) connect claims to the selected evidence.

## See how the research worked

- [Five traced research cases](docs/current-evidence/factory/cases/FACTORY-IN-ACTION.md): policy investigation, labeling, comparison repair and research memory.
- [Original learning components](docs/current-evidence/factory/proofs/ORIGINAL-COMPONENTS.md): actor-visible state, source/target option features, recurrence and sequential stopping; seven prescribed-score decoder checks.
- [Representation experiments](docs/current-evidence/factory/proofs/representation/README.md): two retained cache comparisons and a portable arithmetic check; capacity also increased, and imitation agreement does not measure playing strength.
- [Research inventory](workflow/inventories/sri/INDEX.md) and [corrections](workflow/canon/RETRACTIONS.md): a dated map of the larger investigation, including its limitations. This is a snapshot; not every indexed source or regeneration dependency is redistributed.

## Run the checks and understand their scope

[Reproduction instructions](docs/REPRODUCING.md) distinguish standard-library outcome/aggregate checks from the optional CPU PyTorch selection demonstration. The commands recount saved evidence or exercise generic selection constraints. They do not replay historical games, retrain the student or reconstruct every original execution environment.

My Simulation entry was Tetsutani's unmodified public c61 Grimmsnarl player. The experimental Lucario policies and learner are separate products. The counter credits makthanithin's Apache-2.0 community_1084 foundation; Roman Rozen's V13 supplied policy-study material. [Contributions](docs/current-evidence/CONTRIBUTIONS.md) separates my interventions and components from these public foundations. Repeated retained improvement in an integrated learned player remains future work.

[Kaggle entry](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/measure-everything) · [Researcher guide](docs/FOR-RESEARCHERS.md) · [Opponent provenance](docs/OPPONENT-PROVENANCE.md) · [Release scope](docs/RELEASE-REVIEW.md)

Project-authored materials use the [MIT license](LICENSE), with [credits and competition-use boundaries](NOTICE). The export omits organizer engine/card assets, artwork, full training weights and third-party policy implementations. It is selected research evidence, with portable checks and explicit historical limits.
