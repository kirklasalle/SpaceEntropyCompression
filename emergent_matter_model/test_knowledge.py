"""Schema, integrity, persistence, and interface tests for scientific memory."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import emrf.knowledge.service as knowledge_service
import emrf_cli
from emrf.interfaces.api_v2 import API_V2_TOKEN_ENV, create_app
from emrf.knowledge import KnowledgeStore
from emrf.runs import RunStore
from emrf.sdk import EMRFClient, KnowledgeSourceRequest


def _graph() -> dict[str, object]:
    return {
        "$schema": "GRAPH_MEMORY.schema.json",
        "schema_version": "1.0.0",
        "meta": {
            "title": "Test graph",
            "version": "1.0.0",
            "last_updated": "2026-10-11",
            "project": "EMRF",
            "evidence_policy": "Claims require evidence or proposed status.",
        },
        "nodes": [
            {
                "id": "model:parent",
                "type": "Model",
                "kind": "model",
                "name": "Parent",
                "screened": False,
                "evidence_class": "theoretical",
                "evidence_status": "fixture",
                "use_for_empirical_confirmation": False,
            },
            {
                "id": "model:child",
                "type": "Model",
                "kind": "model",
                "name": "Child",
                "evidence_class": "theoretical",
                "evidence_status": "fixture",
                "use_for_empirical_confirmation": False,
            },
            {
                "id": "claim:testable",
                "type": "ScientificClaim",
                "kind": "claim",
                "name": "Testable claim",
                "lifecycle_status": "proposed",
                "conditions": [
                    {
                        "parameter": "acceleration",
                        "operator": "lt",
                        "value": 1.2e-10,
                        "unit": "m / s2",
                    }
                ],
                "evidence_class": "untested",
                "evidence_status": "proposed_untested",
                "use_for_empirical_confirmation": False,
            },
            {
                "id": "source:fixture",
                "type": "LiteratureReference",
                "kind": "source",
                "title": "Fixture source",
                "filePath": "fixture.txt",
                "evidence_class": "published",
                "evidence_status": "fixture",
                "use_for_empirical_confirmation": False,
            },
            {
                "id": "dataset:fixture",
                "type": "Dataset",
                "kind": "dataset",
                "name": "Fixture dataset",
                "evidence_class": "observational",
                "evidence_status": "fixture",
                "use_for_empirical_confirmation": False,
            },
        ],
        "edges": [
            {
                "source": "model:child",
                "target": "model:parent",
                "relation": "inherits_from",
                "overrides": {"screened": True},
                "confidence": 1.0,
                "evidence_class": "theoretical",
                "provenance": "fixture",
            },
            {
                "source": "claim:testable",
                "target": "source:fixture",
                "relation": "cites",
                "confidence": 1.0,
                "evidence_class": "published",
                "provenance": "fixture",
            },
            {
                "source": "claim:testable",
                "target": "model:parent",
                "relation": "conflicts_with",
                "confidence": 0.5,
                "evidence_class": "theoretical",
                "provenance": "fixture",
            },
        ],
    }


@pytest.fixture
def store(tmp_path: Path) -> KnowledgeStore:
    graph_path = tmp_path / "GRAPH_MEMORY.json"
    graph_path.write_text(json.dumps(_graph()), encoding="utf-8")
    schema_path = (
        Path(__file__).parent
        / "src"
        / "emrf"
        / "knowledge"
        / "graph_memory.schema.json"
    )
    return KnowledgeStore(graph_path, schema_path)


def test_repository_graph_and_packaged_seed_are_valid_and_identical():
    root = Path(__file__).resolve().parent.parent
    repository_graph = root / "knowledgebase" / "GRAPH_MEMORY.json"
    packaged_graph = (
        Path(__file__).parent / "src" / "emrf" / "knowledge" / "graph_memory.json"
    )
    schema = root / "knowledgebase" / "GRAPH_MEMORY.schema.json"
    packaged_schema = (
        Path(__file__).parent
        / "src"
        / "emrf"
        / "knowledge"
        / "graph_memory.schema.json"
    )

    assert repository_graph.read_bytes() == packaged_graph.read_bytes()
    assert schema.read_bytes() == packaged_schema.read_bytes()
    report = KnowledgeStore(repository_graph, schema).validate()
    assert report["valid"], report["errors"]
    assert report["nodes"] == 110
    assert report["edges"] == 131


def test_query_and_inheritance_resolution(store: KnowledgeStore):
    result = store.query("testable", kind="claim")
    resolved = store.get_node("model:child", resolve_inheritance=True)

    assert result["count"] == 1
    assert result["nodes"][0]["lifecycle_status"] == "proposed"
    assert resolved["screened"] is True
    assert resolved["name"] == "Child"


def test_validator_rejects_dangling_edges_and_unsupported_claims(
    store: KnowledgeStore,
):
    graph = store.load()
    graph["edges"][0]["target"] = "model:missing"
    claim = next(node for node in graph["nodes"] if node["id"] == "claim:testable")
    claim["lifecycle_status"] = "tested"
    graph["edges"] = [
        edge for edge in graph["edges"] if edge["source"] != "claim:testable"
    ]
    store.graph_path.write_text(json.dumps(graph), encoding="utf-8")

    report = store.validate()

    assert not report["valid"]
    assert any("Unknown target node" in error["message"] for error in report["errors"])
    assert any("has no evidence" in error["message"] for error in report["errors"])


def test_validator_returns_structural_errors_without_crashing(store: KnowledgeStore):
    graph = store.load()
    graph["nodes"] = None
    store.graph_path.write_text(json.dumps(graph), encoding="utf-8")

    report = store.validate()

    assert not report["valid"]
    assert report["nodes"] == 0
    assert any(error["path"] == "$.nodes" for error in report["errors"])


def test_add_source_requires_pinned_snapshot_and_persists_atomically(
    store: KnowledgeStore,
):
    source = store.add_source(
        {
            "id": "source:jacobson-1995",
            "title": "Thermodynamics of Spacetime",
            "authors": ["Ted Jacobson"],
            "year": 1995,
            "doi": "10.1103/PhysRevLett.75.1260",
            "snapshot_sha256": "a" * 64,
            "bibtex": "@article{jacobson1995}",
        }
    )

    assert source["identifiers"]["doi"] == "10.1103/PhysRevLett.75.1260"
    assert store.validate()["valid"]
    assert not store.graph_path.with_suffix(".json.lock").exists()


def test_first_use_initialization_serializes_concurrent_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    graph_path = tmp_path / "knowledge" / "GRAPH_MEMORY.json"
    store = KnowledgeStore(graph_path)
    copying = threading.Event()
    release = threading.Event()
    original_copy = knowledge_service.shutil.copyfileobj

    def blocked_copy(source, destination):
        copying.set()
        assert release.wait(timeout=5)
        original_copy(source, destination)

    monkeypatch.setattr(knowledge_service.shutil, "copyfileobj", blocked_copy)
    read_thread = threading.Thread(target=store.load)
    write_thread = threading.Thread(
        target=lambda: store.add_source(
            {
                "id": "source:concurrent",
                "title": "Concurrent source",
                "authors": ["Researcher"],
                "year": 2026,
                "doi": "10.0000/concurrent",
                "snapshot_sha256": "c" * 64,
                "bibtex": "@article{concurrent}",
            }
        )
    )
    read_thread.start()
    assert copying.wait(timeout=5)
    write_thread.start()
    assert write_thread.is_alive()
    release.set()
    read_thread.join(timeout=5)
    write_thread.join(timeout=5)

    assert not read_thread.is_alive()
    assert not write_thread.is_alive()
    assert store.get_node("source:concurrent")["title"] == "Concurrent source"


def test_packaged_seed_validation_is_portable_without_checkout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(knowledge_service, "project_root", lambda: None)
    store = KnowledgeStore(tmp_path / "knowledge" / "GRAPH_MEMORY.json")

    report = store.validate()

    assert report["valid"], report["errors"]


def test_link_run_creates_hashed_results_and_evidence_edges(
    store: KnowledgeStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    runs = RunStore(tmp_path / "runs")
    record = runs.create("compare-schwarzschild", [])
    (record.path / "result.json").write_text('{"ok": true}', encoding="utf-8")
    runs.begin(record.run_id)
    record = runs.finish(
        record.run_id,
        status="succeeded",
        returncode=0,
        duration_seconds=0.1,
    )
    monkeypatch.setattr("emrf_run_access.run_store", lambda: runs)

    report = store.link_run(
        record.run_id,
        claim_ids=("claim:testable",),
        source_ids=("source:fixture",),
        dataset_ids=("dataset:fixture",),
    )
    graph = store.load()

    assert report["artifacts"] >= 2
    assert any(node["kind"] == "run" for node in graph["nodes"])
    assert any(node["kind"] == "result" for node in graph["nodes"])
    assert any(edge["relation"] == "uses_dataset" for edge in graph["edges"])
    assert store.validate()["valid"]


def test_link_run_rejects_mutable_runs_and_wrong_semantic_kinds(
    store: KnowledgeStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    runs = RunStore(tmp_path / "runs")
    pending = runs.create("compare-schwarzschild", [])
    monkeypatch.setattr("emrf_run_access.run_store", lambda: runs)

    with pytest.raises(ValueError, match="must be terminal"):
        store.link_run(pending.run_id)

    runs.begin(pending.run_id)
    runs.finish(
        pending.run_id,
        status="succeeded",
        returncode=0,
        duration_seconds=0.1,
    )
    with pytest.raises(ValueError, match="Expected claim nodes"):
        store.link_run(
            pending.run_id,
            claim_ids=("dataset:fixture",),
        )


def test_link_run_rejects_changed_published_artifact(
    store: KnowledgeStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    runs = RunStore(tmp_path / "runs")
    record = runs.create("compare-schwarzschild", [])
    artifact = record.path / "result.json"
    artifact.write_text('{"value": 1}', encoding="utf-8")
    runs.begin(record.run_id)
    runs.finish(
        record.run_id,
        status="succeeded",
        returncode=0,
        duration_seconds=0.1,
    )
    monkeypatch.setattr("emrf_run_access.run_store", lambda: runs)
    store.link_run(record.run_id)
    artifact.write_text('{"value": 2}', encoding="utf-8")

    with pytest.raises(OSError, match="changed after publication"):
        store.link_run(record.run_id)


def test_sdk_cli_and_v2_knowledge_parity(
    store: KnowledgeStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr(EMRFClient, "_knowledge_store", staticmethod(lambda: store))
    direct = EMRFClient().query_knowledge("testable", kind="claim").to_dict()

    assert emrf_cli.main(["kb", "query", "testable", "--kind", "claim", "--json"]) == 0
    cli = json.loads(capsys.readouterr().out)

    token = "phase-seven-test-token"
    monkeypatch.setenv(API_V2_TOKEN_ENV, token)
    client = TestClient(create_app())
    response = client.get(
        "/api/v2/knowledge",
        params={"text": "testable", "kind": "claim"},
    )
    assert response.status_code == 200
    assert response.json() == cli == direct

    source_payload = KnowledgeSourceRequest(
        source_id="source:api-test",
        title="API test",
        authors=("Researcher",),
        year=2026,
        snapshot_sha256="b" * 64,
        bibtex="@article{api2026}",
        arxiv="2610.00001",
    )
    denied = client.post(
        "/api/v2/knowledge/sources",
        json={**source_payload.to_dict(), "id": source_payload.source_id},
    )
    allowed = client.post(
        "/api/v2/knowledge/sources",
        headers={"Authorization": f"Bearer {token}"},
        json={**source_payload.to_dict(), "id": source_payload.source_id},
    )

    assert denied.status_code == 401
    assert allowed.status_code == 201
    assert allowed.json()["id"] == "source:api-test"
    assert client.get("/api/v2/knowledge/validate").json()["valid"]

    output = tmp_path / "export.json"
    assert emrf_cli.main(["kb", "export", "--output", str(output)]) == 0
    assert output.is_file()
