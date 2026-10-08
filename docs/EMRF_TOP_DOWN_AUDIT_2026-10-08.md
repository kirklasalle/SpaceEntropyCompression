# EMRF: theory-to-software-to-observation audit

> **Candidate A definition comparison:** the
> [new mathematical assessment](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
> distinguishes local observer energy, vacuum tidal curvature and regional
> mass. It derives the conditional alpha=1 normalization for an Einstein-tensor
> projection and checks counterexamples to a universal Ricci/sqrt(K) local-density
> interpretation. No new energy channel or full equivalence proof follows.

> **Author decision (2026-10-08):** Kirk selected Candidate A: C as a
> geometry/energy re-description, without the proposed additional exchange
> channel. Candidate B is retained as an unselected proposal. The precise
> definition of C and its relationship to the matter mapping remain open;
> this decision does not establish mathematical equivalence or physics validation.

> **Candidate review packet:** the
> [collision candidate specification](EMRF_COLLISION_CANDIDATE_SPECIFICATION.md)
> now separates a standard-physics re-description from a newly proposed local
> energy-exchange ansatz. The latter has a conditional energy/thermal-entropy
> identity, but no closed geometry-to-drive relation, field momentum or unique
> observable prediction. It is **not approved or implemented**. This narrows the
> mathematical question without changing any previous empirical result or
> promoting the collision illustration to a physical test.

> **Subsequent archive recovery:** the [Antigravity recovery audit](ANTIGRAVITY_RECOVERY_AUDIT.md)
> recovered a September formulation that explicitly distinguishes downstream
> macroscopic thermodynamics from a possible entropy/information input to a
> deeper geometric state. Therefore, not every entropy-input formulation
> necessarily contradicts the original intention. The static collision code
> still does not implement a coupled dynamical or entropy-production mechanism.
> The recovered distinction is now in the active knowledge graph.

**Prepared for:** Kirk LaSalle. **Scope:** follow-up after manual real-data downloads.
**Status:** critical research assessment, not independent peer review or theorem certification.

## 1. What is being assessed

The question is not whether the word "compression" is appropriate. The earlier
[mathematical treatment](EMRF_Comprehensive_Research_Audit_and_Paper_Draft.md#35-the-nature-of-compression-gravitational-geometry-energy-and-entropy-formulations)
already distinguishes:

| Family | Stated mathematical meaning | What still distinguishes a model from a family |
|---|---|---|
| C_G | Functional of spacetime geometry, e.g. curvature invariants or congruence expansion | Select the invariant, normalization, domain and field-to-observable mapping |
| C_E | Functional of an appropriate quasi-local/asymptotic gravitational-energy measure | Select the measure, boundary, reference convention and coupling |
| C_S | Entropy/information coupled to geometry | Specify which entropy and derive or explicitly postulate its coupling |
| C_GSE | Composite of geometry, energy and entropy | Specify the function and independently constrain its parameters |

These are meaningful mathematical starting points. They are not all one
implemented physical model. A failure of one interpolation law does not falsify
all four families. Equally, agreement of a known GR calculation does not prove
that any selected family has been derived from the EMRF action.

The [original discussion](GPT%20Discussion%20-%20the%20start%20of%20it%20all.txt)
records Kirk's statement that thermodynamics and entropy are an **expression
and effect** of the theory. That position is preserved here. An automated question
seeking the missing causal step received no answer because Kirk was unavailable;
this audit does not fill the gap by inventing his intended mechanism.

## 2. The central mathematical chain

The stated relationship is

$$M(X,t)=k[C(X,t)/C_0]^\alpha.$$

It is an explicit mapping once C, k, C0 and alpha are defined. It does not alone
determine C or its evolution. Questions that require equations, not terminology:

1. Does M mean mass density or total mass? The units of k and the integration
   prescription depend on this distinction.
2. What fixes C independently of the observed mass being predicted?
3. Which of the four C families is implemented in the particular test?
4. Which parameters are fitted, measured externally or universal?
5. What produces motion, light deflection and entropy generation from C?

There is a normalization degeneracy: for fixed alpha and dimensional C, the
mapping depends on k/C0^alpha, not independently on both k and C0. A mass fit
alone cannot identify the two unless an independent convention or constraint
fixes one. If C is itself inferred from the mass being "predicted", the test can
be circular.

The generic [model implementation](../emergent_matter_model/model.py) evaluates
a weighted sum of user-supplied functions and applies the power law. This is a
useful exploration engine. It does not evolve an entropy current or solve a
gravitational field boundary-value problem.

The specific galaxy law g = sqrt(g_N^2 + a0 g_N) and the RAR function are
separately assumed phenomenological laws. Their fits test those laws and their
nuisance assumptions. They do not automatically test every possible C functional.

### Theorem, physical model and data test are different obligations

- A theorem requires an explicit proposition and proof from specified hypotheses.
- A physical model requires dynamics, units, boundary/initial conditions and an
  observable mapping.
- An empirical test compares independently computed predictions with appropriate
  measurements, including errors and selection.

The records do not currently complete all three steps. That is not equivalent
to proving that no consistent completion exists.

## 3. Thermodynamics as an output: the substantive open question

There are two different claims:

**A. A compression/gravity model explains particular heating, cooling or entropy
production.** This requires a dynamical energy/entropy budget for a specified
system, with dissipative processes and boundary fluxes.

**B. The thermodynamic laws themselves emerge from the proposed deeper
description.** This additionally requires a statistical/coarse-graining
description or another explicit derivation of temperature, entropy, conservation
and the circumstances of the second law. A hot collision alone cannot prove B.

As consistency requirements, not newly derived EMRF equations, an isolated
system should conserve the appropriate total energy and obey a defensible
entropy balance such as

$$\partial_t s+\nabla\cdot\mathbf J_s=\sigma,\qquad \sigma\geq0.$$

In a relativistic formulation the appropriate current and covariant equations
must be specified. This balance is not a substitute for deriving sigma from the
proposed microphysics. Reversible adiabatic compression can heat material without
entropy production; shocks and other irreversible processes are different.
The earlier use of Delta S = Delta Q/T as a general collision law was too broad:
the familiar equality involves reversible heat transfer and, in general, an
integral rather than an arbitrary finite ratio.

Gravity can convert gravitational/bulk-motion energy into thermal energy through
known processes. Explaining that conversion is not automatically a new
thermodynamic law. Conversely, demonstrating a new mechanism requires a
discriminating prediction, not merely reproducing a familiar temperature pattern.

## 4. The collision example: user intention versus implementation

The relevant repository example is the **Bullet Cluster, a collision of galaxy
clusters**, not just two individual galaxies. Its X-ray component is hot plasma;
"dust", stellar material and plasma cannot be used interchangeably in the
likelihood. A moving lensing mass distribution is also not measured by merely
drawing a gravitational well.

The historical [Bullet Cluster note](../knowledgebase/bullet_cluster_entropy_separation.md)
and [implementation](../emergent_matter_model/bullet_cluster_stress_test.py)
use a static illustration:

1. Assign Gaussian gas and stellar shapes at predetermined positions.
2. Assign a Gaussian entropy field.
3. Apply an assumed suppression

$$C_{\rm proxy}=\frac{\Sigma_\star}{1+0.2\beta}
 +\frac{\Sigma_{\rm gas}}{(1+\beta S_{\rm gas})^{2.2}}.$$

4. Plot sqrt(C_proxy) normalized to its maximum.

This does **not** integrate moving gravitational wells, evolve a collision,
derive entropy from C, or predict absolute lensing convergence. It uses entropy
as an input. Feedback between entropy and C is conceivable, but would need
coupled equations; it is not implemented by these static arrays.

The code's exponent is 2.2; earlier explanatory prose used 2. Neither value is
derived here. The current correction documents 2.2 to match the unchanged
illustration. It does not select a new physical law on Kirk's behalf.

### Software correction made in this follow-up

Previously the function returned fixed "PASSED"/"FALSIFIED" strings and used a
100-kpc offset threshold as "matches_observation", without a measured-map
likelihood or uncertainty. Those claims have been removed from the executable
report. It now returns:

- evidence type `synthetic_static_illustration`;
- `observations_ingested = false`;
- `entropy_is_an_input = true`;
- `entropy_production_computed = false`;
- `matches_observation = null`;
- status `NOT TESTED`.

The numerical maps and offsets remain unchanged. A separately named illustrative
threshold preserves the old numerical diagnostic without calling it a physical
test. The related plot is labelled synthetic and non-empirical. Historical
rendered figures and release archives are not silently overwritten.

## 5. Critical toolkit findings

| Finding | Evidence | Consequence / disposition |
|---|---|---|
| Unconditional physical pass/failure labels | Bullet Cluster returned fixed status strings | Corrected here; tests now prohibit empirical claims from the static illustration |
| Documentation/code exponent mismatch | Bullet prose 2, implementation 2.2 | Executable documentation corrected; historical prose explicitly marked |
| Loss of absolute prediction | Bullet maps divide by their own maxima | Remains illustrative; no absolute mass/shear claim |
| Entropy supplied instead of generated | Bullet entropy arrays, generic weighted entropy term | Implementation does not test the stated thermodynamics-as-output mechanism |
| Template tests can still look like empirical success | CMB wrapper returns `PASSED` from synthetic/template peak tolerances; GW/EP modules impose their standard values | Legacy modules remain demonstration-only and excluded from empirical evidence; not all legacy interfaces were rewritten in this follow-up |
| Particle-mass and entropy identities | Input-mass normalization and assumed black-hole quarter coefficient | Algebra checks, not independent predictions; detailed in the existing horizon audit |
| Optimizer direction dependence | UGC07577 signed-gas floor creates distinct fitting regions | Previously fixed by explicit branch searches; initial failed results preserved |
| Software-test pass count is overinterpreted | Legacy tests include known-answer synthetic fixtures | Test-suite success verifies implementation only, not the full theory |
| Physical/statistical constraints not interchangeable | Cassini quadrupole versus constant radial acceleration; penalized profile versus BIC | No generic "Cassini pass" or unsupported galaxy BIC ranking |
| Earlier theoretical audit overstates a GR argument | Locally setting connection coefficients to zero does not set tidal curvature to zero | Its energy-localization discussion is not a complete proof; local freely falling coordinates do not remove all gravity |

This is a scientific-correctness audit of the theory-to-observable chain and
the identified toolkit surfaces, not an exhaustive security review or a proof
that every unrelated API/visualizer module is bug-free.

## 6. Manual data: verified and now actually used

The manually downloaded SPARC archive/table, DESI means/covariance and Pantheon+
measurement table match the previously verified bytes. Original files were
preserved, including browser-added `.txt` suffixes.

The new Pantheon+ STAT+SYS covariance was independently downloaded from the
same pinned collaboration release and matched byte-for-byte:

- 1,701 by 1,701 elements; all finite, positive diagonal.
- Maximum asymmetry 3e-8, attributable here only to a small serialized numerical
  discrepancy, not assumed physical covariance. The reader explicitly permits
  at most 5e-8, records the measured asymmetry and uses (C+C.T)/2.
- Larger asymmetry, mismatched dimensions, non-finite values or a failed
  Cholesky decomposition raise errors rather than silently replacing covariance.
- No diagonal-error approximation or duplicate-row dropping is used.

The source collaboration's [README](https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/c447f0fea703fcd0fff57de5000947b5ca81286b/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/README)
and [SN-only likelihood](https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/c447f0fea703fcd0fff57de5000947b5ca81286b/Pantheon%2B_Data/5_COSMOLOGY/cosmosis_likelihoods/Pantheon%2B_only_cosmosis_likelihood.py)
specify corrected magnitudes, zHD > 0.01 selection, the selected full covariance
and the heliocentric redshift factor. Those semantics were checked before fitting.

### Executed supernova baseline

For a flat-LCDM comparison (not an EMRF prediction):

$$E(z)=\sqrt{\Omega_m(1+z)^3+1-\Omega_m},$$
$$m_{\rm model}=5\log_{10}\left[(1+z_{\rm HEL})
\int_0^{z_{\rm HD}}\frac{dz}{E(z)}\right]+\mathcal M.$$

The magnitude offset Mcal combines the unknown absolute SN magnitude and the
distance normalization. It is analytically profiled with the full covariance:

$$\widehat{\mathcal M}=
\frac{\mathbf1^T C^{-1}(m-f)}{\mathbf1^T C^{-1}\mathbf1},\qquad
\chi^2=(m-f-\widehat{\mathcal M}\mathbf1)^T
C^{-1}(m-f-\widehat{\mathcal M}\mathbf1).$$

Triangular solves are used instead of constructing the inverse. The code uses
64-point quadrature and verifies the best-fit objective with 128 points.

Fresh result: **1,590 selected measurement rows, 1,473 distinct CID values**;
Omega_m = **0.33158**, conditional Delta-chi-square=1 interval
**[0.31361, 0.35000]**; chi-square **1402.919** for **1588** nominal degrees of
freedom. The quadrature cross-check changes chi-square by approximately 1.14e-12.

This demonstrates that the real data and covariance can be used consistently
in a baseline. It **does not infer H0**, validate an entropy mechanism, or confirm
the EMRF expansion model. The public covariance is held fixed; photometry,
calibration and selection were not re-derived.

Reproduce:

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\fit_pantheon_real_covariance.py
```

The [result artifact](../results/real_data_followup/pantheon_baseline.json)
contains source URLs/hashes, exact selected row indices, conventions and output.

## 7. Where the evidence stands across all requested cases

| Case | What works / was actually checked | What blocks an EMRF conclusion | Is more data alone enough? |
|---|---|---|---|
| S-stars | Standard orbital machinery exists; primary studies identified | Full observational likelihood and derived EMRF deviation missing | No |
| Solar System | High-acceleration limit of the stated square-root law can be computed | Need matching ephemeris observable/constraint, not a repurposed Cassini number | No; specify prediction and valid bound |
| SPARC | Authentic four-law profiling, numerical checks and influence diagnostics run | Model dependence, systematics, uncalibrated significance; no derivation of full compression theory | More data help but do not repair the derivation |
| SLACS | Standard GR/SIS illustrative baseline exists | Derived EMRF lensing potential and measured-profile likelihood absent | No |
| Bullet Cluster | Prescribed entropy weighting can move an illustrative peak | Not dynamic, entropy not generated, no absolute lensing prediction or measured maps | No |
| High-z disks | A phenomenological a0(z) hypothesis exists | Traceable resolved-kinematics sample, corrections and likelihood needed | Data plus a fixed observational model can enable a limited test |
| GW170817 | Published propagation constraint available | Tensor/photon propagation not derived; c is assigned | No |
| Wide binaries | Published catalogues exist | Pair selection, contamination, projection and justified external-field likelihood absent | No, modelling is also required |
| Late expansion | DESI covariance-aware baseline and now full-covariance Pantheon+ baseline executed | An EMRF-derived H(z), parameter link and joint likelihood are missing | No; observational covariance obstacle is now removed |
| CMB | Public spectra/likelihood sources available | Physical perturbation equations and non-template spectrum missing | No |
| Quantum matter | Input-mass identity checked | Independent spectrum/configuration and stability proof missing | No |
| Black-hole entropy | Quarter-area identity evaluated | Quarter coefficient/microstates assumed; no direct entropy measurement | No |
| Cosmic dawn | Real redshift/population studies exist | Assembly/abundance prediction with selection and astrophysics absent | No |

The square-root galaxy law has worse penalized-fit performance than RAR under
the tested sample/constraints. That is a result about that implementation,
not a falsification of every geometric/energy/entropy C family.
The deep-bulge contrast is strongly influenced by UGC06787; it cannot currently
serve as proof of nonuniversal gravity or new thermodynamics.

## 8. What further data would genuinely enable

For a collision study: identified weak/strong lensing catalogues or calibrated
maps and covariance, registered X-ray surface-brightness/temperature products,
stellar-light maps with mass uncertainty, and geometrical/redshift information.
Relevant starting points are the [Chandra archive](https://cda.harvard.edu/chaser/)
and [MAST](https://mast.stsci.edu/). These are acquisition routes, not claims that
a ready-to-fit joint product has been downloaded. A shear catalogue and an
absolute prediction are preferable to matching a schematic peak.

For resolved high-z dynamics: named targets and public
[ALMA archive](https://almascience.nrao.edu/aq/) data/reduction products, plus
inclination, beam and pressure-support treatment. A redshift alone is not a
rotation measurement.

For S-stars: the exact published astrometric/RV tables and covariance/access
conditions, including missing-RV masks; no generated radial velocities.

For CMB: the [Planck Legacy Archive](https://pla.esac.esa.int/) supplies real
products, but acquisition cannot replace a derived perturbation spectrum.

Prioritize data only after specifying the quantity to predict, required units,
selection and comparison statistic. Do not collect more catalogues simply to
make an untestable equation look tested.

## 9. What Kirk can clarify next

The central unresolved question is **which mathematical evolution of C produces
the energy redistribution/entropy generation** intended in the original
discussion. The recorded statement is more specific than the current software.
An equation, a causal description of that step, or an authoritative passage
would let us audit whether an existing implementation omitted or reversed it.

Until then, preserve the original conceptual direction and distinguish known
thermodynamic consistency conditions from a derived EMRF mechanism. The next
honest milestone is a closed theory-to-observable chain for one system, not an
all-regimes pass count.

## Validation and preservation

The supernova likelihood has software checks for covariance dimensions,
asymmetry, non-finite values, full-covariance offset fitting and quadrature.
The collision regression tests retain the historical numerical illustration
while requiring non-empirical result labels. Original downloads, previous SPARC
results and the earlier compiled paper/review bundle are preserved. This
follow-up supersedes the earlier statement that the Pantheon+ covariance had
not been ingested; it does not retroactively change that historical run.

The corrected collision report was executed: its unchanged illustrative
displacements are 0 kpc and 180 kpc, but both observational verdicts are now
`NOT TESTED`. The [captured report](../results/real_data_followup/bullet_illustration_audit.json)
and [clearly labelled plot](../results/real_data_followup/bullet_static_illustration.png)
are software diagnostics, not additional observations.

The complete regression suite passes **226 tests**. Focused Ruff checks and
mypy checks of the new baseline and corrected collision module pass (namespace
packages enabled; missing third-party SciPy stubs explicitly excluded).
The changed HTML's inline JavaScript parses successfully, and the generated
collision plot was visually inspected. No claim of an exhaustive interactive
browser or security audit is made.
