# SPARC quality-3 holdout preregistration

**Study:** `sparc-q3-holdout-v1`  
**Status:** preregistered before computing the Q=3 profiles  
**Authoritative contract:** `research/preregistrations/sparc_q3_holdout_v1.json`  
**Commitment:** `20261012T205817322791Z-806cce833d62`  
**Canonical JSON SHA-256:** `806cce833d62fa2349c5b19a0638e62991e33ed19f05cd65b15de147352fbbb0`

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
