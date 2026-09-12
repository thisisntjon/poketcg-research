# The Fleet: evidence guide

**Jonathan Simone · Pokémon TCG AI Battle Challenge Strategy**

The report follows three game-strategy experiments, the entered deck and a separate learning branch. This package lets a reader inspect the argument, reproduce saved-result arithmetic and distinguish those checks from historical gameplay.

## Start with the strategic decisions

| Case | Question and supported result | Start here |
|---|---|---|
| Hand disruption and targeting | Separate card/rule changes; large counter gains in two tested Alakazam cells, broader benefit unresolved. | [Counter methods](numerical/METHODS.md) |
| Energy recovery | One search slot becomes recovery. First target batch improves; the wider panel does not establish improvement. | [Recycler case](cases/recycler/README.md) |
| Knockout priority | One large scoring bonus produces opposite effects across seven implementations. A universal upgrade is unsupported. | [KO case](cases/ko/README.md) |
| Entered player and deck | Tetsutani's public c61 is the unmodified entry. Its score is separate from every research result. | [Source notes, reference 7](SOURCE-NOTES.md) |
| Owned learning components | Source/target option features, recurrence and sequential STOP; seven prescribed-score checks, with competitive learning still unfinished. | [Original components](factory/proofs/ORIGINAL-COMPONENTS.md) |

## Recount the results

From the extracted archive, the following checks use Python's standard library and no game engine:

```text
python -X utf8 numerical/verify_results.py
python -X utf8 cases/recycler/verify.py
python -X utf8 cases/ko/verify.py
```

See [REPRODUCING.md](REPRODUCING.md) for exact invocation details, remaining source/representation/sensitivity checks and the optional CPU PyTorch selection demonstration. Counter and KO arithmetic uses exported terminal outcome rows. Recovery arithmetic uses exported historical aggregate receipts; original game rows were not recovered. No command above replays games or trains a model.

## Follow the research process

[Five traced research cases](factory/cases/FACTORY-IN-ACTION.md) show policy investigation, labeling, review/repair and research memory. [SOURCE-NOTES.md](SOURCE-NOTES.md) connects report references to source excerpts, identities, methods and limitations. [CONTRIBUTIONS.md](CONTRIBUTIONS.md) separates original work, public foundations and future integration.

The public repository is [poketcg-research](https://github.com/thisisntjon/poketcg-research). The evidence is available without requesting access. The package omits organizer engine/card assets, artwork, full player weights and third-party policy implementations. Its [NOTICE](NOTICE.txt) preserves rights and competition-use boundaries. Source hashes establish file identity; they do not certify complete historical execution or universal strategy quality.
