"""Candidate A, option 2: preregistered SPARC baryonic-matter falsification test.

Applies ``knowledgebase/candidate_a_sparc_baryonic_test_preregistration.json``.
With C = C_m (the Einstein-tensor energy projection), M = observed baryons and
alpha = 1, Candidate A predicts in the weak-field limit that every SPARC
rotation curve equals the Newtonian curve of its observed baryons. That
prediction (A2) is compared with a nested reference (REF) that may add a
non-negative pseudo-isothermal unseen-mass term. The operationalization is an
assistant proposal pending Kirk LaSalle's confirmation, and the test is not
blind: the repository and the literature already show the mass discrepancy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from emergent_matter_model.fetch_real_data import fetch_sparc  # noqa: E402
from emergent_matter_model.sparc_marginalized_a0 import MarginalizedGalaxy  # noqa: E402
from emergent_matter_model.sparc_real_analysis import Galaxy, load_sparc  # noqa: E402

PREREGISTRATION = ROOT / "knowledgebase" / "candidate_a_sparc_baryonic_test_preregistration.json"
FROZEN_PREREGISTRATION_SHA256 = "e1298e2c223882e12b0f05329e2c289f0875cd3eee2258747adedfe482d08e06"
OUTPUT = ROOT / "results" / "candidate_a_sparc_baryonic_test.json"
PINNED_DATA = {
    "Rotmod_LTG.zip": (
        "0a80cc90714828cc28b7dd57923576714d209f2490328c087c4a4ad607faf588", 110737),
    "SPARC_Lelli2016c.mrt": (
        "5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243", 28259),
}
SOURCE_DEPENDENCIES = (
    "emergent_matter_model/sparc_real_analysis.py",
    "emergent_matter_model/sparc_marginalized_a0.py",
    "emergent_matter_model/fetch_real_data.py",
)

UPS_CENTRE = 0.5
UPS_PRIOR_DEX = 0.1
LOG_UPS_UPPER = 0.7
VB2_FLOOR = 1e-2
S_MAX = 250000.0
LOG_RC_BOUNDS = (-2.0, 2.0)
REF_EXTRA_PARAMETERS = 2
NUISANCE_PARAMETERS = 3
CONFIDENCE = 0.999
GALAXY_THRESHOLD = float(chi2.ppf(CONFIDENCE, REF_EXTRA_PARAMETERS))
TREATMENTS = ("T1", "T2")
LEAST_SQUARES: dict[str, Any] = {
    "method": "trf", "jac": "3-point", "ftol": 1e-10, "xtol": 1e-10, "gtol": 1e-9,
    "max_nfev": 2000,
}


class IncompleteTestError(RuntimeError):
    """A frozen completeness rule failed; the outcome is 'incomplete'."""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_preregistration() -> dict[str, Any]:
    """Return the frozen preregistration, refusing any modified copy."""
    if _sha(PREREGISTRATION) != FROZEN_PREREGISTRATION_SHA256:
        raise IncompleteTestError("Preregistration bytes differ from the frozen SHA-256")
    loaded: dict[str, Any] = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    return loaded


def verify_data(sparc: Path) -> list[dict[str, Any]]:
    """Check every SPARC holding against the hashes pinned in the preregistration."""
    holdings = []
    for name, (digest, size) in PINNED_DATA.items():
        path = sparc / name
        if not path.is_file() or path.stat().st_size != size or _sha(path) != digest:
            raise IncompleteTestError(f"SPARC holding does not match its pinned hash: {name}")
        holdings.append({"file": f"data/external/sparc/{name}", "bytes": size, "sha256": digest})
    return holdings


def halo_v2(r_kpc: np.ndarray, s: float, log_rc: float) -> np.ndarray:
    """Pseudo-isothermal circular-speed term s (1 - (r_c/R) arctan(R/r_c)), in (km/s)^2."""
    rc = 10.0**log_rc
    values: np.ndarray = s * (1.0 - (rc / r_kpc) * np.arctan(r_kpc / rc))
    return values


def predicted_velocity(mg: MarginalizedGalaxy,
                       params: Sequence[float] | np.ndarray) -> np.ndarray:
    """A2 (three parameters) or REF (five parameters) in the catalogue-velocity coordinate."""
    log_ups, f_d, inc = params[0], params[1], params[2]
    v2 = np.maximum(mg.vb2_gas + 10.0**log_ups * mg.vb2_star, VB2_FLOOR) * f_d
    if len(params) == 5:
        v2 = v2 + halo_v2(mg.gal.r_kpc, params[3], params[4])
    velocity: np.ndarray = np.sqrt(v2) * math.sin(math.radians(inc)) / mg.sin_i0
    return velocity


def residuals(params: np.ndarray, mg: MarginalizedGalaxy, treatment: str,
              ups_centre: float) -> np.ndarray:
    """Data residuals followed by the treatment's prior residuals."""
    data = (mg.gal.v_obs - predicted_velocity(mg, params)) / mg.gal.v_err
    priors = [(params[1] - 1.0) / mg.sig_fd, (params[2] - mg.gal.inclination_deg) / mg.sig_i]
    if treatment == "T1":
        priors.insert(0, (params[0] - math.log10(ups_centre)) / UPS_PRIOR_DEX)
    elif treatment != "T2":
        raise ValueError(f"Unknown treatment: {treatment}")
    stacked: np.ndarray = np.r_[data, priors]
    return stacked


def chi2_data(mg: MarginalizedGalaxy, params: Sequence[float] | np.ndarray) -> float:
    return float(np.sum(((mg.gal.v_obs - predicted_velocity(mg, params)) / mg.gal.v_err) ** 2))


def _best_of(mg: MarginalizedGalaxy, starts: list[np.ndarray], lower: np.ndarray,
             upper: np.ndarray, x_scale: np.ndarray, treatment: str,
             ups_centre: float) -> tuple[float | None, np.ndarray | None, int, int]:
    best_q: float | None = None
    best_x: np.ndarray | None = None
    counted = 0
    for start in starts:
        result = least_squares(residuals, np.clip(start, lower, upper), bounds=(lower, upper),
                               x_scale=x_scale, args=(mg, treatment, ups_centre), **LEAST_SQUARES)
        q = 2.0 * float(result.cost)
        if result.success and math.isfinite(q) and np.all(np.isfinite(result.x)):
            counted += 1
            if best_q is None or q < best_q:
                best_q, best_x = q, np.asarray(result.x, dtype=float)
    return best_q, best_x, len(starts), counted


def _a2_bounds(mg: MarginalizedGalaxy) -> tuple[np.ndarray, np.ndarray]:
    bounds = np.asarray(mg.bounds, dtype=float)
    return bounds[:, 0].copy(), bounds[:, 1].copy()


def fit_a2(mg: MarginalizedGalaxy, treatment: str, ups_centre: float) -> dict[str, Any]:
    """Profile the A2 objective over the nuisance parameters from the frozen starts."""
    lower, upper = _a2_bounds(mg)
    i0 = mg.gal.inclination_deg
    starts = [np.array([log_ups, f_d, inc])
              for log_ups in (math.log10(0.5), math.log10(0.5) - 0.3,
                              math.log10(0.5) + 0.3, 0.69)
              for f_d, inc in ((1.0, i0), (1.0 + 2 * mg.sig_fd, i0 + 2 * mg.sig_i))]
    x_scale = np.array([0.1, mg.sig_fd, mg.sig_i])
    q, x, attempted, counted = _best_of(mg, starts, lower, upper, x_scale, treatment, ups_centre)
    if q is None or x is None:
        raise IncompleteTestError(f"No counted A2 start: {mg.gal.name} {treatment}")
    return {"Q": q, "x": x, "chi2_data": chi2_data(mg, x), "attempted": attempted,
            "counted": counted}


def fit_ref(mg: MarginalizedGalaxy, treatment: str, ups_centre: float,
            a2: dict[str, Any]) -> dict[str, Any]:
    """Profile the nested REF objective; the A2 optimum (s = 0) is always a candidate."""
    lower_a2, upper_a2 = _a2_bounds(mg)
    lower = np.r_[lower_a2, 0.0, LOG_RC_BOUNDS[0]]
    upper = np.r_[upper_a2, S_MAX, LOG_RC_BOUNDS[1]]
    vmax2 = min(float(np.max(mg.gal.v_obs)) ** 2, S_MAX)
    starts = [np.r_[a2["x"], fraction * vmax2, log_rc]
              for fraction in (0.25, 1.0)
              for log_rc in (math.log10(0.5), math.log10(2.0), math.log10(8.0))]
    starts += [np.array([log_ups, 1.0, mg.gal.inclination_deg, vmax2, math.log10(2.0)])
               for log_ups in (math.log10(0.5), math.log10(0.5) - 0.3,
                               math.log10(0.5) + 0.3, 0.69)]
    x_scale = np.array([0.1, mg.sig_fd, mg.sig_i, max(vmax2, 1.0), 0.5])
    q, x, attempted, counted = _best_of(mg, starts, lower, upper, x_scale, treatment, ups_centre)
    if q is None or x is None:
        raise IncompleteTestError(f"No counted REF start: {mg.gal.name} {treatment}")
    from_a2_point = a2["Q"] <= q
    if from_a2_point:
        q, x = float(a2["Q"]), np.r_[a2["x"], 0.0, 0.0]
    return {"Q": q, "x": x, "chi2_data": chi2_data(mg, x), "attempted": attempted,
            "counted": counted, "a2_point_selected": bool(from_a2_point)}


def _percentiles(values: list[float]) -> dict[str, float]:
    p16, p50, p84 = np.percentile(np.asarray(values, dtype=float), [16, 50, 84])
    return {"p16": float(p16), "median": float(p50), "p84": float(p84)}


def evaluate_population(galaxies: list[Galaxy], treatment: str,
                        ups_centre: float = UPS_CENTRE) -> dict[str, Any]:
    """Apply the frozen statistic to one population under one treatment."""
    rows: list[dict[str, Any]] = []
    for galaxy in galaxies:
        mg = MarginalizedGalaxy(galaxy)
        a2 = fit_a2(mg, treatment, ups_centre)
        ref = fit_ref(mg, treatment, ups_centre, a2)
        outer = int(np.argmax(galaxy.r_kpc))
        predicted = predicted_velocity(mg, a2["x"])
        rows.append({
            "galaxy": galaxy.name, "quality": galaxy.quality, "points": galaxy.n,
            "Q_A2": a2["Q"], "Q_REF": ref["Q"], "delta_Q": a2["Q"] - ref["Q"],
            "chi2_data_A2": a2["chi2_data"], "chi2_data_REF": ref["chi2_data"],
            "a2_upsilon_disk": float(10.0 ** a2["x"][0]), "a2_f_D": float(a2["x"][1]),
            "a2_inclination_deg": float(a2["x"][2]),
            "ref_s_km2_s2": float(ref["x"][3]), "ref_log10_rc_kpc": float(ref["x"][4]),
            "ref_a2_point_selected": ref["a2_point_selected"],
            "outer_ratio_vobs2_over_va2_2": float(galaxy.v_obs[outer] ** 2 / predicted[outer] ** 2),
            "starts": {"a2_attempted": a2["attempted"], "a2_counted": a2["counted"],
                       "ref_attempted": ref["attempted"], "ref_counted": ref["counted"]},
        })
    values = [v for row in rows for v in (row["Q_A2"], row["Q_REF"], row["delta_Q"])]
    if not all(math.isfinite(v) for v in values) or any(row["delta_Q"] < 0 for row in rows):
        raise IncompleteTestError(f"Non-finite or negative statistic under {treatment}")
    n_galaxies = len(rows)
    n_points = sum(row["points"] for row in rows)
    chi2_ref = sum(row["chi2_data_REF"] for row in rows)
    dof = max(n_points - (NUISANCE_PARAMETERS + REF_EXTRA_PARAMETERS) * n_galaxies, 1)
    inflation = max(1.0, chi2_ref / dof)
    for row in rows:
        row["delta_Q_cons"] = row["delta_Q"] / inflation
        row["requires_unseen_mass"] = bool(row["delta_Q_cons"] > GALAXY_THRESHOLD
                                           and row["ref_s_km2_s2"] > 0)
    delta_q = sum(row["delta_Q"] for row in rows)
    delta_q_cons = delta_q / inflation
    threshold = float(chi2.ppf(CONFIDENCE, REF_EXTRA_PARAMETERS * n_galaxies))
    requiring = sum(row["requires_unseen_mass"] for row in rows)
    at_upper = sum(abs(row["a2_upsilon_disk"] - 10.0**LOG_UPS_UPPER) < 1e-3 * 10.0**LOG_UPS_UPPER
                   for row in rows)
    starts = {key: sum(row["starts"][key] for row in rows)
              for key in ("a2_attempted", "a2_counted", "ref_attempted", "ref_counted")}
    return {
        "treatment": treatment, "upsilon_prior_centre": ups_centre if treatment == "T1" else None,
        "galaxies": n_galaxies, "points": n_points,
        "sum_Q_A2": sum(row["Q_A2"] for row in rows),
        "sum_Q_REF": sum(row["Q_REF"] for row in rows),
        "chi2_data_A2": sum(row["chi2_data_A2"] for row in rows), "chi2_data_REF": chi2_ref,
        "inflation_dof": dof, "inflation_lambda": inflation,
        "delta_Q": delta_q, "delta_Q_cons": delta_q_cons,
        "population_threshold": threshold, "galaxy_threshold": GALAXY_THRESHOLD,
        "exceeds_population_threshold": bool(delta_q_cons > threshold),
        "uninflated_exceeds_population_threshold": bool(delta_q > threshold),
        "galaxies_requiring_unseen_mass": requiring,
        "fraction_requiring_unseen_mass": requiring / n_galaxies,
        "outer_ratio_vobs2_over_va2_2": _percentiles(
            [row["outer_ratio_vobs2_over_va2_2"] for row in rows]),
        "fraction_upsilon_disk_at_upper_bound": at_upper / n_galaxies,
        "optimizer_starts": {**starts,
                             "a2_failed": starts["a2_attempted"] - starts["a2_counted"],
                             "ref_failed": starts["ref_attempted"] - starts["ref_counted"]},
        "per_galaxy": rows,
    }


def classify(t1: dict[str, Any], t2: dict[str, Any]) -> str:
    """Frozen outcome rule: rejected only if both treatments exceed the population threshold."""
    if t1["exceeds_population_threshold"] and t2["exceeds_population_threshold"]:
        return "rejected"
    return "not_rejected"


def _strip(summary: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in summary.items() if key != "per_galaxy"}


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def run(evaluate: Callable[[list[Galaxy], str, float], dict[str, Any]] = evaluate_population
        ) -> dict[str, Any]:
    """Run every frozen step and return the artifact dictionary."""
    verify_preregistration()
    sparc = fetch_sparc()
    holdings = verify_data(sparc)
    primary = load_sparc(sparc)
    secondary = [g for g in load_sparc(sparc, max_quality=3) if g.quality == 3]
    deviations = []
    if len(primary) != 153 or sum(g.n for g in primary) != 3168:
        deviations.append(f"Primary population has {len(primary)} galaxies and "
                          f"{sum(g.n for g in primary)} points, not 153 and 3168")
    report: dict[str, Any] = {
        "schema_version": 1,
        "test_id": "candidate-a-option2-sparc-baryonic-v1",
        "candidate": "candidate-a",
        "operationalization": "C = C_m, M = observed baryons, alpha = 1 (option 2)",
        "operationalization_status": "assistant_proposed_pending_author_confirmation",
        "evidence_class": "preregistered observational falsification test; not blind",
        "preregistration": "knowledgebase/candidate_a_sparc_baryonic_test_preregistration.json",
        "preregistration_sha256": FROZEN_PREREGISTRATION_SHA256,
        "source_sha256": _sha(Path(__file__)),
        "dependency_sha256": {name: _sha(ROOT / name) for name in SOURCE_DEPENDENCIES},
        "data": holdings,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__},
        "revision": _git("rev-parse", "HEAD"),
        "implementation_notes": [
            "x_scale is not specified by the preregistration; it was fixed before running to "
            "the natural parameter scales (0.1 dex, sigma_fD, sigma_i, max(V_obs)^2, 0.5 dex).",
            "The halo radius uses the catalogue radius; the free r_c absorbs distance rescaling.",
        ],
        "protocol_deviations": deviations,
    }
    try:
        populations: dict[str, dict[str, Any]] = {}
        for label, sample in (("primary", primary), ("secondary_q3", secondary)):
            populations[label] = {t: evaluate(sample, t, UPS_CENTRE) for t in TREATMENTS}
        sensitivity = {f"T1_upsilon_centre_{c}": _strip(evaluate(primary, "T1", c))
                       for c in (0.4, 0.6)}
    except IncompleteTestError as error:
        report.update(outcome="incomplete", incomplete_reason=str(error))
        return report
    outcome = classify(populations["primary"]["T1"], populations["primary"]["T2"])
    secondary_outcome = classify(populations["secondary_q3"]["T1"],
                                 populations["secondary_q3"]["T2"])
    report.update({
        "outcome": outcome,
        "secondary_q3_outcome": secondary_outcome,
        "populations": {label: {t: _strip(s) for t, s in by_t.items()}
                        for label, by_t in populations.items()},
        "sensitivity_never_the_result": sensitivity,
        "per_galaxy_primary": {t: populations["primary"][t]["per_galaxy"] for t in TREATMENTS},
        "interpretation": interpretation(outcome),
    })
    return report


def interpretation(outcome: str) -> list[str]:
    common = [
        "This tests one assistant-proposed operationalization of Candidate A (option 2), "
        "pending Kirk LaSalle's confirmation.",
        "It is not blind: the mass discrepancy in SPARC was known in the literature and in "
        "this repository before the preregistration was frozen.",
        "Option 1 (M = all gravitating energy) is an exact GR identity and is not tested here.",
    ]
    if outcome == "rejected":
        return [
            "Under both nuisance treatments, the SPARC rotation curves require mass beyond the "
            "observed baryons, so Candidate A with M = observed baryons, C = C_m and alpha = 1 "
            "is falsified for disc galaxies.",
            "Calling the missing mass 'emergent matter' would be a relabelling unless Candidate A "
            "independently predicted its amount and distribution.",
            *common,
        ]
    return [
        "The frozen rule did not reject option 2. This does not confirm Candidate A.",
        *common,
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{report['outcome']}: {args.output}")
    return 0 if report["outcome"] != "incomplete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
