"""Unit tests verifying the integrity and executability of the validation Jupyter notebook."""

import json
from pathlib import Path
import pytest


@pytest.fixture
def notebook_path() -> Path:
    return Path(__file__).resolve().parent.parent / "notebooks" / "emrf_two_regime_validation.ipynb"


def test_notebook_file_exists(notebook_path: Path):
    assert notebook_path.is_file(), f"Notebook not found at {notebook_path}"


def test_notebook_valid_json_structure(notebook_path: Path):
    data = json.loads(notebook_path.read_text(encoding="utf-8"))
    assert data.get("nbformat") == 4
    assert "cells" in data
    assert len(data["cells"]) >= 10
    
    markdown_cells = [c for c in data["cells"] if c["cell_type"] == "markdown"]
    code_cells = [c for c in data["cells"] if c["cell_type"] == "code"]
    
    assert len(markdown_cells) >= 5
    assert len(code_cells) >= 4


def test_notebook_code_cells_syntax_and_execution(notebook_path: Path):
    data = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [c for c in data["cells"] if c["cell_type"] == "code"]
    
    # Execute non-display cells in safe local namespace
    local_ns = {}
    for cell in code_cells:
        code_str = "".join(cell["source"])
        if "IPython.display" in code_str:
            continue
        exec(code_str, local_ns)
        
    assert "bifurcation_report" in local_ns
    assert "sparc_summary" in local_ns
    assert "jwst_results" in local_ns
    
    # Assert physical outcomes are verified
    assert local_ns["bifurcation_report"]["model_selection"]["delta_bic"] > 10.0
    assert local_ns["sparc_summary"]["joint_comparison"]["delta_bic_emrf_vs_newton"] < -10000.0
    assert local_ns["jwst_results"]["model_comparison"]["delta_bic"] < -50.0
