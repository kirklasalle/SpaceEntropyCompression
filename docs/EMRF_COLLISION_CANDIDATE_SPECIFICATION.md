# EMRF collision candidates: energy transfer and thermodynamic entropy

**Status: Candidate A selected by Kirk LaSalle on October 8, 2026.**
His decision, "I'm for candidate A", selects the geometry/energy re-description
direction, not a particular functional, a proof of equivalence or empirical
validation. Candidate B remains an **unselected historical proposal**.
No new collision solver, dynamics, simulation, mock observations or observational
fit accompanies this decision.

### Selected direction and next gate

The subsequent [Candidate A functional comparison](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
now supplies precise local-curvature, observer-energy and regional-energy options.
It recommends an observer-projected Einstein-curvature reference for
energy-equivalent density, with tidal curvature kept separate. This is a
recommendation for review, not an author-selected functional or proof of emergence.

Continue with C as a description of existing geometry/energy organization,
without introducing a separate C energy reservoir, new heat source or force.
Thermodynamic behavior remains downstream of the selected standard dynamics.
The next step is to compare precise C_G/C_E definitions, their units, invariance
and information content, then assess the independent meaning and domain of
M = k(C/C0)^alpha. No particular definition of C is selected by this decision.

A reformulation could offer clarity or a useful diagnostic without changing
observations. If it is exactly equivalent, observational agreement alone cannot
distinguish it from the reference theory or establish novel physics. The
definition and mathematical equivalence must be checked explicitly.

## 1. The question in plain language

The recovered proposal places matter and interactions before macroscopic
thermodynamic behavior. It also permits a distinct information/geometric entropy
to characterize the deeper state. We preserve both roles.

The first question is therefore not "can an assumed entropy map move a drawn
lensing peak?" It is:

> What energy is transferred when the proposed compression state changes, where
> does that energy come from, and what observable heating or entropy production
> would differ from known collision physics?

There are at most two candidates here:

- **A: a description of known geometry/energy organization.** C may be useful
  without adding a new force or heating channel.
- **B: a new, separately accounted energy-exchange sector.** The proposed
  effective equations below illustrate a conditional consistency requirement.
  They are new AI-proposed assumptions, **not recovered equations or a proven
  mechanism**, and do not yet define a complete cluster model.

The stronger proposition that *all thermodynamic laws emerge from EMRF* remains
open. Using familiar energy conservation, a thermal equation of state and an
entropy definition to build an effective model does not derive those laws.

## 2. Attribution and variable dictionary

| Item | Recovered meaning / proposed precise convention | Units and status |
|---|---|---|
| C | One of the recorded geometry, energy, entropy or composite functionals | Units depend on the selected family; not yet uniquely fixed |
| C0 | Independent reference with the same units as C | Reference definition requires author review |
| xi = C/C0 | **Proposed bookkeeping coordinate** for the local effective example | Dimensionless; not an additional spatial dimension |
| M = k(C/C0)^alpha | Recovered matter-state/density mapping | Whether M is total mass or density remains open; k carries M's units |
| rho | Ordinary gas mass density in the baseline | kg m^-3; not automatically identical to the ansatz M |
| S_th, s_th | Thermal entropy and entropy per unit gas mass | J K^-1 and J kg^-1 K^-1 |
| S_geom | **Proposed distinct name** for the candidate information/geometric quantity | Undefined until entropy type, measure and normalization are chosen |
| T, p, e | Temperature, pressure and internal energy per gas mass | K, J m^-3, J kg^-1 |
| v, Phi | Bulk velocity and Newtonian gravitational potential in the chosen approximation | m s^-1, m^2 s^-2 |
| j_Q, tau | Heat flux and viscous stress | J m^-2 s^-1, Pa |
| sigma | Local thermodynamic entropy production per volume | J m^-3 K^-1 s^-1; not entropy flux |
| K_X = k_B T n_e^(-2/3) | Astrophysical entropy proxy | Often keV cm^2; **not** an entropy in J K^-1 |
| U(X,t) in older notes | Open classification of unexplained influence | Not a specified dynamical field; do not confuse with energy density below |

Sources: [recovered theory intentions](../knowledgebase/antigravity_recovered_theory.md),
[claim ledger](../knowledgebase/antigravity_recovery_claims.json), and
[T03 decision](T03_ENTROPY_ONTOLOGY_DECISION_2026-10-07.md).

### Definitions that cannot be silently resolved

For a fixed alpha, the mass mapping constrains k/C0^alpha unless another
definition fixes one scale. It cannot identify both by fitting the same mass.
For noninteger alpha a real-valued model also needs a domain for C/C0.

The collision baseline conserves the ordinary baryonic mass. No mass-creation
term is inserted merely because the larger ontology discusses emergent matter.
If a later candidate changes baryonic rest mass, the associated rest-energy,
momentum, species and observational constraints must be included.

A geometric/information entropy is not set equal to s_th, K_X or black-hole
entropy. Their relationship is an unresolved modelling question, not an
algebraic notational choice.

## 3. Reference system and approximation

The motivating object is a **collision of galaxy clusters**, containing hot
plasma and largely collisionless galaxies. It is not simply two individual
galaxies or two dust clouds. Moving potential wells, plasma shocks, stellar
centroids and lensing peaks are different quantities.

For the first consistency layer use weak-field, nonrelativistic fluid dynamics
for the bulk gas, with a specified potential/source model. This is not a
relativistic completion and does not assume equilibrium everywhere in the
cluster. A one-temperature ideal monatomic gas with fixed composition is an
explicit reference approximation. Electron/ion disequilibrium, magnetic fields,
cosmic rays, conduction and radiative losses require extensions if material.

### 3.1 Energy and entropy accounting already required by standard physics

With material derivative D/Dt and theta = div(v):

$$\partial_t\rho+\nabla\cdot(\rho\mathbf v)=0,$$
$$\rho\frac{D\mathbf v}{Dt}=-\nabla p+\nabla\cdot\tau-\rho\nabla\Phi,$$
$$\rho\frac{De}{Dt}=-p\theta+\tau:\nabla\mathbf v-\nabla\cdot\mathbf j_Q.$$

These are a closed *balance structure*, not a solved cluster: an equation of
state, transport coefficients, potential dynamics and initial/boundary
conditions are still required. If radiation or another external exchange is
included, its energy and entropy fluxes must be added explicitly.

For a simple locally equilibrated fluid, the Gibbs relation is

$$T\,ds_{\rm th}=de+p\,d(1/\rho).$$

It gives, in the absence of extra heat/mass/species sources,

$$\partial_t(\rho s_{\rm th})+
\nabla\cdot\left(\rho s_{\rm th}\mathbf v+\frac{\mathbf j_Q}{T}\right)
=\frac{\tau:\nabla\mathbf v}{T}
-\frac{\mathbf j_Q\cdot\nabla T}{T^2}.$$

For Newtonian stress tau = 2 eta D_dev + zeta theta I and Fourier flux
j_Q = -kappa grad(T),

$$\sigma=
\frac{2\eta D_{\rm dev}:D_{\rm dev}+\zeta\theta^2}{T}
+\frac{\kappa|\nabla T|^2}{T^2}\geq0$$

when T>0 and eta,zeta,kappa>=0. This is **conditional on those constitutive
assumptions**. It is not a derivation of transport coefficients from C.

The pressure-work term -p theta can increase temperature in reversible
compression without producing entropy. For a reversible ideal gas,
T rho^(1-gamma) and p/rho^gamma are constant along an adiabatic trajectory.
Heating is not by itself evidence for new entropy production.

### 3.2 Gravitational work is not free energy

The gas receives mechanical power density -rho v dot grad(Phi). For a prescribed
time-dependent potential the gas-plus-external-potential energy accounting has
a source rho partial_t(Phi), after including the associated transport terms.
That represents work by an external source. It is not legitimate to call the
gas alone an isolated energy-conserving system.

For an isolated self-gravitating Newtonian system, the global binding energy
is conventionally (1/2) integral rho_total Phi dV with suitable boundaries,
plus gas/stellar kinetic and internal terms. Do not add the same gravitational
energy a second time under the name C. In general relativity a chosen
quasi-local/asymptotic energy construction requires its own boundaries and
assumptions; this specification does not invent a universal local gravitational
energy tensor.

### 3.3 A shock gives a concrete baseline observable

For a steady, planar, normal ideal-gas shock with no radiative loss, nonthermal
pressure or extra energy channel, upstream Mach number M1 and gamma give

$$r=\frac{\rho_2}{\rho_1}=
\frac{(\gamma+1)M_1^2}{(\gamma-1)M_1^2+2},$$
$$P=\frac{p_2}{p_1}=
\frac{2\gamma M_1^2-(\gamma-1)}{\gamma+1},\qquad
\frac{T_2}{T_1}=\frac{P}{r},$$
$$\Delta s_{\rm th}=c_v\ln(P/r^\gamma).$$

These follow from mass, momentum and total-energy jump conditions with the
physical entropy-increasing branch. The thin-shock idealization does not resolve
the dissipative layer; it does not mean that microscopic dissipation is absent.
The formulas approach r=P=T2/T1=1 at M1=1; gamma=5/3 gives limiting compression
r=4 for a strong reference shock. Those are algebraic limits, not measurements
of the Bullet Cluster.

For fixed composition and gamma=5/3, K_X is proportional to p/rho^gamma, so
entropy *differences* can be related to c_v ln(K_X,2/K_X,1). A varying composition,
electron temperature different from ion temperature, or projected spectral fit
breaks that simple identification.

Sources: [NASA normal-shock reference](https://www.grc.nasa.gov/www/k-12/airplane/normal.html);
[Markevitch & Vikhlinin review](https://arxiv.org/abs/astro-ph/0701821).
NASA's ideal-gas treatment is a baseline, not a sufficient plasma model.

## 4. Candidate A: geometry/energy re-description without a new channel

**Attribution:** recovered C_G/C_E alternatives; the precise choice of functional
is still for review.

Choose C_A = F(geometry, appropriate energy measure) as a diagnostic computed
from a standard solution. Matter interacts and heats according to section 3.
There is **no independent extra heat source Q_C** just because C_A changes.
Macroscopic thermodynamics is downstream, as in the recorded explanatory chain.

This is potentially a useful representation or reduced diagnostic. A
one-to-one reparameterization of a given solution gives identical observables
by construction; it cannot discriminate itself from the original equations.
If F is many-to-one or discards variables, equivalence is not guaranteed.

The original M=k(C/C0)^alpha mapping must still be independently checked. If
F uses the very mass whose emergence is claimed, fitting the identity is not
a prediction. Equivalence to GR requires mapping equations, constraints,
boundary data and observables, not merely matching an orbit or shock curve.

**Outcome at this stage:** conceptually admissible route; no uniquely chosen F,
no new heating prediction, no theorem of matter emergence.

## 5. Candidate B: a separately budgeted relaxation channel

**Attribution: new AI-proposed effective ansatz for discussion, not Kirk's
recovered law and not an original discovery.** A driven, damped internal
coordinate is a familiar effective modelling structure. Its value here is to
make conservation and assumptions explicit, not to rename it as proven gravity.

### 5.1 Restricted local example

Consider a homogeneous material element of fixed physical volume, in its
instantaneous rest-frame approximation, during a stage with no volume work,
heat flux, radiation, new particle production or changing composition.
This is a consistency example, **not a model of the entire collision or shock**.

Let xi=C/C0 be an internal coordinate and define energy density

$$u_C=\tfrac12 I_C\dot\xi^2+V_C(\xi),$$
$$I_C\ddot\xi+\Gamma_C\dot\xi+V_C'(\xi)=J(t).$$

Assume constant I_C>0, Gamma_C>=0 and a differentiable potential bounded below.
J is a generalized mechanical drive, not yet related to geometry or gas motion.
The proposed transfer to thermal energy is

$$Q_C=\Gamma_C\dot\xi^2,\qquad \dot u_{\rm th}=Q_C,$$
$$\dot u_{\rm drive}=-J\dot\xi.$$

Here u_drive is the energy density of the explicitly accounted driving reservoir.
It must remain physically admissible. If J is prescribed without modelling its
source, the calculation is externally driven, not an isolated cluster.

Dimensions with xi dimensionless:

| Quantity | Units |
|---|---|
| I_C | J s^2 m^-3 |
| Gamma_C | J s m^-3 |
| V_C, J | J m^-3 |
| Q_C | J m^-3 s^-1 |
| u_th, u_drive, u_C | J m^-3 |
| c_V,vol = du_th/dT | J m^-3 K^-1 |

No value, shape or universal normalization for I_C, Gamma_C, V_C or J is fitted
or asserted here. The historical beta=0.45 and gas exponent 2.2 are not used.

### 5.2 A conditional proposition, with its short proof

**Assumptions:** the restricted element above, positive T, positive thermal heat
capacity, the stated evolution/transfer equations, and the local-equilibrium
relation du_th=T ds_th,vol at fixed volume/composition.

Multiplying the coordinate equation by dot(xi) gives

$$\dot u_C=J\dot\xi-\Gamma_C\dot\xi^2.$$

Consequently,

$$\frac{d}{dt}(u_C+u_{\rm drive}+u_{\rm th})=0,\qquad
\dot s_{\rm th,vol}=\frac{\Gamma_C\dot\xi^2}{T}\geq0.$$

This proves a **conditional consistency identity**, not the physical existence
of C or the origin of thermodynamics. Conservation holds because the transfer
terms are included with opposite signs. Thermal entropy increases because a
dissipative closure and equilibrium entropy relation were assumed.

For Gamma_C=0 there is no dissipation or thermal entropy increase from this
channel, although reversible work can change u_C. For J=0 and Gamma_C>0,
initially stored coordinate energy can heat the bath; a stationary state
dot(xi)=0 produces no Q_C. No absolute values or clamping are used to force
the result. Gamma_C<0 would fail the stipulated thermal-production condition.

If S_geom itself carries entropy, the **total** entropy budget also requires
its evolution and any reservoir entropy/flux. The inequality above concerns
the local thermal bath only; it is not automatically a generalized second law
for a gravitational system.

### 5.3 Why this is not yet a predictive EMRF collision model

The following are not supplied by the archived record or the local identity:

1. A specific F connecting xi to geometry/energy/information independently of
   the observed temperature or mass.
2. A mechanical drive J and backreaction derived from an interaction; an arbitrary
   time function could fit almost any heating history.
3. Spatial transport, field momentum/stress, gravitational field equations,
   advection and compression work for moving elements.
4. A microscopic or statistical reason for Gamma_C, its sign, scale and
   temperature/state dependence; ordinary viscosity must not be counted twice.
5. A definition and evolution of S_geom, if present.
6. Independent parameter constraints and a recoverable observational signature.
7. A metric/lensing mapping. The coordinate's energy cannot be converted into
   lensing convergence by taking a square root and normalizing a picture.

Setting Gamma_C=0 removes this *heating channel*, but does not by itself remove
all effects of an independently coupled C sector. Recovering the standard
baseline also requires decoupling that sector and avoiding residual initial
energy/gravitational backreaction. A global stability/hyperbolicity statement
cannot be inferred from this local second-order ordinary differential equation.

**Outcome:** a coherent conditional local accounting example, but an incomplete
physical closure. No simulation or observational test of Candidate B is justified
until those missing specifications are reviewed.

## 6. What would discriminate a model?

### 6.1 First observable: joint density and temperature jumps

Infer a density jump r from a registered X-ray surface-brightness model and
measure upstream/downstream temperature spectra. Under the reference
assumptions, r implies

$$M_1^2=\frac{2r}{(\gamma+1)-(\gamma-1)r}.$$

The independent temperature measurement can then test the reference predicted
T2/T1. Do not infer Mach number from the temperature ratio and then reuse the
same ratio as an independent successful prediction. Shared spectral/imaging
uncertainties require a joint likelihood.

A useful diagnostic is a thermal residual relative to the standard shock
budget, with electron/ion equilibration, nonthermal pressure, geometry, conduction,
mixing and calibration uncertainty propagated. **A residual is not uniquely Q_C.**

The published Bullet Cluster study
[Markevitch, astro-ph/0511345](https://arxiv.org/abs/astro-ph/0511345) already uses
the shock to study electron-ion equilibration. It is a reason to model standard
plasma alternatives carefully, not evidence for this proposed C channel.

### 6.2 Identifiability gate

Candidate A has no distinguishing observable if it is strictly a re-description.
Candidate B has **no identifiable unique prediction yet** while J, Gamma_C,
V_C and the geometry mapping remain free.

A later candidate could be testable if these ingredients predict an energy
transfer as a function of independently constrained state/kinematics, with
parameters fixed on separate regions/systems and evaluated on held-out
observations. Present-day snapshot maps are not time derivatives of the field.
The development of that prediction is gated, not assumed complete.

Do not prescribe a free Q_C from the measured residual and call the agreement
confirmation. Do not use a lensing-gas centroid separation as a substitute for
the thermal budget. Lensing adds a distinct constraint only after a derived,
absolute field-to-light-deflection mapping exists.

## 7. Data-readiness specification (no new bulk download or reduction)

| Product | What must be retained | Why needed |
|---|---|---|
| Chandra event/calibration products | Target, ObsIDs, exposure, instrument/CALDB versions, filtering and backgrounds | Reproducible spectra and surface brightness |
| Region spectra | Upstream/downstream masks, counts/background, response matrices and effective areas | Temperature inference, not an image color |
| Density/profile inference | Emissivity model, abundance/composition, path length/deprojection and covariance | Convert emission measure to n_e/rho and infer r |
| Plasma constraints | Electron-ion state, nonthermal pressure, cooling/conduction and mixing assumptions | Standard alternatives to extra heating |
| Optical/galaxy kinematics | Redshifts, stellar mass/light uncertainty, selection and projection | Independently constrain geometry and motion |
| Lensing data, if later used | Shear/multiple-image catalogues, source redshifts, mass-sheet/source uncertainties | Absolute gravitational constraint, not normalized maxima |
| Cross-product registration | Coordinate system, angular/physical conversion, calibration and shared errors | Ensure the same physical regions are compared |

Public routes: [Chandra archive](https://cda.harvard.edu/chaser/),
[CIAO extended-source spectral workflow](https://cxc.cfa.harvard.edu/ciao/threads/extended/),
and [MAST](https://mast.stsci.edu/). The CIAO workflow documents the need for
source/background spectra and response products; its example observation is
**not** being asserted as a selected Bullet Cluster dataset.

The [Clowe et al. study](https://arxiv.org/abs/astro-ph/0608407) provides the
context for measured lensing/plasma segregation. Its existence is not a
likelihood for the proposed thermodynamic mechanism.

No verified ready-to-fit joint collision product has been acquired in this phase.
Access, table availability, region choices and uncertainties must be checked
after a predictive candidate is selected. Existing SPARC, Pantheon+ and DESI
observations cannot replace these collision products.

## 8. Consistency checklist and disposition

| Check | A | B, local example |
|---|---|---|
| Distinguishes S_th from S_geom | Required; neither is silently substituted | Preserved; S_geom dynamics unresolved |
| Energy source and sink accounted | Standard gravitational/fluid budget | Algebraically paired transfers; physical J/backreaction missing |
| Reversible heating versus entropy | Standard separation in section 3 | Gamma_C=0 creates no thermal entropy through this channel |
| Isolated versus driven system | Explicit boundary/source dependence | Reservoir equation required; prescribed J alone is external work |
| Standard-physics limit | Same physics only if mapping is equivalent | Requires full decoupling, not merely Gamma_C=0 |
| Momentum/geometry/lensing | Existing baseline plus mapping checks | Not provided by a local thermal oscillator |
| A new physical prediction | None for an exact re-description | Not identifiable until closure/parameters fixed |
| Origin of thermodynamic laws | Not derived | Not derived; thermal/constitutive laws assumed |
| New theorem or discovery | Not established | Conditional identity only; not a novelty claim |
| Implementation authorization | Not granted by this document | Not granted by this document |

## 9. Recorded decision and remaining review before implementation

**Decision received:** Kirk selected A. The choice between A and B below is
resolved in favor of A; questions about B's new drive/relaxation mechanism are
retained as proposal history, not the active research direction.

Kirk should be able to reject or revise the interpretation without losing the
original record. The next review should settle:

1. Does C re-describe the existing energy organization (A), or add an independent
   energy-storage/exchange degree of freedom (B), or is neither faithful?
2. Which recovered C family and which entropy definition belong to that choice?
3. What physical process in the moving collision supplies the drive or
   redistributes energy? If known in words but not equations, preserve the
   description before selecting an effective closure.
4. Is a local effective relaxation description acceptable as a candidate,
   acknowledging it is not a derivation of gravity or thermodynamics?
5. What independent observation could falsify the resulting specified mechanism?

**Stop here for functional review.** No C evolution, collision solver, new
observational fit, quantum job or revision of historical data is authorized
by this packet. If neither candidate can be made predictive, that is a useful
negative specification result rather than a reason to generate a passing demo.

## 10. Sources and what was checked

- Recovered source/attribution: [recovery audit](ANTIGRAVITY_RECOVERY_AUDIT.md)
  and [curated theory note](../knowledgebase/antigravity_recovered_theory.md).
- NASA Glenn, *Normal Shock Wave Equations*: equations and assumptions inspected;
  points to NACA Report 1135. This is a standard ideal-gas reference, not
  astronomical evidence.
- Markevitch & Vikhlinin, *Shocks and cold fronts in galaxy clusters*,
  [astro-ph/0701821](https://arxiv.org/abs/astro-ph/0701821),
  DOI 10.1016/j.physrep.2007.01.001: verified metadata and abstract scope,
  including Mach-number and electron-ion-equilibrium diagnostics.
- Markevitch, *Chandra observation of the most interesting cluster in the Universe*,
  [astro-ph/0511345](https://arxiv.org/abs/astro-ph/0511345): verified abstract
  reporting a shock/equilibration analysis. No data values from its abstract are
  treated here as a new independent fit.
- Clowe et al., [astro-ph/0608407](https://arxiv.org/abs/astro-ph/0608407),
  DOI 10.1086/508162: verified observational-study metadata/abstract, not a
  downloaded lensing catalogue.
- CIAO extended-source thread: inspected response/background workflow.
- Jacobson, [gr-qc/9504004](https://arxiv.org/abs/gr-qc/9504004),
  DOI 10.1103/PhysRevLett.75.1260: verified abstract explicitly assumes an
  entropy-area proportionality and delta Q=T delta S to obtain an equation
  of state. It is not a derivation of all thermodynamics from this C ansatz.

These source checks support the stated distinctions and the next data gate.
They are not an exhaustive literature review, novelty certification or full
reanalysis of those papers. An additional attempted APS primary-page retrieval
returned HTTP 403 and was not used as verified source content.

## 11. Packet verification

Eight focused document/graph/recovery checks pass, including unique IDs,
source-reference resolution, preservation of qualified recovery entries and
the explicit author-review gate. The new test file passes the existing Ruff
rules. These are publication-memory integrity checks, **not eight physical
tests of Candidate B**.

The energy and entropy identities in sections 3 and 5 are shown algebraically
with their assumptions. No new physical mechanism was implemented or run.
Existing SPARC/cosmology results, archived source copies, the earlier paper
and the user-added copy of the next-phase plan were not modified by this phase.
