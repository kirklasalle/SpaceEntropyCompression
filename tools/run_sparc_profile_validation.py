"""Fresh real-SPARC penalized profiles, with convergence and influence diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from itertools import pairwise
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emergent_matter_model.fetch_real_data import MANIFEST, fetch_sparc
from emergent_matter_model.sparc_marginalized_a0 import MarginalizedGalaxy
from emergent_matter_model.sparc_real_analysis import (
    ACC,
    LAWS,
    a0_horizon,
    load_sparc,
    v_model,
)
from emergent_matter_model.sparc_tension_diagnostics import build_subsets


def profile_interval(grid, objective):
    grid, objective = np.asarray(grid), np.asarray(objective)
    if (grid.ndim != 1 or objective.shape != grid.shape or len(grid) < 3
            or not np.all(np.isfinite(grid)) or not np.all(np.isfinite(objective))
            or not np.all(np.diff(grid) > 0)):
        raise ValueError("Profile requires finite objectives on an increasing grid of at least 3 points")
    i = int(np.argmin(objective))
    delta = np.asarray(objective) - objective[i]
    limits = []
    for indices in (range(i - 1, -1, -1), range(i + 1, len(grid))):
        previous = i
        crossing = None
        for j in indices:
            if delta[j] >= 1:
                crossing = float(grid[previous] + (grid[j] - grid[previous])
                                 * (1 - delta[previous]) / (delta[j] - delta[previous]))
                break
            previous = j
        limits.append(crossing)
    return {"a0_grid_minimum": float(grid[i]), "delta_Q_1_interval": limits,
            "at_grid_edge": i in (0, len(grid) - 1),
            "interval_kind": "conditional grid-interpolated penalized profile; not calibrated sigma"}


def residual_vector(x, mg, nu, a0, centre):
    """Gaussian residuals in the fixed catalogue-velocity coordinate, then constraints."""
    lu, fd, inc = x[:3]
    if len(x) == 4:
        vb2 = mg.vb2_gas + 10**lu * mg.vb2_disk + 10**x[3] * mg.vb2_bul
    else:
        vb2 = mg.vb2_gas + 10**lu * mg.vb2_star
    gbar = np.maximum(vb2, 1e-2) / mg.gal.r_kpc * ACC
    predicted = np.sqrt(gbar * nu(gbar / a0) / ACC * mg.gal.r_kpc * fd)
    predicted *= np.sin(np.deg2rad(inc)) / mg.sin_i0
    return np.r_[(mg.gal.v_obs - predicted) / mg.gal.v_err,
                 (lu - np.log10(centre)) / .1, (fd - 1) / mg.sig_fd,
                 (inc - mg.gal.inclination_deg) / mg.sig_i]


def residual_jacobian(x, mg, nu, a0, centre):
    """Differentiate the same residuals, including the declared baryonic floor."""
    lu, fd, inc = x[:3]
    stellar = 10**lu * (mg.vb2_disk if len(x) == 4 else mg.vb2_star)
    bulge = 10**x[3] * mg.vb2_bul if len(x) == 4 else np.zeros_like(stellar)
    raw = mg.vb2_gas + stellar + bulge
    gbar = np.maximum(raw, 1e-2) / mg.gal.r_kpc * ACC
    y = gbar / a0
    values = nu(y)
    if nu is LAWS["rar_exponential"][1]:
        t = np.sqrt(y)
        slope = -t * np.exp(-t) / (2 * -np.expm1(-t))
    elif nu is LAWS["emrf_sqrt"][1]:
        slope = -.5 / (1 + y)
    elif nu is LAWS["simple"][1]:
        slope = -1 / (2*y*np.sqrt(.25 + 1/y)*values)
    elif nu is LAWS["standard"][1]:
        slope = -1 / (values**2 * y**2 * np.sqrt(1 + 4/y**2))
    else:
        raise ValueError("No verified residual derivative for this acceleration law")
    predicted = np.sqrt(gbar*values / ACC * mg.gal.r_kpc * fd)
    predicted *= np.sin(np.deg2rad(inc)) / mg.sin_i0
    jac = np.zeros((mg.gal.n + 3, len(x)))
    factor = -.5 * predicted * (1 + slope) / gbar / mg.gal.v_err
    dg = np.log(10) * ACC / mg.gal.r_kpc * (raw > 1e-2)
    jac[:mg.gal.n, 0] = factor * dg * stellar
    jac[:mg.gal.n, 1] = -predicted / (2*fd*mg.gal.v_err)
    jac[:mg.gal.n, 2] = -predicted / mg.gal.v_err / np.tan(np.deg2rad(inc)) * np.pi/180
    if len(x) == 4:
        jac[:mg.gal.n, 3] = factor * dg * bulge
    jac[mg.gal.n:, :3] = np.diag([10., 1/mg.sig_fd, 1/mg.sig_i])
    return jac


def fit_one(mg, nu, a0, centre, warm=None):
    nominal = np.array([np.log10(centre), 1.0, mg.gal.inclination_deg])
    starts = [nominal, nominal + np.array([-.3, -.05, -2.]),
              nominal + np.array([.3, .05, 2.])]
    scale = [.1, mg.sig_fd, mg.sig_i]
    if len(mg.bounds) == 4:
        starts = [np.r_[x, np.log10(b)] for x, b in zip(starts, (.7, .2, 2.0))]
        scale.append(.3)
    bounds_options = [np.array(mg.bounds).T.copy()]
    # Signed gas components can create distinct minima on either side of the floor.
    cuts = []
    for seed in list(starts):
        star = mg.vb2_disk if len(seed) == 4 else mg.vb2_star
        gas = mg.vb2_gas + (10**seed[3]*mg.vb2_bul if len(seed) == 4 else 0)
        positive = star > 0
        thresholds = (1e-2 - gas[positive]) / star[positive]
        thresholds = thresholds[thresholds > 0]
        for threshold in thresholds:
            lu = np.log10(threshold)
            if mg.bounds[0][0] < lu < mg.bounds[0][1]:
                if len(seed) == 3:
                    cuts.append(lu)
                else:
                    for side in (-.02, .02):
                        extra = seed.copy()
                        extra[0] = lu + side
                        starts.append(extra)
    if cuts:
        edges = sorted({mg.bounds[0][0], *cuts, mg.bounds[0][1]})
        bounds_options = []
        for lo, hi in pairwise(edges):
            if hi - lo > 1e-10:
                bounds = np.array(mg.bounds).T.copy()
                bounds[:, 0] = [lo, hi]
                bounds_options.append(bounds)
    if warm is not None:
        starts.append(warm)
    fits = []
    for bounds in bounds_options:
        for start in starts:
            start = np.clip(start, bounds[0], bounds[1])
            res = least_squares(residual_vector, start,
                                args=(mg, nu, a0, centre), jac=residual_jacobian, x_scale=scale,
                                bounds=bounds,
                                max_nfev=600, ftol=1e-10, xtol=1e-10, gtol=1e-9)
            if res.success and np.isfinite(res.cost):
                fits.append(res)
    if not fits:
        raise RuntimeError(f"No converged fit: {mg.gal.name}, a0={a0}, centre={centre}")
    best = min(fits, key=lambda result: result.cost)
    return float(2 * best.cost), mg.chi2(best.x, nu, a0), best.x


def scan(gals, grid, centre=.5, reverse=False, bulge_ratio=1.4,
         law="rar_exponential", free_bulge=False):
    if free_bulge:
        from emergent_matter_model.sparc_bulge_test import FreeBulgeGalaxy
        models = [FreeBulgeGalaxy(g) for g in gals]
    else:
        models = [MarginalizedGalaxy(g) for g in gals]
    for mg in models:
        mg.vb2_star = (mg.gal.v_disk * np.abs(mg.gal.v_disk)
                       + bulge_ratio * mg.gal.v_bul * np.abs(mg.gal.v_bul))
    objectives = np.zeros((len(grid), len(gals)))
    chi = np.zeros_like(objectives)
    warm = [None] * len(gals)
    for j in (range(len(grid)-1, -1, -1) if reverse else range(len(grid))):
        for k, mg in enumerate(models):
            objectives[j, k], chi[j, k], warm[k] = fit_one(
                mg, LAWS[law][1], grid[j], centre, warm[k])
    return objectives, chi


def summarize(gals, grid, obj, chi, nuisance_count=3):
    total = obj.sum(axis=1)
    j = int(np.argmin(total))
    result = profile_interval(grid, total)
    result.update(n_galaxies=len(gals), n_points=sum(g.n for g in gals),
                  minimum_Q=float(total[j]), chi2_data=float(chi[j].sum()),
                  chi2_reduced_descriptive=float(chi[j].sum() / max(sum(g.n for g in gals)
                                                                      - nuisance_count*len(gals)-1, 1)),
                  objective_grid=total.tolist())
    loo = []
    for k, g in enumerate(gals):
        without = total - obj[:, k]
        loo.append({"removed": g.name, "a0": float(grid[np.argmin(without)])})
    result["leave_one_galaxy_out"] = loo
    result["loo_a0_range"] = [min(x["a0"] for x in loo), max(x["a0"] for x in loo)]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=float, default=.05, help="a0 grid step in 1e-10 SI")
    args = parser.parse_args()
    if not np.isfinite(args.step) or not 0 < args.step <= .1:
        parser.error("--step must be finite, positive and at most 0.1")
    fetch_sparc()
    gals = load_sparc()
    grid = np.unique(np.r_[np.arange(.5, 2.51, args.step)*1e-10,
                            a0_horizon(67.4), a0_horizon(73.0)])
    out = ROOT / "results" / "real_data_v1" / "sparc_profile_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(),
              "method": "scaled residual least-squares with analytic Jacobian; fixed-bulge floor branches optimized separately; three fixed starts and continuation; free-bulge floor seeds; successful optimizers only",
              "evidence": "fresh real SPARC rerun", "python": platform.python_version(),
              "numpy": np.__version__, "scipy": scipy.__version__, "command": sys.argv,
              "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
              "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
              "inputs": json.loads(MANIFEST.read_text()), "a0_grid": grid.tolist(),
              "BIC": None, "BIC_reason": "penalized optimum not unpenalized maximum likelihood",
              "H0_reference_values": {"67.4": a0_horizon(67.4), "73.0": a0_horizon(73.0)},
              "H0_uncertainty": "not folded into profile; reference-value comparisons only",
              "limitations": ["unknown radial covariance", "no calibrated significance",
                              "grid-interpolated conditional intervals", "post-hoc subsets",
                              "no full cosmological likelihood", "finite parameter bounds"],
              "complete": False, "numerically_verified": False,
              "fixed_stellar_baselines": {}, "samples": {}, "sensitivity": {},
              "other_law_profiles": {}}

    def save():
        result["source_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in [Path(__file__), *[
                                        ROOT / "emergent_matter_model" / name for name in (
                                            "sparc_marginalized_a0.py", "sparc_real_analysis.py",
                                            "sparc_tension_diagnostics.py", "sparc_bulge_test.py",
                                            "fetch_real_data.py", "data_provenance.py")]]}
        out.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")

    for name, (_, nu) in LAWS.items():
        def baseline(a, law=nu):
            return sum(float(np.sum(((g.v_obs-v_model(g, law, a*1e-10, .5))/g.v_err)**2))
                       for g in gals)
        fit = minimize_scalar(baseline, bounds=(.3, 3.0), method="bounded")
        if not fit.success:
            raise RuntimeError("Fixed stellar baseline failed")
        result["fixed_stellar_baselines"][name] = {"a0": float(fit.x*1e-10), "chi2": float(fit.fun)}
    save()
    obj, chi = scan(gals, grid)
    subsets = build_subsets(gals)
    selected = {"all": gals, "gas_dominated": subsets["gas_dominated"],
                "star_bulgeless": subsets["star_bulgeless"], "star_bulge": subsets["star_bulge"]}
    for label, sample in selected.items():
        names = {g.name for g in sample}
        mask = [g.name in names for g in gals]
        result["samples"][label] = summarize(sample, grid, obj[:, mask], chi[:, mask])
        q = obj[:, mask].sum(axis=1)
        result["samples"][label]["fixed_horizon_delta_Q"] = {
            str(h): float(q[np.argmin(abs(grid-a0_horizon(h)))]-q.min()) for h in (67.4, 73.)}
    save()
    print("Primary sample profiles written", flush=True)
    for centre in (.4, .6):
        o, c = scan(gals, grid, centre=centre)
        result["sensitivity"][f"upsilon_{centre}"] = summarize(gals, grid, o, c)
        save()
    for label in ("star_bulge_deep", "star_bulgeless_deep"):
        sample = subsets[label]
        o, c = scan(sample, grid)
        result["samples"][label] = summarize(sample, grid, o, c)
        save()
    for ratio in (.75, 2.0):
        sample = subsets["star_bulge"]
        ratio_grid = np.unique(np.r_[grid, np.arange(2.55, 4.01, args.step)*1e-10])
        o, c = scan(sample, ratio_grid, bulge_ratio=ratio)
        entry = summarize(sample, ratio_grid, o, c)
        entry["a0_grid"] = ratio_grid.tolist()
        result["sensitivity"][f"bulge_ratio_{ratio}"] = entry
        save()
    sample = subsets["star_bulge"]
    o, c = scan(sample, grid, free_bulge=True)
    result["sensitivity"]["free_bulge_post_hoc"] = summarize(
        sample, grid, o, c, nuisance_count=4)
    save()
    for name in ("emrf_sqrt", "simple", "standard"):
        o, c = scan(gals, grid, law=name)
        result["other_law_profiles"][name] = summarize(gals, grid, o, c)
        save()
    for name, sample in (
        ("quality_1", [g for g in gals if g.quality == 1]),
        ("inclination_40_to_80", [g for g in gals if 40 <= g.inclination_deg <= 80]),
    ):
        mask = [g.name in {s.name for s in sample} for g in gals]
        result["sensitivity"][name] = summarize(sample, grid, obj[:, mask], chi[:, mask])
    save()
    reverse, _ = scan(gals, grid, reverse=True)
    result["reverse_scan_max_total_Q_difference"] = float(abs(reverse.sum(axis=1)-obj.sum(axis=1)).max())
    result["numerically_verified"] = result["reverse_scan_max_total_Q_difference"] < .1
    result["scan_order_tolerance_Q"] = .1
    result["complete"] = True
    save()
    if not result["numerically_verified"]:
        raise RuntimeError("Scan-order check failed; results cannot support reported intervals")
    print(out, flush=True)


if __name__ == "__main__":
    main()
