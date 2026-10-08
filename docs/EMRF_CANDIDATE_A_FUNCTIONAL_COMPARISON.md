# Candidate A: defining C without adding new physics

**Direction selected by Kirk LaSalle:** Candidate A, geometry/energy
re-description. **This document recommends definitions for review; Kirk has not
yet selected a particular functional or approved a theorem.** No new physical
mechanism, field solver, observational fit or heating channel is implemented.

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
