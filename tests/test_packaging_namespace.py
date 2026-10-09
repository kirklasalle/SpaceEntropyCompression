from __future__ import annotations

import pytest
from emrf import API_VERSION, __version__
from emrf.interfaces.cli import main


def test_public_namespace_exposes_version_contract() -> None:
    assert __version__ == "0.9.1"
    assert API_VERSION == "v1"


def test_console_entry_point_supports_version(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == "emrf 0.9.1"
