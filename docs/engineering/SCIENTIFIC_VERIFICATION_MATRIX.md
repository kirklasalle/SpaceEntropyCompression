# EMRF Scientific Verification Matrix

**Status date:** 2026-10-10
**Scope:** Phase 5 verification foundation
**Interpretation:** A passing software check demonstrates recovery of a known
limit. It does not confirm EMRF as a physical theory.

## Certified foundational limits

Run the machine-readable certificate with:

```text
emrf verify physics --json
GET /api/v1/verification/physics
```

| Domain | Boundary or engine | Independent reference | Current check | Status |
|---|---|---|---|---|
| Constants | `emrf.physics.constants` | NIST CODATA 2022 | Explicit value, uncertainty, exactness and source metadata for `G`, `c`, `h`, and `k_B` | Passing |
| Units | `emrf.physics.verification` | Astropy units | Bare, incompatible, non-finite and non-positive physical quantities fail closed | Passing |
| Newtonian mechanics | `physics_baseline.keplerian_orbit_2d` | Kepler equation and vis-viva relation | Period, apsides and specific orbital energy relation | Passing |
| Numerical integration | `physics_baseline.integrate_orbit_1pn` | RK4 theoretical order | Step halving over a bounded orbit recovers order greater than 3.9 | Passing |
| Schwarzschild radius | Unit-aware reference boundary | `r_s = 2GM/c^2` | Solar value 2.95325 km | Passing |
| PPN light bending | Unit-aware reference boundary | First-order PPN with `gamma=1` | Solar-limb deflection 1.7512 arcsec | Passing |
| Schwarzschild precession | `physics_baseline` | Analytical 1PN precession | S2 known limit and 1PN trajectory checks | Passing |
| Curvature | `physics_baseline.kretschmann_invariant` | Exact Schwarzschild invariant | Exact inverse-sixth-power radial scaling | Passing |
| Cosmology | `cosmology_expansion` | Astropy 6.1 `FlatLambdaCDM` | Luminosity distances at five redshifts from 0.01 through 2.0 | Passing |
| Black-hole thermodynamics | `black_hole_horizon_entropy` | Bekenstein-Hawking area law | Absolute solar-mass value, legacy-engine agreement and mass-squared scaling | Passing |

All checks above are classified as `software` evidence. The sources and
tolerances are returned with each CLI/API result.

## Engine-level status and remaining work

| Engine or analysis family | Existing evidence | Phase 5 status | Required next verification |
|---|---|---|---|
| Core `EmergentMatterModel` | Unit and property tests for shape, monotonicity and scaling | Partially verified | Define physically meaningful dimensional boundaries and conservation laws |
| Schwarzschild comparison | Golden output plus exact curvature scaling | Verified foundation | Add independent symbolic/high-precision cross-checks |
| Lensing engine | Regression and stress tests | Pending known-limit certification | Point-mass bending and ray-step convergence against the PPN reference |
| Cosmological expansion | Golden results and Astropy flat-LCDM comparison | Verified foundation | Add radiation and non-flat limits; optional CAMB/CLASS cross-code matrix |
| CMB acoustic engine | Regression/stress behavior | Pending | Cross-code peak locations against CAMB or CLASS |
| Black-hole entropy | Area-law equality and benchmark suite | Verified foundation | Propagate constant uncertainty and document numerical dynamic range |
| Astrometry engine | Synthetic recovery tests | Partially verified | Calibrated injection-recovery coverage and repeated-start agreement |
| SPARC analyses | Eight-pipeline golden harness, profile and influence checks | Partially verified | SBC, calibrated intervals, deterministic repeated starts and reduced golden tolerance |
| Pantheon+ covariance fit | Full-covariance golden pipeline | Partially verified | Injection-recovery, coverage, posterior predictive checks and evidence calculation |
| JWST engine | Regression and domain checks | Pending | Synthetic signal recovery and nuisance-parameter calibration |
| Quantum vibrational compression | Demonstration calculations | Pending | Units, independent oscillator limits and evidence classification |
| Stress-test scripts and figure generators | Golden/regression outputs where applicable | Software-only | Keep separate from observational confirmation; remove legacy verdict semantics |

## Preservation and failure policy

1. Known-limit tests are additive and must not rewrite reviewed scientific
   evidence.
2. Non-finite values, incompatible units and unconverged algorithms raise
   typed errors rather than publishing a result.
3. Reference comparisons use measurable tolerances stated in tests and in the
   CLI/API certificate.
4. A proposed correction to a golden scientific number requires a documented
   scientific review; tests are never weakened merely to accept drift.
