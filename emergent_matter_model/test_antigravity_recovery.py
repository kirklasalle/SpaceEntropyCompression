"""Recovery integrity tests; archived statements are not physics validation."""
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import unquote

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_recovery_bytes_graph_integrity_and_arithmetic():
    module = load_tool("verify_antigravity_recovery")
    result = module.verify()
    assert result["preserved_records_verified"] == 47
    assert result["recovery_claims"] == 10
    assert result["historical_nodes_preserved"] == 81
    assert result["arithmetic_checks"]["quantum_unnormalized_mass_ratio"] == pytest.approx(
        .34359933398697, abs=1e-12)
    assert result["arithmetic_checks"]["schwarzschild_radius_m_for_1e_minus18_solar_masses"] == (
        pytest.approx(2.953339382e-15, rel=1e-9))


def test_mixed_project_filter_does_not_copy_sibling_projects():
    module = load_tool("recover_antigravity_evidence")
    mixed = {"name": "theory", "manifests": {"QubitControl\\x": "unrelated",
                                           "SpaceEntropyCompression\\x": "keep"},
             "paths": ["unrelated", "SpaceEntropyCompression\\y"]}
    result = module.project_only(mixed)
    assert result == {"manifests": {"SpaceEntropyCompression\\x": "keep"},
                      "paths": ["SpaceEntropyCompression\\y"]}


def test_archived_script_write_is_non_destructive(tmp_path):
    module = load_tool("recover_antigravity_evidence")
    path = tmp_path / "snapshot.txt"
    module.write_once(path, b"original")
    module.write_once(path, b"original")
    with pytest.raises(ValueError, match="Refusing"):
        module.write_once(path, b"replacement")
    with pytest.raises(ValueError, match="credential"):
        module.check_text(b"-----BEGIN PRIVATE KEY-----")


def test_curated_documents_resolve_local_links():
    paths = [ROOT / "docs" / "ANTIGRAVITY_RECOVERY_AUDIT.md",
             ROOT / "knowledgebase" / "antigravity_recovered_theory.md",
             ROOT / "docs" / "archive" / "antigravity_recovery" / "README.md"]
    for path in paths:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            assert (path.parent / unquote(target.split("#")[0])).exists(), (path, target)


def test_graph_never_promotes_old_validation():
    graph_path = ROOT / "knowledgebase" / "GRAPH_MEMORY.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert graph["meta"]["recovery_integrated"]
    assert not any(edge["relation"] == "validated_by" for edge in graph["edges"])
    assert all(node["use_for_empirical_confirmation"] is False for node in graph["nodes"])
