# Emergent Matter Research Framework (EMRF)

**A research toolkit for geometric descriptions of matter, reproducible astronomical baselines, and critical tests of space-entropy hypotheses.**

[![Status: Research, not a validated theory](https://img.shields.io/badge/status-research%20not%20validated-orange)](MODEL_CARD.md)
[![Direction: Candidate A within GR](https://img.shields.io/badge/direction-Candidate%20A%20within%20GR-blue)](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
[![Software tests: 244 passed locally](https://img.shields.io/badge/software%20tests-244%20passed%20locally-brightgreen)](STATUS.md)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](emergent_matter_model/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](emergent_matter_model/LICENSE)
[![Historical Zenodo record](https://img.shields.io/badge/Zenodo-historical%20record-grey)](https://doi.org/10.5281/zenodo.23197308)

**Author and principal investigator: Kirk LaSalle.** Current documentation: October 8, 2026.
The test badge reports a local software run, not hosted CI or physical confirmation.
The linked Zenodo record is historical; it does not archive or validate the current working revision.

## Read this first

EMRF contains useful software, real-data re-analyses and proposed mathematical
descriptions. **It does not currently establish a new theory of gravity, an
origin-of-matter theorem, a solution to entropy, or confirmation across ten regimes.**

Earlier releases used synthetic tables labelled as observations and circular
tests with answers built into the implementation. Their headline empirical
results and self-awarded audit certifications are withdrawn. See the
[correction audit](docs/SHOW_YOUR_WORK.md) and
[historical source archive](docs/archive/antigravity_recovery/README.md).
Old documents, figures, release assets and audio can still contain those claims;
their presence is historical evidence, not an endorsement.

## Current direction: Candidate A

Kirk selected **Candidate A: C describes existing geometry and energy
organization**, rather than introducing an additional reservoir, force or
heating channel. He also asked whether the formulation can be found inside GR.
Candidate B, an AI-proposed extra exchange channel, remains unselected.

The recorded matter mapping is

$$M(X,t)=k\left[\frac{C(X,t)}{C_0}\right]^\alpha.$$

Its interpretation depends on what C and M mean. The
[functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md) distinguishes
local energy-equivalent density, vacuum tidal curvature and regional mass.
For the **recommended, not yet author-selected** GR reference

$$C_m=(G_{\mu\nu}+\Lambda g_{\mu\nu})n^\mu n^\nu,\qquad
\rho_{E,(n)}=\frac{c^2}{8\pi G}C_m,$$

with unit timelike observer n and Einstein's equation assumed, the mapping
reproduces this scalar identity for alpha=1 and k=c²C0/(8πG).
This is not an independent derivation of matter or a proof of full dynamical
equivalence. A scalar cannot by itself replace the entire metric/stress tensor.

**Thermodynamics:** the recovered intent places macroscopic thermodynamics
downstream of matter and interactions, while allowing a distinct candidate
geometric/information entropy. These quantities must not be silently conflated.
The collision illustration does not evolve gravitational wells or generate entropy.

## Start here

| Resource | Purpose |
|---|---|
| [Candidate A functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md) | Definitions, units, conditional identity, counterexamples and recommendation |
| [Collision specification](docs/EMRF_COLLISION_CANDIDATE_SPECIFICATION.md) | Standard energy/entropy budget and recorded Candidate A selection |
| [Top-down theory/toolkit audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md) | Theory-to-code gaps and case-by-case data requirements |
| [SPARC paper: PDF](paper/sparc_horizon_test.pdf) / [readable text](docs/SPARC_HORIZON_TEST_PAPER.md) | Six-page research draft; not submitted or peer reviewed |
| [Fresh SPARC results](docs/SPARC_FRESH_RESULTS.md) | Executed fits, sensitivity and numerical checks |
| [Regime evidence report](docs/REAL_DATA_REGIME_AUDIT.md) | All ten regimes and three horizons, including explicit blockers |
| [Archive recovery audit](docs/ANTIGRAVITY_RECOVERY_AUDIT.md) | Recovered meanings, historical artifacts, provenance and coverage limits |
| [Reproducibility guide](docs/REAL_DATA_REPRODUCIBILITY.md) | Commands, software assumptions and publication boundaries |
| [Model card](MODEL_CARD.md) / [status](STATUS.md) / [roadmap](ROADMAP.md) | Intended use, current results and remaining decisions |

## What has actually been computed

| Analysis | Result | Interpretation |
|---|---|---|
| SPARC conventional fixed-stellar RAR reference | a₀ = 1.2216 × 10⁻¹⁰ m/s² | Reproduction of a known acceleration scale, not a new discovery |
| SPARC nuisance profiles | 153 galaxies, 3,168 points; four interpolation laws | Penalized profiling, **not Bayesian marginalization** |
| Deep-bulge influence check | Removing UGC 06787 shifts the grid optimum from 1.60 to 0.90 × 10⁻¹⁰ m/s² | Independently refitted sensitivity; not grounds to discard that galaxy or declare new physics |
| DESI BAO flat-ΛCDM baseline | 12 means, full covariance; χ² = 12.7405 for 10 nominal degrees of freedom | A baseline fit, not EMRF cosmology |
| Pantheon+ flat-ΛCDM baseline | 1,590 rows, full STAT+SYS covariance; Ωm = 0.33158, χ² = 1402.919 for 1588 nominal degrees of freedom | Uncalibrated magnitude offset; **does not measure H₀** |
| Candidate A definition checks | Radiation/vacuum counterexamples and specified regional-energy identities | Exact-background mathematical checks, **not observations** |

SPARC grid intervals and objective differences remain conditional on the
likelihood, nuisance constraints and selection. Unknown correlated errors and
poor fit quality prevent promoting them to calibrated discovery significance.
Historical “5.4σ” and galaxy ΔBIC headlines are not current certified conclusions.
The main profile's forward/reverse numerical discrepancy was reduced to about
4.74 × 10⁻⁹ by explicitly searching the signed-gas floor branches.

The horizon hypothesis a₀=cH₀/(2π) remains a phenomenological question, not a
derived consequence or confirmed universal law. For the selected Candidate A,
a fit of an independently assumed MOND-like law does not validate the entire
compression framework.

## Ten regimes and three horizons: no artificial passes

| Case | Current scope |
|---|---|
| Sgr A* S-stars | Original multi-trajectory design preserved; authentic joint likelihood and specified C mapping remain missing |
| Solar System | Analytic high-acceleration behavior checked; no new tracking-data fit or generic Cassini “pass” claimed |
| SPARC rotation curves | Authentic observations, executed conditional comparisons and influence checks |
| SLACS lensing | Standard GR baseline utilities; no derived separate EMRF lensing prediction |
| Bullet Cluster | Static synthetic illustration; executable status **NOT TESTED** |
| High-redshift disks | Observational sample, corrections and specified prediction still required |
| GW170817 | Published constraint available; assigning c in code is not an independent test |
| Gaia wide binaries | Pair-level selection/contamination and a justified likelihood remain necessary |
| Late-time expansion | Real Pantheon+/DESI baseline fits; no new EMRF expansion dynamics demonstrated |
| CMB | Template checks are not a physical perturbation-spectrum calculation |
| Quantum matter | Input-mass normalization is an identity, not independent particle-mass emergence |
| Black-hole entropy | Assumed quarter-area coefficient is not newly derived |
| Cosmic dawn | A prescribed collapse time does not predict a measured galaxy population |

“Not yet testable” identifies a missing equation, observable or data likelihood.
It means neither confirmation nor universal falsification. See the
[detailed top-down audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md).

## Install and run

Run from the repository root in PowerShell. Use your existing environment if
already configured; otherwise:

```powershell
git clone https://github.com/kirklasalle/SpaceEntropyCompression.git
Set-Location SpaceEntropyCompression
python -m venv emergent_matter_model\.venv
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip install -e ".\emergent_matter_model[dev]"
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model -q
```

**Software validation:** 244 tests passed locally on October 8, 2026.
Some tests exercise synthetic fixtures or check document structure; this count
does not measure empirical support. Optional observed-data artifact checks may
skip when their inputs have not been downloaded.

### Real-data workflows

```powershell
# Download and authenticate SPARC; fail if cached/extracted bytes have changed
& .\emergent_matter_model\.venv\Scripts\python.exe emergent_matter_model\fetch_real_data.py --sparc

# Fresh four-law profiles and deterministic sensitivity diagnostics
& .\emergent_matter_model\.venv\Scripts\python.exe tools\run_sparc_profile_validation.py --step 0.05
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_sparc_influence.py

# Public-source gauntlet, DESI covariance baseline and explicit blockers
& .\emergent_matter_model\.venv\Scripts\python.exe tools\run_real_data_gauntlet.py

# Requires the manually downloaded Pantheon+ files described below
& .\emergent_matter_model\.venv\Scripts\python.exe tools\fit_pantheon_real_covariance.py
```

Raw observations live in the git-ignored `data\external` directory and are
not bundled into the source repository. The Pantheon+ command expects
`Pantheon+SH0ES.dat.txt` and `Pantheon+SH0ES_STAT+SYS.cov.txt` there, preserves
their original bytes, and verifies them against the pinned official release.
Download them from the [collaboration's distances/covariance directory](https://github.com/PantheonPlusSH0ES/DataRelease/tree/c447f0fea703fcd0fff57de5000947b5ca81286b/Pantheon%2B_Data/4_DISTANCES_AND_COVAR).
The extra `.txt` suffixes match the manually ingested files; retain the exact names
for this entry point. Covariance rows must stay aligned with the measurement table.

### Mathematical and evidence checks

```powershell
# No observational evidence is generated by these algebra checks
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_candidate_a_definitions.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_compression_claims.py

# Verify preserved archive copies and graph references without private IDE access
& .\emergent_matter_model\.venv\Scripts\python.exe tools\verify_antigravity_recovery.py
```

Publication generation and local LaTeX build instructions are in the
[reproducibility guide](docs/REAL_DATA_REPRODUCIBILITY.md). No IBM Quantum
account access or quota is required. Read legacy scripts' evidence warnings
before interpreting their output.

## Repository map

| Location | Contents |
|---|---|
| [emergent_matter_model](emergent_matter_model/) | Physics utilities, phenomenological models, API/demo code and software tests |
| [tools](tools/) | Real-data runners, evidence checks, document/build and recovery tools |
| [results](results/) | Versioned derived outputs, convergence diagnostics and provenance |
| [paper](paper/) | Current SPARC manuscript plus clearly distinguished historical drafts |
| [docs](docs/) | Audits, candidate specifications, correction history and reproducibility |
| [knowledgebase](knowledgebase/) | Qualified graph, source-linked claims and historical references |
| [data/synthetic](data/synthetic/) | Quarantined software fixtures, **not observations** |
| [recovered archive](docs/archive/antigravity_recovery/) | Historical drafts/code/logs/images, with hash manifest and warnings |

Archived scripts are not executed during recovery. Old task/status counts,
audio praise, synthetic screenshots and historical “validated” graph entries
are not independent scientific evidence. The
[recovery audit](docs/ANTIGRAVITY_RECOVERY_AUDIT.md) states what was searched and
what could not be established from the incomplete IDE archive.

## Next scientific decision

Candidate A is selected; **the exact functional C and the meaning of M are not**.
The current recommendation is a local observer energy-density reference inside GR,
with tidal curvature kept separate. Regional energy needs an explicit boundary.
Author review should precede any new implementation. A useful reformulation can
succeed without predicting a new force; novelty and full equivalence need their
own arguments.

## Contributing and research integrity

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[validation protocol](docs/REAL_DATA_VALIDATION_PROTOCOL.md).
Contributions should separate recovered author intent, standard physics, new
assumptions, software tests and observational findings. Report failures, missing
data, optimizer instability and non-identifiability explicitly.
Independent domain-expert review remains necessary before submission.

The [community ethics charter](docs/COMMUNITY_ETHICS.md) records Kirk's values.
Ethical commitments and careful software engineering are valuable; neither
constitutes physical evidence.

## Citation, versions and historical releases

Use [CITATION.cff](CITATION.cff) for repository citation metadata and include the
**commit you actually used**. This README describes `main`, not a newly tagged
or peer-reviewed release. Existing version strings and release bundles may refer
to earlier software snapshots.

```bibtex
@software{lasalle_emrf,
  author = {LaSalle, Kirk},
  title = {Emergent Matter Research Framework (EMRF)},
  url = {https://github.com/kirklasalle/SpaceEntropyCompression},
  note = {Research software; cite the exact revision used}
}
```

The [historical Zenodo record](https://doi.org/10.5281/zenodo.23197308) and old
GitHub releases predate important corrections. Their DOI/tag is not evidence
that this current revision was archived. Historical release notes receive
correction notices where access permits; original tags/assets are preserved.

## Selected references

- [Lelli, McGaugh & Schombert (2016): SPARC](https://arxiv.org/abs/1606.09251).
- [McGaugh, Lelli & Schombert (2016): radial acceleration relation](https://arxiv.org/abs/1609.05917).
- [Li et al. (2018): individual SPARC fits](https://arxiv.org/abs/1803.00022).
- [Brown & York: quasi-local energy](https://arxiv.org/abs/gr-qc/9209012).
- [Hayward: gravitational energy in spherical symmetry](https://arxiv.org/abs/gr-qc/9408002).
- [Jacobson (1995): thermodynamics of spacetime](https://arxiv.org/abs/gr-qc/9504004).
- [Markevitch & Vikhlinin: cluster shocks and cold fronts](https://arxiv.org/abs/astro-ph/0701821).

These are precedents and data/method references, not endorsements of EMRF.
Full context and source-verification limits are recorded in the linked audits.

## License and authorship

[MIT License](emergent_matter_model/LICENSE). Copyright (c) 2026 Kirk LaSalle.
Kirk LaSalle is the principal investigator and author of the research hypothesis.
AI assistance has contributed to implementation, documentation and audits;
AI-generated claims require the same scrutiny as any other scientific claim.
