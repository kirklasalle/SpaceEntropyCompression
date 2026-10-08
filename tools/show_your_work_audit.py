"""Independent "show your work" audit of the EMRF / Space-Entropy Compression claims.

Every number quoted in docs/SHOW_YOUR_WORK.md is recomputed here from first
principles or from the repository's own code, so that any reader can check it.

Usage
-----
    python tools/show_your_work_audit.py            # all sections
    python tools/show_your_work_audit.py --no-sparc # skip the real-SPARC download/re-fit

The real-SPARC re-analysis downloads the public SPARC rotation-curve archive
(Lelli, McGaugh & Schombert 2016, AJ 152, 157) from
https://astroweb.case.edu/SPARC/Rotmod_LTG.zip into a temporary cache folder.
It is not redistributed in this repository.
"""

from __future__ import annotations

import argparse
import io
import math
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from scipy import optimize, stats

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "emergent_matter_model"))

# --- Constants (CODATA 2018 / IAU 2015) -----------------------------------
G = 6.67430e-11
C = 2.99792458e8
HBAR = 1.054571817e-34
KB = 1.380649e-23
MSUN = 1.98847e30
AU = 1.495978707e11
PC = 3.085677581e16
KPC = 1e3 * PC
MPC = 1e6 * PC
YR = 365.25 * 86400.0
A0 = 1.20e-10

SPARC_URL = "https://astroweb.case.edu/SPARC/Rotmod_LTG.zip"


def header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# 1. Curvature numbers
# ---------------------------------------------------------------------------
def kretschmann(m_sun: float, r_m: float) -> float:
    rg = G * m_sun * MSUN / C**2
    return 48.0 * rg**2 / r_m**6


def section_curvature() -> None:
    header("1. KRETSCHMANN INVARIANT K = 48 G^2 M^2 / (c^4 r^6)")
    m_bh = 4.297e6
    for label, r_au, claimed in [("S2 pericentre", 118.3, 1.25e-24), ("S301 pericentre", 12.2, 1.4e-18)]:
        k = kretschmann(m_bh, r_au * AU)
        print(f"{label:16s} r = {r_au:6.1f} AU : K = {k:.3e} m^-4   (repo claims {claimed:.2e}; "
              f"off by 10^{math.log10(claimed / k):.1f})")
    ratio = (118.3 / 12.2) ** 6
    print(f"K(S301)/K(S2) = (118.3/12.2)^6 = {ratio:.3e}   (repo: 8.2e5 -- correct)")
    for m, r_kpc in [(1e9, 10), (1e10, 10), (1e11, 50)]:
        print(f"Galaxy M = {m:.0e} Msun at r = {r_kpc} kpc : K = {kretschmann(m, r_kpc * KPC):.2e} m^-4   (repo: ~1e-78)")
    print("Density mapping rho ~ C^alpha with C ~ sqrt(K) ~ r^-3 gives rho ~ r^(-3 alpha).")
    print("  Flat rotation curve needs rho ~ r^-2  ->  alpha = 2/3 (repo text says alpha = 1/3, which gives r^-1).")


# ---------------------------------------------------------------------------
# 2. The acceleration scale a0
# ---------------------------------------------------------------------------
def h0_si(h0_kms_mpc: float) -> float:
    return h0_kms_mpc * 1e3 / MPC


def section_a0() -> None:
    header("2. THE ACCELERATION SCALE a0 AND THE UNRUH / GIBBONS-HAWKING ARGUMENT")
    for h0 in (67.4, 70.0, 73.0):
        h = h0_si(h0)
        print(f"H0 = {h0:5.1f} km/s/Mpc : c*H0 = {C * h:.3e} m/s^2 ; c*H0/(2 pi) = {C * h / (2 * math.pi):.3e} m/s^2")
    h_needed = 2 * math.pi * A0 / C * MPC / 1e3
    print(f"H0 required for c*H0/(2 pi) = 1.20e-10 exactly : {h_needed:.1f} km/s/Mpc")
    h = h0_si(67.4)
    t_ds = HBAR * h / (2 * math.pi * KB)
    a_unruh = 2 * math.pi * C * KB * t_ds / HBAR
    print(f"T_dS (H0=67.4) = {t_ds:.3e} K ; acceleration whose Unruh temperature equals T_dS = {a_unruh:.3e} m/s^2")
    print("  -> Setting T_Unruh = T_dS gives a = c*H0 (no 2 pi). The 1/(2 pi) used in the paper is inserted by hand")
    print("     (it is Milgrom's 1999 numerical observation, not a consequence of the stated equations).")


# ---------------------------------------------------------------------------
# 3. Interpolating functions and the strong-field limit
# ---------------------------------------------------------------------------
def g_emrf(gb: np.ndarray, a0: float = A0) -> np.ndarray:
    return np.sqrt(gb**2 + a0 * gb)


def g_rar(gb: np.ndarray, a0: float = A0) -> np.ndarray:
    return gb / (1.0 - np.exp(-np.sqrt(gb / a0)))


def section_interpolation() -> None:
    header("3. THE WEAK-FIELD FORMULA g = sqrt(g_N^2 + a0 g_N) AND ITS STRONG-FIELD LIMIT")
    m_flat = 1e10 * MSUN
    v_flat = (G * m_flat * A0) ** 0.25
    print(f"Deep limit g -> sqrt(a0 g_N) => V^4 = G M a0 ; M = 1e10 Msun gives V_flat = {v_flat / 1e3:.1f} km/s (algebra correct)")
    print("Strong limit: sqrt(g^2 + a0 g) = g sqrt(1 + a0/g) = g + a0/2 - a0^2/(8g) + ...  -> constant extra a0/2 everywhere")
    gm_sun = G * MSUN
    for name, r_au, bound in [("Mercury", 0.387, 1.2e-12), ("Earth", 1.0, 1.0e-13), ("Saturn", 9.5826, 3.2e-14)]:
        gn = gm_sun / (r_au * AU) ** 2
        d_emrf = float(g_emrf(np.array([gn]))[0] - gn)
        d_rar = float(g_rar(np.array([gn]))[0] - gn)
        print(f"  {name:8s} g_N = {gn:.3e} : EMRF extra = {d_emrf:.3e} m/s^2 ({d_emrf / bound:8.1f} x the bound used in the repo);"
              f" RAR extra = {d_rar:.1e}")
    print("  -> The formula used for SPARC, JWST and the paper is the repo's own 'unscreened_naive' model,")
    print("     which stress_test_solar_system.py marks FALSIFIED. The passing 'emrf_screened' model is a different,")
    print("     hand-built function (McGaugh nu times 1 - tanh(y/100)).")


# ---------------------------------------------------------------------------
# 4. S-star orbits: table consistency, data integrity and the BIC procedure
# ---------------------------------------------------------------------------
def section_sstars() -> None:
    import fit_astrometry as fa

    header("4a. S-STAR ORBITAL TABLE IN paper/main.tex (M_BH = 4.3e6 Msun)")
    table = {"S2": (16.05, 1020, 0.884, 118.3), "S29": (90.0, 3448, 0.969, 106.9), "S38": (19.2, 1162, 0.820, 209.2),
             "S55": (12.8, 887, 0.720, 248.4), "S301": (8.7, 620, 0.960, 12.2)}
    for star, (p, a, e, rp) in table.items():
        p_kepler = math.sqrt(a**3 / 4.3e6)
        print(f"{star:5s} a(1-e) = {a * (1 - e):6.1f} AU (table {rp:6.1f}) | Kepler P = {p_kepler:5.2f} yr (table {p:5.2f})")
    print("  -> S301 row is internally inconsistent (published: a ~ 83 mas ~ 690 AU, e ~ 0.983, Nature 2026 / arXiv:2607.12664).")

    gm = G * 4.297e6 * MSUN
    for name, a_au, e in [("S2", 1035.0, 0.88466), ("S301", 679.0, 0.982)]:
        a_m = a_au * AU
        dphi = 6 * math.pi * gm / (C**2 * a_m * (1 - e**2))
        vp = math.sqrt(gm * (1 + e) / (a_m * (1 - e)))
        print(f"{name}: Schwarzschild precession = {math.degrees(dphi) * 60:6.2f} arcmin/orbit ; v_peri = {vp / 1e3:7.0f} km/s = {vp / C:.4f} c")

    header("4b. INTEGRITY OF THE (NOW QUARANTINED) S-STAR TABLES data/synthetic/astrometry/*.csv")
    d = REPO / "data" / "synthetic" / "astrometry"
    s2 = fa.load_astrometry_csv(d / "s2_synthetic.csv")
    i1, i2 = 0, int(np.argmin(np.abs(s2["epoch"] - 2018.379)))
    sep = math.hypot(s2["ra_mas"][i1] - s2["ra_mas"][i2], s2["dec_mas"][i1] - s2["dec_mas"][i2])
    print(f"S2 position at {s2['epoch'][i1]:.3f} = ({s2['ra_mas'][i1]:.1f}, {s2['dec_mas'][i1]:.1f}) mas; "
          f"at {s2['epoch'][i2]:.3f} = ({s2['ra_mas'][i2]:.2f}, {s2['dec_mas'][i2]:.2f}) mas")
    print(f"  Two pericentre passages one period apart are {sep:.1f} mas apart. 12' of precession moves the")
    print(f"  pericentre by only ~0.05 mas (r_peri ~ 14 mas x 3.6e-3 rad). Real orbits cannot do this.")

    mas_to_km = 1e-3 / 206264.806 * 8275.0 * PC / 1e3
    for star, fname, params in [("S2", "s2_synthetic.csv", fa.S2_BENCHMARK_PARAMS),
                                ("S301", "s301_synthetic.csv", fa.S301_BENCHMARK_PARAMS)]:
        obs = fa.load_astrometry_csv(d / fname)
        a_m = params.semi_major_axis_au * AU
        gmb = G * params.mass_bh * MSUN
        v_max = math.sqrt(gmb * (1 + params.eccentricity) / (a_m * (1 - params.eccentricity))) / 1e3
        worst = 0.0
        for k in range(len(obs["epoch"]) - 1):
            dt = (obs["epoch"][k + 1] - obs["epoch"][k]) * YR
            dth = math.hypot(obs["ra_mas"][k + 1] - obs["ra_mas"][k], obs["dec_mas"][k + 1] - obs["dec_mas"][k])
            v_sky = dth * mas_to_km / dt
            v3d = math.hypot(v_sky, obs["vr_kms"][k])
            worst = max(worst, v3d)
            if v_sky > C / 1e3 or v3d > 1.2 * v_max:
                print(f"  {star} {obs['epoch'][k]:.3f}->{obs['epoch'][k + 1]:.3f}: sky speed {v_sky:9.0f} km/s, "
                      f"with v_r -> |v| ~ {v3d:9.0f} km/s (max allowed by orbit {v_max:6.0f}; c = 299792)")
        print(f"  {star}: largest implied 3-D speed {worst:.0f} km/s vs orbital maximum {v_max:.0f} km/s")
    print("  S301 discovery paper (Nature 2026): radial velocity NOT yet measured; 19 astrometric points from 2017-2025.")
    print("  The repo file has 15 radial velocities from 2020-2026 -> these cannot come from the cited source.")

    header("4c. WHAT THE 'MULTI-STAR JOINT FIT' ACTUALLY COMPUTES")
    total_dchi2, n_tot = 0.0, 0
    for sid, params in fa.ALL_S_STAR_PARAMS.items():
        fname = f"{sid}_synthetic.csv"
        obs = fa.load_astrometry_csv(d / fname)
        n = 3 * len(obs["epoch"])
        chi_gr = fa.compute_residuals_and_chi2(obs, fa.project_orbital_position_to_sky(params, obs["epoch"], "gr_1pn"))[0]

        def chi_beta(b: float) -> float:
            return fa.compute_residuals_and_chi2(obs, fa.project_orbital_position_to_sky(params, obs["epoch"], "emrf", b))[0]

        dchi = chi_beta(0.005) - chi_gr
        betas = np.linspace(-50, 50, 2001)
        best = betas[int(np.argmin([chi_beta(b) for b in betas]))]
        total_dchi2 += dchi
        n_tot += n
        print(f"{params.name:5s} N = {n:3d} chi2_GR = {chi_gr:12.1f} (reduced {chi_gr / (n - 8):10.1f}) | "
              f"dchi2(beta=0.005) = {dchi:+8.2f} | chi2-minimising beta in [-50,50] = {best:+6.2f}")
    print(f"Sum of per-star dchi2 + ln(N_total) = {total_dchi2:.3f} + {math.log(n_tot):.3f} = {total_dchi2 + math.log(n_tot):.3f}")
    print("  -> Equals the published 'joint' Delta-BIC = +70.743. No parameter is shared or fitted; orbital elements")
    print("     are fixed, beta is fixed at 0.005, and S38's negative contribution is still in the sum (it is outweighed")
    print("     by S301, whose data are not authentic). Reduced chi2 of 1e5-1e6 means no model fits these data.")


# ---------------------------------------------------------------------------
# 5. SPARC: repo files vs the real database, and an honest re-fit
# ---------------------------------------------------------------------------
TEN = ["DDO154", "IC2574", "NGC1560", "NGC2403", "NGC2841", "NGC2903", "NGC3198", "NGC6503", "NGC7331", "UGC02885"]
ACC = 1e6 / KPC  # (km/s)^2 / kpc -> m/s^2


def load_real_sparc() -> dict[str, np.ndarray]:
    cache = Path(tempfile.gettempdir()) / "emrf_sparc_cache" / "Rotmod_LTG.zip"
    if not cache.is_file():
        cache.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {SPARC_URL} ...")
        with urllib.request.urlopen(SPARC_URL, timeout=120) as r:
            cache.write_bytes(r.read())
    out = {}
    with zipfile.ZipFile(cache) as z:
        for name in z.namelist():
            if name.endswith("_rotmod.dat"):
                arr = np.loadtxt(io.StringIO(z.read(name).decode()), comments="#", usecols=range(6), ndmin=2)
                out[Path(name).name.replace("_rotmod.dat", "")] = arr
    return out


def vbar2(arr: np.ndarray, ups: float) -> np.ndarray:
    _, _, _, vg, vd, vb = arr.T
    return vg * np.abs(vg) + ups * vd * np.abs(vd) + 1.4 * ups * vb * np.abs(vb)


def model_v(kind: str, arr: np.ndarray, p: np.ndarray) -> np.ndarray:
    r = arr[:, 0]
    vb2 = np.clip(vbar2(arr, p[0]), 1e-6, None)
    gb = vb2 / r * ACC
    if kind == "newton":
        g = gb
    elif kind == "rar":
        g = g_rar(gb)
    elif kind == "emrf":
        g = g_emrf(gb)
    elif kind == "iso":  # pseudo-isothermal dark halo: rho0 [Msun/pc^3], rc [kpc]
        rho0, rc = 10 ** p[1], 10 ** p[2]
        m = 4 * math.pi * rho0 * (rc * 1e3) ** 3 * (r / rc - np.arctan(r / rc))
        g = gb + G * m * MSUN / (r * KPC) ** 2
    return np.sqrt(g / ACC * r)


def fit_galaxy(kind: str, arr: np.ndarray) -> tuple[float, int]:
    v, ev = arr[:, 1], np.maximum(arr[:, 2], 1e-3)

    def chi(p):
        return float(np.sum(((v - model_v(kind, arr, p)) / ev) ** 2))

    if kind == "iso":
        best = None
        for lr in (-3.0, -2.0, -1.0):
            for lc in (-0.5, 0.5, 1.2):
                res = optimize.minimize(chi, [0.5, lr, lc], method="L-BFGS-B",
                                        bounds=[(0.1, 2.0), (-5.0, 1.0), (-1.5, 2.0)])
                best = res if best is None or res.fun < best.fun else best
        return best.fun, 3
    res = optimize.minimize_scalar(lambda u: chi([u]), bounds=(0.1, 2.0), method="bounded")
    return res.fun, 1


def section_sparc(do_download: bool) -> None:
    header("5. SPARC ROTATION CURVES")
    import fit_sparc as fs

    if not do_download:
        print("Skipped (--no-sparc).")
        return
    try:
        real = load_real_sparc()
    except Exception as exc:  # network issues should not hide the other sections
        print(f"Could not obtain SPARC archive: {exc}")
        return
    print("Repo file vs real SPARC (number of points, outer radius, V_disk max at Upsilon=1):")
    for gal in TEN:
        _, repo_pts = fs.load_sparc_galaxy(REPO / "data" / "synthetic" / "sparc" / f"{gal.lower().replace('ugc02885', 'ugc2885')}.csv")
        rr = np.array([p.radius_kpc for p in repo_pts])
        rd = np.array([p.v_disk_kms for p in repo_pts])
        if gal not in real:
            print(f"  {gal:9s} repo N={len(rr):3d} R_max={rr.max():5.1f} Vd_max={rd.max():6.1f} | "
                  f"NOT IN THE 175-GALAXY SPARC CATALOGUE")
            continue
        a = real[gal]
        print(f"  {gal:9s} repo N={len(rr):3d} R_max={rr.max():5.1f} Vd_max={rd.max():6.1f} | "
              f"real N={len(a):3d} R_max={a[:, 0].max():5.1f} Vd_max={a[:, 4].max():6.1f}")

    in_sparc = [g for g in TEN if g in real]
    for label, names in [(f"Same galaxies ({len(in_sparc)} of the 10 exist in SPARC), REAL data", in_sparc),
                         ("All 175 SPARC galaxies, REAL data", sorted(real))]:
        tot = {k: [0.0, 0, 0] for k in ("newton", "rar", "emrf", "iso")}
        for gal in names:
            arr = real[gal]
            arr = arr[arr[:, 0] > 0]
            for kind in tot:
                c2, k = fit_galaxy(kind, arr)
                tot[kind][0] += c2
                tot[kind][1] += k
            for kind in tot:
                tot[kind][2] += len(arr)
        n = tot["newton"][2]
        print(f"\n{label}: N = {n} points (Upsilon_disk fitted per galaxy in [0.1, 2.0]; Upsilon_bulge = 1.4 Upsilon_disk)")
        bic = {k: v[0] + v[1] * math.log(n) for k, v in tot.items()}
        for kind, nm in [("newton", "Newtonian baryons only"), ("emrf", "EMRF sqrt(g^2 + a0 g)"),
                         ("rar", "McGaugh RAR (2016)"), ("iso", "Baryons + isothermal DM halo")]:
            c2, k, _ = tot[kind]
            print(f"  {nm:30s} chi2 = {c2:11.1f}  params = {k:4d}  BIC = {bic[kind]:11.1f}  "
                  f"dBIC vs EMRF = {bic[kind] - bic['emrf']:+10.1f}")


# ---------------------------------------------------------------------------
# 6. JWST sample
# ---------------------------------------------------------------------------
def section_jwst() -> None:
    header("6. JWST / ALMA HIGH-REDSHIFT SAMPLE")
    chi2_claim, dof = 1.20, 9
    print(f"Claimed chi2 = {chi2_claim} for {dof} degrees of freedom; P(chi2 <= {chi2_claim}) = "
          f"{stats.chi2.cdf(chi2_claim, dof):.5f}  (a fit this good happens ~1 time in {1 / stats.chi2.cdf(chi2_claim, dof):.0f})")
    rows = np.genfromtxt(REPO / "data" / "synthetic" / "jwst_kinematics_synthetic.csv", delimiter=",", names=True,
                         dtype=None, encoding="utf-8", skip_header=3)
    print("Is the deep-MOND formula V = (G M a0(z))^(1/4) applicable? Compare g_bar(r_half) with a0(z):")
    for row in rows:
        z = float(row["redshift_z"])
        ez = math.sqrt(0.315 * (1 + z) ** 3 + 0.685)
        gb = G * 0.5 * 10 ** float(row["log_m_bar_solar"]) * MSUN / (float(row["r_half_light_kpc"]) * KPC) ** 2
        print(f"  {row['galaxy_id']:18s} z = {z:4.2f}  g_bar(r_half)/a0(z) = {gb / (A0 * ez):5.2f}")
    print("  Known catalogue facts (rows SYN-Z04, SYN-Z07, SYN-Z08 originally carried these names): GN-z11 is at")
    print("  z = 10.6 (not 3.15); REBELS-12 is at z = 7.35 (not 5.18); GS-9422 (Cameron+2024) is a nebular-continuum")
    print("  spectrum, not a rotation-velocity measurement.")


# ---------------------------------------------------------------------------
# 7. Cosmology data files
# ---------------------------------------------------------------------------
def section_cosmology() -> None:
    header("7. COSMOLOGY DATA FILES")
    raw = np.loadtxt(REPO / "data" / "synthetic" / "cosmology" / "sn_hubble_diagram_synthetic.csv", delimiter=",", comments="#", skiprows=4)
    sn = {"z_hd": raw[:, 0], "mu_obs": raw[:, 1], "mu_err": raw[:, 2]}

    def mu(z, h0, om):
        zz = np.linspace(0, z, 400)
        dc = C / 1e3 / h0 * np.trapezoid(1 / np.sqrt(om * (1 + zz) ** 3 + 1 - om), zz)
        return 5 * np.log10((1 + z) * dc) + 25

    def chi(p):
        return np.sum(((sn["mu_obs"] - np.array([mu(z, *p) for z in sn["z_hd"]])) / sn["mu_err"]) ** 2)

    res = optimize.minimize(chi, [70, 0.3], method="Nelder-Mead")
    resid = sn["mu_obs"] - np.array([mu(z, *res.x) for z in sn["z_hd"]])
    n_sn = len(sn["z_hd"])
    print(f"'Pantheon+ binned' file: flat LCDM best fit H0 = {res.x[0]:.2f}, Om = {res.x[1]:.3f}, "
          f"chi2 = {res.fun:.3f} for {n_sn - 2} dof")
    print(f"  RMS residual = {np.std(resid):.4f} mag vs typical quoted error {np.mean(sn['mu_err']):.3f} mag;"
          f" P(chi2 <= obs) = {stats.chi2.cdf(res.fun, n_sn - 2):.2e}")
    print("  -> Points lie on a smooth curve with no statistical scatter: generated, not binned real data.")
    desi_dr1 = {("BGS", "DV_over_rd"): (0.295, 7.93, 0.15),
                ("LRG1", "DM_over_rd"): (0.510, 13.62, 0.25), ("LRG1", "DH_over_rd"): (0.510, 20.98, 0.61),
                ("LRG2", "DM_over_rd"): (0.706, 16.85, 0.32), ("LRG2", "DH_over_rd"): (0.706, 20.08, 0.60),
                ("LRG3_ELG1", "DM_over_rd"): (0.930, 21.71, 0.28), ("LRG3_ELG1", "DH_over_rd"): (0.930, 17.88, 0.35),
                ("ELG2", "DM_over_rd"): (1.317, 27.79, 0.69), ("ELG2", "DH_over_rd"): (1.317, 13.82, 0.42),
                ("QSO", "DV_over_rd"): (1.491, 26.07, 0.67),
                ("Lya_QSO", "DM_over_rd"): (2.330, 39.71, 0.94), ("Lya_QSO", "DH_over_rd"): (2.330, 8.52, 0.17)}
    print("DESI DR1 (arXiv:2404.03002 Table 1) vs data/cosmology/desi_2024_bao.csv:")
    n_bad, n_rows = 0, 0
    with open(REPO / "data" / "cosmology" / "desi_2024_bao.csv", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("tracer"):
                continue
            tr, z, obs, val, err = line.strip().split(",")[:5]
            n_rows += 1
            ref = desi_dr1.get((tr, obs))
            if ref is None or abs(ref[1] - float(val)) > 1e-6 or abs(ref[0] - float(z)) > 1e-3 or abs(ref[2] - float(err)) > 1e-6:
                n_bad += 1
                print(f"  MISMATCH {tr:10s} {obs:11s} repo z={z} {val}+/-{err}  | DR1 {ref}")
    print(f"  {n_rows - n_bad} of {n_rows} rows match the published table"
          f" (the original file had 5 mismatching rows; corrected 2026-10-07).")
    print("CMB: cmb_acoustic_engine.py hard-codes peak heights 5748.2, 2552.4, 2521.8 uK^2 -- the identical numbers")
    print("  stored as 'data' in the (now quarantined) CMB peak table, and uses Omega_C_matter = 0.266 (= Planck's")
    print("  cold dark matter density, renamed). The CMB 'fit' is therefore circular and assumes dark matter.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-sparc", action="store_true", help="skip downloading / re-fitting the real SPARC data")
    args = ap.parse_args()
    section_curvature()
    section_a0()
    section_interpolation()
    section_sstars()
    section_sparc(not args.no_sparc)
    section_jwst()
    section_cosmology()


if __name__ == "__main__":
    main()
