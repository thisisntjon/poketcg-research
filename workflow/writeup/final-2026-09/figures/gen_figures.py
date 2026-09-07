"""Figures 1-2 for FINAL-v2 ("The Ladder Cannot See You Improve").

Every constant here is receipt-backed:
  - local law: 1pp at z=3 needs ~13,300 games/cell (4-cell panel mean), A/A calibrated
  - ladder:    sigma_delta(mature pair) = 38.9 mu, 5.45 mu/pp  ->  z=3 MDE = 21.41/sqrt(k) pp
  - 458 pairs needed for 1pp, ~45 available; 400-game screens resolve ~5.8pp (panel mean)
Figure 3 (matchup profile) is deliberately NOT generated: its cells have no on-disk
receipts yet (verification-pass finding, 2026-08-08).
Palette: dataviz reference instance, light mode, slots 1-2 (validated order).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, SEC, MUT = "#0b0b0b", "#52514e", "#898781"
GRID, BASE, SURF = "#e1e0d9", "#c3c2b7", "#fcfcfb"
BLUE, ORANGE, CRIT = "#2a78d6", "#eb6834", "#d03b3b"

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 9,
    "axes.edgecolor": BASE, "axes.linewidth": 0.8,
    "axes.labelcolor": SEC, "xtick.color": MUT, "ytick.color": MUT,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
})

# ---------------------------------------------------------------- Figure 1
fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.2), sharey=True, constrained_layout=True)

n = np.logspace(np.log10(150), 5, 200)
mde_local = np.sqrt(13300.0 / n)              # pp, panel-mean, z=3 (calibrated to A/A law)
k = np.logspace(0, 3, 200)
mde_ladder = 21.41 / np.sqrt(k)               # pp, z=3, sigma_d=38.9mu @ 5.45mu/pp

for ax in axes:
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(0.4, 40)
    ax.grid(True, which="major", color=GRID, lw=0.6)
    ax.grid(False, which="minor")
    ax.axhline(1.0, color=MUT, lw=1.0, ls=(0, (4, 3)))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([0.5, 1, 2, 5, 10, 20])
    ax.set_yticklabels(["0.5", "1", "2", "5", "10", "20"])

axL, axR = axes
axL.plot(n, mde_local, color=BLUE, lw=2)
axL.plot([400, 13300], [np.sqrt(13300/400), 1.0], "o", color=BLUE, ms=7,
         mec=SURF, mew=1.5)
axL.annotate("400-game screen: ~5.8pp\n(4-cell pool; ~11pp single-cell)", (400, 5.77), xytext=(170, 13),
             color=SEC, fontsize=8.2)
axL.annotate("1pp detectable at\n~13,300 games/cell", (13300, 1.0), xytext=(3200, 0.52),
             color=SEC, fontsize=8.2)
axL.set_title("Local instrument  (4-cell panel, A/A-calibrated)", color=INK,
              fontsize=10, loc="left")
axL.set_xlabel("games per cell per arm")
axL.set_ylabel("smallest detectable effect at z = 3  (pp)", color=SEC)

axR.plot(k, mde_ladder, color=ORANGE, lw=2)
axR.axvline(45, color=MUT, lw=1.0, ls=(0, (2, 2)))
axR.plot([45, 458], [21.41/np.sqrt(45), 1.0], "o", color=ORANGE, ms=7,
         mec=SURF, mew=1.5)
axR.annotate("all pairs available\nbefore the wall: ~45\n→ resolves only ~3.2pp",
             (45, 3.19), xytext=(1.4, 1.3), color=SEC, fontsize=8.2)
axR.annotate("1pp needs 458 pairs\n(10× the budget)", (458, 1.0), xytext=(120, 6.5),
             color=SEC, fontsize=8.2)
axR.set_title("The ladder  (mature submission pairs, σΔ = 38.9 μ)", color=INK,
              fontsize=10, loc="left")
axR.set_xlabel("independent submission pairs")

axL.text(160, 1.08, "the ~1pp class our candidates actually produced", color=MUT,
         fontsize=8, va="bottom")
fig.suptitle("Figure 1 — What each instrument can detect. Real decisions must be made "
             "locally: the ladder cannot see them.", color=INK, fontsize=11, x=0.01,
             ha="left")
fig.savefig(r"C:\Users\thisi\Desktop\CAREER-PORTFOLIO\D1-strategy-writeup\figures\fig1-resolution.png",
            dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
rows = [
    ("1", "Measured a module the agent never loads",
     "clean candidate-vs-control deltas",
     "weeks of screens ran the agent against a byte-identical fallback of itself"),
    ("2", "Code census inherited the same error",
     "handlers found for 20 of 49 decision contexts",
     "the live policy branches on 6 (verified at the bytes)"),
    ("3", "A confident signal that was noise",
     "+0.592pp, all 4 cells positive (n = 12,000)",
     "−0.154pp when re-screened fresh at n = 31,000"),
    ("4", "A variance estimate on 5 degrees of freedom",
     "harness noise 1.48× binomial",
     "0.9–1.2× per cell, mean ≈1.0; CI contains the null"),
    ("5", "A panel that could not trigger what it screened",
     "archetype rule reads −0.296pp (no panel deck plays it)",
     "−2.153pp (z = −5.07) on a cell that does"),
    ("6", "A text search with nothing it could find",
     "0 matches over the deck files → “clean”",
     "the files hold only numeric IDs; the query can never match"),
]
fig2, ax = plt.subplots(figsize=(9.6, 5.6))
ax.set_axis_off()
top, rh = 0.815, 0.132
ax.text(0.055, 0.905, "what the instrument reported", color=MUT, fontsize=8.8,
        weight="bold", transform=ax.transAxes)
ax.text(0.535, 0.905, "what was true", color=MUT, fontsize=8.8, weight="bold",
        transform=ax.transAxes)
for i, (num, name, said, truth) in enumerate(rows):
    y = top - i * rh
    if i:
        ax.plot([0.0, 1.0], [y + rh * 0.60] * 2, color=GRID, lw=0.7,
                transform=ax.transAxes)
    ax.add_patch(plt.Circle((0.018, y + 0.052), 0.0135, color=BLUE,
                            transform=ax.transAxes))
    ax.text(0.018, y + 0.050, num, color=SURF, fontsize=8.5, weight="bold",
            ha="center", va="center", transform=ax.transAxes)
    ax.text(0.055, y + 0.052, name, color=INK, fontsize=9.6, weight="bold",
            va="center", transform=ax.transAxes)
    ax.text(0.055, y - 0.004, said, color=SEC, fontsize=8.6, transform=ax.transAxes)
    ax.text(0.535, y - 0.004, "✗  " + truth, color=CRIT, fontsize=8.6,
            fontfamily="DejaVu Sans", transform=ax.transAxes)
ax.text(0.0, 0.012,
        "Every failure produced clean output, plausible magnitudes, and no errors.  "
        "The control that closes the class:\n“Would this check produce the same output "
        "if the thing it describes were completely broken?”",
        color=INK, fontsize=9, style="italic", transform=ax.transAxes)
fig2.suptitle("Figure 2 — Six ways the instrument lied before it was an instrument",
              color=INK, fontsize=11, x=0.01, ha="left")
fig2.savefig(r"C:\Users\thisi\Desktop\CAREER-PORTFOLIO\D1-strategy-writeup\figures\fig2-failure-modes.png",
             dpi=200, bbox_inches="tight")

# ---------------------------------------------------------------- Figure 3: the funnel
# Counts verified at the bytes 2026-08-08 (ARCHITECTURE-v1.md §1).
stages = [
    ("mechanisms proposed", 68),
    ("implemented as exact candidates", 122),
    ("screened  (n ≥ 400)", 106),
    ("powered confirmation  (n ≥ 1200)", 67),
    ("survived at power", 0),
    ("ladder submissions", 26),
]
SEQ = ["#104281", "#184f95", "#256abf", "#2a78d6", "#5598e7", "#86b6ef"]
fig3, ax = plt.subplots(figsize=(9.2, 4.0))
ys = range(len(stages))[::-1]
vals = [v for _, v in stages]
mx = max(vals)
for (label, v), y, c in zip(stages, ys, SEQ):
    w = max(v / mx, 0.012)
    ax.barh(y, w, height=0.62, color=c if v else "#e34948", zorder=3)
    ax.text(-0.015, y, label, ha="right", va="center", color=INK, fontsize=9.3)
    ax.text(w + 0.012, y, f"{v}", va="center", color=INK, fontsize=10, weight="bold")
ax.set_xlim(-0.55, 1.12); ax.set_ylim(-0.9, len(stages) - 0.4)
ax.set_axis_off()
ax.text(-0.55, -0.62, "2,833,711 games in the final measurement window · 421,749-game "
        "matchup dataset · 2,209 merged PRs · every count receipt-traced",
        color=SEC, fontsize=8.4)
ax.text(-0.55, -0.88, "122 > 68 because several mechanisms shipped as multiple exact "
        "candidates, and 35 were borrowed public kernels", color=MUT, fontsize=8)
fig3.suptitle("Figure 3 — What we tested, honestly counted: the hypothesis funnel",
              color=INK, fontsize=11, x=0.01, ha="left")
fig3.savefig(r"C:\Users\thisi\Desktop\CAREER-PORTFOLIO\D1-strategy-writeup\figures\fig3-funnel.png",
             dpi=200, bbox_inches="tight")

# ------------------------------------------------------- Figure D1: matchup profile
# Fresh receipted cells, seq-808 session 2026-08-08, n=1200 each, our policy (agent.main).
cells = [
    ("Raging Bolt (yakitori55)",            98.08, 97.31, 98.86),
    ("Lucario mirror (kokinnwakashuu)",     59.25, 56.47, 62.03),
    ("kojimar (baseline tests)",            49.08, 46.25, 51.91),
    ("aristophanivan (probabilistic)",      46.17, 43.35, 48.99),
    ("Mega Lucario v62 (pixiux)",           45.67, 42.85, 48.49),
    ("Grimmsnarl ex control (tetsutani)",   44.08, 41.27, 46.89),
    ("Crustle library-out (prvsiyan)",      33.67, 30.99, 36.34),
    ("Alakazam belief v22 (prvsiyan)",      33.00, 30.34, 35.66),
    ("Steel wall (plamen06)",               28.50, 25.95, 31.05),
]
figd, ax = plt.subplots(figsize=(8.6, 4.6))
ax.set_facecolor(SURF)
ax.axvline(50, color=MUT, lw=1.0, ls=(0, (4, 3)))
ax.text(51.0, len(cells)-0.55, "even", color=MUT, fontsize=8)
for i, (name, wr, lo, hi) in enumerate(cells):
    y = len(cells) - 1 - i
    ax.plot([lo, hi], [y, y], color=BLUE, lw=2, solid_capstyle="round", zorder=3)
    ax.plot(wr, y, "o", color=BLUE, ms=8, mec=SURF, mew=1.5, zorder=4)
    ax.text(lo - 1.0, y, name, ha="right", va="center", color=INK, fontsize=9)
    ax.text(hi + 1.0, y, f"{wr:.1f}%", va="center", color=SEC, fontsize=8.6)
ax.set_xlim(0, 104); ax.set_ylim(-0.6, len(cells) - 0.2)
ax.set_yticks([])
ax.set_xlabel("win rate vs real competition pilots  (n = 1,200 per cell, 95% CI)",
              color=SEC)
ax.grid(True, axis="x", color=GRID, lw=0.6)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
figd.suptitle("Figure D1 — The matchup boundary, measured: competitive vs tempo decks, "
              "beaten by disruption, lock, and walls", color=INK, fontsize=11,
              x=0.01, ha="left")
figd.savefig(r"C:\Users\thisi\Desktop\CAREER-PORTFOLIO\D1-strategy-writeup\figures\figD1-matchup.png",
             dpi=200, bbox_inches="tight")
print("done")
