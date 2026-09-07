> **Export note — added when this register was published; not part of the original record.**
>
> **No third-party kernel source is in this repository.** This register is
> attribution metadata only: authors, source URLs, licences, pull dates and file
> hashes, so a reader can obtain each kernel from its original author and confirm
> the bytes. Publishing this register does not redistribute any kernel.
>
> The dispositions recorded below were written about the **private working
> repository** `thisisntjon/poketcg`, and some of them reason explicitly from that
> repository being private. Read them as history of decisions taken there. They are
> not a clearance for this public export, and nothing here asserts one.
>
> **Coverage is incomplete.** Five authors whose agents appear in the published
> seven-opponent panel — `plamen06`, `llccqq624`, `raunakdey07`, `zoli800`,
> `harukiharada` — have **no row in this register**. Their kernel source is not
> redistributed here and no claim is made about their licence terms. See
> [`NOTICE`](../NOTICE) and [`docs/RELEASE-REVIEW.md`](../docs/RELEASE-REVIEW.md).

---

# PUBLIC-KERNELS-PROVENANCE — license + provenance register for tracked third-party kernels

**Authority:** `JON-DIRECT RULING 2026-07-24T17:14Z` (narrow permit) — see `AGENTS.md` §3 and
`workflow/DECISIONS.md` (07-24 rows). **Master-implemented 2026-07-24.**

Every file tracked under `ptcg-agent/experiments/public_kernels/` MUST appear here before it is
consumed by a gate-bearing run. The directory remains git-ignored; permitted assets are added
deliberately with `git add -f`. The engine / card-data / secrets ban is **absolute** and is not
softened by this register.

**Form note (deviation, stated openly):** Jon's ruling said "each kernel directory must carry
recorded license + provenance." Those directories are git-ignored, so a per-directory file needs a
forced add on every touch and is easy to miss in review. This central register is always tracked
and diffs in one place, which is stronger for audit. A `GO6-spec-001-provenance.md`-style file
beside a consuming spec remains an equally valid form.

## Required fields

`source slug` · `source URL` · `author` · `public?` · `license` · `pull date` · `per-file sha256`
· `consumed by`

---

## BACKFILL — four files resident on `main` before the ruling

**Disposition:** provenance backfill, **no history rewrite** (Master bounded-severity call, ratified
in the ruling: repo `thisisntjon/poketcg` is **PRIVATE**, so there is no public redistribution, and
these are the ratified cells the decisive lane depends on). Added to `main` 2026-07-24T02:18:03Z in
commit `ca8a51e53` (GO-2b joint ratification battery).

### 1. `prvsiyan_alakazam_v8` — "PTCG AI Battle: Field-Audited Alakazam v8"

| field | value |
|---|---|
| source slug | `prvsiyan/ptcg-ai-battle-field-audited-alakazam-v8` |
| source URL | https://www.kaggle.com/code/prvsiyan/ptcg-ai-battle-field-audited-alakazam-v8 |
| author | `prvsiyan` |
| public? | **YES** — `"is_private": false` in `kernel-metadata.json`; confirmed present in public `kaggle kernels list` search results |
| kaggle id_no | `128101926` |
| competition source | `pokemon-tcg-ai-battle` |
| last run (Kaggle) | `2026-07-21 22:36:01` |
| kaggle version | Version 8 of 8; public best 774.1 (V2), bronze medal |
| **license** | **Apache 2.0** — human-verified from the kernel page by Jon, 2026-07-24 ("This Notebook has been released under the Apache 2.0 open source license") |
| pull date | on/before 2026-07-24T02:18:03Z (commit `ca8a51e53`); exact pull timestamp not recorded by the puller |
| sha256 `…/kernel-metadata.json` | `0eafe7f558d2dfa498f0b8a5632b0b380d1918c270d5778eeb73d308eeaaeec2` |
| sha256 `…/ptcg-ai-battle-field-audited-alakazam-v8.ipynb` | `1bc2b61221d17bda116e27abc4f44c763df2865f9ec6ab4169b3077d2c76025e` |
| consumed by | GO-2b ratification (#1668); `GO5-OV-S2-03-alakazam-prvsiyan.json`; `GO5-OV-S2-04-secure-close.json` (hard-edge cell, champion-OFF WR 0.145) |

### 2. `prvsiyan_alakazam_v12` — "PTCG AI Battle: Search-Audited Alakazam v12"

| field | value |
|---|---|
| source slug | `prvsiyan/ptcg-ai-battle-search-audited-alakazam-v12` |
| source URL | https://www.kaggle.com/code/prvsiyan/ptcg-ai-battle-search-audited-alakazam-v12 |
| author | `prvsiyan` |
| public? | **YES** — `"is_private": false` in `kernel-metadata.json` |
| kaggle id_no | `128235234` |
| competition source | `pokemon-tcg-ai-battle` |
| kaggle version | Version 3 of 3; public best 728.8 (V3) |
| **license** | **Apache 2.0** — human-verified from the kernel page by Jon, 2026-07-24 |
| pull date | on/before 2026-07-24T02:18:03Z (commit `ca8a51e53`); exact pull timestamp not recorded by the puller |
| sha256 `…/kernel-metadata.json` | `16e6934cb447f56fc2f3a9364617c6989ca48ce951bf58b97d35ef674847bddc` |
| sha256 `…/ptcg-ai-battle-search-audited-alakazam-v12.ipynb` | `aa0cba4bda3624b129c1467ce1f5b2aa181b204b83b5e7065773d1c01b6f977c` |
| consumed by | GO-2b ratification (#1668); `GO5-OV-S2-04-secure-close.json` (easy-edge cell, champion-OFF WR 0.3625) |

All four sha256 values were computed by Master directly from the `origin/main` git blobs
(`git cat-file blob origin/main:<path> | sha256sum`), not copied from a report.

---

## ARRIVING with PR #1685 (GO-6 bakeoff spec 001) — licenses now VERIFIED by Jon

Compliance HOLD lifted (JON-DIRECT narrow permit). Licenses human-verified by Jon 2026-07-24; the
`sha256`/pull-date rows are completed by the #1685 author in `GO6-spec-001-provenance.md` (accepted
alternative form) and must match the committed notebooks before any GO-6 game runs.

- **`prvsiyan_control_v11_portfolio`** — `ptcg-ai-battle-control-v11-meta-portfolio.ipynb` —
  author `prvsiyan`; Version 1 of 1; public 735.9 (V1); **license Apache 2.0** (human-verified from
  kernel page by Jon, 2026-07-24); ipynb sha256 `93e3aae3…` (per Roach Tier-1 verify #1685).
- **`prvsiyan_rmy_grimmsnarl_hybrid`** — `ptcg-rmy-grimmsnarl-replay-hybrid-v1.ipynb` — author
  `prvsiyan`; Version 2 of 2; public **817.6** (V2); **notebook license Apache 2.0**; ipynb sha256
  `69c13532…`. **⚠ Consumes a separate DATASET** "PTCG Rmy Grimmsnarl Replay Hybrid Weights v1" —
  **license CC BY 4.0** (human-verified from the dataset page by Jon, 2026-07-24). **ATTRIBUTION
  REQUIRED:** any artifact derived from these weights — including any future ladder submission —
  must credit the dataset author (`prvsiyan`). Local evaluation and adaptation are permitted.
  - **NOT EXTRACTABLE in spec-001 (Roach Tier-1 FAIL 2):** this notebook has no `%%writefile main.py`
    / `deck_text` cell, so `extract_keval24_cell.py` skips it. Per Master re-scope ruling
    (DECISIONS.md 07-24), spec-001 runs as the **duo** (control_v11 + alakazam_v12); the grimmsnarl
    hybrid moves to its own weights-aware extraction workstream and re-enters GO-6 as a later arm.
    - **STATUS UPDATE 2026-09-04 (MASTER/4070, ATTEMPTS-LEDGER GR-83): that workstream produced a
      runtime, and this entry was never updated to say so.** A complete, importable runtime is staged
      at `external-teachers/prvsiyan-rmy-grimmsnarl-replay-hybrid-v2-runtime/` — `main.py` (exposing
      `def agent(obs_dict) -> list[int]`), `deck.csv` (60 rows), `bc_agent.py`, `model.pt` (4,044,141 B).
      Verified to import and expose `agent()` with the engine on path. Its `stage.json` records
      `notebook_sha256 = 69c13532…`, **matching the ipynb sha above**, so the derivation chain holds.
      **It is still NOT registered as a POOL opponent**, so the repo reads as blocked when it is not.
      **Two conditions before anyone seats it:** `stage.json` sets
      `fresh_process_per_trajectory_required = True` and `native_menu_order_required = True` — the
      pooled opponent path reuses a process, so a naive `OpponentSpec` would silently contaminate
      measurements; `opponents/__init__.py:246` (`--per-game-isolation`) satisfies it at a cost the
      fleet must accept deliberately. And carry `status = RECOVERED_PROPOSAL_POLICY_NOT_STRENGTH_EVIDENCE`
      / `strength_evidence = False`: acceptable for an *opponent*, but the label must not be dropped.
      The weights are `local-eval`+`opponent`, **not committable** — keep the runtime git-ignored.

---

## ARRIVING with GO6-spec-002 (cached 940/950 kernels) — LICENSES VERIFIED Apache 2.0; VERSION DRIFT

Surfaced by advisor #1695, Master-verified on disk (5080 findings
`ptcg-agent/experiments/analysis/2026-07-24-go6-spec002-license-extractability-findings-5080.md`).
Both `is_private:false`. Both shipped agents' decision code is network-free (scanned), so
`enable_internet:true` on the source notebooks is a build-time flag only.

**LICENSES VERIFIED 2026-07-24 — Jon human-read both kernel pages verbatim: BOTH Apache 2.0.**

**⚠ VERSION DRIFT (Jon page-read 2026-07-24): our CACHE holds OLDER versions than live.** The cached
shas below pin what we analyzed; the LIVE best scores are higher. Before any gate-bearing run, the
version to be run must be decided (Master) and its shas re-frozen — a re-pull of the current version is
recommended. Do NOT run the cached older bytes as if they were the 945/994 agent.

- **`aristophanivan__multiply-agent-best-940-lb`** — `multiply-agent-best-940-lb.ipynb` — author
  `aristophanivan` (Ivan Ternovskiy); **license Apache 2.0 (Jon-verified 2026-07-24, verbatim off
  page)**; **live public/best 945.4 (V2 of 2), bronze medal**; no datasets;
  CACHED ipynb sha256 `3ab0b12994b33895b62fdcf93874919548f85da6085cb2225c7dfd94ba71ec39`;
  CACHED kernel-metadata sha256 `e43496fdbf3ca42a78c1795287727b38f1e925018f7089e33bd860341562fcb9`;
  page https://www.kaggle.com/code/aristophanivan/multiply-agent-best-940-lb
  - **Extractable** with a small adapter (deck is a `DECK=[int-list]` literal, not `deck_text`).
    Parse-only extracted shas (CACHED version): `main.py` `5884a990…0da52`, `deck.csv` `2a541d7b…5357c19`.
  - **NOTE: 940's deck.csv is byte-identical to our champion `deck_lucario.csv`** — a same-deck,
    better-policy candidate (LB 940/945 vs our ~711 floor). Confirm the deck still matches after a re-pull.
- **`romanrozen__strong-start-baseline-agent-v10-lb-950`** —
  `strong-start-baseline-agent-v10-lb-950.ipynb` — author `romanrozen` (Roman Rozen); **license
  Apache 2.0 (Jon-verified 2026-07-24, verbatim off page)**; **live current public 994.0 (V13 of 14),
  SILVER medal**; lineage **"Copied from Kiyota (+68,−526)"** = our known-clean kiyotah reference family;
  CACHED ipynb sha256 `5a199c4f80b548fd38e0065863070c200b2c09ff3af1044de6f0b403d07972b6`;
  CACHED kernel-metadata sha256 `b16c3074736181fd07fef1e7c583e86715e53c3ea280c6c7883d0e15a830ae8f`;
  page https://www.kaggle.com/code/romanrozen/strong-start-baseline-agent-v10-lb-950
  - **CACHE IS STALE: cached copy is the V10/950-era pull (Jul 13); live is V13/994.0.** The
    extracted A/B payloads below are from the OLDER version; the V13 payloads/agents may differ.
    Re-pull V13 and re-extract before freezing spec shas.
  - **Extractable** with a moderate adapter (agents embedded in `AGENT_PAYLOADS=json.loads('...')`,
    no `%%writefile`/`deck_text`). Parse-only extracted shas (CACHED V10-era): A (archaludon) `main.py`
    `a4c53101…9518` / `deck.csv` `fbe6ab59…93e6`; B (alakazam/dunsparce) `main.py` `46aae796…8225` /
    `deck.csv` `0f8fb632…a36c`.
  - Declares `dataset_sources: kiyotah/cg-lib` (organizer engine — a user-republished copy; we do NOT
    need it, the eval provides its own `cg`; do not consume without a ruling) + `kiyotah/mega-lucario-ex-deck`
    (reference dataset — deck is embedded in the notebook, not sourced from it; license travels with
    the kernel review if 950 is ever shipped).

### RE-PULL RESULT 2026-07-24 (SK-31 authorized; APPENDED — rows above are the superseded audit trail)

Read-only re-pull of current versions (staged out of git at `D:/ptcg-episodes/raw/kernel-repull-20260724`).
Pin bases STATED per the recurring mixed-basis defect: ipynb sha256 = raw kaggle-pulled FILE bytes;
extracted sha256 = extracted UTF-8 content, LF newlines (= git-blob when written LF).

- **`aristophanivan/multiply-agent-best-940-lb` — V2, public 945.4, bronze — license Apache 2.0
  (Jon-verified live page).** `is_private:false`, no datasets, decision code network-free.
  - ipynb (raw file) sha256 `3ab0b12994b33895b62fdcf93874919548f85da6085cb2225c7dfd94ba71ec39`
    (**identical to our cache — 940 was already V2, no drift**).
  - extracted `main.py` `5884a990678db3ee217bb6d6fc01dd98f1ebe6b4448ba837a415babeead0da52`;
    `deck.csv` `2a541d7bf3d9e6b36037123f53f4dfef6348223f79fd27095dafc602a5357c19`.
- **`romanrozen/strong-start-baseline-agent-v10-lb-950` — V13, public 994.0, SILVER — license Apache 2.0
  (Jon-verified live V13 page).** Lineage **"Copied from Kiyota (+68,−526)"** (kiyotah reference family;
  derived-work license + attribution inherited). `is_private:false`; datasets `kiyotah/cg-lib`
  (**INADMISSIBLE PERMANENTLY — SK-43**: a user-republished copy of the organizer engine; the
  Pokémon-materials/engine ban is ABSOLUTE and not softened by the narrow permit; republishing does
  not launder it. Do NOT download, track, or reference it as a source. The eval provides its own `cg`.)
  + `kiyotah/mega-lucario-ex-deck` (fine — deck is embedded in the notebook, not sourced from it).
  Decision code network-free. **Attribution to Kiyota is INHERITED (Apache 2.0 derived work) and is a
  PRE-SUBMIT GATE if any romanrozen-derived line ever reaches a submission.**
  - ipynb (raw file) sha256 `f37c4d444eb9dd6111e87c500ef33f4d4b1349af14243c591817ee1721c6b90c`
    (**NEW — supersedes cached V10-era `5a199c4f…`; V13 dropped the multi-agent AGENT_PAYLOADS wrapper
    and is now a single `%%writefile` agent**).
  - extracted `main.py` `a81eab3eb761af95da2ddf70a67d6078897a2cd698dae4a7b6ea92de070fad2b`;
    `deck.csv` `2a541d7bf3d9e6b36037123f53f4dfef6348223f79fd27095dafc602a5357c19`.

**DECISIVE FINDING: BOTH candidates' `deck.csv` is byte-identical to our champion `deck_lucario.csv`
(`2a541d7b…`).** 940 and romanrozen-V13 both play OUR EXACT DECK with different policies -> spec-002 is
a pure same-deck POLICY bakeoff (deck held constant). The cached V10 archaludon/alakazam A/B arms are
RETIRED (they do not exist in V13). This is exactly the drift SK-31 re-pulled to catch: the register
would otherwise have described agents (archaludon/alakazam) we are not running.

**Transfer caution (records honestly, binds interpretation):** 945/994 are PUBLIC scores and do NOT
transfer 1:1 to us — our own champion's source kernel scored ~1084 public and converged to ~711–750
for us (meta drift + convergence timing). Treat 945/994 as a CANDIDATE CEILING, not an expected score.
The bakeoff + MME ≥ +60μ gate + pair-read measure the real delta before any promotion claim.

---

---

## ARRIVING 2026-07-31 (fresh-kernel adjudication) — LICENSE VERIFIED Apache 2.0

### `mechi22_1070_alakazam` — "PTCG 1070.9 Alakazam: Rule-Based Skeleton"

| field | value |
|---|---|
| source slug | `mechi22/ptcg-1070-9-alakazam-rule-based-skeleton` |
| source URL | https://www.kaggle.com/code/mechi22/ptcg-1070-9-alakazam-rule-based-skeleton |
| author | account slug `mechi22` (display name is non-ASCII Japanese; slug recorded to keep this register ASCII for `bank_lint`) |
| public? | **YES** — `"is_private": false` in `kernel-metadata.json`; page publicly viewable |
| kaggle id_no | `129187273` |
| kaggle version | **Version 6 of 6**; runtime 23s, successful |
| competition source | `pokemon-tcg-ai-battle` |
| **license** | **Apache 2.0** — human-verified from the kernel page by Jon, 2026-07-31, verbatim: *"This Notebook has been released under the Apache 2.0 open source license."* |
| `dataset_sources` | **`[]`** — declares NO datasets. In particular it does NOT declare `kiyotah/cg-lib` (permanently inadmissible under SK-43). |
| `kernel_sources` | **`[]`** — declares no parent kernel |
| `enable_internet` | `false` |
| pull date | 2026-07-31 (read-only `kaggle kernels pull`, Master) |
| sha256 `…/ptcg-1070-9-alakazam-rule-based-skeleton.ipynb` | `b3f1febec564c21e9baf50280416d636d8352a749bf76d12f1760b3f6715d7de` |
| sha256 `…/kernel-metadata.json` | `3768b935330b4e324fa369bbe10856f08ba2c1c1c6c3dabab0d6cce3e48ba921` |
| extracted `main.py` sha256 | `9b9f71473f7997812a8cc71d4aff7ea1ed0f0b1f6db00bd70704139939219b15` |
| consumed by | (pending) lineage-distinct roster admission (Misty); H2H opponent + trigger-bar candidate (5080) |

**Pin bases STATED** (per the recurring mixed-basis defect): the two file shas are **raw
kaggle-pulled FILE bytes**. The `main.py` sha is over the **raw base64-decoded bytes** of
`PAYLOADS["main.py"]` in notebook cell 8 — and it **matches the author's own published
`EXPECTED_SHA256`**, which the notebook itself asserts before writing. Independent confirmation
of the extraction, not merely of our arithmetic.

**LINEAGE: MECHANICALLY DISTINCT from the 1084-5 kernel** (Master fingerprint 2026-07-31; Misty
re-derives independently before roster admission). 3 shared function names out of 32 (ours) / 12
(theirs) — `agent`, `get_card`, `prize_count`, all trivial kiyotah-scaffold helpers; **5.7%**
verbatim substantive-line overlap (16/282), all boilerplate helper bodies; different archetype
(Alakazam vs Lucario), different decklist, 46,432 B vs 22,227 B. **This is the first mechanically
independent public agent this program has found** — our whole committee (`champion_rules`,
`v13_adapter`, `stage_940`) traces to the single 1084-5 kernel.

**⚠ THE PUBLISHED SCORES DO NOT BELONG TO THE SHIPPED CODE — bind this before any use.** The
author states it plainly and we record it as they wrote it: the archive this notebook builds is
**the skeleton alone, not the rated agent**. Peak 1071 and settled **890.2** were recorded by an
agent running **three further layers** — opponent deck inference, a learned leaf evaluator
(hand-built features + small MLP ensemble), and 1–2 ply turn-planning rollout — whose code is
**described only, not shipped**. Author, verbatim scope note: *"no claim is made that the archive
in this notebook reproduces those numbers."* **Any use of "890.2" as this artifact's expected
value is a category error.** The skeleton's own rating is unpublished and unknown.

### PANEL-CANDIDATE SWEEP 2026-07-31 (Master, read-only pulls) — 4 fingerprinted, 1 ADMITTED

Pulled to answer the ratified trigger's **lineage-diversity** membership rule. Fingerprint = the
committee test (shared function names / verbatim substantive-line overlap / shared 3-4 digit
card-ID constants) against `champion agent_ship/main.py` (`739aae36…f050`).

| candidate | shared fns | verbatim lines | card-IDs | verdict |
|---|---|---|---|---|
| `prvsiyan/ptcg-844-4-observable-meta-router-visuals` | 2/32 | **1.3%** | 27.7% | **LINEAGE-DISTINCT — ADMITTED** |
| `daniilkrasnovvv/pokemon-conservative-probabilistic-agent` | 26/32 | 28.7% | 90.3% | same family — rejected |
| `borealis27/elo-1050-rule-based-agent-matchup-tests` | 29/32 | **98.8%** | 100% | effectively our champion — rejected |
| `jaafarbk/pokemon-tcg-explainable-heuristic-agent` | 1 | 0.0% | 0.0% | 1,423 B fragment, not a full agent |

**ADMITTED MEMBER — `prvsiyan_844_router`**

| field | value |
|---|---|
| source slug | `prvsiyan/ptcg-844-4-observable-meta-router-visuals` |
| source URL | https://www.kaggle.com/code/prvsiyan/ptcg-844-4-observable-meta-router-visuals |
| author | `prvsiyan` |
| public? | **YES** — `"is_private": false` |
| kaggle id_no | `128618226` |
| `dataset_sources` / `kernel_sources` | **`[]` / `[]`** — no declared parent; does **NOT** touch `kiyotah/cg-lib` (SK-43) |
| `enable_internet` | `false` |
| **license** | ✅ **Apache 2.0 — VERIFIED 2026-07-31 by Jon's own page-read**, verbatim: *"This Notebook has been released under the Apache 2.0 open source license."* Supersedes the prior UNVERIFIED status. **Gate-bearing use is now permitted** and the notebook is committable under the narrow permit. |
| ⚠️ **SCORE — "844.4" IS A BEST-SCORE FROM V3, NOT THE BYTES WE HOLD** | Page reads **Public Score 647.3** at **Version 35 of 35**; **Best Score 844.4 (V3)**. Our pull is dated 2026-07-31 and Kaggle pulls default to the LATEST version, so the bytes in the panel are almost certainly **V35 (647.3)**, not the V3 that scored 844.4. **CONFIRM the pulled version before any claim keys on the number.** This is the THIRD instance of the same trap (1084.5 and 994.0 were both publication-epoch titles, not live scores) — the standing lesson applies: **rank kernels by diff-against-what-we-hold, never by page title or peak score.** Panel membership does NOT depend on this: member 3 was admitted for being lineage-distinct and mechanistically different (mill/route/thin), not for its score. |
| pull date | 2026-07-31 (read-only, Master) |
| sha256 ipynb (raw pulled FILE bytes) | `4fbc3710b4e4fa59099db0ba950ccfbe9e8d20da59a01c262d213496369d6bd9` |
| sha256 kernel-metadata.json | `bd30c49da3d12bce620cce2fe23933defcbdba6751515786a0d72869bdea62e5` |
| extracted `main.py` sha256 (UTF-8, LF) | `21c8bec9f0d4e4745e3a2f48feaa533225a36fe5cc4f4355d4ba487681a29b04` |
| size | 57,424 B / 1,301 lines |
| consumed by | discriminating-panel member 3 — mechi22 trigger legs; ash panel member-3 arms (#2186); router ablations |
| ✅ **REPRODUCIBILITY** | **MULTI-SEAT as of #2195 (merged `de5a4d64e`, 2026-07-31).** Runtime committed under `ptcg-agent/experiments/public_kernels/keval24/sources/prvsiyan_844_router/` (`main.py` + `deck.csv` + `ATTRIBUTION.md` + `PROVENANCE.md`). **No notebook was ever held** — the commit is the extracted runtime (same bytes `extract_keval24_cell.py` would emit). Load path for any seat: `source:ptcg-agent/experiments/public_kernels/keval24/sources/prvsiyan_844_router`. Optional SKYNET mirror `D:\policy_rows\prvsiyan_844_router` remains byte-identical (`main.py` sha `21c8bec9…a29b04`, re-verified ash 2026-08-01). |
| ✅ **CITATION RULE** | **Licence verified (Jon page-read Apache 2.0, banked #2193) and runtime is multi-seat.** Numbers derived from these pinned bytes may be cited fleet-wide **without** the SINGLE-BOX / SINGLE-SEAT label, provided the receipt pins the `main.py` sha above (or the in-repo path). Pre-#2195 SKYNET-only runs keep their historical single-box label if the sha was not pinned. |
| **UNBLOCK PATH** | **CLOSED — discharged.** Licence gate → #2193. Runtime commit → #2195. Residual score-version ambiguity (V35/647.3 vs peak V3/844.4) remains a naming caution only; it does **not** block multi-seat load or panel use. |

**Pin bases STATED:** ipynb + kernel-metadata shas are raw kaggle-pulled FILE bytes; the `main.py`
sha is over the extracted UTF-8 content with LF newlines (= git-blob when written LF).

**WHY IT IS THE RIGHT MEMBER — mechanism, not score.** `mill` occurs throughout (lines 10/61/65/
309/362/423/432…) plus `route`, `thin`, `prize`: this is the **deck-race / library-out** mechanism,
the axis our own losses name and the one NEITHER of our kernels represents. A panel of
{V13, 940, 844-router} spans **two lineages and two mechanisms** — strictly more informative than
three members of one family, which is what a bare "minimum 3 members" rule would have bought.

**⚠ A STANDING CAUTION IS PARTIALLY REFUTED:** `DECISIONS.md` 07-30 flagged *"prvsiyan trio
explicitly cautioned"* as possible 1084-5 descendants. **For THIS kernel that is refuted at the
bytes** (1.3% verbatim overlap is not descendance). The caution stands for the other prvsiyan
kernels until each is tested individually — **lineage is a per-artifact property, not an author
property**, exactly as licence is.

**⚠ AND THE REJECTIONS CARRY THE MORE USEFUL FINDING:** `borealis27` advertises **"ELO 1050"** and
is **98.8% verbatim-identical** to the bytes we measure at **711.2 μ**. That is the
title-versus-settled discount demonstrated a third independent time today, and it is direct
evidence that the 1084-5 lineage SATURATES the public pool. **Operational rule for panel building:
"another public kernel" is NOT another data point by default — fingerprint before admitting.**

## Open items

1. **RESOLVED 2026-07-24 — licenses verified.** Jon human-verified all four prvsiyan kernels as
   **Apache 2.0** (read verbatim off each kernel page) and the grimmsnarl weights **dataset** as
   **CC BY 4.0**. The earlier UNVERIFIED gap is closed. The standing rule stands for any FUTURE
   kernel: no new gate-bearing run consumes a kernel/dataset whose license row is `UNVERIFIED`, and
   licenses are never assumed by default.
2. **CC BY 4.0 attribution obligation is now load-bearing on submissions.** If any GO-6 line derived
   from the grimmsnarl weights ever reaches a ladder submission, it must credit `prvsiyan`. Carry
   this to the submission checklist, not just this register.
3. Confirm no other untracked-but-consumed public kernel exists outside this register before the
   GO-6 launch (open — assign with the GO-6 launch preflight).
4. **RESOLVED 2026-07-24 — 940 + 950 licenses verified + re-pulled.** Jon human-verified both live
   pages: 940 V2 (945.4) and romanrozen V13 (994.0) both **Apache 2.0**. Re-pulled current versions
   (SK-31); shas re-frozen in the RE-PULL RESULT block above. spec-002 is now a same-deck DUO;
   remaining gate is the extractor adapter + candidate loader, not license. Confirm the
   `kiyotah/mega-lucario-ex-deck` dataset license only if romanrozen is ever shipped (deck is embedded,
   not sourced from it).
