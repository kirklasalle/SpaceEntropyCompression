"""Validation and pre-flight submission check for academic preprint package."""

import re
from pathlib import Path
import pytest


@pytest.fixture
def paper_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "paper"


def test_manuscript_files_exist(paper_dir: Path):
    assert (paper_dir / "main.tex").is_file(), "main.tex not found in paper/"
    assert (paper_dir / "references.bib").is_file(), "references.bib not found in paper/"
    assert (paper_dir / "README.md").is_file(), "README.md not found in paper/"


def test_citation_keys_resolve(paper_dir: Path):
    tex_content = (paper_dir / "main.tex").read_text(encoding="utf-8")
    bib_content = (paper_dir / "references.bib").read_text(encoding="utf-8")
    
    # Extract all \cite{...} instances
    raw_citations = re.findall(r"\\cite\{([^}]+)\}", tex_content)
    cited_keys = set()
    for rc in raw_citations:
        for k in rc.split(","):
            cited_keys.add(k.strip())
            
    # Extract all @article{key, @book{key, etc. from bib
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([a-zA-Z0-9_\-]+)\s*,", bib_content))
    
    missing_keys = cited_keys - bib_keys
    assert not missing_keys, f"Found cited keys in main.tex missing from references.bib: {missing_keys}"


def test_labels_and_refs_resolve(paper_dir: Path):
    tex_content = (paper_dir / "main.tex").read_text(encoding="utf-8")
    
    # Extract labels and refs
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex_content))
    refs = set(re.findall(r"\\ref\{([^}]+)\}", tex_content))
    
    missing_refs = refs - labels
    assert not missing_refs, f"Found \\ref in main.tex without corresponding \\label: {missing_refs}"


def test_manuscript_structural_sections(paper_dir: Path):
    tex_content = (paper_dir / "main.tex").read_text(encoding="utf-8")
    
    required_sections = [
        "Correction statement",
        "Introduction",
        "Theoretical Formulation and Spatial Ontology",
        "Candidate Acceleration Laws",
        "Data and Method",
        "Results",
        "Status of Other Regimes and Prior Work",
        "Conclusion",
        "Reproducibility and data availability",
    ]
    for sec in required_sections:
        assert f"\\section{{{sec}" in tex_content or f"\\section*{{{sec}" in tex_content, f"Missing section: {sec}"
        
    assert "Kirk LaSalle" in tex_content, "Author Kirk LaSalle missing from author metadata"
    assert "Sagittarius~A*" in tex_content
    assert "SPARC" in tex_content
    assert any(tok in tex_content for tok in ("Delta-BIC", "\\Delta\\text{BIC}", "\\Delta\\mathrm{BIC}"))
