"""Selected Candidate B restricted test: model predictions and data readiness.

Kirk LaSalle selected Candidates A and B on 2026-10-16, with B active, and
approved a restricted tree-level brane Higgs-portal test. This module freezes
the model side of that test and qualifies the public ATLAS contour product. It
does not compare the model with the contour; ``evaluate_candidate_b_atlas_contour.py``
does that after this readiness report is written.

All masses are in GeV and the radius ``R`` is in GeV^-1.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = ROOT / "knowledgebase" / "candidate_b_restricted_test_preregistration.json"
PROTOCOL = ROOT / "knowledgebase" / "candidate_b_first_test_protocol.json"
CATALOG = ROOT / "knowledgebase" / "library" / "data_catalog.json"
FIGURE4 = ROOT / "data" / "external" / "candidate_b" / "raw" / "hepdata_130266_v1_figure4.yaml"
OUTPUT = ROOT / "results" / "candidate_b_test_readiness.json"
DATASET_IDS = ("atlas-higgs-couplings-2022", "cms-hig-24-002-heavy-scalar-zz")
CHI2_2DOF_68 = -2.0 * math.log(1.0 - 0.6827)
CHI2_2DOF_95 = -2.0 * math.log(1.0 - 0.95)


@dataclass(frozen=True)
class Constants:
    g_fermi: float
    higgs_mass: float
    w_mass: float
    z_mass: float
    top_mass: float

    @property
    def vev(self) -> float:
        return float((math.sqrt(2.0) * self.g_fermi) ** -0.5)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def constants_from_preregistration(prereg: dict[str, Any],
                                   higgs_mass: float | None = None) -> Constants:
    c = prereg["constants"]
    return Constants(c["G_F_GeV_minus2"], higgs_mass or c["M_H_GeV"], c["m_W_GeV"],
                     c["m_Z_GeV"], c["m_t_GeV"])


# --- restricted model -------------------------------------------------------

def tower(radius: float, m5: float, cutoff: float) -> tuple[int, np.ndarray, np.ndarray]:
    """Return N_Lambda, unmixed cosine-mode masses squared and mu_n^2/mu_4^2."""
    if radius <= 0 or m5 <= 0 or cutoff <= m5:
        raise ValueError("require R>0, m5>0 and Lambda>m5")
    levels = math.floor(radius * math.sqrt(cutoff**2 - m5**2))
    n = np.arange(levels + 1, dtype=float)
    return levels, m5**2 + (n / radius) ** 2, np.where(n == 0, 1.0, 2.0)


def matched_sums(radius: float, m5: float, cutoff: float,
                 higgs_mass: float) -> tuple[float, float]:
    """S1 = sum w_n/(m_n^2-M_H^2) and S2 = sum w_n/(m_n^2-M_H^2)^2."""
    _, masses_sq, weights = tower(radius, m5, cutoff)
    gap = masses_sq - higgs_mass**2
    if np.any(gap <= 0):
        raise ValueError("every unmixed tower mass must exceed M_H")
    return float(np.sum(weights / gap)), float(np.sum(weights / gap**2))


def matched_kappa(mu4: float, radius: float, m5: float, cutoff: float,
                  constants: Constants) -> float:
    """Exact Higgs component of the state matched to M_H (secular equation)."""
    _, s2 = matched_sums(radius, m5, cutoff, constants.higgs_mass)
    return 1.0 / math.sqrt(1.0 + (constants.vev * mu4) ** 2 * s2)


def mu4_for_kappa(kappa: float, radius: float, m5: float, cutoff: float,
                  constants: Constants) -> float:
    if not 0.0 < kappa <= 1.0:
        raise ValueError("kappa must lie in (0, 1]")
    _, s2 = matched_sums(radius, m5, cutoff, constants.higgs_mass)
    return math.sqrt((kappa**-2 - 1.0) / (constants.vev**2 * s2))


def matched_unmixed_higgs_mass_sq(mu4: float, radius: float, m5: float, cutoff: float,
                                  constants: Constants) -> float:
    s1, _ = matched_sums(radius, m5, cutoff, constants.higgs_mass)
    return constants.higgs_mass**2 + (constants.vev * mu4) ** 2 * s1


def portal_couplings(mu4: float, levels: int) -> np.ndarray:
    return mu4 * np.where(np.arange(levels + 1) == 0, 1.0, math.sqrt(2.0))


def diagonalize(mu4: float, radius: float, m5: float, cutoff: float,
                constants: Constants) -> dict[str, Any]:
    """Diagonalize the matched (h, phi_0..phi_N) mass matrix."""
    levels, masses_sq, _ = tower(radius, m5, cutoff)
    mu = portal_couplings(mu4, levels)
    mh0_sq = matched_unmixed_higgs_mass_sq(mu4, radius, m5, cutoff, constants)
    size = levels + 2
    matrix = np.zeros((size, size))
    matrix[0, 0] = mh0_sq
    matrix[0, 1:] = matrix[1:, 0] = constants.vev * mu
    matrix[np.arange(1, size), np.arange(1, size)] = masses_sq
    eigenvalues, vectors = np.linalg.eigh(matrix)
    vectors = vectors * np.where(vectors[0] < 0, -1.0, 1.0)
    return {"levels": levels, "mu": mu, "mh0_sq": mh0_sq, "eigenvalues": eigenvalues,
            "vectors": vectors, "masses": np.sqrt(eigenvalues)}


def cubic_tensor_slice(state: int, vectors: np.ndarray, mu: np.ndarray, mh0_sq: float,
                       vev: float) -> np.ndarray:
    """g_abc = d^3V/dy_a dy_b dy_c for fixed a, from the tree-level cubic terms.

    Gauge basis: d^3V/dh^3 = 6 lambda v = 3 m_h0^2/v and d^3V/dh^2 dphi_n = mu_n.
    """
    u = vectors[0]
    w = mu @ vectors[1:]
    hhh = 3.0 * mh0_sq / vev
    ua, wa = u[state], w[state]
    slice_: np.ndarray = (hhh * ua + wa) * np.outer(u, u) + ua * (np.outer(w, u)
                                                                  + np.outer(u, w))
    return slice_


def two_scalar_width(state: int, masses: np.ndarray, coupling: np.ndarray) -> float:
    """Sum of on-shell widths for state -> b c over all open scalar pairs."""
    big = masses[state]
    light = masses[:state]
    total_sq, diff_sq = (light[:, None] + light) ** 2, (light[:, None] - light) ** 2
    kallen = (1 - total_sq / big**2) * (1 - diff_sq / big**2)
    upper = np.triu(np.ones((state, state), dtype=bool))
    open_pairs = upper & (total_sq < big**2)
    symmetry = np.where(np.eye(state, dtype=bool), 0.5, 1.0)
    g_sq = coupling[:state, :state] ** 2
    terms = symmetry * g_sq * np.sqrt(np.where(open_pairs, kallen, 0.0)) / (16 * math.pi * big)
    return float(np.sum(terms[open_pairs]))


def sm_like_tree_widths(mass: float, constants: Constants) -> dict[str, float]:
    """On-shell tree-level WW, ZZ and t tbar widths of an SM-like scalar of this mass."""
    widths = {}
    for name, boson, factor in (("WW", constants.w_mass, 2.0), ("ZZ", constants.z_mass, 1.0)):
        x = boson**2 / mass**2
        widths[name] = 0.0 if 4 * x >= 1 else factor * constants.g_fermi * mass**3 / (
            16 * math.sqrt(2) * math.pi) * math.sqrt(1 - 4 * x) * (1 - 4 * x + 12 * x**2)
    beta_sq = 1 - 4 * constants.top_mass**2 / mass**2
    widths["ttbar"] = 0.0 if beta_sq <= 0 else 3 * constants.g_fermi * constants.top_mass**2 * \
        mass / (4 * math.sqrt(2) * math.pi) * beta_sq**1.5
    return widths


def heavy_state_widths(spectrum: dict[str, Any], constants: Constants) -> list[dict[str, Any]]:
    masses, vectors = spectrum["masses"], spectrum["vectors"]
    rows = []
    for state in range(1, len(masses)):
        coupling = cubic_tensor_slice(state, vectors, spectrum["mu"], spectrum["mh0_sq"],
                                      constants.vev)
        scalar = two_scalar_width(state, masses, coupling)
        higgs_fraction = float(vectors[0, state] ** 2)
        tree = sm_like_tree_widths(float(masses[state]), constants)
        sm = {k: higgs_fraction * v for k, v in tree.items()}
        lower = scalar + sum(sm.values())
        rows.append({"mass_GeV": float(masses[state]), "higgs_fraction": higgs_fraction,
                     "two_scalar_width_GeV": scalar, "sm_like_tree_widths_GeV": sm,
                     "computed_width_lower_bound_GeV": lower,
                     "lower_bound_width_over_mass": lower / float(masses[state])})
    return rows


# --- data readiness ---------------------------------------------------------

def verify_holdings(catalog: dict[str, Any], dataset_ids: tuple[str, ...] = DATASET_IDS,
                    root: Path = ROOT) -> list[dict[str, Any]]:
    by_id = {entry["id"]: entry for entry in catalog["datasets"]}
    rows = []
    for dataset_id in dataset_ids:
        for holding in by_id[dataset_id]["holdings"]:
            path = root / holding["path"]
            present = path.is_file()
            rows.append({"dataset": dataset_id, "path": holding["path"], "present": present,
                         "sha256_matches": present and sha256_file(path) == holding["sha256"],
                         "bytes_match": present and path.stat().st_size == holding["bytes"]})
    return rows


def load_contour_table(path: Path) -> dict[str, Any]:
    table = yaml.safe_load(path.read_text(encoding="utf-8"))
    (independent,), (dependent,) = table["independent_variables"], table["dependent_variables"]
    x = np.array([v["value"] for v in independent["values"]], dtype=float)
    y = np.array([v["value"] for v in dependent["values"]], dtype=float)
    qualifiers = {q["name"]: q["value"] for q in dependent.get("qualifiers", [])}
    return {"points": np.column_stack([x, y]), "x_header": independent["header"]["name"],
            "y_header": dependent["header"]["name"], "qualifiers": qualifiers}


def split_closed_loops(points: np.ndarray, tolerance: float = 1e-12
                       ) -> tuple[list[np.ndarray], np.ndarray]:
    """Split an ordered vertex list into loops that return exactly to their start."""
    loops, start = [], 0
    while start < len(points):
        later = np.flatnonzero(np.linalg.norm(points[start + 3:] - points[start], axis=1)
                               <= tolerance)
        if later.size == 0:
            break
        end = start + 3 + int(later[0])
        loops.append(points[start:end + 1])
        start = end + 1
    return loops, points[start:]


def polygon_area(loop: np.ndarray) -> float:
    x, y = loop[:, 0], loop[:, 1]
    return 0.5 * float(np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))


def point_in_polygon(point: np.ndarray, loop: np.ndarray) -> bool:
    """Even-odd ray casting for a closed loop whose last vertex repeats the first."""
    px, py = float(point[0]), float(point[1])
    inside = False
    for (x0, y0), (x1, y1) in zip(loop[:-1], loop[1:], strict=True):
        if (y0 > py) != (y1 > py) and px < x0 + (py - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _segments_cross(p: np.ndarray, q: np.ndarray, r: np.ndarray, s: np.ndarray) -> bool:
    def orient(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        return float((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))

    return orient(p, q, r) * orient(p, q, s) < 0 and orient(r, s, p) * orient(r, s, q) < 0


def self_intersections(loop: np.ndarray) -> int:
    edges = len(loop) - 1
    count = 0
    for i in range(edges):
        for j in range(i + 2, edges):
            if i == 0 and j == edges - 1:
                continue
            count += _segments_cross(loop[i], loop[i + 1], loop[j], loop[j + 1])
    return count


def identify_contours(points: np.ndarray) -> dict[str, Any]:
    """Identify the observed 68% and 95% loops by nesting of confidence regions."""
    loops, leftover = split_closed_loops(points)
    summary: list[dict[str, Any]] = [
        {"vertices": len(loop), "area": abs(polygon_area(loop)),
         "self_intersections": self_intersections(loop),
         "kappa_V_range": [float(loop[:, 0].min()), float(loop[:, 0].max())],
         "kappa_F_range": [float(loop[:, 1].min()), float(loop[:, 1].max())]}
        for loop in loops]
    result: dict[str, Any] = {"closed_loops": summary, "unlooped_points": leftover.tolist(),
                              "identified": False}
    if len(loops) != 2 or any(row["self_intersections"] for row in summary):
        result["reason"] = "expected two closed, simple loops"
        return result
    areas = [abs(polygon_area(loop)) for loop in loops]
    inner, outer = sorted(range(2), key=lambda i: areas[i])
    nested = all(point_in_polygon(v, loops[outer]) for v in loops[inner][:-1])
    if not nested:
        result["reason"] = "loops are not nested"
        return result
    ratio = areas[outer] / areas[inner]
    result.update({
        "identified": True,
        "inner_loop_index": inner, "outer_loop_index": outer,
        "observed_95_loop": loops[outer].tolist(),
        "rule": "a 95% region from the same likelihood contains the 68% region, so the "
                "outer nested loop is the observed 95% contour",
        "area_ratio_outer_to_inner": ratio,
        "gaussian_two_parameter_area_ratio": CHI2_2DOF_95 / CHI2_2DOF_68,
        "unlooped_points_inside_both": [bool(point_in_polygon(p, loops[inner]))
                                        and bool(point_in_polygon(p, loops[outer]))
                                        for p in leftover],
        "unlooped_point_use": "unlabeled, consistent with a best-fit marker; not used",
    })
    return result


# --- report -----------------------------------------------------------------

def model_self_checks(prereg: dict[str, Any]) -> dict[str, Any]:
    """Compare the closed-form matched results with full diagonalization."""
    constants = constants_from_preregistration(prereg)
    grid = prereg["parameter_grid"]
    cutoff = grid["cutoff_GeV"]
    rows = []
    for inverse_radius in grid["inverse_radius_GeV"]:
        for m5 in grid["m5_GeV"]:
            radius = 1.0 / inverse_radius
            mu4 = mu4_for_kappa(0.9, radius, m5, cutoff, constants)
            spectrum = diagonalize(mu4, radius, m5, cutoff, constants)
            u = spectrum["vectors"][0]
            rows.append({
                "inverse_radius_GeV": inverse_radius, "m5_GeV": m5,
                "levels": spectrum["levels"],
                "probe_kappa": 0.9,
                "lightest_mass_error_GeV": abs(float(spectrum["masses"][0])
                                               - constants.higgs_mass),
                "kappa_error": abs(float(u[0]) - matched_kappa(mu4, radius, m5, cutoff,
                                                                constants)),
                "higgs_sum_rule_error": abs(float(np.sum(u**2)) - 1.0),
            })
    return {"probe": "kappa = 0.9 at every preregistered grid point; not a data value",
            "rows": rows,
            "max_lightest_mass_error_GeV": max(r["lightest_mass_error_GeV"] for r in rows),
            "max_kappa_error": max(r["kappa_error"] for r in rows),
            "max_sum_rule_error": max(r["higgs_sum_rule_error"] for r in rows)}


def build_report() -> dict[str, Any]:
    prereg = load_json(PREREGISTRATION)
    holdings = verify_holdings(load_json(CATALOG))
    report: dict[str, Any] = {
        "schema_version": 1,
        "artifact": "candidate_b_test_readiness",
        "source": Path(__file__).relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(Path(__file__)),
        "preregistration_sha256": sha256_file(PREREGISTRATION),
        "protocol_sha256": sha256_file(PROTOCOL),
        "research_selection": {"selected_candidates": ["candidate-a", "candidate-b"],
                               "active_candidate": "candidate-b"},
        "vev_GeV": constants_from_preregistration(prereg).vev,
        "model_self_checks": model_self_checks(prereg),
        "data_holdings": holdings,
        "comparison_performed": False,
        "evidence_kind": "model algebra and public-data qualification, not a test outcome",
    }
    if all(row["sha256_matches"] for row in holdings if row["dataset"] == DATASET_IDS[0]):
        table = load_contour_table(FIGURE4)
        contours = identify_contours(table["points"])
        contours.pop("observed_95_loop", None)
        report["atlas_figure4"] = {"headers": [table["x_header"], table["y_header"]],
                                   "qualifiers": table["qualifiers"],
                                   "vertex_count": len(table["points"]),
                                   "contours": contours}
        report["ready_for_comparison"] = bool(contours["identified"])
    else:
        report["ready_for_comparison"] = False
    return report


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_json(OUTPUT, report)
    print(f"Saved {OUTPUT}: ready_for_comparison={report['ready_for_comparison']}")
    print("Model and data readiness only; no comparison or empirical support is implied.")


if __name__ == "__main__":
    main()
