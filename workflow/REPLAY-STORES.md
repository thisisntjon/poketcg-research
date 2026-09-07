# REPLAY STORES — what we hold, what each one can answer

**Status:** CURRENT. **Every figure below was measured on 2026-08-06 by the Auditor**, on disk,
not quoted from a prior document. Re-measure before citing after a bulk pull.

> **READ THIS FIRST - THIS FILE WAS WRONG ONCE. HERE IS THE CORRECTION, AT THE TOP.**
>
> An earlier revision of this document (and the F0 redirect built on it) claimed that
> `replays-omniscient` is **not** engine-branchable and that `R1\e3night1\` (50 games) is the only
> usable substrate. **That conclusion is REFUTED and withdrawn.**
>
> **Every episode - in `raw` AND in `replays-omniscient` - stores TWO seat-entries per step, one
> view per seat.** Each view hides the *other* player's hand; the union recovers both. The original
> error was reading a single seat-view and generalising. Verified on
> `replays-omniscient/episode-84927907`, mid-game step: `entry0` shows `p0.hand=7 / p1.hand=None`,
> `entry1` shows `p0.hand=None / p1.hand=5`.
>
> **`PLAN.md` section 5b's "~10^5 of our own ladder decision points" was therefore CORRECT**, and the
> redirect to a 50-game corpus was an over-correction. Branchability is a **four-way** property,
> not a yes/no - see section 1.

---

## 1. The one question that decides which store you need

**Do you need to BRANCH the engine from a recorded state** (force action A vs B and run sibling
continuations)? That requires `build_true_determinization`
(`ptcg-agent/harness/t2_lethal_solver_census.py`), which reads, per player:

```python
your_deck      = players[your_index]["deck"]      # CONTENTS, not deckCount
your_prize     = players[your_index]["prize"]
opponent_deck  = players[1 - your_index]["deck"]
opponent_prize = players[1 - your_index]["prize"]
opponent_hand  = players[1 - your_index]["hand"]
```

**Those five fields must be populated lists.** A store that carries only `deckCount` cannot be
branched — it can still answer frequency, divergence, and behavioural questions.

### The four branchability classes (use these terms; "branchable" alone is ambiguous)

| Class | Meaning | Stores |
|---|---|---|
| **DIRECT** | structured hidden zones stored as contents; read and go | `R1\e3night1eplays\` |
| **RECONSTRUCTED** | two-seat union + serial complement + later-reveal retrodiction recovers the world | `raw`, `replays-omniscient` |
| **BELIEF-BRANCHABLE** | the above, plus a bounded sample over the residual (the 6-card prize split) | `raw`, `replays-omniscient` |
| **CENSUS-ONLY** | frequency / reach / loss-weight; no state reconstruction | `policy_rows` alone, until joined by its `game` key |

| If you need... | Use |
|---|---|
| a zero-build feasibility spike, today | `R1\e3night1\` (section 2) - DIRECT, 50 games |
| engine branching at ladder scale | `raw` / `replays-omniscient` - RECONSTRUCTED / BELIEF-BRANCHABLE |
| decision frequency, loss-weight, reach | `policy_rows`, joined to `raw` by `game` = `"date:episode_id"` |
| field census, meta, opponent decklists | `raw` |

**A determinization built by reconstruction is `BELIEF_ROBUST`, never `TACTICAL_INVARIANT`.** The
residual prize split is sampled, not known. Do not silently swap the label.

**NOT YET PROVEN, and it gates scaling:** that a reconstructed determinization is *accepted by the
engine* end-to-end (`search_begin` -> `search_step` on forced A and B). The information is
demonstrably present; engine acceptance is a separate claim and has not been reproduced.

## 2. `C:\Users\thisi\Desktop\R1\e3night1\` — THE ENGINE-BRANCHABLE CORPUS ✅

**0.06 GB · 50 replays + 50 traces, paired 1:1 · this is the corpus `t2_lethal_solver_census.py`
actually runs on.**

```
R1\e3night1\
  replays\game_0000.json … game_0049.json     <- 1 JSON array per game; supplies the DETERMINIZATION
  traces\ game_0000.trace.jsonl … 0049        <- 1 row per decision; supplies the DECISION ROWS
  ledger_48.jsonl                             <- 48 rows
  MANIFEST.sha256.json
  brick_split_classification{,_v2,_v3}.json · brick_split_receipt.json
```

**Verified populated (measured 2026-08-06, `game_0000.json`) — BOTH seats, full contents:**

| replay index | turn | player[0] deck / hand / prize | player[1] deck / hand / prize |
|---|---|---|---|
| 0   | 0  | 60 / 0 / 0 | 60 / 0 / 0 |
| 63  | 6  | **34** / 3 / 6 | **26** / 6 / 5 |
| 124 | 14 | **25** / 2 / 6 | **8** / 9 / 1 |

Deck list lengths match `deckCount` exactly at every step checked, for both seats. **This is a
genuinely omniscient record and `build_true_determinization` works on it.**

**The replay and the trace are not interchangeable — you need both.**
`process_one_game(replay, trace_rows, …)` consumes them together:

- **trace row** = `{seat, observation, action}`. `observation.current.players[]` here is the
  **acting agent's own view**: own hand populated, **opponent hand empty by construction**, and
  no deck contents. Use it for *which decisions happened and what was chosen*.
- **replay step** = `{select, logs, current, selected, ver}`. `current.players[]` here carries the
  **true hidden zones for both seats**. Use it for *the determinization*.

Joining rule (proven in-repo, 125/125): `trace row i` ↔ `replay step i`.

> **SCALE LIMIT, state it in any receipt that uses this store: 50 games.** That is ample for a
> feasibility spike or a single forced-action state. It is **not** a reach or prevalence sample —
> do not compute frequency claims from 50 games and do not present them as corpus-wide.

Related banked ledgers: `ptcg-agent/experiments/analysis/2026-07-30-5080-e3night{1,2,2-part2}-loss-harvest-ledger.jsonl`.

---

## 3. `D:\ptcg-episodes\raw\` — the official daily dumps (source of truth) 📦

**Re-measured 2026-08-23 (probe C-I; walked on-disk, zip entries counted): 264,548 episode
files across 53 date-named directories 2026-06-16 → 2026-08-07, 38.81 GB in the dated dirs
(plus 25 non-dated working dirs at the same root) · one
`pokemon-tcg-ai-battle-episodes-<date>.zip` per day.** This reconciles the two previously
conflicting counts: ATTEMPTS-LEDGER §3b's "~264k raw episodes" (08-09) matches the store; the
figure below was a 07-27 census of the first 41 days only. *(The former header line here read
"45.76 GB · 75 dated directories" — both stale.)*

Historical census of 2026-07-27
(`workflow/research/2026-07-27-LX-replays.md`, figures from that report):
**209,926 episodes** across 41 contiguous days 06-16→07-26, ~4,450–4,650 episodes/day, mean
**~177 replay frames/episode (~162 with a real choice)** ⇒ **~34 M decision-states** (the
frames/episode and decision-state rates were not re-measured on 08-23).

Use for: prevalence, meta/deck census, opponent intel, loss-endpoint classification, field drift.
**Not** directly branchable — extract first and check the zones before assuming otherwise.

**Compliance: these are Pokémon-provided materials. They are git-ignored on purpose and must never
be committed.** Seven episode replays reached `main` on 2026-08-05 via a mass sweep commit and had
to be untracked (`#2647`). Keep bulk pulls out of the repo; ~21 GB/day disk budget.

---

## 4. `D:\ptcg-episodeseplays-omniscient\` - OUR OWN GAMES, RECONSTRUCTED-branchable

**8.10 GB - 2,426 files - 1,488 of them contain us - 367 distinct opponents.**

**This is our own fielded-agent corpus, not the field.** Two-seat format, same as `raw`.

| Quantity | Value |
|---|---|
| our record | **679 W / 805 L = 45.8%** over **n=1,484** decisive (4 null-reward) |
| our multi-option decisions | ~102/game -> **~246,600** across the store |
| positional knowledge, late-game / long games | **42.9/60 = 72%** |
| positional knowledge, mid-game / long games | 28.2/60 = 47% |
| positional knowledge, late / short games | 23.4/60 = 39% |
| positional knowledge, mid / short games | 16.3/60 = 27% |

**Two different "world fraction" numbers exist and must never be conflated.**
**POSITIONAL** (which physical serial sits in which zone) is the table above.
**COMPOSITIONAL** (which card identities are accounted for once the decklist is pinned) is higher.
A branching claim needs the positional figure; a belief claim may use the compositional one. State
which one you mean, every time.

`observation.search_begin_input` is present at every step but is an **opaque ~82-char encoded
string**, and `cg.api` exposes no decode/restore entrypoint - so it is not a shortcut.
Reconstruction goes through the two-seat union, not through that field.

## 5. `D:\policy_rows` — 129.16 GB, UNCONSUMED 🔓

The largest single asset we hold and **nothing reads it.** Previously described in the charter and
in memory as "92 GB" — **measured 2026-08-06 at 129.16 GB**; use the measured figure.

Open as **Better-Agent Charter unknown #13**: *what signal is extractable for **evaluator-fitting**
— explicitly NOT behaviour cloning?* That framing is binding, for two independent reasons:

- `DEAD-ENDS.md` **A13** closes pre-wall behaviour cloning on **arithmetic** (teacher μ 711–753
  against a wall of ~805–815). Its own scope guard re-files label/representation work to **Sept-13**
  — closed for this window, *not* refuted as science.
- `PLAN.md` §1: **torch is not available at episode runtime (measured)**, so a learned net at
  runtime is closed for Aug-16 regardless of label quality.

---

## 6. Smaller stores

| Path | Size | Contents |
|---|---|---|
| `D:\ptcg-episodes\derived\` | 0.02 GB | derived extracts |
| `D:\ptcg-episodes\leaderboards\` | 0.01 GB | daily LB snapshot zips |
| `D:\ptcg-episodes\analysis\` | <0.01 GB | analysis outputs |
| `D:\ptcg-episodes\intel.db` | small | opponent intel (SQLite; `intel`/`watermarks`/`intel_ingest`) |
| `D:\ptcg-episodes\certification-bytes-backup\` | — | certification byte backups |
| `D:\ptcg-episodes\ops\` | — | ops scratch |

---

## 7. Standing rules for anyone touching these

1. **Check the zones before you plan a run.** Open one file, print
   `current.players[i]["deck"|"hand"|"prize"]` lengths, and confirm they are populated lists —
   *before* dispatching a seat against a corpus. `PLAN.md` §5b's substrate claim was passed to a
   seat untested and cost ~6.5 hours.
2. **`deckCount` is not `deck`.** A count cannot be branched.
3. **Never commit episode data, decompressed or not.** Git-ignored on purpose; absolute fence.
4. **State the store, the file count, and the join rule in every receipt** that consumes replays.
   "From the replays" is not provenance.
5. **A true determinization can only be *reconstructed* where the record contains hidden state**
   (§2). Everywhere else it must be **sampled** over hidden worlds consistent with the observation
   — which is the `BELIEF_ROBUST` label class, not `TACTICAL_INVARIANT`. Do not silently swap one
   for the other.

---

*Measured and authored by the Auditor, 2026-08-06, at `origin/main` `db969092c0`. Sizes via
`os.walk` byte sums; zone population read directly from the JSON. §3's episode/frame counts are
carried from the 2026-07-27 LX census and are the only figures here not re-measured today.*
