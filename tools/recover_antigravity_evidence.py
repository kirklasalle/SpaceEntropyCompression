"""Preserve an explicit allowlist of EMRF archive evidence without executing it.

Raw IDE messages, model-internal fields, credentials and unrelated project
material are not copied. Source paths are relative to the supplied brain root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "archive" / "antigravity_recovery"
CORE = "8de1a404-0739-40f4-a4af-8d636b604cc9"
REVIEW = "67e60b60-238b-4fb1-8fcc-1e4c3034f1fe"
EARLY = "e5da707a-459a-4d74-91d8-b0c8df2a569a"
PORTFOLIO = "fde69dc2-de73-40cc-b2d0-0e1e2de57be7"
SECRET = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\b(?:ghp_|github_pat_|AIzaSy)[A-Za-z0-9_]{20,}|"
    r"\bsk-[A-Za-z0-9_-]{30,}")

SELECTION = {
    CORE: [
        "EMRF_MASTER_AUDIT_2026-10-05.md", "COSMOLOGICAL_FRONTIERS_IMPLEMENTATION_PLAN.md",
        "GRAND_AUDIT_TEMPLATE_REVIEW.md",
        r"scratch\FIRST_USE_CASE_LASALLE_SPATIAL_ONTOLOGY.md",
        r"scratch\GRAND_DUE_DILIGENCE_AUDIT_CASE_002_FIRST_USE_CASE.md",
        r"scratch\use_case_lasalle_ontology.tex",
        r"scratch\black_hole_horizon_entropy.py", r"scratch\quantum_vibrational_compression.py",
        r"scratch\jwst_highz_early_galaxies.py", r"scratch\plot_three_horizons_figures.py",
        r"scratch\test_three_horizons.py", r"scratch\test_use_case_submission.py",
        r"scratch\package_use_case_submission.py", r"scratch\generate_compendium.py",
        r"browser\scratchpad_0tiaazre.md",
        "visualizer_initial_state_1791306927723.png", "rar_scatter_tab_1791306996881.png",
        "cosmic_expansion_regime_1791307013899.png", "cmb_peaks_regime_1791307030494.png",
        "returned_3d_tab_1791307103916.png", "sidebar_collapsed_1791307056781.png",
        "sidebar_expanded_1791307081750.png", "test_visualizer_1791306915824.webp",
    ],
    REVIEW: ["forward_document_emrf_peer_review_refinement.md", r"scratch\release_notes_v0.9.1.md"],
    EARLY: [r"scratch\emrf_full_text.txt", r"scratch\emrf_dump.txt",
            r"scratch\build_emrf_all.py", r"scratch\build_emrf_docs.py",
            r"scratch\update_emrf_docx.py"],
}
LOGS = {
    CORE: ["task-276.log", "task-1183.log", "task-1196.log", "task-1241.log",
           "task-1376.log", "task-1413.log", "task-1598.log", "task-2073.log", "task-2252.log"],
    REVIEW: ["task-153.log", "task-168.log", "task-203.log", "task-330.log"],
}
MEDIA_DUPLICATES = [
    (REVIEW, r".tempmediaStorage\media_1791333042941.mp4",
     ROOT / "docs" / "audio" / "Preparing_EMRF_Physics_for_Peer_Review.m4a"),
    (REVIEW, r".tempmediaStorage\media_1791333057512.mp4",
     ROOT / "docs" / "audio" / "Refining_the_Emergent_Matter_Research_Framework.m4a"),
]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check_text(raw: bytes) -> None:
    text = raw.decode("utf-8-sig")
    if SECRET.search(text):
        raise ValueError("Possible credential/private-key material; manual review required")


def write_once(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != raw:
        raise ValueError(f"Refusing to overwrite different archived bytes: {path}")
    if not path.exists():
        path.write_bytes(raw)


def existing_candidates(name: str) -> list[Path]:
    candidates = [ROOT / "docs" / name, ROOT / "paper" / name,
                  ROOT / "emergent_matter_model" / name]
    aliases = {
        "COSMOLOGICAL_FRONTIERS_IMPLEMENTATION_PLAN.md": ROOT / "docs" / "COSMOLOGICAL_FRONTIERS_PLAN.md",
        "forward_document_emrf_peer_review_refinement.md":
            ROOT / "docs" / "FORWARD_DOCUMENT_EMRF_PEER_REVIEW_REFINEMENT.md",
    }
    if name in aliases:
        candidates.append(aliases[name])
    return [p for p in candidates if p.is_file()]


def preserve(source: Path, brain: Path, kind: str) -> dict:
    raw = source.read_bytes()
    if kind != "historical_visualization":
        check_text(raw)
    relative = source.relative_to(brain)
    identical = [p for p in existing_candidates(source.name) if p.read_bytes() == raw]
    stat = source.stat()
    entry = {"source_relative_path": str(relative), "sha256": digest(raw), "bytes": len(raw),
             "kind": kind, "evidence_status": "historical_not_new_validation",
             "source_modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
             "existing_same_name_candidates": [str(p.relative_to(ROOT))
                                               for p in existing_candidates(source.name)]}
    if identical:
        entry.update(disposition="already_preserved_exact",
                     destination=str(identical[0].relative_to(ROOT)))
        return entry
    name = source.name
    if source.suffix in (".py", ".tex", ".log", ".js"):
        name += ".txt"
    destination = DEST / "sources" / relative.parts[0] / name
    write_once(destination, raw)
    entry.update(disposition="copied_exact", destination=str(destination.relative_to(ROOT)))
    return entry


def project_only(value):
    """Retain only explicitly project-addressed fields from a mixed inventory."""
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            if "spaceentropycompression" in key.lower():
                out[key] = child
            elif isinstance(child, (dict, list)):
                selected = project_only(child)
                if selected:
                    out[key] = selected
        return out
    if isinstance(value, list):
        return [child for child in value if isinstance(child, str)
                and "spaceentropycompression" in child.lower()]
    return None


def recover(brain: Path, discovery: Path, user_payloads: Path) -> dict:
    brain = brain.resolve(strict=True)
    records = []
    for session, names in SELECTION.items():
        for name in names:
            path = brain / session / name
            kind = ("historical_visualization" if path.suffix in (".png", ".webp")
                    else "historical_code_snapshot" if path.suffix == ".py"
                    else "historical_draft")
            records.append(preserve(path, brain, kind))
    for session, names in LOGS.items():
        for name in names:
            records.append(preserve(brain / session / ".system_generated" / "tasks" / name,
                                    brain, "historical_execution_log"))
    for session, name, destination in MEDIA_DUPLICATES:
        source = brain / session / name
        raw = source.read_bytes()
        if raw != destination.read_bytes():
            raise ValueError("Audio duplicate no longer matches; do not infer transcript identity")
        records.append({"source_relative_path": str(source.relative_to(brain)),
                        "sha256": digest(raw), "bytes": len(raw), "kind": "existing_audio_attachment",
                        "disposition": "already_preserved_exact",
                        "destination": str(destination.relative_to(ROOT)),
                        "evidence_status": "existing_review_audio_not_physics_validation"})
    for name in ("deep_analysis.json", "inventory.json"):
        source = brain / PORTFOLIO / "scratch" / name
        data = json.loads(source.read_text(encoding="utf-8"))
        selected = project_only(data.get("theory", {}))
        destination = DEST / "extracts" / f"august_{name}"
        raw = (json.dumps(selected, indent=2)+"\n").encode()
        check_text(raw)
        write_once(destination, raw)
        records.append({"source_relative_path": str(source.relative_to(brain)),
                        "source_sha256": digest(source.read_bytes()), "sha256": digest(raw),
                        "destination": str(destination.relative_to(ROOT)),
                        "disposition": "project_only_json_extraction",
                        "selection": "theory subtree; only explicitly SpaceEntropyCompression fields",
                        "kind": "historical_inventory", "evidence_status": "not_observational_data"})
    payloads = json.loads(user_payloads.read_text())
    user_records = [r for r in payloads["project_candidate_records"]
                    if r["source"].startswith((CORE, "6b8936a8-", "d803e888-"))]
    raw = (json.dumps(user_records, indent=2)+"\n").encode()
    check_text(raw)
    user_destination = DEST / "extracts" / "user_text_records.json"
    write_once(user_destination, raw)
    for record in user_records:
        source = brain / record["source"]
        if digest(source.read_bytes()) != record["source_sha256"]:
            raise ValueError("User record source changed since extraction")
    # Export only visible task result fields; opaque signatures/payloads are excluded.
    events = []
    for session in (CORE, REVIEW):
        for path in sorted((brain / session / ".system_generated" / "messages").glob("*.json")):
            message = json.loads(path.read_text())
            title = message.get("renderDetails", {}).get("messageTitle")
            content = message.get("content")
            if not title or not content or not re.search(r"test|pytest|CI|ci_local", title, re.IGNORECASE):
                continue
            check_text(content.encode())
            events.append({"timestamp": message.get("timestamp"), "title": title,
                           "visible_result": content, "source_relative_path": str(path.relative_to(brain)),
                           "source_sha256": digest(path.read_bytes()),
                           "evidence_status": "execution_record_not_validation_of_inputs"})
    event_destination = DEST / "extracts" / "execution_events.json"
    write_once(event_destination, (json.dumps(events, indent=2)+"\n").encode())
    inventory = json.loads(discovery.read_text())
    october = [r for r in inventory["records"] if r["modified_utc"].startswith("2026-10")]
    report = {"schema_version": 1, "source_root": str(brain),
              "generated_utc": datetime.now(timezone.utc).isoformat(),
              "coverage": {"files_inventoried": len(inventory["records"]),
                           "total_bytes": sum(r["bytes"] for r in inventory["records"]),
                           "october_modified_files": len(october),
                           "scan_counts": inventory["scan_counts"],
                           "serialized_payloads_examined": payloads["payloads_seen"],
                           "user_text_slots_recovered": payloads["texts_recovered"],
                           "user_text_extraction_errors": len(payloads["errors"]),
                           "preserved_project_user_records": len(user_records)},
              "scope_limits": [
                  "Archive artifacts are not a guaranteed full transcript of Antigravity conversations",
                  "Only observed user-text protobuf slot 19.2 extracted; other internal fields excluded",
                  "No archive scripts executed; no private material uploaded",
                  "Unrelated projects and model-internal signatures not copied",
                  "No exhaustive OCR of unrelated images; project screenshots and animation reviewed",
                  "Existing audio matched byte-for-byte; existing transcripts reviewed, not retranscribed",
                  "Historical draft dates/metadata do not prove user authorship or empirical validity"],
              "records": records,
              "derived_extracts": [
                  {"destination": str(user_destination.relative_to(ROOT)),
                   "sha256": digest(user_destination.read_bytes()), "kind": "user_text_extraction"},
                  {"destination": str(event_destination.relative_to(ROOT)),
                   "sha256": digest(event_destination.read_bytes()), "kind": "visible_execution_events"}]}
    destination = DEST / "manifest.json"
    destination.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brain", type=Path, required=True)
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--user-payloads", type=Path, required=True)
    args = parser.parse_args()
    result = recover(args.brain, args.discovery, args.user_payloads)
    print("Preserved/reference records:", len(result["records"]))
    print("Coverage:", result["coverage"])


if __name__ == "__main__":
    main()
