# Candidate B model contract — draft for author review

**Date:** 2026-10-13  
**Decision status:** Restricted first test approved on 2026-10-16; broader model
and numerical inference protocol remain open.  
**Research status:** Both A and B are selected research candidates and run
concurrently ([dual-candidate program](../EMRF_DUAL_CANDIDATE_PROGRAM.md)).
Sections 15–17 were written while B was the one active candidate.  
**Selection status:** Kirk's 2026-10-16 decision supersedes the exclusive
Candidate A selection of 2026-10-08; it does not establish physical validity.
**Author decision (2026-10-13):** Kirk LaSalle specifies that the additional
coordinates \(d_i\) are physical spatial dimensions. Their geometry and
observable reduction remain open. For this first pass, “entropy” means
thermodynamic entropy \(S\), and no zero value is assumed; its system boundary
and reference remain open. He also intends field co-location to enter
Candidate B's exchange law and requested comparison of universal and
species-specific new couplings. Kirk has agreed to retain the worked Higgs
portal as an **unselected working hypothesis** on October 13. On October 16 he
approved it as the restricted first test in Section 16. This is a test
assumption, not an established physical interaction.

This contract is a gate for deciding whether Candidate B can be specified
coherently. It is not a proposed final theory, a simulation specification, or
evidence that an additional physical sector exists. See the
[dimensionality and co-location exploration](CANDIDATE_B_DIMENSIONALITY_EXPLORATION_2026-10-13.md)
for the motivating question and its boundaries.

## 1. Agreed scope for this exploration

1. Preserve Candidate A as a selected research candidate, currently paused.
   Keep its functional-selection and validation gates open.
2. Work actively on selected Candidate B. Work on only one candidate at a time;
   switching active work does not reject the other candidate.
3. Treat field co-location as an intended input to Candidate B's exchange law,
   but do not infer the interaction, energy transfer, entropy value, or
   physical prediction from the bar-and-stool analogy.
4. Do not interpret field overlap as zero entropy, positive entropy
   production, particle creation, or a shared physical state without separate
   definitions and equations. The overlap variable must be connected to energy
   transfer by a specified physical interaction.
5. Treat the driven/damped coordinate in
   [the existing Candidate B specification](../EMRF_COLLISION_CANDIDATE_SPECIFICATION.md#5-candidate-b-a-separately-budgeted-relaxation-channel)
   as a conditional bookkeeping example only. Its drive, field mapping,
   momentum, backreaction, and physical damping mechanism are not supplied.
6. Do not fit an unconstrained Candidate B heat source to an observed thermal
   residual or count standard plasma dissipation a second time.
7. Compare established Standard Model interactions with possible new
   compression-field couplings. Compare universal and species-specific
   couplings before selecting any interaction route.

## 2. Provisional notation contract

Use \(X\in\mathcal{M}^{D}\) for a point in the spatial domain, with
\(D=3+d_{\rm ext}\), and \(t\) for the parameter of change. Entropy \(S(X,t)\)
is a state field, not a coordinate. Kirk has specified that the additional
coordinates are physical spatial dimensions. This does not yet specify their
metric, coordinate ranges, topology, or coupling to fields.
The Candidate B bookkeeping variable \(\xi=C/C_0\) is an internal state
coordinate, not another spatial coordinate.

For the first mathematical consistency pass:

* Use the already specified three-dimensional local cell as the reference
  calculation, with its quantities expressed per physical 3-volume.
* Treat the reference calculation as a three-dimensional baseline, not as the
  complete higher-dimensional model.
* Keep the metric, ranges, and boundary or compactification conditions of the
  additional \(d_i\) unresolved until specified.
* Do not extend a per-volume equation to \(D\) spatial dimensions by changing
  units alone. First define the \(D\)-dimensional measure and the reduction or
  projection that relates it to observable three-dimensional quantities.
* Track full-manifold overlap and overlap after projection onto observed
  three-space as distinct questions. Projected coincidence alone is not
  full-manifold coincidence.

This is a conservative calculation boundary, not a claim that the physical
extra dimensions are absent or negligible.

## 3. Provisional entropy contract

Follow the project’s
[entropy ontology decision](../T03_ENTROPY_ONTOLOGY_DECISION_2026-10-07.md):
for this first pass, \(S(X,t)\) means thermodynamic entropy and is a state
field; \(\sigma\) denotes local entropy production. Kirk specified that no
zero value of \(S\) is assumed. A proposed geometric or information entropy, if
later introduced, must have a distinct definition until a relation to
thermodynamic entropy is derived.

The entropy measure, subsystem, coarse-graining, reference convention, and
state must still be specified before any absolute value such as \(S=0\) is
meaningful. No claim involving \(\sigma=0\) follows merely from co-location.
The conditional Candidate B identity
\(\dot{s}_{\rm th,vol}=\Gamma_C\dot{\xi}^{\,2}/T\geq0\) remains conditional on
its local-equilibrium, positive-temperature, and nonnegative-damping
assumptions; it does not determine an absolute entropy or a generalized second
law.

## 4. Minimum requirements before Candidate B equations are extended

Any proposed extension must state:

| Item | Required before extension |
|---|---|
| Domain and measure | Spatial dimension, metric volume element, boundaries, and whether densities are per 3-volume or \(D\)-volume |
| State variable | Definition and units of \(C\), \(C_0\), and \(\xi=C/C_0\), with domain for any non-integer power |
| Exchange mechanism | Physical origin of the drive \(J\), damping \(\Gamma_C\), and potential \(V_C\); no unconstrained functions selected to fit residuals |
| System boundary | Included material, field, and driving-reservoir energies, plus boundary fluxes |
| Conservation | Energy and momentum balance, including field stress/momentum and backreaction where applicable |
| Entropy | Thermal entropy current/balance and any distinct geometric or information entropy, without double counting |
| Baseline limit | Explicit conditions that recover the selected standard-physics baseline |
| Observable | A derived, independently measurable difference from the baseline and parameters constrained independently of the test data |

Until these are supplied, no collision simulation, new observational fit, or
claim of a Candidate B prediction is authorized by this draft.

## 5. Co-location interaction routes to compare

The requested comparison has two levels: ordinary Standard Model processes
versus a new Candidate B sector, then universal versus species-specific forms
of that new coupling. The bar-stool analogy selects none of them.

| Route | What makes co-location relevant | What it would mean for Candidate B |
|---|---|---|
| Established Standard Model interactions | Local field configurations interact through their specified gauge couplings, quantum states, and kinematics. Quarks participate in the strong interaction; electrically charged particles interact electromagnetically; neutrinos participate in weak interactions. Mere support overlap is not sufficient to calculate a transfer. | First calculate the ordinary matter/radiation energy and momentum exchange. Candidate B remains distinct only if a coupling to \(C\) or \(\xi\) is derived without double-counting those known exchanges; otherwise this is standard physics or a re-description, not an additional energy sector. |
| New universal metric/scalar coupling | As one common example, let all Standard Model matter fields see the same conformally related metric \(A^2(\xi)g_{AB}\). Variation sources \(\xi\) through a factor proportional to \(d\ln A/d\xi\) times the stress-energy trace \(T=G_{AB}T^{AB}\), not a generic direct coupling to every component of \(T_{AB}\). Classically trace-free radiation therefore needs separate consideration; quantum trace anomalies can modify this statement. This is a schematic scalar-tensor route, not an EMRF equation. | A universal coupling can preserve leading-order composition-independent free fall, but it can still produce an additional force or modify gravitational dynamics. It is not thereby equivalent to GR or unconstrained. Derive the \(\xi\) source, field stress, and backreaction from one complete action. |
| New species-specific coupling | Couple \(\xi\) to a selected gauge-invariant matter or gauge-field operator. Low-energy expressions such as \(\xi \mathcal{F}_{AB}\mathcal{F}^{AB}\) are illustrative only; a complete theory must satisfy the relevant gauge symmetries and use the correct operator and units in \(D+1\) dimensions. | Material response can depend on species and composition, and may generate equivalence-principle violations or other constrained effects. The actual prediction depends on the operator, mediator range, screening, and couplings; it cannot be inferred from the symbolic term alone. |

The first route is the lower-assumption baseline. The Standard Model describes
the strong, electromagnetic, and weak interactions through their specified
fields and carrier particles; it does not include gravity as a quantum
interaction. It explains known particle interactions, but it does not by itself
establish an extra coupling to \(C\). Neither new-coupling route is ruled out
merely by writing it down, but both must face relevant precision tests. The
MICROSCOPE weak-equivalence-principle result is one constraint class; this
draft does not calculate a Candidate B prediction or claim that the experiment
excludes a particular, still-undefined coupling.

Universal free fall is not a no-new-physics test: a universally coupled scalar
can still change gravitational dynamics and must pass the applicable
gravitational tests. Conversely, species-dependent effects are not automatic
for every proposed operator; calculate the resulting material charges and
predictions instead of assigning a generic exclusion. Extra physical
dimensions add further requirements: define the bulk operator, metric measure,
coupling units, and reduction before comparing with four-dimensional
constraints.

To claim a Candidate B energy exchange, define an overlap functional on the
full spatial domain and its observable projection, then derive how it enters
the interaction and any resulting source for \(\xi\). A Standard
Model-only calculation may yield no source for \(\xi\); that outcome means no
separate Candidate B exchange has been established. Do not prescribe \(J\) or
\(\Gamma_C\) as free functions of overlap merely to reproduce a measured
heating residual. In particular, a damping term must follow from a specified
interaction and coarse-graining before it is interpreted as thermal entropy
production.

**Sources checked:** CERN,
[The Standard Model](https://home.cern/science/physics/standard-model/),
for the scope of the strong, electromagnetic, and weak interactions and their
carrier particles; Damour and Donoghue,
[Equivalence Principle Violations and Couplings of a Light Dilaton](https://arxiv.org/abs/1007.2792),
for the relation between scalar couplings to Standard Model parameters and
composition-dependent effects; Touboul et al.,
[Result of the MICROSCOPE Weak Equivalence Principle test](https://arxiv.org/abs/2209.15488),
for the relevance of precision equivalence-principle tests to proposed new
interactions; and the project’s
[action-principle note](../../knowledgebase/action_principle_derivation.md#2-the-action),
which explicitly leaves the source \(J\) unspecified. These references
motivate constraints and bookkeeping; they do not validate Candidate B.

## 6. Decisions reserved for Kirk's review

These questions are intentionally left open rather than silently decided:

1. What metric, coordinate ranges, topology, and boundary or compactification
   conditions describe the physical \(d_i\), and how should the first model
   reduce them to three-dimensional observables?
2. What subsystem, coarse-graining, and reference convention define the
   thermodynamic entropy for the proposed “moment before a new condition,” and
   what precisely are the initial and final states?
3. Is a brane-localized Higgs-portal interaction a useful first working
   hypothesis, or should a different interaction be derived?
4. After comparing the routes in Section 5, which physical interaction
   couples field co-location to the compression degree of freedom and produces
   the proposed exchange? Specify the involved fields/species, coupling, and
   source of transferred energy.
5. Which system is the first intended application? A homogeneous local cell is
   suitable for accounting checks; a cluster collision requires spatial
   transport, plasma physics, gravity, and observational closure.

## 7. Worked interaction candidate: bulk compression scalar / brane Higgs portal

**Status:** originally assistant-proposed; now author-approved for the restricted
first test in Section 16. It is not recovered from Kirk's earlier theory or
evidence that the physical interaction exists. Its purpose is to make one co-location coupling explicit
enough to derive a source and paired energy exchange.

### 7.1 Fields, domain, and interaction

Use natural units \(\hbar=c=1\) for the field-theory equations. Let the
spacetime bulk be \(\mathcal M^{D,1}\) with coordinates
\(X^A=(x^\mu,y^a)\), where \(\mu=0,1,2,3\), \(a=1,\ldots,d_{\rm ext}\), and
\(D=3+d_{\rm ext}\). As a **working localization assumption**, take the
Standard Model fields to live on a 3+1-dimensional brane \(\Sigma\), embedded
at \(y^a=0\), and let a real compression scalar \(\phi(X)\) propagate in the
bulk. The induced brane metric is \(\gamma_{\mu\nu}\), and
\(\phi_b(x)=\phi(x,y=0)\).

The brane Higgs doublet is \(H(x)\), with the gauge-invariant operator

$$\mathcal O_H(x)=H^\dagger H-\frac{v^2}{2}.$$

Here \(v\) is the Higgs vacuum expectation value in the selected convention.
The subtraction sets this operator to zero in the chosen Higgs vacuum; it does
not remove fluctuations or define a thermodynamic entropy. The proposed action
is

$$
S=S_{\rm bulk}+S_{\rm SM,\Sigma}+S_{\rm int},
$$
$$
S_{\rm bulk}=\int_{\mathcal M^{D,1}}d^{D+1}X\sqrt{-G}
\left[-\frac12G^{AB}\partial_A\phi\,\partial_B\phi-V(\phi)\right],
$$
$$
S_{\rm int}=-\int_\Sigma d^4x\sqrt{-\gamma}\,
g_\xi\,\xi_b\,\mathcal O_H,\qquad
\phi=f_\phi\xi,\quad \xi_b=\xi|_\Sigma,\quad g_\xi=\mu f_\phi.
$$

Here \(\xi\) is dimensionless, \(f_\phi\) is a constant normalization with
mass dimension \((D-1)/2\), and \(g_\xi\) has mass dimension two. This supplies
a proposed bridge to the bookkeeping coordinate \(\xi=C/C_0\), but it does
not derive that \(C/C_0\) is a propagating scalar field.

This is a species-specific Higgs-operator portal, not a universal metric
coupling. It makes local bulk/brane co-location explicit: the brane source for
\(\phi\) exists at the same brane point where \(\mathcal O_H\) is present.
It is not a product of arbitrary particle “occupancy” probabilities. Quarks,
neutrinos, and photons do not each receive this term directly; any effect on
them would have to follow through specified Standard Model interactions and
the resulting Higgs dynamics.

The corresponding local signed overlap-energy density on the brane is

$$u_{\rm ov}(x)=g_\xi\,\xi_b(x)\,\mathcal O_H(x).$$

It can be positive or negative and is not by itself a probability, an entropy,
or a heating rate. The interaction-energy functional on a brane spatial slice
\(\mathcal B_t\) is

$$E_{\rm ov}(t)=\int_{\mathcal B_t}d^3x\sqrt{h}\,
g_\xi\,\xi_b\,\mathcal O_H,$$

with \(h\) the induced spatial metric determinant. A finite-range or
coarse-grained overlap kernel is deliberately not added: it would introduce
extra length scales and additional assumptions.

In \(D+1\) bulk spacetime dimensions, the canonical mass dimension of \(\phi\)
is \([\phi]=(D-1)/2\); on the four-dimensional brane,
\([H]=1\) and \([\mathcal O_H]=2\). Therefore
$$[\mu]=2-[\phi]=\frac{5-D}{2}$$
in mass units. For \(D=3\), \(\mu\) has mass dimension one. For other \(D\),
this operator may be an effective interaction with a dimensionful coupling;
its cutoff and completion must be specified. These are natural-unit mass
dimensions, not a completed SI normalization.

### 7.2 Equations of motion and source

Define the transverse delta distribution by
\[
\int d^{d_{\rm ext}}y\sqrt{h_\perp}\,
\delta_\perp(y) f(y)=f(0).
\]
Variation with respect to the bulk scalar gives

$$f_\phi^2\Box_{D+1}\xi-
\frac{dV_\xi}{d\xi}=
g_\xi\,\mathcal O_H(x)\delta_\perp(y),\qquad
V_\xi(\xi)=V(f_\phi\xi).$$

For a flat bulk with signature \((-+\cdots+)\), this is

$$f_\phi^2\big(\ddot\xi-\nabla_D^2\xi\big)+
\frac{dV_\xi}{d\xi}=
-g_\xi\,\mathcal O_H(x)\delta_\perp(y).$$

Thus the source is fixed by the interaction, rather than independently
prescribing the earlier \(J(t)\). The brane-localized source couples to
\(\xi_b\); under the one-circle benchmark in Section 7.5 its periodic profile
is resolved into the stated KK modes. The Higgs equation also changes. Writing
\(\mathcal L_{\rm SM}\supset-(D_\mu H)^\dagger D^\mu H-V_H(H)\), the portal
contributes

$$D_\mu D^\mu H-
\frac{\partial V_H}{\partial H^\dagger}
-g_\xi\xi_b H=0,$$

with the sign following the stated \(S_{\rm int}\) convention. Hence the
backreaction acts on both the bulk scalar and the brane Higgs. After
electroweak symmetry breaking, \(\mathcal O_H=vh+h^2/2\) in unitary gauge;
the portal contains scalar-Higgs mixing. Its size and phenomenology require
independent parameter constraints.

### 7.3 Paired energy-momentum transfer

Let \(T_\phi^{AB}\) be the bulk scalar stress tensor derived from
\(S_{\rm bulk}\), and let \(T_\Sigma^{\mu\nu}\) include the Standard Model
brane fields and portal interaction. On their equations of motion, the
interaction gives

$$\nabla_A T_\phi^{AB}=
g_\xi\,\mathcal O_H\,\delta_\perp(y)\nabla^B\xi,$$
$$D_\mu T_\Sigma^{\mu\nu}=
-g_\xi\,\mathcal O_H\,D^\nu\xi_b.$$

The brane expression is the tangential exchange; the bulk equation is
distributional. Tangential energy-momentum exchange cancels between the
compression and brane sectors. Full normal momentum conservation additionally
requires a dynamical brane embedding (including its tension/stress and recoil)
or an explicitly modelled support sector: an externally fixed brane can absorb
normal momentum. With dynamical gravity, the complete bulk, brane, and
embedding system must satisfy the corresponding covariant conservation law,
subject to boundary fluxes. Energy transferred to the Higgs/Standard-Model
sector is removed from the compression scalar sector, and conversely; it is
not drawn from an unmodelled reservoir.

For a locally flat, fixed brane with negligible spatial or transverse
boundary flux, the interaction contributions to the integrated energy
balances are

$$\left.\dot E_\Sigma\right|_{\rm exch}
=+\int_{\mathcal B_t}d^3x\sqrt h\,
g_\xi\,\mathcal O_H\,\dot\xi_b,\qquad
\left.\dot E_\phi\right|_{\rm exch}
=-\int_{\mathcal B_t}d^3x\sqrt h\,
g_\xi\,\mathcal O_H\,\dot\xi_b.$$

for the paired sectors, with \(E_\Sigma\) defined from the brane stress tensor
including the portal interaction energy and \(E_\phi\) the integrated bulk
scalar energy. In a dynamic Higgs state, these are the source terms in the
covariant stress-energy identity; the Higgs equation and interaction energy
must be retained rather than treating \(\mathcal O_H(t)\) as a fixed external
source. Spatial gradients, bulk propagation, brane motion, metric
backreaction, and boundary fluxes add terms and cannot be dropped in a cluster
model.

For the displayed sign convention, energy delivered to the brane comes from
the compression-scalar sector; the sign reverses when energy flows back into
that sector. The model does not specify how the scalar was excited or
replenished: that requires initial/boundary data or an explicit drive and its
energy budget. The portal therefore identifies a paired transfer channel, not
an ultimate energy origin or a free energy reservoir. Subsequent Standard
Model processes may redistribute energy received by the brane.

The portal supplies a reversible interaction and does **not** by itself give a
positive damping coefficient \(\Gamma_C\) or thermal entropy production.
Dissipation could arise only after specifying and deriving the Higgs/SM
environment, coarse-graining, and energy/entropy fluxes. Any candidate scalar-to-SM transfer must appear with its opposite
scalar-sector change. The contract's earlier
three-dimensional fixed-volume identity is not this higher-dimensional
derivation.

### 7.4 Scope and risks of this candidate

* The brane embedding and the localization of Standard Model fields are
  additional assumptions; Kirk has specified physical extra dimensions but
  has not specified a brane, metric, compactification, or dimensional
  reduction.
* The interaction is species-specific at the operator level. Any effective
  coupling to quarks, neutrinos, or photons is indirect and model-dependent.
* A universal conformal coupling \(A^2(\phi)G_{AB}\) would be a different
  model and requires its own action, source, and predictions. Universal
  coupling does not establish equivalence to GR.
* Higgs-sector and scalar mixing constraints, fifth-force and equivalence
  principle limits where applicable, collider bounds, stability, and
  higher-dimensional cutoff/compactification constraints would have to be
  evaluated for a fully specified parameterization. No bound is computed here.
* The portal does not yet define an entropy-zero event, an entropy law, a
  cluster observable, or evidence for Candidate B.

## 8. Three-dimensional local-cell algebra and units audit

For the existing fixed-volume example, take \(C\) and \(C_0\) to have the same
units, so \(\xi=C/C_0\) is dimensionless. The documented equations are

$$u_C=\tfrac12 I_C\dot{\xi}^{\,2}+V_C(\xi),\qquad
I_C\ddot{\xi}+\Gamma_C\dot{\xi}+V_C'(\xi)=J,$$
$$Q_C=\Gamma_C\dot{\xi}^{\,2},\qquad
\dot{u}_{\rm th}=Q_C,\qquad
\dot{u}_{\rm drive}=-J\dot{\xi}.$$

Under the stated fixed physical 3-volume convention, the units are:

| Quantity | Required units | Check |
|---|---|---|
| \(\xi\) | dimensionless | Requires \(C/C_0\) to be dimensionless |
| \(u_C,V_C,u_{\rm th},u_{\rm drive},J\) | J m\(^{-3}\) | Energy or generalized force density for dimensionless \(\xi\) |
| \(I_C\) | J s\(^2\) m\(^{-3}\) | Makes \(I_C\dot{\xi}^{\,2}\) an energy density |
| \(\Gamma_C\) | J s m\(^{-3}\) | Makes \(\Gamma_C\dot{\xi}\) a force density and \(Q_C\) a power density |
| \(Q_C,\dot{u}_{\rm th},\dot{u}_{\rm drive}\) | J m\(^{-3}\) s\(^{-1}\) | Energy-transfer rates per physical 3-volume |
| \(\dot{s}_{\rm th,vol}=Q_C/T\) | J m\(^{-3}\) K\(^{-1}\) s\(^{-1}\) | Thermal entropy-production rate density |

For constant \(I_C\) and differentiable \(V_C\), multiply the \(\xi\) equation
by \(\dot{\xi}\):

$$\dot{u}_C=J\dot{\xi}-\Gamma_C\dot{\xi}^{\,2}.$$

With the stipulated equal-and-opposite transfers,
\(\dot{u}_{\rm th}=\Gamma_C\dot{\xi}^{\,2}\) and
\(\dot{u}_{\rm drive}=-J\dot{\xi}\), this gives

$$\frac{d}{dt}(u_C+u_{\rm th}+u_{\rm drive})=0.$$

**Audit outcome:** the local equations are algebraically and dimensionally
consistent for the stated fixed-volume, three-dimensional bookkeeping example,
provided the listed assumptions hold. The entropy-production sign additionally
requires \(T>0\) and \(\Gamma_C\geq0\). This is a conditional identity built
into the assumed transfer laws; it does not derive a physical interaction,
justify the damping coefficient, or establish that Candidate B exists.

**Not audited by this local-cell check:** a higher-dimensional lift of the
phenomenological \(J\)-and-\(\Gamma_C\) damping model. Sections 10--13 instead
define and reduce a distinct bulk-field/brane benchmark; they do not derive
\(J\), \(\Gamma_C\), or the entropy-production closure. Do not treat the 3D
unit check as validation in \(\mathcal M^D\).

## 9. Interim review outcome

At the October 13 stage this draft recorded seven author decisions and one
assistant-proposed interaction retained as an unselected working hypothesis.
The October 16 selection and restricted-test approval are recorded in Section 16.
A flat one-circle compactification and brane localization are now specified
as a benchmark, not as author-selected facts about nature. The entropy
boundary/reference, benchmark parameters, full KK-tower constraint, and
application details remain open. The equations above establish conditional
exchange and backreaction for the stated action; they do not establish that
this action describes nature. Candidate A remains selected throughout unless
Kirk explicitly records a later selection decision, as he now has for B.

## 10. Explicit benchmark geometry and KK reduction

Specialize the working model to one flat compact extra dimension:
\[
\mathcal M^{4,1}=\mathbb R^{3,1}\times S^1_R,\qquad
y\sim y+2\pi R,\qquad
ds^2=\eta_{\mu\nu}dx^\mu dx^\nu+dy^2.
\]
Thus there are four spatial dimensions in the bulk (\(D=4\)). Standard Model
fields live on a fixed 3+1-dimensional brane at \(y=0\), while the real
compression scalar \(\phi\) is periodic and propagates in the bulk. Flatness,
the circle topology, brane localization, and the fixed-brane approximation
are benchmark assumptions; the radius \(R\), its stabilization, gravity
backreaction, and the EFT cutoff are not specified by the project or inferred
from data here.

For a bulk mass \(m_5\), expand the scalar in canonically normalized real
Fourier modes:
\[
\phi(x,y)=\frac{1}{\sqrt{2\pi R}}\left[
\phi_0(x)+\sqrt{2}\sum_{n\ge1}\left(
\phi_n^c(x)\cos\frac{ny}{R}+\phi_n^s(x)\sin\frac{ny}{R}\right)\right],
\qquad
m_n^2=m_5^2+\frac{n^2}{R^2}.
\]
The brane interaction in Section 7.1 is equivalently
\[
S_{\rm int}=-\int d^4x\,\mu_5\phi(x,0)\mathcal O_H(x),
\qquad \mu_5=\mu,\quad [\mu_5]=\tfrac12
\]
in mass units. The sine modes vanish at \(y=0\), giving
\[
S_{\rm int}=-\int d^4x\,\mu_4\left[
\phi_0+\sqrt{2}\sum_{n\ge1}\phi_n^c\right]\mathcal O_H,\qquad
\mu_4=\frac{\mu_5}{\sqrt{2\pi R}},\quad [\mu_4]=1.
\]
This volume normalization is the explicit reduction from the five-dimensional
coupling to the four-dimensional brane theory. At low energies, the
observable brane energy exchange is calculated from the reduced modes;
integrating out modes is valid only below their masses and with their induced
operators retained. If several modes lie in the relevant spectrum, the
single-mode approximation below does not constrain the full model.

## 11. Conditional independent coupling constraint

After electroweak symmetry breaking, write the neutral Higgs excitation as
\(h\), with \(\mathcal O_H=vh+h^2/2\). The zero-mode quadratic mass matrix,
before diagonalization, is
\[
\mathcal M_0^2=
\begin{pmatrix}
m_h^2 & \mu_4 v\\
\mu_4 v & m_0^2
\end{pmatrix},
\qquad
\tan(2\theta_0)=\frac{2\mu_4v}{m_h^2-m_0^2}.
\]
Here \(m_h\) denotes the unmixed Higgs mass parameter at this order, and
\(m_0=m_5\). The positive-definite tree-level mass matrix requires
\(m_h^2>0\), \(m_0^2>0\), and
\((\mu_4v)^2<m_h^2m_0^2\). In particular, this minimal quadratic
benchmark is unstable for a strictly massless zero mode and nonzero portal
coupling unless additional stabilizing terms or a changed vacuum are supplied.

For an **isolated** scalar mode with no other changes to Higgs production or
decay, the SM-like Higgs coupling modifier is \(\kappa_V=\cos\theta_0\).
ATLAS's Run-2 Higgs-interaction combination reports coupling modifiers
consistent with their Standard Model values (ATLAS Collaboration,
arXiv:2207.00092). This establishes an external constraint class, but the
published fit is not a fit to this bulk-scalar KK model. The earlier numerical
one-sigma translation is therefore withdrawn: a model-independent uncertainty
must not be promoted to a model-specific coupling ceiling.

For the KK tower, define
\[
\mu_0=\mu_4,\qquad \mu_n=\sqrt{2}\mu_4\ (n\ge1),\qquad
N_\Lambda=\left\lfloor R\sqrt{\Lambda^2-m_5^2}\right\rfloor
\]
when \(\Lambda\ge m_5\). The modes retained by the four-dimensional EFT are
\(0\le n\le N_\Lambda\). The Schur-complement condition for the truncated
tree-level mass matrix to be positive definite is
\[
m_h^2>v^2\left(
\frac{\mu_4^2}{m_5^2}
+2\mu_4^2\sum_{n=1}^{N_\Lambda}
\frac{1}{m_5^2+n^2/R^2}\right).
\]
Consequently,
\[
|\mu_4|<
\frac{m_h}{v\sqrt{S_{\rm stab}(R,m_5,\Lambda)}},\qquad
S_{\rm stab}=
\frac{1}{m_5^2}+2\sum_{n=1}^{N_\Lambda}
\frac{1}{m_5^2+n^2/R^2}.
\]
This is an internal stability envelope, not an observational limit. If the
cutoff is taken formally to infinity, the convergent sum gives
\[
S_{\rm stab}^{(\infty)}
=\frac{\pi R}{m_5}\coth(\pi m_5R),\qquad
|\mu_4|<
\frac{m_h}{v}
\sqrt{\frac{m_5\tanh(\pi m_5R)}{\pi R}}.
\]
Equivalently, using \(\mu_5=\sqrt{2\pi R}\mu_4\),
\[
|\mu_5|<
\frac{m_h}{v}\sqrt{2m_5\tanh(\pi m_5R)}.
\]
The limit tends to zero with \(m_5\), confirming that the minimal quadratic
benchmark cannot support a massless zero mode with nonzero portal coupling.

At momenta well below every retained \(m_n\), tree-level elimination of the
massive modes produces the local brane operator
\[
\Delta\mathcal L_{\rm eff}
=\frac12\mu_4^2S_{\rm stab}\,\mathcal O_H^2.
\]
For the formal infinite tower this coefficient is
\[
\frac{\mu_4^2}{2}\frac{\pi R}{m_5}\coth(\pi m_5R)
=\frac{\mu_5^2}{4m_5}\coth(\pi m_5R).
\]
This term shifts Higgs-sector self-interactions and must be included in a
low-energy comparison. It is not an entropy source: it is the reversible
effective interaction left by the exchanged tower.

Away from a degeneracy \(m_n^2\simeq m_h^2\), perturbative diagonalization
gives the Higgs admixture
\[
\epsilon_{\rm KK}=
v^2\mu_4^2\left[
\frac{1}{(m_h^2-m_5^2)^2}
+2\sum_{n=1}^{N_\Lambda}
\frac{1}{(m_h^2-m_5^2-n^2/R^2)^2}\right].
\]
To this order, the normalized SM-like state has
\(\kappa_V\simeq(1+\epsilon_{\rm KK})^{-1/2}\). If a future
model-specific analysis supplies an allowed lower value
\(\kappa_{\min}\), then a conditional tower envelope is
\[
|\mu_4|\le
\sqrt{\frac{\kappa_{\min}^{-2}-1}
{v^2S_{\rm mix}(R,m_5,\Lambda)}},
\]
where \(S_{\rm mix}\) is the bracketed sum without \(\mu_4^2v^2\).
This formula is not valid near a Higgs--KK degeneracy, where the relevant
finite mass matrix and widths must be diagonalized and compared directly with
resonance data. It also omits exotic decays and other loop or production
effects.

The non-arbitrary validity domain used for these formulas is
\[
R>0,\qquad m_5>0,\qquad
\Lambda\ge\max(m_5,m_h),\qquad
\max_{0\le n\le N_\Lambda}
\left|\frac{v\mu_n}{m_h^2-m_n^2}\right|\ll1.
\]
The last condition is the weak-mixing and spectral-gap requirement. Parameter
points that fail it are not excluded by this derivation; they require exact
finite-matrix diagonalization and a resonance/width treatment instead.

Thus a valid parameter point must satisfy the internal stability envelope and,
once a model-specific \(\kappa_{\min}\) exists, the perturbative mixing
envelope. No value of \(R\), \(m_5\), \(\Lambda\), or
\(\kappa_{\min}\) is selected here. No observational dataset was downloaded
or reanalyzed, no fit was performed, and no simulation or data test was run.
A genuine tower-wide confidence limit requires a specified parameter domain,
full mass/width and decay treatment, and a dedicated likelihood analysis.

**External reference:** ATLAS Collaboration, [A detailed map of Higgs boson
interactions by the ATLAS experiment ten years after the
discovery](https://arxiv.org/abs/2207.00092). The published agreement with
Standard Model Higgs interactions motivates the parameterized
\(\kappa_{\min}\) gate above; no numerical model-specific bound is attributed
to that paper here, and it is not evidence for Candidate B.

## 12. Source-bounded parameter domain

No single experimental result supplies preferred values of \(R\), \(m_5\),
or \(\Lambda\). The defensible domain is therefore defined by the model's
validity conditions and by the ranges in which specific likelihood terms are
applicable, rather than by an invented rectangular scan box.

Use the parameter vector
\[
\Theta=(R,m_5,\Lambda,\mu_5,\vartheta_V),
\]
where \(\vartheta_V\) denotes any still-unspecified parameters in the bulk
potential, brane-localized counterterms, and non-Standard-Model widths. The
common theory domain is
\[
R>0,\quad m_5>0,\quad \Lambda\ge\max(m_5,m_h),\quad
N_\Lambda=\left\lfloor R\sqrt{\Lambda^2-m_5^2}\right\rfloor<\infty,
\]
with a positive mass matrix and all retained eigenmasses below \(\Lambda\).
All masses and inverse lengths use the natural-unit convention of Section 7.1,
so \(R\) is expressed in inverse energy. The case \(N_\Lambda=0\) is a
zero-mode EFT. A genuine finite-tower analysis additionally requires
\(N_\Lambda\ge1\), equivalently
\(\Lambda^2\ge m_5^2+R^{-2}\). For perturbative formulas, also require the
weak-mixing/spectral-gap condition in Section 11. Otherwise use exact
finite-matrix diagonalization.

The cutoff is a declared EFT boundary, not an observable. A convenient
bookkeeping variable is the dimensionless brane coefficient
\(\widehat\mu_5=\mu_5/\sqrt{\Lambda}\). Requiring
\(|\widehat\mu_5|<1\) is adopted only as a conservative working
perturbativity domain for a future scan; changing this convention requires a
separate unitarity or loop analysis. It is not an experimental exclusion.

Partition the domain by observable regime after exact diagonalization:
| Regime | Criterion | Authorized likelihood treatment |
|---|---|---|
| 125 GeV Higgs state | One eigenstate is identified with the observed Higgs and its predicted rates lie in the published measurement domain | Evaluate a Higgs-rate/STXS likelihood after mapping the full model to production and decay observables |
| Resolved additional state | An additional eigenstate lies in a direct-search mass range and neighboring states are separated by more than the relevant detector resolution and physical widths | Evaluate that search's signal model for the state; do not apply a limit from a different production or decay topology |
| Unresolved or overlapping tower | Neighboring eigenstates are closer than detector resolution or have overlapping widths | Build one combined spectral template including interference; do not multiply independent single-resonance limits |
| Above direct-search reach | Additional states lie outside the published search range but below \(\Lambda\) | Use only applicable indirect/effective constraints; absence from a search window is not exclusion |
| Below a cited search range | A state lies below the direct-search threshold | Require a separate light-scalar, exotic-Higgs-decay, or other applicable likelihood before drawing a numerical conclusion |

The official CMS direct search
[CMS-HIG-24-002](https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-24-002/index.html)
provides a concrete resonance window for this contract: a neutral scalar
decaying to \(ZZ\to4\ell\), with gluon-fusion or vector-boson-fusion
production, over 130 GeV to 3 TeV and with narrow- and broad-width treatments.
It reports 95% confidence limits, not a Candidate B likelihood. In the
unmixed-mass preselection only, a level \(n\) enters this window when
\[
(130\ {\rm GeV})^2\le m_5^2+\frac{n^2}{R^2}
\le(3\ {\rm TeV})^2.
\]
Final applicability must use the mixed eigenmass, production mode, width, and
branching ratio. Graviton ADD searches, short-range tests of Newtonian gravity,
and gravitational supernova-loss bounds do not directly define \(R\) here:
this benchmark contains a non-gravitational singlet scalar coupled through the
brane Higgs operator, not a universally coupled graviton tower.

## 13. Model-specific likelihood contract

Before evaluating any data, the prediction pipeline must:

1. Construct the finite mass matrix through \(N_\Lambda\), diagonalize it,
   and record eigenmasses \(M_i\) and the orthogonal mixing matrix \(U\).
2. Identify the Higgs component of each state,
   \(\kappa_i=U_{hi}\), and verify the sum rule
   \(\sum_i\kappa_i^2=1\) for the retained finite system.
3. Under the restricted mixing-only hypothesis, predict
   \(\sigma_p(M_i)=\kappa_i^2\sigma_p^{\rm SM}(M_i)\) and
   \(\Gamma_{i\to X}=\kappa_i^2\Gamma_{\rm SM\to X}(M_i)\).
   Any cascade, invisible, bulk, or other width
   \(\Gamma_i^{\rm new}(\vartheta_V)\) must be derived and included; it may
   be set to zero only as an explicit restricted hypothesis.
4. Evaluate the 125 GeV term from a published Higgs-rate or STXS likelihood,
   such as the ATLAS Run-2 interpretations, rather than converting a reported
   uncertainty into an ad hoc Gaussian bound.
5. Evaluate each resolved additional state only with a likelihood matching its
   mass, production mode, width, and decay topology. For an unresolved tower,
   use a joint mass-spectrum template including signal--signal and relevant
   signal--background interference.
6. Correlate shared luminosity, theory, detector, and background nuisance
   parameters where the public products permit it. Do not multiply analyses
   with overlapping event samples as if independent.
7. Predefine the test statistic, confidence construction, parameter ranges,
   nuisance treatment, and coverage checks. Published upper-limit curves are
   not to be digitized or treated as a likelihood unless the collaboration
   supplies a validated reinterpretation prescription.

Schematically,
\[
\mathcal L(\Theta,\eta)=
\mathcal L_{125}\big(\text{STXS/rates}\mid\Theta,\eta\big)\,
\mathcal L_{\rm res}\big(m_{4\ell}\text{ or other spectra}\mid
\Theta,\eta\big),
\]
but this factorization is allowed only after checking event-sample and nuisance
correlations. The ATLAS Run-2
[interpretation paper](https://arxiv.org/abs/2402.05742) and
[Higgs characterization review](https://arxiv.org/abs/2404.05498) define the
Higgs-observable side of this contract. CMS-HIG-24-002 defines one direct
resonance topology and range. None is a drop-in likelihood for this KK tower.

**Original stopping point (before the Section 16 extension):** the domain and likelihood interface are
specified without choosing unsupported values. A numerical limit remains
unauthorized until the bulk potential/extra widths are closed, suitable public
statistical products are verified, and a preregistered parameter domain is
approved. No likelihood has been evaluated here.

## 14. Executed benchmark checks

**Date:** 2026-10-16. Kirk LaSalle asked that Candidate B be brought to the
same level of verification as Candidate A. The
[diagnostic script](../../tools/check_candidate_b_definitions.py) executes the
algebra of Sections 7, 8, 10, 11 and 12 on stipulated inputs and writes the
[result artifact](../../results/candidate_b_definition_checks.json). As for
Candidate A, the inputs are mathematical probes, not observations. Rounded
values \(v=246\) GeV and an unmixed \(m_h=125\) GeV exercise the formulas.
\(R\), \(m_5\), \(\Lambda\), \(\mu_4\) and \(\kappa_{\min}\) are stipulated
for the checks and are not selected, measured or fitted.

| Contract statement | Executed check | Outcome on the probe |
|---|---|---|
| Section 8 units and ledgers | SI exponent algebra; RK4 integration of the driven, damped cell with \(u_{\rm th}\) and \(u_{\rm drive}\) carried in the same state | Units agree; \(u_C+u_{\rm th}+u_{\rm drive}\) is conserved to about \(10^{-14}\) relative, for \(\Gamma_C>0\) and \(\Gamma_C=0\) |
| Entropy-sign condition | Same integration with \(\Gamma_C<0\) | Thermal entropy production becomes negative: the sign is an assumption, not a theorem |
| Section 1 of the exploration note: \(D\)-volume densities | Dimensional reduction for \(D=3,4,5,6\) | J m\(^{-D}\) becomes J m\(^{-3}\) only after integrating the extra-dimensional lengths |
| Section 7.1 mass dimensions | Exact rational arithmetic for \(D=3,4,5,6,9\) | \([\mu]=(5-D)/2\) and \([g_\xi]=2\) for every \(D\); after volume reduction, \([\mu_4]=1\) |
| Section 10 modes and brane sampling | Quadrature Gram matrix on \(S^1_R\); mode values at \(y=0\) | Orthonormal to \(4\times10^{-16}\); sine modes vanish at the brane; each cosine mode couples with \(\sqrt2\mu_4\) |
| Projection versus bulk coincidence | Same \(\mathbf x\), different \(y\) | Equal projection, distinct bulk points; a sine profile has zero brane overlap energy despite off-brane support |
| Signed overlap | \(u_{\rm ov}\) for \(h<0\) and \(h>0\) | Both signs occur, so \(u_{\rm ov}\) is not a probability or entropy |
| Section 11 stability envelope | Eigenvalues of the truncated mass matrix (\(N_\Lambda=4\)) at 0.99 and 1.01 times the Schur bound | Lowest eigenvalue changes sign at the bound: the envelope is exact for this tree-level matrix |
| Infinite-tower limit | Finite sum with \(N_\Lambda=19\,999\) versus \(\pi R\coth(\pi m_5R)/m_5\); \(\mu_5=\sqrt{2\pi R}\,\mu_4\) | Relative difference \(6\times10^{-5}\), decreasing with \(N_\Lambda\); both bound forms agree; the bound tends to zero with \(m_5\) |
| Low-energy operator | \(\tfrac12 b^{\mathsf T}M_\phi^{-1}b\) versus \(\tfrac12\mu_4^2S_{\rm stab}\) | Agree to rounding |
| Perturbative mixing | \((1+\epsilon_{\rm KK})^{-1/2}\) versus exact diagonalization | Agree to \(10^{-7}\) at weak-mixing ratio 0.015; \(\sum_i\kappa_i^2=1\) |
| Near degeneracy | \(m_5=126\) GeV, \(\mu_4=1\) GeV, ratio 0.98 | Perturbative formula is refused; if forced it gives \(\kappa_V=0.714\) against the exact 0.853, and two states share the Higgs component |
| \(\kappa_{\min}\) envelope | Invert at the stipulated \(\kappa_{\min}=0.99\) | The perturbative \(\kappa_V\) returns 0.99 exactly; exact diagonalization gives 0.990, and the Higgs-like eigenmass moves from the unmixed 125 GeV to about 109 GeV |
| CMS 4-lepton window | Unmixed-mass preselection | Levels 0–2 enter 130 GeV–3 TeV; this is preselection only |
| Section 7.3 paired exchange | Homogeneous zero mode and Higgs with \(S_{\rm int}=-\mu_4\phi\mathcal O_H\) | \(\dot E_\Sigma=+\mu_4\mathcal O_H\dot\phi\) and \(\dot E_\phi=-\mu_4\mathcal O_H\dot\phi\) hold; total drift \(10^{-8}\) relative; the exchange reverses direction hundreds of times; time reversal returns the initial fields to \(5\times10^{-8}\) GeV |
| Boundedness of the zero-mode truncation | \(V=\lambda(\mathcal O_H+\mu_4\phi/2\lambda)^2+(m_5^2/2-\mu_4^2/4\lambda)\phi^2\) | Bounded below for \((\mu_4v)^2\le m_h^2m_5^2\); equality has a flat direction and is excluded by the strict positive-mass condition |

These checks establish internal consistency and executable formulas. They do
not show that the extra dimension, brane, or portal exists, and they do not
constrain any physical parameter. The exchange integration is a homogeneous
benchmark ODE, not a collision simulation or data test. The shift in the
Higgs-like eigenmass means that matching the observed 125 GeV state requires
solving for the unmixed parameter; using 125 GeV directly is only a probe.

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_candidate_b_definitions.py
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model\test_candidate_b_definitions.py -q
```

## 15. Decision-ready outcome

**What succeeds:** within its stated assumptions, Candidate B now has an
executable and internally consistent chain. The chain runs from the
fixed-volume local cell, through dimensionally consistent portal couplings, an
explicit one-circle reduction, exact stability and controlled mixing envelopes,
to a paired energy exchange whose ledgers close.

**What fails under stated assumptions:** the entropy-production sign does not
survive \(\Gamma_C<0\). Perturbative mixing fails near a Higgs--KK degeneracy.
The minimal benchmark cannot pair a massless zero mode with a nonzero portal
coupling. The reversible portal does not by itself supply damping, thermal
entropy production, or an energy origin.

**What remains open:** whether the physical extra dimensions have this
geometry; the entropy subsystem, coarse-graining and reference; complete
heavy-state widths beyond the scalar-pair calculation; a preregistered numerical
inference domain; and a qualified model-specific likelihood. Section 16 now
closes a restricted tree-level potential and supplies a testable Higgs-rate
prediction, not a general entropy or collision model.

**Next review after selection:** Section 16 records the first preregistered
public-data check. Both A and B are selected by Kirk; B is active. The checks
in this section themselves confer no empirical support.

### Verification status

The focused Candidate B suite, the collision-specification suite, and the
knowledge-graph checks pass. The new diagnostic and test files pass Ruff, and
the diagnostic script passes a focused mypy check. These checks validate
calculations and record integrity, not new physics.

## 16. Selected research program and first test

**Date:** 2026-10-16. Kirk LaSalle made B a selected candidate alongside A,
with B active, and asked that the four open items be begun and B be tested
against real data. This section closes the items only for the restricted
model approved in Section 13's decision record. It does not close them for
Candidate B in general.

### 16.1 Closures for the restricted model

**Bulk potential.** The bulk scalar has a quadratic, tree-level potential with
no bulk self-interaction. In the basis \((h,\phi_0,\phi_{1c},\dots,\phi_{Nc})\)
the mass matrix has diagonal entries \(m_{h0}^2\) and \(m_5^2+n^2/R^2\), and
off-diagonal entries \(v\mu_n\) with \(\mu_0=\mu_4\) and
\(\mu_{n\ge1}=\sqrt2\mu_4\). The secular equation fixes the unmixed Higgs
parameter so that one eigenvalue is exactly \(M_H^2\):
\[
m_{h0}^2=M_H^2+v^2\mu_4^2S_1,\qquad
\kappa^2=\frac1{1+v^2\mu_4^2S_2},\qquad
S_k=\sum_{n=0}^{N_\Lambda}\frac{w_n}{(m_n^2-M_H^2)^k},
\]
with \(w_0=1\) and \(w_{n\ge1}=2\). Because every \(m_n>M_H\), the matched
state is the lightest. The universal suppression is
\(\kappa_V=\kappa_F=\kappa\le1\), so
\(\mu_4^{\max}=\sqrt{(\kappa_{\rm lo}^{-2}-1)/(v^2S_2)}\).

**Decay widths.** The cubic couplings follow from
\(\partial^3V/\partial h^3=3m_{h0}^2/v\) and
\(\partial^3V/\partial h^2\partial\phi_n=\mu_n\), rotated to the mass basis.
Each heavy state receives tree-level two-scalar widths and Higgs-fraction-scaled
on-shell \(WW\), \(ZZ\) and \(t\bar t\) widths. The sum is a **lower bound**:
\(b\bar b\), \(gg\), \(\gamma\gamma\), off-shell and loop channels are omitted.

**Parameter range.** The
[preregistration](../../knowledgebase/candidate_b_restricted_test_preregistration.json)
fixes \(R^{-1}\in\{10,100,1000\}\) GeV, \(m_5\in\{150,300,600,1200\}\) GeV and
\(\Lambda=3000\) GeV. It also fixes the constants, flags and outcome rules. It
was frozen at SHA-256 `69458ad7…7f6d` before any contour coordinate was
retrieved, and the evaluation script refuses to run if that hash changes.

**Public data.** The ATLAS Run-2 combination (Nature 607 (2022) 52), Figure 4
observed \((\kappa_V,\kappa_F)\) contour,
[HEPData table 10.17182/hepdata.130266.v1/t4](https://doi.org/10.17182/hepdata.130266.v1/t4).
The table and the original submission archive are pinned by SHA-256 in the
data catalog. The file inside the archive is byte-identical to the
downloaded table. The table holds two closed loops. The outer loop contains the
inner one, and the area ratio of 2.65 is close to the Gaussian two-parameter
value of 2.61, so the outer loop is identified as the observed 95% region.

### 16.2 Outcome

The statistic is the part of the diagonal \((k,k)\), \(0\le k\le1\), inside
the observed 95% loop. The result is **compatible with limit**:
\(\kappa_{\rm lo}=0.9759\). The SM point \((1,1)\) is inside, and the contour
vertex spacing at the crossing is 0.005.

| \(R^{-1}\) (GeV) | \(m_5\) (GeV) | \(N_\Lambda\) | \(\mu_4^{\max}\) (GeV) | \(m_{h0}\) (GeV) | lightest new state (GeV) | its \(\Gamma/M\) lower bound | conventions failed at \(\mu_4^{\max}\) |
|---|---|---|---|---|---|---|---|
| 10 | 150 | 299 | 1.73 | 127.8 | 150.0 | 0 | none |
| 10 | 300 | 298 | 10.3 | 150.5 | 300.0 | 2.4e-6 | none |
| 10 | 600 | 293 | 32.6 | 214.1 | 600.0 | 1.7e-6 | none |
| 10 | 1200 | 274 | 95.8 | 352.0 | 1200.0 | 8.1e-7 | \(\lvert\mu_5/\sqrt\Lambda\rvert<1\), \(\lambda_0\le1\) |
| 100 | 150 | 29 | 5.28 | 127.6 | 150.8 | 0 | none |
| 100 | 300 | 29 | 32.6 | 150.5 | 301.2 | 3.3e-4 | none |
| 100 | 600 | 29 | 103 | 214.1 | 601.0 | 5.2e-4 | none |
| 100 | 1200 | 27 | 303 | 352.1 | 1200.7 | 4.4e-4 | \(\lvert\mu_5/\sqrt\Lambda\rvert<1\), \(\lambda_0\le1\) |
| 1000 | 150 | 2 | 6.22 | 126.5 | 151.1 | 0 | none |
| 1000 | 300 | 2 | 67.2 | 141.3 | 306.1 | 2.1e-3 | none |
| 1000 | 600 | 2 | 292 | 202.0 | 612.3 | 0.011 | narrow width |
| 1000 | 1200 | 2 | 956 | 347.5 | 1215.3 | 0.024 | \(\lvert\mu_5/\sqrt\Lambda\rvert<1\), narrow width |

Using \(M_H=125.2\) GeV instead of 125.09 GeV changes every \(\mu_4^{\max}\) by
at most 0.4%. Each bound is the coupling at which the predicted
\((\kappa,\kappa)\) reaches the published 95% joint region. It is not a
likelihood-based one-parameter interval. A failed convention flag marks where
the restricted model's own working assumptions stop holding; it is not an
experimental exclusion.

### 16.3 Interpretation and limits

The restricted model predicts \(\kappa\le1\) and contains the SM decoupling
limit \(\mu_4\to0\). This data set can therefore bound \(\mu_4\) but cannot
refute the restricted model. The outcome is conditional compatibility, not
evidence for Candidate B, its extra dimension or its portal. No likelihood,
p-value or one-parameter confidence interval has been evaluated.

Deferred: the CMS-HIG-24-002 comparison for heavy scalars decaying to \(ZZ\),
which must match production, width and topology. Also deferred: a correlated
STXS likelihood, and loop and off-shell heavy-state widths. Section 17 takes
up the CMS comparison and a Higgs-rate likelihood.

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\prepare_candidate_b_test.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\evaluate_candidate_b_atlas_contour.py
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model\test_candidate_b_restricted_test.py -q
```

The raw HEPData files are git-ignored. HEPData blocks scripted downloads, so
they were retrieved through a browser session and checked against the
catalog hashes. Without them, the reproduction test is skipped and the
committed artifacts are still checked for consistency.

## 17. Extended tests: Higgs-rate likelihood and CMS direct-resonance comparison

**Date:** 2026-10-16. Kirk LaSalle asked to take B further with the two tests
proposed after Section 16. Both apply to the restricted model of Section 16
only, on the same grid.

### 17.1 Preregistration and theory inputs

The [extended preregistration](../../knowledgebase/candidate_b_extended_test_preregistration.json)
inherits the parent model, grid and constants unchanged. It was frozen at
SHA-256 `fc23f2e3…90a2` before the ATLAS likelihood scans or any CMS limit
value, observed or expected, were read. It discloses that the ATLAS headline
\(\mu=1.05\pm0.06\) was already known, so test A is not blind to its
approximate outcome.

The heavy-state prediction adds one assumption to the restricted model: each
eigenstate \(a\) with Higgs component \(u_a\) is produced and decays like an
SM-like Higgs of the same mass, scaled by \(u_a^2\). Its width also includes
the tree-level two-scalar widths of Section 16:
\[
\sigma_{p,a}=u_a^2\sigma_p^{\rm SM}(M_a),\qquad
\Gamma_a=u_a^2\Gamma^{\rm SM}(M_a)+\Gamma_{a\to SS},\qquad
{\rm BR}_{ZZ,a}=\frac{u_a^2\Gamma^{\rm SM}(M_a){\rm BR}^{\rm SM}_{ZZ}(M_a)}{\Gamma_a}.
\]
The SM-like inputs are the LHC Higgs Cross Section Working Group ggF and VBF
cross sections (Yellow Report 4) and the SM total width and \(ZZ\) branching
ratio (Yellow Report 3 update). They were
[extracted](../../tools/extract_candidate_b_theory_inputs.py) into the
[pinned theory table](../../knowledgebase/candidate_b_theory_inputs.json),
SHA-256 `bc2ec81c…7833`. The width table ends at 1 TeV. Heavier states use a
tree-level width scaled for continuity at 1 TeV, and are labelled
extrapolated and kept out of the primary result.

### 17.2 Test A: global signal-strength profile likelihood

The restricted model scales every 125 GeV production and decay rate by
\(\mu=\kappa^2\le1\) with SM kinematics. That is exactly the global
signal-strength hypothesis, so the ATLAS observed \(-2\ln\Lambda(\mu)\) scan
with all systematics (HEPData ins2104706 v1, Aux. Figure 8) applies directly.
The rule tests the family first: \(q_{\rm family}=L(1)-L(\hat\mu)\) for
\(\hat\mu>1\), with a half-\(\chi^2\) null. It then takes the first crossing
\(q(\mu)=2.706\) below \(\mu_{\rm ref}=\min(\hat\mu,1)\).

**Outcome: compatible with limit.** \(\hat\mu=1.054\) and
\(q_{\rm family}=0.752\). The lower limit is \(\mu_{\rm lo}=0.9420\), giving
\(\kappa_{\rm lo}=0.97059\). For comparison, the unbounded one-sided limit is
0.9544 and the two-sided limit is 0.9363. The
[script](../../tools/evaluate_candidate_b_higgs_rate_likelihood.py) also
applies the primary rule to scans with theory or systematic uncertainties
fixed. These understate the uncertainty and are never the result. The
statistical-only scan would be labelled incompatible
(\(q_{\rm family}=3.12\)), which shows that the conclusion depends on the
published systematic uncertainties. The bound is weaker than the
Section 16 contour value 0.97591 at every grid point, so the contour remains
the stronger Higgs-rate bound. It is an asymptotic one-sided 95% CL bound at
fixed \((R,m_5,\Lambda)\), not a joint interval over the grid.

### 17.3 Test B: width-matched CMS-HIG-24-002 comparison

CMS-HIG-24-002 (HEPData ins3161000 v1) gives observed and expected 95% CL
upper limits on \(\sigma\times{\rm BR}(X\to ZZ)\) for ggF and VBF separately.
It covers 130 GeV to 3 TeV, with width hypotheses NWA, 1, 10 and 100 GeV.
The rules were fixed before any limit value was read:

- For each state, take the bracketing width hypotheses, and in each the
  bracketing table masses. The primary limit is the largest observed limit
  among these points, a conservative envelope.
- A state is covered if \(130\le M\le3000\) GeV and \(\Gamma\le100\) GeV.
  The primary result uses covered states with tabulated theory
  (\(M\le1\) TeV).
- \(R(\mu_4)\) is the largest ratio of predicted to excluded
  \(\sigma\times{\rm BR}\) over states and production modes. Each mode is
  compared alone. The scan has 100 steps up to \(\kappa=0.90\), and the first
  exclusion is refined by bisection.

| \(R^{-1}\) (GeV) | \(m_5\) (GeV) | contour \(\mu_4^{\max}\) | likelihood \(\mu_4^{\max}\) | CMS outcome | CMS \(\mu_4^{\rm excl}\) | combined bound | binding |
|---|---|---|---|---|---|---|---|
| 10 | 150 | 1.73 | 1.91 | no exclusion in scan | — | 1.73 | contour |
| 10 | 300 | 10.3 | 11.5 | no exclusion in scan | — | 10.3 | contour |
| 10 | 600 | 32.6 | 36.2 | no exclusion in scan | — | 32.6 | contour |
| 10 | 1200 | 95.8 | 106 | not covered | — | 95.8 | contour |
| 100 | 150 | 5.28 | 5.86 | exclusion within rate-allowed region | 5.02 | 5.02 | CMS |
| 100 | 300 | 32.6 | 36.2 | exclusion above rate bounds | 45.7 | 32.6 | contour |
| 100 | 600 | 103 | 114 | no exclusion in scan | — | 103 | contour |
| 100 | 1200 | 303 | 336 | not covered | — | 303 | contour |
| 1000 | 150 | 6.22 | 6.90 | exclusion within rate-allowed region | 4.91 | 4.91 | CMS |
| 1000 | 300 | 67.2 | 74.5 | exclusion above rate bounds | 69.2 | 67.2 | contour |
| 1000 | 600 | 292 | 324 | exclusion within rate-allowed region | 281 | 281 | CMS |
| 1000 | 1200 | 956 | 1061 | not covered | — | 956 | contour |

All values are in GeV. The combined bound is the smallest of the three. It is
an intersection of separate 95% CL-type constraints, not a joint statistical
combination.

- **CMS stronger (3 points).** At \(m_5=150\) GeV the leading state is the
  150.7 GeV level, with \(u^2=0.030\) and \({\rm BR}_{ZZ}=0.082\), produced by
  ggF. At \((1000,600)\) it is the 611 GeV state, with \(\Gamma=6.4\) GeV and
  \({\rm BR}_{ZZ}=0.21\).
- **Above rate bounds (2 points).** At \((100,300)\) the onset is a step of the
  envelope rule. The 321 GeV state crosses a CMS table mass, the bracketing
  ggF limit drops from 0.075 to 0.050 pb, and \(R\) jumps from 0.91 to 1.36.
- **Variants.**
  - The mass-interpolation variant excludes earlier at every excluded point.
  - At \((1000,300)\) the expected median would exclude from 55 GeV, below the
    rate bound, so the observed limit there is weaker than expected.
  - At \((1000,600)\) the expected median excludes only from 329 GeV.
- **Not covered (\(m_5=1200\) GeV).** Every heavy state lies above the 1 TeV
  tabulated theory range. The labelled extrapolated variant reaches at most
  \(R=0.125\).
- **Heuristic tower clusters.** A secondary comparison sums nearby narrow
  states and treats them as one resonance of width 10 or 100 GeV. It exceeds
  a limit below the rate bound at 7 points, including \(R^{-1}=10\) GeV with
  \(m_5=150\) and 300 GeV. It is labelled heuristic and is not the result:
  discrete narrow states are not one broad resonance, and interference is
  neglected.

### 17.4 Interpretation and limits

\(\mu_4=0\) is the SM limit and is always allowed, so both tests bound the
restricted coupling and cannot refute the restricted family. Neither is
evidence for Candidate B, its extra dimension or its portal. The likelihood
contract of Section 13 is now partly evaluated. The global-\(\mu\) profile
likelihood has been used. The STXS likelihood with correlations has not, and
no direct-resonance likelihood has been built: the CMS upper limits are
compared state by state and are not converted into a likelihood.

Caveats:

- Interference with the \(gg\to ZZ\) continuum, the off-shell 125 GeV tail and
  among nearby tower states is neglected.
- Each production mode is compared alone.
- Signal acceptance is assumed to match the CMS SM-like scalar hypothesis.
- Heavy-state scalar widths are tree level.
- Statistics are asymptotic.

Still deferred: the STXS likelihood, loop and off-shell widths, interference,
a joint ggF + VBF treatment, and a published direct-resonance statistical
model. Any wider grid or added correction needs a new frozen preregistration.

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\evaluate_candidate_b_higgs_rate_likelihood.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\evaluate_candidate_b_cms_resonance.py
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model\test_candidate_b_extended_tests.py -q
```

The CMS run takes about three and a half minutes, mostly for the
\(R^{-1}=10\) GeV towers of about 300 states. The test file checks that the
pinned theory table reproduces from the HXSWG pages without rewriting it. The
HXSWG pages, the ATLAS archive and the CMS archive are git-ignored and pinned
by SHA-256 in the data catalog. Without them, the reproduction tests are
skipped.
