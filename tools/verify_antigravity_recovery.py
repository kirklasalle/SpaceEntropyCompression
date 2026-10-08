"""Verify recovered evidence bytes, graph references and selected historical arithmetic."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs" / "archive" / "antigravity_recovery"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(brain: Path | None = None) -> dict:
    manifest = json.loads((ARCHIVE / "manifest.json").read_text())
    source_checks = 0
    for record in manifest["records"]:
        destination = ROOT / record["destination"]
        if sha(destination) != record["sha256"]:
            raise ValueError(f"Recovered artifact changed: {destination}")
        if brain is not None:
            source = brain / record["source_relative_path"]
            expected = record.get("source_sha256", record["sha256"])
            if sha(source) != expected:
                raise ValueError(f"Original source changed: {source}")
            source_checks += 1
    for record in manifest["derived_extracts"]:
        if sha(ROOT / record["destination"]) != record["sha256"]:
            raise ValueError("Derived extract changed")
    graph = json.loads((ROOT / "knowledgebase" / "GRAPH_MEMORY.json").read_text())
    snapshot = ROOT / graph["meta"]["pre_recovery_snapshot"]
    if sha(snapshot) != graph["meta"]["pre_recovery_sha256"]:
        raise ValueError("Historical graph snapshot changed")
    old = json.loads(snapshot.read_text())
    ids = {n["id"] for n in graph["nodes"]}
    if len(ids) != len(graph["nodes"]) or not {n["id"] for n in old["nodes"]} <= ids:
        raise ValueError("Graph lost old nodes or contains duplicates")
    for edge in graph["edges"]:
        if edge["source"] not in ids or edge["target"] not in ids:
            raise ValueError("Dangling graph edge")
    claims = json.loads((ROOT / "knowledgebase" / "antigravity_recovery_claims.json").read_text())
    for claim in claims["claims"]:
        node = next(n for n in graph["nodes"] if n["id"] == claim["id"])
        if node["source_sha256"] != sha(ROOT / claim["source"]):
            raise ValueError("Claim source hash mismatch")
        if node["use_for_empirical_confirmation"]:
            raise ValueError("Recovered claims are not new empirical confirmation")
    quantum_ratio, integration_error = quad(
        lambda x: 2*math.pi*x*x*math.exp(-2*x)/(1+x)**2, 0, math.inf, epsabs=1e-12)
    radius = 2*6.67430e-11*(1e-18*1.98847e30)/299792458**2
    return {
        "preserved_records_verified": len(manifest["records"]),
        "derived_extracts_verified": len(manifest["derived_extracts"]),
        "original_source_hashes_verified": source_checks,
        "graph_nodes": len(ids), "graph_edges": len(graph["edges"]),
        "recovery_claims": len(claims["claims"]),
        "historical_nodes_preserved": len(old["nodes"]),
        "arithmetic_checks": {
            "evidence_type": "mathematical_diagnostic_not_observations",
            "quantum_unnormalized_mass_ratio": quantum_ratio,
            "integration_estimated_error": integration_error,
            "schwarzschild_radius_m_for_1e_minus18_solar_masses": radius,
            "historical_table_radius_m": 2.95e-45,
            "interpretation": "Normalization identity and historical table error, not new physics",
        },
        "verification_script_sha256": sha(Path(__file__)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brain", type=Path)
    args = parser.parse_args()
    result = verify(args.brain)
    destination = ROOT / "results" / "antigravity_recovery_verification.json"
    destination.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
