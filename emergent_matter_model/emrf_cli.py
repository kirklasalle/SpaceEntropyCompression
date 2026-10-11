"""EMRF unified command-line interface.

Usage examples::

    python emergent_matter_model/emrf_cli.py --version
    python emergent_matter_model/emrf_cli.py list [--category analysis] [--json]
    python emergent_matter_model/emrf_cli.py run sparc-real-analysis -- --help
    python emergent_matter_model/emrf_cli.py simulate --n 2 --weights 0.5 0.5 \
        --grid=-1,0,1 --grid=0,0.5,1
    python emergent_matter_model/emrf_cli.py data list [--verify] [--json]
    python emergent_matter_model/emrf_cli.py data catalog [--verify] [--json]
    python emergent_matter_model/emrf_cli.py data info DATASET [--verify]
    python emergent_matter_model/emrf_cli.py data import DATASET [HOLDING]
    python emergent_matter_model/emrf_cli.py data fetch DATASET [HOLDING]
    python emergent_matter_model/emrf_cli.py data backup DESTINATION
    python emergent_matter_model/emrf_cli.py data restore SOURCE
    python emergent_matter_model/emrf_cli.py data drill [--receipt FILE]
    python emergent_matter_model/emrf_cli.py doctor [--json]
    python emergent_matter_model/emrf_cli.py serve [--host 127.0.0.1] [--port 5000]
    python emergent_matter_model/emrf_cli.py test [-- pytest args]

Exit codes: 0 success, 1 failure/unhealthy, 2 usage error, otherwise the wrapped
program's own exit code.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import emrf_registry as reg
from emrf_sdk_access import (
    EMRFClient,
    KnowledgeSourceRequest,
    RunRequest,
    SimulationRequest,
)
from emrf_version import __version__

sdk = EMRFClient()


def _print_json(obj: object) -> None:
    print(json.dumps(obj, indent=2, default=str))


def _strip_separator(rest: list[str]) -> list[str]:
    return rest[1:] if rest and rest[0] == "--" else rest


def cmd_list(a: argparse.Namespace) -> int:
    rows = [command.to_dict() for command in sdk.list_commands(a.category).commands]
    if a.json:
        _print_json(rows)
        return 0
    width = max(len(r["name"]) for r in rows) if rows else 0
    current = None
    for r in rows:
        if r["category"] != current:
            current = r["category"]
            print(f"\n[{current}]")
        flags = "".join(
            [" (network)" if r["network"] else "", " (gui)" if r["gui"] else "",
             "" if r["exists"] else " (MISSING)"]
        )
        print(f"  {r['name']:<{width}}  {r['summary']}{flags}")
    return 0


def cmd_run(a: argparse.Namespace) -> int:
    try:
        result = sdk.run(
            RunRequest(
                command=a.name,
                args=tuple(_strip_separator(a.args)),
                timeout=a.timeout,
            )
        )
    except KeyError as exc:
        print(f"error: {exc.args[0]}. Use 'list' to see commands.", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print(f"error: {a.name} exceeded timeout of {a.timeout}s", file=sys.stderr)
        return 1
    return result.returncode


def _parse_grid(text: str) -> list[float]:
    try:
        return [float(v) for v in text.split(",") if v.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"grid must be comma-separated numbers: {text!r}"
        ) from None


def cmd_simulate(a: argparse.Namespace) -> int:
    import numpy as np

    try:
        result = sdk.simulate(
            SimulationRequest(
                n=a.n,
                weights=tuple(a.weights),
                grid=tuple(tuple(axis) for axis in a.grid),
                k=a.k,
                alpha=a.alpha,
                C0=a.C0,
            )
        )
    except (TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.output:
        np.save(a.output, np.asarray(result.values))
        print(f"Saved array with shape {result.shape} to {a.output}")
    else:
        _print_json(result.to_dict())
    return 0


def cmd_data(a: argparse.Namespace) -> int:
    rows = reg.dataset_status(verify=a.verify)
    if a.json:
        _print_json(rows)
    elif not rows:
        print("No dataset manifest found. Run: emrf_cli.py run fetch-real-data -- --sparc")
    else:
        for r in rows:
            status = r.get("status", "present" if r["present"] else "missing")
            print(f"{r['id']:<32} {status:<14} {r['bytes']:>10} B  {r['url']}")
    if a.verify and any(r.get("status") != "ok" for r in rows):
        return 1
    return 0


def _run_store():
    from emrf_run_access import run_store

    return run_store()


def _public_record(record):
    from emrf_run_access import public_record

    return public_record(record)


def cmd_runs(a: argparse.Namespace) -> int:
    if a.runs_command == "list":
        records = sdk.list_runs(limit=a.limit).runs
        if a.json:
            _print_json([record.to_dict() for record in records])
        else:
            for record in records:
                print(
                    f"{record.run_id} {record.status:<11} "
                    f"{record.command} attempt={record.attempt}"
                )
        return 0
    if a.runs_command == "info":
        _print_json(sdk.get_run(a.run_id).to_dict())
        return 0
    if a.runs_command == "artifacts":
        _print_json(sdk.list_artifacts(a.run_id).to_dict())
        return 0
    if a.runs_command == "artifact":
        artifact = sdk.get_artifact(a.run_id, a.path)
        destination = Path(a.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(artifact.file_path.read_bytes())
        _print_json({**artifact.info.to_dict(), "output": str(destination)})
        return 0
    result = reg.resume_run(a.run_id, timeout=a.timeout)
    _print_json(result)
    return int(result["returncode"])


def cmd_jobs(a: argparse.Namespace) -> int:
    store = _run_store()
    if a.jobs_command == "submit":
        command = reg.get_command(a.name)
        if command.gui or command.category == "service":
            raise ValueError(
                f"{a.name} is interactive or a service and cannot run as a job"
            )
        record = store.enqueue(
            a.name,
            _strip_separator(a.args),
            timeout_seconds=a.timeout,
            evidence_class=a.evidence_class,
            max_attempts=a.max_attempts,
        )
        _print_json(_public_record(record))
        return 0
    if a.jobs_command == "list":
        records = store.list_jobs(limit=a.limit)
        if a.json:
            _print_json([_public_record(record) for record in records])
        else:
            for record in records:
                print(
                    f"{record.job_id} {record.status:<9} {record.command} "
                    f"attempts={record.attempts}/{record.max_attempts}"
                )
        return 0
    if a.jobs_command == "info":
        _print_json(_public_record(store.get_job(a.job_id)))
        return 0
    if a.jobs_command == "cancel":
        _print_json(_public_record(store.cancel_job(a.job_id)))
        return 0
    worker_id = a.worker_id or f"{socket.gethostname()}:{os.getpid()}"
    record = reg.run_next_job(worker_id, lease_seconds=a.lease_seconds)
    if record is None:
        print("No queued jobs.")
        return 0
    public = _public_record(record)
    _print_json(public)
    return 0 if public["status"] in {"succeeded", "queued"} else 1


def cmd_knowledge(a: argparse.Namespace) -> int:
    if a.kb_command == "validate":
        report = sdk.validate_knowledge()
        if a.json:
            _print_json(report.to_dict())
        else:
            state = "valid" if report.valid else "invalid"
            print(
                f"Knowledge graph {state}: {report.nodes} nodes, "
                f"{report.edges} edges, schema {report.schema_version}"
            )
            for error in report.errors:
                print(f"  {error['path']}: {error['message']}", file=sys.stderr)
        return 0 if report.valid else 1
    if a.kb_command == "query":
        result = sdk.query_knowledge(
            a.text,
            kind=a.kind,
            lifecycle_status=a.status,
            limit=a.limit,
        )
        if a.json:
            _print_json(result.to_dict())
        else:
            for node in result.nodes:
                row = node.to_dict()
                label = row.get("name", row.get("title", ""))
                print(f"{row['id']:<52} {row['kind']:<10} {label}")
        return 0
    if a.kb_command == "add-source":
        bibtex = Path(a.bibtex_file).read_text(encoding="utf-8")
        node = sdk.add_knowledge_source(
            KnowledgeSourceRequest(
                source_id=a.source_id,
                title=a.title,
                authors=tuple(a.author),
                year=a.year,
                snapshot_sha256=a.snapshot_sha256,
                bibtex=bibtex,
                doi=a.doi,
                arxiv=a.arxiv,
                ads_bibcode=a.ads_bibcode,
            )
        )
        _print_json(node.to_dict())
        return 0
    if a.kb_command == "export":
        _print_json(sdk.export_knowledge(a.output).to_dict())
        return 0
    result = sdk.link_run_knowledge(
        a.run_id,
        claim_ids=tuple(a.claim),
        source_ids=tuple(a.source),
        dataset_ids=tuple(a.dataset),
    )
    _print_json(result.to_dict())
    return 0


def cmd_data_catalog(a: argparse.Namespace) -> int:
    rows = [record.to_dict() for record in sdk.list_datasets(verify=a.verify).datasets]
    if a.json:
        _print_json(rows)
    else:
        for row in rows:
            print(
                f"{row['id']:<30} {row['status']:<10} "
                f"{row['priority']:<6} {row['title']}"
            )
    return 1 if a.verify and any(row["status"] == "corrupt" for row in rows) else 0


def cmd_data_info(a: argparse.Namespace) -> int:
    _print_json(sdk.get_dataset(a.dataset_id, verify=a.verify).to_dict())
    return 0


def cmd_data_import(a: argparse.Namespace) -> int:
    result = sdk.import_dataset(
        a.dataset_id,
        logical_name=a.logical_name,
        source=a.source,
    )
    _print_json(result.to_dict())
    return 0


def cmd_data_fetch(a: argparse.Namespace) -> int:
    result = sdk.fetch_dataset(
        a.dataset_id,
        logical_name=a.logical_name,
        retries=a.retries,
        timeout=a.timeout,
    )
    _print_json(result.to_dict())
    return 0


def cmd_data_verify(_a: argparse.Namespace) -> int:
    result = sdk.verify_datasets().to_dict()
    _print_json(result)
    return 0 if result["healthy"] else 1


def cmd_data_backup(a: argparse.Namespace) -> int:
    _print_json(sdk.create_data_backup(a.destination).to_dict())
    return 0


def cmd_data_backup_offsite(a: argparse.Namespace) -> int:
    _print_json(sdk.create_offsite_data_backup(a.destination_root).to_dict())
    return 0


def cmd_data_backup_verify(a: argparse.Namespace) -> int:
    _print_json(sdk.verify_data_backup(a.source).to_dict())
    return 0


def cmd_data_restore(a: argparse.Namespace) -> int:
    _print_json(sdk.restore_data_backup(a.source).to_dict())
    return 0


def cmd_data_drill(a: argparse.Namespace) -> int:
    _print_json(
        sdk.run_data_restore_drill(
            receipt=a.receipt,
            workspace=a.workspace,
        ).to_dict()
    )
    return 0


def cmd_data_gc(a: argparse.Namespace) -> int:
    _print_json(sdk.garbage_collect_data(execute=a.execute).to_dict())
    return 0


def cmd_doctor(a: argparse.Namespace) -> int:
    rep = sdk.environment_report(include_executable=True).to_dict()
    if a.json:
        _print_json(rep)
    else:
        print(f"EMRF {rep['emrf_version']} (API {rep['api_version']}) on Python {rep['python']}")
        for group in ("core_dependencies", "optional_dependencies"):
            print(f"{group}:")
            for name, ver in rep[group].items():
                print(f"  {name:<12} {ver or 'NOT INSTALLED'}")
        print(f"registered commands: {rep['registered_commands']}; "
              f"missing scripts: {rep['missing_scripts'] or 'none'}")
        print("status:", "HEALTHY" if rep["healthy"] else "ATTENTION NEEDED")
    return 0 if rep["healthy"] else 1


def cmd_verify_physics(a: argparse.Namespace) -> int:
    result = sdk.verify_physics()
    report = result.to_dict()
    if a.json:
        _print_json(report)
    else:
        for check in report["checks"]:
            marker = "PASS" if check["passed"] else "FAIL"
            print(
                f"{marker:<4} [{check['evidence_class']}] {check['name']}: "
                f"{check['measured']:.12g} "
                f"{check['unit']} (relative error {check['relative_error']:.3g})"
            )
            if check["limitation"]:
                print(f"     limitation: {check['limitation']}")
        print("status:", "VERIFIED" if report["all_passed"] else "FAILED")
    return 0 if report["all_passed"] else 1


def cmd_verify_inference(a: argparse.Namespace) -> int:
    result = sdk.verify_inference()
    report = result.to_dict()
    if a.json:
        _print_json(report)
    else:
        for check in report["checks"]:
            marker = "PASS" if check["passed"] else "FAIL"
            print(
                f"{marker:<4} [{check['evidence_class']}] {check['name']}: "
                f"{check['measured']:.6g} "
                f"(accepted {check['lower_bound']:.6g} to "
                f"{check['upper_bound']:.6g})"
            )
            print(f"     limitation: {check['limitation']}")
        for limitation in report["limitations"]:
            print(f"limitation: {limitation}")
        print("status:", "CALIBRATED" if report["all_passed"] else "FAILED")
    return 0 if report["all_passed"] else 1


def cmd_verify_engines(a: argparse.Namespace) -> int:
    result = sdk.verify_engines()
    report = result.to_dict()
    if a.json:
        _print_json(report)
    else:
        for check in report["checks"]:
            marker = "PASS" if check["passed"] else "FAIL"
            print(
                f"{marker:<4} [{check['evidence_class']}] {check['name']}: "
                f"{check['measured']:.6g}"
            )
            if check["limitation"]:
                print(f"     limitation: {check['limitation']}")
        print("status:", "VERIFIED" if report["all_passed"] else "FAILED")
    return 0 if report["all_passed"] else 1


def cmd_predict(a: argparse.Namespace) -> int:
    if a.commit:
        result = sdk.commit_prediction_file(a.commit, label=a.label).to_dict()
    else:
        result = sdk.verify_prediction_file(a.commitment_id, a.verify).to_dict()
    _print_json(result)
    return 0 if result.get("matches", True) else 1


def cmd_serve(a: argparse.Namespace) -> int:
    from server import app

    app.run(host=a.host, port=a.port, debug=False)
    return 0


def cmd_test(a: argparse.Namespace) -> int:
    return subprocess.call(  # noqa: S603
        [sys.executable, "-m", "pytest", *_strip_separator(a.args)], cwd=str(reg.PACKAGE_DIR)
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="emrf", description="Emergent Matter Research Framework (EMRF) command-line interface",
        epilog="Run 'emrf <command> -h' for command help.",
    )
    p.add_argument("--version", action="version", version=f"emrf {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("list", help="list every registered program")
    s.add_argument("--category", choices=reg.CATEGORIES)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("run", help="run a registered program; pass its args after --")
    s.add_argument("name")
    s.add_argument("--timeout", type=float, default=None, help="seconds before aborting")
    s.add_argument("args", nargs=argparse.REMAINDER)
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("simulate", help="run the emergent-matter grid simulation locally")
    s.add_argument("--n", type=int, required=True)
    s.add_argument("--weights", type=float, nargs="+", required=True)
    s.add_argument("--grid", type=_parse_grid, action="append", required=True,
                   help="comma-separated axis values, one flag per dimension; use the "
                        "--grid=-1,0,1 form when values start with '-'")
    s.add_argument("--k", type=float, default=1.0)
    s.add_argument("--alpha", type=float, default=1.0)
    s.add_argument("--C0", type=float, default=1.0)
    s.add_argument("--output", help="save result as .npy instead of printing JSON")
    s.set_defaults(func=cmd_simulate)

    s = sub.add_parser("data", help="observational data library")
    dsub = s.add_subparsers(dest="data_command", required=True)
    d = dsub.add_parser("list", help="list manifest-registered datasets")
    d.add_argument("--verify", action="store_true", help="re-hash files (read-only)")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_data)

    d = dsub.add_parser("catalog", help="list the curated managed-data catalog")
    d.add_argument("--verify", action="store_true", help="re-hash managed objects")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_data_catalog)

    d = dsub.add_parser("info", help="show catalog and managed status for one dataset")
    d.add_argument("dataset_id")
    d.add_argument("--verify", action="store_true")
    d.set_defaults(func=cmd_data_info)

    d = dsub.add_parser("import", help="import locally acquired catalog holdings")
    d.add_argument("dataset_id")
    d.add_argument("logical_name", nargs="?")
    d.add_argument("--source", help="source file; requires one selected holding")
    d.set_defaults(func=cmd_data_import)

    d = dsub.add_parser("fetch", help="safely fetch pinned catalog holdings")
    d.add_argument("dataset_id")
    d.add_argument("logical_name", nargs="?")
    d.add_argument("--retries", type=int, default=3)
    d.add_argument("--timeout", type=float, default=180.0)
    d.set_defaults(func=cmd_data_fetch)

    d = dsub.add_parser("verify", help="verify all managed catalog holdings")
    d.set_defaults(func=cmd_data_verify)

    d = dsub.add_parser("backup", help="create a verified data-library backup")
    d.add_argument("destination")
    d.set_defaults(func=cmd_data_backup)

    d = dsub.add_parser("backup-offsite", help="back up to an independent configured root")
    d.add_argument(
        "--destination-root",
        help="overrides EMRF_OFFSITE_BACKUP_DIR without storing credentials",
    )
    d.set_defaults(func=cmd_data_backup_offsite)

    d = dsub.add_parser("backup-verify", help="verify a data-library backup")
    d.add_argument("source")
    d.set_defaults(func=cmd_data_backup_verify)

    d = dsub.add_parser("restore", help="restore a verified backup without overwriting")
    d.add_argument("source")
    d.set_defaults(func=cmd_data_restore)

    d = dsub.add_parser("drill", help="run a full temporary backup and restore drill")
    d.add_argument("--receipt", help="durable JSON receipt; defaults under the data root")
    d.add_argument("--workspace", help="parent directory for temporary drill data")
    d.set_defaults(func=cmd_data_drill)

    d = dsub.add_parser("gc", help="report unreferenced objects (dry-run by default)")
    d.add_argument(
        "--execute",
        action="store_true",
        help="remove reported unreferenced objects",
    )
    d.set_defaults(func=cmd_data_gc)

    s = sub.add_parser("runs", help="inspect and resume durable scientific runs")
    rsub = s.add_subparsers(dest="runs_command", required=True)
    r = rsub.add_parser("list", help="list recent runs")
    r.add_argument("--limit", type=int, default=50)
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_runs)
    r = rsub.add_parser("info", help="show one run")
    r.add_argument("run_id")
    r.set_defaults(func=cmd_runs)
    r = rsub.add_parser("artifacts", help="list files recorded for one run")
    r.add_argument("run_id")
    r.set_defaults(func=cmd_runs)
    r = rsub.add_parser("artifact", help="copy one run artifact to a safe output path")
    r.add_argument("run_id")
    r.add_argument("path")
    r.add_argument("--output", required=True)
    r.set_defaults(func=cmd_runs)
    r = rsub.add_parser("resume", help="resume a failed, timed-out or interrupted run")
    r.add_argument("run_id")
    r.add_argument("--timeout", type=float)
    r.set_defaults(func=cmd_runs)

    s = sub.add_parser("jobs", help="manage the durable execution queue")
    jsub = s.add_subparsers(dest="jobs_command", required=True)
    j = jsub.add_parser("submit", help="submit a registered command")
    j.add_argument("name")
    j.add_argument("--timeout", type=float)
    j.add_argument("--max-attempts", type=int, default=1)
    j.add_argument(
        "--evidence-class",
        choices=("observational", "published", "synthetic", "illustrative", "software"),
        default="software",
    )
    j.add_argument("args", nargs=argparse.REMAINDER)
    j.set_defaults(func=cmd_jobs)

    j = jsub.add_parser("list", help="list queued and completed jobs")
    j.add_argument("--limit", type=int, default=50)
    j.add_argument("--json", action="store_true")
    j.set_defaults(func=cmd_jobs)
    j = jsub.add_parser("info", help="show one job")
    j.add_argument("job_id")
    j.set_defaults(func=cmd_jobs)
    j = jsub.add_parser("cancel", help="cancel a queued job")
    j.add_argument("job_id")
    j.set_defaults(func=cmd_jobs)
    j = jsub.add_parser("run-next", help="claim and execute one queued job")
    j.add_argument("--worker-id")
    j.add_argument("--lease-seconds", type=float, default=3600)
    j.set_defaults(func=cmd_jobs)

    s = sub.add_parser("kb", help="query and maintain scientific knowledge")
    ksub = s.add_subparsers(dest="kb_command", required=True)
    k = ksub.add_parser("validate", help="validate schema and graph integrity")
    k.add_argument("--json", action="store_true")
    k.set_defaults(func=cmd_knowledge)
    k = ksub.add_parser("query", help="query knowledge nodes")
    k.add_argument("text", nargs="?")
    k.add_argument(
        "--kind",
        choices=(
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
        ),
    )
    k.add_argument(
        "--status",
        choices=("proposed", "tested", "supported", "refuted", "retracted"),
    )
    k.add_argument("--limit", type=int, default=100)
    k.add_argument("--json", action="store_true")
    k.set_defaults(func=cmd_knowledge)
    k = ksub.add_parser("add-source", help="register a pinned literature source")
    k.add_argument("source_id", help="stable id in source:<name> form")
    k.add_argument("--title", required=True)
    k.add_argument("--author", action="append", required=True)
    k.add_argument("--year", type=int, required=True)
    identifiers = k.add_mutually_exclusive_group(required=True)
    identifiers.add_argument("--doi")
    identifiers.add_argument("--arxiv")
    identifiers.add_argument("--ads-bibcode")
    k.add_argument("--snapshot-sha256", required=True)
    k.add_argument("--bibtex-file", required=True)
    k.set_defaults(func=cmd_knowledge)
    k = ksub.add_parser("export", help="export a validated JSON snapshot")
    k.add_argument("--output", required=True)
    k.set_defaults(func=cmd_knowledge)
    k = ksub.add_parser(
        "link-run",
        help="link a durable run and its artifacts to scientific evidence",
    )
    k.add_argument("run_id")
    k.add_argument("--claim", action="append", default=[])
    k.add_argument("--source", action="append", default=[])
    k.add_argument("--dataset", action="append", default=[])
    k.set_defaults(func=cmd_knowledge)

    s = sub.add_parser("doctor", help="diagnose environment and dependencies")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("verify", help="run scientific verification certificates")
    vsub = s.add_subparsers(dest="verify_command", required=True)
    v = vsub.add_parser("physics", help="run foundational known-limit checks")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify_physics)
    v = vsub.add_parser(
        "inference",
        help="run deterministic injection-recovery and interval-calibration checks",
    )
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify_inference)
    v = vsub.add_parser("engines", help="run remaining cross-engine verification")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify_engines)

    s = sub.add_parser("predict", help="commit or verify a preregistered prediction")
    action = s.add_mutually_exclusive_group(required=True)
    action.add_argument("--commit", metavar="FILE", help="commit the SHA-256 of prediction bytes")
    action.add_argument("--verify", metavar="FILE", help="verify revealed prediction bytes")
    s.add_argument("--label", help="human-readable prediction label")
    s.add_argument("--commitment-id", help="commitment id used with --verify")
    s.set_defaults(func=cmd_predict)

    s = sub.add_parser("serve", help="start the REST API (development server)")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=5000)
    s.set_defaults(func=cmd_serve)

    s = sub.add_parser("test", help="run the pytest suite; pass pytest args after --")
    s.add_argument("args", nargs=argparse.REMAINDER)
    s.set_defaults(func=cmd_test)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "predict":
            if args.commit and not args.label:
                raise ValueError("--label is required with --commit")
            if args.verify and not args.commitment_id:
                raise ValueError("--commitment-id is required with --verify")
        return int(args.func(args))
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
