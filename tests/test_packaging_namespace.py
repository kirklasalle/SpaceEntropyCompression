from __future__ import annotations

import data_provenance as legacy_provenance
import physics_baseline as legacy_baselines
import pytest
from emrf import API_VERSION, __version__
from emrf.data import provenance as packaged_provenance
from emrf.interfaces.api import app as packaged_app
from emrf.interfaces.api import run_simulation as packaged_run_simulation
from emrf.interfaces.cli import main
from emrf.interfaces.registry import COMMANDS as packaged_commands
from emrf.interfaces.registry import run_command as packaged_run_command
from emrf.physics import EmergentMatterModel as PackagedModel
from emrf.physics import baselines as packaged_baselines
from emrf_registry import COMMANDS as legacy_commands
from emrf_registry import run_command as legacy_run_command
from model import EmergentMatterModel as LegacyModel
from server import app as legacy_app
from server import run_simulation as legacy_run_simulation


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


def test_api_interface_preserves_legacy_application_identity() -> None:
    assert packaged_app is legacy_app
    assert packaged_run_simulation is legacy_run_simulation


def test_registry_interface_preserves_legacy_object_identity() -> None:
    assert packaged_commands is legacy_commands
    assert packaged_run_command is legacy_run_command
