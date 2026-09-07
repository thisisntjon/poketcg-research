# NUMBERS INVENTORY — every quantity we can obtain, and the exact command to obtain it

**Status:** CURRENT. Authored by the Auditor 2026-08-06 at `origin/main` `db969092c0`.
**Discipline:** each row is either **MEASURED** (I ran it this session — figure shown), **AVAILABLE**
(the producer exists and is verified present; figure not yet taken), or **BLIND** (not obtainable
from data; needs simulation or is genuinely unknown). Nothing here is quoted from a summary surface
without its producer named.

> ## ⚠️ CORRECTION 2026-08-06 — THIS FILE'S ORIGINAL HEADLINE WAS WRONG. READ THIS FIRST.
>
> v1 opened with: *"the fielded scorer **never imports the attack table**. We decide with
> `len(pokemon.energies) * 300` while `cg.api.all_attack()` sits one import away."*
> **Both halves are wrong, and I am the author.**
>
> **1. Outgoing damage is already exact.** The live attack site applies `weakness ×2` /
> `resistance −30`, compares `damage` to `op_pokemon.hp` for KO, scales by `damage/hp` when not
> lethal, and carries a game-winning-lethal branch. `len(energies) * 300` is the **target
> valuation** term — a different quantity from damage. Our own four attacks are hardcoded, which is
> correct: we only ever play our own deck.
>
> **2. The `all_attack` gap is in the INCOMING-threat model, which is DEAD CODE.**
> `evaluate_state` (the `assumed_energies * 40` fallback) is reachable **only** through
> `SEARCH_ALGO`, which returns `None` unless `_SEARCH_OK and USE_SEARCH`. Ash's F0b census measured
> **`search_begin_attempts = 0`** on the fielded bytes. Classify every threat-model finding in §7 as
> **`SEARCH_ONLY`**. The 87.4% fallback rate is **observation reach on dead code**, not decision
> impact, and it was wrong of me to price it as the strongest live lane.
>
> **3. The fielded bundle is 24 files:** `main.py` (543 lines), `deck.csv`, `cg/`, metadata.
> **No `beliefs.py`. No `rules_lucario.py`.** Any finding measured outside those 24 files is
> September material at best.
>
> **Mandatory check before funding any lane: is the file in the tar, and is the function on the
> live call path?**
>
> **4. The `2.8 pp` A/A floor in §6.3 is approximately CORRECT.** A later claim of mine that it was
> "~80% too wide" is **withdrawn** — it compared a single-arm SD against a difference threshold at a
> different n. ~~Measured paired A-minus-A difference SD = **2.199 pp** at n=400 → 95% threshold
> 4.31 pp → **2.49 pp at n=1200**, within ~10% of the banked 2.8 pp.~~ **[RETRACTED 2026-08-23:
> the 2.199 pp figure is retracted (`canon/RETRACTIONS.md`) — the dated 120k-game measurement
> gives σ_Δ = 3.529 pp @n=400 / 2.520 pp @n=1200 (`canon/MEASURED-2026-08-06.md` §2); the
> engine exposes no seed and Cov(arms)=0 is measured, so a paired SD below the unpaired σ_Δ is
> not a valid noise floor.]**
>
> Full amendment record: `workflow/AUDITOR-LADDER-MU-FINDINGS-2026-08-06.md` §0.

---

## 0. The six sources at a glance

| # | Source | Headline quantity | State |
|---|---|---|---|
| 1 | Replays | **264,548** field episodes (re-measured 2026-08-23, probe C-I; was 209,926 per the 07-27 census) · **2,426** of our own · **~246,600** of our own decisions | MEASURED |
| 2 | Prior investigations | **2,656** banked artifacts · **47** GATES rows · **~24** dead-end rows | MEASURED |
| 3 | Tools | **326** harness programs; `eval.py` is the richest emitter | MEASURED |
| 4 | Factory | registry v1 — actors/authority/prohibitions; **non-actuating** | AVAILABLE |
| 5 | Learning loop | teacher μ **711–753** vs wall **~805–815**; clock **8 s** vs **~0.3 ms** used | MEASURED |
| 6 | Referee / 9 gates | **8 of 8 required GREEN**; local A/A floor **2.8 pp** | MEASURED |

---

## 1. REPLAYS — what the recorded games give us

### 1.1 Corpus scale (MEASURED)

| Store | Bytes | Episodes | What it is |
|---|---:|---:|---|
| `D:\ptcg-episodes\raw\` | 38.81 GB (dated dirs) | **264,548** | the whole field; re-measured 2026-08-23 (probe C-I): 53 dated dirs 06-16→08-07, one zip/day (row formerly read 45.76 GB / 209,926 / 75 dated dirs — the 07-27 census) |
| `D:\ptcg-episodes\replays-omniscient\` | 8.10 GB | **2,426** | **our own fielded games**, 367 distinct opponents |
| `C:\…\R1\e3night1\` | 0.06 GB | 50 | self-play, replays+traces paired 1:1 |
| `D:\policy_rows` | 129.16 GB | ~24.8 M rows | `(obs, action, result, label)`; joins to raw by `game` = `"date:episode_id"` |

Per episode (2026-07-27 LX census, **not** re-measured): ~177 frames, ~162 with a real choice →
**~34 M decision-states** in `raw`.

### 1.2 State recoverability (MEASURED — this is the load-bearing part)

**Every episode stores TWO seat-entries per step, one view per seat.** Each hides the *other*
player's hand; the union recovers both.

```
episode-84927907, mid-game step:
  entry0 (seat 0 view): player[0].hand = 7    player[1].hand = None
  entry1 (seat 1 view): player[0].hand = None player[1].hand = 5
  UNION               -> both hands exact
```

Cards carry `{"id", "playerIndex", "serial"}` — **a unique serial per physical card, in contiguous
60-blocks per player** (p0 `3..62`, p1 `63..122`). Therefore:

| Quantity | Value | Basis |
|---|---|---|
| positionally known per player, mid-game | **22.0/60** and **23.6/60** (37–39%) | 25 states sampled, both-seat union, serial-level |
| the unseen set | **exactly `deck ∪ prize`** | serial-block complement — nothing else can hide |
| composition of the unseen set | **exact once the decklist is known** | decklist − observed |
| decklist convergence, cross-game | **40 → 50 → 53 → 54 → 58 of 60** over six games of one opponent | serial+id union per team |
| residual uncertainty | **which 6 of ~37 are prizes** | `prize` elements are `null` (face-down) |

**Consequence:** a determinization is *exact in composition* with a bounded 6-of-~37 prize sample.
This is **strictly more information than the live agent had** — it never saw the opponent's hand.
That is what makes replay a teacher signal.

### 1.3 Per-step fields available (MEASURED)

`observation.current` → `turn`, `turnActionCount`, `yourIndex`, `firstPlayer`, `supporterPlayed`,
`stadiumPlayed`, `energyAttached`, `retreated`, `result`, `stadium`, and per player:
`active`, `bench`, `benchMax`, `deckCount`, `discard`, `hand`, `handCount`, `prize`,
`poisoned`, `burned`, `asleep`, `paralyzed`, `confused`.
Pokémon carry `hp`, `energies`, `energyCards`, `appearThisTurn`.
Also per step: `select{type,context,minCount,maxCount,option[]}`, `logs`,
**`remainingOverageTime`** (the live clock), `action`, `reward`, `status`,
and `search_begin_input` (opaque encoded string — **no decode entrypoint in `cg.api`**).

Episode level: `info.TeamNames`, `info.EpisodeId`, `rewards[2]`,
`configuration{actTimeout, episodeSteps, runTimeout, seed}`.

### 1.4 Our own agent, from our own games (MEASURED)

| Quantity | Value | How |
|---|---|---|
| sampled fielded record | **16 W / 42 L = 27.6 %** | 59 episodes, `rewards[]` vs our seat |
| real (multi-option) decisions per game | **~102** | `len(select.option) > 1` at `yourIndex == our seat` |
| **our own decisions, whole store** | **~246,600** | 102 × 2,426 |
| distinct opponents faced | **367** | `info.TeamNames` over 399 sampled |

### 1.5 Field/opponent coverage (MEASURED)

In a 500-episode sample of the 2026-08-04 dump: **149 distinct teams**, with the field #1
(`Raihan Ramadistra`) in **40**, `213tubo` in 37, `Majkel1337` in 31. Across 50 days that is
**thousands of games per top agent**, each with both hands recoverable.

### 1.6 How to get them

```bash
# field episode, both-seat union
python - <<'PY'
import zipfile, json
z = zipfile.ZipFile(r'D:\ptcg-episodes\raw\<DATE>\pokemon-tcg-ai-battle-episodes-<DATE>.zip')
d = json.loads(z.read('<EPISODE_ID>.json'))
for step in d['steps']:            # step is a 2-list: one entry per seat
    for ent in step:               # union ent['observation'] across both entries
        ...
PY
```
`policy_rows` join key is `game == "<DATE>:<EPISODE_ID>"` — the same episode id as the zip member.

---

## 2. PRIOR INVESTIGATIONS — what is already banked

### 2.1 Volume (MEASURED, `git ls-tree origin/main`)

| Path | Files |
|---|---:|
| `ptcg-agent/experiments/analysis/` | **1,711** |
| `workflow/research/` | **660** |
| `workflow/reports/` | **113** |
| `workflow/receipts/` | **102** |
| `ptcg-agent/docs/experiments/` | **70** |
| **total** | **2,656** |
| `workflow/GATES.md` promotion rows | **47** |

### 2.2 The load-bearing banked numbers (each with its register row)

| Number | Meaning | Register |
|---|---|---|
| **136 W / 314 L = 30.2 %**, n=450, errors 0, `search_pimc_zero_det_decisions` 0 | determinized search on our champion deck | seq-155 receipt; closes the search lane |
| **24–0** | V13's dormant search, once alive, vs its own fallback | `DEAD-ENDS` A2 (SK-294 scope guard) |
| **476–554 μ** | H+S+D stack as shipped, on ladder | A1 |
| **0.744 AUC** | imitation wall on the 148-feature representation | A3 |
| **711–753 μ** teacher vs **~805–815** wall | pre-wall BC closed on arithmetic | A13 |
| **0.345** vs **0.587** | value-net top-1 vs champion on recorded elite actions | A11 |
| **Δ −0.40 pp**, CI [−3.05, +2.25] | equal-compute value-leaf | GATES M5 |
| **9.84 pp** | MDE at n=400/arm — *34 of 34 declared sample sizes cannot resolve 5–8 pp* | GATES reclassification |
| **753.1 μ** pair-mean, spread **26.2 μ** | protected floor | MASTER_DASHBOARD |
| **31–40 μ** | matched-maturity same-bytes σ | PLAN assumption 6 |
| **422 μ** | cross-archetype deck swap on ladder | A7 |

### 2.3 How to get them

```bash
python ptcg-agent/harness/receipt_chain.py <IDENTIFIER>     # date-ordered chain
```
**Tool limit, travels with every use:** the date-ordered chain is the deliverable; the disposition
label is advisory and over-reports OPEN. Read the latest hits yourself.

---

## 3. TOOLS — what our programs emit when run

**326 harness programs** (`ptcg-agent/harness/*.py`, excluding tests).

### 3.1 `eval.py` — the richest emitter (MEASURED, schema read from a live artifact)

```
matchups[]              opponent, games, wins, losses, draws, win_rate,
                        wilson95[lo,hi], candidate_errors, opponent_errors,
                        unknown_errors, avg_steps,
                        candidate_move_time{p50,p95,p99}, candidate_total_time{...}
execution               total_games, elapsed_seconds, workers, mode,
                        latency_claims_valid, games_jsonl
raw_policy_decision_stats  raw_calls, exceptions, illegal, repairs
fallback_substitutions, fallback_details[]
pin2                    requested, applied
provenance              schema_version, argv, cwd, python,
                        git{commit,branch,dirty,status_porcelain},
                        deck{path,sha256}, config{path,sha256},
                        pool{keys,selfcheck,hash},
                        hook_resolution{archetype,total,configured_archetype_total,
                                        counts,bind_calls,bind_pilots}
```

**Throughput (MEASURED, promoted to VERIFIED as PLAN assumption 5):** **21.71 games/s** —
1,600 games in **73.696 s**, single worker.
**Binding scope limit:** local in-process screening only, measured *unpinned*
(`pin2.applied=false`, `latency_claims_valid=false`) — **never citable as Kaggle-runtime or
match-clock evidence.**
**Consequence:** local screening is effectively free (F4 ≈ 74 s; F5 at n≥1200 close behind), so the
funnel bottleneck is **causal labelling, not evaluation**.

```bash
python ptcg-agent/harness/eval.py --candidate-source <path/to/main.py> --games <N> --workers 1
```

### 3.2 The other decision-grade emitters (AVAILABLE, verified present)

| Tool | Numbers it produces |
|---|---|
| `r2_verify.py` | **exact this-turn lethal** — verified winning line or `no_verified_win` (abstains; never guesses) |
| `t2_lethal_solver_census.py` | `build_true_determinization(replay_step, your_index)` → the six zone lists; trace row *i* ↔ replay step *i*, **125/125 proven** |
| `run_f0b_v13_census.py` | `_SEARCH_OK`, `USE_SEARCH`, `search_begin_attempts`, `choose_maxcount_truncated`, agent invocations, main-context prompts, p50/p99 |
| `decision_diff_gate.py` / `_cli.py` | decision-divergence rate between two policies on a frozen corpus |
| `block_confirm_cli.py` | complete 2×2 blocks; incomplete block contributes **zero** games; incumbent identity checked against a full 64-hex sha before scheduling |
| `master_dashboard.py` | floor pair-mean, within-pair spread, latest-2 refs/scores/ages, days-since-submit, cutoff snapshot |
| `verify_curve_receipt.py` | validates the exact-runner curve receipt against the frozen panel |
| `oracle_labeler.py` | perfect-info oracle vs champion divergence set. **RAN HISTORICALLY (corrected 2026-08-23, probe C-E — this row said "NEVER RUN"): PR #2161, 331 games / 44,366 states, scoped lethal NO-RUNTIME-GAIN; needs a new consumer** (TOOLS-OUTPUT-EXISTS T-ORACLE; ATTEMPTS-LEDGER §3f) |
| `submit_gate.py` → `submit_hashgate.py` | slot budget; hash-bound submission (raw kaggle submit retired) |
| `receipt_chain.py` | date-ordered disposition chain per identifier |
| `active_comms_lint.py` | dispatch/receipt schema validation, fails closed |

### 3.3 A measured caution

`eval.py --candidate-source` emits `hook_resolution.total = 0` **even on a no-candidate baseline
run.** I control-tested this across three artifacts. **It therefore has no discriminating power on
that path and must not be cited as activation evidence.** Activation requires an explicit counter in
the candidate itself.

---

## 4. FACTORY — what the registry gives us

`workflow/factory/registry.schema.json` — **`ptcg.factory.registry/v1`, non-actuating.**
Required blocks: `registry_id`, `registry_version`, `published_at`, `exact_base`, `mode`,
`default_write_effect`, `authority_precedence`, `authority_sources`, `capability_catalog`,
`prohibition_catalog`, `write_surface_catalog`, `separation_groups`, `resources`, `actors`,
`sessions`, `backup_policies`, `authority_conflicts`.

**Numbers it yields:** counts and conflict sets over actors/authority/prohibitions/write-surfaces —
*governance* quantities, not game quantities. Semantic constraints additionally enforced by
`factory_model.validate_registry`. **It produces no strength evidence and must never be cited as
such.**

---

## 5. LEARNING LOOP — what it has produced and what it can still produce

### 5.1 Measured outcomes (from `PLAN-LEARNING-LOOP.md`, all with their caveats)

| Number | Meaning |
|---|---|
| **2 / 80** | gen-1's four learned cells in real games — *despite* **+19–27 pp** elite-agreement. The training signal is **provably disconnected** from winning |
| **711–753 μ** | teacher μ (G1-verified) against a **~805–815** wall → criterion 8, ARITHMETIC-CLOSED pre-wall |
| **0.95–1.0** | M2 AUC |
| **58.9 %** | M1 divergence |
| **64 %**, n=50, CI floor **50.1 %** | BOSS assumption |
| **[0.490, 0.612]**, n=250 | "a better teacher is purchasable" — a **straddle**; recorded as **EVIDENCE-HELD, NOT REFUTED**. A straddle cannot establish an absence |
| **zero** | closed prospective calibration rows ever (harvest-F1) |
| **8 s cap vs ~0.3 ms used** | `ClockBudget` per decision — **prices search-on-top headroom**; ~4 orders of magnitude unused |

### 5.2 Status

Phase 1 executed (zero-game half complete). **Phase 2 DAgger: tool delivered, RE-FILED to Sept-13**
by the teacher-ceiling gate — not a pre-wall bronze play. Phase 3 (exceed-teacher go/no-go) is now
the only phase that could contribute pre-wall.

**The 8 s / 0.3 ms figure is the most under-used number in this file.**

---

## 6. REFEREE + THE NINE GATES — what the measurement machine gives us

### 6.1 Gate states (MEASURED, `RELIABILITY-MANIFEST.json`, schema `v2-split-identity`)

| Row | Required | State |
|---|---|---|
| `identity_artifact` | ✔ | **GREEN** |
| `failure_attribution` | ✔ | **GREEN** |
| `concurrent_stratification` | ✔ | **GREEN** |
| `declared_estimand` | ✔ | **GREEN** |
| `exact_runner_curves` | ✔ | **GREEN** |
| `aa_rebuild` | ✔ | **GREEN** |
| `panel_multiplicity` | ✔ | **GREEN** |
| `doctrine_coherence` | ✔ | **GREEN** |
| `identity_episode` | optional | YELLOW (accepted; does not gate) |

**8 of 8 required rows GREEN → the promotion freeze is lifted.** Rule as written: *sealed Confirm
may not license a Jon promote packet until every required row is GREEN; partial prose overrides do
not unfreeze.*

### 6.2 What the referee emits (MEASURED, from a curve receipt)

```
n_plan, multiplier, design_id, code_sha256, seed_base
condition_results[<condition>].terminal_outcomes{FAIL, PASS, UNDECIDED,
                                                 AMBIGUOUS_AT_NMAX, INVALID}
condition_results[<condition>].bound_kind   # clopper_pearson_upper_95 | _lower_95
condition_results[<condition>].bound
```

Measured at `n_plan = 2556` across the nine conditions, e.g.:

| condition | outcome | bound |
|---|---|---|
| `clean_boundary_null` | FAIL 9,382 / PASS 20 / AMBIG 598 | upper-95 **0.00290** |
| `clean_plus6pp` | PASS 9,348 / FAIL 17 / AMBIG 635 | lower-95 **0.93059** |
| `drift_boundary_null` | FAIL 9,275 / PASS 24 / AMBIG 701 | upper-95 **0.00337** |

Plus the refusal conditions (`truncation_refusal`, `unattributable_refusal`) which must return
**UNDECIDED / INVALID** — a control that cannot refuse is not a control.

### 6.3 Power arithmetic (the number that governs every screen)

**MDE at 80 % power = `2.8 × σ_Δ(n)` with the MEASURED σ_Δ (`canon/MEASURED-2026-08-06.md`
§2), not the binomial `2.8 × sqrt(0.5/n)` — the measured noise is super-binomial, so the
binomial formula understates the MDE. (Corrected 2026-08-23, probe C-F: this table previously
printed the binomial 5.7 pp at n=1200; the measured value is 7.06 pp.)**

| n/arm | MDE (measured σ_Δ) | verdict |
|---:|---:|---|
| 100 | ~19.8 pp | resolves nothing a rules patch produces |
| 400 | **9.88 pp** | cannot resolve a 5–8 pp claim → **n=400 is KILL-ONLY, never promotes** |
| 1,200 | **7.06 pp** | the protocol floor; a clean 5 pp claim needs n≈2,400 (MDE 4.55 pp) |

**Local A/A floor, measured 2026-08-06: 2.8 pp.**

---

## 7. THE ENGINE MATH — exposed, in-bundle, and unused  
**⚠️ `SEARCH_ONLY` — see the correction block at the top of this file. The unused-`all_attack` gap is in dead code.**

| Surface | Measured | At Kaggle runtime? |
|---|---|---|
| `cg.api.all_card_data()` | **1,267 cards × 18 attrs** — `hp`, `weakness`, `resistance`, `retreatCost`, `attacks`, `skills`, `evolvesFrom`, `stage1/2`, `basic`, `ex/megaEx/tera`, `energyType`, `cardType`, `aceSpec` | **yes**, stdlib |
| `cg.api.all_attack()` | **1,556 attacks × 5 fields** — `attackId`, `damage`, `energies`, `name`, `text`. **1,175 (75.5 %) carry a declared numeric damage** + exact energy-cost list | **yes**, stdlib |

**BLIND:** **381 of 1,556 attacks (24.5 %) have `damage == 0`** — effect exists only as English
`text`; likewise **all `skills`**. These are computable **only by engine simulation**, never by
formula.

### What the fielded scorer actually uses (MEASURED — grep of the shipped `main.py`, 543 lines)

| Primitive | Occurrences |
|---|---:|
| `all_attack` | **0** |
| `retreatCost` | **0** |
| `weakness` | 1 |
| `resistance` | 1 |
| `all_card_data` | 2 |

…against **58 scoring lines of hand-tuned constants**: `prize_count*2000`, `len(energies)*300`,
`SNOVER +950`, `RIOLU +800`, `stage2 +500`, `8000`, `500000`, `220/300`.

### Directly computable, today, from data already in the bundle

exact post-weakness/resistance damage · KO vs no-KO against `hp` · resulting prize swing ·
energy-cost satisfiability · exact `retreatCost` payability · exact this-turn lethal (`r2_verify`).

**Every one of those is currently approximated by a guessed integer.**

---

## 8. What is BLIND — the honest list

1. **381 attack effects + all abilities** — text only; engine simulation is the only evaluator.
2. **The prize split** — which 6 of the ~37 unknown cards; bounded belief, must be *sampled*
   (`BELIEF_ROBUST`), never *reconstructed* (`TACTICAL_INVARIANT`).
3. **`search_begin_input`** — present at every step, opaque, **no decode entrypoint exists**.
4. **Local→ladder transfer coefficient** — **zero** closed prospective calibration rows, ever.
   PLAN assumption 3, the most load-bearing unverified item.
5. **Kaggle-runtime timing** — every local timing figure is unpinned
   (`latency_claims_valid=false`). The 8 s budget is *declared*, our ~0.3 ms is *local*.
6. **Episode → submission_id attribution** — the one YELLOW gate; accepted, does not gate promotion.

---

## 9. The measurement nobody has taken

Everything above says the exact quantities are **obtainable**. Nothing above says they would
**change a decision**.

> **DECISION-DIFF, over our ~246,600 banked multi-option decisions: for each, compute the shipped
> scorer's chosen option and the option chosen when the exact quantity replaces the guessed
> constant. Report the % where the choice CHANGES, bucketed by decision class, weighted by the
> outcome label we already hold on every row.**

Zero games. Zero ladder. Zero new tooling — `decision_diff_gate.py` and the replay union are both
in hand. **A ~0 % change rate kills the idea cheaply and honestly; that is the point of measuring
before authoring.** No candidate should be compiled off §7 until this number exists — an arm that
changes ~0 % of decisions is vacuous and must never consume a screen.

---

*Every MEASURED figure in this file was produced by the Auditor on 2026-08-06 against
`origin/main` `db969092c0`, the live `cg` engine, and the stores on `C:` and `D:`. Figures marked
as carried (§1.1 episode/frame counts, from the 2026-07-27 LX census) are the only ones not
re-measured. Re-measure before citing after any bulk pull.*
