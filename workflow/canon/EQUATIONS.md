# CANON — EQUATIONS (verified constants; check RETRACTIONS.md before citing anything else)
**Created 2026-08-07 (Strategist). This file exists because the fitted-equation constants
lived only in bus posts and memory — a genuine canon gap found by the MVP-20 sweep
(`workflow/research/2026-08-07-mvp20-conversion.md`). One entry per equation; corrections
by deletion.**

## §E-MU — ladder rating model (fitted 2026-08-06, 9,483,374 EpisodeAgents rows, R²=0.999997)

```
TrueSkill: beta = 149.8034 ± 0.0004 · tau = 0 · mu0 = 600 · sigma0 = 200
           sigma floor 35.0 · sigma-step cap −15
Outcome:   P(win) = Φ(Δμ / b)
```

### The three b-curves — three different questions (Sol Q4 ruling, 2026-08-07, Jon-backed)

| b | μ per +1pp | Question it answers | Approval status |
|---|---|---|---|
| 217.55 | **5.45** | mechanical TrueSkill scale at the σ-floor | **CONSERVATIVE — use for approval** |
| 265.7 | **6.66** | empirical band-local outcome curve | **SENSITIVITY — show alongside** |
| 366.8 | 9.20 | provisional mixed curve | **EXCLUDED from approval arithmetic** (producer/filters/holdout/re-fit unverified — verification debt) |

**Rules:** price every candidate at 5.45 AND 6.66, show both. Never approve on 9.2.
Never linearize across >50μ — use the full probit. The operative long-form method is
MU-BRIDGE (W/D/L by exact stratum × rating-conditioned exposure × update kernel).

### Slot identities (measured)

```
sigma_draw (same-bytes ladder draw)          = 27.5 mu
matched-maturity same-bytes spread           = 31–40 mu
E[max] of two iid copies, spread sigma_d     = mu + sigma_d/sqrt(pi)  (= mu + 15.5 at 27.5)
E[max(B,C)] two independent legs             = mu_B·Φ(d/θ) + mu_C·Φ(−d/θ) + θ·φ(d/θ),
                                               d = mu_B − mu_C, θ = sqrt(σ_B² + σ_C²)
maturity                                     = 85–100 h; reads < 85 h are NOT observations
```

### Local screening noise (measured — provenance: `MEASURED-2026-08-06.md` §2, the 120k-game
mirror measurement; the former "reinstated per RETRACTIONS" cite was a phantom — RETRACTIONS
had no σ_Δ row until 2026-08-23, when the `2.199pp @n=400` value was retracted there; probe C-C)

```
sigma_Delta(n=400) = 3.53pp · sigma_Delta(1200) = 2.52pp · sigma_Delta(2400) = 1.63pp
admit doctrine z>4  =>  n=1200 admits >=10.1pp · n=2400 admits >=6.5pp
  (>=10.1pp is the z>4 ADMIT bar = 4*sigma_Delta, NOT the MDE — the MDE@80% at n=1200 is
   7.06pp per MEASURED-2026-08-06 SS2; the two numbers answer different questions. C-F.)
direct H2H at n=10,000: MDE = 1.80pp at alpha=.01 one-sided, 90% power
n=400 is KILL-ONLY. Never extend N after a promising partial (peeking).
```

### Field anchors (SNAPSHOT 2026-08-07T16:43Z — these move; re-read, never cite stale)

```
teams 6,519 · top-10% line 840.8 (rank 652) · line RISING intraday; entry deadline
2026-08-09 ends dilution · grading band planning ~830–870 (assumption A-LINE-v2)
"errors consume no submission slot" = UNVERIFIED on live pages (doctrine only)
runner = kaggle_environments env cabt, pinned 1.14.10 · 600 s per-agent per-episode pool
```

Provenance: fit = LANE-6 (bus-banked 2026-08-06); σ_Δ = 120k-game measurement 2026-08-06;
Sol Q4 adjudication + Strategist adoption 2026-08-07 (bus #2638 5213376649); field = live
API reads 2026-08-07 (`workflow/research/2026-08-07-mvp20-web.md`).

### Derived receipts (2026-08-08)

The 4.27pp transitivity prediction now has its probit derivation on main:
[`workflow/receipts/2026-08-08-transitivity-derivation-apprentice.md`](../receipts/2026-08-08-transitivity-derivation-apprentice.md)
(predicted +4.27pp vs measured +1.00pp, shortfall z ≈ 5.9; all inputs no-search scope).
Convergence dynamics derived from these constants (reversion half-life ≈1.28 days at the
σ-floor; stationary spread 24.7μ reproducing σ_draw 27.5): PR #2773 receipt §2.
