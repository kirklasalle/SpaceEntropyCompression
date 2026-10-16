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
    decision = ledger["author_decision"]
    assert decision["selected_candidates"] == ["candidate-a", "candidate-b"]
    assert decision["active_candidate"] == "candidate-b"
    assert decision["active_candidate"] in decision["selected_candidates"]
    assert decision["work_policy"] == "one_candidate_at_a_time"
    assert ledger["author_decision_history"][0]["selected_candidate"] == "candidate-a"
    assert ledger["author_decision"]["specific_functional_selected"] is False
    assert "not physical validation" in ledger["approval_scope"]
    assert ledger["new_mechanism_implemented"] is False
    assert ledger["empirically_validated"] is False
    assert ledger["review_gate"]["state"] == "candidates_a_b_selected_b_active"
    sources = {s["id"] for s in ledger["sources"]}
    ids = [c["id"] for c in ledger["claims"]]
    assert len(ids) == len(set(ids))
    for claim in ledger["claims"]:
        assert set(claim["sources"]) <= sources
        assert claim["attribution"] and claim["limitation"]
    candidate = next(c for c in ledger["claims"] if c["id"] == "candidate-b")
    assert candidate["classification"] == "proposed"
    assert candidate["selection_status"] == "selected_active_restricted_test_preparation"
    assert "AI-proposed" in candidate["attribution"]
    parallel = ledger["parallel_exploration"]
    assert parallel["candidate_a_selection_changed"] is False
    assert parallel["candidate_b_selected"] is True
    interaction = parallel["worked_interaction"]
    assert interaction["status"] == "author_selected_restricted_test_hypothesis"
    assert set(interaction["comparison_sources"]) <= sources
    assert "unspecified" in interaction["energy_source_status"]
    assert any(
        decision["subject"] == "status of the worked Higgs-portal hypothesis"
        for decision in parallel["author_decisions"]
    )
    assert interaction["geometry_benchmark"]["extra_spatial_dimensions"] == 1
    assert interaction["geometry_benchmark"]["radius_selected_or_measured"] is False
    limit = interaction["independent_constraint"]
    assert "restricted-model likelihood-based bound only" in limit["numerical_status"]
    assert ("no likelihood-based numerical coupling limit is claimed for the general Candidate B"
            in limit["numerical_status"])
    assert "kappa_min" in limit["mixing_envelope"]
    assert "R>0" in limit["validity_domain"]
    assert "O_H^2" in limit["low_energy_operator"]
    assert "widths" in limit["near_degeneracy_treatment"]
    domain = limit["source_bounded_domain"]
    assert domain["gravitational_extra_dimension_bounds_applied"] is False
    assert "130 GeV to 3 TeV" in domain["direct_resonance_example"]
    likelihood = limit["likelihood_contract"]
    assert set(likelihood["sources"]) <= sources
    assert likelihood["evaluated"] == "partial"
    assert set(likelihood["channel_status"]) == set(likelihood["channels"])
    assert likelihood["channel_status"][likelihood["channels"][1]].startswith("not evaluated")
    assert "95% upper-limit curves" in likelihood["forbidden_shortcut"]
    assert limit["full_kk_tower_constrained"] is False
    assert limit["new_data_test_or_simulation_run"] is True
    test = parallel["selected_restricted_test"]
    assert test["preregistration"]["frozen_before_contour_coordinates_retrieved"] is True
    assert test["outcome"] in {"compatible_with_limit", "incompatible"}
    assert test["likelihood_evaluated"] is False
    assert test["one_parameter_interval_claimed"] is False
    assert test["candidate_b_confirmed"] is False
    for path in (test["protocol"], test["preregistration"]["path"], *test["scripts"],
                 *test["artifacts"]):
        assert (ROOT / path).is_file()
    result = json.loads((ROOT / test["artifacts"][1]).read_text(encoding="utf-8"))
    assert result["outcome"] == test["outcome"]
    assert round(result["kappa_lo"], 5) == test["kappa_lo"]
    assert result["preregistration_sha256"] == test["preregistration"]["sha256"]
    extended = parallel["selected_extended_tests"]
    assert extended["preregistration"]["frozen_before_likelihood_scan_or_cms_limit_values_read"]
    assert extended["preregistration"]["parent_sha256"] == test["preregistration"]["sha256"]
    assert extended["candidate_b_confirmed"] is False
    for path in (extended["preregistration"]["path"], extended["theory_inputs"]["path"],
                 *extended["scripts"], *extended["artifacts"]):
        assert (ROOT / path).is_file()
    rate = json.loads((ROOT / extended["artifacts"][0]).read_text(encoding="utf-8"))
    cms = json.loads((ROOT / extended["artifacts"][1]).read_text(encoding="utf-8"))
    for artifact in (rate, cms):
        assert artifact["preregistration_sha256"] == extended["preregistration"]["sha256"]
        assert artifact["candidate_b_confirmed"] is False
    assert cms["theory_inputs_sha256"] == extended["theory_inputs"]["sha256"]
    test_a = extended["test_a_higgs_rate_likelihood"]
    assert rate["outcome"] == test_a["outcome"]
    assert round(rate["kappa_lo"], 5) == test_a["kappa_lo"]
    assert rate["likelihood_evaluated"] is test_a["likelihood_evaluated"] is True
    test_b = extended["test_b_cms_direct_resonance"]
    assert cms["summary"]["outcomes"] == test_b["outcomes"]
    assert cms["likelihood_evaluated"] is test_b["likelihood_evaluated"] is False
    binding = {(row["inverse_radius_GeV"], row["m5_GeV"]) for row in cms["grid"]
               if row["combined_binding_constraint"] == "cms_direct"}
    assert binding == {(p["inverse_radius_GeV"], p["m5_GeV"]) for p in test_b["cms_binding_points"]}
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
    assert review["state"] == "candidates_a_b_selected_b_active"
    assert review["selected_candidates"] == [
        "candidate:collision_geometry_reference", "candidate:collision_exchange_channel"]
    assert review["active_candidate"] == "candidate:collision_exchange_channel"
    assert review["work_policy"] == "one_candidate_at_a_time"
    assert nodes["candidate:collision_exchange_channel"]["status"] == (
        "selected_active_restricted_test_preparation")
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

    contract = (
        ROOT / "docs" / "engineering" / "CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md"
    ).read_text(encoding="utf-8")
    assert "## 12. Source-bounded parameter domain" in contract
    assert "## 13. Model-specific likelihood contract" in contract
    assert "No likelihood has been evaluated here" in contract
    assert not any(marker in contract for marker in ("â", "Ã", "Â"))
