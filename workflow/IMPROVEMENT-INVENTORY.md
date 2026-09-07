# IMPROVEMENT-STRATEGY INVENTORY — LIVING REGISTER

> ## RECLASSIFICATION PASS - 2026-08-01 (Master). A THIRD CLOSE-CLASS IS MISSING FROM THIS REGISTER.
>
> This file already distinguishes **CLOSED-PHYSICS** (a real barrier) from **CLOSED-SCARCITY** (we
> chose not to spend). That discipline is good and it is why this pass is small. **But the three
> defects verified on 2026-07-31 create a third class that has no name here, and rows are currently
> being filed as PHYSICS when they belong in it.**
>
> ### CLOSED-UNREAD - the new class
>
> **A lane closed because the instrument could not resolve the effect is neither physics nor
> scarcity. It is UNREAD.** Nothing was learned; a measurement was taken that could not have
> answered the question either way.
>
> **This misfiling is the expensive one, because PHYSICS reads as PERMANENT and UNREAD is candidate
> supply.** Re-running an UNREAD row is not re-litigation.
>
> | class | means | may it be re-run? |
> |---|---|---|
> | **CLOSED-PHYSICS** | a real barrier was measured | only on its stated reopening condition |
> | **CLOSED-SCARCITY** | we chose not to spend | yes, when the budget changes |
> | **CLOSED-UNREAD** *(new)* | the instrument could not resolve it | **yes - it is candidate supply** |
>
> ### The three tests that move a row to UNREAD
>
> 1. **Band pool** - the opponent was a real decklist piloted by *our own* generic heuristic, so the
>    row measured self-similarity. Our lineage scores 97-99 pct there.
> 2. **Ship path** - the mechanism was a `rules_lucario` / `config` flag. The submitted bundle reads
>    **no config, no env, no flag**, so the row is silent about the ladder whatever it says.
> 3. **Power** - `GATES.md`'s own pass found **34 of 34 declared sample sizes cannot resolve a 5-8 pp
>    effect**, and **no gate was ever run at n>=1200**. A null at n<=400 is an UNREAD measurement.
>
> **The asymmetry, stated so this is not misused: a POSITIVE is not weakened by low power the way a
> null is.** Underpowering makes an effect harder to detect. **Do not use this pass to discount
> detections** - that inverts the arithmetic.
>
> ### Rows this pass moves, by their own recorded wording
>
> - **The clock/branch-cost row: `CLOSED-SCARCITY (clock +70-80 pct p99) - reopening condition:
>   branch cost fix; re-price under 300x throughput`.** **Its own reopening condition has been met** -
>   the throughput refutation landed (304.5x / 373.2x) - **and nobody re-priced it.** This is the
>   clearest actionable row in the file: it is closed on a reason that has evaporated.
> - **`CLOSED 07-31: port faithful (mirror 52.5 pct n=400; Crustle arm +1.75pp CI-overlap)`** ->
>   **UNREAD on two counts**: a *mirror* opponent (test 1) and a **+1.75 pp claim read at n=400 where
>   the MDE is 9.9 pp** (test 3). The CI-overlap it was closed on was guaranteed by the instrument.
> - **`CLOSED as champion; H remains leaf/comparator - and the band-pool pilot, see #55 caution`** ->
>   **UNREAD (test 1)**; the row already carries the caution, which was never actioned.
> - **`CLOSED-PHYSICS for champion (decision-grade diffuse null)`** -> **UNREAD.** This is the
>   `DEAD-ENDS` **A6** class, which that file's pass already ruled **VOID** (basis `n>=200`, opponent
>   set NOT LOCATED, almost certainly the harness-flag path). **PHYSICS is the wrong label for it.**
> - **`CLOSED as probe - taxonomy caveat: single probe on a retired weak stack; kill is
>   SCARCITY-class, not PHYSICS`** -> already self-corrected in its own text; make the label match.
>
> ### Rows that STAY CLOSED-PHYSICS - do not re-run these
>
> `contrast 2.5e-5 vs a 0.1 pct bar` (four orders off) · `6.0 pct H2H` (a floor - bias inflates, it
> cannot produce 6 pct) · `6/6 dead; survives proper-mixture retrain` (**the arithmetic carries it,
> not the six cells**) · the E016 loader-sim gate (mechanical, must never recur) · `winner/loser
> equidistance 54.4/53.7` (offline, structural) · `0.744 AUC on 148-d` (offline, and already
> apparatus-scoped).
>
> **"The record is invalid" is a misreading and is not a permit.** This pass moves five rows and
> leaves the rest standing.

**Jon-directed standing artifact ("lets keep the inventory updated", 2026-07-31). Maintainer: APPRENTICE (board-keeper duty).**
Seeded from the 62-row inventory (2026-07-31) + PR #2180 rider (pr-agent, 8 corrections) + second rider (apprentice, 9 deltas). All three folded; rows updated in place with UTC datestamps, never silently.

**UPDATE PROTOCOL:** (1) a row changes ONLY when a receipt lands — cite it; (2) every close carries its CLASS: `PHYSICS` (mechanism refuted, reopening condition stated) vs `SCARCITY` (stopped for pre-wall economics — cheap to reopen when economics change) — never cite a SCARCITY close as if it were PHYSICS; (3) corrections are edited in place with a dated note, riders fold in, provenance in git history; (4) new strategies get new rows, never overwrite; (5) apprentice sweeps the register every board-keeper pass; any seat may propose a row-delta on the bus TO: APPRENTICE.
**Status legend:** LIVE (candidate/module in flight, bar stated) · OPEN-PREWALL · OPEN-SEPT13 · WORKING (proven, keep) · CLOSED-PHYSICS · CLOSED-SCARCITY · OPS (not a strength lever).

> **COMPANION REGISTER (added 2026-09-02, Jon-directed).** This file inventories *strategies*.
> The *method defects* — what we assert without measuring, why, and the fix for each — belong in
> the **`ATTEMPTS-LEDGER` §8 GUESS REGISTER**, which is canonical for that object by Jon's standing
> order of 08-21. **One register, not three.**
>
> **The two are coupled:** the underpowered-sample finding there is the reason many rows *here*
> should read `CLOSED-UNREAD` rather than `CLOSED-PHYSICS` — `GATES.md` records that **34 of 34 of
> its declared sample sizes cannot resolve a 5–8pp effect**, and `CLOSED-UNREAD` is, in this file's
> own words, *candidate supply*. Relabelling those rows is not bookkeeping; it restocks the
> generator that `DECISIONS.md` 08-02 rules **weak** (*"guesses buy decisions (17/18 purposive) but
> 0/9 positive candidates"*).
>
> Archetypes are `PATTERNS.md` P8–P11; the lessons are `LESSONS.md` 21–23.
>
> **Maintainer note:** this file names **APPRENTICE** as board-keeper, and APPRENTICE is not on the
> active roster — that duty is currently **orphaned**. Flagged rather than silently reassigned.

## A. Baseline / product identity
| # | Strategy | Status @ 2026-07-31T22:10Z | Receipt / next trigger |
|---|---|---|---|
| GR-INV-1 | **OPEN — the SRI registers carry none of canon's 34 retracted CLAIMS.** `build_sri.py` harvests `RETRACTIONS.md` §Retracted values into `CLAIMS.md` (12 rows, status RETRACTED) but nothing harvests §Retracted claims. Probed 2026-09-06: 'bench snipe', 'super-additive', 'our own agent is unmeasured', 'UNOBTAINABLE offline' and the new 09-06 card-pin row each appear in canon and in **zero** register files. INDEX.md routes 'is this number retracted?' to `registers/CLAIMS.md`, so a reader who follows the index sees 12 of 46 retractions and misses every claim-level one. | **Not a live-firewall hole:** `retraction_scan.py`, `retraction_register.py` and `workflow/writeup/qa_scan.py` all read canon directly and DO carry the claim rows (qa_scan went 26→27 needles when the 09-06 row landed). The gap is the register mirror and the index's routing promise. Unblock: teach `build_sri.harvest_claims` to emit §Retracted claims as their own kind, or amend INDEX.md to route claim-level retractions to canon. Found 2026-09-06 while banking `judged-writeup-prior-art-2026-09-06`. |
| 1 | Random/guarded-random baseline (~263μ) | CLOSED-PHYSICS as product; kept as regression floor | E001/E005/E010 |
| 2 | Handcrafted H heuristic v1→v3 (ladder ~476-549) | CLOSED as champion; H remains leaf/comparator — **and the band-pool pilot, see #55 caution** | E035 |
| 3 | Silent-fallback "agent" (μ→210, 100% fallback) | CLOSED-PHYSICS (must never recur); loader-sim gate permanent | E022/E028 |
| 4 | Borrowed 1084 rules bot = champion (pair-mean ~750-753) | STILL THE PRODUCT. ~~"fresher 1084.5 fork open to mine"~~ **REFUTED at bytes 07-31** — fresh page byte-identical to our champion (0 added/3 removed, all ours) | main 234791a68 |

## B. Search / planning
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 5 | Belief-PIMC / determinized search on H leaf | CLOSED as ship; assets feed leaf redesign | E031/E062 |
| 6 | "Search superiority" confirmation campaign | CLOSED (question answered; no re-confirmation) | E031-E062 |
| 7 | Enable dormant V13/public search (24-0 vs own fallback) | OPEN under SK-294 — needs non-weak evaluator FIRST | seq-89/90 |
| 8 | Shallow search + rules (seq-155, 30.2% w/ 0.345 leaf) | OPEN-PREWALL **iff** offline leaf dominance first; mechi22/prvsiyan = public existence proofs above 1000; 600s think-bank confirms deployability | seq-155; census |
| 9 | This-turn lethal oracle runtime retrofit | CLOSED-PHYSICS on mirror corpus (97.8% of proven missed wins in won games); asymmetric/loss corpora still open | sign-check receipts |
| 10 | Oracle-PIMC full-info substrate | OPEN-SEPT13 (labeler → value-guiding, Suphx-style, not naive distill) | labeler merged #2161 |
| 11 | ALL_LEGAL candidate expansion | CLOSED-SCARCITY (clock +70-80% p99) — reopening condition: branch cost fix; **re-price under 300x throughput** | E-ledger |

## C. Deck / meta
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 12 | Deck-lab re-rank under policy | WORKING doctrine (deck-only ranking = cargo cult) | E003/E018/E041 |
| 13 | Dragapult-vs-Garchomp ruling | Historical (Lucario era) | E068 |
| 14 | Wall / Crustle-Drednaw decks | LOW unless generic-pilot specialized | E027/E034/E039 |
| 15 | Garchomp prize-race list A/B | CLOSED for that loss mode (policy not list) | E051/E055 |
| 16 | Cross-archetype deck swap (~422μ probe) | CLOSED as probe — **taxonomy caveat: single probe on a retired weak stack; kill is SCARCITY-class, not PHYSICS** | SoR §0a; taxonomy 07-31 |
| 17 | Alakazam meta pivot | Intel-only unless Jon new-family ruling — **note: mechi22 (Alakazam shell) beating both our kernels is new evidence for the shell's strength** | R-PIVOT-01; mechi22 receipts |
| 18 | Within-family Lucario list variants / hand-MC | OPEN-PREWALL (OP-DECK, behind fail-closed ID-map gate; ParkerT first; staple A/B one tech at a time) | #2143; OP-DECK |
| 19 | Public deck-meta intel (myso1987/Limitless/FarmScore) | OPS ongoing (priors + coverage only — population-transfer guardrail) | Limitless harvest |

## D. Rules / heuristic patches on champion
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 20 | POLICY_WALL playbook | CLOSED as ship | E044/E064 |
| 21 | RACE_MODE | **SUPERSEDED 07-31 by #32's prize-liability module** (same territory, now with measured mechanism + bar) | 5080 22:00Z |
| 22 | K-H-01 / decisive-gate / CAFL levers | Flags OFF — **band-pool caution applies (#55): nulls measured on home-field instrument** | 07-31 bias finding |
| 23 | Cheap single-rule conversion mine | CLOSED-PHYSICS for champion (decision-grade diffuse null) | R1/R1b |
| 24 | Rule-extraction from elite divergence | CLOSED (gap not encodable as one rule) | #1438-#1450 |
| 25 | Setup-greed / Option-B piloting generation | CLOSED this gate (replay unfaithful); needs full-game tools | #1535 |
| 26 | Decode-fidelity port (rules_lucario) | SHIPPED base. **OP-FIDELITY CLOSED 07-31: port faithful (mirror 52.5% n=400; Crustle arm +1.75pp CI-overlap) — restoration + Xerosic A/B moot** | 5080 21:18Z receipts |
| 27 | BOSS patch | Null n=450 — **suspect ×2: underpowered opponents (rider) + home-field bias; retest = REAL-POLICY panel, not more n on the same pool** | retest queue |
| 28 | Grimmsnarl playbook | Null n=400 — same double caution as #27 | retest queue |
| 29 | Alakazam/Solrock playbooks | HELD — revive trigger: real-policy-panel evidence (#27/#28 retests inform) | — |
| 30 | ALP M1/M2/M3 attacker-line modules | OPEN-PREWALL, HIGH — OP-MODULES M2-first live (5080 flags + Roach batteries; worst-matchup targeting) | 21:12Z offense |
| 31 | Rules bugs 1-8 (fetch priority, free draw, retreat, prize-map…) | **HIGHEST residual, OPEN-PREWALL** — throughput stop-reason REFUTED (304.5x/373.2x); implementation queued under OP-MODULES. **AUTHORING-SURFACE NOTE (22:07Z, applies to #30/#31/#32): flags in rules_lucario cannot reach the FIELDED bundle (borrowed kernel = single hardcoded .py, reads no flags). A ladder-bearing module must be authored INTO a copy of the fielded kernel file itself (Apache-2.0, already ours to ship; prvsiyan's one-gated-mechanism-per-version method is exactly this) OR ride a our-lineage candidate that first reaches V13 level. Master ruling requested; until then module authoring targets the kernel copy, not the port** | #2172; rider; 5080 22:07Z |
| 32 | mechi22 mechanics ports | **NULL 22:07Z**: prize-liability flags built + batteried (7.0%→8.0% vs mechi22, CIs overlap) — the measured asymmetry (2.43 vs 1.47 prizes/KO) is DOWNSTREAM of what decides the games. Flags stay in-tree default-OFF w/ tests (live instrument, cheap re-test). **Structural finding: rules_lucario flags cannot patch the FIELDED submission (borrowed kernel = one hardcoded file, no config) — see authoring-surface note under #30/#31** | 5080 22:07Z receipts |

## E. Learning / representation / RL
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 33 | BC on 1M/elite dumps | CLOSED-PHYSICS for dumps (winner/loser equidistance 54.4/53.7) | signal agent |
| 34 | Full-policy imitation on 148-d | CLOSED on 148-d (0.744 AUC wall) — **apparatus-scoped: field census shows rank-34 GM on PURE imitation (~21k games); category is viable with a seeing representation** | #1444; census |
| 35 | Gen-1 learned cells | CLOSED recipe (2/80 real games despite +19-27pp agreement) | GEN1 receipts |
| 36 | Gen-2 (mirror mix) | CLOSED (6/6 dead; survives proper-mixture retrain) | GEN2-GRID-001 |
| 37 | Teacher-swap BC on current feats | CLOSED on current feats (6.0% H2H) | #2144 |
| 38 | ε-deviation / advantage minting | CLOSED-PHYSICS (contrast 2.5e-5 vs 0.1% bar) | #2144 |
| 39 | DAgger relabel tooling | **MEASURED NULL — re-stamped 2026-08-23 (was a stale undated `OPEN-SEPT13`): 2026-08-18 5-cycle DAgger line = 14/800, overlaps teacher; prereg FORBIDS cycle-6 on the same teacher (ATTEMPTS-LEDGER §1 fact 4, §7 Forbidden). Tooling survives as an asset; reopen only with a different/stronger teacher or a named exceed-teacher mechanism** | dagger_relabel.py; ATTEMPTS-LEDGER §3/§7 |
| 40 | Value-net leaf | Reopen ONLY with better labels/repr — **field-replicated 07-31: three ranked teams report value nets failing; bottleneck is the competition's data, not us** | census |
| 41-43 | Feature families on 148 (lethal/race, card-identity, history) | CLOSED those families (nulls on the blind base) | #1505/#1519/K-REP |
| 44 | Identity embedding / tied-row unlock (+25.6/+32.5pp offline) | **OPEN, RANKED UP 07-31; now TWO boxes** — the repaired apparatus; Roach 10k-mint foundation retrain in flight + 5080 moved here 22:07Z (10.1M-row identity column ~40 min, then full-ladder identity-vs-baseline arms, multi-seed, 3-leg bar). The only lane with a positive measured trajectory (DAgger gen-1 +3.4pp CI-separated) AND the only one producing a POLICY rather than a patch to bytes we don't field | REPR-PROBE-01; convergence plan; 5080 22:07Z |
| 45 | Capacity scaling on current featurizer | CLOSED until new features (+0.23pp max vs +1.5 bar) | 5080 receipts |
| 46 | RL / policy-gradient pilot | OPEN-SEPT13; deployment envelope now known (CPU 1.6 vCPU / 8 GB / 600s per game — small net fits, heavy search crushed) | census; R-C build |
| 47 | Top-K outcome re-ranker | Residual if labels exist (exceed-teacher path) | design 07-31 |
| 48 | Oracle-as-value-labeler / guiding | HIGH residual — the correct reopen path for #40; oracle-value on identity features = the open question | labeler #2161 |

## F. Teachers / kernels
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 49 | Same-deck public teacher (20-0) | Historical — proved policy is the lever | lane-2 |
| 50+51 | V13 teacher + 940 opponent | **MERGED ROW 07-31: ONE LINEAGE (Master ruling — identical card-ID constants/scoring). H2H 55.33% n=1500 stands; batteries must not count them as independent arms; panel = lineage-diverse by ratified rule** | main d001ba242 |
| 52 | Fresher public bots | **SPLIT 07-31:** 1084.5 = REFUTED at bytes (see #4). mechi22 = **CANDIDACY CLOSED 22:18Z on the repaired instrument**: 29.5% [25.2,34.1] vs lineage-distinct 844-router while fielded V13 scores 43.3% [38.5,48.2] same arm — CI-separated loss ⇒ fails trigger leg (b). Verdict: mechi22 is a COUNTER to the 1084-5 lineage, weaker on the deck-race axis; NOT a submission candidate. SURVIVES as: opponent/teacher asset (its exploit of us = lineage-wide hole, mined), license verified, and the full episode = Sept-13 case study (false fire → false refute → instrument repair → clean kill, ~40 min, zero spend) | Ash #2186; main 2f9a84f92 |

## G. Measurement / portfolio
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 53 | Pair-mean / latest-2 management | REDUCED to the **ratified 3-leg trigger** (>=60% H2H vs submitted bundle; no CI-separated loss + >=1 CI-separated win on lineage-diverse real-policy panel; all before EV; Jon-keyed) | Jon approval 21:48Z; ratification 21:58Z |
| 54 | n>=400 confirmation-first | WORKING — keep (caught BOSS/Grimm mirages; externally replicated by crustle author's own screen→confirm collapse) | board |
| 55 | Mirror/band-pool patch testing | **INSTRUMENT DEFECT CONFIRMED 07-31 (home-field bias: our-H pilot, 97-99% lineage ceiling vs 82-92% for independent agent that beats us). Fix = real-policy lineage-diverse panel; THEN retest queue (#27/#28/#22)** | 5080 21:51Z |
| 56 | 20-game screens as gates | CLOSED as gates (optimistic 5/5; external replication banked) | calibration story |
| 57 | Clone/reliability resubmit | OPS; **re-anchoring MC pending** (submitters decline ~25μ/10.8d less than holders; collides with eviction mechanics — Master sizes) | cadence analysis |
| 58 | Strategy report as primary EV | SHIP (Sept-13 = the prize; outline merged #2173) | outline on main |

## H. Meta-process
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 59 | Growth loop (witness→dual-agree→flag→ladder A/B) | Right process; needs WORKING modules to feed it | — |
| 60 | Learning factory (corpus→train→judge) | Factory OK; objective wrong pre-wall (freeze routes to Sept-13 unless exceed-teacher) | freeze |
| 61 | FIX-IT explorer + evidence board | ACTIVE | #2145 |
| 62 | Bronze endgame = portfolio framing | ACTIVE via #53's trigger only | reckoning + corrections |

## NEW ROWS (post-inventory, 07-31)
| # | Strategy | Status | Receipt / next trigger |
|---|---|---|---|
| 63 | OP-LOSSES coach loop (own real-ladder losses, current band, weekly) | LIVE — harvester restart + classifier + pinned per-mechanism table; Misty #2168 = narration seed | loop audit; OP-LOSSES routing |
| 64 | Real-policy lineage-diverse panel build | **DELIVERED + VALIDATED 22:18Z** — panel = {V13, 940, 844-router}: 3 members, 2 lineages, 2 mechanisms (844 = mill/deck-race axis, fingerprinted distinct 1.3% overlap; per-artifact lineage AND license principle banked). The panel refuted a candidate the thin panel had admitted — instrument proven discriminating in live use. NEXT: #27/#28/#22 null retests run against THIS panel; per-kernel license page-read pending for any gate-bearing use of 844 | main 2f9a84f92; Ash #2186 |
| 65 | Re-anchoring cadence (maintenance submissions) | PENDING Master's feasible-set MC under verified band decay (−5.9/day in [800,900)) | field-motion VERIFY |
| 66 | Forum-intel standing watch (Kaggle internal JSON API, no login) | PROPOSED to Master — obsoletes "forum is dark"; new-thread poll into read-side tasks | census |
| 67 | crustle_skip_ex_wall build | OPEN-PREWALL — Roach builds; pre-registered to author's own confirm row (~0 overall, +30pp Crustle-only); ship value ≈ share 10.09% × 30pp ≈ +3pp field. **22:26Z: DEMOTED below #68 (one matchup vs the class); gains a mandatory Stage-3 exclusion set (REGRESSION_IDS pattern) before measurement** | Brock share-pull 21:57Z; Master 22:26Z |
| 68 | **OP-ROUTER — opponent routing (observable-ID inference → policy switch)** | **OPEN-PREWALL, RANKED ABOVE #67 — Master 22:26Z.** The 844 line identifies its opponent from visible cards (field + attached energy + tools + discard) and switches policy (bench floor by matchup, wall-mode by stadium, deck-safety guard vs mill, aggressive lines gated by named REGRESSION_IDS exclusion sets). Ours to reimplement (doctrine-read, zero lines copied, license not needed). **Why never found: the band pool has ONE pilot — an opponent-router shows ~no benefit against it; our instrument could not pay for opponent modelling** (home-field mechanism pointed at policy, extends #55). **CONVERGENCE NOTE: our own V13 divergence mine independently concluded "the edge is CONDITIONAL LOGIC, not weights" (attacker-line doctrine, transplant rejected at two layers) — two independent derivations of the same architecture class = strong prior.** Staged: (1) Roach `observed_opponent_ids()` observation-only, lands alone; (2) predicates + ONE routed decision (bench floor); (3) exclusion sets retrofit to every module. BAR pre-registered: real-policy panel ONLY; predict ~zero on band pool (movement there = suspect harness) + positive MATCHUP-VARYING panel delta; uniform-help = bug report. Brock verifies Roach, Ash verifies 5080 | Master 22:26Z |

**Cross-references:** loop-class analysis `workflow/research/2026-07-31-improvement-loop-taxonomy.md` (PR #2178) — same space, different grain. DEAD-ENDS.md §D should pointer here with the close-class distinction stated at the pointer.

---

## VALUE-086 two-host witness banking (added 2026-08-24)

| Field | Value |
|---|---|
| **Status** | **MECHANICS COMPLETE — exact assets on-repo; transfer fidelity MEASURED; export correctness MEASURED AND PASSING 2026-08-31; zero games** |
| **Exact identities** | `origin/main` landing `35cdc058341fe817bf1a732361352ae892c37b44`; checkpoint `VALUE-086.pt` SHA-256 `2c744ed5f02c5e6633d68d7274fe4a6b39dc0ebceee7d315185e86dfbfc9d366`, 419,949 B, blob `07bad88d09f9dfd85bf0ea905ee4fe85790060b9`; runtime export `VALUE-086.npz` SHA-256 `a1a64a66630f1c6127187aacf8f770febbeb12268ecd88a68d3eb67e34d1d330`, 419,008 B, blob `7d9dbb9631db959f8a8e3eac3f3bf13e30d301ac` |
| **Evidence** | `workflow/artifacts/value-leaf-conversion-v1/TWO-HOST-WITNESS-PACKAGE-v1.json` binds ROACH comment 5397991970 and SKYNET/STRATEGIST comment 5398202370 by exact body SHA-256, host, asset digest, size, and unchanged Git blob OIDs from `e692b281…` through landing head `1a3b7ad3…` to main. The tracked 1,027-probe parity receipt remains SHA-256 `94f35c9a0c765d753fe4143b1dba886608615ce586882b3414bb80272eafeff2`. |
| **Result class** | **MECHANICS / TRANSFER FIDELITY.** Two hosts independently agree on the transferred bytes. This is not export correctness, action difference, causal advantage, agent strength, or improvement. Git content addressing already protects blob identity; the witness package banks cross-host observation and provenance. |
| **Falsification / limits** | Transfer fidelity reopens if either live witness body digest drifts, either asset digest/blob changes, or the hosts disagree. Two hosts can agree perfectly on a faithfully replicated but wrongly exported file. The witness package does not re-execute the source-bound parity probe and supports no gameplay/outcome claim. |
| **Answer-map delta** | `n-value086-artifact`: `MEASURED-OFFREPO` → `MEASURED`. `n-value-lane-export-bank`: remains `OPEN` on the corrected terminal; two-device SHA evidence is satisfied and no third rehash is owed. |
| **Export correctness (2026-08-31)** | **MEASURED — PASS.** All six state_dict tensors of `VALUE-086.pt` are reproduced **bitwise** by `VALUE-086.npz`: `max|diff| = 0.000e+00` on `w0 b0 w2 b2 w4 b4`, with export metadata `state_dim 148` / `hidden 256` matching the checkpoint's own, and the checkpoint's recorded `params 104193` equal to its summed tensor sizes. **Negative control ran and refused:** the adjacent, identically-shaped, previously-mislabelled `B339.npz` (`value_net_rlvr`, a different model per :269) reproduces **0/6** tensor digests, differing by up to 3.093. Executable closure is tracked at `ptcg-agent/harness/value086_export_check.py` + its suite, and runs **without torch** so it can never skip. Receipt: `workflow/research/2026-08-31-value086-export-correctness/RECEIPT.json`. Authority: AUDITOR ruling bus #3011 `5483062178` §3. |
| **Next decision** | Export correctness is closed; the preregistered replay re-step is unblocked on that axis alone. **Still owed before any powered WDL spend: nonzero semantic action difference** (ledger MET-2). VALUE-086 does **not** enter the Gate-1 package — Gate-1 binds B339 and only B339 per `5483062178`; VALUE-086 is a distinct follow-on leaf candidate needing its own identity-bound admission. |

---

## DEBT ROW — exact-runner terminal variance defect (logged 2026-08-04, apprentice)

**Class: DEFERRED-KNOWN.** Not physics, not scarcity, not unread — the effect *was* resolved. We
know what is wrong and chose not to fix the cause under time pressure. Recording it because
"formally deferred" is only true if it is written down somewhere a future pass will read.

| Field | Value |
|---|---|
| **What** | `fixed_n_terminal.py` was not demonstrably α-controlled under two required null conditions |
| **Evidence** | `receipts/2026-08-04-EXACT-RUNNER-ALPHA-LEAK-EVIDENCE.md` + `attempt-2556.json` (10,000 trials, n_plan 2556) |
| **Measured** | `product_fault` 29/10000 (0.00290), `restart` 32/10000 (0.00320) vs α=0.0025. `clean` 0.00200 and `drift` 0.00240 sat just under. `outcome_conditioned_fault` passed at 0.00070 |
| **Localisation** | The leak is **specific to the fault-injection and restart paths**. Clean and drift are near-nominal. That asymmetry is the diagnostic signal and argues for a real variance-accounting defect rather than a generic normal-approximation error |
| **What shipped instead** | PR #2575: `internal_alpha = 0.0015` when `claim.alpha == 0.0025`, tightening z from 2.807 → 2.968 |
| **Why that is acceptable** | A more conservative critical value **cannot inflate** Type-I. It is valid; it costs power, not correctness |
| **Why it is still debt** | (a) it **compensates**, it does not repair — the variance model is untouched; (b) it is **α-specific** — the `isclose(0.0025)` guard means the leak returns at any other α; (c) an undiagnosed variance error can distort power estimates and interval widths elsewhere, not only Type-I |
| **Known cost, accepted** | Projected power at n=2556 drops `heterogeneity_plus6pp` from 0.9233 → ~0.897, below the 0.90 bar, forcing the grid to n=3834. Master ruled this acceptable: Type-I validity is strictly protected and compute is cheaper than calendar |
| **Ruling** | **MASTER 2026-08-04** — offset stands as the fix for this run; deep-internals diagnosis deferred; will not block the scoring phase |
| **Reopening condition** | Any Confirm at an α other than 0.0025 · any change to the fault or restart injection paths · any use of the terminal's interval width as evidence · Sept-13 report preparation |
| **Report disposition** | **Include.** "We shipped a calibration offset, accepted a measured power penalty, and logged the underlying defect" is a stronger and more checkable claim than asserting a clean repair. The near-miss is also report material: at 50 trials the same conditions reported a Type-I upper bound of 0.0582 — the Clopper–Pearson limit on 0/50, not a defect — and we almost condemned a correct instrument before the arithmetic caught it |

**Standing note:** these diagnostics exist only because the diagnostics-on-FAIL patch (#2550) landed
hours earlier. Without it the run would have refused after ~9 hours emitting zero bytes of
explanation, and this row would say "unknown."

## Row 79 — P-C first-D=1 causal discovery line (added 2026-08-23)

| Field | Value |
|---|---|
| **Status** | **OPEN — instrument/design line; zero causal games; outcomes never opened** |
| **What ran** | seq-159 mechanics pilot EXECUTED 2026-08-23: 48/48, PRICE_ONLY, spend VERIFIED; S=8/48 supported reach (all mirror), q_D=8/48 pre-assignment proposal differences; 33.86 s/start on the live P-C path (4.27× the sentinel path — path must be named in every pricing receipt); outcomes sealed |
| **Design state** | N512 Bernoulli(0.5) first-D=1 randomization + exact stratified W/D/L Fisher (twice-verified math); seven pre-use retractions banked (fixed-64:64 predictability, paired-correlation transport, unsalted Merkle, aggregate D0 cap, +3); H4→H2 topology refreeze + finalize()-race fix + assignment-service qualification PENDING; ΔITT=q_D·δ_D admission law frozen (bus 5387528153 + q_D correction 5387537633) |
| **Receipts** | `PK-runs\pc-model-alt-run-9cd654-20260823\TERMINAL.json` + GAME-SPEND ledger; PRs #2903/#2904/#2905 (OPEN); `research/2026-08-23-pc-n512-adoption-and-execution-handoff.md` (branch); ROACH gap audit on un-PR'd `card/roach-pc-gap-audit-20260823` (GR-16) |
| **Reopening/kill** | Governed by the corrected terminal tree + the admission equation; candidate family retires on the prereg'd harm tail or on q_U·δ_U < 0.02 with defensible bounds |

## Row 80 — the confirmation price is irreducible by covariate adjustment (added 2026-08-26, AUDITOR)

| Field | Value |
|---|---|
| **Status** | **MEASURED — closed as a method question. Zero new games, zero agent-strength claim.** |
| **Finding** | Lin/CUPED cannot cut P2. Incremental pre-treatment R² *within a design cell* is **structurally 0**: every pre-treatment field (`opponent`, `seat`, `swapped`, `schema`) is CONSTANT within cell, because those variables **are** the strata and the engine exposes no seed. Separately, the endpoint is **not over-dispersed** — n-weighted obs/exp 1.011 at m=10 and 0.941 at m=20 across 27 labelled cells / 5,400 games — so the ~36,214 inflated price is unsupported and **N stays 23,764**. |
| **Consequence** | P2 alone FITS both walls (2,098/day against the 2,500 cap by 09-06; 1,297/day by 09-13). **P2+P3 misses the 09-13 report wall by 3.7%** — it needs 2,593/day against a 2,500 seat-authored rail. That rail is now the single arithmetic difference between a reproduced claim and an unreproduced one. |
| **Discarded instruments** | Three, each publishable and each wrong: (1) marginal variance vs `p(1−p)` — an algebraic identity, returned `1.000000` on all 32 files, a control that cannot fail; (2) whole-file block dispersion + lag-1 — 4.41×, confounded because rows are ordered by opponent; (3) within-cell across all files — 1.81×, confounded because 7 files do not record `opponent` and collapse conditions into one pseudo-cell. Also discarded: pooled R² of 0.149, which is between-opponent variance the design already removes. |
| **Receipts** | `workflow/research/2026-08-26-variance-reduction-ceiling-measured.md`. Population = all **44** committed `*games.jsonl` at `origin/main 7d604919e2`, enumerated by `git ls-files`; 35 usable, **18,760 scorable games**. |
| **Open lever** | AIVAT chance-event control variates (arXiv:1612.06915) is the only technically valid N-reduction remaining — it conditions on *known* chance distributions rather than realised outcomes. Needs engine instrumentation at chance nodes plus out-of-sample validation before it prices anything. Cap ruling and MDE choice are Jon/STRATEGIST calls, not method. |

## Row 81 — an artifact that records outcomes cannot answer a question about state (added 2026-09-03, MASTER)

| Field | Value |
|---|---|
| **Status** | **MEASURED — process defect, named and closed. Zero games.** |
| **Finding** | Three seats hit the same blocker in one night, each **after** the analysis was already designed: `--replays` carries full both-seat hidden state but **no `search_begin_input`**, so a position cannot be resumed from it; `p1d_roots.jsonl` carries label and menu shape but **no board state**; `games.jsonl` is 39 keys of outcome/identity/bookkeeping with **no board state at any turn** — so it cannot answer a bench question at *any n*, the field being absent rather than sparse. One failure class, not three incidents. |
| **Why it recurs** | The question-to-artifact mapping is **not written down anywhere**, so it is rediscovered by collision. Contributing cause: `--replays` had **no help text at all** while `--traces` had six lines explaining how it differs from `--replays` — the artifact easiest to reach for documented itself least. |
| **The check** | `print(sorted(json.loads(open(path).readline()).keys()))` — one line, catches all three in seconds. `games.jsonl` already carries `decision_trace_path`, `null` unless `--traces` ran. |
| **Worse than a blocker** | In the P4-B case the check caught a **near-fabrication**: the roots *could* have been joined to a local replay corpus by game index, supplying every requested feature, and it would have been wrong — the roots index a different run. Measured before use: **2.5% join validity, i.e. chance.** Skipping the check there produces a confident fabricated result, not an error. |
| **Receipts** | `workflow/research/2026-09-03-artifact-question-mismatch.md` (PR **#3217**, MERGED 2026-09-03T02:45:13Z). `--replays` help text added and verified against the code, not asserted: the "written only for games that finish without error" clause is `ptcg-agent/harness/eval.py:1157`, `if replay_path and error is None`. |
| **Not claimed** | Nothing about carelessness — all three seats caught their own instance, two within minutes, and each artifact holds exactly what it was designed to hold. |

## Row 82 — the generated-inventory cascade: measured cost, builder exonerated, mechanism still open (added 2026-09-03, MASTER)

| Field | Value |
|---|---|
| **Status** | **PARTIALLY MEASURED — cost quantified and mitigated; root cause NOT established. Zero games.** |
| **Cost (measured)** | Committed generated inventories re-stale every open PR on every merge. **6 of 10 merges since 18:00Z (60%) touch them.** `ARTIFACT-CATALOG.jsonl` showed **+3068/−3068 lines on a commit changing 12 lines of real content**. In practice the conflicting files are `workflow/HARNESS-INDEX.json` and `workflow/HARNESS-INDEX-FULL.json` — confirmed as the *only* conflicts on #3080 via `git merge-tree --write-tree`. |
| **Ruled OUT** | **Builder non-determinism.** Two consecutive builds of `scripts/build_artifact_catalog.py` on a fixed HEAD are **byte-identical** (sha `421293710730`, 2,430,525 bytes, CR=0) and leave `git status` clean. An earlier report of non-determinism in this session was **an artifact of the test harness** (a `cp` step translating line endings), not of the tool — retracted. `BULK_COMMIT_FILE_LIMIT = 200` was also tested and does not explain it: the probed file's sole commit touches 69 files, under the limit. |
| **Still open** | Why `first_commit` / `last_commit` / `size` differ *across* branches. These fields are derived from a `git log` walk at the current HEAD, so they are branch-dependent by construction — committing a git-history-derived artifact into git makes it conflict by design. **This is a hypothesis, not a measured mechanism; it has not been tested and must not be cited as the cause.** |
| **Mitigation in place** | `scripts/unconflict.py` (PR **#3191**) resolves generated-file conflicts with main's copy, regenerates, and pushes. Its load-bearing behaviour is the **refusal**: it declines diverged branches and worktrees with uncommitted changes rather than guessing. Measured 2026-09-03: open-PR conflicts **9 → 3**, and all three survivors belong to other seats. |
| **Trap encountered** | `unconflict` refused #3080 for local divergence (+9/−37) — the stale-ref trap. Gate used before realigning: `git cherry` patch-identity, which showed 8 of 9 local commits already upstream and **one that was not**. Inspecting it first was load-bearing: it turned out to be a pure inventory regen (disposable), but a blind `reset --hard` would have destroyed real work had it been anything else. |
| **Receipts** | `scripts/unconflict.py`, `scripts/build_artifact_catalog.py:73,151,231`. Verification method: every clear re-checked against `gh api .../pulls/N --jq .mergeable` rather than trusting the tool's own report — `gh pr list --json mergeable` serves cached values and overstated the conflict count. |
| **Severity change (2026-09-06, SKYNET)** | The generated-content freshness gate landed in **#3502** and turned this row from an annoyance into a **hard CI stop**. Before, a stale generated file cost a rebase; now it fails the build. Two consequences measured today: a drift inherited from main fails **every** open PR regardless of what that PR touches (**#3506**, a scanner repair with no inventory content, went red on one inherited file), and any PR that adds or removes a tracked file must itself carry a regeneration, which the next merge then invalidates. |
| **The mitigation no longer covers the case (2026-09-06, SKYNET)** | `scripts/unconflict.py`'s `GENERATED` tuple lists only the four legacy files (`HARNESS-INDEX.json`, `HARNESS-INDEX-FULL.json`, `ARTIFACT-CATALOG.jsonl`, `ARTIFACT-CATALOG.md`) and its regeneration step runs only `scripts/regen_indexes.py`. The SRI layer added since — the 14 files under `workflow/inventories/sri/`, rebuilt by `scripts/build_sri.py` — is outside both. A conflict confined to the SRI layer therefore hits the `unexpected` branch and the tool **refuses**, which is correct conservative behaviour and also means the automated fix is unavailable for the layer now causing the conflicts. Observed on **#3503** on 2026-09-06: the conflict was SRI-only and was resolved by hand twice in ten minutes. |
| **Correction to the record (2026-09-06, SKYNET)** | I posted this to the bus at 15:05Z as a newly-observed structural problem and proposed two fixes to ASTRA, without first running `python scripts/prior_art.py`. This row, dated 2026-09-03, already had the cost measured (**60% of merges**, and **69 of 126 open PRs conflicting on 09-02**) and a tool shipped. What is genuinely new is only the severity change and the coverage gap above; the mechanism was known. Logged because the prior-art step exists precisely to stop a seat re-deriving a banked row. |

## Row 83 — S0 exact-action native fanout (added 2026-09-04, STRATEGIST)

| Field | Value |
|---|---|
| **Status** | **S0_MECHANICS_PASS — full eight-root, four-cell native certificate. Zero games.** |
| **What passed** | At exact code head `f92ef24db6df00856a72c5bee3718d7885623b7e`, two roots in each `raw`/`replays-omniscient` × seat-0/seat-1 cell resumed through native `cg`. All 23 exact legal actions were stepped from their retained roots: 8 begins, 23 steps, 31 handles opened/released, 8 ends, zero cleanup faults. The panel includes four ordered roots, four unordered roots, and one legal STOP root. |
| **What failed before the pass** | Three defects were caught without games: the old split controller compares sanitized and private c61 dictionaries despite intentional private-only byte fields; later setup roots require the true face-down opponent Active in search argument 6; and semantic-only action hashes collide when distinct indices encode identical options. S0 now supplies hidden Active only when required and records a unique index-bound action digest alongside the semantic digest. It also avoids `search_end` when `search_begin` never succeeded. |
| **Receipt** | `workflow/research/2026-09-04-s0-exact-action/full-s0-certificate.json`, self-digest `240ab34be18e1ebf8e97102747abddfa931c0f728f842b698b17ee8321242ab9`; certificate module SHA-256 `675d7614d4b84a7a9fc2ea4986fbe0c004c14dd4d25b3c17cd3a014ee8c12655`; native binary SHA-256 `a3a401d0f5ccc3474b9c8a7a2431920c4b728d28105a510aa6927ad6283e5cf7`. The earlier two-root canary remains provenance, not the terminal. |
| **Authority / limit** | Mechanics authority only: `mechanics_authority=true`; direction, strength, label, training, and promotion authority remain false. S0 proves exact resumption/fanout/cleanup, not that search values or chosen actions are better than Parent1. |
| **Next trigger** | Build the live Parent1-fallback controller: capture Parent1 first, use fresh selection/evaluation cells, enforce the match bank, and run at most 20 traced games only after RED/GREEN lifecycle, timeout, legality, and fallback tests pass. |
