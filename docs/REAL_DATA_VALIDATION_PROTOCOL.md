# Real-observation validation protocol

**Owner:** Kirk LaSalle. **Protocol:** real_data_v1, 2026-10-08. **Status:** prospective rerun protocol, not preregistration of discoveries already examined. Historical exploratory analyses and post-hoc bulge changes remain exploratory.

## Scope and interpretation

This protocol governs a full SPARC paper and a separate ten-regime/three-horizon evidence report. Numerical evaluation of physical predictions is permitted; simulated observations cannot stand in for measured data. Synthetic software fixtures remain outside the empirical evidence chain. No minimum number of successful physical tests is required. Missing data, missing predictions and computational failures must remain visible.

EMRF is a research framework with a compression ansatz, not a certified theorem. BIC is a statistic, not a physical regime. Alternative interpolation functions are separately named hypotheses; switching functions or screening laws across regimes cannot count as validation of one common theory.

## Frozen questions

1. Under the stated SPARC selections and nuisance constraints, what acceleration scale is preferred by each tested law?
2. How does the fixed hypothesis a₀ = cH₀/(2π) compare with a free scale using the **same** data and nuisance treatment?
3. How sensitive are the results to stellar mass assumptions, bulge presence, selection and individual galaxies?
4. Which other regimes admit a real, non-circular prediction from the specified model? What do their authentic measurements constrain?
5. Which compression and horizon statements follow mathematically from explicit assumptions, and which remain assumptions?

No discovery threshold is chosen after viewing the new fits. Exploratory contrasts are reported as such, without converting a large residual contrast into proof of new physics.

## Data contract

Each ingested dataset must identify the originating collaboration/catalogue, release, DOI or source URL, exact table/object IDs, units, errors and available covariance. Keep original bytes and record SHA-256, retrieval time and the transformation/selection chain. A matching hash establishes byte identity, not truth; source authenticity and interpretation must also be checked. A citation alone or an absent synthetic marker is insufficient.

Cached inputs must be verified. Unavailable covariance is a limitation, never license to invent one. Official published parameter constraints can support conditional comparisons, but must not be presented as fresh raw-observation fits. Publication metadata/abstracts are sources, not measurement tables. No private uploads, IBM account access, publication or researcher contact occurs under this protocol.

## SPARC model and statistical contract

Let y = g_bar/a₀ and g_model = g_bar ν(y). Retain separately:

- Earlier EMRF phenomenology: ν(y) = sqrt(1 + 1/y).
- McGaugh RAR: ν(y) = 1/[1 − exp(−sqrt(y))].
- MOND simple: ν(y) = 1/2 + sqrt(1/4 + 1/y).
- MOND standard: ν(y) = sqrt([1 + sqrt(1 + 4/y²)]/2).

The horizon relation is an externally specified hypothesis, not derived by equating Unruh and de Sitter temperatures (their 2π factors cancel). Keep Planck/SH0ES choices and uncertainty assumptions visible. Do not regard cosmology-dependent H₀ estimates as theory-independent measurements.

Baseline selections reproduce the existing Q ≤ 2, inclination ≥ 30°, positive radius/velocity SPARC analysis before any changed cuts are interpreted. Record velocity-error floors, signed baryonic component conventions, per-galaxy counts and exclusions. A changed implementation must retain a historical-result comparison without overwriting it.

Write the Gaussian likelihood in the original observed velocity coordinates; parameter-dependent transformations must preserve its normalization. Distinguish data χ², nuisance-constraint penalties and their sum Q. Optimizing Q over nuisance parameters is **penalized profiling**, not Bayesian marginalization. Label ΔQ intervals as conditional objective-profile intervals unless justified likelihood calibration exists. Inspect failed minimizations, multiple starts, scan order, boundaries and inadequate fit quality. Do not conceal missing interval crossings with a symmetric error bar.

A reduced-χ² scaling is not a substitute for a physical covariance/discrepancy model. Correlated radial measurements, catalogue systematics, selection and shared galaxies complicate significance. Use observed-data influence and sensitivity analyses; no synthetic galaxy catalogues are authorized. The bulge finding is exploratory, including the lighter-bulge and free-bulge post-hoc choices already recorded in the code.

For justified comparisons only:

$$\mathrm{BIC}=k\ln n-2\ln\widehat L.$$

Use the maximized **data likelihood**, common observations and a defensible parameter/sample count. Never insert a MAP/prior-penalized objective into BIC. If these conditions are not met, report BIC unavailable rather than manufacture a ranking. ΔBIC does not by itself prove a new theory or establish novelty.

## Case registry

| ID | Case | Observable and gate |
|---|---|---|
| R01 | Sgr A* S-stars | Astrometry/RV and orbital residuals; authentic time series and a defined deviation are required |
| R02 | Solar System | Ranging, precession or PPN constraints matched to the predicted observable; no ad-hoc screening |
| R03 | SPARC | Rotation curves, fixed versus free a₀, nuisance and sample sensitivity |
| R04 | SLACS | Einstein radii plus stellar dynamics; GR SIS baseline is not an EMRF prediction |
| R05 | Bullet Cluster | Absolute shear/convergence and mass distributions; not imposed offset maxima |
| R06 | High-z disk kinematics | Resolved dynamics with mass, inclination and pressure/beam uncertainties |
| R07 | GW170817 | Propagation constraint with emission-delay assumptions; derive tensor/photon speeds first |
| R08 | Gaia wide binaries | Pair-level projected dynamics and selection; unresolved companions and external field cannot be ignored |
| R09 | Late expansion | Pantheon+ and DESI distances with covariance/calibration; CPL is not derived EMRF cosmology |
| R10 | CMB | Spectrum/likelihood from physical perturbation predictions, not copied peak amplitudes |
| H01 | Quantum matter | Independent mass prediction, field-equation residual and stability; input-mass recovery is circular |
| H02 | Black-hole entropy | Derivation of coefficient/microstates; mass-derived area is not measured horizon entropy |
| H03 | Cosmic dawn | Authentic redshift/photometry/population observations and assembly predictions; collapse time alone is insufficient |

Equivalence-principle and ghost/stability arguments are auxiliary theoretical requirements, not additional observational regimes. [Compression/horizon audit](EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md) records their proof obligations.

## Evidence grades and completion

Every case records source, equation, assumptions, computation, outcome and limitations. Grades distinguish software validation, baseline reproduction, conditional constraint, model comparison, missing observations, missing prediction and computational failure. A blocked case is a completed audit entry, **not a passed physical test**. There is no all-regimes-passed score.

Results must retain commands, runtime/dependency versions, code revision/source hashes, input hashes, fit diagnostics and generated tables. Publication text is written from fresh results only; historical numbers are clearly labelled and cannot silently become new evidence. Independent domain-expert review remains necessary.

## Primary literature checked for framing

- Lelli, McGaugh & Schombert (2016), *SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves*, [arXiv:1606.09251](https://arxiv.org/abs/1606.09251).
- McGaugh, Lelli & Schombert (2016), *The Radial Acceleration Relation in Rotationally Supported Galaxies*, [arXiv:1609.05917](https://arxiv.org/abs/1609.05917).
- Li, Lelli, McGaugh & Schombert (2018), *Fitting the radial acceleration relation to individual SPARC galaxies*, [arXiv:1803.00022](https://arxiv.org/abs/1803.00022). This work is context, not evidence that the repository implements its complete inference procedure.
- Rodrigues et al. (2018), *Absence of a fundamental acceleration scale in galaxies*, [arXiv:1806.06803](https://arxiv.org/abs/1806.06803). This establishes prior investigation of nonuniversality, not an adopted settled conclusion. Its arXiv text explicitly differs from the published version; review that distinction before submission.
- Milgrom (1999), *The Modified Dynamics as a Vacuum Effect*, [arXiv:astro-ph/9805346](https://arxiv.org/abs/astro-ph/9805346). Cosmological acceleration-scale connections predate EMRF; exact coefficients and mechanisms must not be conflated.

- Kroupa et al., *A common Milgromian acceleration scale in nature*, [arXiv:1811.11754](https://arxiv.org/abs/1811.11754), argues that distance/orientation uncertainties and quality selections affect the nonuniversality claim. Rodrigues et al.'s [reply, arXiv:1811.05882](https://arxiv.org/abs/1811.05882), disputes the inference and prior criticisms. These competing interpretations are material to the present bulge/selection analysis.

This is not an exhaustive novelty certification. A bulge-dependent signal in a re-analysis may be worth reporting, but neither priority nor robustness is established by these citations alone.
