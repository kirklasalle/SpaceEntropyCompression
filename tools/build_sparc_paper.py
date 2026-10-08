"""Build the research PDF locally and record the exact inputs and compiler outcome."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default="tectonic", help="Path to the Tectonic executable")
    args = parser.parse_args()
    paper = ROOT / "paper"
    inputs = [paper / name for name in (
        "sparc_horizon_test.tex", "sparc_horizon_results.tex", "sparc_horizon_references.bib")]
    inputs.append(paper / "figures" / "sparc_fresh_profiles.png")
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in inputs}
    version = subprocess.check_output([args.compiler, "--version"], text=True).strip()
    command = [args.compiler, "--untrusted", "--keep-logs", "sparc_horizon_test.tex"]
    completed = subprocess.run(command, cwd=paper, capture_output=True, text=True, check=False)
    print(completed.stdout)
    print(completed.stderr)
    artifact = {"compiler": version, "command": command[1:],
                "completed_utc": datetime.now(timezone.utc).isoformat(),
                "returncode": completed.returncode, "source_sha256": hashes,
                "stdout": completed.stdout, "stderr": completed.stderr}
    output = paper / "sparc_horizon_test.pdf"
    if completed.returncode == 0:
        raw = output.read_bytes()
        if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-1024:]:
            raise RuntimeError("Compiler returned success without a complete PDF")
        artifact["pdf_sha256"] = hashlib.sha256(raw).hexdigest()
        artifact["pdf_bytes"] = len(raw)
    record = ROOT / "results" / "real_data_v1" / "manuscript_build.json"
    record.write_text(json.dumps(artifact, indent=2)+"\n", encoding="utf-8")
    completed.check_returncode()


if __name__ == "__main__":
    main()
