"""Crash-safe operations for the versioned EMRF scientific knowledge graph."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import time
from collections.abc import Mapping
from contextlib import suppress
from copy import deepcopy
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

from emrf.core.errors import IntegrityError, StorageError
from emrf_paths import app_root, project_root

_NODE_ID = re.compile(r"^[a-z][a-z0-9_-]*:[a-z0-9][a-z0-9_.-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_EVIDENCE_RELATIONS = {
    "cites",
    "evaluates",
    "produced",
    "refutes",
    "supports",
    "tests",
    "uses_dataset",
}


class KnowledgeStore:
    """Load, validate, query, and atomically update scientific memory."""

    def __init__(
        self,
        graph_path: str | Path | None = None,
        schema_path: str | Path | None = None,
    ) -> None:
        self.graph_path = (
            Path(graph_path).resolve()
            if graph_path is not None
            else self._default_graph_path()
        )
        self.schema_path = (
            Path(schema_path).resolve()
            if schema_path is not None
            else Path(str(files("emrf.knowledge").joinpath("graph_memory.schema.json")))
        )

    @staticmethod
    def _default_graph_path() -> Path:
        checkout = project_root()
        if checkout is not None:
            return cast(Path, checkout / "knowledgebase" / "GRAPH_MEMORY.json")
        return cast(Path, app_root() / "knowledgebase" / "GRAPH_MEMORY.json")

    def load(self) -> dict[str, Any]:
        self._initialize()
        try:
            value = json.loads(self.graph_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Could not read knowledge graph: {self.graph_path}") from exc
        if not isinstance(value, dict):
            raise IntegrityError("Knowledge graph root must be a JSON object")
        return value

    def validate(self) -> dict[str, Any]:
        graph = self.load()
        schema = self._load_schema()
        schema_errors = sorted(
            Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            ).iter_errors(graph),
            key=lambda item: _json_path(item.absolute_path),
        )
        errors = [
            {
                "path": _json_path(error.absolute_path),
                "message": error.message,
            }
            for error in schema_errors
        ]
        if not schema_errors:
            errors.extend(self._semantic_errors(graph, graph_path=self.graph_path))
        nodes = graph.get("nodes")
        edges = graph.get("edges")
        return {
            "valid": not errors,
            "schema_version": graph.get("schema_version"),
            "graph_path": str(self.graph_path),
            "nodes": len(nodes) if isinstance(nodes, list) else 0,
            "edges": len(edges) if isinstance(edges, list) else 0,
            "errors": errors,
        }

    def query(
        self,
        text: str | None = None,
        *,
        kind: str | None = None,
        lifecycle_status: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        valid_kinds = {
            "concept",
            "equation",
            "dataset",
            "source",
            "software",
            "model",
            "run",
            "result",
            "claim",
            "decision",
        }
        valid_lifecycles = {
            "proposed",
            "tested",
            "supported",
            "refuted",
            "retracted",
        }
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        if kind is not None and kind not in valid_kinds:
            raise ValueError(f"Unknown knowledge kind: {kind}")
        if lifecycle_status is not None and lifecycle_status not in valid_lifecycles:
            raise ValueError(f"Unknown claim lifecycle: {lifecycle_status}")
        graph = self.load()
        needle = None if text is None else text.strip().casefold()
        if text is not None and not needle:
            raise ValueError("text must be non-empty when provided")
        rows: list[dict[str, Any]] = []
        for node in graph["nodes"]:
            if kind is not None and node.get("kind") != kind:
                continue
            if (
                lifecycle_status is not None
                and node.get("lifecycle_status") != lifecycle_status
            ):
                continue
            if needle is not None and needle not in json.dumps(
                node,
                sort_keys=True,
            ).casefold():
                continue
            rows.append(deepcopy(node))
            if len(rows) == limit:
                break
        return {"nodes": rows, "count": len(rows)}

    def get_node(self, node_id: str, *, resolve_inheritance: bool = False) -> dict[str, Any]:
        graph = self.load()
        nodes = {node["id"]: node for node in graph["nodes"]}
        if node_id not in nodes:
            raise KeyError(f"Unknown knowledge node: {node_id}")
        if not resolve_inheritance:
            return deepcopy(nodes[node_id])
        return self._resolve_node(node_id, nodes, graph["edges"], ())

    def add_source(self, source: Mapping[str, Any]) -> dict[str, Any]:
        node = self._source_node(source)
        self._initialize()
        with self._lock():
            graph = self.load()
            if any(item["id"] == node["id"] for item in graph["nodes"]):
                raise ValueError(f"Knowledge node already exists: {node['id']}")
            graph["nodes"].append(node)
            self._validate_or_raise(graph)
            self._write(graph)
        return deepcopy(node)

    def export(self, destination: str | Path) -> dict[str, Any]:
        graph = self.load()
        self._validate_or_raise(graph)
        output = Path(destination).expanduser().resolve()
        if output == self.graph_path:
            raise ValueError("Export destination must differ from the active graph")
        self._write_json(output, graph)
        return {
            "path": str(output),
            "sha256": _file_sha256(output),
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
        }

    def link_run(
        self,
        run_id: str,
        *,
        claim_ids: tuple[str, ...] = (),
        source_ids: tuple[str, ...] = (),
        dataset_ids: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        from emrf_run_access import run_store

        try:
            record = run_store().get(run_id)
        except KeyError:
            raise KeyError(f"Unknown run: {run_id}") from None
        if record.status not in {"succeeded", "failed", "timed_out", "interrupted"}:
            raise ValueError(
                f"Run must be terminal before evidence linking: {record.status}"
            )
        artifacts = tuple(
            path
            for path in sorted(record.path.rglob("*"))
            if path.is_file() and not path.is_symlink() and path.name != "run.json"
        )
        self._initialize()
        with self._lock():
            graph = self.load()
            nodes_by_id = {node["id"]: node for node in graph["nodes"]}
            known = set(nodes_by_id)
            requested = set(claim_ids) | set(source_ids) | set(dataset_ids)
            missing = sorted(requested - known)
            if missing:
                raise KeyError(f"Unknown knowledge nodes: {', '.join(missing)}")
            self._require_kinds(nodes_by_id, claim_ids, "claim")
            self._require_kinds(nodes_by_id, source_ids, "source")
            self._require_kinds(nodes_by_id, dataset_ids, "dataset")
            run_node_id = f"run:{run_id.casefold()}"
            additions = 0
            if run_node_id not in known:
                graph["nodes"].append(
                    {
                        "id": run_node_id,
                        "type": "ScientificRun",
                        "kind": "run",
                        "name": f"{record.command} run {run_id}",
                        "run_id": run_id,
                        "command": record.command,
                        "status": record.status,
                        "evidence_class": record.evidence_class,
                        "evidence_status": "durable_run_record",
                        "use_for_empirical_confirmation": False,
                    }
                )
                known.add(run_node_id)
                additions += 1
            for artifact in artifacts:
                relative = artifact.relative_to(record.path).as_posix()
                result_id = f"result:{hashlib.sha256(f'{run_id}:{relative}'.encode()).hexdigest()}"
                digest = _file_sha256(artifact)
                existing = next(
                    (
                        node
                        for node in graph["nodes"]
                        if node.get("run_id") == run_id
                        and node.get("artifact_path") == relative
                    ),
                    None,
                )
                if existing is not None and existing.get("sha256") != digest:
                    raise IntegrityError(
                        f"Linked run artifact changed after publication: {relative}"
                    )
                if result_id not in known:
                    graph["nodes"].append(
                        {
                            "id": result_id,
                            "type": "RunArtifact",
                            "kind": "result",
                            "name": relative,
                            "run_id": run_id,
                            "artifact_path": relative,
                            "sha256": digest,
                            "bytes": artifact.stat().st_size,
                            "evidence_class": record.evidence_class,
                            "evidence_status": "immutable_run_artifact",
                            "use_for_empirical_confirmation": False,
                        }
                    )
                    known.add(result_id)
                    additions += 1
                _append_edge(
                    graph,
                    run_node_id,
                    result_id,
                    "produced",
                    record.evidence_class,
                    f"run:{run_id}",
                    1.0,
                )
                for claim_id in claim_ids:
                    _append_edge(
                        graph,
                        result_id,
                        claim_id,
                        "tests",
                        record.evidence_class,
                        f"run:{run_id}",
                        1.0,
                    )
            for dataset_id in dataset_ids:
                _append_edge(
                    graph,
                    run_node_id,
                    dataset_id,
                    "uses_dataset",
                    record.evidence_class,
                    f"run:{run_id}",
                    1.0,
                )
            for claim_id in claim_ids:
                for source_id in source_ids:
                    _append_edge(
                        graph,
                        claim_id,
                        source_id,
                        "cites",
                        "published",
                        f"run:{run_id}",
                        1.0,
                    )
            self._validate_or_raise(graph)
            self._write(graph)
        return {
            "run_id": run_id,
            "run_node_id": run_node_id,
            "artifacts": len(artifacts),
            "nodes_added": additions,
        }

    @staticmethod
    def _require_kinds(
        nodes: Mapping[str, Mapping[str, Any]],
        node_ids: tuple[str, ...],
        expected_kind: str,
    ) -> None:
        wrong = sorted(
            node_id
            for node_id in node_ids
            if nodes[node_id].get("kind") != expected_kind
        )
        if wrong:
            raise ValueError(
                f"Expected {expected_kind} nodes, got: {', '.join(wrong)}"
            )

    def _initialize(self) -> None:
        if self.graph_path.is_file():
            return
        with self._lock():
            if self.graph_path.is_file():
                return
            self.graph_path.parent.mkdir(parents=True, exist_ok=True)
            seed = files("emrf.knowledge").joinpath("graph_memory.json")
            staged: Path | None = None
            try:
                with seed.open("rb") as source, tempfile.NamedTemporaryFile(
                    dir=self.graph_path.parent,
                    delete=False,
                ) as temporary:
                    shutil.copyfileobj(source, temporary)
                    temporary.flush()
                    os.fsync(temporary.fileno())
                    staged = Path(temporary.name)
                if self.graph_path.exists():
                    staged.unlink()
                    return
                os.replace(staged, self.graph_path)
                _fsync_directory(self.graph_path.parent)
            except OSError as exc:
                if staged is not None:
                    staged.unlink(missing_ok=True)
                raise StorageError(
                    f"Could not initialize knowledge graph: {self.graph_path}"
                ) from exc

    def _load_schema(self) -> dict[str, Any]:
        try:
            value = json.loads(self.schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Could not read knowledge schema: {self.schema_path}") from exc
        Draft202012Validator.check_schema(value)
        return cast(dict[str, Any], value)

    def _validate_or_raise(self, graph: dict[str, Any]) -> None:
        schema_errors = list(
            Draft202012Validator(
                self._load_schema(),
                format_checker=FormatChecker(),
            ).iter_errors(graph)
        )
        semantic_errors = self._semantic_errors(graph, graph_path=self.graph_path)
        if schema_errors or semantic_errors:
            message = (
                schema_errors[0].message
                if schema_errors
                else semantic_errors[0]["message"]
            )
            raise IntegrityError(f"Knowledge graph validation failed: {message}")

    @staticmethod
    def _semantic_errors(
        graph: dict[str, Any],
        *,
        graph_path: Path | None = None,
    ) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        nodes = graph.get("nodes")
        edges = graph.get("edges")
        if not isinstance(nodes, list) or not isinstance(edges, list):
            return errors
        node_ids = [
            node["id"]
            for node in nodes
            if isinstance(node, dict) and isinstance(node.get("id"), str)
        ]
        duplicate_ids = sorted(
            {node_id for node_id in node_ids if node_ids.count(node_id) > 1}
        )
        for node_id in duplicate_ids:
            errors.append(
                {"path": "$.nodes", "message": f"Duplicate node id: {node_id}"}
            )
        known = set(node_ids)
        inherited: dict[str, list[str]] = {}
        evidence_nodes: set[str] = set()
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            source = edge.get("source")
            target = edge.get("target")
            relation = edge.get("relation")
            if source not in known:
                errors.append(
                    {
                        "path": f"$.edges[{index}].source",
                        "message": f"Unknown source node: {source}",
                    }
                )
            if target not in known:
                errors.append(
                    {
                        "path": f"$.edges[{index}].target",
                        "message": f"Unknown target node: {target}",
                    }
                )
            if relation == "inherits_from":
                inherited.setdefault(str(source), []).append(str(target))
            elif "overrides" in edge:
                errors.append(
                    {
                        "path": f"$.edges[{index}].overrides",
                        "message": "overrides is only valid on inherits_from edges",
                    }
                )
            if relation in _EVIDENCE_RELATIONS:
                evidence_nodes.update((str(source), str(target)))
        for node_id in inherited:
            if _has_cycle(node_id, inherited, ()):
                errors.append(
                    {
                        "path": "$.edges",
                        "message": f"Inheritance cycle includes: {node_id}",
                    }
                )
        for index, node in enumerate(nodes):
            if not isinstance(node, dict) or node.get("kind") != "claim":
                continue
            lifecycle = node.get("lifecycle_status")
            direct_refs = node.get("evidence_refs", [])
            if lifecycle != "proposed" and not direct_refs and node.get("id") not in evidence_nodes:
                errors.append(
                    {
                        "path": f"$.nodes[{index}]",
                        "message": (
                            f"Claim {node.get('id')} is {lifecycle} but has no "
                            "evidence reference or evidence edge"
                        ),
                    }
                )
            for reference in direct_refs:
                if reference.startswith("file:"):
                    relative = PurePosixPath(reference.removeprefix("file:"))
                    if relative.is_absolute() or ".." in relative.parts:
                        errors.append(
                            {
                                "path": f"$.nodes[{index}].evidence_refs",
                                "message": f"Unsafe evidence file reference: {reference}",
                            }
                        )
                        continue
                    checkout = project_root()
                    if graph_path is None or checkout is None:
                        continue
                    repository = Path(checkout).resolve()
                    evidence_path = repository.joinpath(*relative.parts).resolve()
                    if (
                        repository not in evidence_path.parents
                        or not evidence_path.is_file()
                        or evidence_path.is_symlink()
                    ):
                        errors.append(
                            {
                                "path": f"$.nodes[{index}].evidence_refs",
                                "message": (
                                    f"Claim {node.get('id')} references unavailable "
                                    f"evidence file: {reference}"
                                ),
                            }
                        )
                elif reference.startswith("sha256:"):
                    if not _SHA256.fullmatch(reference.removeprefix("sha256:")):
                        errors.append(
                            {
                                "path": f"$.nodes[{index}].evidence_refs",
                                "message": f"Invalid evidence digest: {reference}",
                            }
                        )
                elif reference not in known:
                    errors.append(
                        {
                            "path": f"$.nodes[{index}].evidence_refs",
                            "message": f"Unknown evidence node: {reference}",
                        }
                    )
        return errors

    def _resolve_node(
        self,
        node_id: str,
        nodes: dict[str, dict[str, Any]],
        edges: list[dict[str, Any]],
        trail: tuple[str, ...],
    ) -> dict[str, Any]:
        if node_id in trail:
            raise IntegrityError(f"Inheritance cycle includes: {node_id}")
        value: dict[str, Any] = {}
        for edge in edges:
            if edge.get("source") != node_id or edge.get("relation") != "inherits_from":
                continue
            parent_id = str(edge["target"])
            value.update(
                self._resolve_node(parent_id, nodes, edges, (*trail, node_id))
            )
            value.update(deepcopy(edge.get("overrides", {})))
        value.update(deepcopy(nodes[node_id]))
        return value

    @staticmethod
    def _source_node(source: Mapping[str, Any]) -> dict[str, Any]:
        node_id = str(source.get("id", "")).strip().casefold()
        title = str(source.get("title", "")).strip()
        if not _NODE_ID.fullmatch(node_id) or not node_id.startswith("source:"):
            raise ValueError("id must use the form source:<stable-id>")
        if not title:
            raise ValueError("title must be non-empty text")
        identifiers = {
            key: str(value).strip()
            for key in ("doi", "arxiv", "ads_bibcode")
            if (value := source.get(key)) is not None and str(value).strip()
        }
        if not identifiers:
            raise ValueError("At least one DOI, arXiv id, or ADS bibcode is required")
        snapshot_sha256 = str(source.get("snapshot_sha256", "")).strip().casefold()
        if not _SHA256.fullmatch(snapshot_sha256):
            raise ValueError("snapshot_sha256 must be 64 lowercase hexadecimal characters")
        bibtex = str(source.get("bibtex", "")).strip()
        if not bibtex:
            raise ValueError("bibtex must be non-empty text")
        authors = source.get("authors", [])
        if not isinstance(authors, (list, tuple)) or not all(
            isinstance(author, str) and author.strip() for author in authors
        ):
            raise TypeError("authors must be a list of non-empty strings")
        year = source.get("year")
        if isinstance(year, bool) or not isinstance(year, int) or year < 1000 or year > 9999:
            raise ValueError("year must be a four-digit integer")
        return {
            "id": node_id,
            "type": "LiteratureReference",
            "kind": "source",
            "title": title,
            "name": title,
            "authors": list(authors),
            "year": year,
            "identifiers": identifiers,
            "snapshot_sha256": snapshot_sha256,
            "bibtex": bibtex,
            "evidence_class": "published",
            "evidence_status": "registered_literature_source",
            "use_for_empirical_confirmation": False,
        }

    def _write(self, graph: dict[str, Any]) -> None:
        graph["meta"]["last_updated"] = time.strftime("%Y-%m-%d", time.gmtime())
        self._write_json(self.graph_path, graph)

    @staticmethod
    def _write_json(path: Path, value: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        staged: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
                newline="\n",
            ) as temporary:
                json.dump(value, temporary, indent=2, ensure_ascii=True)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
                staged = Path(temporary.name)
            os.replace(staged, path)
            _fsync_directory(path.parent)
        except OSError as exc:
            if staged is not None:
                staged.unlink(missing_ok=True)
            raise StorageError(f"Could not write knowledge graph: {path}") from exc

    def _lock(self):
        return _FileLock(self.graph_path.with_suffix(self.graph_path.suffix + ".lock"))


class _FileLock:
    def __init__(self, path: Path, *, timeout: float = 30.0) -> None:
        self.path = path
        self.timeout = timeout

    def __enter__(self) -> _FileLock:
        deadline = time.monotonic() + self.timeout
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                descriptor = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )
                os.write(descriptor, str(os.getpid()).encode("ascii"))
                os.close(descriptor)
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    if not _lock_owner_alive(self.path):
                        with suppress(FileNotFoundError):
                            self.path.unlink()
                        deadline = time.monotonic() + self.timeout
                        continue
                    raise StorageError(
                        f"Timed out waiting for knowledge lock: {self.path}"
                    ) from None
                time.sleep(0.05)

    def __exit__(self, *_: object) -> None:
        with suppress(FileNotFoundError):
            self.path.unlink()


def _append_edge(
    graph: dict[str, Any],
    source: str,
    target: str,
    relation: str,
    evidence_class: str,
    provenance: str,
    confidence: float,
) -> None:
    identity = (source, target, relation)
    if any(
        (edge["source"], edge["target"], edge["relation"]) == identity
        for edge in graph["edges"]
    ):
        return
    graph["edges"].append(
        {
            "source": source,
            "target": target,
            "relation": relation,
            "confidence": confidence,
            "evidence_class": evidence_class,
            "provenance": provenance,
            "evidence_status": "durable_knowledge_link",
        }
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _lock_owner_alive(path: Path) -> bool:
    try:
        process_id = int(path.read_text(encoding="ascii"))
        os.kill(process_id, 0)
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return False
    except OSError:
        return True
    return True


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _json_path(parts: Any) -> str:
    value = "$"
    for part in parts:
        value += f"[{part}]" if isinstance(part, int) else f".{part}"
    return value


def _has_cycle(
    node_id: str,
    inherited: dict[str, list[str]],
    trail: tuple[str, ...],
) -> bool:
    if node_id in trail:
        return True
    return any(
        _has_cycle(parent, inherited, (*trail, node_id))
        for parent in inherited.get(node_id, [])
    )


__all__ = ["KnowledgeStore"]
