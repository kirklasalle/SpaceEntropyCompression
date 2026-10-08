"""SPARC Data Ingestion and Catalog Management Module.

Automates ingestion, validation, and metadata registration of galaxy rotation
curves from the Spitzer Photometry & Accurate Rotation Curves (SPARC) database
(Lelli, McGaugh, & Schombert 2016, Astronomical Journal 152:157).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List


def get_sparc_data_dir() -> Path:
    """Return the absolute path to the data/sparc directory."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    return repo_root / "data" / "synthetic" / "sparc"


def list_available_galaxies(sparc_dir: Path | None = None) -> List[str]:
    """Return list of galaxy IDs available in data/sparc."""
    if sparc_dir is None:
        sparc_dir = get_sparc_data_dir()
    
    galaxies = []
    for csv_file in sorted(sparc_dir.glob("*.csv")):
        if csv_file.name == "sparc_sample_summary.csv":
            continue
        galaxies.append(csv_file.stem.upper())
    return sorted(galaxies)


def validate_sparc_table(csv_path: Path) -> Dict[str, Any]:
    """Validate format and contents of a SPARC CSV file."""
    required_cols = {"radius_kpc", "v_obs_kms", "v_obs_err_kms", "v_gas_kms", "v_disk_kms", "v_bulge_kms"}
    rows: List[Dict[str, float]] = []
    
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(line for line in f if not line.lstrip().startswith("#"))
        fieldnames = set(reader.fieldnames or [])
        missing = required_cols - fieldnames
        if missing:
            raise ValueError(f"Missing required columns in {csv_path.name}: {missing}")
            
        for i, row in enumerate(reader):
            try:
                parsed_row = {col: float(row[col]) for col in required_cols}
                if parsed_row["radius_kpc"] <= 0:
                    raise ValueError(f"Row {i+1}: radius_kpc must be positive, got {parsed_row['radius_kpc']}")
                if parsed_row["v_obs_err_kms"] <= 0:
                    raise ValueError(f"Row {i+1}: v_obs_err_kms must be positive, got {parsed_row['v_obs_err_kms']}")
                rows.append(parsed_row)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Error parsing row {i+1} in {csv_path.name}: {e}") from e
                
    if not rows:
        raise ValueError(f"File {csv_path.name} contains no data rows.")
        
    return {
        "file": csv_path.name,
        "galaxy": csv_path.stem.upper(),
        "n_points": len(rows),
        "r_min": rows[0]["radius_kpc"],
        "r_max": rows[-1]["radius_kpc"],
        "v_max": max(r["v_obs_kms"] for r in rows),
        "valid": True
    }


def validate_catalog(sparc_dir: Path | None = None) -> List[Dict[str, Any]]:
    """Validate all galaxy tables in the catalog."""
    if sparc_dir is None:
        sparc_dir = get_sparc_data_dir()
        
    results = []
    for csv_file in sorted(sparc_dir.glob("*.csv")):
        if csv_file.name == "sparc_sample_summary.csv":
            continue
        res = validate_sparc_table(csv_file)
        results.append(res)
    return results


def main() -> int:
    """CLI entry point for SPARC catalog management."""
    parser = argparse.ArgumentParser(description="SPARC Data Ingestion and Catalog Management")
    parser.add_argument("--list", action="store_true", help="List available SPARC galaxies")
    parser.add_argument("--validate", action="store_true", help="Validate all SPARC CSV data files")
    args = parser.parse_args()
    
    sparc_dir = get_sparc_data_dir()
    
    if args.list or (not args.list and not args.validate):
        galaxies = list_available_galaxies(sparc_dir)
        print(f"Available SPARC Galaxies in {sparc_dir} ({len(galaxies)} total):")
        for g in galaxies:
            print(f"  - {g}")
            
    if args.validate:
        results = validate_catalog(sparc_dir)
        print(f"\nCatalog Validation Summary ({len(results)} galaxies):")
        total_pts = sum(r["n_points"] for r in results)
        for r in results:
            print(f"  [{r['galaxy']}] {r['n_points']:2d} points (r: {r['r_min']:.2f} - {r['r_max']:.2f} kpc, v_max: {r['v_max']:.1f} km/s) - OK")
        print(f"\nTotal radial data points across catalog: {total_pts}")
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
