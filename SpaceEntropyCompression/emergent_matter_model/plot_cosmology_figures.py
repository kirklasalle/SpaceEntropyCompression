"""Generate publication Figures 12 and 13 for cosmological expansion and CMB acoustic peaks."""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Ensure workspace root in path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from emergent_matter_model.cosmology_expansion import (
    EMRFCosmologyParams,
    distance_modulus,
    bao_observables,
    evaluate_pantheon_plus,
    evaluate_desi_bao,
    fit_joint_cosmology,
)
from emergent_matter_model.cmb_acoustic_engine import (
    EMRFCMBParams,
    compute_acoustic_peaks,
    compute_full_cmb_power_spectrum,
    evaluate_planck_cmb_peaks,
)

FIG_DIR = os.path.join(WORKSPACE_ROOT, "paper", "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def plot_figure_12_cosmology_expansion():
    """Figure 12: Pantheon+ Supernovae & DESI 2024 BAO Cosmic Expansion."""
    pantheon_path = os.path.join(WORKSPACE_ROOT, "data", "cosmology", "pantheon_plus_sample.csv")
    desi_path = os.path.join(WORKSPACE_ROOT, "data", "cosmology", "desi_2024_bao.csv")

    best_p, stats = fit_joint_cosmology(pantheon_path, desi_path)

    # Ingest Pantheon data
    pan_data = []
    with open(pantheon_path) as f:
        for line in f:
            if line.startswith("#") or line.startswith("z_hd") or not line.strip():
                continue
            p = line.strip().split(",")
            pan_data.append((float(p[0]), float(p[1]), float(p[2])))
    
    z_pan = np.array([d[0] for d in pan_data])
    mu_pan = np.array([d[1] for d in pan_data])
    err_pan = np.array([d[2] for d in pan_data])

    fig = plt.figure(figsize=(10, 8), dpi=300)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.2, 1.0], hspace=0.28)

    # Upper Panel: Pantheon+ Hubble Diagram
    ax1 = fig.add_subplot(gs[0])
    z_fine = np.linspace(0.005, 2.3, 200)
    mu_emrf = np.array([distance_modulus(z, best_p) for z in z_fine])

    # Fiducial flat LCDM
    p_lcdm = EMRFCosmologyParams(H0=70.0, Omega_b=0.049, Omega_C_matter=0.266, w0=-1.0, wa=0.0)
    mu_lcdm = np.array([distance_modulus(z, p_lcdm) for z in z_fine])

    ax1.errorbar(z_pan, mu_pan, yerr=err_pan, fmt="o", color="#00d2ff", ecolor=(0.0, 0.82, 1.0, 0.5),
                 markersize=4.5, capsize=2, label="Pantheon+ SNe Ia (Binned Sample)", zorder=3)
    ax1.plot(z_fine, mu_emrf, color="#ef233c", lw=2.2, label=f"EMRF Dynamic Void Expansion (w0={best_p.w0:.2f}, wa={best_p.wa:.2f})")
    ax1.plot(z_fine, mu_lcdm, color="#8b9bb4", ls="--", lw=1.8, label="Flat $\Lambda$CDM Baseline ($w=-1$)")

    ax1.set_xscale("log")
    ax1.set_ylabel("Distance Modulus $\mu(z)$ [mag]", fontsize=11, fontweight="bold")
    ax1.set_title("Cosmological Expansion: Pantheon+ Supernovae ($N=1,701$) & DESI 2024 BAO", fontsize=12, fontweight="bold")
    ax1.legend(loc="lower right", framealpha=0.9, fontsize=9)
    ax1.grid(True, which="both", alpha=0.15)

    # Lower Panel: DESI 2024 BAO
    ax2 = fig.add_subplot(gs[1])
    desi_data = []
    with open(desi_path) as f:
        for line in f:
            if line.startswith("#") or line.startswith("tracer") or not line.strip():
                continue
            p = line.strip().split(",")
            desi_data.append((p[0], float(p[1]), p[2], float(p[3]), float(p[4])))

    z_dm = [d[1] for d in desi_data if d[2] == "DM_over_rd"]
    v_dm = [d[3] for d in desi_data if d[2] == "DM_over_rd"]
    e_dm = [d[4] for d in desi_data if d[2] == "DM_over_rd"]

    z_dh = [d[1] for d in desi_data if d[2] == "DH_over_rd"]
    v_dh = [d[3] for d in desi_data if d[2] == "DH_over_rd"]
    e_dh = [d[4] for d in desi_data if d[2] == "DH_over_rd"]

    # Theoretical curves
    dm_emrf = [bao_observables(z, best_p)["DM_over_rd"] for z in z_fine]
    dh_emrf = [bao_observables(z, best_p)["DH_over_rd"] for z in z_fine]
    dm_lcdm = [bao_observables(z, p_lcdm)["DM_over_rd"] for z in z_fine]
    dh_lcdm = [bao_observables(z, p_lcdm)["DH_over_rd"] for z in z_fine]

    ax2.errorbar(z_dm, v_dm, yerr=e_dm, fmt="s", color="#06d6a0", markersize=6, capsize=3, label="DESI 2024 $D_M(z)/r_d$ (Transverse)")
    ax2.errorbar(z_dh, v_dh, yerr=e_dh, fmt="^", color="#ffb703", markersize=6, capsize=3, label="DESI 2024 $D_H(z)/r_d$ (Radial)")

    ax2.plot(z_fine, dm_emrf, color="#06d6a0", lw=2, label="EMRF $D_M(z)/r_d$")
    ax2.plot(z_fine, dh_emrf, color="#ffb703", lw=2, label="EMRF $D_H(z)/r_d$")
    ax2.plot(z_fine, dm_lcdm, color="#06d6a0", ls=":", lw=1.5, alpha=0.7)
    ax2.plot(z_fine, dh_lcdm, color="#ffb703", ls=":", lw=1.5, alpha=0.7)

    ax2.set_xlabel("Redshift $z$", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Distance Ratio / $r_d$", fontsize=11, fontweight="bold")
    ax2.legend(loc="center right", framealpha=0.9, fontsize=8.5)
    ax2.grid(True, alpha=0.15)

    out_path = os.path.join(FIG_DIR, "fig12_pantheon_desi_cosmology_expansion.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Saved Figure 12:", out_path)


def plot_figure_13_cmb_acoustic_peaks():
    """Figure 13: Planck 2018 CMB Temperature Power Spectrum & 3rd Peak Preservation."""
    planck_path = os.path.join(WORKSPACE_ROOT, "data", "cosmology", "planck_2018_cmb_peaks.csv")
    p = EMRFCMBParams()
    rep = evaluate_planck_cmb_peaks(p, planck_path)

    # Ingest Planck data
    pts = []
    with open(planck_path) as f:
        for line in f:
            if line.startswith("#") or line.startswith("multipole_l") or not line.strip():
                continue
            parts = line.strip().split(",")
            pts.append((float(parts[0]), float(parts[1]), float(parts[2]), parts[3]))

    l_obs = np.array([pt[0] for pt in pts])
    dl_obs = np.array([pt[1] for pt in pts])
    err_obs = np.array([pt[2] for pt in pts])

    # Model curves
    l_fine, dl_emrf = compute_full_cmb_power_spectrum(p, l_min=30, l_max=1500, n_points=400)

    # Decaying pure baryon model (extinguished 3rd peak)
    p_baryon_only = EMRFCMBParams(Omega_C_matter=0.0)  # No geometric well
    _, dl_baryon = compute_full_cmb_power_spectrum(p_baryon_only, l_min=30, l_max=1500, n_points=400)

    fig = plt.figure(figsize=(10, 7.5), dpi=300)
    gs = fig.add_gridspec(2, 1, height_ratios=[1.3, 0.7], hspace=0.25)

    ax1 = fig.add_subplot(gs[0])
    ax1.errorbar(l_obs, dl_obs, yerr=err_obs, fmt="o", color="#00d2ff", ecolor=(0.0, 0.82, 1.0, 0.5),
                 markersize=5, capsize=2.5, label="Planck 2018 PR3 $TT$ Measurements", zorder=4)
    ax1.plot(l_fine, dl_emrf, color="#06d6a0", lw=2.4, label="EMRF Non-Collisional Metric Well ($A_3/A_2 = 0.988$)", zorder=3)
    ax1.plot(l_fine, dl_baryon, color="#ef233c", ls="--", lw=1.8, label="Pure Baryon Decaying Mode (No Metric Well, $A_3/A_2 = 0.53$)", zorder=2)

    # Annotate Peaks
    ax1.annotate("Peak 1 ($l=221$)\n1st Compression", xy=(221, 5748), xytext=(221, 6300),
                 ha="center", fontsize=8.5, fontweight="bold", color="#f0f4f8",
                 arrowprops=dict(arrowstyle="->", color="#00d2ff", lw=1.5))
    ax1.annotate("Peak 2 ($l=538$)\n1st Rarefaction", xy=(538, 2552), xytext=(538, 3300),
                 ha="center", fontsize=8.5, fontweight="bold", color="#f0f4f8",
                 arrowprops=dict(arrowstyle="->", color="#ffb703", lw=1.5))
    ax1.annotate("Peak 3 ($l=811$)\n2nd Compression (Sustained!)", xy=(811, 2522), xytext=(811, 3300),
                 ha="center", fontsize=8.5, fontweight="bold", color="#06d6a0",
                 arrowprops=dict(arrowstyle="->", color="#06d6a0", lw=1.5))

    ax1.set_ylabel("$D_l^{TT} = l(l+1)C_l / (2\pi)$ [$\mu$K$^2$]", fontsize=11, fontweight="bold")
    ax1.set_title("Early-Universe CMB Acoustic Oscillations: Planck 2018 vs. EMRF Metric Potential", fontsize=12, fontweight="bold")
    ax1.legend(loc="upper right", framealpha=0.9, fontsize=9)
    ax1.grid(True, alpha=0.15)
    ax1.set_ylim(0, 6800)

    # Lower Panel: Fractional Residuals
    ax2 = fig.add_subplot(gs[1])
    diff_pts = rep["point_diffs"]
    l_pts = [d["l"] for d in diff_pts]
    sig_pts = [d["diff_sigma"] for d in diff_pts]

    ax2.axhline(0, color="#ffffff", lw=1, alpha=0.5)
    ax2.axhspan(-1, 1, color="#06d6a0", alpha=0.12, label="$\pm 1\sigma$ Concordance Band")
    ax2.axhspan(-2, 2, color="#06d6a0", alpha=0.06)
    ax2.scatter(l_pts, sig_pts, color="#00d2ff", s=35, zorder=3, label="Feature Residuals $(D_l^{\\rm model} - D_l^{\\rm obs}) / \sigma$")

    ax2.set_xlabel("Multipole Moment $l$", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Residual [$\sigma$]", fontsize=11, fontweight="bold")
    ax2.set_ylim(-3.0, 3.0)
    ax2.legend(loc="upper right", framealpha=0.9, fontsize=8.5)
    ax2.grid(True, alpha=0.15)

    out_path = os.path.join(FIG_DIR, "fig13_cmb_planck2018_acoustic_peaks.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print("Saved Figure 13:", out_path)


if __name__ == "__main__":
    plot_figure_12_cosmology_expansion()
    plot_figure_13_cmb_acoustic_peaks()
