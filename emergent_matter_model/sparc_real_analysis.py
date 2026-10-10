"""Real-data test of the EMRF weak-field hypothesis against the SPARC database.

What is tested
--------------
EMRF's falsifiable weak-field content is the claim that galaxies follow a single
acceleration law g = g_N * nu(g_N / a0) with a universal scale

    a0 = c H0 / (2 pi)          (the "horizon" hypothesis; 1.04e-10 m/s^2 for H0 = 67.4)

and, in the paper, the specific law nu(y) = sqrt(1 + 1/y), i.e. g = sqrt(g_N^2 + a0 g_N).

This module, using only the official SPARC files (Lelli, McGaugh & Schombert 2016):

1. fits a single global a0 for several candidate laws (each galaxy keeps one nuisance
   parameter, its stellar mass-to-light ratio, with the standard log-normal prior
   0.5 +/- 0.1 dex used by Li et al. 2018);
2. compares the fitted a0 with c H0 / (2 pi) for Planck and SH0ES values of H0;
3. compares the laws with Newtonian baryons and with a pseudo-isothermal dark halo
   using chi^2 and BIC;
4. checks each law against the Solar System (no External Field Effect included).

All inputs are downloaded by fetch_real_data.py. Nothing here reads data/synthetic.

Usage
-----
    python emergent_matter_model/sparc_real_analysis.py            # full run, writes results + figures
    python emergent_matter_model/sparc_real_analysis.py --quick    # coarser a0 grid, no halo fits
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import optimize

try:
    from fetch_real_data import REPO_ROOT, fetch_sparc
except ImportError:  # imported as a package
    from emergent_matter_model.fetch_real_data import REPO_ROOT, fetch_sparc

# --- Constants ---------------------------------------------------------------
G = 6.67430e-11
C = 2.99792458e8
MSUN = 1.98847e30
AU = 1.495978707e11
KPC = 3.085677581e19
MPC = 3.085677581e22
ACC = 1.0e6 / KPC                     # (km/s)^2 / kpc  ->  m/s^2
UPS_DISK_PRIOR = 0.5                  # 3.6 micron stellar M/L, Li et al. (2018)
UPS_BULGE_RATIO = 1.4                 # Upsilon_bulge = 0.7 when Upsilon_disk = 0.5
UPS_PRIOR_DEX = 0.1
H0_VALUES = {"Planck 2018 (67.4)": 67.4, "SH0ES (73.0)": 73.0}
LITERATURE_A0 = (1.20e-10, 0.02e-10, 0.24e-10)   # McGaugh+2016: value, random, systematic

RESULTS_DIR = REPO_ROOT / "results"
FIGURE_DIR = REPO_ROOT / "paper" / "figures"
_CHECKPOINT_NAME = "analysis-progress"


def _active_run_checkpoint():
    run_id = os.environ.get("EMRF_RUN_ID")
    run_dir = os.environ.get("EMRF_RUN_DIR")
    if not run_id or not run_dir:
        return None
    from emrf_run_access import run_store

    return run_store(Path(run_dir).parent), run_id


def _save_analysis_checkpoint(results: dict, quick: bool) -> None:
    context = _active_run_checkpoint()
    if context is not None:
        store, run_id = context
        store.save_checkpoint(
            run_id,
            _CHECKPOINT_NAME,
            {"quick": quick, "results": results},
        )


def _load_analysis_checkpoint(quick: bool) -> dict | None:
    context = _active_run_checkpoint()
    if context is None:
        return None
    store, run_id = context
    if not store.checkpoint_exists(run_id, _CHECKPOINT_NAME):
        return None
    checkpoint = store.load_checkpoint(run_id, _CHECKPOINT_NAME)
    if checkpoint.get("quick") is not quick or not isinstance(checkpoint.get("results"), dict):
        raise ValueError("SPARC analysis checkpoint does not match this run configuration")
    return checkpoint["results"]


def _write_results_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(
            prefix=f".{path.name}-",
            suffix=".part",
            dir=path.parent,
        )
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(json.dumps(value, indent=2))
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def a0_horizon(h0_kms_mpc: float) -> float:
    """Horizon hypothesis a0 = c H0 / (2 pi) in m/s^2."""
    return C * h0_kms_mpc * 1e3 / MPC / (2.0 * math.pi)


# --- Candidate acceleration laws: g = g_N * nu(y), y = g_N / a0 --------------
def nu_newton(y: np.ndarray) -> np.ndarray:
    return np.ones_like(y)


def nu_emrf_sqrt(y: np.ndarray) -> np.ndarray:
    """EMRF paper law g = sqrt(g_N^2 + a0 g_N)."""
    return np.sqrt(1.0 + 1.0 / y)


def nu_rar_exponential(y: np.ndarray) -> np.ndarray:
    """McGaugh et al. (2016) RAR function."""
    return 1.0 / -np.expm1(-np.sqrt(y))


def nu_simple(y: np.ndarray) -> np.ndarray:
    return 0.5 + np.sqrt(0.25 + 1.0 / y)


def nu_standard(y: np.ndarray) -> np.ndarray:
    return np.sqrt(0.5 + 0.5 * np.sqrt(1.0 + 4.0 / y**2))


LAWS = {
    "emrf_sqrt": ("EMRF paper law sqrt(g_N^2 + a0 g_N)", nu_emrf_sqrt),
    "rar_exponential": ("McGaugh RAR 1/(1 - exp(-sqrt y))", nu_rar_exponential),
    "simple": ("MOND 'simple' nu", nu_simple),
    "standard": ("MOND 'standard' nu", nu_standard),
}


# --- Data loading ------------------------------------------------------------
@dataclass
class Galaxy:
    name: str
    distance_mpc: float
    inclination_deg: float
    quality: int
    r_kpc: np.ndarray
    v_obs: np.ndarray
    v_err: np.ndarray
    v_gas: np.ndarray
    v_disk: np.ndarray
    v_bul: np.ndarray
    e_distance_mpc: float = 0.0
    e_inclination_deg: float = 0.0
    luminosity_36: float = 0.0        # 10^9 Lsun at 3.6 micron
    m_hi: float = 0.0                 # 10^9 Msun

    @property
    def n(self) -> int:
        return len(self.r_kpc)

    def gas_fraction(self, ups_disk: float = UPS_DISK_PRIOR) -> float:
        """Baryonic gas fraction 1.33 M_HI / (1.33 M_HI + Upsilon L[3.6]) from the SPARC table."""
        m_gas = 1.33 * self.m_hi
        m_star = ups_disk * self.luminosity_36
        return m_gas / (m_gas + m_star) if (m_gas + m_star) > 0 else 0.0


def parse_sparc_table(text: str) -> dict[str, dict]:
    """Parse SPARC_Lelli2016c.mrt.

    The distributed file does not follow the byte offsets in its own header, so rows are parsed
    as whitespace-separated tokens: Galaxy T D e_D f_D Inc e_Inc L e_L Reff SBeff Rdisk SBdisk
    MHI RHI Vflat e_Vflat Q Ref.
    """
    out = {}
    for line in text.splitlines():
        tok = line.split()
        if len(tok) < 18:
            continue
        try:
            row = {
                "T": int(tok[1]), "D": float(tok[2]), "e_D": float(tok[3]), "f_D": int(tok[4]),
                "Inc": float(tok[5]), "e_Inc": float(tok[6]), "L36": float(tok[7]), "MHI": float(tok[13]),
                "Vflat": float(tok[15]), "Q": int(tok[17]),
            }
        except ValueError:
            continue
        out[tok[0]] = row
    return out


def parse_rotmod(text: str) -> np.ndarray:
    """Parse a SPARC *_rotmod.dat file into columns Rad, Vobs, errV, Vgas, Vdisk, Vbul."""
    rows = [list(map(float, ln.split()[:6])) for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]
    return np.array(rows, dtype=float).reshape(-1, 6)


def load_sparc(sparc_path: Path | None = None, max_quality: int = 2, min_inclination: float = 30.0) -> list[Galaxy]:
    """Load real SPARC galaxies with the standard quality cuts (Q <= 2, i >= 30 deg)."""
    base = Path(sparc_path) if sparc_path else fetch_sparc()
    table = parse_sparc_table((base / "SPARC_Lelli2016c.mrt").read_text(encoding="utf-8"))
    galaxies = []
    for f in sorted((base / "Rotmod_LTG").glob("*_rotmod.dat")):
        name = f.name.replace("_rotmod.dat", "")
        meta = table.get(name)
        if meta is None or meta["Q"] > max_quality or meta["Inc"] < min_inclination:
            continue
        a = parse_rotmod(f.read_text(encoding="utf-8"))
        a = a[(a[:, 0] > 0) & (a[:, 1] > 0)]
        if len(a) < 3:
            continue
        galaxies.append(Galaxy(name, meta["D"], meta["Inc"], meta["Q"], a[:, 0], a[:, 1],
                               np.maximum(a[:, 2], 1.0), a[:, 3], a[:, 4], a[:, 5],
                               meta["e_D"], meta["e_Inc"], meta.get("L36", 0.0), meta.get("MHI", 0.0)))
    return galaxies


# --- Model -------------------------------------------------------------------
def g_newton(gal: Galaxy, ups: float) -> np.ndarray:
    vb2 = (gal.v_gas * np.abs(gal.v_gas) + ups * gal.v_disk * np.abs(gal.v_disk)
           + UPS_BULGE_RATIO * ups * gal.v_bul * np.abs(gal.v_bul))
    return np.maximum(vb2, 1e-2) / gal.r_kpc * ACC


def v_model(gal: Galaxy, nu, a0: float, ups: float) -> np.ndarray:
    gn = g_newton(gal, ups)
    g = gn * nu(gn / a0)
    return np.sqrt(g / ACC * gal.r_kpc)


def ups_prior_penalty(ups: float) -> float:
    return ((math.log10(ups) - math.log10(UPS_DISK_PRIOR)) / UPS_PRIOR_DEX) ** 2


def fit_galaxy(gal: Galaxy, nu, a0: float, ups_mode: str = "prior") -> tuple[float, float, float]:
    """Return (chi2_data, prior_penalty, best_upsilon) for one galaxy at fixed a0."""
    def chi2(u):
        return float(np.sum(((gal.v_obs - v_model(gal, nu, a0, u)) / gal.v_err) ** 2))

    if ups_mode == "fixed":
        return chi2(UPS_DISK_PRIOR), 0.0, UPS_DISK_PRIOR
    use_prior = ups_mode == "prior"
    res = optimize.minimize_scalar(lambda lu: chi2(10**lu) + (ups_prior_penalty(10**lu) if use_prior else 0.0),
                                   bounds=(-1.3, 0.7), method="bounded", options={"xatol": 1e-4})
    u = 10 ** res.x
    return chi2(u), (ups_prior_penalty(u) if use_prior else 0.0), u


def total_objective(gals: list[Galaxy], nu, a0: float, ups_mode: str) -> tuple[float, float]:
    """Return (sum chi2_data + prior, sum chi2_data) over the sample."""
    obj = chi = 0.0
    for gal in gals:
        c2, pen, _ = fit_galaxy(gal, nu, a0, ups_mode)
        obj += c2 + pen
        chi += c2
    return obj, chi


def profile_a0(gals: list[Galaxy], nu, a0_grid: np.ndarray, ups_mode: str = "prior") -> dict:
    """Profile the objective over a global a0 and locate its minimum and 1-sigma interval."""
    objs = np.array([total_objective(gals, nu, a, ups_mode)[0] for a in a0_grid])
    i = int(np.argmin(objs))
    lo, hi = a0_grid[max(i - 1, 0)], a0_grid[min(i + 1, len(a0_grid) - 1)]
    res = optimize.minimize_scalar(lambda a: total_objective(gals, nu, a, ups_mode)[0],
                                   bounds=(lo, hi), method="bounded", options={"xatol": 1e-14})
    a_best = float(res.x)
    obj_best, chi_best = total_objective(gals, nu, a_best, ups_mode)
    n_pts = sum(g.n for g in gals)
    k = len(gals) * (0 if ups_mode == "fixed" else 1) + 1
    chi2_red = chi_best / max(n_pts - k, 1)

    def delta(a):
        return total_objective(gals, nu, a, ups_mode)[0] - obj_best

    # Statistical 1-sigma half-width from the curvature of the profile (delta = 1).
    h = 0.01 * a_best
    curv = (delta(a_best + h) + delta(a_best - h)) / h**2
    sigma_stat = math.sqrt(2.0 / curv) if curv > 0 else float("nan")
    return {
        "a0_grid": a0_grid.tolist(), "objective_grid": objs.tolist(),
        "a0_best": a_best, "objective_best": obj_best, "chi2_best": chi_best,
        "n_points": n_pts, "n_params": k, "chi2_reduced": chi2_red,
        "sigma_stat": sigma_stat, "sigma_scaled": sigma_stat * math.sqrt(max(chi2_red, 1.0)),
        "delta_objective_at_horizon": {lbl: delta(a0_horizon(h0)) for lbl, h0 in H0_VALUES.items()},
    }


def fit_isothermal_halo(gal: Galaxy) -> tuple[float, int]:
    """Baryons + pseudo-isothermal halo (rho0, rc) with the same Upsilon prior; returns (chi2, n_params)."""
    def model(p):
        ups, lrho, lrc = 10 ** p[0], p[1], p[2]
        rho0, rc = 10**lrho, 10**lrc            # Msun/pc^3, kpc
        m = 4 * math.pi * rho0 * (rc * 1e3) ** 3 * (gal.r_kpc / rc - np.arctan(gal.r_kpc / rc))
        g = g_newton(gal, ups) + G * m * MSUN / (gal.r_kpc * KPC) ** 2
        return np.sqrt(g / ACC * gal.r_kpc)

    def obj(p):
        return float(np.sum(((gal.v_obs - model(p)) / gal.v_err) ** 2)) + ups_prior_penalty(10 ** p[0])

    best = None
    for lrho in (-3.0, -2.0, -1.0):
        for lrc in (-0.5, 0.5, 1.2):
            r = optimize.minimize(obj, [math.log10(UPS_DISK_PRIOR), lrho, lrc], method="L-BFGS-B",
                                  bounds=[(-1.3, 0.7), (-6.0, 2.0), (-2.0, 2.5)])
            best = r if best is None or r.fun < best.fun else best
    chi = float(np.sum(((gal.v_obs - model(best.x)) / gal.v_err) ** 2))
    return chi, 3


# --- Solar System ------------------------------------------------------------
SOLAR_PROBES = [("Mercury", 0.387), ("Earth", 1.0), ("Mars", 1.524), ("Jupiter", 5.204), ("Saturn", 9.583)]
# Order-of-magnitude bounds on an anomalous constant radial acceleration from planetary ephemerides
# and Cassini ranging (e.g. Hees et al. 2014 PRD 89, 102002). 1e-12 m/s^2 is deliberately generous.
SOLAR_BOUND_GENEROUS = 1.0e-12


def solar_system_check(nu, a0: float) -> dict:
    out = {}
    for name, r_au in SOLAR_PROBES:
        gn = G * MSUN / (r_au * AU) ** 2
        y = np.array([gn / a0])
        extra = float(gn * (nu(y)[0] - 1.0))
        out[name] = {"g_N": gn, "anomalous_acceleration": extra,
                     "ratio_to_generous_bound": extra / SOLAR_BOUND_GENEROUS}
    out["passes_generous_bound"] = all(v["anomalous_acceleration"] < SOLAR_BOUND_GENEROUS
                                       for k, v in out.items() if isinstance(v, dict))
    return out


# --- Driver ------------------------------------------------------------------
def bic(chi2: float, k: int, n: int) -> float:
    return chi2 + k * math.log(n)


def run(quick: bool = False, make_figures: bool = True) -> dict:
    gals = load_sparc()
    n_pts = sum(g.n for g in gals)
    grid = np.linspace(0.6e-10, 2.0e-10, 15 if quick else 57)
    print(f"Real SPARC sample after cuts (Q <= 2, i >= 30 deg): {len(gals)} galaxies, {n_pts} points")

    results: dict = _load_analysis_checkpoint(quick) or {
        "dataset": "SPARC (Lelli, McGaugh & Schombert 2016, AJ 152, 157)",
        "cuts": "Q <= 2 and inclination >= 30 deg; points with R > 0 and V > 0; errV floored at 1 km/s",
        "n_galaxies": len(gals), "n_points": n_pts,
        "upsilon_treatment": ("baseline: per-galaxy Upsilon_disk with log-normal prior 0.5 +/- 0.1 dex "
                              "(Upsilon_bulge = 1.4 Upsilon_disk); systematic variants: Upsilon fixed at "
                              "0.5/0.7 (McGaugh+2016 convention) and Upsilon free without prior"),
        "horizon_prediction": {lbl: a0_horizon(h0) for lbl, h0 in H0_VALUES.items()},
        "literature_a0": {"value": LITERATURE_A0[0], "random": LITERATURE_A0[1], "systematic": LITERATURE_A0[2],
                          "source": "McGaugh, Lelli & Schombert 2016, PRL 117, 201101"},
        "laws": {},
    }

    if "newton" not in results:
        chi_newton = 0.0
        for gal in gals:
            c2, _, _ = fit_galaxy(gal, nu_newton, 1.0, "prior")
            chi_newton += c2
        results["newton"] = {
            "chi2": chi_newton,
            "n_params": len(gals),
            "bic": bic(chi_newton, len(gals), n_pts),
        }
        _save_analysis_checkpoint(results, quick)
    chi_newton = results["newton"]["chi2"]

    for key, (label, nu) in LAWS.items():
        if key not in results["laws"]:
            prof = profile_a0(gals, nu, grid, "prior")
            variants = {"prior": prof["a0_best"],
                        "fixed": profile_a0(gals, nu, grid, "fixed")["a0_best"],
                        "free": profile_a0(gals, nu, grid, "free")["a0_best"]}
            lo, hi = min(variants.values()), max(variants.values())
            prof["label"] = label
            prof["bic"] = bic(prof["chi2_best"], prof["n_params"], n_pts)
            prof["a0_by_upsilon_treatment"] = variants
            prof["a0_systematic_range"] = [lo, hi]
            prof["solar_system"] = solar_system_check(nu, prof["a0_best"])
            prof["horizon_within_systematic_range"] = {
                lbl: bool(lo <= a_pred <= hi) for lbl, a_pred in results["horizon_prediction"].items()}
            prof["horizon_fractional_offset"] = {
                lbl: (a_pred - prof["a0_best"]) / prof["a0_best"] for lbl, a_pred in results["horizon_prediction"].items()}
            del prof["a0_grid"]
            prof["objective_grid"] = [float(x) for x in prof["objective_grid"]]
            results["laws"][key] = prof
            _save_analysis_checkpoint(results, quick)
        prof = results["laws"][key]
        lo, hi = prof["a0_systematic_range"]
        print(f"  {label:38s} a0 = {prof['a0_best']:.3e} (stat +/- {prof['sigma_scaled']:.0e}; "
              f"Upsilon-systematic range {lo:.2e}-{hi:.2e})  chi2 = {prof['chi2_best']:9.1f}  "
              f"BIC = {prof['bic']:9.1f}  solar system: "
              f"{'PASS' if prof['solar_system']['passes_generous_bound'] else 'FAIL'}")
    results["a0_grid"] = grid.tolist()

    if not quick and "isothermal_halo" not in results:
        chi_halo = k_halo = 0
        for gal in gals:
            c2, k = fit_isothermal_halo(gal)
            chi_halo += c2
            k_halo += k
        results["isothermal_halo"] = {"chi2": chi_halo, "n_params": k_halo, "bic": bic(chi_halo, k_halo, n_pts)}
        _save_analysis_checkpoint(results, quick)
        print(f"  {'Baryons + isothermal DM halo':38s} chi2 = {chi_halo:9.1f}  BIC = {results['isothermal_halo']['bic']:9.1f}")
    print(f"  {'Newtonian baryons only':38s} chi2 = {chi_newton:9.1f}  BIC = {results['newton']['bic']:9.1f}")
    for lbl, a in results["horizon_prediction"].items():
        print(f"  Horizon prediction c*H0/(2 pi), {lbl}: {a:.3e} m/s^2")

    out_json = RESULTS_DIR / ("sparc_real_analysis_quick.json" if quick else "sparc_real_analysis.json")
    _write_results_atomic(out_json, results)
    print(f"Results written to {out_json.relative_to(REPO_ROOT)}")
    if make_figures:
        make_plots(gals, results)
    return results


def make_plots(gals: list[Galaxy], results: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    grid = np.array(results["a0_grid"])

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for key, prof in results["laws"].items():
        obj = np.array(prof["objective_grid"])
        scale = max(prof["chi2_reduced"], 1.0)
        ax.plot(grid * 1e10, (obj - obj.min()) / scale, label=prof["label"])
    for lbl, a in results["horizon_prediction"].items():
        ax.axvline(a * 1e10, ls="--", color="k" if "Planck" in lbl else "gray", lw=1, label=f"c H0 / 2 pi, {lbl}")
    lit = results["literature_a0"]
    ax.axvspan((lit["value"] - lit["systematic"]) * 1e10, (lit["value"] + lit["systematic"]) * 1e10,
               color="orange", alpha=0.12, label="McGaugh+2016 systematic band")
    ax.set_ylim(0, 60)
    ax.set_xlabel(r"global $a_0$  [$10^{-10}$ m s$^{-2}$]")
    ax.set_ylabel(r"$\Delta\chi^2 / \chi^2_\nu$ (profile, error-rescaled)")
    ax.set_title(f"Real SPARC: global $a_0$ profile ({results['n_galaxies']} galaxies, {results['n_points']} points)")
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_real_sparc_a0_profile.png", dpi=150)
    plt.close(fig)

    key = "emrf_sqrt"
    a0 = results["laws"][key]["a0_best"]
    gb_all, go_all = [], []
    for gal in gals:
        _, _, ups = fit_galaxy(gal, nu_emrf_sqrt, a0, "prior")
        gb_all.append(g_newton(gal, ups))
        go_all.append(gal.v_obs**2 / gal.r_kpc * ACC)
    gb, go = np.concatenate(gb_all), np.concatenate(go_all)
    x = np.logspace(-12.5, -8.0, 300)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.0, 7.0), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax1.loglog(gb, go, ".", ms=2, alpha=0.35, color="gray", label="SPARC (real)")
    ax1.loglog(x, x, "k:", lw=1, label="Newton")
    for k2, (label, nu) in LAWS.items():
        ax1.loglog(x, x * nu(x / results["laws"][k2]["a0_best"]), lw=1.2, label=label)
    ax1.set_ylabel(r"$g_{\rm obs}$ [m s$^{-2}$]")
    ax1.set_xlim(1e-13, 3e-8)
    ax1.legend(fontsize=7)
    ax1.set_title("Radial acceleration relation, real SPARC data")
    resid = np.log10(go) - np.log10(gb * nu_emrf_sqrt(gb / a0))
    ax2.semilogx(gb, resid, ".", ms=2, alpha=0.35, color="gray")
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_ylim(-0.6, 0.6)
    ax2.set_xlabel(r"$g_{\rm bar}$ [m s$^{-2}$]")
    ax2.set_ylabel("resid. vs EMRF law [dex]")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_real_sparc_rar.png", dpi=150)
    plt.close(fig)
    print("Figures written to paper/figures/fig_real_sparc_a0_profile.png and fig_real_sparc_rar.png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="coarse a0 grid and no dark-halo fits")
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()
    run(quick=args.quick, make_figures=not args.no_figures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
