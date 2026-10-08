# Testing a Cosmological Acceleration Scale with SPARC
## Profile constraints and bulge-dependent systematics

**Author:** Kirk LaSalle. **Status:** research draft, requiring independent review. **Source:** [LaTeX manuscript](../paper/sparc_horizon_test.tex). **Protocol:** [real_data_v1](REAL_DATA_VALIDATION_PROTOCOL.md).

## Abstract

The numerical proximity of the galactic acceleration scale to cH₀/(2π) motivates a testable phenomenological hypothesis, not a derived theory of gravity. This study re-examines public SPARC rotation curves using explicit stellar, distance and inclination constraints, separating penalized profiling from Bayesian marginalization. A conventional reference fit, a global acceleration scale and exploratory bulge-related contrasts are examined with numerical and observational limitations exposed. Fresh numerical results are reported in the accompanying generated supplement. Poor fit quality, selection sensitivity and unknown radial covariance prevent conditional profile intervals from serving as discovery significances. A separate audit covers ten observational regimes and three horizons; imposed identities do not count as empirical validation. The outcome is a reproducible re-analysis, not a new observing campaign or proof of a compression theorem.

## 1. Motivation and prior work

The SPARC database supplies mass models for 175 nearby disk galaxies. The radial acceleration relation (RAR) associates observed rotation-derived acceleration with that expected from baryons. Cosmic connections to the acceleration scale have a substantial history, including Milgrom's vacuum-effect discussion. A cosmological numerical coincidence is therefore neither unique to EMRF nor a derivation of its dynamics.

Li et al. (2018), Rodrigues et al. (2018), and the Kroupa et al. critique and Rodrigues et al. reply illustrate why acceleration-scale universality cannot be judged without examining priors, quality cuts, distances, inclinations and statistical definitions. A bulge-dependent contrast is scientifically interesting only if it survives those concerns. This work does not certify priority over the literature.

## 2. Observations and selection

Use the official SPARC mass-model archive and galaxy metadata, preserving raw bytes and identifying their sources and checksums. Baseline selections are quality Q ≤ 2, inclination ≥ 30°, positive radius and observed velocity. The implementation records velocity-error floors and signed component conventions. Fresh artifacts, not earlier prose, determine the actual sample size.

Neither checksum matching nor a catalogue citation removes astrophysical systematics. Radial errors may be correlated; stellar masses depend on population assumptions; mass decomposition and gas measurements have uncertainties. Missing covariance is disclosed, not fabricated.

## 3. Models

Write y = g_bar/a₀ and g_model = g_bar ν(y), retaining separately:

$$\nu_{\rm RAR}=(1-e^{-\sqrt y})^{-1},\quad
\nu_{\rm sqrt}=\sqrt{1+1/y},$$
$$\nu_{\rm simple}=\tfrac12+\sqrt{\tfrac14+1/y},\quad
\nu_{\rm standard}=\sqrt{[1+\sqrt{1+4/y^2}]/2}.$$

The fixed scale is a₀,H = cH₀/(2π), with SI conversion of H₀ explicit. Planck-like and SH0ES-like choices are separate conditional comparisons, not independent resolutions of cosmology. Propagate the uncertainty attached to whichever external H₀ estimate is used. H₀ estimates themselves depend on their underlying inference assumptions.

The externally quoted references are [Planck base-ΛCDM, 67.4 ± 0.5](https://arxiv.org/abs/1807.06209), and [SH0ES Cepheid-SN, 73.04 ± 1.04](https://arxiv.org/abs/2112.04510), in km/s/Mpc. The numerical grid retains the earlier rounded SH0ES value 73.0. The fresh supplement propagates those external errors to a₀,H separately; it does not combine them into a calibrated joint SPARC significance.

Equating Unruh and de Sitter temperatures gives a = cH, because both 2π factors cancel. Thus the additional factor here remains a hypothesis. In the deep limit, under the usual asymptotic mass/geometry assumptions, V⁴ = GMa₀ follows algebraically; it is not a new EMRF theorem.

## 4. Likelihood and profiling

The signed-component baryonic acceleration is

$$g_{\rm bar}=\frac{V_g|V_g|+\Upsilon_dV_d|V_d|+\Upsilon_bV_b|V_b|}{R}.$$

With f_D = D′/D, radius and squared baryonic speed scale together; g_bar stays unchanged in the adopted prescription. The predicted circular speed is sqrt(g_model R f_D). For s = sin(i)/sin(i′), the model in the original observed-velocity coordinate is V_pred/s. Its Gaussian residual is

$$\chi^2=\sum_j\left[\frac{V_j-V_{{\rm pred},j}/s}{\sigma_j}\right]^2.$$

Transforming both observations and errors by s gives the same residual, but a probability density in transformed coordinates requires the appropriate Jacobian. One cannot insert parameter-dependent transformed normalization terms arbitrarily.

The objective Q = χ² + P includes Gaussian penalties in log₁₀Υ_d (width 0.1 dex), distance and inclination. Minimizing Q at fixed a₀ is **penalized profiling**, not integrating out nuisance parameters. The historic filename containing “marginalized” is not evidence of a marginalization calculation. Baseline Υ_b = 1.4Υ_d is an assumption relaxed only in explicitly named variants.

A ΔQ = 1 crossing is a conditional objective-profile interval. It does not automatically supply a calibrated frequentist confidence level. Failed fits, multiple minima, grid boundaries and poor goodness of fit must be visible. Rescaling errors by reduced χ² is not a replacement for understanding covariance or model discrepancy.

The rerun exposed a concrete numerical pitfall: signed gas components combined with a baryonic-acceleration floor can create distinct smooth fitting regions. UGC 07577 initially produced a scan-direction-dependent optimum. The corrected fixed-bulge solver partitions stellar mass-to-light bounds at every such transition, searches each region, and checks forward/reverse agreement. Analytic residual derivatives are tested against finite differences. This is a numerical correction, not a detection of new physics; the unsuccessful runs remain in the correction history.

## 5. Comparisons and sensitivity

Reproduce a fixed mass-to-light reference before interpreting a free-scale fit. Evaluate fixed-horizon and free-a₀ hypotheses on the same observations with the same nuisance constraints. Inspect influence of individual galaxies and sensitivity to selections and stellar priors using measured data only.

Gas/star and bulge/bulgeless contrasts are exploratory; shared galaxies can correlate estimates. The earlier lighter-bulge and free-bulge follow-ups were post hoc and stay labelled that way. Neither a later protocol nor a large contrast retroactively establishes preregistration or discovery significance.

BIC = k ln(n) − 2 ln(Lhat) requires comparable maximized **data likelihoods** and defensible k and n. A prior-penalized optimum is not automatically Lhat. Where these assumptions fail, omit BIC rather than report a spurious preference.

## 6. Fresh results

The [fresh numerical supplement](SPARC_FRESH_RESULTS.md) is generated from versioned run artifacts and accompanies the LaTeX manuscript. Historical σ values and ΔBIC values are not carried forward as verified results. Read the supplement's explicit scope, convergence diagnostics, fit quality and sensitivity limitations together with each estimate.

The new run includes **153 galaxies / 3,168 points**. The fixed-stellar RAR reference gives a₀ = **1.2216 × 10⁻¹⁰ m/s²**. The main RAR grid optima are 1.25 for the full sample, 1.00 for gas-dominated galaxies, 0.90 for star-dominated bulgeless galaxies, and 1.90 for star-dominated bulge galaxies, in the same acceleration units. These are grid estimates, not calibrated confidence statements.

A particularly important check changes the interpretation of the earlier bulge claim: removing **UGC 06787** shifts the deep-bulge optimum from **1.60 to 0.90**. A separate full-grid refit of the remaining **24 galaxies / 287 observed points** confirms the effect. This does not justify discarding UGC 06787; it shows why the deep-bulge excess cannot yet be called a robust population discovery. The primary forward/reverse objective difference after the numerical correction is approximately **4.7 × 10⁻⁹**.

## 7. Interpretation

Bulge-associated differences can reflect mass decomposition, orientation/distance errors, correlated velocities, selection, noncircular motion, a deficient interpolation law or nonuniversal dynamics. This analysis does not select one explanation uniquely. Increasing a bulge contribution can also change the preferred disk and nuisance parameters; a one-variable intuition is insufficient.

Agreement in one subset does not confirm a universal horizon relation; tension in a poorly modelled sample does not prove its physical absence. Any publishable statement must identify the assumptions under which the computation is informative.

## 8. Cross-regime and theoretical context

The [ten-regime report](REAL_DATA_REGIME_AUDIT.md) treats data and prediction gaps explicitly. A standard GR lensing calculation, an imposed luminal speed, a CPL expansion fit or copied CMB peaks are not independently derived EMRF successes.

The [compression/horizon audit](EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md) demonstrates why normalization to an input mass is not particle-mass emergence, why integrating an assumed quarter-area entropy density is not a new entropy theorem, and why a chosen collapse time is not a galaxy-population prediction. IBM Quantum remains a feasibility discussion, with no account access or quota use.

## 9. Correction history and reproducibility

Earlier project releases mislabeled synthetic observations and contained circular tests. Their empirical headlines are withdrawn. Subsequent stored SPARC numbers were also described too strongly as independent verification and marginalization. The new work distinguishes observed data, numerical checks, baseline reproduction, conditional constraints and unresolved questions.

The reproducibility package contains source manifests, commands, versioned numerical results, source hashes, tests and a limitations report. Re-analysis is not independent observing replication. AI assistance was used to prepare code and text; independent galaxy-dynamics/statistics review remains necessary before submission. No external submission or release upload has occurred.

## 10. Conclusions

A concrete contribution can consist of a transparent, reproducible test and well-characterized limitations. That is different from demonstrating a new gravitational theory. Neither favorable subsets nor software pass counts establish novelty, a compression theorem or ten-regime agreement. The next scientific decision must follow review of the fresh evidence, not a predetermined success narrative.

## References

Primary references and source links are listed in the [protocol](REAL_DATA_VALIDATION_PROTOCOL.md#primary-literature-checked-for-framing) and the [manuscript bibliography](../paper/sparc_horizon_references.bib).
