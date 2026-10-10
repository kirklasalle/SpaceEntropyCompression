from __future__ import annotations

from pathlib import Path

import emrf_paths
import pytest

from emergent_matter_model import data_provenance as package_provenance
from emergent_matter_model import emrf_paths as package_paths
from emergent_matter_model import emrf_registry as package_registry
from emergent_matter_model import fetch_real_data as package_fetch


def test_package_qualified_legacy_imports_share_path_policy() -> None:
    assert package_paths.data_root() == emrf_paths.data_root()
    assert package_provenance.SYNTHETIC_DIR == emrf_paths.data_root() / "synthetic"
    assert package_fetch.DATA_ROOT == emrf_paths.data_root()
    assert package_registry.EXTERNAL_DIR == emrf_paths.data_root() / "external"


def test_checkout_uses_repository_data_root() -> None:
    root = emrf_paths.project_root()
    assert root is not None
    assert emrf_paths.app_root() == root
    assert emrf_paths.data_root() == root / "data"


def test_environment_overrides_are_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    data = tmp_path / "observations"
    monkeypatch.setenv("EMRF_HOME", str(home))
    monkeypatch.setenv("EMRF_DATA_DIR", str(data))
    monkeypatch.setattr(emrf_paths, "project_root", lambda: None)
    assert emrf_paths.app_root() == home.resolve()
    assert emrf_paths.data_root() == data.resolve()
    assert emrf_paths.resolve_data_path("data/external/a.dat") == data / "external/a.dat"


def test_invalid_project_override_fails_explicitly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EMRF_PROJECT_ROOT", str(tmp_path))
    with pytest.raises(ValueError, match="not a project checkout"):
        emrf_paths.project_root()
