"""Independently refit the most downward-influential deep-bulge exclusion."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.run_sparc_profile_validation import (
    build_subsets,
    load_sparc,
    scan,
    summarize,
)


def main():
    source = ROOT / "results" / "real_data_v1" / "sparc_profile_validation.json"
    data = json.loads(source.read_text())
    if not data.get("numerically_verified"):
        raise RuntimeError("Verify the primary profiles before checking their influence")
    sample = data["samples"]["star_bulge_deep"]
    exclusion = min(sample["leave_one_galaxy_out"], key=lambda row: row["a0"])
    galaxies = [g for g in build_subsets(load_sparc())["star_bulge_deep"]
                if g.name != exclusion["removed"]]
    grid = np.array(data["a0_grid"])
    objective, chi2 = scan(galaxies, grid)
    result = summarize(galaxies, grid, objective, chi2)
    if abs(result["a0_grid_minimum"] - exclusion["a0"]) > 1e-20:
        raise RuntimeError("Independent refit disagrees with profile subtraction")
    result.update(
        removed=exclusion["removed"],
        method="independent full-grid refit; exploratory exclusion, not a justified data cut",
        matches_profile_subtraction=True,
        parent_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    output = source.with_name("sparc_influence_crosscheck.json")
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(f"Verified {exclusion['removed']} exclusion: a0={result['a0_grid_minimum']:.3g}")


if __name__ == "__main__":
    main()
