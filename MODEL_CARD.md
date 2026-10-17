# EMRF model and evidence card

- **Principal investigator:** Kirk LaSalle
- **Repository:** https://github.com/kirklasalle/SpaceEntropyCompression
- **Scope:** current `main` research revision, October 16, 2026
**License:** [MIT](emergent_matter_model/LICENSE)

## Intended use

Explore explicit mathematical hypotheses, reproduce standard analytical
benchmarks, analyze authenticated astronomical observations, and identify
limits and failures. Not a validated fundamental theory or a certified proof
of matter emergence, gravity unification or entropy generation.

## Evidence classes

| Class | Examples | What may be claimed |
|---|---|---|
| Standard mathematical baseline | Kepler/1PN utilities; exact-background Candidate A checks | Conditional algebra or software agreement with a known formula |
| Real-data baseline | DESI flat-LCDM fit; full-covariance Pantheon+ fit | Results under the stated baseline and data assumptions, not EMRF validation |
| Conditional model comparison | Fresh SPARC four-law profiles and influence checks | Comparative fit behavior with nuisance/systematic caveats |
| Preregistered coupling bound | Candidate B restricted Higgs portal against ATLAS and CMS public results | Compatibility with an upper bound on the new coupling; never support for B |
| Preregistered falsification | Candidate A option 2 (M = observed baryons) against SPARC rotation curves | Rejection of that operationalization only; not blind; not a test of A's other options |
| Full-density numerical benchmark | Candidate A option-3 source mapping and axisymmetric Poisson solver | Agreement with an analytic potential and quadrature convergence; no observational fit or verdict |
| Proposed interpretation | Candidates A and B; A's recommended C definition | Selected research programs, not a selected unique functional, equivalence proof or validated sector |
| Historical illustration | Bullet maps, CMB templates, synthetic catalogs and old dashboard | Demonstration only; no observational verdict |
| Historical recovery | Archived drafts, code, logs, audio and screenshots | Provenance of statements/development, not confirmation of the statements |

## Selected interpretations

Kirk LaSalle runs two candidate programs concurrently; see the
[dual-candidate program](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md). Neither is
confirmed, and evidence about one is not evidence for the other.

**Candidate A** re-describes existing geometry/energy organization, without adding
an independent heat source or reservoir. The recommended reference
C_m=(G+Lambda g)(n,n) gives rho_E=c² C_m/(8πG) if Einstein's equation is assumed
and the observer is specified. The power-law ansatz requires alpha=1 and fixed
normalization to reproduce that scalar identity. It is not a derivation of
microscopic matter or equivalence of the full dynamics.

One operationalization, option 2 (C = C_m, alpha = 1, M = observed baryons),
was proposed by the assistant while Kirk was unavailable. It was tested on
SPARC under a frozen preregistration and **rejected**: rotation curves need
more mass than the observed baryons in 153 galaxies. The test was not blind.
It falsifies option 2 only. Kirk subsequently authorized investigation of all
three options, with the full-density route for option 3, not selection of a
single final theory. Option 1 passes 81 GR consistency checks and option 2's
6,621 result fields reproduce. The option-3 volume-density solver passes
analytic benchmarks, but no observational fit was performed: the downloaded
Leroy surface-density profiles need a justified 3-D reconstruction and
missing/censored-data treatment. A nonunit exponent is not the same
baryons-only GR source; a physical completion or explicit phenomenological
restriction and a new observational protocol remain necessary.
See the [functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md).
Tidal curvature, local material density, thermal entropy and regional mass
must not be substituted for one another.

**Candidate B** adds a separately budgeted exchange sector. It began as an
AI-proposed ansatz; it has been tested only as a restricted one-circle,
tree-level Higgs portal. Three preregistered comparisons with ATLAS and CMS
public results allow the new coupling to vanish and bound it from above. See
the [model contract](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md),
sections 16–17.

## Data and statistical constraints

- Source/checksum-verified SPARC data: 153 selected galaxies / 3,168 points.
- Pantheon+: 1,590 selected rows / 1,473 distinct CID values, full STAT+SYS
  covariance, profiled magnitude offset; H0 is not independently inferred.
- DESI: 12 BAO means with their covariance, explicitly labelled baseline.
- Synthetic inputs remain [quarantined](data/synthetic/README.md).
- Raw public inputs are downloaded separately under git-ignored `data/external`.
- Profiling is not marginalization. Reduced-chi-square rescaling and
  grid intervals do not establish calibrated discovery significance.
- A prior-penalized objective is not automatically a maximized likelihood for BIC.
- Multiple radial samples and exploratory subgroup choices limit interpretation.

## Known failure modes

Earlier synthetic data, copied answers, circular normalizations and unconditional
pass labels generated unjustified scientific confidence. Those claims are
withdrawn. The collision report now explicitly says NOT TESTED, but not every
legacy module's API has been comprehensively rewritten.

The legacy `evaluate_bifurcation` API cannot prove equivalence to GR from an
unfavourable BIC difference. The cosmology/CMB templates are not a relativistic
EMRF completion. The particle mass and black-hole entropy demonstrations do not
independently predict their normalization. Published source retrieval is not
equivalent to measurement-table ingestion.

## Validation and limitations

On October 16, 2026, 594 non-golden software tests passed locally; 3 property-based
tests failed from an internal error in the installed `hypothesis` library
(`'TreeNode' object has no attribute 'is_exhausted'`), not from EMRF code.
Tests include synthetic fixtures, API behavior, document structure and
graph/provenance checks. They do not constitute 594 physical tests. The current
compiled paper is a research draft, not accepted
or peer-reviewed work. Consult [status](STATUS.md), [top-down audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
and [reproducibility guide](docs/REAL_DATA_REPRODUCIBILITY.md).

No new IBM Quantum experiment, external submission or new archival DOI is
claimed. Future work needs a precisely chosen functional, meaningful observable,
appropriate data likelihood and independent scientific review.
