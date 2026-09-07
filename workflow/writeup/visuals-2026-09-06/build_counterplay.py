"""Render write-up figures from committed outcomes; never executes games or models."""
from pathlib import Path
import csv
import hashlib
import json
import math
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "research/2026-09-03-strike3-rows.csv"
ORDER = [
    ("tb_567ea9be_llccqq624_ptcg-alakazam-marniebelief-0723-a", "Alakazam · llccqq624*"),
    ("tb_64e9991a_raunakdey07_pok-mon-tcg-advanced-heuristic-agent", "Alakazam · raunakdey07"),
    ("tb_4b3946f9_plamen06_pokemon-steel", "Steel · plamen06"),
    ("tb_a4c53101_aristophanivan_one-of-snapshot-versions", "Snapshot · aristophanivan"),
    ("tb_ded5c6a6_zoli800_top-dragapult-ex-tempo-control-agent", "Dragapult · zoli800"),
    ("tb_eb8c2384_harukiharada_crustle-wall-mirror-ok", "Crustle · harukiharada"),
    ("tb_f2e2c18d_grimmsnarl_bc_alias", "Grimmsnarl · grimmsnarl_bc†"),
]


def main():
    rows = list(csv.DictReader(SOURCE.open(encoding="utf-8", newline="")))
    assert len(rows) == 8400
    assert {r["opponent"] for r in rows} == {x[0] for x in ORDER}
    assert {r["arm"] for r in rows} == {"BASELINE", "CHAMPION"}
    values = {"win": 1., "draw": .5, "loss": 0.}
    result = []
    for key, label in ORDER:
        arms = {}
        for arm in ("BASELINE", "CHAMPION"):
            selected = [r for r in rows if r["opponent"] == key and r["arm"] == arm]
            assert len(selected) == 600
            assert len({r["game_index"] for r in selected}) == 600
            assert all(sum(r["seat"] == seat for r in selected) == 300 for seat in ("first", "second"))
            scores = [values[r["outcome"]] for r in selected]
            arms[arm] = {"n": len(scores), "mean": statistics.mean(scores),
                         "variance_of_mean": statistics.variance(scores) / len(scores),
                         "outcomes": {k: sum(r["outcome"] == k for r in selected) for k in values}}
        delta = 100 * (arms["CHAMPION"]["mean"] - arms["BASELINE"]["mean"])
        variance = 10000 * sum(v["variance_of_mean"] for v in arms.values())
        result.append({"opponent": key, "label": label, "arms": arms, "delta_pp": delta,
                       "variance_pp2": variance, "ci95_pp": [delta - 1.96 * math.sqrt(variance), delta + 1.96 * math.sqrt(variance)]})
    a = statistics.mean(r["delta_pp"] for r in result[:2])
    n = statistics.mean(r["delta_pp"] for r in result[2:])
    va = sum(r["variance_pp2"] for r in result[:2]) / 4
    vn = sum(r["variance_pp2"] for r in result[2:]) / 25
    payload = {"source": str(SOURCE.relative_to(HERE.parents[2])).replace("\\", "/"),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "method": "Draw-half scores; sample variance/n per arm; independent-arm and independent-cell normal 95% intervals. Fixed opponent implementations, no new-opponent uncertainty or multiplicity correction.",
               "cells": result, "equal_weight_groups": {"alakazam_pp": a, "other_five_pp": n,
               "alakazam_variance_pp2": va, "other_five_variance_pp2": vn,
               "illustrative_q25_pp": .25*a + .75*n}}
    (HERE / "counterplay-data.json").write_bytes((json.dumps(payload, indent=2) + "\n").encode("utf-8"))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.spines.left": False, "axes.labelcolor": "#34465a",
                         "text.color": "#18334c", "xtick.color": "#34465a", "ytick.color": "#18334c",
                         "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(12, 6.8))
    fig.subplots_adjust(left=.32, right=.96, bottom=.23, top=.78)
    for i, row in enumerate(result):
        color = "#007f86" if i < 2 else "#65788b"
        ax.axhspan(i-.43, i+.43, color="#edf7f7" if i<2 else "#f5f7f9", zorder=0)
        ax.errorbar(row["delta_pp"], i, xerr=1.96*math.sqrt(row["variance_pp2"]), fmt="o",
                    color=color, capsize=5, markersize=8, linewidth=2.3)
        ax.annotate(f'{row["delta_pp"]:+.2f}', (row["delta_pp"], i), xytext=(0, 12),
                    textcoords="offset points", ha="center", fontsize=11, weight="bold", color=color)
    ax.axvline(0, color="#334e68", linestyle=(0,(3,3)), linewidth=1)
    ax.set_yticks(range(7), [x[1] for x in ORDER]); ax.invert_yaxis()
    ax.tick_params(axis="y", length=0, pad=12)
    ax.set_xlim(-12,30); ax.set_xticks([-10,0,10,20,30]); ax.set_xlabel("Change in mean game score (percentage points)", labelpad=13)
    fig.text(.055,.94,"A counter with a clearly bounded advantage",fontsize=23,weight="bold")
    fig.text(.055,.885,"One Carmine → Xerosic, plus targeting enabled  |  compared with the original deck and targeting off",fontsize=11)
    fig.text(.055,.075,"8,400 recorded games · 600 per arm per opponent · win = 1, draw = ½, loss = 0\nPoints: measured differences. Whiskers: approximate 95% intervals for these fixed implementations.",fontsize=10,linespacing=1.6)
    fig.text(.055,.017,"* Development deck reused under another pilot.  † This pilot is distinct from submitted c61.",fontsize=9)
    for ext in ("png","svg","pdf"): fig.savefig(HERE / f"01-matchup-evidence.{ext}",dpi=220,facecolor="white")
    plt.close(fig)
    q=np.linspace(0,1,401); mean=q*a+(1-q)*n; margin=1.96*np.sqrt(q*q*va+(1-q)**2*vn)
    fig,ax=plt.subplots(figsize=(10,6.3));fig.subplots_adjust(left=.12,right=.94,top=.76,bottom=.33)
    ax.fill_between(q*100,mean-margin,mean+margin,color="#007f86",alpha=.14)
    ax.plot(q*100,mean,color="#007f86",linewidth=3)
    ax.axhline(0,color="#334e68",linestyle=(0,(3,3)),linewidth=1)
    ax.scatter([25],[.25*a+.75*n],color="#18334c",s=50,zorder=3)
    ax.annotate(f"Illustration: 25% → {(.25*a+.75*n):+.2f} pp",(25,.25*a+.75*n),xytext=(37,1),arrowprops={"arrowstyle":"-","color":"#65788b"},fontsize=11)
    ax.set(xlim=(0,100),ylim=(-5,25),xlabel="Assumed Alakazam share of this seven-opponent mixture (%)",ylabel="Expected score change (pp)")
    fig.text(.065,.93,"Opponent mix changes the value of the counter",fontsize=21,weight="bold")
    fig.text(.065,.865,"Sensitivity analysis · assumed mixture, not a measured competitive meta",fontsize=12)
    fig.text(.065,.065,f"Δ(q) = {a:.3f}q + ({n:.3f})(1 − q) pp; q is a fraction.\nEqual weights within the two Alakazam cells and within the other five. Shading: approximate 95%\nuncertainty in fixed-cell means; excludes uncertainty about meta share and unseen opponents.",fontsize=10,linespacing=1.6)
    for ext in ("png","svg","pdf"): fig.savefig(HERE / f"02-mixture-sensitivity.{ext}",dpi=220,facecolor="white")
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,5.4));ax.set(xlim=(0,12),ylim=(0,5.4));ax.axis("off")
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
    ax.text(.45,4.9,"From observation to a playing decision",fontsize=23,weight="bold")
    ax.text(.45,4.5,"Submitted public foundation and experimental counter are separate products",fontsize=12)
    lanes=[(3.0,"Submitted Grimmsnarl · tetsutani c61 · unmodified", "#365f84",[
        "Observation\n+ recent actions", "Tree ensemble\n+ policy proposals", "Controller\n+ tactical checks", "Check selection\nReturn indices"]),
        (1.2,"Experimental Lucario · community-derived · tested card + targeting change", "#007f86",[
        "Visible board\n+ available choices", "Score attack plans\nTarget preference", "Choose actions\nfor the plan", "Return selection\nEngine resolves"])]
    for y,title,color,labels in lanes:
        ax.text(.45,y+.98,title,fontsize=12,weight="bold",color=color)
        for i,label in enumerate(labels):
            x=.45+2.95*i
            ax.add_patch(FancyBboxPatch((x,y),2.45,.73,boxstyle="round,pad=0.08",facecolor="#f3f7fa",edgecolor=color,linewidth=1.5))
            ax.text(x+1.225,y+.365,label,ha="center",va="center",fontsize=12)
            if i<3:ax.annotate("",(x+2.83,y+.365),(x+2.56,y+.365),arrowprops={"arrowstyle":"->","color":color,"lw":1.8})
    ax.text(.45,.37,"Simplified source paths. Boxes describe implementation, not execution frequencies or strength.\nThe teacher-to-student learning cycle remains future work.",fontsize=10,linespacing=1.5)
    for ext in ("png","svg","pdf"):fig.savefig(HERE / f"03-decision-paths.{ext}",dpi=220,facecolor="white")
    plt.close(fig)
    for svg in HERE.glob("*.svg"):
        svg.write_bytes(b"\n".join(line.rstrip() for line in svg.read_bytes().splitlines()) + b"\n")
    print(json.dumps(payload["equal_weight_groups"],indent=2))


if __name__ == "__main__":
    main()
