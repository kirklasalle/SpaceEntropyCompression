"""Validation and pre-flight check for First Use Case academic paper package."""

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


@pytest.fixture
def paper_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "paper"


def test_use_case_manuscript_files_exist(paper_dir: Path, tmp_path: Path):
    assert (paper_dir / "use_case_lasalle_ontology.tex").is_file(), (
        "use_case_lasalle_ontology.tex not found"
    )
    assert (paper_dir / "references.bib").is_file(), "references.bib not found"
    for name in (
        "use_case_lasalle_ontology.tex",
        "references.bib",
        "package_use_case_submission.py",
    ):
        shutil.copy2(paper_dir / name, tmp_path / name)
    (tmp_path / "figures").mkdir()
    for name in (
        "fig14_jwst_cosmic_dawn.png",
        "fig15_black_hole_horizon_entropy.png",
        "fig16_quantum_vibrational_solitons.png",
    ):
        shutil.copy2(paper_dir / "figures" / name, tmp_path / "figures" / name)
    subprocess.run(
        [sys.executable, str(tmp_path / "package_use_case_submission.py")],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    with zipfile.ZipFile(tmp_path / "use_case_submission.zip") as archive:
        assert archive.testzip() is None
        assert "use_case_lasalle_ontology.tex" in archive.namelist()


def test_use_case_citations_resolve(paper_dir: Path):
    tex_content = (paper_dir / "use_case_lasalle_ontology.tex").read_text(encoding="utf-8")
    bib_content = (paper_dir / "references.bib").read_text(encoding="utf-8")

    raw_citations = re.findall(r"\\cite\{([^}]+)\}", tex_content)
    cited_keys = set()
    for rc in raw_citations:
        for k in rc.split(","):
            cited_keys.add(k.strip())

    bib_keys = set(re.findall(r"@\w+\s*\{\s*([a-zA-Z0-9_\-]+)\s*,", bib_content))
    missing_keys = cited_keys - bib_keys
    assert not missing_keys, (
        f"Found cited keys in use_case missing from references.bib: {missing_keys}"
    )


def test_use_case_figures_exist(paper_dir: Path):
    tex_content = (paper_dir / "use_case_lasalle_ontology.tex").read_text(encoding="utf-8")
    fig_matches = re.findall(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}", tex_content)
    assert len(fig_matches) == 3, f"Expected 3 figures, found {len(fig_matches)}"
    for fig in fig_matches:
        fig_path = paper_dir / fig
        assert fig_path.is_file(), f"Missing figure: {fig_path}"
        assert fig_path.stat().st_size > 100_000, f"Figure {fig_path} too small"


def test_use_case_sections_and_author(paper_dir: Path):
    tex_content = (paper_dir / "use_case_lasalle_ontology.tex").read_text(encoding="utf-8")
    assert "Kirk LaSalle" in tex_content, "Author Kirk LaSalle missing"
    assert "LaSalle's Spatial Ontology" in tex_content or "LaSalle Spatial Ontology" in tex_content
    assert "Quantum Vibrations" in tex_content
    assert "Bekenstein-Hawking" in tex_content
    assert "JADES-GS-z14-0" in tex_content
    assert "10.5281/zenodo.23197308" in tex_content
