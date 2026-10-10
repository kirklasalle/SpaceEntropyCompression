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

import emrf_registry as reg
from emrf_version import __version__


def _print_json(obj: object) -> None:
    print(json.dumps(obj, indent=2, default=str))


def _strip_separator(rest: list[str]) -> list[str]:
    return rest[1:] if rest and rest[0] == "--" else rest


def cmd_list(a: argparse.Namespace) -> int:
    rows = reg.list_commands(a.category)
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
        result = reg.run_command(a.name, _strip_separator(a.args), timeout=a.timeout)
    except KeyError as exc:
        print(f"error: {exc.args[0]}. Use 'list' to see commands.", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print(f"error: {a.name} exceeded timeout of {a.timeout}s", file=sys.stderr)
        return 1
    return int(result["returncode"])


def _parse_grid(text: str) -> list[float]:
    try:
        return [float(v) for v in text.split(",") if v.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"grid must be comma-separated numbers: {text!r}"
        ) from None


def cmd_simulate(a: argparse.Namespace) -> int:
    import numpy as np

    from server import _validate_and_parse_payload, run_simulation

    payload = {"n": a.n, "weights": a.weights, "X_grid": a.grid,
               "k": a.k, "alpha": a.alpha, "C0": a.C0}
    try:
        n, weights, grid, k, alpha, c0 = _validate_and_parse_payload(payload)
    except (TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    m = run_simulation(n, weights, grid, k, alpha, c0)
    if a.output:
        np.save(a.output, m)
        print(f"Saved array with shape {m.shape} to {a.output}")
    else:
        _print_json({"shape": list(m.shape), "M": m.tolist()})
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


def _data_library():
    from emrf_data_access import data_library

    return data_library()


def _run_store():
    from emrf_run_access import run_store

    return run_store()


def _public_record(record):
    from emrf_run_access import public_record

    return public_record(record)


def cmd_runs(a: argparse.Namespace) -> int:
    store = _run_store()
    if a.runs_command == "list":
        records = store.list(limit=a.limit)
        if a.json:
            _print_json([_public_record(record) for record in records])
        else:
            for record in records:
                print(
                    f"{record.run_id} {record.status:<11} "
                    f"{record.command} attempt={record.attempt}"
                )
        return 0
    if a.runs_command == "info":
        _print_json(_public_record(store.get(a.run_id)))
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
    _print_json(_public_record(record))
    return 0 if record.status in {"succeeded", "queued"} else 1


def cmd_data_catalog(a: argparse.Namespace) -> int:
    rows = _data_library().catalog_status(verify=a.verify)
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
    _print_json(_data_library().info(a.dataset_id, verify=a.verify))
    return 0


def cmd_data_import(a: argparse.Namespace) -> int:
    result = _data_library().import_dataset(
        a.dataset_id,
        logical_name=a.logical_name,
        source=a.source,
    )
    _print_json({"holdings": result})
    return 0


def cmd_data_fetch(a: argparse.Namespace) -> int:
    result = _data_library().fetch_dataset(
        a.dataset_id,
        logical_name=a.logical_name,
        retries=a.retries,
        timeout=a.timeout,
    )
    _print_json({"holdings": result})
    return 0


def cmd_data_verify(a: argparse.Namespace) -> int:
    result = _data_library().verify()
    _print_json(result)
    return 0 if result["healthy"] else 1


def cmd_data_backup(a: argparse.Namespace) -> int:
    _print_json(_data_library().create_backup(a.destination))
    return 0


def cmd_data_backup_offsite(a: argparse.Namespace) -> int:
    _print_json(_data_library().create_offsite_backup(a.destination_root))
    return 0


def cmd_data_backup_verify(a: argparse.Namespace) -> int:
    _print_json(_data_library().verify_backup(a.source))
    return 0


def cmd_data_restore(a: argparse.Namespace) -> int:
    _print_json(_data_library().restore_backup(a.source))
    return 0


def cmd_data_drill(a: argparse.Namespace) -> int:
    _print_json(
        _data_library().run_restore_drill(
            receipt=a.receipt,
            workspace=a.workspace,
        )
    )
    return 0


def cmd_data_gc(a: argparse.Namespace) -> int:
    _print_json(_data_library().garbage_collect(execute=a.execute))
    return 0


def cmd_doctor(a: argparse.Namespace) -> int:
    rep = reg.environment_report()
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
    from emrf_physics_access import known_limit_report

    report = known_limit_report()
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

    s = sub.add_parser("doctor", help="diagnose environment and dependencies")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("verify", help="run scientific verification certificates")
    vsub = s.add_subparsers(dest="verify_command", required=True)
    v = vsub.add_parser("physics", help="run foundational known-limit checks")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify_physics)

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
