# LEARNINGS INDEX — harness-friendly inventory

**What this is:** one place a new harness can learn *what we already know*, *what we tried*, and *where the receipts live* — without loading the whole corpus.

**What this is not:** a replacement for the deep registers. **Cite the deep file for any ship claim.**

| Depth | File |
|-------|------|
| **This page** | Inventory + map (start here) |
| Negatives | [`DEAD-ENDS.md`](DEAD-ENDS.md) — closed work + **scope guards** |
| Positives | [`PLAYBOOK.md`](PLAYBOOK.md) — proven methods + receipts |
| Measurements | `ptcg-agent/docs/STRATEGY_SCORECARD.md` |
| Rulings | [`DECISIONS.md`](DECISIONS.md) |
| Fences | [`STRATEGY-OF-RECORD.md`](STRATEGY-OF-RECORD.md) §0/§0a |
| Live execution | [`STRATEGY-0731-ASAP.md`](STRATEGY-0731-ASAP.md) · [`STRATEGY-HARDENED.md`](STRATEGY-HARDENED.md) |
| Experiments | `ptcg-agent/docs/experiments/` (E-ledger; `EXPERIMENTS.md` is a freeze pointer only) |

**Update rule:** when a verdict is consumed, update DEAD-ENDS *or* PLAYBOOK the same session. Then add a one-line row here under the right section (or fix a row’s pointer). Do not grow this file into a second scorecard.

---

## 0. Thirty-second orientation

| Fact | Learning |
|------|----------|
| **What ships today** | Community-1084–class **rules pilot** (kernel-copy / Lucario family), not our old H+search stack |
| **What lost on ladder** | H + belief-PIMC search as **product** (mid-pack / below borrowed rules) |
| **Biggest instrument bugs** | (1) band pool = **self-similarity**, not strength; (2) **ship path never carried our knobs** for a long time; (3) **underpowered n** (n=400 MDE ~10pp) |
| **Field recipe** | Good pilot code (rules + matchup conditionals) ± shallow search/leaf — **not** deep PUCT on a weak net |
| **How we promote now** | 3-leg foreign-policy panel (lineage-diverse): ≥60% H2H n≥400 · no CI-separated loss · ≥1 CI-separated win |
| **How we improve the ship** | Reverse-engineer **our** tarred `main.py` → edit on `ship_kernels/copies/` one mechanism at a time |

If you only remember five strings: **rules pilot · foreign panel · ship file · scope guards · 3-leg rule**.

---

## 1. Strategies we tried (family inventory)

Use this table to avoid reinventing a family that already has a verdict. **Status** is coarse; open the deep link before acting.

| Family | What we tried | Coarse status | Deep link |
|--------|---------------|---------------|-----------|
| **Heuristic H** | Handcrafted scorer as policy | Useful as leaf/support; **not** the ladder champion story | Scorecard §1 |
| **Search (belief-PIMC / V13 dormant)** | Ship search product; enable dormant search | **CLOSED as product** (ladder + 24–0 to own fallback). Search as *mechanism class* still has scope guards | DEAD-ENDS **A1/A2** |
| **Borrowed rules / community-1084** | Field rules_lucario / kernel-copy Lucario | **Live floor / ship surface** | SoR · `ship_kernels/` · scorecard identity |
| **Deck lab / meta decks** | Grimmsnarl, walls, Garchomp, crustle, … | Within-family OK to study; **cross-archetype swap as probe CLOSED** | DEAD-ENDS **A7** · PLAYBOOK §B |
| **Representation / nets** | Family-1/2 scalars, value leaf, BC/imitation | **Killed or scarcity-closed for pre-wall ship** (see scope) | DEAD-ENDS **A3–A5, A8, A11, A13** |
| **Cheap single-rule patches on floor bot** | Data-mined lever hunt | **A6 VOID** (instrument) — structural pilot work / Tier-0 bugs **not** the same object | DEAD-ENDS reclass pass |
| **Conversion loop / loss labels** | Mine losses → cheap policy fix | Mostly nulls under proper identity; still useful **factory** lessons | Scorecard §6 · PLAYBOOK #4/#9 |
| **Opponent routing (OP-ROUTER)** | Matchup-conditioned policy (e.g. bench floors 5/3/2) | **Active build lane** (observe first, then one lever) | ASAP Lane 2 · HARDENED B1–B3 |
| **Understand / RE ship agent** | Anatomy of **our** fielded `main.py` + teachers | **Active foundation lane** (Team B / Lane 0–U) | ASAP Lane 0 · `STRATEGY-UNDERSTAND-AGENT.md` if present |
| **Foreign kernel legs (e.g. mechi22)** | H2H vs fielded on real panel | Candidate legs only; **3-leg rule** before pair reopen | ASAP Lane 3 |
| **Probe fleet / ladder pair-mean** | Bounded ladder experiments | Ladder = truth; pair-mean not max | SoR · GATES · MASTER_DASHBOARD |

---

## 2. Closed / do-not-retread (cheat sheet)

**Cite DEAD-ENDS for full scope guards.** Never quote a dead-end without its guard.

| ID | One-line | Do NOT conclude |
|----|----------|-----------------|
| **A1** | Search stack **as shipped** lost to borrowed rules on ladder | “Search can never work” |
| **A2** | V13 search-as-enabled lost **24–0** to its own fallback | “Search class refuted” (weak-eval only) |
| **A3** | Imitation on **148-feature** rep hit AUC wall | Imitation on *any* rep forever |
| **A4/A5** | Family-1/2 scalar add-ons BANK_NULL offline | All representation research impossible (A5 has embedding tension) |
| **A6** | ~~Cheap patches closed~~ → **VOID** | Use VOID as “untested,” not “proven useless” |
| **A7** | Cross-archetype deck-swap probes toxic on ladder | Within-family list work |
| **A8** | Representation re-architecture **killed this competition** | Representation science in general |
| **A10** | Same-deck H2H not yet a qualified strength *selector* | H2H measurements are meaningless |
| **A13** | Pre-wall BC generations **arithmetic-closed** vs bronze wall | Label/Sept-13 work is dead |

**Sound on ladder / ship path (do not “invalidate the whole record”):** A1, A2, A7, A13 arithmetic, A10 evidence-floor.

**Instruments that lied (process learnings):**

| Bug | Learning |
|-----|----------|
| Band pool = our H in different decks | Measures self-similarity, not strength |
| Harness flags / rules knobs not in tarred `main.py` | Lab green ≠ ladder candidate |
| n=400 for +5–8pp claims | Underpowered → UNKNOWN, not REFUTED |
| MERGEABLE/CLEAN + SKIPPED checks | Merge-conflict state ≠ CI ran |
| Dual `ci.yml` documents | YAML can “parse” while GitHub runs **zero jobs** |
| Clean status worktree delete | Clean + on-remote ≠ disposable ops path |

---

## 3. What worked (process & product)

Condensed from PLAYBOOK — receipts live there.

| # | Proven method | Why it matters |
|---|---------------|----------------|
| 1 | **Graded evidence ladder** (screen → battery → confirm) | Kills false positives before ladder spend |
| 2 | **Preregistered kill bars** before data | Kills lanes in hours, not weeks |
| 3 | **Replicate-pair / pair-mean floor** | Only strategy that banked reliable ladder μ for us |
| 4 | **Elite-vs-us behavioral census** | Cheapest defect finder (abilities, attach, draws, …) |
| 5 | **Measurement-before-strategy** | Census/kill before build |
| 6 | **Consumables-in-git + host paths** | Cross-host blockers → routine |
| 7 | **Double-blind + reconcile** | Confidence when independent seats agree |
| 8 | **Sub-game brute force** over full-game spam | Better info/hour |
| 9 | **Code-first labels**; LLM only if it beats validators | Unvalidated LLM labels ≈ zero signal |
| 10 | **Calibration ledger** (predict then read) | Instrument authority from closed rows |

**Lucario family (pin class `c6ca3985`):** brick is often evolution-line failure; play-side priorities lag human playbook; elite dumps rarely contain *our* deck; wall/mill needs explicit counters — see PLAYBOOK §B.

---

## 4. Timeline of strategy eras (context, not schedule)

| Era | Dominant bet | Outcome learning |
|-----|--------------|------------------|
| Early | Build H + eval + decks | Factory / reliability lessons; local eval ≠ ladder |
| Mid | Search supremacy (local E031+) | Local ≠ ladder; ship search underperformed rules |
| Pivot | Borrow community rules / Lucario floor | Floor pair-mean; report protected primary |
| Late Jul | Conversion loop / cheap levers / nets | Cheap levers null under identity; rep killed for competition |
| 07-31+ | **Real-policy panel** + **ship kernel-copy** + RE own agent | Measure truth; author on tar; understand file before edit |

**Only real walls:** entry/merger **2026-08-09** · submit **2026-08-16** · convergence ~Aug-17–31 · strategy track **2026-09-13**. Derived “probe cutoff” dates are **not** submit walls (`DATES.md`).

---

## 5. Live strategy stack (what to execute *now*)

| Layer | Content |
|-------|---------|
| **Field truth** | Pilot code + matchup conditionals; not deep public search |
| **Lane 0 / U** | Reverse-engineer **our** ship `main.py` (call graph, edit_points, fingerprint) |
| **Lane 1** | Selective null re-audit on real panel (not wholesale “all nulls fake”) |
| **Lane 2** | OP-ROUTER: observe opponent → one lever (e.g. bench floor **5 / Lucario, 3 / bench pressure, 2 default**) |
| **Lane 3** | Foreign legs (lineage-diverse); 3-leg rule before pair reopen |
| **Promote** | ≥60% H2H n≥400 · no CI-separated panel loss · ≥1 CI-separated win → Jon packet (EV + borrowed-vs-original) |
| **Ship surface** | `ptcg-agent/ship_kernels/copies/` (v000 pin; v00N one mechanism) |

Detail: `STRATEGY-0731-ASAP.md` · `STRATEGY-HARDENED.md` · onboarding: `HARNESS-RAMP.md`.

---

## 6. Harness use patterns (context budgets)

| Situation | Load this only |
|-----------|----------------|
| Cold start (5 min) | §0 here + [`HARNESS-RAMP.md`](HARNESS-RAMP.md) + [`ACTIVE-COMMS.md`](ACTIVE-COMMS.md) |
| “Has this been tried?” | §1–2 here → then DEAD-ENDS / PLAYBOOK row |
| Ship / promote claim | 3-leg rule §5 + GATES + scorecard + identity assert |
| Writing strategy report | PLAYBOOK + DEAD-ENDS scope guards + scorecard |
| Avoiding retread | DEAD-ENDS scope guard **verbatim** |

**Do not** paste full DEAD-ENDS / DECISIONS / E-ledger into every prompt. Link + one-line cite.

---

## 7. Maintenance (keep this thin)

| When | Action |
|------|--------|
| Verdict banked null / refuted | DEAD-ENDS row (or reclass) + one-line here if family table drifts |
| Method proven | PLAYBOOK entry + optional §3 strengthen |
| Strategy era shift | Update §4–5 only; don’t rewrite history |
| Stale | Prefer deep file over this index if they disagree |

**Owners:** any seat may propose a one-line PR; Master absorbs contested rows.

---

## 8. Related inventories (ops, not science)

| Topic | Where |
|-------|--------|
| Disk / worktree locations | `research/2026-08-01-location-inventory-post-tidy-grok.md` |
| Tools | `HARNESS-TOOLS.md` (if merged) / harness dir |
| Status worktree protect | DEAD-ENDS instrument lessons · bus #1935 incident |
| Experiments list | `ptcg-agent/docs/experiments/INDEX.md` |

---

*Harness-friendly: short tables, progressive depth, mandatory pointers. Full truth remains DEAD-ENDS + PLAYBOOK + SCORECARD + DECISIONS.*
