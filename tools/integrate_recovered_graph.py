"""Integrate curated recovery claims without resurrecting historical validation labels."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    graph_path = ROOT / "knowledgebase" / "GRAPH_MEMORY.json"
    snapshot = ROOT / "docs" / "archive" / "antigravity_recovery" / "graph_memory_before_recovery.json"
    current = graph_path.read_bytes()
    graph = json.loads(current)
    if not snapshot.exists():
        if graph["meta"].get("recovery_integrated"):
            raise ValueError("Cannot create historical snapshot from an already integrated graph")
        snapshot.write_bytes(current)
    claims = json.loads((ROOT / "knowledgebase" / "antigravity_recovery_claims.json").read_text())
    if not graph["meta"].get("recovery_integrated"):
        graph["meta"]["historical_summary"] = graph["meta"]["summary"]
        for node in graph["nodes"]:
            node["historical_status"] = node.get("status")
            node["evidence_status"] = "legacy_record_requires_source_specific_review"
            node["use_for_empirical_confirmation"] = False
            if node.get("status") == "Standard Physics":
                node["evidence_status"] = "standard_formula_not_EMRF_validation"
            elif (node.get("type") in ("EmpiricalDataset", "ObservationalDataset", "Dataset")
                  and "Ingested" in node.get("status", "")):
                node["status"] = "Historical ingestion claim; not authenticated by this graph"
            elif "Empirically Confirmed" in node.get("status", ""):
                node["status"] = "Withdrawn historical confirmation claim"
            elif "Verified" in node.get("status", "") or "Ratified" in node.get("status", ""):
                node["status"] = "Historical implementation/audit claim; not physical verification"
        for edge in graph["edges"]:
            edge["evidence_status"] = "historical_relationship_not_new_confirmation"
            if edge["relation"] == "validated_by":
                edge["historical_relation"] = edge["relation"]
                edge["relation"] = "historically_claimed_validated_by"
    recovery_ids = {c["id"] for c in claims["claims"]}
    graph["nodes"] = [n for n in graph["nodes"] if n["id"] not in recovery_ids]
    graph["edges"] = [e for e in graph["edges"] if e["source"] not in recovery_ids]
    for claim in claims["claims"]:
        source = ROOT / claim["source"]
        if not source.is_file():
            raise FileNotFoundError(source)
        node = {
            "id": claim["id"], "type": claim["kind"], "name": claim["name"],
            "description": claim["statement"], "status": claim["status"],
            "attribution": claim["attribution"], "limitation": claim["limitation"],
            "filePath": claim["source"], "locator": claim["locator"],
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "use_for_empirical_confirmation": False,
            "evidence_status": "curated_historical_recovery",
        }
        graph["nodes"].append(node)
        for target in claim["connects_to"]:
            graph["edges"].append({"source": claim["id"], "target": target,
                                   "relation": "clarifies_or_qualifies",
                                   "evidence_status": "documented_interpretive_link_not_validation"})
    graph["meta"].update(
        version="2.1.0", last_updated="2026-10-08", recovery_integrated=True,
        repository=str(ROOT),
        notes="Archive recovery preserves source provenance and qualifications. Historical nodes are not evidence of current empirical validation.",
        summary="Research graph with 10 curated Antigravity recovery claims; original C families, downstream thermodynamics, multi-star design and implementation history. Historical empirical certification labels are not endorsed.",
        evidence_policy="Do not infer physics validation from old status, description, dataset names or test counts. Consult evidence_status, curated recovery claims and current real-data reports.",
        current_reports=["docs/ANTIGRAVITY_RECOVERY_AUDIT.md",
                         "docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md",
                         "docs/SPARC_FRESH_RESULTS.md",
                         "results/real_data_followup/pantheon_baseline.json"],
        pre_recovery_snapshot=str(snapshot.relative_to(ROOT)),
        pre_recovery_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    )
    ids = [n["id"] for n in graph["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate graph node IDs")
    if any(e["source"] not in ids or e["target"] not in ids for e in graph["edges"]):
        raise ValueError("Dangling graph edge")
    graph_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"Integrated {len(claims['claims'])} qualified claims; {len(ids)} nodes, {len(graph['edges'])} edges")


if __name__ == "__main__":
    main()
