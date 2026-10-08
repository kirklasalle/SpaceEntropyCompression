# EMRF model and evidence card

- **Principal investigator:** Kirk LaSalle
- **Repository:** https://github.com/kirklasalle/SpaceEntropyCompression
- **Scope:** current `main` research revision, October 8, 2026
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
| Proposed interpretation | Candidate A and its recommended C definition | A selected research direction, not a selected unique functional or equivalence proof |
| Historical illustration | Bullet maps, CMB templates, synthetic catalogs and old dashboard | Demonstration only; no observational verdict |
| Historical recovery | Archived drafts, code, logs, audio and screenshots | Provenance of statements/development, not confirmation of the statements |

## Selected interpretation

Candidate A re-describes existing geometry/energy organization, without adding
an independent heat source or reservoir. The recommended reference
C_m=(G+Lambda g)(n,n) gives rho_E=c² C_m/(8πG) if Einstein's equation is assumed
and the observer is specified. The power-law ansatz requires alpha=1 and fixed
normalization to reproduce that scalar identity. It is not a derivation of
microscopic matter or equivalence of the full dynamics.

See the [functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md).
Tidal curvature, local material density, thermal entropy and regional mass
must not be substituted for one another.

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

244 software tests passed locally. Tests include synthetic fixtures, API
behavior, document structure and graph/provenance checks. They do not constitute
244 physical tests. The current compiled paper is a research draft, not accepted
or peer-reviewed work. Consult [status](STATUS.md), [top-down audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
and [reproducibility guide](docs/REAL_DATA_REPRODUCIBILITY.md).

No new IBM Quantum experiment, external submission or new archival DOI is
claimed. Future work needs a precisely chosen functional, meaningful observable,
appropriate data likelihood and independent scientific review.
