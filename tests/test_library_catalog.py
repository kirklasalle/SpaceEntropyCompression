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
        "gaia-elbadry-wide-binaries",
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
        for holding in entry.get("holdings", []):
            assert len(holding["sha256"]) == 64


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
