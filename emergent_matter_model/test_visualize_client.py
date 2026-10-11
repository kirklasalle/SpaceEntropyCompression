"""Compatibility tests for the supported Python visualization client."""

from __future__ import annotations

from unittest.mock import Mock

import requests

import visualize


def test_visualize_cli_can_select_online_and_offline_modes():
    parser = visualize.build_parser()

    assert parser.parse_args([]).offline is True
    assert parser.parse_args(["--offline"]).offline is True
    assert parser.parse_args(["--online"]).offline is False


def test_online_visualizer_uses_v1_simulation_contract(tmp_path, monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "M": [[[[1.0]], [[2.0]]], [[[3.0]], [[4.0]]]]
    }
    post = Mock(return_value=response)
    monkeypatch.setattr(visualize.requests, "post", post)
    output = tmp_path / "online.png"

    visualize.run_simulation(
        server="http://example.test",
        resolution=2,
        offline=False,
        save_fig=str(output),
    )

    assert output.is_file()
    assert output.stat().st_size > 0
    assert post.call_args.args[0] == "http://example.test/api/v1/simulate"
    payload = post.call_args.kwargs["json"]
    assert payload["n"] == 4
    assert payload["weights"] == [0.40, 0.40, 0.10, 0.10]
    assert payload["X_grid"][2] == [0.5]
    assert payload["X_grid"][3] == [0.4]


def test_online_visualizer_falls_back_without_losing_output(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(
        visualize.requests,
        "post",
        Mock(side_effect=requests.ConnectionError("offline")),
    )
    output = tmp_path / "fallback.png"

    visualize.run_simulation(
        resolution=4,
        offline=False,
        save_fig=str(output),
    )

    assert output.is_file()
    assert "using the local calculation" in capsys.readouterr().err
