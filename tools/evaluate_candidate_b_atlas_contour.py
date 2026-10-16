"""Selected Candidate B: restricted Higgs-portal comparison with ATLAS Figure 4.

Applies the frozen preregistration in
``knowledgebase/candidate_b_restricted_test_preregistration.json``. The
restricted model predicts kappa_V = kappa_F = kappa <= 1 for the observed Higgs
state. The statistic is the intersection of that diagonal with the published
observed 95% joint contour; no likelihood, p-value or one-parameter interval is
reconstructed. The result is a conditional compatibility statement, not
confirmation or exclusion of Candidate B as a whole.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "prepare_candidate_b_test", Path(__file__).with_name("prepare_candidate_b_test.py"))
assert _SPEC is not None and _SPEC.loader is not None
prep = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("prepare_candidate_b_test", prep)
_SPEC.loader.exec_module(prep)

OUTPUT = ROOT / "results" / "candidate_b_atlas_contour_test.json"
FROZEN_PREREGISTRATION_SHA256 = "69458ad7edd1c1e7362e04b553f318d5942922a5cc109d4bc524253eb7167f6d"
ISOLATION_GEV = 130.0
NARROW_WIDTH_RATIO = 0.01


def diagonal_intersection(loop: np.ndarray, k_max: float = 1.0) -> dict[str, Any]:
    """Return the parts of {(k, k): 0 <= k <= k_max} inside a closed polygon."""
    crossings, edges = [], []
    for start, end in zip(loop[:-1], loop[1:], strict=True):
        d0, d1 = start[0] - start[1], end[0] - end[1]
        if d0 == d1 or d0 * d1 > 0:
            continue
        s = d0 / (d0 - d1)
        k = float(start[0] + s * (end[0] - start[0]))
        crossings.append(k)
        edges.append(float(np.linalg.norm(end - start)))
    cuts = sorted({0.0, k_max, *(k for k in crossings if 0.0 < k < k_max)})
    inside = [(a, b) for a, b in zip(cuts[:-1], cuts[1:], strict=True)
              if prep.point_in_polygon(np.array([(a + b) / 2] * 2), loop)]
    return {"crossings": sorted(crossings), "crossing_edge_lengths": edges,
            "inside_intervals": [[a, b] for a, b in inside],
            "sm_point_inside": prep.point_in_polygon(np.array([k_max, k_max]), loop)}


def grid_point(inverse_radius: float, m5: float, cutoff: float,
               intervals: list[list[float]], constants: Any) -> dict[str, Any]:
    radius = 1.0 / inverse_radius
    levels, _, _ = prep.tower(radius, m5, cutoff)
    row: dict[str, Any] = {"inverse_radius_GeV": inverse_radius, "m5_GeV": m5,
                           "cutoff_GeV": cutoff, "levels": levels}
    if levels < 1:
        row["valid"] = False
        row["reason"] = "N_Lambda < 1"
        return row
    kappa_lo = intervals[0][0]
    row["mu4_ranges_GeV"] = [
        [prep.mu4_for_kappa(top, radius, m5, cutoff, constants),
         prep.mu4_for_kappa(bottom, radius, m5, cutoff, constants)]
        for bottom, top in reversed(intervals)]
    mu4 = prep.mu4_for_kappa(kappa_lo, radius, m5, cutoff, constants)
    spectrum = prep.diagonalize(mu4, radius, m5, cutoff, constants)
    masses = spectrum["masses"]
    widths = prep.heavy_state_widths(spectrum, constants)
    mu5 = mu4 * math.sqrt(2 * math.pi * radius)
    lam0 = spectrum["mh0_sq"] / (2 * constants.vev**2)
    worst = max(widths, key=lambda r: r["lower_bound_width_over_mass"])
    row.update({
        "valid": True,
        "mu4_max_GeV": mu4,
        "mu5_max_GeV_half": mu5,
        "brane_coefficient_mu5_over_sqrt_cutoff": mu5 / math.sqrt(cutoff),
        "unmixed_higgs_mass_GeV": math.sqrt(spectrum["mh0_sq"]),
        "brane_quartic_lambda0": lam0,
        "lightest_additional_mass_GeV": float(masses[1]),
        "heaviest_mass_GeV": float(masses[-1]),
        "flags": {
            "eigenmasses_below_cutoff": bool(masses[-1] < cutoff),
            "isolated_from_125": bool(masses[1] >= ISOLATION_GEV),
            "brane_coefficient_convention": bool(abs(mu5 / math.sqrt(cutoff)) < 1),
            "brane_quartic_convention": bool(lam0 <= 1),
            "lightest_additional_narrow_lower_bound": bool(
                widths[0]["lower_bound_width_over_mass"] < NARROW_WIDTH_RATIO),
        },
        "lightest_additional_states": widths[:3],
        "largest_lower_bound_width_over_mass": {
            "mass_GeV": worst["mass_GeV"], "ratio": worst["lower_bound_width_over_mass"]},
    })
    return row


def build_report() -> dict[str, Any]:
    prereg_sha = prep.sha256_file(prep.PREREGISTRATION)
    if prereg_sha != FROZEN_PREREGISTRATION_SHA256:
        raise RuntimeError("preregistration changed after it was frozen; stop")
    prereg = prep.load_json(prep.PREREGISTRATION)
    holdings = prep.verify_holdings(prep.load_json(prep.CATALOG), prep.DATASET_IDS[:1])
    if not all(row["sha256_matches"] for row in holdings):
        raise RuntimeError("ATLAS holdings missing or changed; stop")
    table = prep.load_contour_table(prep.FIGURE4)
    if table["qualifiers"].get("Exclusion contour") != "observed":
        raise RuntimeError("Figure 4 table is not the observed contour; stop")
    contours = prep.identify_contours(table["points"])
    if not contours["identified"]:
        raise RuntimeError(f"observed 95% contour ambiguous: {contours.get('reason')}")
    loop = np.array(contours.pop("observed_95_loop"))
    diagonal = diagonal_intersection(loop)
    intervals = diagonal["inside_intervals"]
    report: dict[str, Any] = {
        "schema_version": 1,
        "artifact": "candidate_b_atlas_contour_test",
        "source": Path(__file__).relative_to(ROOT).as_posix(),
        "source_sha256": prep.sha256_file(Path(__file__)),
        "model_source_sha256": prep.sha256_file(
            prep.ROOT / "tools" / "prepare_candidate_b_test.py"),
        "preregistration_sha256": prereg_sha,
        "protocol_sha256": prep.sha256_file(prep.PROTOCOL),
        "data": {"table_doi": "10.17182/hepdata.130266.v1/t4", "holdings": holdings,
                 "qualifiers": table["qualifiers"]},
        "contour_identification": {k: v for k, v in contours.items()
                                   if k not in ("closed_loops",)},
        "contour_loops": contours["closed_loops"],
        "diagonal": diagonal,
        "evidence_kind": "conditional compatibility with a published joint 95% region",
        "likelihood_evaluated": False,
        "one_parameter_interval_claimed": False,
        "candidate_b_confirmed": False,
    }
    if not intervals:
        report["outcome"] = "incompatible"
        report["interpretation"] = ("No point (k, k) with 0 <= k <= 1 lies inside the observed "
                                    "95% joint region, so every parameter point of the "
                                    "restricted hypothesis is incompatible with it.")
        return report
    kappa_lo = intervals[0][0]
    resolution = max(diagonal["crossing_edge_lengths"]) if diagonal["crossing_edge_lengths"] \
        else None
    grid = prereg["parameter_grid"]
    constants = prep.constants_from_preregistration(prereg)
    rows = [grid_point(r, m5, grid["cutoff_GeV"], intervals, constants)
            for r in grid["inverse_radius_GeV"] for m5 in grid["m5_GeV"]]
    sensitivity = []
    for mass in prereg["constants"]["M_H_sensitivity_GeV"]:
        shifted = prep.constants_from_preregistration(prereg, mass)
        for row in rows:
            if row["valid"]:
                alt = prep.mu4_for_kappa(kappa_lo, 1 / row["inverse_radius_GeV"], row["m5_GeV"],
                                         grid["cutoff_GeV"], shifted)
                sensitivity.append({"M_H_GeV": mass, "inverse_radius_GeV":
                                    row["inverse_radius_GeV"], "m5_GeV": row["m5_GeV"],
                                    "relative_change_mu4_max": alt / row["mu4_max_GeV"] - 1})
    report.update({
        "outcome": "compatible_with_limit",
        "kappa_lo": kappa_lo,
        "kappa_inside_intervals": intervals,
        "contour_resolution_at_crossing": resolution,
        "interpretation": (
            "The restricted hypothesis's universal suppression line enters the published "
            "observed 95% joint region. Parameter points with kappa < kappa_lo lie outside "
            "that region under its assumptions; mu4_max translates this boundary for each "
            "preregistered grid point. This is not a B-specific confidence interval."),
        "grid": rows,
        "higgs_mass_sensitivity": sensitivity,
        "max_abs_relative_change_mu4_max": max(abs(s["relative_change_mu4_max"])
                                               for s in sensitivity),
    })
    return report


def main() -> None:
    report = build_report()
    prep.write_json(OUTPUT, report)
    print(f"Saved {OUTPUT}: outcome={report['outcome']}")
    if report["outcome"] == "compatible_with_limit":
        print(f"kappa_lo = {report['kappa_lo']:.5f}; SM point inside: "
              f"{report['diagonal']['sm_point_inside']}")
    print("Conditional compatibility check only; no likelihood or confirmation is implied.")


if __name__ == "__main__":
    main()
