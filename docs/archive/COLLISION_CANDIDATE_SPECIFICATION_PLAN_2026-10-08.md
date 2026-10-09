# Next phase: faithful collision-focused thermodynamic candidate formulations

> **Archived planning record — completed and superseded.**
> This plan produced
> [the collision candidate specification](../EMRF_COLLISION_CANDIDATE_SPECIFICATION.md),
> [the Candidate A functional comparison](../EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md),
> and the qualified claim ledger at
> `knowledgebase/thermodynamic_collision_candidates.json` in commit `7f5e4a4`.
> Kirk selected Candidate A on October 8, 2026. This record is valuable as
> process provenance, but it is not evidence that either candidate is physically
> validated and does not authorize a new collision mechanism or solver.

## Problem and approach

The archive recovery clarifies the intended explanatory direction: a geometric/
information state described by C may underlie matter and interactions, with
macroscopic thermodynamics downstream. A distinct geometric/information entropy
may also participate in the deeper description. Current static collision code
does not implement that causal chain.

The next deliverable is a **reviewable mathematical specification**, not another
simulation that assumes the desired result. Establish the known-physics energy
and entropy budget, formulate at most two clearly attributed candidate approaches,
identify testable differences, and stop for Kirk's review before implementing any
new physical mechanism.

The previous research plan is retained in
`files/completed_real_data_recovery_plan.md` in session storage. Repository sources,
historical evidence, published drafts and existing working changes remain intact.

## Decisions confirmed with Kirk

1. Start with compression dynamics and the collision example, not the multi-star
   geometry experiment or a general software-cleanup project.
2. The first physical target is **energy transfer and entropy production during
   a collision**. Deriving all thermodynamic laws remains a separate open claim.
3. Where equations are missing, prepare explicitly labelled candidates for review.
   Do not silently assign a new equation to Kirk or present it as recovered theory.
4. Stop for Kirk's review **before implementing a new mechanism**. Approval of
   this plan authorizes the specification/research phase only.
5. Numerical mathematics may check candidate consequences, but only authentic
   observations can supply physical evidence. No synthetic observational catalogues,
   imposed entropy maps, target-normalized lensing maps or programmed success claims.
6. No repository commits, publication uploads, external contact, IBM Quantum jobs,
   new simulations or cloud use in this phase.

## Evidence used to define the phase

- `knowledgebase/antigravity_recovered_theory.md` preserves the two entropy roles,
  C_G/C_E/C_S/C_GSE families, matter ansatz, U hypothesis space and multi-star design.
- `docs/ANTIGRAVITY_RECOVERY_AUDIT.md` and its source manifest qualify attribution:
  recovered AI drafts, reported author quotations, limited direct user snippets,
  code snapshots and execution records are distinct evidence types.
- `docs/T03_ENTROPY_ONTOLOGY_DECISION_2026-10-07.md` explicitly leaves entropy
  evolution, production and coupling unresolved.
- `knowledgebase/action_principle_derivation.md` contains a canonical entropy-field
  sketch; other records propose a C-field action. These are different formulations,
  not an already unified dynamical theory.
- `emergent_matter_model/bullet_cluster_stress_test.py` now correctly labels its
  generated shapes, assigned entropy and normalized proxy as an illustration.
  Its beta and exponent 2.2 are not accepted as the next theory's constants.
- The attached terminal-output snapshot is an archive file listing, not an
  additional derivation. It remains read-only.

## First deliverables

1. `docs/EMRF_COLLISION_CANDIDATE_SPECIFICATION.md`
   - Plain-language interpretation followed by mathematical definitions.
   - Known-physics baseline, two candidate approaches, consistency findings,
     assumptions, discriminating observables and review questions.
2. `knowledgebase/thermodynamic_collision_candidates.json`
   - Small source/claim ledger: recovered, established baseline, newly proposed,
     derived conditionally, inconsistent, or unresolved.
   - Source locators and explicit author/AI attribution.
3. A narrowly scoped graph-memory update pointing to proposed candidates with
   **not approved / not implemented / not empirically validated** labels.
4. An updated top-down regime assessment only where this phase changes a specific
   blocker. No new paper, broad rewrite or replacement of historical artifacts.

## Todos

### 1. Fix the interpretation and variable dictionary

Trace each foundational statement to the recovered source before translating it.
Record conflicts as alternatives rather than silently reconciling them.

Define, or explicitly leave open:

- C, C0 and the observed matter quantity M: total mass, mass density, energy density,
  or a state descriptor are not interchangeable.
- Thermodynamic entropy S_th / entropy density s_th versus a distinct candidate
  geometric/information quantity S_geom. The latter notation is a proposed
  bookkeeping distinction, not an established new field.
- Temperature, pressure, internal energy, bulk kinetic energy, gravitational/
  field contribution, fluxes and boundary conditions.
- The candidate system: colliding galaxy clusters with hot plasma and collisionless
  galaxies; do not substitute dust, individual galaxies, or peak positions for
  these separate physical observables.
- Whether matter creation is actually invoked in this collision mechanism.
  Do not insert mass source terms merely because the broader ontology discusses
  emergent matter; if invoked, account for corresponding energy and momentum.

Deliver an interpretation table with the original wording, proposed precise
meaning, units, source, uncertainty and whether author review is required.

### 2. Establish the standard collision energy/entropy baseline

Research primary/authoritative sources for fluid energy balance, shocks,
Rankine-Hugoniot relations, entropy production and cluster plasma measurements.
Use public search terms; do not upload private source content.

Write the baseline before adding C:

- Gravitational/bulk energy can be converted into internal energy through
  shocks, viscosity and other dissipative processes.
- Reversible adiabatic compression can heat matter without entropy production.
- Distinguish an entropy flux from local entropy generation.
- Distinguish a gravitational energy convention appropriate to the approximation
  from a claimed universal local GR gravitational-energy density.
- A prescribed moving potential can perform external work; its energy is not
  conserved in the gas alone. A self-consistent closed model must account for
  backreaction and the energy source rather than hide it.
- Distinguish thermodynamic entropy from the astrophysical entropy proxy
  K = k_B T n_e^(-2/3); specify ideal-gas/composition assumptions before mapping them.
- Cluster shocks may require electron/ion temperature and nonthermal components;
  a one-temperature equilibrium gas is an approximation, not a default truth.

State conditions under which an entropy-current equation or fluid balance is
being used. Adopting the first/second law for an effective model is not deriving
those laws from EMRF.

### 3. Formulate at most two candidate approaches

**Candidate A: geometric reformulation / null extension.**
C describes existing geometry or energy organization; standard dynamics supplies
the collision heating. Identify what would make the reformulation mathematically
equivalent, rather than claiming equivalence because one curve matches.
It may be useful without an additional prediction.

**Candidate B: explicit dynamical energy-exchange extension.**
Investigate a separately labelled C sector with a stated energy/momentum budget
and a coupling to matter. Any new action term, dissipative closure, coefficient,
entropy functional or transport rule is an **AI-proposed research ansatz**, not
Kirk's established equation.

Requirements for Candidate B:

- Specify which original C family it instantiates and why.
- Distinguish reversible exchange from irreversible dissipation. A conservative
  scalar action alone is not a derivation of irreversible entropy production.
- Account for exchange terms in both sectors so total conservation is respected.
- Explain the coarse-graining/constitutive assumptions under which nonnegative
  total entropy production follows, if it does.
- Do not force positive entropy with absolute values, clamping, or a sign choice
  made after the calculation; a positivity condition must be stated and justified.
- Track possible double counting if C is constructed from the same gravitational
  or matter energy already included in the baseline.
- Recover the chosen baseline when the new coupling is removed.
- Keep a geometrical/information entropy distinct unless a relationship to
  measured plasma entropy is actually specified.

Do not select a detailed new mechanism solely because it is easy to code. If no
candidate closes consistently, deliver the failed derivation and exact missing
equations rather than adding enough adjustable functions to match the target.

### 4. Audit consistency and theorem scope

Check dimensions, normalization degeneracy, independent parameters, source
dependencies, boundary/initial conditions and conservation.

Use only applicable analytic or numerical mathematical checks:

- Zero new coupling reduces to the reference theory.
- No dissipation does not create spurious thermal entropy.
- Reversible compression is distinguished from irreversible shocks.
- Stationary/isolated limits do not inject unexplained energy.
- An open system includes the measured or modelled boundary/external work.
- A positive-entropy claim specifies the system and coarse-graining; geometry
  or reversible motion alone does not establish an arrow-of-time theorem.
- Stability/hyperbolicity claims are not inferred just from second-order equations.

State any proposed mathematical proposition as assumptions -> conclusion ->
proof or counterexample. Separate that conditional proposition from whether
nature satisfies its assumptions. A dimensionally consistent ansatz is not a proof.

Do not introduce a new field solver, time-evolution implementation or mock-data
test suite in this phase. Existing computation may be used read-only to confirm
what is and is not implemented; any extra mathematical check must be labelled
non-empirical and must not change production physics.

### 5. Define a discriminating observable and data gate

For each viable candidate, identify what could distinguish it from standard
shock heating and collision dynamics without assuming the answer.

Prefer a narrowly defined joint observable (for example, density/temperature
jumps or an energy-budget relation with independently constrained kinematics).
Do not treat spatial separation of lensing and gas peaks alone as a new-law test.

For the selected target, list:

- Actual measured quantity, units, aperture/region, redshift and projection.
- Required density/temperature, stellar/dynamical and lensing constraints.
- Instrument response, calibration, covariance and dominant systematics.
- Which parameters are externally constrained versus fitted.
- Which observations are used for fitting versus evaluation.
- What the candidate predicts before observing the evaluation data.
- Whether the effect is identifiable or degenerate with ordinary plasma/
  astrophysical nuisance parameters.

Research public Chandra/MAST and published catalogue access as appropriate, but
do not bulk-download/reduce imaging until the observable and prediction are
specified. Record access restrictions honestly.

Lensing comparison remains gated on a derived potential/metric and absolute
observable; a normalized proxy cannot satisfy the gate. The existing SPARC,
Pantheon+ and DESI inputs do not substitute for collision measurements.

### 6. Publish the review packet and update active memory

Complete the specification with:

- What is faithfully recovered from the source record.
- What is standard physics.
- What is a new proposed assumption.
- What is conditionally derived or demonstrably inconsistent.
- What remains missing, and what a real observational test would require.
- A comparison of Candidate A versus Candidate B, including the possibility
  that no distinguishable new effect has yet been specified.

Add candidate nodes/relationships to `knowledgebase/GRAPH_MEMORY.json` using
existing evidence qualifiers; do not restore withdrawn validation language.
Update `docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md` with only material new conclusions.
Preserve original source copies and the current paper/results.

Check JSON parsing, node/edge integrity and local source links using existing
recovery validation patterns. Documentation-only work requires no numerical
reruns; relevant graph tests are required for a graph schema/content update.
No wholesale refactor of legacy tests is included.

End with a user review checkpoint. **Do not implement Candidate B, a dynamical
collision simulator, or new observational fitting until Kirk reviews the proposed
mechanism and explicitly authorizes the next phase.**

## Acceptance criteria

- The distinction between downstream thermal entropy and candidate geometric/
  information entropy is maintained throughout.
- Every newly introduced assumption is labelled and never attributed to Kirk
  without supporting source evidence or approval.
- The reference model is sufficient to identify known heating mechanisms before
  claiming an extra EMRF contribution.
- Each candidate either has a coherent stated energy/entropy accounting or an
  explicit, precisely located blocker.
- At least one proposed observable is assessed for identifiability; if none is
  justified, that negative result is the deliverable.
- No invented observational data, predetermined success claims or parameter
  tuning presented as proof.
- A clear reviewable specification and qualified graph entries are produced;
  production physics, archived records, current numerical results and publications
  remain unchanged.

## Out of scope and follow-on

Out of scope: proof of all thermodynamics, automatic closure of every regime,
new relativistic/Boltzmann/galaxy-formation engines, dark-matter exclusion,
quantum hardware experiments, journal submission or retrospective novelty claims.

After author review and only if a candidate is sufficiently defined, a separate
implementation plan can cover deterministic baseline checks, an explicit solver,
genuine observational ingestion and model comparison. The original multi-star
geometry experiment remains a separate viable route, not forgotten or falsified
by the collision project's unresolved assumptions.
