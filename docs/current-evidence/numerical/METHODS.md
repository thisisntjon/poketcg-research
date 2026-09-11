# Verify the numerical results

From this directory, run:

```text
python verify_results.py --output verified-results.json
```

Python 3.10 or newer is sufficient. The command prints a human-readable summary,
writes the full machine-readable results, and exits nonzero on missing or altered
input, malformed or duplicate games, unexpected cohort/seat counts, or a failed
published-value check. `--json` prints only the machine-readable result to stdout.
No network, engine, account, GPU, model weights or third-party Python package is
needed. Paths are resolved beside the script, regardless of the working directory.

This verifies **arithmetic from saved terminal outcomes**. It does not rerun the
original players, reconstruct all historical execution conditions, independently
validate seeds, or prove that every decision in the original games was correct.
No new games or training were performed to prepare this package.

## Portable files

Keep these files together:

- `verify_results.py`
- `SOURCE-MANIFEST.json`
- `development-outcomes.csv`
- `panel-outcomes.csv`
- `anchor-outcomes.csv`
- `student-outcomes.csv`
- `learning-summary.json`
- `opponents.json`
- `retained-opponent-identity.json`
- `activation-checks.json`
- `METHODS.md`

`verified-results.json` and `VERIFICATION.txt` are saved output for convenient
inspection; the command can regenerate them. `build_from_sources.py` is a separate
maintainer tool requiring the original research checkout and saved learning
receipts. It is unnecessary for portable verification.

## What is included

| Outcome file | Records | Selection |
|---|---:|---|
| Development | 28,000 | Five named cohorts from the original combined CSV, plus the separate 4,000-record reproduction on the 4070 |
| Seven-opponent panel | 8,400 | All records; 600 per arm/opponent, exactly 300 in each seat |
| Exact-c61 follow-up | 16,000 | All four original follow-up parts, 8,000 per arm, 4,000 per seat/arm |
| Historical student | 1,203 | All per-game records in the historical screen receipt; 1,200 decided and three draws |

The exports contain only cohort, arm, anonymous opponent identifier, game index,
seat, terminal outcome and original source locator. They contain no card-state
observations, decks, organizer engine, teacher labels, weights or third-party
policy implementations. `opponents.json` maps the identifiers to the implementation
aliases already used in the research report; where available, it preserves the
historical candidate inventory's policy/deck hashes. The seventh panel alias lacked
a matching full-hash row there. A September 11 inspection recovered full hashes
from retained files matching the historical report's prefixes, recorded in
`retained-opponent-identity.json`. Its deck matches c61 and its policy differs.
Retained-file identity does not independently reconstruct historical execution.

`SOURCE-MANIFEST.json` records exact hashes of the inspected source files and the
exported data. Git normalized six original JSONL files to LF in this checkout;
their historical manifests recorded CRLF bytes. **All six match the historical
SHA256 exactly after LF-to-CRLF normalization.** Both raw current and historical
CRLF-equivalent hashes are provided. This establishes a byte correspondence with
those saved manifests, not independent certification of the original experiments.

## Development: within-batch comparisons

All development comparisons exclude draws: `p = wins / (wins + losses)`.
Each arm requested 2,000 games, with five equally represented opponent aliases;
two of the five are Alakazam implementations. Every exported opponent/arm cell
contains 200 first-seat and 200 second-seat games.

| Effect | Included treatment-versus-control comparisons |
|---|---|
| Card alone | `xerosic_screen1` variant/control; `xerosic_replicate` variant/control; `factorial` C_xerosic/A_baseline |
| Targeting rule alone | `sniper_screen1` ON/OFF; `factorial` B_sniper/A_baseline |
| Combined | `factorial` D_both/A_baseline; `combined_replicate` D_both/A_baseline; `combined_reproduction_4070` D_both/A_baseline |

The source development CSV contains 36,000 records across additional experiments.
Those extra cohorts are **not** additional replications of these effects. The
export selects exactly 24,000 applicable records from that CSV and appends the
separate 4,000-record reproduction once. The three combined comparisons used two
computers: factorial and replicate on the 5080, reproduction on the 4070. Factorial arms are reused
across distinct component questions; the reported card, rule and combined pooled
estimates are consequently not independent of one another.

For an independent-arm comparison, difference in percentage points is
`d = 100 * (p_treatment - p_control)` and estimated variance is
`v = 10000 * [p_treatment*(1-p_treatment)/n_treatment + p_control*(1-p_control)/n_control]`.
Within each named effect, pool its distinct batch contrasts with `w_i = 1/v_i`,
`d_pool = sum(w_i*d_i)/sum(w_i)`, and `v_pool = 1/sum(w_i)`.
The 95% interval is `d ± 1.96*sqrt(v)`. These are fixed inverse-variance summaries
of the specified experiments, not estimates of the competitive metagame.

The four-arm interaction is `p_D - p_C - p_B + p_A`, multiplied by 100.
Its variance is the sum of the four independent-arm mean variances. Its interval
contains zero: these data do not establish synergy or prove additivity.

**Rounding correction:** the exact combined interval is
`[6.079377392259157, 9.554363678201325]` percentage points. Rounded directly to two
decimals, that is **[6.08, 9.55]**. Earlier prose printed an upper limit of 9.56.
The effect, inference and retained observations are unchanged.

## Seven-opponent panel and mixture

Score each game `win=1`, `draw=0.5`, `loss=0`. Keep all 600 records in each
opponent/arm denominator. For scores `x_1 ... x_n`, use the unbiased sample
variance of scores divided by `n`:

```text
mean = (wins + draws/2) / n
variance_of_mean = (wins + draws/4 - n*mean*mean) / (n*(n-1))
```

The difference variance is the sum of the two arm mean variances, multiplied by
10,000. Normal 95% intervals assume independent games, arms and opponent cells.
They condition on these fixed implementations and do not include uncertainty
about new opponents or metagame composition. No multiplicity adjustment is applied;
matchup/seat breakdowns are descriptive follow-up analyses, not seven independent
confirmatory discoveries.

This matches the **current article's figures**, whose earlier
`counterplay-data.json` uses sample variance/n. The older public
`2026-09-03-strike3-recompute.py` used `p*(1-p)/n` even for fractional draw scores
and also printed fixed/random-effects summaries. Those are different conventions
and estimands. This verifier checks all seven cell variances against the current
figure data, within 1e-10 percentage-points squared. Reference member:
`original-evidence/workflow/writeup/visuals-2026-09-06/counterplay-data.json`,
SHA256 `8dc89872395e8d87f7d776254b798c7b74d02006fbfad30c8b507598138a5cab`,
in the inspected September 8 package.

The two Alakazam deltas are equally weighted. The other five are equally weighted.
For a group of `k` cells, `d_group = sum(d_i)/k` and
`v_group = sum(v_i)/(k*k)`. One Alakazam deck was present in development under a
different pilot. The development and follow-up panels therefore do not establish
unseen-deck generalization.

For an assumed Alakazam field share `q`, keeping equal weights within groups:

```text
delta(q) = q * 19.5833333333333 + (1-q) * (-0.466666666666667) pp
variance(q) = q*q*v_Alakazam + (1-q)*(1-q)*v_Other
```

At `q=0.25`, the estimate is +4.5458333333333 pp. This reuses the same panel and
is an illustrative sensitivity calculation. It is not a measured metagame, a
deployment threshold, or a fresh replication.

Seat summaries aggregate outcomes within each fixed group and seat; they do not
reweight opponent cells by their precision. The first-minus-second interval uses
the sum of the two seat-effect variances. Gains in both seats do not prove seat
independence. Seat balance alone does not verify independent random seeds.

## Exact-c61 follow-up

The candidate remains the experimental Lucario derivative. Exact c61 is the
**opponent** in this comparison. Baseline counts are 3,463 wins, 4,508 losses,
29 draws; combined counts are 3,457 wins, 4,526 losses, 17 draws. Exclude draws,
giving denominators 7,971 and 7,983. Use the same independent-binomial difference
formula as development. This follow-up is separate from the seven-opponent panel
and excludes the earlier 4,000-record anchor screen.

Its approximate interval permits modest benefit or harm. A failure to detect a
penalty does not prove equality, zero cost, or universal safety across opponents.

Saved `activation-checks.json` fields document the two original child-process
flag/deck-prefix checks. The outcome records were also checked for the recorded
`rules_lucario` effective policy and absence of recorded errors during export.
Neither replaces full reconstruction of historical code, engine, seed generation,
process state or per-decision behavior.

## Historical learner

The screen receipt's full per-game list yields 23 wins and 1,177 losses, plus three
draws. Scored records' `win` flags were checked against `result == seat` during
export. All non-scored records were explicitly `void_draw`, with draw result 2.
Each seat has 600 decided games. The student win rate is 23/1,200 = 1.9166667%.

`learning-summary.json` preserves the training receipt's 1,358 learner-state
teacher-decision count, checkpoint identities, seed, completed epochs and selected
validation metrics. **The count is a receipt assertion**, not a recount of the
original labeled decision records in this bundle. The training receipt's selected
state hash matches the screen receipt's child-state hash. The original trainer was
inspected separately for how those labels entered training; that source inspection
is distinct from this portable arithmetic command.

Validation NLL changed from 1.0717802047729492 to 1.0417600870132446 on the
checkpoint-selection validation set. This is not untouched-holdout evidence,
does not isolate the effect of learner-state teaching, and does not establish
improved game strength relative to the parent. The screen evaluates the historical
August checkpoint/runtime combination, not later v2 runtime changes.

## Scope and attribution

These are original research outcome exports and analysis, credited to Jonathan
Simone. The submitted c61 policy is credited to Tetsutani; the experimental
Lucario lineage derives from makthanithin's Apache-2.0 community policy. Outcomes
against third-party implementations are attributed by the saved aliases and
source hashes in `opponents.json`; those programs are not included here.
Publication of this arithmetic bundle does not resolve any separately documented
upstream license/provenance gaps or satisfy full winner-code delivery by itself.
