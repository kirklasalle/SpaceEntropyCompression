"""
Quantum Acoustic Qubit Stabilization — Full Pipeline (QuTiP + Differential Evolution) — Script Version

Replicates the functionality of `Quantum_Acoustic_Qubit_QuTiP_Pipeline_FULL_FIXED.ipynb`.

CLI Features:
  * Parameter sweep (including drive phase φ)
  * Heatmap generation for selected φ values
  * Differential evolution optimization with purity regularizer
  * Phase scan at optimized parameters

Usage examples (PowerShell):
  python qubit_pipeline.py --all
  python qubit_pipeline.py --sweep --heatmaps --opt --phi-scan
  python qubit_pipeline.py --opt --opt-maxiter 10 --opt-popsize 10 --seed 42
  python qubit_pipeline.py --sweep --g-list 0.3 0.6 1.2 --phi-list 0 pi/2 pi 3*pi/2

To make a quick smoke test (light optimization):
  python qubit_pipeline.py --opt --opt-maxiter 1 --opt-popsize 4

Outputs directory (default): qutip_full_results_fixed
"""
from __future__ import annotations
import argparse
import math
import os
import json
import csv
import sys
from dataclasses import dataclass
from typing import List, Tuple

try:
    import numpy as np
    import qutip as qt
    import matplotlib.pyplot as plt
    from scipy.optimize import differential_evolution
except ImportError as e:
    print("Missing dependencies:", e)
    print("Install with: pip install qutip numpy matplotlib scipy")
    sys.exit(1)

# --------------------------------------------------------------------------------------
# Parameters & Physical constants
# --------------------------------------------------------------------------------------
OUT_DIR_DEFAULT = "qutip_full_results_fixed"

omega_q = 5.0 * 2*math.pi   # qubit (2π·GHz)
omega_a = 2.0 * 2*math.pi   # acoustic (2π·GHz)
N_a = 12  # Fock truncation

gamma1 = 1.0e-5 * 2*math.pi
gamma_phi = 1.0e-5 * 2*math.pi
kappa_nat = 1.0e-4 * 2*math.pi

k_B = 1.380649e-23
h = 6.62607015e-34
GHz_to_Hz = 1e9
T_K = 0.015

# Unit converters (MHz/kHz to GHz*2π for direct use with Hamiltonian defined in rad/s units)
# We treat input frequency values as MHz or kHz and convert to rad/s consistent with original notebook scaling.
toGHz = lambda MHz: MHz*1e-3*2*math.pi  # MHz -> (2π·GHz)
toGHz_kHz = lambda kHz: kHz*1e-6*2*math.pi  # kHz -> (2π·GHz)

# Drive amplitude scale factor (dimensionless * scale -> frequency units)
eps_scale = 1e-4*2*math.pi

# --------------------------------------------------------------------------------------
# Thermal occupancy
# --------------------------------------------------------------------------------------
def n_thermal(freq_GHz: float, T_K: float) -> float:
    f_hz = freq_GHz * GHz_to_Hz
    x = (h*f_hz)/(k_B*T_K + 1e-300)
    if x > 50:
        return 0.0
    return 1.0/(math.exp(x)-1.0)

n_th = n_thermal(omega_a/(2*math.pi), T_K)

# --------------------------------------------------------------------------------------
# Operators & target state
# --------------------------------------------------------------------------------------
Iq = qt.qeye(2); Ia = qt.qeye(N_a)
sx = qt.sigmax(); sz = qt.sigmaz(); sm = qt.sigmam()
a = qt.destroy(N_a)

sxF = qt.tensor(sx, Ia)
szF = qt.tensor(sz, Ia)
smF = qt.tensor(sm, Ia)
aF  = qt.tensor(Iq, a)
aFd = aF.dag()

ket0 = qt.basis(2,0); ket1 = qt.basis(2,1)
ket_plus = (ket0 + ket1).unit()

# --------------------------------------------------------------------------------------
# Hamiltonian & collapse operators
# --------------------------------------------------------------------------------------

def build_H(g: float, eps: float, delta_a: float, phi: float):
    H0 = 0.5*omega_q*szF + delta_a*(aFd*aF) + 0.5*g*(sxF*(aF + aFd))
    X = (aF + aFd)
    Y = 1j*(aF - aFd)
    H_drive = eps * (math.cos(phi)*X + math.sin(phi)*Y)
    return H0 + H_drive

def build_cops(kappa_eng: float):
    k_tot = kappa_nat + kappa_eng
    C = []
    if gamma1 > 0: C.append(math.sqrt(gamma1)*smF)
    if gamma_phi > 0: C.append(math.sqrt(gamma_phi)*szF)
    if k_tot > 0:
        C.append(math.sqrt(k_tot*(n_th+1))*aF)
        if n_th > 0:
            C.append(math.sqrt(k_tot*n_th)*aFd)
    return C

# --------------------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------------------

def metrics(g: float, eps: float, delta_a: float, kappa_eng: float, phi: float):
    H = build_H(g, eps, delta_a, phi)
    C = build_cops(kappa_eng)
    rho = qt.steadystate(H, C, method='direct')
    rho_q = rho.ptrace(0)
    purity = float((rho_q*rho_q).tr().real)
    P_g = float(rho_q[1,1].real)
    P_e = float(rho_q[0,0].real)
    # Fidelity to |+>: expectation value of projector |+><+|
    # Older QuTiP versions allowed casting 1x1 Qobj directly to float; newer require explicit extraction.
    F_plus_obj = ket_plus.dag() * rho_q * ket_plus  # 1x1 Qobj or complex
    # Support both legacy (Qobj) and newer (complex) return types.
    if hasattr(F_plus_obj, 'full'):
        F_plus_val = F_plus_obj.full()[0,0]
    else:
        F_plus_val = F_plus_obj  # already complex scalar
    F_plus = float((F_plus_val).real)
    return purity, P_g, P_e, F_plus, rho_q

# --------------------------------------------------------------------------------------
# Sweep
# --------------------------------------------------------------------------------------

def run_sweep(out_dir: str,
              g_list: List[float], eps_units: List[float], delta_list: List[float],
              kappa_eng_list: List[float], phi_list: List[float]) -> dict:
    rows = []
    best = {"F_plus": -1, "params": None, "purity": None}
    for gM in g_list:
        for eu in eps_units:
            for dM in delta_list:
                for kk in kappa_eng_list:
                    for phi in phi_list:
                        purity, Pg, Pe, Fp, _ = metrics(toGHz(gM), eu*eps_scale, toGHz(dM), toGHz_kHz(kk), phi)
                        rows.append([gM, eu, dM, kk, phi, purity, Pg, Pe, Fp])
                        if Fp > best["F_plus"]:
                            best = {"F_plus": Fp, "params": (gM, eu, dM, kk, phi), "purity": purity}
    sweep_path = os.path.join(out_dir, "sweep_fidelity_fixed.csv")
    with open(sweep_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["g_MHz","drive_units","delta_MHz","kappa_eng_kHz","phi","purity","P_g","P_e","F_plus"])
        for r in rows:
            w.writerow([f"{r[0]:.3f}", f"{r[1]:.3f}", f"{r[2]:.3f}", f"{r[3]:.3f}", f"{r[4]:.6f}", f"{r[5]:.6f}", f"{r[6]:.6f}", f"{r[7]:.6f}", f"{r[8]:.6f}"])
    return {"best": best, "csv": sweep_path}

# --------------------------------------------------------------------------------------
# Heatmaps
# --------------------------------------------------------------------------------------

def run_heatmaps(out_dir: str, eps_units: List[float], delta_list: List[float],
                 g_fix: float, kk_fix: float, phi_heatmap_list: List[float]):
    for phi in phi_heatmap_list:
        F = np.zeros((len(eps_units), len(delta_list)))
        for i, eu in enumerate(eps_units):
            for j, dM in enumerate(delta_list):
                _,_,_,Fp,_ = metrics(toGHz(g_fix), eu*eps_scale, toGHz(dM), toGHz_kHz(kk_fix), phi)
                F[i,j] = Fp
        plt.figure(figsize=(6,4))
        plt.imshow(F, origin='lower', aspect='auto', extent=[delta_list[0], delta_list[-1], 0, len(eps_units)-1])
        plt.xlabel("Δ_a (MHz)")
        plt.ylabel("Drive index (ε / 1e-4·2π)")
        plt.title(f"F(|+>) heatmap — g≈{g_fix} MHz, κ_eng≈{kk_fix} kHz, φ≈{phi:.2f} rad")
        plt.colorbar(label="F(|+>)")
        plt.tight_layout()
        fname = os.path.join(out_dir, f"heatmap_Fplus_phi_{phi:.2f}.png")
        plt.savefig(fname, dpi=200)
        plt.close()

# --------------------------------------------------------------------------------------
# Optimization
# --------------------------------------------------------------------------------------

def run_optimization(out_dir: str, lam: float, maxiter: int, popsize: int, seed: int | None):
    def objective(x):
        gM, eu, dM, kk, phi = x
        purity, Pg, Pe, Fp, _ = metrics(toGHz(gM), eu*eps_scale, toGHz(dM), toGHz_kHz(kk), phi)
        return 1.0 - Fp + lam*(1.0 - purity)

    bounds = [
        (0.2, 1.5),   # g_MHz
        (0.0, 2.5),   # drive_units
        (-30.0, 30.0),# delta_MHz
        (0.0, 600.0), # kappa_eng_kHz
        (0.0, 2*math.pi) # phi
    ]

    opt = differential_evolution(objective, bounds, maxiter=maxiter, popsize=popsize, tol=1e-4, seed=seed, polish=True)
    gM_opt, eu_opt, dM_opt, kk_opt, phi_opt = opt.x
    pur_opt, Pg_opt, Pe_opt, Fp_opt, _ = metrics(toGHz(gM_opt), eu_opt*eps_scale, toGHz(dM_opt), toGHz_kHz(kk_opt), phi_opt)

    opt_summary = {
        "optimum": {
            "g_MHz": float(gM_opt),
            "drive_units": float(eu_opt),
            "delta_MHz": float(dM_opt),
            "kappa_eng_kHz": float(kk_opt),
            "phi_rad": float(phi_opt),
            "F_plus": float(Fp_opt),
            "purity": float(pur_opt),
            "P_g": float(Pg_opt),
            "P_e": float(Pe_opt)
        }
    }
    path = os.path.join(out_dir, "opt_summary_fixed.json")
    with open(path, "w") as f:
        json.dump(opt_summary, f, indent=2)
    return opt_summary, path

# --------------------------------------------------------------------------------------
# Phase scan
# --------------------------------------------------------------------------------------

def run_phi_scan(out_dir: str, opt_summary: dict, phi_points: int):
    opt = opt_summary["optimum"]
    gM = opt["g_MHz"]; eu = opt["drive_units"]; dM = opt["delta_MHz"]; kk = opt["kappa_eng_kHz"]
    phis = np.linspace(0, 2*math.pi, phi_points)
    Fphi = []
    for p in phis:
        _,_,_,Fp,_ = metrics(toGHz(gM), eu*eps_scale, toGHz(dM), toGHz_kHz(kk), p)
        Fphi.append(Fp)
    plt.figure(figsize=(6,4))
    plt.plot(phis, Fphi, '-o', markersize=3)
    plt.xlabel("φ (rad)")
    plt.ylabel("F(|+>)")
    plt.title("Fidelity vs Drive Phase at Optimized Params")
    plt.tight_layout()
    fname = os.path.join(out_dir, "Fplus_vs_phi_optimized_fixed.png")
    plt.savefig(fname, dpi=200)
    plt.close()
    return fname

# --------------------------------------------------------------------------------------
# Argument parsing
# --------------------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="Quantum Acoustic Qubit Stabilization Pipeline")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Run sweep, heatmaps, optimization, and phi scan (default if none specified)")
    p.add_argument("--sweep", action="store_true", help="Run parameter sweep")
    p.add_argument("--heatmaps", action="store_true", help="Generate heatmaps")
    p.add_argument("--opt", action="store_true", help="Run differential evolution optimization")
    p.add_argument("--phi-scan", action="store_true", help="Run phase scan at optimized parameters")

    p.add_argument("--out-dir", default=OUT_DIR_DEFAULT, help="Output directory")
    p.add_argument("--lam", type=float, default=0.1, help="Purity regularization weight λ")
    p.add_argument("--opt-maxiter", type=int, default=30, help="Max iterations for differential evolution")
    p.add_argument("--opt-popsize", type=int, default=14, help="Population size for differential evolution")
    p.add_argument("--phi-points", type=int, default=121, help="Number of points in phi scan (including 0 and 2π)")
    p.add_argument("--seed", type=int, default=7, help="Random seed for optimizer")

    # Sweep parameter lists
    p.add_argument("--g-list", type=float, nargs="+", default=[0.3, 0.6, 1.2], help="g values (MHz) for sweep")
    p.add_argument("--eps-units", type=float, nargs="+", default=[0.0, 0.5, 1.0, 1.5, 2.0], help="Drive amplitude units for sweep")
    p.add_argument("--delta-list", type=float, nargs="+", default=[-25.0, -10.0, 0.0, 10.0, 25.0], help="Detuning values (MHz) for sweep")
    p.add_argument("--kappa-eng-list", type=float, nargs="+", default=[0.0, 50.0, 200.0, 400.0], help="Engineered kappa values (kHz) for sweep")
    p.add_argument("--phi-list", type=str, nargs="+", default=["0", "pi/2", "pi", "3*pi/2"], help="List of phi expressions for sweep (e.g. 0 pi/2 pi 3*pi/2)")
    p.add_argument("--phi-heatmap-list", type=str, nargs="+", default=["0", "pi/2"], help="Phi values for heatmaps")
    p.add_argument("--g-fix", type=float, default=0.6, help="g (MHz) for heatmaps")
    p.add_argument("--kappa-fix", type=float, default=200.0, help="kappa_eng (kHz) for heatmaps")

    return p

# --------------------------------------------------------------------------------------
# Utility for parsing phi expressions like "pi/2"
# --------------------------------------------------------------------------------------

def parse_phi_expr(expr: str) -> float:
    expr = expr.replace('π', 'pi')
    allowed = {"pi": math.pi}
    return float(eval(expr, {"__builtins__": {}}, allowed))  # controlled eval

# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    run_all = args.all or not any([args.sweep, args.heatmaps, args.opt, args.phi_scan])

    os.makedirs(args.out_dir, exist_ok=True)

    phi_list = [parse_phi_expr(x) for x in args.phi_list]
    phi_heatmap_vals = [parse_phi_expr(x) for x in args.phi_heatmap_list]

    opt_summary = None

    if run_all or args.sweep:
        print("[SWEEP] Starting sweep...")
        sweep_info = run_sweep(args.out_dir, args.g_list, args.eps_units, args.delta_list, args.kappa_eng_list, phi_list)
        best = sweep_info["best"]
        print(f"[SWEEP] Best F_plus={best['F_plus']:.6f} at params (g_MHz, drive_units, delta_MHz, kappa_eng_kHz, phi)={best['params']}")
        print(f"[SWEEP] Purity at best: {best['purity']:.6f}")
    else:
        print("[SWEEP] Skipped")

    if run_all or args.heatmaps:
        print("[HEATMAPS] Generating heatmaps...")
        run_heatmaps(args.out_dir, args.eps_units, args.delta_list, args.g_fix, args.kappa_fix, phi_heatmap_vals)
        print("[HEATMAPS] Saved heatmaps for φ in", phi_heatmap_vals)
    else:
        print("[HEATMAPS] Skipped")

    if run_all or args.opt:
        print("[OPT] Running differential evolution optimization...")
        opt_summary, opt_path = run_optimization(args.out_dir, args.lam, args.opt_maxiter, args.opt_popsize, args.seed)
        print("[OPT] Completed. Optimum summary:")
        print(json.dumps(opt_summary["optimum"], indent=2))
    else:
        print("[OPT] Skipped")
        # Load existing summary if available for phi scan
        possible = os.path.join(args.out_dir, "opt_summary_fixed.json")
        if os.path.exists(possible):
            with open(possible) as f:
                opt_summary = json.load(f)

    if (run_all or args.phi_scan) and opt_summary is not None:
        print("[PHI SCAN] Generating phase scan plot...")
        phi_plot = run_phi_scan(args.out_dir, opt_summary, args.phi_points)
        print("[PHI SCAN] Saved:", phi_plot)
    elif run_all or args.phi_scan:
        print("[PHI SCAN] Skipped (no optimization summary available)")
    else:
        print("[PHI SCAN] Skipped")

    print("Done.")

if __name__ == "__main__":
    main()
