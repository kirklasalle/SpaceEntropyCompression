# EMRF research manuscripts

## Current SPARC research draft

- [Compiled six-page PDF](sparc_horizon_test.pdf)
- [LaTeX source](sparc_horizon_test.tex)
- [Generated results supplement](sparc_horizon_results.tex)
- [Bibliography](sparc_horizon_references.bib)
- [Readable paper](../docs/SPARC_HORIZON_TEST_PAPER.md)
- [Fresh numerical results](../docs/SPARC_FRESH_RESULTS.md)

This is a conditional real-data re-analysis, not a submitted/accepted paper or
proof of new gravity. It reports the substantial UGC 06787 influence on the
deep-bulge subset. Subsequent Candidate A work is in the
[functional comparison](../docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md);
it is not retroactively presented as a result in the SPARC paper.

## Rebuild

Follow the [reproducibility guide](../docs/REAL_DATA_REPRODUCIBILITY.md) to generate
verified numerical artifacts and the supplement first. Then, from repository root:

```powershell
python tools\build_sparc_paper.py --compiler tectonic
```

Tectonic performs the bibliography/reruns locally. Alternatively, from this
directory run pdfLaTeX, BibTeX and two more pdfLaTeX passes on `sparc_horizon_test`.
The [build record](../results/real_data_v1/manuscript_build.json) identifies the
executed compiler and source/PDF hashes.

## Historical material

[main.tex](main.tex), [use_case_lasalle_ontology.tex](use_case_lasalle_ontology.tex),
older cover letters, FAQs, submission instructions and existing archives retain
historical claims. They are **not current submission-ready validated findings**.
See the [integrity audit](../docs/SHOW_YOUR_WORK.md).
Do not submit an old package simply because its structural tests pass.
