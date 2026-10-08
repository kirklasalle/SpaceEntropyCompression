# Ten-regime and three-horizon real-data evidence audit

> **Current follow-up:** the [top-down theory/toolkit audit](EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
> checks the original compression families and thermodynamics-as-output statement,
> corrects the Bullet Cluster demonstration's unsupported verdicts, and reports
> the new full-covariance Pantheon+ baseline using the manually downloaded data.

**Protocol:** [real_data_v1](REAL_DATA_VALIDATION_PROTOCOL.md). **Companion:** [SPARC paper](SPARC_HORIZON_TEST_PAPER.md). This report separates data authentication, baseline calculations and genuinely derived model tests. There is no combined “all regimes passed” score.

The [executed-results supplement](REAL_DATA_GAUNTLET_RESULTS.md) records the actual fresh run, retrieved measurement products and case statuses. It is distinct from the requirements below.

## Interpreting the gauntlet

Retrieving an authentic measurement is necessary but not sufficient. A physical test also needs a prediction, specified nuisance parameters, a likelihood or justified published constraint, and an uncertainty treatment. A software test can pass while the physical hypothesis remains unsupported. A missing prediction is not evidence of agreement; a failed optimizer is not evidence of exclusion.

The named square-root law must retain the same functional form and parameters across its comparisons. Replacing it with RAR, screening, a GR lensing prescription or a CPL cosmology defines different hypotheses. Those variants cannot jointly be advertised as one successful derivation.

## Regime-by-regime evidence requirements

| ID | Regime | What authentic data can supply | What must be predicted or fitted |
|---|---|---|---|
| R01 | Sgr A* S-stars | Published astrometry and radial velocities where measured | Shared black-hole/frame parameters and orbits; derived modification, not a fixed multiplier |
| R02 | Solar System | Tracking/precession/PPN measurements or correctly sourced limits | The corresponding observable for the same law; no arbitrary suppression |
| R03 | SPARC | Official rotation curves and mass-model metadata | Fixed/free acceleration-scale profiles and documented nuisance sensitivity |
| R04 | SLACS | Lensing geometry and stellar kinematics with uncertainties | Lensing potential plus dynamics; standard SIS agreement is baseline-only |
| R05 | Bullet Cluster | Lensing/shear, X-ray and stellar maps | Absolute mass/shear prediction, not hand-placed normalized peaks |
| R06 | High-z disks | Resolved kinematics and mass/inclination constraints | Full law with pressure support and beam effects; no invented velocities |
| R07 | GW170817 | Observed multimessenger timing/distance constraints | Derived tensor/photon propagation and emission-delay assumptions |
| R08 | Wide binaries | Identified pairs, astrometry covariance and selection | Projected orbital distribution, contamination and external-field response |
| R09 | Late expansion | Pantheon+ and DESI distances/covariance/calibration | Consistent expansion and ruler calibration; CPL fits are not EMRF dynamics |
| R10 | CMB | Planck spectra and likelihood products | Perturbation evolution and spectra, not assigned peak heights |

## Why more downloads do not guarantee ten tests

Lensing needs a metric prediction beyond a galaxy acceleration interpolation. The Bullet Cluster additionally requires a projected dynamical mass model and boundary conditions. A gravitational-wave speed prediction must follow from tensor propagation in the specified action. CMB peaks require a physical perturbation calculation. These are theory gaps, not missing CSV files.

Wide-binary population inference requires selection, projection and companion modelling; the present scope does not authorize replacing observations with simulated catalogues. A published constraint can be examined conditionally if its applicability is established, but it is not a fresh pair-level inference.

For cosmology, correlations between DESI radial/transverse BAO measurements and Pantheon+ calibration/systematic covariance matter. A diagonal-error fit or a fixed sound horizon silently imported from another cosmology cannot prove the full EMRF cosmology.

## Three additional horizons

| ID | Claim | Current evidential boundary |
|---|---|---|
| H01 | Matter from quantum compression/solitons | Input mass fixes the profile and is recovered by normalization; no independent particle-mass prediction |
| H02 | Compression derivation of black-hole entropy | Quarter-area coefficient is assumed; mass-to-area conversion is not a measurement of entropy |
| H03 | JWST cosmic dawn | Observations do not validate assumed cloud times without an assembly/population prediction |

The [detailed theory audit](EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md) supplies equations, source-code links and proof obligations. Its [executed algebra checks](../results/real_data_v1/compression_algebra.json) are explicitly non-empirical.

## Novelty and significance

The cosmological acceleration-scale connection and debates about universal a₀ predate this project. A new analysis can still be valuable, but priority requires a literature comparison and robustness requires independent methodological scrutiny. The historical bulge contrast is an exploratory lead, not a certified discovery. New numerical agreement alone is not independent observing replication.

## Reproducibility and disposition

Use the [reproducibility guide](REAL_DATA_REPRODUCIBILITY.md) and the generated numerical/evidence supplements to identify actual retrieved products, hashes, executed comparisons and blocked cases. All limitations remain attached to the results. No external submission or IBM Quantum computation is part of this audit.
