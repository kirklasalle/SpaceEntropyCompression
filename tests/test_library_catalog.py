from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "knowledgebase" / "library"


def _load(name: str) -> dict:
    return json.loads((LIBRARY / name).read_text(encoding="utf-8"))


def test_data_catalog_has_unique_ids_and_required_provenance() -> None:
    datasets = _load("data_catalog.json")["datasets"]
    ids = [entry["id"] for entry in datasets]
    assert len(ids) == len(set(ids))
    assert {
        "sparc-rotation-curves",
        "pantheon-plus-shoes",
        "desi-dr1-bao",
        "desi-dr2-bao",
        "des-sn5yr",
        "union3-unity",
        "planck-2018-likelihood",
        "gwtc-catalogs",
        "gaia-chae-dr3-wide-binaries",
        "codata-2022",
    } <= set(ids)
    for entry in datasets:
        assert entry["url"].startswith("https://")
        assert entry["priority"] in {"high", "medium", "low"}
        assert entry["status"] in {"existing_holding", "planned"}
        assert entry["citation"]
        assert entry["license_terms_url"].startswith("https://")
        assert entry["redistribution"]
        assert entry["acquisition"]
        assert entry["verified"]
        if entry.get("holdings"):
            assert entry.get("version")
        for holding in entry.get("holdings", []):
            assert len(holding["sha256"]) == 64
            assert holding["url"].startswith("https://")


def test_gaia_wide_binary_source_is_exactly_pinned() -> None:
    datasets = _load("data_catalog.json")["datasets"]
    gaia = next(
        entry for entry in datasets if entry["id"] == "gaia-chae-dr3-wide-binaries"
    )

    assert gaia["status"] == "existing_holding"
    assert gaia["version"] == "zenodo-8270396"
    assert gaia["data_doi"] == "10.5281/zenodo.8270396"
    assert gaia["verified"]["license"] == "cc-by-4.0"
    assert {holding["path"]: holding["sha256"] for holding in gaia["holdings"]} == {
        "data/external/gaia_wide_binaries/gaia_dr3_MSMS_d200pc.csv": (
            "0b10a6e66d59bc781c0902a3cd3dc2c37db5ffdc9677113e0cdd54f9c80d6804"
        ),
        "data/external/gaia_wide_binaries/READMEv2": (
            "a9c83bee209460b82c21171af03aed883d694cddcc40dcb543739987e2b13990"
        ),
        "data/external/gaia_wide_binaries/accel_ortho_wb_v2.py": (
            "69a989c6677c9dd733e9c932ad11b3d65d0773c11404457dd7b16e8b46767e26"
        ),
        "data/external/gaia_wide_binaries/accel_plane_ortho_wb_v2.py": (
            "052cced94956ebd178c04550a34f9eddba7b90bb0919b78993af1c0472a9a13b"
        ),
        "data/external/gaia_wide_binaries/run_wb_v2.py": (
            "79153971387aea0d466edafc33828789ac70015ea55c9b384a0db695d34dd430"
        ),
        "data/external/gaia_wide_binaries/make_Newton_sample_gaia.py": (
            "e92c35b5aa9519a3f07880a099abad05e9aee3add39d66421c98b935853f7f8f"
        ),
        "data/external/gaia_wide_binaries/M_MagG_polyfit_V_Ic.dat": (
            "9dee3bde5356254c028d50e933b2005bd0b6ce7dd4a78a376f100f3cb617ed11"
        ),
        "data/external/gaia_wide_binaries/MagG_M_polyfit_V_Ic.dat": (
            "6c0bbf9017cf64435205994f960bde731f23a02a055ee53490d6627e7f962545"
        ),
        "data/external/gaia_wide_binaries/M_MagG_polyfit_J_Bp_Rp.dat": (
            "2567bd22e638663bd732f2c0aef3b7a2b3ecd9c0cadf48ffbc87f48b6a9a8aeb"
        ),
        "data/external/gaia_wide_binaries/MagG_M_polyfit_J_Bp_Rp.dat": (
            "03c37afa4963b2abbe72ac302c5ee70b6ead554286923978e4275c17a9240134"
        ),
        "data/external/gaia_wide_binaries/M_MagG_polyfit_F.dat": (
            "a5aebecfded9a2d4627a4f1ef6378f435f4e521abc56812ec183b33c6fb492f5"
        ),
        "data/external/gaia_wide_binaries/MagG_M_polyfit_F.dat": (
            "e74acde941d32b6087aa04f3577be1382eba83bbd0291f73178ee5cb0aeebc82"
        ),
    }


def test_software_catalog_has_unique_ids_and_licences() -> None:
    packages = _load("software_catalog.json")["packages"]
    ids = [entry["id"] for entry in packages]
    assert len(ids) == len(set(ids))
    assert {
        "python",
        "numpy",
        "scipy",
        "pytest",
        "hypothesis",
        "brainsimiii-uks",
    } <= set(ids)
    for entry in packages:
        assert entry["status"] in {"adopted", "evaluated"}
        assert entry["url"].startswith("https://")
        assert entry["role"]
        assert entry["license"]
