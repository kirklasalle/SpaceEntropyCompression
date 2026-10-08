"""Bulge mass-to-light test: mis-modelled bulges, or a non-universal a0?

Background
----------
sparc_tension_diagnostics.py found that star-dominated galaxies WITH bulges prefer
a0 = 1.91 +/- 0.18 (x1e-10 m/s^2), while bulgeless galaxies prefer ~0.9. In the deep regime
a0 and the baryonic mass are degenerate (g ~ sqrt(a0 g_bar)), so under-estimated bulge masses
would mimic a larger a0. This module asks how heavy the bulges would have to be for the bulge
galaxies to agree with the bulgeless ones, and whether that is physically plausible.

Pre-registered design (fixed before running)
--------------------------------------------
Sample: the 31 star-dominated SPARC galaxies with a bulge (subset H of the diagnostics).
Distance, inclination and Upsilon_disk are marginalized exactly as before (Li et al. 2018 priors).

Test 1 - global bulge scaling: Upsilon_bulge = r * Upsilon_disk with r in RATIOS (standard r = 1.4).
         Profile a0 for each r (all points, and deep points). Report r* where the bulge-galaxy a0
         equals the bulgeless reference A0_TARGETS (linear interpolation in r).
Test 2 - per-galaxy bulge M/L: at fixed a0 in A0_TARGETS, fit each galaxy with Upsilon_bulge free
         (log-uniform in [0.05, 20], no prior), D, i, Upsilon_disk marginalized as usual.
         Report the median and spread of the required Upsilon_bulge.

Plausibility (3.6 micron stellar-population expectation for bulges ~0.7; e.g. Schombert & McGaugh 2014,
Lelli et al. 2016 adopt 0.7):  Upsilon_bulge <= 1.0 plausible | 1.0-1.4 stretched | > 1.4 implausible
(i.e. more than twice the expected bulge mass).

Post hoc additions (after the first run showed that HEAVIER bulges RAISE the fitted a0, because the
bulge is pinned by the inner rotation curve and a heavier bulge forces a lighter disk):
- lighter-bulge ratios r = 0.25, 0.5, 0.75 in Test 1;
- symmetric lower plausibility bounds: 0.5-1.0 plausible, 0.35-0.5 stretched, < 0.35 implausible;
- Test 3: profile a0 with every galaxy's Upsilon_bulge free, to see whether the bulge galaxies then
  agree with the bulgeless value.

Usage
-----
    python emergent_matter_model/sparc_bulge_test.py
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np
from scipy import optimize

try:
    from sparc_marginalized_a0 import MarginalizedGalaxy, best_a0
    from sparc_real_analysis import (ACC, FIGURE_DIR, H0_VALUES, RESULTS_DIR, UPS_DISK_PRIOR, UPS_PRIOR_DEX,
                                     a0_horizon, load_sparc, nu_rar_exponential)
    from sparc_tension_diagnostics import build_subsets
except ImportError:  # imported as a package
    from emergent_matter_model.sparc_marginalized_a0 import MarginalizedGalaxy, best_a0
    from emergent_matter_model.sparc_real_analysis import (ACC, FIGURE_DIR, H0_VALUES, RESULTS_DIR,
                                                           UPS_DISK_PRIOR, UPS_PRIOR_DEX, a0_horizon, load_sparc,
                                                           nu_rar_exponential)
    from emergent_matter_model.sparc_tension_diagnostics import build_subsets

RATIOS = (1.0, 1.4, 2.0, 3.0, 4.0, 6.0)
# Added after the first run showed that heavier bulges RAISE the fitted a0 (post hoc):
POST_HOC_RATIOS = (0.25, 0.5, 0.75)
STANDARD_RATIO = 1.4
A0_TARGETS = {"bulgeless combined (0.930)": 0.930e-10, "cH0/2pi Planck (1.042)": a0_horizon(67.4)}
EXPECTED_UPS_BULGE = 0.7
PLAUSIBLE_MAX = 1.0
STRETCHED_MAX = 1.4
# Post hoc lower bounds, symmetric in log around 0.7 with the pre-registered upper bounds.
PLAUSIBLE_MIN = 0.5
STRETCHED_MIN = 0.35
GRID = np.arange(0.40e-10, 3.00e-10 + 1e-15, 0.04e-10)


class ScaledBulgeGalaxy(MarginalizedGalaxy):
    """Upsilon_bulge = ratio * Upsilon_disk."""

    def __init__(self, gal, ratio: float):
        super().__init__(gal)
        self.vb2_star = gal.v_disk * np.abs(gal.v_disk) + ratio * gal.v_bul * np.abs(gal.v_bul)


class FreeBulgeGalaxy(MarginalizedGalaxy):
    """Upsilon_bulge free (no prior); x = [log Ups_disk, f_D, i, log Ups_bulge]."""

    def __init__(self, gal):
        super().__init__(gal)
        self.vb2_disk = gal.v_disk * np.abs(gal.v_disk)
        self.vb2_bul = gal.v_bul * np.abs(gal.v_bul)
        self.bounds = self.bounds + [(math.log10(0.05), math.log10(20.0))]

    def chi2(self, x, nu, a0):
        lu, fd, inc, lb = x
        g_bar = np.maximum(self.vb2_gas + 10**lu * self.vb2_disk + 10**lb * self.vb2_bul, 1e-2) / self.gal.r_kpc * ACC
        v_pred = np.sqrt(g_bar * nu(g_bar / a0) / ACC * self.gal.r_kpc * fd)
        scale = self.sin_i0 / math.sin(math.radians(inc))
        return float(np.sum(((self.gal.v_obs * scale - v_pred) / (self.gal.v_err * scale)) ** 2))

    def prior(self, x, ups0):
        return super().prior(x[:3], ups0)

    def fit_free(self, nu, a0: float) -> dict:
        best = None
        for lb0 in (math.log10(0.3), math.log10(EXPECTED_UPS_BULGE), math.log10(2.0), math.log10(5.0)):
            x0 = np.array([math.log10(UPS_DISK_PRIOR), 1.0, self.gal.inclination_deg, lb0])
            r = optimize.minimize(lambda x: self.chi2(x, nu, a0) + self.prior(x, UPS_DISK_PRIOR), x0,
                                  method="L-BFGS-B", bounds=self.bounds)
            best = r if best is None or r.fun < best.fun else best
        lu, fd, inc, lb = best.x
        return {"galaxy": self.gal.name, "ups_bulge": float(10**lb), "ups_disk": float(10**lu),
                "f_D": float(fd), "inc": float(inc), "chi2": self.chi2(best.x, nu, a0),
                "at_bound": bool(abs(lb - self.bounds[3][0]) < 1e-3 or abs(lb - self.bounds[3][1]) < 1e-3)}


def classify(ups: float) -> str:
    if PLAUSIBLE_MIN <= ups <= PLAUSIBLE_MAX:
        return "plausible"
    if STRETCHED_MIN <= ups <= STRETCHED_MAX:
        return "stretched"
    return "implausible"


def profile_free_bulge(sample) -> dict:
    """Post hoc decisive check: profile a0 with every galaxy's Upsilon_bulge free (warm-started)."""
    mgals = [FreeBulgeGalaxy(g) for g in sample]
    starts = [None] * len(mgals)
    obj = np.zeros(len(GRID))
    for j, a0 in enumerate(GRID):
        for k, mg in enumerate(mgals):
            if starts[k] is None:
                f = mg.fit_free(nu_rar_exponential, a0)
                starts[k] = np.array([math.log10(f["ups_disk"]), f["f_D"], f["inc"], math.log10(f["ups_bulge"])])
            res = optimize.minimize(lambda x: mg.chi2(x, nu_rar_exponential, a0) + mg.prior(x, UPS_DISK_PRIOR),
                                    starts[k], method="L-BFGS-B", bounds=mg.bounds)
            starts[k] = res.x
            obj[j] += res.fun
    n_pts = sum(g.n for g in sample)
    chi2_red = float(obj.min()) / max(n_pts - (4 * len(sample) + 1), 1)
    b = best_a0(GRID, obj, chi2_red)
    b["chi2_reduced_approx"] = chi2_red
    b["delta_objective_at_targets"] = {
        lbl: float(np.interp(t, GRID, obj) - obj.min()) / max(chi2_red, 1.0) for lbl, t in A0_TARGETS.items()}
    b["objective_profile"] = obj.tolist()
    return b


def profile_scaled(sample, ratio: float) -> dict:
    mgals = [ScaledBulgeGalaxy(g, ratio) for g in sample]
    obj = np.zeros(len(GRID))
    chi = np.zeros(len(GRID))
    for j, a0 in enumerate(GRID):
        for mg in mgals:
            o, c, _ = mg.fit(nu_rar_exponential, a0, UPS_DISK_PRIOR, "rar")
            obj[j] += o
            chi[j] += c
    n_pts = sum(g.n for g in sample)
    j = int(np.argmin(obj))
    chi2_red = chi[j] / max(n_pts - (3 * len(sample) + 1), 1)
    b = best_a0(GRID, obj, chi2_red)
    b.update({"ratio": ratio, "ups_bulge_nominal": ratio * UPS_DISK_PRIOR, "chi2": float(chi[j]),
              "chi2_reduced": chi2_red})
    return b


def required_ratio(scan: list[dict], target: float) -> float | None:
    """Linear interpolation of the ratio at which the fitted a0 crosses the target."""
    for lo, hi in zip(scan, scan[1:]):
        if (lo["a0"] - target) * (hi["a0"] - target) <= 0 and lo["a0"] != hi["a0"]:
            return lo["ratio"] + (target - lo["a0"]) * (hi["ratio"] - lo["ratio"]) / (hi["a0"] - lo["a0"])
    return None


def run(make_figures: bool = True) -> dict:
    subsets = build_subsets(load_sparc())
    samples = {"all_points": subsets["star_bulge"], "deep_points": subsets["star_bulge_deep"]}
    results = {
        "design": __doc__.split("Pre-registered design (fixed before running)")[1].split("Usage")[0].strip(),
        "n_galaxies": {k: len(v) for k, v in samples.items()},
        "n_points": {k: int(sum(g.n for g in v)) for k, v in samples.items()},
        "a0_targets": A0_TARGETS, "test1_scan": {}, "test1_required": {}, "test2_per_galaxy": {},
    }
    for sname, sample in samples.items():
        scan = []
        for r in sorted(RATIOS + POST_HOC_RATIOS):
            b = profile_scaled(sample, r)
            scan.append(b)
            print(f"  Test 1 [{sname:11s}] Ups_bulge = {r:.1f} x Ups_disk (nominal {b['ups_bulge_nominal']:.2f}): "
                  f"a0 = {b['a0'] * 1e10:.3f} +/- {b['sigma_scaled'] * 1e10:.3f}  chi2_nu = {b['chi2_reduced']:.2f}"
                  f"{'  [GRID EDGE]' if b['at_grid_edge'] else ''}")
        results["test1_scan"][sname] = scan
        req = {}
        for lbl, tgt in A0_TARGETS.items():
            r_req = required_ratio(scan, tgt)
            ups = None if r_req is None else r_req * UPS_DISK_PRIOR
            req[lbl] = {"ratio": r_req, "ups_bulge": ups,
                        "verdict": "not reached within scanned ratios" if ups is None else classify(ups)}
            print(f"    -> to reach a0 = {tgt * 1e10:.3f} ({lbl}): "
                  + ("not reached" if ups is None else f"r = {r_req:.2f}, Ups_bulge = {ups:.2f} [{classify(ups)}]"))
        results["test1_required"][sname] = req

    for lbl, tgt in A0_TARGETS.items():
        fits = [FreeBulgeGalaxy(g).fit_free(nu_rar_exponential, tgt) for g in samples["all_points"]]
        ups = np.array([f["ups_bulge"] for f in fits])
        counts = {c: int(sum(classify(u) == c for u in ups)) for c in ("plausible", "stretched", "implausible")}
        results["test2_per_galaxy"][lbl] = {
            "a0": tgt, "median_ups_bulge": float(np.median(ups)),
            "percentile_16_84": [float(np.percentile(ups, 16)), float(np.percentile(ups, 84))],
            "counts": counts, "n_at_bound": int(sum(f["at_bound"] for f in fits)), "fits": fits,
        }
        print(f"  Test 2 [a0 = {tgt * 1e10:.3f}, {lbl}] required Ups_bulge: median {np.median(ups):.2f} "
              f"(16-84%: {np.percentile(ups, 16):.2f}-{np.percentile(ups, 84):.2f}); {counts}; "
              f"{results['test2_per_galaxy'][lbl]['n_at_bound']} at search bound")

    fb = profile_free_bulge(samples["all_points"])
    results["test3_free_bulge_profile_post_hoc"] = fb
    print(f"  Test 3 (post hoc) a0 with every Ups_bulge free: a0 = {fb['a0'] * 1e10:.3f} +/- "
          f"{fb['sigma_scaled'] * 1e10:.3f} (chi2_nu ~ {fb['chi2_reduced_approx']:.2f})"
          f"{'  [GRID EDGE]' if fb['at_grid_edge'] else ''}; rescaled delta-chi2 at targets: "
          + ", ".join(f"{k}: {v:.1f}" for k, v in fb["delta_objective_at_targets"].items()))

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "sparc_bulge_test.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {out.name}")
    if make_figures:
        make_plot(results)
    return results


def make_plot(results: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    for sname, col in (("all_points", "tab:blue"), ("deep_points", "tab:purple")):
        scan = results["test1_scan"][sname]
        x = [s["ups_bulge_nominal"] for s in scan]
        ax1.errorbar(x, [s["a0"] * 1e10 for s in scan], yerr=[s["sigma_scaled"] * 1e10 for s in scan],
                     fmt="o-", color=col, capsize=3, label=f"bulge galaxies, {sname.replace('_', ' ')}")
    for lbl, tgt in results["a0_targets"].items():
        ax1.axhline(tgt * 1e10, ls="--", color="k" if "Planck" in lbl else "tab:green", lw=1, label=lbl)
    for lo, hi, c in ((PLAUSIBLE_MIN, PLAUSIBLE_MAX, "tab:green"), (PLAUSIBLE_MAX, STRETCHED_MAX, "gold"),
                      (STRETCHED_MIN, PLAUSIBLE_MIN, "gold"), (STRETCHED_MAX, 3.2, "tab:red"),
                      (0.0, STRETCHED_MIN, "tab:red")):
        ax1.axvspan(lo, hi, color=c, alpha=0.08)
    ax1.set_xlabel(r"assumed $\Upsilon_{\rm bulge}$ at 3.6 $\mu$m (= ratio $\times$ 0.5)")
    ax1.set_ylabel(r"fitted $a_0$ [$10^{-10}$ m s$^{-2}$]")
    ax1.set_title("Test 1: fitted $a_0$ vs assumed bulge M/L (edge values are lower limits)", fontsize=9)
    ax1.set_xlim(0.0, 3.2)
    ax1.set_ylim(0.3, 3.2)
    ax1.legend(fontsize=7)

    labels = list(results["test2_per_galaxy"])
    data = [[f["ups_bulge"] for f in results["test2_per_galaxy"][lbl]["fits"]] for lbl in labels]
    ax2.boxplot(data, tick_labels=[lbl.split(" (")[0] for lbl in labels], showfliers=True)
    for i, d in enumerate(data, start=1):
        ax2.plot(np.full(len(d), i) + np.random.default_rng(0).uniform(-0.12, 0.12, len(d)), d, ".", alpha=0.5)
    ax2.set_yscale("log")
    for lo, hi, c in ((PLAUSIBLE_MIN, PLAUSIBLE_MAX, "tab:green"), (PLAUSIBLE_MAX, STRETCHED_MAX, "gold"),
                      (STRETCHED_MIN, PLAUSIBLE_MIN, "gold"), (STRETCHED_MAX, 25, "tab:red"),
                      (0.04, STRETCHED_MIN, "tab:red")):
        ax2.axhspan(lo, hi, color=c, alpha=0.08)
    ax2.axhline(EXPECTED_UPS_BULGE, color="k", lw=0.8, ls=":")
    ax2.set_ylabel(r"required $\Upsilon_{\rm bulge}$ per galaxy (free)")
    ax2.set_title("Test 2: per-galaxy bulge M/L at fixed $a_0$", fontsize=10)
    fig.tight_layout()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / "fig_real_sparc_bulge_test.png", dpi=150)
    plt.close(fig)
    print("Figure written to paper/figures/fig_real_sparc_bulge_test.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-figures", action="store_true")
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()
    if args.plot_only:
        make_plot(json.loads((RESULTS_DIR / "sparc_bulge_test.json").read_text(encoding="utf-8")))
        return 0
    run(make_figures=not args.no_figures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
