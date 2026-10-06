# EMRF Academic Preprint Package

This directory contains the formal academic preprint source for the Emergent Matter Research Framework (EMRF):

**Title:** Space-Entropy Compression and Relativistic Dynamics: Multi-Star Astrometric Testing of Emergent Matter Hypotheses in the Sagittarius A* Nuclear Cluster  
**Author:** Kirk LaSalle  
**Date:** October 2026  
**Format:** Standard LaTeX with BibTeX bibliography (`main.tex`, `references.bib`)  

---

## Files
- `main.tex`: Full publication manuscript with abstract, 8 sections, mathematical derivations, tables, and references.
- `references.bib`: Complete BibTeX bibliography with DOIs.
- `README.md`: Compilation instructions and metadata.

---

## Compilation Instructions

### Local LaTeX Installation (TeX Live, MacTeX, MiKTeX)
```bash
# Standard three-pass compilation with BibTeX
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Or using latexmk (automated single command)
latexmk -pdf main.tex
```

### Overleaf / arXiv Submission
1. Upload both `main.tex` and `references.bib` directly to an Overleaf project or the arXiv submission portal.
2. Select standard pdfLaTeX compiler.
