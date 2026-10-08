# Executed gauntlet results

> **Follow-up using Kirk's manual downloads:** the full Pantheon+ covariance has
> now been authenticated and fitted in an explicitly non-EMRF baseline:
> 1,590 selected rows, Omega_m = 0.33158, chi-square = 1402.919 for 1588 nominal
> degrees of freedom. The table below records the earlier run, not the updated
> baseline scope. See the [current top-down audit](EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
> and [new result artifact](../results/real_data_followup/pantheon_baseline.json).

| Case | Status | Source retrieval | Remaining blocker |
|---|---|---|---|
| R01 Sgr A* S-stars | not_yet_testable | retrieved | Astrometric/RV time-series ingestion and a derived EMRF orbital deviation are absent. |
| R02 Solar System | not_yet_testable | retrieved | Cassini external-field quadrupole constraint is not a direct constant-acceleration bound; no matching ephemeris likelihood. |
| R03 SPARC | conditional_model_comparison | retrieved | Conditional profiles do not calibrate discovery significance; unknown radial covariance remains. |
| R04 SLACS lensing | not_yet_testable | retrieved | No derived EMRF lensing potential and joint stellar-dynamical likelihood. |
| R05 Bullet Cluster | not_yet_testable | retrieved | No absolute EMRF shear/convergence prediction or calibrated aligned-map likelihood. |
| R06 High-z disk kinematics | not_yet_testable | retrieved | No frozen resolved-disk sample with pressure/beam/inclination likelihood; no new fit claimed. |
| R07 GW170817 propagation | not_yet_testable | retrieved | No EMRF-derived tensor/photon propagation; imposed luminal speed is not evidence. |
| R08 Gaia wide binaries | not_yet_testable | retrieved | Pair-level contamination, projection and external-field likelihood not implemented; no synthetic forward-model fallback. |
| R09 Late expansion | not_yet_testable | retrieved | Authentic SN measurements do not supply EMRF expansion dynamics; full covariance/calibration fit not performed. |
| R10 CMB | not_yet_testable | retrieved | No EMRF perturbation spectrum; downloading spectra cannot fix copied-peak circularity. |
| H01 Quantum matter | not_yet_testable | retrieved | Input mass is normalized back into the answer; no independent mass prediction. |
| H02 Black-hole entropy | not_yet_testable | failed | Quarter-area coefficient assumed, not independently derived; no direct horizon-entropy data. |
| H03 JWST cosmic dawn | not_yet_testable | retrieved | No assembly/population prediction; observed redshifts do not validate a chosen collapse time. |

Source/abstract retrieval is not ingestion of a measurement table.

- Authenticated SPARC: 153 galaxies and 3168 selected points.
- Official Pantheon+ table: 1701 measurement rows; zHD 0.00122–2.26137; no covariance likelihood fitted.
- Local DESI table matches the retrieved means to two-decimal rounding: True; maximum absolute difference 0.004871.
- Version-pinned DESI likelihood distribution: 12 means and [12, 12] positive-definite covariance; no EMRF cosmological likelihood fitted.
- Actual flat-ΛCDM BAO baseline using the full covariance: Ωm = 0.29389, c/(H₀ rd) = 29.4097, χ² = 12.7405 for 10 nominal degrees of freedom. This is a baseline fit, not an EMRF prediction or success.
- Solar high-acceleration correction is evaluated algebraically only; no mismatched Cassini bound is used to claim exclusion.
- H02 source retrieval failed: HTTP Error 403: Forbidden. The source was not treated as successfully retrieved.

See [artifact](../results/real_data_v1/gauntlet.json) for URLs, hashes and errors.
