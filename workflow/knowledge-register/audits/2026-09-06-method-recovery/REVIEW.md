# Screening methods: recovered dispute and arithmetic

Reviewed snapshot: `d5aa507323d40c8c4b63d4fad7d3a86c1267f4e7`.
The [independent review](independent-review.json) and [ASTRA consumption](consumption.json)
bind the sources and calculations. The [original receipt envelope](original-review-envelope.json)
preserves its exact UTF-8 bytes and hash; the reading copy normalizes newlines only.

The claimed 120,000-game `rules_lucario` mirror calibration remains a historical assertion
with unresolved primary provenance in this recovered chain. The already-banked August 22
BREAKTHROUGH-VERIFICATION audit, lines 137–145, records the missing manifest, eval-index row
and producer, plus the conflicting scaling correction. This investigation did not exhaust
every disk or host; failure to recover a manifest does not prove the run never occurred.

The correction at `b139264419ae61fdae5f86a7721d260fa15b6cbf` is **not an ancestor** of
the reviewed head. Its exact [source text](unmerged-equations.json) is preserved as
unmerged evidence, without adopting its proposed conservative rule as current authority.
The current retraction of 2.199pp is not reversed here.

The nearby actual A/A receipt is a different experiment: 6,000 `v000_baseline` games,
60 blocks of 100. Retained block rates recompute to 2,941 wins and sample-variance
design effect 0.8905026. The August 2 rebuild receipt later marks this design effect
UNREAD because module load order was confounded. Its games=0 rebuild verification
does not supply the missing 120k measurement. No game program was executed here.

## What the equations do and do not establish

The historical table reports sigma values 3.529, 2.520 and 1.626 percentage points
at 400, 1,200 and 2,400 games per arm. Multiplication by 1.96 and 2.8 reproduces its
CI half-widths and MDEs. But its separate law `2.520*sqrt(1200/n)` gives 4.3648pp at
400 and 1.7819pp at 2,400. Empirical estimates need not follow exact scaling; their
unrecovered sampling uncertainty cannot be assessed here. These are distinct quantities.

Using that declared scaling law and multiplier 2.8, solving for MDE=14.81pp gives
`n = 1200*(2.8*2.520/14.81)^2 = 272.388`, or 273 whole games per arm, not 180.
This is an algebraic comparison, **not a proposed allocation** or validated power design.

For independent Bernoulli arms with probabilities pA/pB and N observations per arm:

`Var(pA_hat - pB_hat) = pA*(1-pA)/N + pB*(1-pB)/N`.

At pA=pB=0.5, `SE = 100*sqrt(0.5/N)` percentage points. At N=400 this is 3.5355pp.
The SRI M-001 expression `100/sqrt(N)` gives 5pp. That expression would instead be
correct if N meant the **combined total** across two balanced arms, contrary to its
explicit definition. This theoretical formula does not replace an empirical calibration.

For correlated arms subtract `2*Cov` from the variance; within-arm dependence also changes
the variance of each mean. No public seed-setting ABI does not imply zero covariance.
Finite-sample SD agreement cannot prove independence, and zero covariance alone is weaker
than independence. Future teacher studies need their actual units, pairing/clustering,
controls, target effect and error criterion. A universal n>=1200 guarantee does not follow.

SRI M-004's negative lower-bound wording also fails as evidence of harm: CI [-1,+1]pp
has a negative lower bound and still includes benefit. A directional harm claim requires
the relevant upper bound below the prespecified harm boundary. Operational stopping for
cost or lack of promise is a separate decision and must retain its declared rationale.

## Concrete repair and current state

[sri-methods-correction.patch](sri-methods-correction.patch) corrects M-001/M-004 at their
CURATED source and the generator's misleading claim that its definitions are literal
canonical quotations. It is **prepared, not applied**: the generator is in the active
#3469 lessons branch (the preceding #3468 cleanup is now merged). Its owner should apply it after the reader/evidence carrier is
integrated, regenerate with the current generator and verify the two consumer rows.
No hand edits to generated tables are proposed.

The reader now exposes the measurement summary plus hypothesis, metric, domain-term and
trace-source registers. Reviewed links put this dispute before each affected screening
record, the equations, retraction row and n>=1200 metric. The scientific status of the
historical source is unchanged; the missing qualification is now retrievable.

Acceptance questions: recover the calibration's missing provenance and distinct 6k control;
distinguish the empirical table, its scaling law and independent-Bernoulli formula; distinguish
an operational kill from evidence of inferiority. Games and training remain paused.

## Actual retrieval evidence

[opening-checks.json](opening-checks.json) records five normal commands at implementation/data
head `2a19ec09857d50674da44f8daa96f433d7a623c8`, including reader SHA-256, output bytes,
hashes, elapsed time and the saved output path. All exited 0 within the default 14,000-byte
budget; the largest was 12,154 bytes. These demonstrate the named retrievals, not an
unseen-question benchmark. [source-checks.json](source-checks.json) records the 20 source
hash and locator-range checks against the independent source review.

The [independent connection review](independent-connection-review.json) executed two of
these normal openings and passed 14/14 preservation assertions. Its outputs match the
saved outputs exactly; all five saved hashes and sizes match. It reviewed the final
prepared patch and its wording without applying it. [Consumption checks](connection-consumption.json)
bind the returned receipt, six reviewed source files and the two independently opened
outputs. These checks are scoped retrieval/patch acceptance, not whole-inventory acceptance.
