from __future__ import annotations

import data_provenance as legacy_provenance
import physics_baseline as legacy_baselines
import pytest
from emrf import API_VERSION, __version__
from emrf.data import provenance as packaged_provenance
from emrf.interfaces.cli import main
from emrf.physics import EmergentMatterModel as PackagedModel
from emrf.physics import baselines as packaged_baselines
from model import EmergentMatterModel as LegacyModel


def test_public_namespace_exposes_version_contract() -> None:
    assert __version__ == "0.9.1"
    assert API_VERSION == "v1"


def test_console_entry_point_supports_version(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == "emrf 0.9.1"


def test_physics_namespace_preserves_legacy_model_identity() -> None:
    assert PackagedModel is LegacyModel


def test_physics_baselines_preserve_legacy_function_identity() -> None:
    assert packaged_baselines.solve_kepler is legacy_baselines.solve_kepler
    assert (
        packaged_baselines.kretschmann_invariant
        is legacy_baselines.kretschmann_invariant
    )
    assert packaged_baselines.G == legacy_baselines.G


def test_data_provenance_preserves_legacy_function_identity() -> None:
    assert (
        packaged_provenance.verify_observation_file
        is legacy_provenance.verify_observation_file
    )
    assert packaged_provenance.is_synthetic is legacy_provenance.is_synthetic
    assert packaged_provenance.SYNTHETIC_MARKER == legacy_provenance.SYNTHETIC_MARKER
