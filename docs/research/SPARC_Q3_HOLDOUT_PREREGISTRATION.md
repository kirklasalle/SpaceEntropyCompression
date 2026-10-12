# SPARC quality-3 holdout preregistration

- **Study:** `sparc-q3-holdout-v1`
- **Status:** completed from the preregistered contract on protected `main`
- **Authoritative contract:** `research/preregistrations/sparc_q3_holdout_v1.json`
- **Current commitment:** `20261012T211327324282Z-d6ab49c9b4b7`
- **Canonical JSON SHA-256:** `d6ab49c9b4b7ecdc50bad2a57b5018ccffd0736bafcc7d61a59472e38614a602`
- **Superseded pre-outcome commitment:** `20261012T205817322791Z-806cce833d62`

The first commitment remains preserved. Review found that its multi-start
convergence gate did not state whether one failed start invalidated an otherwise
successful fit. Before computing any Q=3 outcome, the contract was clarified to
require at least one successful finite start for every galaxy, grid value, scan
direction, and law, while retaining counts of every successful and failed
start. The current commitment binds that clarified contract.

## Purpose

This study challenges the already-certified SPARC quality-1/2 acceleration
profiles using the lower-quality `Q = 3` galaxies that the existing analyses
exclude. It is a prospective same-catalogue holdout validation, not a blind
discovery or an independent-survey replication. The SPARC catalogue is public
and its quality flags were available before this protocol.

No repository result or analysis of a Q=3 acceleration-scale profile was found
before freezing the contract. The official rotation-curve archive and catalogue
table are already held with exact byte counts, SHA-256 digests, source URLs,
citation, DOI, and retrieval provenance.

## Frozen primary screen

The existing Q≤2 result fixes the training intervals. The Q=3 sample is fitted
separately with the same velocity-coordinate objective, nuisance parameters,
priors, bulge treatment, error floor, acceleration grid, optimizer, and
scan-order check.

The EMRF square-root law passes this limited conditional generalization screen
only when the Q=3 grid minimum:

1. is not at either acceleration-grid boundary; and
2. lies within the closed Q≤2 conditional ΔQ=1 interval
   `[1.55781092394229e-10, 1.60831784955957e-10] m/s²`.

The McGaugh RAR exponential law is evaluated by the same rule as a comparator.
Failure rejects the corresponding generalization claim. Passing would show
only consistency under this declared penalized-profile design.

## Evidence limits

SPARC does not provide the radial covariance required for a complete
likelihood, and this study will not invent one. ΔQ=1 intervals are conditional
profile summaries, not calibrated confidence intervals. Penalized objectives
will not be inserted into BIC. Every eligible galaxy, failed target, numerical
failure, and protocol deviation must remain visible.

The authoritative JSON contract contains the complete population rules,
input hashes, training-result hash, nuisance treatment, numerical gates,
hypotheses, reporting requirements, and prohibited interpretations. Its
canonical JSON content is protected by the accompanying immutable prediction
commitment.

## Protected execution

The manually dispatched `SPARC Q3 holdout` workflow is the supported execution
path. It refuses commits other than current protected `main`, downloads and
hash-verifies the preregistered official holdings, verifies the training result
and prediction commitment, executes both laws in forward and reverse grid
order, and retains the complete or failed JSON evidence for 90 days. It has
read-only repository permissions and no schedule. Every supported execution is
bound to an exact protected commit and retains a run-specific evidence artifact;
manual reruns remain possible and must not replace or conceal earlier evidence.

A scientifically rejected hypothesis does not make the computation fail.
Workflow failure means the analysis was incomplete, an input or commitment did
not match, or a numerical gate failed. The output records the primary claim as
`consistent` or `rejected` separately from operational completeness.

## Protected outcome

Workflow run `38315325901` executed the frozen protocol from clean protected
`main` revision `f09633b6bded2b239372dd76630b1e38d92e0992`. The complete
artifact is preserved unchanged at
`results/real_data_v1/sparc_q3_holdout_v1.json` with SHA-256
`87dea72269652bea6e24d03876dfe4c65075d7254031b2852e31a09add55231a`.
Independent receipt checks confirmed the committed input, training-result and
preregistration hashes; all 10 eligible galaxies and 109 points; no missing or
silently excluded targets; no protocol deviations; and passing optimizer and
forward/reverse numerical gates for both laws.

The preregistered outcomes are:

- **H1 EMRF square-root generalization: `rejected`.** The Q=3 grid minimum is
  `1.50e-10 m/s²`. It is not on a grid edge, but it is outside the frozen Q≤2
  interval `[1.55781092394229e-10, 1.60831784955957e-10] m/s²`.
- **H2 RAR comparator generalization: `rejected`.** The Q=3 grid minimum is
  `1.15e-10 m/s²`. It is not on a grid edge, but it is outside the frozen Q≤2
  interval `[1.22152425035699e-10, 1.2557224809968e-10] m/s²`.

These outcomes reject only the declared conditional same-catalogue
lower-quality generalization screens. They are not calibrated significance,
blind discovery, or independent-survey replication.
