"""Check the review packet's provenance and gates, not candidate physics."""
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def test_direction_approval_does_not_claim_implementation_or_validation():
    ledger = json.loads(
        (ROOT / "knowledgebase" / "thermodynamic_collision_candidates.json").read_text())
    assert ledger["author_approved"] is True
    assert ledger["author_decision"]["selected_candidate"] == "candidate-a"
    assert ledger["author_decision"]["specific_functional_selected"] is False
    assert "direction only" in ledger["approval_scope"]
    assert ledger["new_mechanism_implemented"] is False
    assert ledger["empirically_validated"] is False
    assert ledger["review_gate"]["state"] == "candidate_a_selected_functional_pending"
    sources = {s["id"] for s in ledger["sources"]}
    ids = [c["id"] for c in ledger["claims"]]
    assert len(ids) == len(set(ids))
    for claim in ledger["claims"]:
        assert set(claim["sources"]) <= sources
        assert claim["attribution"] and claim["limitation"]
    candidate = next(c for c in ledger["claims"] if c["id"] == "candidate-b")
    assert candidate["classification"] == "proposed"
    assert candidate["selection_status"] == "not_selected_retained_for_history"
    assert "AI-proposed" in candidate["attribution"]
    identity = next(c for c in ledger["claims"] if c["id"] == "candidate-b-conditional-identity")
    assert identity["classification"] == "derived_conditionally"
    assert len(identity["assumptions"]) >= 6


def test_candidate_graph_nodes_and_edges_are_qualified():
    graph = json.loads((ROOT / "knowledgebase" / "GRAPH_MEMORY.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert len(nodes) == len(graph["nodes"])
    candidates = [n for n in nodes.values() if n["id"].startswith("candidate:collision_")]
    assert len(candidates) == 3
    assert all(n["use_for_empirical_confirmation"] is False for n in candidates)
    for edge in graph["edges"]:
        assert edge["source"] in nodes and edge["target"] in nodes
        if edge["source"].startswith("candidate:collision_"):
            assert edge["relation"] != "validated_by"
    review = graph["meta"]["collision_candidate_review"]
    assert review["state"] == "candidate_a_selected_functional_pending"
    assert review["selected_candidate"] == "candidate:collision_geometry_reference"
    assert nodes["candidate:collision_exchange_channel"]["status"] == (
        "not_selected_retained_for_history")
    assert review["new_mechanism_implemented"] is False


def test_specification_local_links_and_explicit_stopping_point():
    path = ROOT / "docs" / "EMRF_COLLISION_CANDIDATE_SPECIFICATION.md"
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / unquote(target.split("#")[0])).exists()
    assert "Stop here for functional review" in text
    assert "not Kirk's" in text
    assert "no identifiable unique prediction yet" in text
    assert "not a derivation" in text
