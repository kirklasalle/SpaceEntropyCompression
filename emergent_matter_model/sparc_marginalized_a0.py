"""Sharpened real-data test of a0 = c H0 / (2 pi): marginalizing distance and inclination.

Method (following Li, Lelli, McGaugh & Schombert 2018, A&A 615, A3)
------------------------------------------------------------------
Each SPARC galaxy gets three nuisance parameters with Gaussian priors:

* stellar mass-to-light ratio Upsilon_disk:  log-normal, centre Upsilon_0, width 0.1 dex
  (Upsilon_bulge = 1.4 Upsilon_disk);
* distance factor f_D = D'/D:                Gaussian, mean 1, sigma = e_D / D (SPARC table);
* inclination i':                            Gaussian, mean i, sigma = e_i (SPARC table).

Distance scaling: R -> f_D R and V_bar^2 -> f_D V_bar^2, so g_bar = V_bar^2/R is unchanged while
g_obs = V_obs^2/R scales as 1/f_D. Inclination scaling: V_obs and its error scale as sin(i)/sin(i').

For a trial global a0, every galaxy is fitted by minimizing chi^2 + priors over its nuisance
parameters; the sum over galaxies is profiled in a0.

Why gas-dominated galaxies matter
---------------------------------
In the deep regime g = sqrt(a0 g_bar) with g_bar proportional to Upsilon, so a0 and the stellar
mass scale are degenerate. Marginalizing D and i does not remove that degeneracy. Galaxies whose
baryons are mostly gas (gas fraction > 0.5) barely depend on Upsilon, so we report a0 for that
subsample separately, and we vary the Upsilon prior centre (0.4 / 0.5 / 0.6) to measure the
remaining systematic.

Usage
-----
    python emergent_matter_model/sparc_marginalized_a0.py          # all four laws (~5-10 min)
    python emergent_matter_model/sparc_marginalized_a0.py --quick  # RAR law only, coarse grid
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np
from scipy import optimize

try:
    from sparc_real_analysis import (ACC, C, FIGURE_DIR, H0_VALUES, LAWS, LITERATURE_A0, MPC, RESULTS_DIR,
                                     UPS_BULGE_RATIO, UPS_PRIOR_DEX, Galaxy, a0_horizon, load_sparc)
except ImportError:  # imported as a package
    from emergent_matter_model.sparc_real_analysis import (ACC, C, FIGURE_DIR, H0_VALUES, LAWS, LITERATURE_A0,
                                                           MPC, RESULTS_DIR, UPS_BULGE_RATIO, UPS_PRIOR_DEX,
                                                           Galaxy, a0_horizon, load_sparc)

UPS_CENTRES = (0.4, 0.5, 0.6)
GAS_DOMINATED = 0.5
MIN_E_INC = 1.0       # deg; guards against zero catalogue errors
MIN_FRAC_E_D = 0.02


def implied_h0(a0: float) -> float:
    """H0 (km/s/Mpc) implied by a0 = c H0 / (2 pi)."""
    return 2.0 * math.pi * a0 / C * MPC / 1e3


def a0_lambda(h0: float = 67.4, omega_lambda: float = 0.685) -> float:
    """Alternative horizon scale tied to the cosmological constant: c sqrt(Lambda/3) / (2 pi)."""
    return a0_horizon(h0) * math.sqrt(omega_lambda)


class MarginalizedGalaxy:
    """Wraps a Galaxy with the nuisance-parameter likelihood."""

    def __init__(self, gal: Galaxy):
        self.gal = gal
        self.sig_fd = max(gal.e_distance_mpc / gal.distance_mpc, MIN_FRAC_E_D)
        self.sig_i = max(gal.e_inclination_deg, MIN_E_INC)
        self.sin_i0 = math.sin(math.radians(gal.inclination_deg))
        self.vb2_gas = gal.v_gas * np.abs(gal.v_gas)
        self.vb2_star = gal.v_disk * np.abs(gal.v_disk) + UPS_BULGE_RATIO * gal.v_bul * np.abs(gal.v_bul)
        i_lo = max(gal.inclination_deg - 5 * self.sig_i, 10.0)
        i_hi = min(gal.inclination_deg + 5 * self.sig_i, 90.0)
        fd_lo = max(1.0 - 5 * self.sig_fd, 0.3)
        self.bounds = [(-1.3, 0.7), (fd_lo, 1.0 + 5 * self.sig_fd), (i_lo, i_hi)]
        self.x_last: dict = {}

    def chi2(self, x: np.ndarray, nu, a0: float) -> float:
        lu, fd, inc = x
        ups = 10.0**lu
        g_bar = np.maximum(self.vb2_gas + ups * self.vb2_star, 1e-2) / self.gal.r_kpc * ACC
        g_mod = g_bar * nu(g_bar / a0)
        v_pred = np.sqrt(g_mod / ACC * self.gal.r_kpc * fd)
        scale = self.sin_i0 / math.sin(math.radians(inc))
        return float(np.sum(((self.gal.v_obs * scale - v_pred) / (self.gal.v_err * scale)) ** 2))

    def prior(self, x: np.ndarray, ups0: float) -> float:
        lu, fd, inc = x
        return (((lu - math.log10(ups0)) / UPS_PRIOR_DEX) ** 2
                + ((fd - 1.0) / self.sig_fd) ** 2
                + ((inc - self.gal.inclination_deg) / self.sig_i) ** 2)

    def fit(self, nu, a0: float, ups0: float, key: str) -> tuple[float, float, np.ndarray]:
        """Return (chi2 + prior, chi2, best x), warm-started from the previous a0 on the grid."""
        x0 = self.x_last.get(key, np.array([math.log10(ups0), 1.0, self.gal.inclination_deg]))
        res = optimize.minimize(lambda x: self.chi2(x, nu, a0) + self.prior(x, ups0), x0,
                                method="L-BFGS-B", bounds=self.bounds)
        if not res.success or not np.isfinite(res.fun) or not np.isfinite(res.x).all():
            retry_start = res.x if np.isfinite(res.x).all() else x0
            retry = optimize.minimize(
                lambda x: self.chi2(x, nu, a0) + self.prior(x, ups0),
                retry_start,
                method="Powell",
                bounds=self.bounds,
                options={"xtol": 1e-10, "ftol": 1e-10, "maxiter": 2000},
            )
            if (
                not retry.success
                or not np.isfinite(retry.fun)
                or not np.isfinite(retry.x).all()
            ):
                raise RuntimeError(
                    "SPARC nuisance optimizer did not converge: "
                    f"L-BFGS-B={res.message}; Powell={retry.message}"
                )
            res = retry
        self.x_last[key] = res.x
        return float(res.fun), self.chi2(res.x, nu, a0), res.x


def profile(mgals: list[MarginalizedGalaxy], nu, law_key: str, ups0: float, grid: np.ndarray) -> np.ndarray:
    """Return array [n_grid, n_gal, 2] of (objective, chi2) per galaxy per trial a0."""
    out = np.zeros((len(grid), len(mgals), 2))
    for j, a0 in enumerate(grid):
        for k, mg in enumerate(mgals):
            obj, c2, _ = mg.fit(nu, a0, ups0, f"{law_key}:{ups0}")
            out[j, k] = (obj, c2)
    return out


def best_a0(grid: np.ndarray, obj: np.ndarray, chi2_red: float) -> dict:
    """Parabolic refinement around the grid minimum; 1-sigma from delta(objective) = 1."""
    i = int(np.clip(np.argmin(obj), 2, len(grid) - 3))
    x, y = grid[i - 2:i + 3], obj[i - 2:i + 3]
    c2, c1, c0 = np.polyfit(x, y, 2)
    a_best = -c1 / (2 * c2) if c2 > 0 else float(grid[i])
    sigma = math.sqrt(1.0 / c2) if c2 > 0 else float("nan")
    return {"a0": float(a_best), "sigma_stat": sigma, "sigma_scaled": sigma * math.sqrt(max(chi2_red, 1.0)),
            "at_grid_edge": bool(np.argmin(obj) in (0, len(grid) - 1))}


def run(quick: bool = False, make_figures: bool = True) -> dict:
    gals = load_sparc()
    mgals = [MarginalizedGalaxy(g) for g in gals]
    gas_mask = np.array([g.gas_fraction() > GAS_DOMINATED for g in gals])
    grid = np.arange(0.70e-10, 1.80e-10 + 1e-15, 0.04e-10 if quick else 0.03e-10)
    laws = {"rar_exponential": LAWS["rar_exponential"]} if quick else LAWS
    samples = {"all": np.ones(len(gals), bool), "gas_dominated": gas_mask}

    results = {
        "method": "Li et al. (2018)-style: per-galaxy Upsilon (0.1 dex), distance (e_D) and inclination (e_i) "
                  "Gaussian priors; profiled global a0; Upsilon prior centre varied 0.4/0.5/0.6",
        "n_galaxies": len(gals), "n_points": int(sum(g.n for g in gals)),
        "gas_dominated_definition": f"1.33 M_HI / (1.33 M_HI + 0.5 L[3.6]) > {GAS_DOMINATED}",
        "n_gas_dominated": int(gas_mask.sum()),
        "n_points_gas_dominated": int(sum(g.n for g, m in zip(gals, gas_mask) if m)),
        "horizon_prediction": {lbl: a0_horizon(h) for lbl, h in H0_VALUES.items()},
        "lambda_variant_prediction": {"c sqrt(Lambda/3)/(2 pi), H0=67.4, Omega_L=0.685": a0_lambda()},
        "literature_a0": {"value": LITERATURE_A0[0], "random": LITERATURE_A0[1], "systematic": LITERATURE_A0[2]},
        "a0_grid": grid.tolist(),
        "laws": {},
    }
    print(f"{len(gals)} galaxies ({results['n_points']} points); gas-dominated: "
          f"{results['n_gas_dominated']} ({results['n_points_gas_dominated']} points)")

    for key, (label, nu) in laws.items():
        law_out = {"label": label, "by_upsilon_centre": {}}
        for ups0 in UPS_CENTRES:
            prof = profile(mgals, nu, key, ups0, grid)
            entry = {}
            for sname, mask in samples.items():
                obj = prof[:, mask, 0].sum(axis=1)
                j = int(np.argmin(obj))
                chi_min = float(prof[j, mask, 1].sum())
                n_pts = int(sum(g.n for g, m in zip(gals, mask) if m))
                k = 3 * int(mask.sum()) + 1
                chi2_red = chi_min / max(n_pts - k, 1)
                b = best_a0(grid, obj, chi2_red)
                b.update({"chi2": chi_min, "chi2_reduced": chi2_red, "n_points": n_pts,
                          "implied_H0_kms_mpc": implied_h0(b["a0"]),
                          "objective_profile": [float(v) for v in obj]})
                entry[sname] = b
            law_out["by_upsilon_centre"][str(ups0)] = entry
            print(f"  {label:38s} Ups0={ups0:.1f}  all: a0 = {entry['all']['a0'] * 1e10:.3f} "
                  f"+/- {entry['all']['sigma_scaled'] * 1e10:.3f} (chi2_nu {entry['all']['chi2_reduced']:.2f})   "
                  f"gas-dom: a0 = {entry['gas_dominated']['a0'] * 1e10:.3f} "
                  f"+/- {entry['gas_dominated']['sigma_scaled'] * 1e10:.3f} (chi2_nu {entry['gas_dominated']['chi2_reduced']:.2f})")
        for sname in samples:
            vals = [law_out["by_upsilon_centre"][str(u)][sname]["a0"] for u in UPS_CENTRES]
            base = law_out["by_upsilon_centre"]["0.5"][sname]
            sys_half = (max(vals) - min(vals)) / 2.0
            total = math.hypot(base["sigma_scaled"], sys_half)
            law_out[f"summary_{sname}"] = {
                "a0_baseline": base["a0"], "sigma_stat_scaled": base["sigma_scaled"],
                "sigma_upsilon_systematic": sys_half, "sigma_total": total,
                "pulls_vs_horizon": {lbl: (base["a0"] - a) / total for lbl, a in results["horizon_prediction"].items()},
                "pull_vs_lambda_variant": (base["a0"] - a0_lambda()) / total,
                "implied_H0_kms_mpc": implied_h0(base["a0"]),
                "implied_H0_range": [implied_h0(base["a0"] - total), implied_h0(base["a0"] + total)],
            }
        results["laws"][key] = law_out

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / ("sparc_marginalized_a0_quick.json" if quick else "sparc_marginalized_a0.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print_summary(results)
    print(f"Results written to {out.name}")
    if make_figures and not quick:
        make_plot(results)
    return results


def print_summary(results: dict) -> None:
    print("\nSUMMARY (baseline Upsilon_0 = 0.5; total sigma = stat (chi2-rescaled) (+) half-range over Upsilon_0)")
    hz = results["horizon_prediction"]
    lam = list(results["lambda_variant_prediction"].values())[0]
    print(f"  Predictions: cH0/2pi = {', '.join(f'{v * 1e10:.3f} ({k})' for k, v in hz.items())}; "
          f"c sqrt(Lambda/3)/2pi = {lam * 1e10:.3f}")
    for key, law in results["laws"].items():
        for sname in ("all", "gas_dominated"):
            s = law[f"summary_{sname}"]
            pulls = ", ".join(f"{p:+.1f} sigma vs {k.split()[0]}" for k, p in s["pulls_vs_horizon"].items())
            print(f"  {law['label'][:30]:30s} {sname:13s} a0 = {s['a0_baseline'] * 1e10:.3f} +/- "
                  f"{s['sigma_total'] * 1e10:.3f} (stat {s['sigma_stat_scaled'] * 1e10:.3f}, Ups sys "
                  f"{s['sigma_upsilon_systematic'] * 1e10:.3f}) | {pulls}; {s['pull_vs_lambda_variant']:+.1f} sigma vs "
                  f"Lambda-variant | implied H0 = {s['implied_H0_kms_mpc']:.1f} "
                  f"[{s['implied_H0_range'][0]:.1f}, {s['implied_H0_range'][1]:.1f}]")


SHORT_LABELS = {"emrf_sqrt": "EMRF sqrt law", "rar_exponential": "RAR (McGaugh)",
                "simple": "MOND simple", "standard": "MOND standard"}


def make_plot(results: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels, vals, errs, colors = [], [], [], []
    for key, law in results["laws"].items():
        for sname, col in (("all", "tab:blue"), ("gas_dominated", "tab:green")):
            s = law[f"summary_{sname}"]
            labels.append(f"{SHORT_LABELS.get(key, key)}\n{'all galaxies' if sname == 'all' else 'gas-dominated'}")
            vals.append(s["a0_baseline"] * 1e10)
            errs.append(s["sigma_total"] * 1e10)
            colors.append(col)
    y = np.arange(len(vals))[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.55 * len(vals) + 1.6))
    for yi, v, e, c in zip(y, vals, errs, colors):
        ax.errorbar(v, yi, xerr=e, fmt="o", color=c, capsize=3)
    for lbl, a in results["horizon_prediction"].items():
        ax.axvline(a * 1e10, ls="--", color="k" if "Planck" in lbl else "gray", lw=1, label=f"cH0/2pi, {lbl}")
    lam = list(results["lambda_variant_prediction"].values())[0]
    ax.axvline(lam * 1e10, ls=":", color="tab:red", lw=1.2, label=r"$c\sqrt{\Lambda/3}/2\pi$ (Planck)")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel(r"global $a_0$ [$10^{-10}$ m s$^{-2}$]  (total 1$\sigma$: stat $\oplus$ $\Upsilon_\star$ systematic)")
    ax.set_title("Real SPARC, distance + inclination marginalized: all (blue) vs gas-dominated (green)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / "fig_real_sparc_a0_marginalized.png", dpi=150)
    plt.close(fig)
    print("Figure written to paper/figures/fig_real_sparc_a0_marginalized.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="RAR law only, coarse grid, no figure")
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--plot-only", action="store_true", help="redraw the figure from results/sparc_marginalized_a0.json")
    args = ap.parse_args()
    if args.plot_only:
        results = json.loads((RESULTS_DIR / "sparc_marginalized_a0.json").read_text(encoding="utf-8"))
        print_summary(results)
        make_plot(results)
        return 0
    run(quick=args.quick, make_figures=not args.no_figures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
