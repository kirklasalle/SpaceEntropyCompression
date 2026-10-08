# Compression, matter and the three horizons: proof-obligation audit

**Author:** Kirk LaSalle; computational/documentation assistance from an AI assistant using Copilot SDK in VS Code. **Status:** research audit, not peer review or theorem certification. **Protocol:** [real_data_v1](REAL_DATA_VALIDATION_PROTOCOL.md).

## 1. What exists, and what does not follow from it

EMRF has an implemented phenomenological mapping, a proposed ontology and several numerical demonstrations. Those are concrete intellectual and software outputs. A mathematical theorem additionally requires a precise statement, hypotheses and a valid proof; a physical theory requires well-defined dynamics and independently testable consequences. Neither software agreement with its own definitions nor renaming known identities establishes either condition.

The implemented mapping in [model.py](../emergent_matter_model/model.py) is

$$C=\sum_i w_i C_i+w_S C_S,\qquad M=k(C/C_0)^\alpha.$$

If M denotes density, k has density units; if M denotes total mass, k has mass units and the spatial integration prescription must be specified. C and C₀ must have identical units, and all summed terms require compatible units after weighting. A scalar field is not automatically a coordinate invariant when implemented as a sum of arbitrary coordinate functions. Domain restrictions are also needed: a noninteger real power requires an appropriate sign/domain for C/C₀. Normalization and fitted weights do not supply dynamical equations or an independently fixed mass scale.

The quantum demonstration instead uses C as an energy density, while the black-hole demonstration uses an inverse-area saturation. Those are different dimensional objects unless a mapping is explicitly supplied. They cannot silently serve as one universal compression field.

### A conditional result that can actually be shown

If one **assumes** spherical density ρ ∝ C^α and C ∝ sqrt(K) ∝ r⁻³ in a Schwarzschild-like exterior, then ρ ∝ r⁻³α. For 0 < 3α < 3 and a radial interval where the enclosed integral dominates any central contribution,

$$M(<r)\propto r^{3-3\alpha},\qquad V^2(r)=GM(<r)/r\propto r^{2-3\alpha}.$$

A flat circular speed therefore requires α = 2/3, not α = 1/3. This is conditional algebra, not a derivation of a self-consistent halo: prescribing a Schwarzschild vacuum curvature while adding extended gravitating density requires checking the coupled field equations. It is also not evidence of novelty.

## 2. Action-to-observable gap

The [corrected action note](../knowledgebase/action_principle_derivation.md) proposes a canonical scalar entropy sector,

$$\mathcal L_S=-\tfrac12\kappa_S g^{AB}\nabla_A S\nabla_B S-V(S).$$

With a specified coupling/source convention its field equation has the form κ_S □S − V′(S) = J. Linearizing about a stable constant background gives

$$\kappa_S\nabla^2\delta S-m^2\delta S=J.$$

For fixed coefficients, boundary conditions independent of source mass and J linear in mass, the perturbation scales linearly with mass. That **linearized sector** does not establish a deep-MOND force ∝ sqrt(M). This does not rule out every nonlinear canonical theory or noncanonical completion; changing the dynamics would require a new explicit model and new tests.

To close the gap, specify the matter coupling, C(S,g,...) functional, metric equations, cosmological background, weak-field limit and boundary conditions. Derive both motion of matter and lensing (the relevant metric potentials), tensor propagation, and perturbative stability from the same action. Choosing a rotation-law interpolation, independently imposing luminal waves and using GR lensing is not such a derivation.

For g = sqrt(g_N² + a₀g_N), the high-acceleration expansion is

$$g-g_N=\frac{a_0}{2}-\frac{a_0^2}{8g_N}+\cdots.$$

That constant leading correction is an analytically checkable property of this named phenomenological law. Observational exclusion requires matching it to an actual ephemeris constraint, not treating an unrelated Cassini PPN bound as an acceleration measurement. Screening introduced solely to evade this result is a different model, not a successful retest of the original law.

Equating the Unruh and de Sitter temperatures,

$$T_U=\frac{\hbar a}{2\pi c k_B},\qquad T_{dS}=\frac{\hbar H}{2\pi k_B},$$

gives a = cH. The extra 1/(2π) in a₀ = cH/(2π) remains a hypothesis here.

## 3. Horizon H01: quantum matter and solitons

[quantum_vibrational_compression.py](../emergent_matter_model/quantum_vibrational_compression.py) constructs a prescribed radial envelope using an **input** mass, whose Compton scale and frequency are ħ/(mc) and mc²/ħ. It does not numerically solve a stated field boundary-value problem. After integrating its assigned energy density, it computes

$$m_{\rm raw}=E/c^2,\quad r=m_{\rm raw}/m_{\rm input},\quad m_{\rm reported}=m_{\rm raw}/r=m_{\rm input}.$$

Equality is built into the final normalization for nonzero finite values. Replacing reference masses with improved CODATA/PDG measurements does not make this an independent mass prediction.

The stability routine tests an imposed entropy profile and a positive ratio, and sets `free_energy_barrier_positive` to true. These are not a perturbation spectrum, conserved-energy analysis, or proof of nonlinear stability. Terms involving m²ψ², ψ⁴ and k_Bψ² require a declared unit convention and dimensional couplings before they can be summed as a physical potential.

**Current status:** not yet testable as emergent-particle physics. Required: an explicit action/Hamiltonian, solved localized configuration, independent normalization/mass spectrum, conserved quantities and a stability analysis. Experimental mass values can then constrain it, rather than calibrate the answer.

## 4. Horizon H02: black-hole entropy

[black_hole_horizon_entropy.py](../emergent_matter_model/black_hole_horizon_entropy.py) explicitly assigns k_B/4 per Planck-area cell. The subsequent integration gives

$$S=\int_A\frac{k_B}{4\ell_P^2}\,dA=\frac{k_B A}{4\ell_P^2}.$$

The integral is correct, but the coefficient is an input. Independent microstate counting or another derivation must determine the coefficient without assuming the target law. Measured black-hole masses can constrain inferred areas conditional on a spacetime model; they do not directly measure astrophysical horizon entropy. EHT or gravitational-wave observations are not automatically thermodynamic entropy measurements.

Also, Schwarzschild coordinate-time behavior at the horizon is not an invariant statement that all physical change stops. Horizon claims must distinguish coordinate effects from local/invariant observables.

**Current status:** a standard-identity demonstration, not a new entropy theorem or empirical confirmation. Preserve the original calculation as illustrative software, excluded from empirical pass counts.

## 5. Horizon H03: cosmic dawn

[jwst_highz_early_galaxies.py](../emergent_matter_model/jwst_highz_early_galaxies.py) contains hand-entered benchmark redshifts/masses and an assumed cloud-collapse calculation. Authentic redshift and photometric observations must be traced to a release/table and carry uncertainties and selection effects. Early-galaxy stellar masses depend on stellar populations, dust, star-formation history, emission lines and distance assumptions.

A short collapse time does not predict observed abundance, luminosity, stellar mass or size. To test the proposed acceleration history, derive an assembly prescription, initial conditions, baryon supply and conversion to observed light under the same cosmological model. Do not claim that the existence of a high-redshift galaxy has disproved ΛCDM or that fitting one timescale has resolved a crisis.

**Current status:** authentic observations can inform a research question, but an EMRF population prediction is missing. This horizon is distinct from resolved high-z disk dynamics (R06).

Primary observational context: Carniani et al., *Spectroscopic confirmation of two luminous galaxies at z ∼ 14*, [arXiv:2405.18485](https://arxiv.org/abs/2405.18485). Prior discussion of accelerated formation also exists (McGaugh et al., [arXiv:2406.17930](https://arxiv.org/abs/2406.17930)); the broad idea is not itself a new EMRF discovery.

## 6. Auxiliary consistency checks

A universal metric coupling can enforce a form of the equivalence principle by construction; this is an assumption/structural implication, not an independent empirical success. Composition-dependent couplings require a derived Eötvös parameter matched to actual experiments.

Second-order equations alone do not prove complete stability. Kinetic signs, gradient terms, constraints, relevant backgrounds, masses and strong-coupling regimes must be examined. The scope of any no-ghost statement must be specified rather than inferred from a positive hand-chosen coefficient.

## 7. IBM Quantum feasibility appendix

The [official IBM plans overview](https://quantum.cloud.ibm.com/docs/en/guides/plans-overview), consulted for this audit, specifies up to **10 QPU minutes per rolling 28-day window** for the Open Plan. This is not a check of Kirk LaSalle's account or remaining allowance. No credentials were requested and no quota has been consumed by this work.

A small real-hardware experiment can measure qubit observables, noise, correlations or entanglement under documented control conditions. It may help study an independently defined quantum model. But a quantum circuit that encodes an assumed Hamiltonian is an implementation of that assumption; its hardware output does not show that spacetime or particle masses obey that Hamiltonian. A quantum simulation remains a simulation of the target physics even though the processor is physical.

Before a later hardware proposal, require:

1. A precise physical claim and a discriminating observable, not merely recovery of an encoded identity.
2. A mapping from that observable to measurable operators, with approximations, scale conventions and classical analytic checks.
3. A hardware protocol including controls, calibration snapshots, shot uncertainty, noise treatment and job metadata.
4. A realistic resource allowance and explicit approval before uploads or jobs.

Under the present real-observation-only project, the appropriate action is to **reserve the quota**. There is no identified QPU experiment that closes the missing gravity/matter derivation.

## Reproducing the algebra checks

Run `emergent_matter_model\.venv\Scripts\python.exe tools\check_compression_claims.py` from the repository root. The [stored diagnostic](../results/real_data_v1/compression_algebra.json) records evaluated input-mass recovery, the assumed entropy coefficient, temperature-factor cancellation and source hashes. Its evidence type explicitly says **not observations**. These calculations were executed; they are neither new experimental measurements nor validation of the horizon claims.

## Bottom line

What is concrete is the model implementation, conditional mathematics, identifiable failed/circular claims and a testable galaxy-scale hypothesis. What remains open is a new physical theorem, a unified dynamical theory, independent particle-mass or horizon-entropy predictions, and observational validation across all regimes. Honest negative and blocked results are useful because they specify exactly what must be supplied next.
