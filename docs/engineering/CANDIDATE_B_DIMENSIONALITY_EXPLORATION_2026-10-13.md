# Candidate B: dimensionality, co-location and entropy

**Date:** 2026-10-13  
**Direction:** Kirk LaSalle requested that Candidate B exploration begin and
that the dimensionality of \(X\) receive greater emphasis.  
**Status updated 2026-10-16:** Candidate B is selected and active. Candidate A
also remains selected, but paused; only one is worked at a time. Kirk has
approved a restricted quadratic Higgs-portal test, not established a physical
event, zero entropy, or a validated prediction.

This note is an author-directed follow-up to the
[Candidate B energy-exchange specification](../EMRF_COLLISION_CANDIDATE_SPECIFICATION.md#5-candidate-b-a-separately-budgeted-relaxation-channel).
Candidate B remains an incomplete, conditional effective proposal, now selected
for active research rather than merely retained as an alternative. The separate
[draft model contract](CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md) records
this boundary and the author-review questions. The purpose here is to make the
spatial domain and the proposed co-location question mathematically explicit
before interpreting dynamics or observational data. Its
[selected first-test extension](CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#16-selected-research-program-and-first-test)
now defines the potential and rate observable and records public-data retrieval
requirements. The original dimensionality and entropy cautions below still apply.

## 1. Make dimensionality explicit

Use

$$X \in \mathcal{M}^{D}, \qquad D=3+d_{\rm ext}, \qquad
p=(X,t),$$

where \(X\) is a point in the spatial manifold, \(D\) is the number of spatial
dimensions, \(d_{\rm ext}\) is the number of additional spatial dimensions,
and \(t\) parameterizes change. For example,

$$X=(x,y,z,d_0,d_1,\ldots,d_{d_{\rm ext}-1}).$$

Kirk LaSalle specified on 2026-10-13 that the additional \(d_i\) are physical
spatial dimensions. Their metric, coordinate ranges, topology, and coupling to
fields remain to be specified. Writing \(X\in\mathcal{M}^D\) makes the
dimensionality of its domain explicit; \(D\) is not itself another coordinate.
For this first pass, Kirk also specified that entropy means thermodynamic
entropy \(S(X,t)\), with no zero value assumed. It remains a state field, not
an axis of \(X\); its subsystem and reference convention remain open.

For Candidate B, dimensionality affects more than notation. Its existing local
example uses energy *per three-dimensional physical volume* (J m\(^{-3}\)).
If the energy is local in all \(D\) dimensions, the corresponding density is
per \(D\)-dimensional volume (J m\(^{-D}\)); the coefficients in the existing
three-dimensional example then have different units. To compare with a
three-dimensional observation, a model must specify whether and how the extra
dimensions are integrated out, including the metric volume measure and any
compactification or boundary conditions.

Accordingly, every proposed \(C(X,t)\), field, or energy transfer should declare
which domain it lives on and whether its density is \(D\)-dimensional or
effective three-dimensional. No such declaration is yet part of the Candidate
B example.

## 2. Turn the bar-and-stool image into a limited question

The joke suggests a question about whether several distinct excitations or
fields can have support in the same region. A careful mathematical shorthand
for that question is:

$$\bigcap_{a\in\{q,\nu,\gamma,\mathrm{waves}\}}
\operatorname{supp}(\Psi_a(\cdot,t))\ \cap\ B \ne \varnothing,$$

where \(B\subset\mathcal{M}^{D}\) is a specified region and \(\Psi_a\) denotes
the model's representation of each species or field. This is only a
co-location criterion; it does not say that the excitations are identical,
that they occupy one indivisible object, or that they have a common entropy.
In quantum field theory, “a quark,” “a neutrino,” and “a photon” require a
specified state and measurement context; classical support functions are
illustrative notation, not a complete quantum description.

There is also a dimensionality test hidden in the image. Equality after
projection onto ordinary three-space,
\(\pi(X_1)=\pi(X_2)\), need not imply equality in the full domain,
\(X_1=X_2\), if the points differ along an additional spatial coordinate.
Thus a claim of “the same space” must say whether it means the same observed
three-dimensional location or the same point in \(\mathcal{M}^{D}\).

Kirk has specified that co-location is intended to enter Candidate B's
exchange law. The stool remains an analogy, not a boundary condition, capacity
constraint, or physical data source. It motivates asking what fields overlap
and on what domain; it does not identify the physical interaction that turns
overlap into energy transfer. That interaction must be stated separately.

## 3. Co-location does not imply zero entropy

The coincidence or overlap of field support alone does not determine an
entropy. Here the entropy concept is thermodynamic \(S\), as specified for this
first pass. Any entropy value still requires the system or subsystem, its state
or ensemble, the coarse-graining, and the reference convention. In particular:

* \(S\), the entropy state, is not the same quantity as \(\sigma\), the local
  entropy-production rate.
* A zero value of \(S\) is convention- and model-dependent; it is not implied
  by several fields sharing a location.
* Reversible change may have \(\sigma=0\); irreversible entropy production is
  not automatically a transition to \(S=0\).
* A proposed geometric or information entropy is not automatically the gas's
  thermodynamic entropy or a black-hole entropy.

Candidate B's existing conditional relation

$$\dot{s}_{\rm th,vol}=\frac{\Gamma_C\dot{\xi}^{\,2}}{T}\geq 0$$

follows only under its stated local-equilibrium and dissipative assumptions,
with \(T>0\) and \(\Gamma_C\geq0\). It concerns thermal entropy production in
that example. It does not establish an absolute entropy value, an “entropy-zero
condition,” or a generalized entropy law for the full spatial manifold.

Therefore the proposed “moment before a new condition” remains undefined.
Before assigning it an entropy value, define the initial and final states,
their entropy measure, the relevant system boundary, and the evolution that
connects them. A change in field configuration is not by itself evidence that
the entropy becomes zero.

## 4. Data needed for the exploration

The original exploration first required definitions and controlled mathematical
examples. Those checks now support a restricted Higgs-rate test, which has been
run against the public ATLAS joint coupling contour (contract section 16).
The broader thermodynamic or cluster application still needs the definitions below.

| Input | Required declaration | Why it is needed |
|---|---|---|
| Spatial domain | \(D\), topology, coordinates and their units | Establish what \(X\) denotes |
| Extra dimensions | Physical interpretation, coordinate ranges, metric and boundary/compactification conditions | Decide whether fields can differ outside the observed 3D projection |
| Fields and state | Species/field variables, state or ensemble, and meaning of “field waves” | Give co-location a precise model meaning |
| Co-location rule | Full-manifold coincidence versus projected 3D overlap; point versus finite region | Define the intended input to the exchange law |
| Physical interaction | Fields/species involved, coupling, and energy source linking overlap to transfer | Co-location is not itself a mechanism |
| Entropy | Thermodynamic \(S\) for the first pass; subsystem, coarse-graining and reference still required | Determine whether an absolute value such as \(S=0\) is meaningful |
| Compression | Definition and units of \(C\), \(C_0\), and \(\xi=C/C_0\) | Connect the spatial state to Candidate B |
| Energy accounting | Density measure, source/reservoir, transfer, momentum, and field backreaction | Test conservation and dimensional consistency |
| Evolution and observables | Equations, initial/boundary data, and an independently measurable consequence | Make a prediction falsifiable rather than descriptive |

An initial toy calculation may vary the declared dimension \(D\), metric
measure, and field-support overlap while keeping the entropy definition fixed.
Its purpose would be to expose which conclusions depend on dimensionality or
projection. Such a calculation must be labeled illustrative and must not be
presented as measured physics.

Real observational data become appropriate only after a specific system,
physical coupling, units, conservation law, and distinguishable prediction are
defined. For a cluster application, the existing
[Candidate B data-readiness specification](../EMRF_COLLISION_CANDIDATE_SPECIFICATION.md#7-data-readiness-specification-no-new-bulk-download-or-reduction)
is a starting checklist, not evidence for this bar analogy. No data are
identified here as showing the proposed co-location or an entropy-zero event.

## 5. Explicit geometry and dimensional reduction benchmark

To make the previous open geometry gate calculable without claiming that
Nature uses this geometry, take the following **working benchmark**:

* One additional spatial dimension, \(d_{\rm ext}=1\), with spatial domain
  \(\mathbb R^3\times S^1_R\). The coordinate \(y\) is periodic,
  \(y\sim y+2\pi R\), and \(D=4\).
* A flat product metric
  \(ds^2=\eta_{\mu\nu}dx^\mu dx^\nu+dy^2\), with signature
  \((-+++ +)\). Curvature, warping, gravity backreaction, and stabilization
  dynamics for \(R\) are omitted in this first reduction.
* Standard Model fields are localized on a fixed 3+1-dimensional brane at
  \(y=0\). The compression scalar propagates on the full
  \(\mathbb R^{3,1}\times S^1_R\) bulk. This idealized localization is an
  assumption for the worked portal, not a consequence of the extra dimension.

For any field point \(X=(\mathbf x,y)\), the observable projection is
\(\pi(X)=\mathbf x\). Points with the same \(\mathbf x\) but different \(y\)
are distinct bulk points. The brane portal samples the bulk field specifically
at \(y=0\); projected three-space coincidence by itself does not create a
coupling at another value of \(y\).

Write a real periodic bulk scalar in canonically normalized modes:

$$
\phi(x,y)=\frac{1}{\sqrt{2\pi R}}\left[
\phi_0(x)+\sqrt{2}\sum_{n=1}^{\infty}
\left(\phi_n^c(x)\cos\frac{ny}{R}
+\phi_n^s(x)\sin\frac{ny}{R}\right)\right].
$$

For a flat bulk mass \(m_5\), the four-dimensional masses are
\(m_n^2=m_5^2+n^2/R^2\). At the brane, the sine modes vanish. The
four-dimensional observer therefore sees a zero mode and a tower of cosine
modes coupled to the localized Higgs operator; the tower cannot in general be
replaced by only the zero mode. At energies below \(1/R\), higher modes can be
integrated out only if their induced effects are also negligible or included
in the resulting effective operators.

With this choice, the reduced brane coupling and a cutoff-dependent KK-tower
envelope are derived in the
[model contract](CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#10-explicit-benchmark-geometry-and-kk-reduction).
The radius \(R\), bulk mass \(m_5\), and cutoff \(\Lambda\) remain parameters;
this benchmark does not assign them measured values. The envelope separates a
tree-level stability condition from a perturbative Higgs-state mixing
condition. Neither is a model-specific confidence limit. A phenomenological
constraint still requires a dedicated treatment of the KK spectrum, widths,
near-degenerate modes, and experimental likelihood.

The calculable domain of this benchmark is now explicit:
\(R>0\), \(m_5>0\), and a finite EFT cutoff
\(\Lambda\ge\max(m_5,m_h)\). Perturbative Higgs-state mixing additionally
requires every retained Higgs--KK mass gap to be large compared with its
off-diagonal mixing. This defines where the formulas may be used without
choosing numerical values for physical parameters that Kirk has not selected.

The [source-bounded domain and likelihood contract](CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#12-source-bounded-parameter-domain)
then partitions points by what an experiment can resolve: the observed 125 GeV
state, isolated additional resonances, unresolved or overlapping tower modes,
and states outside a cited search range. The official CMS direct
\(H\to ZZ\to4\ell\) search covers 130 GeV to 3 TeV for its stated production
and width hypotheses. This range defines where that particular search may be
considered; it does not select \(R\), \(m_5\), or \(\Lambda\), and it does not
constrain a state with a different topology. Gravitational extra-dimension
bounds are not transferred to this non-gravitational brane-Higgs portal.

## 6. Exploratory gates

1. **Notation gate:** state \(D\), \(X\in\mathcal{M}^D\), and the status and
   units of every additional coordinate.
2. **Projection gate:** define what “same space” means in the full manifold and
   in any observable three-dimensional projection.
3. **Entropy gate:** select and define the entropy measure, subsystem,
   coarse-graining, and reference before using the value zero.
4. **Candidate B closure gate:** extend the local energy balance with
   dimensionally consistent measures, a physical drive/source, momentum
   accounting, and the relevant entropy balance.
5. **Prediction gate:** only after the preceding gates, specify data,
   uncertainty, controls, and an outcome that could distinguish Candidate B
   from standard physics.

Passing a gate means the proposal is better specified; it is not evidence that
the proposal is physically true.

**Executed checks (2026-10-16):** the notation, projection, and closure-gate
algebra above is now executed on stipulated benchmark inputs. See the
[executed benchmark checks](CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#14-executed-benchmark-checks)
and the [decision-ready outcome](CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#15-decision-ready-outcome).
These calculations confirm internal consistency. They do not pass the entropy
or prediction gates.

## 7. Kirk LaSalle's joke, recorded verbatim

The following is the complete passage Kirk LaSalle submitted on 2026-10-13,
preserved verbatim as requested, including its spelling, punctuation, and
spacing. The joke and its authorship are credited to Kirk LaSalle.

```text
A Quark, a neutrino, a photon, and many field waves with their, whatever the cat dragged in, walk into a bar (I know, it gets better). There is only one bar stool, and of course, they all sit there (let's take it up a notch)  and somebody flatulates; was it one of them or all of them? who knows ?   LOL.  (and that is a grade A physics fart joke in disguise). As bad as that joke is I will take credit for it. ,only if this is documented in its entirety.
```

The wording is preserved as a creative analogy. It is not a scientific claim,
observation, or evidence for Candidate B.
