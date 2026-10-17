# Candidate A: defining C without adding new physics

**Direction selected by Kirk LaSalle:** Candidate A, geometry/energy
re-description. **Kirk has now authorized investigation of options 1, 2 and 3,
with the full-density route for option 3; he has not selected a single final
law or approved a theorem.** No new covariant theory or heating channel is
implemented. The option-2 SPARC rejection is preserved; see
[section 11](#11-preregistered-sparc-test-of-option-2). A benchmarked
axisymmetric density-to-gravity solver and the current data-reconstruction
gate are recorded in [section 12](#12-all-three-options-authorized-full-density-gates).

## 1. Plain-language conclusion

**Kirk's follow-up direction:** "why can't we find this inside of GR?"
This supports looking for a faithful internal reformulation before proposing
new dynamics. It does not yet select C_m or assert that GR derives microscopic
matter or thermodynamic entropy from the proposed scalar. The comparison below
pursues that existing-GR route.

There is no single interchangeable meaning of "how much gravity/matter is here."
The comparison separates:

1. **Local material/non-gravitational energy**, measured by a specified observer.
2. **Tidal curvature**, which can exist in otherwise empty space.
3. **Energy or mass associated with a region**, which requires a boundary and
   a precise definition.

Your recorded C_G and C_E families accommodate these distinctions. They should
not be combined into one scalar and called the same physical quantity without
additional mathematics.

**Recommendation:** for a precise *local matter-energy reference*, use the
observer-projected Einstein curvature below, with a separate tidal-curvature
diagnostic where relevant. This is an assistant recommendation, not a change
to your approved theory or the production model.

For that reference, your power law can reproduce the GR energy-density identity
with **alpha=1 and a fixed normalization**. That is a coherent reformulation.
It does not show that matter has been created or independently predicted.

## 2. Conventions and what M means

Use four-dimensional GR with signature (-+++), coordinates with x0=ct, and a
unit timelike observer n^mu satisfying g_mu_nu n^mu n^nu=-1. The ordinary
four-velocity is u^mu=c n^mu. Write

$$G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu},\qquad
\epsilon_{(n)}=T_{\mu\nu}n^\mu n^\nu.$$

epsilon_(n) has units J m^-3. It includes whichever **non-gravitational**
stress-energy components are placed in T, not a universal local gravitational
energy density. Here Lambda is kept on the geometric side; absorbing it into
an effective T would change the energy definition and must be declared.

For this comparison denote

$$\rho_{E,(n)}=\epsilon_{(n)}/c^2.$$

That is energy-equivalent mass density. It is not generally conserved baryonic
rest-mass density, not the central mass parameter of a black hole, and not an
enclosed mass integral. This notation clarifies the possibilities for your M;
it does not silently redefine M throughout the repository.

For a fluid's comoving observer, epsilon includes rest and internal energy.
Another observer generally measures a different epsilon. The contraction is
coordinate-invariant **for a specified physical observer**, not observer-independent.
Tensors and quantities measured in a specified frame are legitimate observables;
it is too restrictive to say that only scalar curvature invariants are physical.

The comparison is within ordinary 3+1 GR. It does not settle the physical
meaning or reduction of additional dimensions in the broader recorded ontology.

## 3. Comparison of precise definitions

| Definition | Units | What it measures | Critical limitation |
|---|---|---|---|
| C_R=R | m^-2 | Trace curvature | Zero for trace-free radiation at Lambda=0 despite nonzero energy; includes 4 Lambda |
| C_t=sqrt(K), K=R_abcd R^abcd | m^-2 where K>=0 | Curvature magnitude in applicable backgrounds, including vacuum tides | Not local matter density; K is not generally nonnegative in Lorentzian geometry |
| C_m=(G_mu_nu+Lambda g_mu_nu)n^mu n^nu | m^-2 | Curvature projection tied to epsilon_(n) by GR | Observer specified; using Einstein's equations makes the density relation an identity |
| C_E=epsilon_(n) | J m^-3 | Observer-measured non-gravitational energy density | Matter-energy is explicitly an input, so epsilon/c^2 is not emergence |
| E_BY[boundary,slice,reference] | J | Brown-York regional energy | Boundary, observers/slice and reference subtraction matter; not a pointwise density |
| m_MS[areal sphere] | kg | Misner-Sharp mass in spherical symmetry | Not a generic definition for two merging nonspherical clusters |
| theta=div(u) or div(n), with convention stated | s^-1 or m^-1 | Expansion/contraction of a chosen congruence | Depends on the congruence and motion; not itself a matter density or entropy |

The functions are not equivalent simply because several can be normalized to
the same units. C0 must carry the units of the chosen C. Converting an energy
to a density requires a physically defined volume and slicing, not division
by an arbitrary plotting volume.

### 3.1 Why R alone does not give a universal matter density

Tracing Einstein's equation gives

$$R=4\Lambda-\frac{8\pi G}{c^4}T.$$

For a perfect fluid T=-epsilon+3p in its rest frame,

$$R=4\Lambda+\frac{8\pi G}{c^4}(\epsilon-3p).$$

For pressureless matter and known Lambda this can encode epsilon. For radiation,
p=epsilon/3, so R=4 Lambda regardless of the nonzero radiation energy density.
Thus a function of R alone cannot universally recover all local energy.
Conversely, a vacuum solution with Lambda nonzero can have R nonzero without
non-Lambda material stress-energy.

The timelike Ricci contraction does not fix this by being interchangeable with R:

$$R_{\mu\nu}n^\mu n^\nu=
\frac{4\pi G}{c^4}(\epsilon+3p)-\Lambda$$

for a comoving perfect fluid. It contains pressure. A focusing quantity and a
material-density quantity must not be silently identified.

### 3.2 Why sqrt(K) is a tidal diagnostic, not a universal local-density law

For Schwarzschild exterior with Lambda=0,

$$R_{\mu\nu}=0,\quad T_{\mu\nu}=0,\quad
K=\frac{48G^2M_\bullet^2}{c^4r^6}>0.$$

For positive k,C0, positive finite alpha, and C=sqrt(K), the mapping

$$M_{\rm mapped}=k(C/C_0)^\alpha$$

is strictly positive in this vacuum region. It therefore **cannot equal the
local material density there**. That is a counterexample to this particular
universal identification, not a refutation of every C functional or of using C
to describe gravitational geometry.

If instead M_mapped is called an effective tidal/organization indicator, its
nonzero value is not a contradiction—but it cannot then be reported as an
independent material mass density. Adding it as a new gravitating halo changes
the spacetime and is not merely Candidate A re-description.

The Schwarzschild expression is valid on a particular solution. Using its
fixed central-mass geometry to infer an additional extended density and then
claiming a self-consistent solution without resolving the field equations is
not legitimate. In general Lorentzian spacetimes K may be negative or vanish
despite nonzero curvature; sqrt(K) is not a universal real-valued magnitude.
Restrict its domain rather than replacing K by abs(K) without explanation.

### 3.3 A precise geometric local-energy reference

Define the following **recommended reference**, not a new field:

$$\boxed{C_m[g,n;\Lambda]=(G_{\mu\nu}+\Lambda g_{\mu\nu})n^\mu n^\nu.}$$

Then, conditional on Einstein's equation,

$$\boxed{\rho_{E,(n)}=\frac{c^2}{8\pi G}C_m.}$$

For your ansatz to reproduce this linear identity across a continuum of
positive C_m values with fixed constants,

$$\boxed{\alpha=1,\qquad k=\frac{c^2 C_0}{8\pi G}.}$$

**Proof:** with A=c^2/(8 pi G), equality requires
k C_m^alpha/C0^alpha=A C_m. Its logarithmic slope with respect to positive C_m
is alpha on the left and 1 on the right, so alpha=1; matching coefficients
then fixes k/C0=A. This proof assumes the mapping is required across varying
C_m, not fitted at a single point. A noninteger power also needs an explicit
domain if the chosen source permits negative energy density.

This is a mathematically valid *conditional equivalence of one scalar
relation*. It is not proof that the full EMRF equations are equivalent to GR:
a scalar projection does not recover all metric components, stress components,
Weyl curvature, constraints, boundary data or dynamics.

Nor is it a matter-creation derivation: T and Einstein's equation have already
supplied the relation. Reconstructing curvature from independent observations
can test the consistency of that mapping; calculating both sides from the same
fitted T/metric is not independent confirmation.

### 3.4 A precise direct-energy reference

Choose C_E=epsilon_(n), C0 an energy-density reference. Then
rho_E=C_E/c^2 is reproduced by alpha=1 and k=C0/c^2. It is even more explicit
that matter-energy is the input. This can be useful bookkeeping, but relabelling
it as compression does not explain the microscopic origin of the input.

Neither local reference contains thermal entropy by itself. Equal total energy
densities can correspond to different compositions, temperatures, particle
numbers, phase-space distributions and coarse-grained entropies. A state
description and equation of state are still needed.

## 4. Regional mass/energy: useful but different

### 4.1 Misner-Sharp benchmark

In spherical symmetry with areal radius r and the metric h_ab on the radial-time
two-space, define the mass convention

$$m_{\rm MS}=\frac{c^2r}{2G}\left(1-h^{ab}\partial_a r\,\partial_b r\right).$$

In the Lambda=0 Schwarzschild exterior this equals M_bullet, even though the
local material density at the boundary is zero. The region encloses the mass.
In other solutions its interpretation, including any cosmological-constant
contribution, must be declared. This spherical construction is not automatically
available for an arbitrary merging-cluster geometry.

### 4.2 Brown-York benchmark

With the convention yielding positive Schwarzschild energy, flat-space
reference subtraction, a static spatial slice and a round outer boundary,

$$E_{\rm BY}=\frac{c^4}{8\pi G}\int_{\partial\Sigma}(k_0-k_{\partial\Sigma})\,dA
=\frac{rc^4}{G}\left(1-\sqrt{1-\frac{2GM_\bullet}{rc^2}}\right),\quad r>r_s.$$

Here k_boundary is the trace of the two-surface extrinsic curvature in the
slice, not the normalization k of the matter ansatz. The sign/orientation and
reference convention are stated because they are not universal notation.

E_BY/c^2 approaches M_bullet at large r but is generally different at finite r.
Its formal limit is 2 M_bullet as r approaches r_s from outside; the static
observer construction is not a regular static measurement at the horizon.

Brown-York and Misner-Sharp need not agree at finite boundaries. Their
differences do not mean one has discovered or destroyed matter. They answer
different specified regional-energy questions. Neither should be added on top
of an existing gravitational energy budget as an independent C reservoir.

### 4.3 What one curvature number can and cannot determine

Within known Schwarzschild geometry,

$$M_\bullet=\frac{c^2r^3}{G}\sqrt{\frac{K}{48}}.$$

This uses **both** K and the areal radius and assumes spherical vacuum geometry.
Changing M_bullet -> 8 M_bullet and r -> 2r leaves K unchanged. Consequently,
one scalar K alone does not uniquely determine enclosed mass.

This does not rule out richer geometric information or derivatives under
additional assumptions. It only rules out the claimed one-number universal
inference. A local density and an enclosed central mass must not share an
undefined M label in the same comparison.

## 5. Recommendation within the selected direction

For the next definition review:

1. Use **C_m** as the exact local matter-energy reference *if* M is meant to be
   observer energy-equivalent density. Keep alpha=1 and the normalization fixed
   for this reference; do not fit them and then call the result an identity.
2. Keep **C_t** (restricted sqrt(K), or an explicitly specified observer tidal
   tensor) as a separate diagnostic of gravitational geometry. Do not feed it
   unqualified into a local material-density power law.
3. If the aim is **regional mass or energy**, choose the boundary/symmetry/observer
   definition first. Misner-Sharp and the round static Brown-York example are
   analytic benchmarks, not cluster collision prescriptions.
4. Do not invent a universal weighted sum of these quantities. A collection of
   physically different diagnostics may be more faithful than forcing one scalar.

This is not another Candidate B: no independent energy sector, damping,
new force, reservoir or entropy source has been added.

Kirk has selected Candidate A as the direction. These **specific choices remain
recommendations for his review**, because the meaning of M is consequential.
The safest next mathematical milestone is a defined dictionary and verified
reference relation, not an observational claim of matter emergence.

## 6. Thermodynamics and the collision target

Candidate A permits geometry and matter to change while ordinary interactions
convert bulk/gravitational energy into internal energy. That respects the
recorded downstream thermodynamic direction.

It does not make thermal entropy a function of curvature alone. Entropy still
needs the relevant matter state/coarse-graining and a balance law. A density
map, tidal curvature map or regional mass does not predict irreversible heating
without the dynamics and transport physics.

The standard reference-fluid/shock balances in the
[collision specification](EMRF_COLLISION_CANDIDATE_SPECIFICATION.md) still apply.
The legacy prescribed entropy-suppression plot is not promoted to a prediction.
An exact reformulation cannot yield extra heat or displaced lensing relative
to its reference dynamics. A proposed departure would need to be acknowledged
as a different hypothesis and reviewed separately.

## 7. Actual toolkit versus mathematical names

Read-only code inspection found:

- `geometry_formulation` and `energy_formulation` in
  [model.py](../emergent_matter_model/model.py) instantiate the same weighted
  function-evaluation machinery. They do not calculate an Einstein tensor,
  stress tensor, Brown-York boundary or Misner-Sharp mass.
- The matter routine applies the power law to caller-supplied values. That
  calculation alone does not select their physical meaning.
- [physics_baseline.py](../emergent_matter_model/physics_baseline.py) has a
  Schwarzschild K implementation; the diagnostics here reuse it rather than
  create a second production curvature engine.
- The existing `evaluate_bifurcation` wording still equates an unfavourable
  BIC difference with "compression reduces to gravitational geometry." That
  inference is not justified: lack of statistical preference is not an
  equivalence proof. It was not used in this assessment.

No production physics module or existing result has been changed in this
comparison. Correcting all legacy classification APIs is a separate scoped
task; callers should use the qualified reports, not those verdict strings.

## 8. Executed checks: exact backgrounds, not observed data

The [diagnostic script](../tools/check_candidate_a_definitions.py) and
[result artifact](../results/candidate_a_definition_checks.json) check:

- A nonzero radiation energy density with zero Ricci scalar at Lambda=0.
- Vacuum Lambda curvature without non-Lambda local material energy.
- The normalization that maps C_m to epsilon/c^2.
- Schwarzschild vacuum with nonzero K, zero local T, and nonzero regional mass.
- Finite-radius Brown-York versus Misner-Sharp, with stated conventions.
- Equal K for distinct mass/radius pairs and the radius-dependent inverse formula.
- Rejection of invalid reference scales and boundaries outside the static
  exterior domain.

Inputs are stipulated analytic examples. They are not fabricated observations,
physical simulations or an EMRF observational test. The outputs do not certify
the mapping as a new discovery. Nine focused algebra tests pass.

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_candidate_a_definitions.py
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model\test_candidate_a_definitions.py -q
```

## 9. Source verification and limits

- Recovered project intent and existing definitions:
  [curated recovered theory](../knowledgebase/antigravity_recovered_theory.md),
  [theoretical framework](../knowledgebase/theoretical_framework.md), and
  [Candidate A author decision](../knowledgebase/thermodynamic_collision_candidates.json).
  Older assertions in the theoretical framework are not automatically endorsed.
- Carroll, *Lecture Notes on General Relativity*,
  [gr-qc/9712019](https://arxiv.org/abs/gr-qc/9712019): metadata checked; the
  [NED-hosted gravitation chapter](https://ned.ipac.caltech.edu/level5/March01/Carroll3/Carroll4.html)
  was consulted for the distinction between local inertial frames and tidal effects.
- Brown & York, *Quasilocal Energy and Conserved Charges Derived from the
  Gravitational Action*, [gr-qc/9209012](https://arxiv.org/abs/gr-qc/9209012):
  primary abstract checked for boundary projection, Hamiltonian meaning,
  asymptotic limit and reference scope. Attempts to retrieve its PDF/HTML
  full text returned 404; no claim of complete full-text review is made.
  The round-boundary expression above follows from k0=2/r,
  k_boundary=2 sqrt(1-r_s/r)/r and area 4 pi r^2.
- Hayward, *Gravitational Energy in Spherical Symmetry*,
  [gr-qc/9408002](https://arxiv.org/abs/gr-qc/9408002):
  abstract and section II of the [HTML text](https://arxiv.org/html/gr-qc/9408002)
  inspected for spherical scope, areal-radius conventions and equation (4),
  E=r[1-g^(-1)(dr,dr)]/2 in geometrized units.

This is a source-grounded mathematical comparison, not exhaustive priority
research or a claim to have reconstructed an unknown spacetime from data.

## 10. Decision-ready outcome

**What succeeds:** Candidate A admits precise standard-physics definitions and
conditional identities. C can serve as a well-defined diagnostic rather than
an extra energy reservoir.

**What fails under stated assumptions:** R alone cannot universally encode
all local material energy; positive sqrt(K)^alpha cannot universally equal
local material density in Schwarzschild vacuum; scalar K alone cannot identify
enclosed mass without additional information.

**What remains open:** the intended meaning of M, the final C choice,
the map between full equations/observables, utility relative to standard
variables, and any independent claim of matter emergence or thermodynamics.

**Recommended next review:** approve or revise the proposed local energy-density
reference C_m, retaining tidal curvature separately. Do not call this selection
proof of an underlying origin of matter, even if its GR identity is exact.

### Verification status

Eighteen focused checks passed across the definition diagnostics, decision-ledger
and recovered-graph suites. The new diagnostic/test files pass Ruff, and the
diagnostic script passes a focused mypy check with explicit namespace-package
resolution. These validate calculations and record integrity, not new physics.

## 11. Preregistered SPARC test of option 2

**Why this test exists.** On 2026-10-16 Kirk asked to resolve the uneven
testing of Candidates A and B ("Let's resolve this now"). No observational test
of A is possible until C and M are fixed, so he was offered three written
operationalizations:

| Option | C and M | Observational test? |
|---|---|---|
| 1 | C = C_m, M = all gravitating energy, alpha = 1 | None: an exact GR identity |
| 2 | C = C_m, M = observed baryons, alpha = 1 | Yes: a parameter-free falsification test |
| 3 | Option 2 with a free exponent alpha | Requires a physical density scale, spatial source model and completion; see section 12 |

Kirk was unavailable and asked the assistant to choose pragmatically. The
assistant chose **option 2**, because it is the only option that gives A an
observational test without adding a departure from GR. It is recorded as
`assistant_proposed_pending_author_confirmation`, **not as Kirk's selection at
that time**. That frozen provenance is not rewritten. Kirk subsequently
authorized investigation of all three options (section 12); this result stays
attached to option 2 only.

**Prediction.** In a weak, quasi-static field, Einstein's equation gives
C_m = 8 pi G rho_dyn / c^2 = 2 laplacian(Phi_obs) / c^2. Option 2 sets
rho_dyn = rho_bar, so laplacian(Phi_obs) = laplacian(Phi_bar). For an isolated
galaxy, Poisson uniqueness then gives Phi_obs = Phi_bar, and every rotation
curve must equal the Newtonian curve of its observed baryons:
V_obs^2 = V_bar^2 at every radius. The Lambda term is about 1e-4 of the outer
disc density and is neglected.

**Preregistration.**
[candidate_a_sparc_baryonic_test_preregistration.json](../knowledgebase/candidate_a_sparc_baryonic_test_preregistration.json),
SHA-256 `e1298e2c223882e12b0f05329e2c289f0875cd3eee2258747adedfe482d08e06`,
frozen and committed before any Candidate A statistic was computed. **The test
is not blind.** The mass discrepancy in disc galaxies is decades old, the
radial acceleration relation was established on this same SPARC sample, and
this repository had already computed the same Newtonian baryons-only model
under other nuisance treatments ([SHOW_YOUR_WORK.md](SHOW_YOUR_WORK.md)
section 4, `results/sparc_real_analysis.json` and the SPARC Q3 holdout). The
preregistration lists all of this.

**Design.**

- Data: SPARC `Rotmod_LTG.zip` and `SPARC_Lelli2016c.mrt`, pinned by SHA-256.
- Primary population: the certified selection (Q <= 2, inclination >= 30
  degrees, at least 3 points), 153 galaxies and 3,168 points. Secondary: Q = 3,
  reported separately.
- Nuisance parameters per galaxy, exactly as in the certified marginalized
  pipeline: disc mass-to-light ratio (bulge = 1.4 x disc), distance factor and
  inclination, each bounded and penalized as preregistered.
- Option 2's prediction (A2) is compared with a nested reference (REF) that
  may add a non-negative pseudo-isothermal unseen-mass term. REF is a standard
  yardstick, not a dark-matter claim; with no halo it reduces to A2 exactly.
- Two nuisance treatments: T1 uses the certified mass-to-light prior; T2 drops
  it, letting the disc mass-to-light ratio range from 0.05 to 5, which favours A.
- Statistic: Delta_Q = Q(A2) - Q(REF) summed over galaxies, divided by an
  error-inflation factor lambda. The threshold is the 0.999 quantile of chi^2
  with 2 N_galaxies degrees of freedom (nominal, not a calibrated significance).
- Rule: **rejected** only if both T1 and T2 exceed the threshold.

**Result: rejected.**

| Primary population (153 galaxies) | T1 certified priors | T2 free mass-to-light |
|---|---|---|
| Delta_Q_cons | 98,216 | 100,067 |
| Threshold | 388.2 | 388.2 |
| Error inflation lambda | 2.80 | 2.73 |
| Galaxies individually needing unseen mass | 124 (81%) | 111 (73%) |
| Median outermost V_obs^2 / V_A2^2 (16th-84th percentile) | 1.61 (1.21-2.40) | 1.60 (1.21-2.27) |
| Disc mass-to-light ratio at its upper bound | 3.9% | 7.2% |

The Q = 3 secondary population (10 galaxies, 109 points) is also rejected under
both treatments. The sensitivity runs (prior centre 0.4 and 0.6; no error
inflation) all exceed the threshold, and they are reported, never the result.
There were no protocol deviations. All 5,508 optimizer starts in the primary
treatments converged.

**What this means.**

- **Option 2 is falsified for disc galaxies.** With C = C_m, alpha = 1 and
  M = observed baryons, Candidate A predicts too little gravity. At the
  outermost measured radius, the median galaxy's observed squared speed is
  about 1.6 times what its baryons provide.
- The outcome was expected, so this is a preregistered, reproducible record,
  not a discovery.
- **This does not test Candidate A as a whole.** Option 1 cannot independently
  discriminate against GR. Option 3 now has mathematical and solver checks
  (section 12), but still no observational fit.
- **Renaming the missing mass "emergent matter" would be relabelling** unless
  Candidate A predicts its amount and distribution from the baryons and the
  geometry before seeing the data. A law that did that would be a genuine
  departure from GR and would need its own preregistration.
- Kirk's later authorization to investigate all three options does not undo
  this result or select one of them as the final theory.

**Reproduce.**

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\evaluate_candidate_a_sparc_baryonic.py
```

If the preregistration, the SPARC cache or the pinned data fail verification,
the tool writes an `incomplete` report and exits nonzero. Otherwise it writes
[candidate_a_sparc_baryonic_test.json](../results/candidate_a_sparc_baryonic_test.json).

The first run used the evaluator committed before any statistic was computed.
Code review on PR #37 then moved the input checks inside the
incomplete-report path; the computation did not change. Rerunning the revised
evaluator reproduced every statistic, per-galaxy value and outcome exactly.
Only the artifact's `revision` and `source_sha256` fields changed. Its
`revision` names the PR #37 branch commit, because GitHub's rebase merge
rewrites commit hashes.

`emergent_matter_model/test_candidate_a_sparc_test.py` checks the model algebra
on synthetic galaxies, checks that the artifact is current, and re-evaluates
galaxies from the pinned data when it is present.

## 12. All three options authorized: full-density gates

On October 16, 2026, Kirk directed: **"Candidate A, all options 1, 2, and 3
can be tested. Run the gamut."** When offered a full-density route or an
exploratory spherical approximation, he chose **full-density**. This removes
the authorization barrier to investigating each option; it does not approve a
unique final theory, arbitrary missing-data assumptions or a physical result.

The [all-option protocol](../knowledgebase/candidate_a_all_options_protocol.json)
was frozen at commit `1c4efe3`, before the new numerical diagnostics:
SHA-256 `99bb1ab4be277a9683bbf9c2391196cf27f6e7b548f940abec992ed274fb3847`.
It is a prospective **diagnostic and reproduction protocol**, not a new blind
observational preregistration. The old SPARC result and an initial audit of the
new density tables were already known and disclosed.

### 12.1 Option 1: testable consistency, not independent evidence over GR

The executed sweep spans three energy densities, dust/radiation/vacuum-energy
fluid equations of state, three observer speeds and three normalization
scales: **81 checks**, maximum relative identity error **1.33e-15**.
The calculation constructs Ricci and Einstein tensors in an orthonormal frame,
checks the observer normalization, and compares the projected curvature with
the observer's stress-energy density. Schwarzschild and Lambda-vacuum checks
also preserve the distinction between material density and nonzero curvature.

**Outcome: consistency checks passed.** These use stipulated exact
backgrounds. They neither independently confirm A against GR nor establish
equivalence of the full equations. "All gravitating energy" here means the
non-gravitational stress-energy in T measured by the specified observer; it
does not introduce a universal local gravitational-field energy density.

### 12.2 Option 2: complete reproduction of the existing data test

The evaluator reran the primary T1/T2, Q=3 and prior-centre sensitivity
treatments. **All 6,621 compared result fields reproduced**, including
per-galaxy quantities, not just headline totals. Floating-point tolerances
were fixed at rtol=1e-8 and atol=1e-8; integers and labels match exactly.
Only revision and software-environment metadata are excluded from comparison.

**Outcome: rejected, unchanged.** Primary Delta_Q_cons is 98,216 (T1) and
100,067 (T2), compared with 388.2. Reproduction is not a second independent
observational test. The original protocol, source and result bytes remain
unchanged, including their historical assistant-proposed attribution.

### 12.3 Option 3: derive the full-density prediction before fitting

The earlier shorthand "option 2 with a free exponent" did **not** specify a
complete observational model. With the same normalization as options 1/2, set

$$\rho_0=\frac{c^2 C_0}{8\pi G}>0,\qquad
\rho_{\rm bar}=\rho_0(C_m/C_0)^\alpha,\qquad \alpha>0.$$

In the weak, static, pressure-negligible limit this gives

$$\rho_{\rm eff}=\rho_0(\rho_{\rm bar}/\rho_0)^{1/\alpha},\qquad
\nabla^2\Phi=4\pi G\rho_{\rm eff},\qquad
V_c^2(R)=R\,\partial_R\Phi(R,0).$$

The positive-exponent domain admits a continuous zero-density vacuum limit.
Alpha=0 cannot be inverted; negative alpha is singular as the baryonic density
approaches zero. The density scale rho0 is physically consequential for a
nonunit exponent and is unidentifiable at alpha=1. A dimensionful density must
not simply be raised to an exponent without this normalization.

Important restrictions tested or exposed by this form:

- Sum the **volume densities** of stars, HI and H2 before mapping. A power of
  their separate Newtonian speed contributions is not this model.
- Alpha=1 recovers the baryons-only source exactly. If ordinary GR is still
  sourced only by those same baryons, a universal relation at varying
  densities requires alpha=1. Nonunit alpha needs an effective additional
  stress-energy source or modified dynamics; this scalar equation does not
  itself provide a covariant conserved completion.
- For alpha>1 the source is enhanced below rho0 and suppressed above it;
  alpha<1 reverses this. Thus the difference rho_eff-rho_bar is not a
  universally nonnegative "extra matter" component.
- A local power law with alpha>0 leaves a truly baryon-free region source-free.
  For a finite isolated source the asymptotic field remains Keplerian; this
  does not by itself exclude approximately flat curves over a finite observed
  radial range.

The new solver evaluates the **finite-thickness axisymmetric volume source**:
the azimuthal Newtonian kernel is integrated analytically using complete
elliptic integrals; radial and vertical Gauss-Legendre quadrature extends to
infinity. It assumes reflection symmetry about the midplane. No spherical
replacement, force softening, or clipping of an outward radial force is used.

For the stipulated Miyamoto-Nagai analytic density/potential benchmark, the
maximum relative squared-speed error at order 128 is **1.66e-6**
(**0.000166%**), below the frozen 0.5% gate. Doubling order 64 to 128 changes
the result by at most 5.01e-6. Separate nonlinear double-exponential-disc
benchmarks at alpha=0.5, 1 and 2 also converge below that gate.
These are **mathematical/software benchmarks, not observed galaxies**.
Accuracy for a future reconstructed source must be checked separately.

### 12.4 Public density data: retrieved, but not silently made complete

New inputs were retrieved from the primary
[CDS Leroy et al. (2008) archive](https://cdsarc.cds.unistra.fr/ftp/J/AJ/136/2782/ReadMe):
table4 (galaxy properties), table7 (radial profiles) and the byte-format ReadMe.
All three are SHA-256 pinned in the protocol and
[data catalog](../knowledgebase/library/data_catalog.json), with raw inputs
kept in the ignored external-data cache. The source is Leroy et al. (2008),
AJ 136, 2782-2845, doi:10.1088/0004-6256/136/6/2782.

Table7 supplies projected HI, H2 and stellar surface densities. The gas
columns **already include helium**. Blank fields are missing, not zero;
the archive also documents upper-limit flags. The existing
[SPARC products](https://astroweb.case.edu/SPARC/) instead give component
rotation speeds and stellar surface brightness, not a complete three-dimensional
baryonic source.

| Certified SPARC overlap | Profile rows | Missing HI rows | Missing H2 rows |
|---|---:|---:|---:|
| DDO154 | 7 | 0 | 7 |
| IC2574 | 46 | 0 | 46 |
| NGC2403 | 57 | 0 | 57 |
| NGC2841 | 25 | 5 | 16 |
| NGC2976 | 26 | 8 | 26 |
| NGC3198 | 23 | 0 | 13 |
| NGC3521 | 30 | 0 | 11 |
| NGC5055 | 43 | 0 | 20 |
| NGC6946 | 41 | 0 | 14 |
| NGC7331 | 33 | 0 | 17 |
| NGC7793 | 38 | 0 | 38 |

None of these 11 overlaps has every component tabulated at every profile
radius; vertical densities are not supplied. This does **not** mean modeling
them is impossible. It means the current tables do not justify an automatic,
assumption-free full-density fit. Missing/censored gas, vertical scale heights,
bulge deprojection, inner/outer boundaries, distances, inclinations and
mass-to-light/CO conversion uncertainties need explicit modeling.

**Option 3 has no observational fit, rejection, support or parameter bound in
this run.** Next: reconstruct and qualify those sources using the underlying
HI/CO/photometry observations and justified nuisance assumptions; declare the
weak-field-only or covariant scope; then freeze an observational parameter
domain, sample, comparator, statistic and uncertainty treatment before fitting.
The diagnostic exponent examples are not a preregistered empirical search range.

### 12.5 Reproduce and interpret the exit status

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\evaluate_candidate_a_all_options.py --fetch-density-data
```

The same entry point is registered as `evaluate-candidate-a-all-options`.
The [artifact](../results/candidate_a_all_options.json) records each option,
source/data hashes and the reconstruction requirements. **Exit 2** means
completed diagnostic/reproduction checks with the option-3 observational gate
still blocked. **Exit 1** means input or numerical failure with an explicit
reason. Neither is a claim that all requested observational work is finished.

Validation of this checkpoint: **147 focused tests passed** across both
candidate programs, the CLI, ledger and graph. The new evaluator passes Ruff
and a focused mypy check (existing untyped imports excluded); generated
references and the strict documentation build pass. This is not a new
whole-repository test count or physical validation.
