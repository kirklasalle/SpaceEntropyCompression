"""Publication-grade visualization script for EMRF deep perspectives and stress tests.

Generates 4 high-DPI (300 DPI) figures for the extended scientific audit and manuscript:
1. fig5_solar_system_screening_limits.png:
   Multi-decade acceleration profile & Cassini / LLR anomalous acceleration bounds.
2. fig6_gravitational_lensing_geodesics.png:
   2D null geodesic ray tracing & SLACS strong lensing benchmark comparison.
3. fig7_bullet_cluster_entropy_separation.png:
   4-panel 2D contour map of 1E 0657-56 showing entropy-driven lensing centroid displacement.
4. fig8_rar_universal_scatter_landscape.png:
   Universal RAR (g_obs vs g_bar) across 214 points with Monte Carlo observational scatter.
"""

from __future__ import annotations

import os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Headless rendering
import matplotlib.pyplot as plt

from stress_test_solar_system import (
    SOLAR_SYSTEM_BENCHMARKS,
    A0_NOMINAL,
    acceleration_unscreened_naive,
    acceleration_standard_screened,
    acceleration_emrf_geometric_screened,
)
from lensing_engine import (
    SLACS_BENCHMARKS,
    calculate_deflection_angle_profile,
    evaluate_slacs_sample,
)
from bullet_cluster_stress_test import BulletClusterSimulation
from stress_test_galaxy_scatter import compile_master_rar_dataset, evaluate_rar_statistics


def plot_fig5_solar_system_screening(output_path: Path):
    """Plot Fig 5: Solar System multi-decade acceleration and screening boundaries."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True, gridspec_kw={"height_ratios": [1.2, 1.0]})

    r_au = np.logspace(-0.5, 2.3, 300)
    r_m = r_au * 1.495978707e11
    a_newton = (6.67430e-11 * 1.98847e30) / (r_m ** 2)

    a_unscreened = acceleration_unscreened_naive(a_newton, A0_NOMINAL)
    a_screened_std = acceleration_standard_screened(a_newton, A0_NOMINAL)
    a_screened_emrf = acceleration_emrf_geometric_screened(a_newton, A0_NOMINAL)

    # Top panel: Total Acceleration
    ax1.loglog(r_au, a_newton, "k-", lw=2.2, label="GR / Newtonian Baseline")
    ax1.loglog(r_au, a_unscreened, "r--", lw=1.8, label="Unscreened Naive Model (Falsified)")
    ax1.loglog(r_au, a_screened_std, "b:", lw=2.0, label="Standard Screened Model")
    ax1.loglog(r_au, a_screened_emrf, "g-.", lw=2.0, label="EMRF Geometric Screened ($M^D$)")

    # Mark benchmark probes
    for probe in SOLAR_SYSTEM_BENCHMARKS:
        ax1.plot(probe.semi_major_axis_au, probe.newtonian_acceleration, "ko", markersize=5)
        ax1.annotate(
            probe.name.split()[0],
            (probe.semi_major_axis_au, probe.newtonian_acceleration),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
            fontweight="bold",
        )

    ax1.set_ylabel("Orbital Acceleration $a$ [m/s$^2$]", fontsize=11)
    ax1.set_title("Solar System Precision Constraints & Screening Transition", fontsize=13, fontweight="bold")
    ax1.grid(True, which="both", alpha=0.25)
    ax1.legend(loc="upper right", framealpha=0.9)

    # Bottom panel: Anomalous Residual |delta_a| vs Tolerance
    delta_unscreened = np.abs(a_unscreened - a_newton)
    delta_screened_std = np.abs(a_screened_std - a_newton)
    delta_screened_emrf = np.maximum(np.abs(a_screened_emrf - a_newton), 1e-22)

    ax2.loglog(r_au, delta_unscreened, "r--", lw=1.8, label="|$\\Delta a$| Naive Unscreened")
    ax2.loglog(r_au, delta_screened_std, "b:", lw=2.0, label="|$\\Delta a$| Standard Screened")
    ax2.loglog(r_au, delta_screened_emrf, "g-.", lw=2.0, label="|$\\Delta a$| EMRF Geometric Screened")

    # Plot empirical limits
    probe_r = [p.semi_major_axis_au for p in SOLAR_SYSTEM_BENCHMARKS]
    probe_tol = [p.acceleration_tolerance_ms2 for p in SOLAR_SYSTEM_BENCHMARKS]
    ax2.scatter(probe_r, probe_tol, color="darkorange", s=60, zorder=5, label="Empirical $3\\sigma$ Tolerance Limit")

    saturn = next(p for p in SOLAR_SYSTEM_BENCHMARKS if "Saturn" in p.name)
    ax2.annotate(
        "Cassini Limit\n$3.2 \\times 10^{-14}$ m/s$^2$",
        (saturn.semi_major_axis_au, saturn.acceleration_tolerance_ms2),
        textcoords="offset points",
        xytext=(20, -15),
        arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5),
        fontsize=9,
        fontweight="bold",
        color="darkred",
    )

    ax2.set_xlabel("Semi-Major Axis $r$ [AU]", fontsize=11)
    ax2.set_ylabel("Anomalous Acceleration $|\\Delta a|$ [m/s$^2$]", fontsize=11)
    ax2.set_ylim(1e-20, 1e-8)
    ax2.grid(True, which="both", alpha=0.25)
    ax2.legend(loc="lower left", framealpha=0.9)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_fig6_gravitational_lensing(output_path: Path):
    """Plot Fig 6: Relativistic Gravitational Lensing & SLACS Benchmarks."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

    # Left: Deflection profile vs impact parameter
    b_kpc = np.linspace(0.5, 30.0, 200)
    alpha_200 = calculate_deflection_angle_profile(b_kpc, v_circ_kms=200.0, r_core_kpc=1.0)
    alpha_250 = calculate_deflection_angle_profile(b_kpc, v_circ_kms=250.0, r_core_kpc=1.0)
    alpha_300 = calculate_deflection_angle_profile(b_kpc, v_circ_kms=300.0, r_core_kpc=1.0)

    ax1.plot(b_kpc, alpha_200, "b-", lw=2, label="EMRF Potential ($V_c = 200$ km/s)")
    ax1.plot(b_kpc, alpha_250, "g--", lw=2, label="EMRF Potential ($V_c = 250$ km/s)")
    ax1.plot(b_kpc, alpha_300, "r-.", lw=2, label="EMRF Potential ($V_c = 300$ km/s)")

    # Newtonian point mass comparison for M = 1e11 M_sun
    alpha_newton = (4.0 * 6.67430e-11 * 1e11 * 1.98847e30) / (299792458.0**2 * b_kpc * 3.085677581e19) / (np.pi / (180.0 * 3600.0))
    ax1.plot(b_kpc, alpha_newton, "k:", lw=1.8, label="Pure Baryonic Point Mass ($10^{11} M_\\odot$)")

    ax1.set_xlabel("Impact Parameter $b$ [kpc]", fontsize=11)
    ax1.set_ylabel("Deflection Angle $\\hat{\\alpha}(b)$ [arcsec]", fontsize=11)
    ax1.set_title("Relativistic Light Deflection in Compressed Space", fontsize=12, fontweight="bold")
    ax1.set_ylim(0, 3.5)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")

    # Right: SLACS Benchmark Comparison (Observed vs Predicted Einstein Radii)
    evals = evaluate_slacs_sample()
    names = list(evals.keys())
    obs = [evals[n]["theta_obs_arcsec"] for n in names]
    pred = [evals[n]["theta_pred_arcsec"] for n in names]
    err = [next(l.theta_ein_err_arcsec for l in SLACS_BENCHMARKS if l.name == n) for n in names]

    ax2.errorbar(obs, pred, xerr=err, fmt="ro", markersize=8, capsize=4, elinewidth=1.5, label="SLACS Lenses (HST)")
    ideal_line = np.linspace(0.8, 1.4, 100)
    ax2.plot(ideal_line, ideal_line, "k--", lw=1.8, label="1:1 Exact Agreement")

    for n in names:
        ax2.annotate(
            n.split()[1],
            (evals[n]["theta_obs_arcsec"], evals[n]["theta_pred_arcsec"]),
            textcoords="offset points",
            xytext=(8, -5),
            fontsize=9,
        )

    ax2.set_xlabel("Observed Einstein Radius $\\theta_{\\mathrm{Ein, obs}}$ [arcsec]", fontsize=11)
    ax2.set_ylabel("EMRF Predicted Einstein Radius $\\theta_{\\mathrm{Ein, pred}}$ [arcsec]", fontsize=11)
    ax2.set_title("SLACS Survey Strong Lens Benchmark ($N=5$)", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")

    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_fig7_bullet_cluster(output_path: Path):
    """Plot Fig 7: Bullet Cluster 4-Panel 2D Simulation & Entropy Separation."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    sim = BulletClusterSimulation(grid_size_kpc=450.0, resolution=101)

    sigma_gas, sigma_stars, sigma_tot = sim.generate_baryonic_distributions()
    entropy = sim.generate_entropy_field()
    kappa_naive = sim.compute_naive_mond_lensing_convergence()
    kappa_emrf = sim.compute_emrf_entropy_compression_convergence()

    extent = [-450, 450, -450, 450]

    # Panel A: X-ray Gas (85% baryons)
    im0 = axes[0, 0].imshow(sigma_gas, extent=extent, origin="lower", cmap="plasma")
    axes[0, 0].set_title("(a) Collisional X-ray Gas $\\Sigma_{\\mathrm{gas}}$ (85% Baryons)", fontsize=11, fontweight="bold")
    axes[0, 0].set_ylabel("y [kpc]", fontsize=10)
    fig.colorbar(im0, ax=axes[0, 0], shrink=0.8)

    # Panel B: Turbulent Entropy Field S(X,y)
    im1 = axes[0, 1].imshow(entropy, extent=extent, origin="lower", cmap="magma")
    axes[0, 1].set_title("(b) Thermodynamic Entropy $S(X,y)$ (Shock Heated)", fontsize=11, fontweight="bold")
    fig.colorbar(im1, ax=axes[0, 1], shrink=0.8)

    # Panel C: Naive MOND Convergence (Falsified)
    im2 = axes[1, 0].imshow(kappa_naive, extent=extent, origin="lower", cmap="viridis")
    axes[1, 0].set_title("(c) Naive MOND Lensing $\\kappa$ (Peaks Trapped on Gas)", fontsize=11, fontweight="bold")
    axes[1, 0].set_xlabel("x [kpc]", fontsize=10)
    axes[1, 0].set_ylabel("y [kpc]", fontsize=10)
    axes[1, 0].contour(sim.X, sim.Y, kappa_naive, levels=5, colors="white", alpha=0.6)
    fig.colorbar(im2, ax=axes[1, 0], shrink=0.8)

    # Panel D: EMRF Entropy-Coupled Lensing Convergence (Passed)
    im3 = axes[1, 1].imshow(kappa_emrf, extent=extent, origin="lower", cmap="viridis")
    axes[1, 1].set_title("(d) EMRF Entropy-Coupled Lensing $\\kappa$ (Displaced $\\sim 180$ kpc)", fontsize=11, fontweight="bold")
    axes[1, 1].set_xlabel("x [kpc]", fontsize=10)
    axes[1, 1].contour(sim.X, sim.Y, kappa_emrf, levels=5, colors="cyan", alpha=0.8)
    fig.colorbar(im3, ax=axes[1, 1], shrink=0.8)

    # Mark peaks
    axes[1, 1].plot([-260, 240], [0, 0], "r*", markersize=10, label="Collisionless Galaxies")
    axes[1, 1].legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_fig8_rar_scatter(output_path: Path):
    """Plot Fig 8: Universal Radial Acceleration Relation & Scatter Distribution."""
    dataset = compile_master_rar_dataset()
    stats = evaluate_rar_statistics(dataset)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

    g_obs = np.array([r["g_obs_ms2"] for r in dataset])
    g_bar = np.array([r["g_bar_ms2"] for r in dataset])
    morphs = [r["morphology"] for r in dataset]

    # Morphology color coding
    color_map = {
        "IBm": "#1f77b4", "SABm": "#17becf", "Sd": "#2ca02c",
        "Scd": "#8c564b", "Sc": "#ff7f0e", "SBbc": "#d62728", "Sb": "#9467bd"
    }

    for m in set(morphs):
        idx = [i for i, morph in enumerate(morphs) if morph == m]
        ax1.scatter(
            g_bar[idx],
            g_obs[idx],
            c=color_map.get(m, "gray"),
            alpha=0.75,
            s=28,
            label=f"Type {m}",
        )

    # Overplot theoretical lines
    g_line = np.logspace(-14, -8, 200)
    # 1:1 Newtonian line
    ax1.plot(g_line, g_line, "k:", lw=1.5, label="Newtonian $g_{\\mathrm{obs}} = g_{\\mathrm{bar}}$")
    # RAR / EMRF curve
    nu_line = 1.0 / (1.0 - np.exp(-np.sqrt(np.maximum(g_line / A0_NOMINAL, 1e-15))))
    ax1.plot(g_line, g_line * nu_line, "r-", lw=2.2, label="EMRF / RAR Universal Relation")

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("Baryonic Acceleration $g_{\\mathrm{bar}}$ [m/s$^2$]", fontsize=11)
    ax1.set_ylabel("Observed Acceleration $g_{\\mathrm{obs}}$ [m/s$^2$]", fontsize=11)
    ax1.set_title(f"Universal RAR Landscape ($N={len(dataset)}$ Points)", fontsize=12, fontweight="bold")
    ax1.grid(True, which="both", alpha=0.25)
    ax1.legend(loc="lower right", fontsize=8, ncol=2)

    # Right: Residual Histogram
    log_res = np.log10(g_obs) - np.log10(g_bar * (1.0 / (1.0 - np.exp(-np.sqrt(g_bar / A0_NOMINAL)))))
    n, bins, _ = ax2.hist(log_res, bins=25, density=True, color="steelblue", alpha=0.7, edgecolor="black")

    # Gaussian fit overlay
    x_pts = np.linspace(-0.6, 0.6, 200)
    gauss = (1.0 / (stats["std_scatter_dex"] * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x_pts - stats["mean_bias_dex"]) / stats["std_scatter_dex"]) ** 2)
    ax2.plot(x_pts, gauss, "r-", lw=2.2, label=f"Gaussian Fit\n$\\mu = {stats['mean_bias_dex']:+.3f}$ dex\n$\\sigma = {stats['std_scatter_dex']:.3f}$ dex")

    ax2.axvline(0.0, color="black", linestyle="--", lw=1.2)
    ax2.set_xlabel("Log Residual $\\Delta \\log_{10}(g)$ [dex]", fontsize=11)
    ax2.set_ylabel("Probability Density", fontsize=11)
    ax2.set_title("Empirical Residual Scatter Distribution", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def generate_all_deep_perspective_figures(figures_dir: Path | str | None = None):
    """Generate all 4 deep perspective publication figures."""
    if figures_dir is None:
        figures_dir = Path(__file__).resolve().parent.parent / "paper" / "figures"
    else:
        figures_dir = Path(figures_dir)

    figures_dir.mkdir(parents=True, exist_ok=True)

    print("Generating Figure 5: Solar System Precision & Cassini Limits...")
    plot_fig5_solar_system_screening(figures_dir / "fig5_solar_system_screening_limits.png")

    print("Generating Figure 6: Relativistic Gravitational Lensing & Geodesics...")
    plot_fig6_gravitational_lensing(figures_dir / "fig6_gravitational_lensing_geodesics.png")

    print("Generating Figure 7: Bullet Cluster 2D Simulation & Entropy Separation...")
    plot_fig7_bullet_cluster(figures_dir / "fig7_bullet_cluster_entropy_separation.png")

    print("Generating Figure 8: Universal RAR Scatter & Residual Distribution...")
    plot_fig8_rar_scatter(figures_dir / "fig8_rar_universal_scatter_landscape.png")

    print("All 4 deep perspective figures generated successfully in:", figures_dir)


if __name__ == "__main__":
    generate_all_deep_perspective_figures()
