# Candidate A option 3: segmented quadrature experiment

**Status:** the first run reported here was exploratory and model-only. Kirk
subsequently approved amendment 1, and a hash-verified rerun under that
amendment is now complete. This report does not modify the frozen v1
reconstruction specification or protocol.
It supplements the [reconstruction specification](EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md)
and [frozen protocol](../knowledgebase/candidate_a_option3_reconstruction_protocol.json)
without changing either.

## Method

The experimental radial integration applies an order-\(n\) Gauss-Legendre rule
independently on each finite source interval. Intervals split at zero, aligned
profile-ring centres, each field radius inside the source support, and the
frozen outer cutoff. The vertical half-line retains the frozen rational map
with order-\(n\) Gauss-Legendre nodes. The comparison uses \(n=64\) and \(n=128\)
on every radial panel and in the vertical integral.

This changes only the numerical quadrature used to evaluate the primary
reconstructed sources. It does not change the source profiles, envelopes,
parameter grid, data, statistic, or the frozen protocol. The GPU path computes
elliptic kernels on CPU with SciPy and evaluates densities and weighted
reductions on the GPU in float64.

## Results

The pre-approval
[artifact](../results/candidate_a_option3_segmented_experiment_2026-11-04_r2.json)
contains 180 galaxy/envelope/parameter cases. The experimental V3 maximum
relative order-64/128 discrepancy is `2.790382718485572e-4`, below the
`0.005` threshold. The artifact labels this
`candidate_passed_not_authorized`; it is not a pass of frozen-v1 V3.
Experimental V3b CPU/GPU agreement is `1.93162313531924e-15`, below `1e-10`.
Both checks cover primary sources only and all positive-radius rows inside
their density coverage, not the unevaluated velocity-dependent fit subset.

The primary projection error is `2.746430965098234e-9` against `1e-3`, and
primary-scope V2 passes. Full V1 remains incomplete because required
sensitivity variants have not been validated. V4 and V5 were not run.
Accordingly, the artifact outcome is incomplete and `fit_permitted` is false.
No observed velocities were parsed and no observational fit was performed.

## Validation under approved amendment 1

The
[amended validation artifact](../results/candidate_a_option3_segmented_amendment_1_validation_2026-11-04.json)
repeats all 180 cases under the separately versioned protocol. V3 passes at
`2.790382718485572e-4` versus `< 0.005`; V3b passes at
`1.93162313531924e-15` versus `< 1e-10`. Primary V1 projection error is
`2.746430965098234e-9` versus `< 1e-3`, and primary-scope V2 passes. In that
primary-only run, full V1 remained incomplete because the sensitivity variants
were not validated; V4/V5 were not run. The amended artifact remains
`outcome: incomplete` with
`fit_permitted: false`.

The amended run measured 881.21 s for CPU V3 and 869.24 s for GPU V3b,
including GPU first use and transfers; total elapsed time was 1844.35 s. These
are validation timings, not an optimizer benchmark or a fit-duration estimate.
The CuPy pool had a 1 GiB process limit; peak device memory was not measured.
The amended artifact's `created_utc` is `2026-11-05T09:07:13.354170+00:00`.

## Provenance and change control

The pre-approval artifact records frozen-v1 SHA-256
`CD9687DDAC497025E709FCCC0C6BAF3D40AE5BCE92166B8C23FEFEEC16270518`.
The amended artifact records amendment 1 SHA-256
`D71702204520526730B78F2DF0298DB272CD1B210572F83E5A6D02AAC2898C3C` and
the frozen-v1 value above as its parent-protocol hash.
The pre-approval run records five code-source hashes. The amended artifact
records those five plus the amendment JSON; all six hashes match the files
used for the rerun, including the segmented quadrature module. Pre-approval
artifact SHA-256:
`3479F9981E7799F9BDA872822380902061A009FE96FFE5300554EDC004B1DA78`.
Amended artifact SHA-256:
`A3D8885CE741B2C7EE15CEAC177EE34C998CD7277525ED66ED6EB05B7A125285`.

The earlier
[`candidate_a_option3_segmented_experiment_2026-11-04.json`](../results/candidate_a_option3_segmented_experiment_2026-11-04.json)
is retained but superseded: its provenance omitted the quadrature module and
its recorded GPU and validator hashes did not match the final source files.
The amended validation artifact is the reproducibility record for prospective
use of the approved method.

The segmented method is not part of frozen v1. Kirk approved the separately
versioned
[amendment](../knowledgebase/candidate_a_option3_reconstruction_protocol_v1_amendment_1_segmented_quadrature.json)
with SHA-256
`D71702204520526730B78F2DF0298DB272CD1B210572F83E5A6D02AAC2898C3C` for
further model-only validation. The amended artifact records the new protocol
hash and matching source hashes. At this report's initial publication, the V1 sensitivity work and V4/V5 gates
remained incomplete. Their later model-only results and blockers are recorded
in the [reconstruction specification update](EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md#12-amendment-1-sensitivity-validation-update-2026-11-05)
and the [GPU runbook](site/development/gpu-compute.md#sensitivity-validation-checkpoint-2026-11-05).
No candidate verdict follows from this numerical experiment.

## Full sensitivity validation under amendment 1 (2026-11-05)

The later full run is preserved as
[`candidate_a_option3_sensitivity_validation_2026-11-04.json`](../results/candidate_a_option3_sensitivity_validation_2026-11-04.json),
SHA-256 `b3d502f5b9be54260979e990b82a6dc398a4bc2b1800370eb4a99b4cf3be4654`.
It reports V3 pass (`2.790382718485572e-4`), V3b pass
(`2.076880311640573e-15`), V2 pass and V4 model-only results for 20 cases.
V1 remains incomplete: the outer-exponential-tail sensitivity could not be
constructed for 11 of 20 galaxy/envelope sources because a terminal component
has a nonnegative log-slope and therefore no finite-mass infinite tail. The
maximum reported projection error among constructed cases is `6.1755e-4`
against `< 1e-3`. The initial SciPy warnings in the spherical projection
calculation were subsequently resolved by the independent closed-form
recheck recorded below.

V5 is incomplete: 10/12 variants produced all 180 fixed-grid cases. Eleven
outer-tail source pairs were unavailable, and the spherical-inner-bulge
variant failed density validation for eight galaxies
(IC 2574, NGC 2403, NGC 2841, NGC 2976, NGC 3198, NGC 3521, NGC 5055 and
NGC 6946), leaving 36/180 cases. Negative deprojected densities were not
clipped. The run took `5893.1996` seconds, a validation timing rather than a
fit estimate. No observed velocities were parsed; no fit or candidate verdict
was produced. The frozen protocol and amendment remain unchanged.

The [projection recheck artifact](../results/candidate_a_option3_projection_recheck_2026-11-05_r2.json)
has SHA-256 `951448be4cb1dd819f0c4f072f87f997433e30cbb577fe4364ad59c3ee6f2d41`.
