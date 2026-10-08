"""Check the new research source package without treating it as a PDF build."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manuscript_bibliography_and_inputs_exist():
    paper = ROOT / "paper"
    text = (paper / "sparc_horizon_test.tex").read_text(encoding="utf-8")
    bibliography = (paper / "sparc_horizon_references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\{([^,]+),", bibliography))
    for group in re.findall(r"\\cite\{([^}]+)\}", text):
        assert set(group.split(",")) <= keys
    for include in re.findall(r"\\input\{([^}]+)\}", text):
        assert (paper / include).is_file()
    assert text.count("\\begin{document}") == text.count("\\end{document}") == 1
    for environment in ("equation", "align", "abstract"):
        begins = text.count("\\begin{" + environment + "}")
        assert begins == text.count("\\end{" + environment + "}")
    assert "not Bayesian" in text
    assert "not a new" in text


def test_readable_reports_have_resolvable_local_file_links():
    names = [
        "REAL_DATA_VALIDATION_PROTOCOL.md",
        "EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md",
        "SPARC_HORIZON_TEST_PAPER.md",
        "REAL_DATA_REGIME_AUDIT.md",
        "REAL_DATA_REPRODUCIBILITY.md",
    ]
    for name in names:
        path = ROOT / "docs" / name
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            target = target.split("#")[0]
            assert (path.parent / target).exists(), (name, target)


def test_generated_results_match_fresh_verified_artifact():
    path = ROOT / "results" / "real_data_v1" / "sparc_profile_validation.json"
    if not path.exists():
        import pytest
        pytest.skip("Generate the real-data profile artifact before checking publication numbers")
    data = json.loads(path.read_text())
    assert data["complete"] and data["numerically_verified"]
    assert data["reverse_scan_max_total_Q_difference"] < data["scan_order_tolerance_Q"]
    text = (ROOT / "docs" / "SPARC_FRESH_RESULTS.md").read_text(encoding="utf-8")
    assert hashlib.sha256(path.read_bytes()).hexdigest() in text
    tex = (ROOT / "paper" / "sparc_horizon_results.tex").read_text(encoding="utf-8")
    for name, sample in data["samples"].items():
        row = (f"{name.replace('_', ' ')} & {sample['n_galaxies']} & "
               f"{sample['a0_grid_minimum']/1e-10:.3f}")
        assert row in tex
