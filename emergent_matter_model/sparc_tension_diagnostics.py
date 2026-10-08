"""Diagnosing the gas- vs star-dominated a0 disagreement (real SPARC data).

The marginalized analysis (sparc_marginalized_a0.py) found, for the RAR law,
a0 = 1.02 +/- 0.08 (66 gas-dominated galaxies) but a higher value for the full sample.
This module asks *why*, by re-fitting the star-dominated galaxies after removing the
places where stellar modelling or the interpolating-function shape could bias a0.

Pre-registered subsets (all cuts use the nominal Upsilon_disk = 0.5 and are fixed before fitting)
--------------------------------------------------------------------------------------------------
A  gas_dominated               reference (galaxy gas fraction > 0.5), all points
B  star_dominated              galaxy gas fraction <= 0.5, all points
C  star_bulgeless              B without any galaxy that has a bulge component (any V_bul > 0)
D  star_deep_points            B, only points with g_bar < 0.3 * 1.2e-10 m/s^2 (deep regime:
                               the interpolating-function shape no longer matters)
E  star_local_gas_points       B, only points where gas supplies > 50% of the local V_bar^2
F  star_bulgeless_deep         C and D combined
G  all_deep_points             every galaxy, deep points only
H  star_bulge                  complement of C: star-dominated galaxies WITH a bulge (added after the
                               first run, because removing them moved a0 strongly; labelled post hoc)
I  star_bulge_deep             H, deep points only (post hoc)

Galaxies left with fewer than MIN_POINTS points after a cut are dropped.
Each subset is fitted with the RAR law for Upsilon prior centres 0.4 / 0.5 / 0.6 (distance and
inclination marginalized), and subset D is also fitted with all four laws to test whether the
law dependence disappears in the deep regime.

Reading the outcome
-------------------
* If D/E/F move down to the gas-dominated value -> the tension comes from stellar modelling or the
  interpolating-function shape at higher acceleration, not from a0 itself.
* If they stay high -> star-dominated galaxies genuinely prefer a larger a0, and the disagreement
  is a real problem for a single universal a0 (and therefore for a0 = c H0 / 2 pi).

Usage
-----
    python emergent_matter_model/sparc_tension_diagnostics.py      # ~15 min
    python emergent_matter_model/sparc_tension_diagnostics.py --plot-only
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math

import numpy as np

try:
    from sparc_marginalized_a0 import (GAS_DOMINATED, UPS_CENTRES, MarginalizedGalaxy, best_a0, implied_h0,
                                       profile)
    from sparc_real_analysis import (FIGURE_DIR, H0_VALUES, LAWS, RESULTS_DIR, UPS_DISK_PRIOR, Galaxy, a0_horizon,
                                     g_newton, load_sparc)
except ImportError:  # imported as a package
    from emergent_matter_model.sparc_marginalized_a0 import (GAS_DOMINATED, UPS_CENTRES, MarginalizedGalaxy,
                                                             best_a0, implied_h0, profile)
    from emergent_matter_model.sparc_real_analysis import (FIGURE_DIR, H0_VALUES, LAWS, RESULTS_DIR,
                                                           UPS_DISK_PRIOR, Galaxy, a0_horizon, g_newton,
                                                           load_sparc)

A0_REF = 1.2e-10
DEEP_FRACTION = 0.3
MIN_POINTS = 3
GRID = np.arange(0.50e-10, 2.00e-10 + 1e-15, 0.03e-10)

SUBSET_LABELS = {
    "gas_dominated": "A: gas-dominated galaxies (reference)",
    "star_dominated": "B: star-dominated galaxies, all points",
    "star_bulgeless": "C: star-dominated, bulgeless galaxies",
    "star_deep_points": "D: star-dominated, deep points only",
    "star_local_gas_points": "E: star-dominated, locally gas-dominated points",
    "star_bulgeless_deep": "F: star-dominated, bulgeless, deep points",
    "all_deep_points": "G: all galaxies, deep points only",
    "star_bulge": "H: star-dominated, bulge galaxies (post hoc)",
    "star_bulge_deep": "I: star-dominated, bulge galaxies, deep pts (post hoc)",
}


# --- Point and galaxy selections ---------------------------------------------
def has_bulge(gal: Galaxy) -> bool:
    return bool(np.any(gal.v_bul > 0))


def deep_point_mask(gal: Galaxy, ups: float = UPS_DISK_PRIOR) -> np.ndarray:
    """Points in the deep-MOND regime at nominal stellar mass: g_bar < DEEP_FRACTION * A0_REF."""
    return g_newton(gal, ups) < DEEP_FRACTION * A0_REF


def local_gas_point_mask(gal: Galaxy, ups: float = UPS_DISK_PRIOR) -> np.ndarray:
    """Points where gas supplies more than half of the local baryonic V^2 at nominal stellar mass."""
    gas = gal.v_gas * np.abs(gal.v_gas)
    star = ups * (gal.v_disk * np.abs(gal.v_disk) + 1.4 * gal.v_bul * np.abs(gal.v_bul))
    total = gas + star
    return (total > 0) & (gas > 0.5 * total)


def subset_points(gal: Galaxy, mask: np.ndarray) -> Galaxy | None:
    if int(mask.sum()) < MIN_POINTS:
        return None
    return dataclasses.replace(gal, r_kpc=gal.r_kpc[mask], v_obs=gal.v_obs[mask], v_err=gal.v_err[mask],
                               v_gas=gal.v_gas[mask], v_disk=gal.v_disk[mask], v_bul=gal.v_bul[mask])


def build_subsets(gals: list[Galaxy]) -> dict[str, list[Galaxy]]:
    gas = [g for g in gals if g.gas_fraction() > GAS_DOMINATED]
    star = [g for g in gals if g.gas_fraction() <= GAS_DOMINATED]
    star_nb = [g for g in star if not has_bulge(g)]
    star_b = [g for g in star if has_bulge(g)]

    def cut(sample, mask_fn):
        out = []
        for g in sample:
            s = subset_points(g, mask_fn(g))
            if s is not None:
                out.append(s)
        return out

    return {
        "gas_dominated": gas,
        "star_dominated": star,
        "star_bulgeless": star_nb,
        "star_deep_points": cut(star, deep_point_mask),
        "star_local_gas_points": cut(star, local_gas_point_mask),
        "star_bulgeless_deep": cut(star_nb, deep_point_mask),
        "all_deep_points": cut(gals, deep_point_mask),
        "star_bulge": star_b,
        "star_bulge_deep": cut(star_b, deep_point_mask),
    }


# --- Fitting ------------------------------------------------------------------
def fit_subset(sample: list[Galaxy], law_key: str, ups_centres=UPS_CENTRES) -> dict:
    nu = LAWS[law_key][1]
    mgals = [MarginalizedGalaxy(g) for g in sample]
    n_pts = int(sum(g.n for g in sample))
    by_ups = {}
    for ups0 in ups_centres:
        prof = profile(mgals, nu, law_key, ups0, GRID)
        obj = prof[:, :, 0].sum(axis=1)
        j = int(np.argmin(obj))
        chi_min = float(prof[j, :, 1].sum())
        chi2_red = chi_min / max(n_pts - (3 * len(sample) + 1), 1)
        b = best_a0(GRID, obj, chi2_red)
        b.update({"chi2": chi_min, "chi2_reduced": chi2_red})
        by_ups[str(ups0)] = b
    base = by_ups[str(UPS_DISK_PRIOR)] if str(UPS_DISK_PRIOR) in by_ups else next(iter(by_ups.values()))
    vals = [b["a0"] for b in by_ups.values()]
    sys_half = (max(vals) - min(vals)) / 2.0
    total = math.hypot(base["sigma_scaled"], sys_half)
    return {
        "n_galaxies": len(sample), "n_points": n_pts,
        "a0": base["a0"], "sigma_stat_scaled": base["sigma_scaled"], "sigma_upsilon_sys": sys_half,
        "sigma_total": total, "chi2_reduced": base["chi2_reduced"], "at_grid_edge": base["at_grid_edge"],
        "by_upsilon_centre": by_ups,
        "pulls_vs_horizon": {lbl: (base["a0"] - a0_horizon(h)) / total for lbl, h in H0_VALUES.items()},
        "implied_H0_kms_mpc": implied_h0(base["a0"]),
    }


def tension(a: dict, b: dict) -> float:
    return (a["a0"] - b["a0"]) / math.hypot(a["sigma_total"], b["sigma_total"])


def run(make_figures: bool = True) -> dict:
    gals = load_sparc()
    subsets = build_subsets(gals)
    results = {
        "description": "Real SPARC; distance, inclination and Upsilon marginalized (Li et al. 2018 method); "
                       "pre-registered subsets testing the gas- vs star-dominated a0 disagreement",
        "cuts": {"gas_dominated_galaxy": f"gas fraction > {GAS_DOMINATED}",
                 "deep_point": f"g_bar(Upsilon=0.5) < {DEEP_FRACTION} x {A0_REF:.1e} m/s^2",
                 "local_gas_point": "gas > 50% of local V_bar^2 at Upsilon=0.5",
                 "bulge": "any V_bul > 0", "min_points_per_galaxy": MIN_POINTS},
        "horizon_prediction": {lbl: a0_horizon(h) for lbl, h in H0_VALUES.items()},
        "rar_subsets": {}, "deep_points_all_laws": {}, "tensions_vs_gas_dominated": {},
    }
    for key, sample in subsets.items():
        r = fit_subset(sample, "rar_exponential")
        r["label"] = SUBSET_LABELS[key]
        results["rar_subsets"][key] = r
        print(f"  {SUBSET_LABELS[key]:50s} {r['n_galaxies']:3d} gal {r['n_points']:4d} pts  "
              f"a0 = {r['a0'] * 1e10:.3f} +/- {r['sigma_total'] * 1e10:.3f}  chi2_nu = {r['chi2_reduced']:.2f}"
              f"{'  [GRID EDGE]' if r['at_grid_edge'] else ''}")
    ref = results["rar_subsets"]["gas_dominated"]
    for key, r in results["rar_subsets"].items():
        if key != "gas_dominated":
            results["tensions_vs_gas_dominated"][key] = tension(r, ref)
    rs = results["rar_subsets"]
    results["independent_comparisons"] = {
        "bulge_vs_bulgeless_star_dominated": tension(rs["star_bulge"], rs["star_bulgeless"]),
        "bulge_vs_bulgeless_star_dominated_deep": tension(rs["star_bulge_deep"], rs["star_bulgeless_deep"]),
    }
    print("  Independent comparisons (sigma): " + ", ".join(
        f"{k} = {v:+.1f}" for k, v in results["independent_comparisons"].items()))

    print("\n  Law dependence in subset D (deep points of star-dominated galaxies), Upsilon_0 = 0.5:")
    for law_key in LAWS:
        r = fit_subset(subsets["star_deep_points"], law_key, ups_centres=(UPS_DISK_PRIOR,))
        results["deep_points_all_laws"][law_key] = {"a0": r["a0"], "sigma_stat_scaled": r["sigma_stat_scaled"],
                                                    "chi2_reduced": r["chi2_reduced"]}
        print(f"    {LAWS[law_key][0]:38s} a0 = {r['a0'] * 1e10:.3f} +/- {r['sigma_stat_scaled'] * 1e10:.3f}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "sparc_tension_diagnostics.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print_summary(results)
    print(f"Results written to {out.name}")
    if make_figures:
        make_plot(results)
    return results


def print_summary(results: dict) -> None:
    print("\nSUMMARY (RAR law; total sigma = stat (chi2-rescaled) (+) Upsilon-centre half-range)")
    hz = results["horizon_prediction"]
    print("  cH0/2pi: " + ", ".join(f"{v * 1e10:.3f} ({k})" for k, v in hz.items()))
    for key, r in results["rar_subsets"].items():
        t = results["tensions_vs_gas_dominated"].get(key)
        pulls = " / ".join(f"{p:+.1f}" for p in r["pulls_vs_horizon"].values())
        print(f"  {r['label']:50s} a0 = {r['a0'] * 1e10:.3f} +/- {r['sigma_total'] * 1e10:.3f} | "
              f"pull vs cH0/2pi (67.4/73.0): {pulls} sigma"
              + (f" | vs gas-dominated: {t:+.1f} sigma" if t is not None else ""))
    vals = [v["a0"] for v in results["deep_points_all_laws"].values()]
    print(f"  Deep-point law spread (D): {min(vals) * 1e10:.3f} - {max(vals) * 1e10:.3f} "
          f"(half-range {(max(vals) - min(vals)) / 2 * 1e10:.3f})")
    for k, v in results.get("independent_comparisons", {}).items():
        print(f"  Independent comparison {k}: {v:+.1f} sigma")


def make_plot(results: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    items = list(results["rar_subsets"].items())
    y = np.arange(len(items))[::-1]
    fig, ax = plt.subplots(figsize=(9.5, 0.6 * len(items) + 1.8))
    for yi, (key, r) in zip(y, items):
        col = "tab:green" if key == "gas_dominated" else ("tab:purple" if "deep" in key or "gas_points" in key
                                                          else "tab:blue")
        ax.errorbar(r["a0"] * 1e10, yi, xerr=r["sigma_total"] * 1e10, fmt="o", color=col, capsize=3)
        ax.text(2.25, yi, f"{r['n_galaxies']} gal / {r['n_points']} pts", va="center", fontsize=7)
    for lbl, a in results["horizon_prediction"].items():
        ax.axvline(a * 1e10, ls="--", color="k" if "Planck" in lbl else "gray", lw=1, label=f"cH0/2pi, {lbl}")
    ax.set_yticks(y)
    ax.set_yticklabels([r["label"] for _, r in items], fontsize=7)
    ax.set_xlim(0.6, 2.7)
    ax.set_xlabel(r"global $a_0$ [$10^{-10}$ m s$^{-2}$], RAR law, D + i + $\Upsilon_\star$ marginalized")
    ax.set_title("Gas- vs star-dominated disagreement: subset diagnostics (real SPARC)", fontsize=10)
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / "fig_real_sparc_tension_diagnostics.png", dpi=150)
    plt.close(fig)
    print("Figure written to paper/figures/fig_real_sparc_tension_diagnostics.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()
    if args.plot_only:
        results = json.loads((RESULTS_DIR / "sparc_tension_diagnostics.json").read_text(encoding="utf-8"))
        print_summary(results)
        make_plot(results)
        return 0
    run(make_figures=not args.no_figures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
