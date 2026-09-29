#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import argparse
import csv
import os
import signal
import sys
from scipy.optimize import differential_evolution

# ===== Global interrupt flag =====
interrupted = False

# ===== Signal handler =====
def sigint_handler(signum, frame):
    global interrupted
    interrupted = True
    print("\n[CTRL-C] Interrupt detected. Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# ===== Example Hamiltonian calculation (stub for real QuTiP code) =====
def compute_fidelity(params, lam, enable_qubit_drive=False, enable_Lx=False):
    g_MHz, drive_units, delta_MHz, kappa_eng_kHz, phi_rad = params
    # Dummy fidelity formula for illustration — replace with real QuTiP computation
    f_plus = 0.5 + 0.001*np.sin(phi_rad)
    purity = 0.99999
    return f_plus, purity

# ===== Differential Evolution optimization =====
def run_optimization(maxiter, popsize, lam, enable_qubit_drive, enable_Lx, log_csv=True):
    bounds = [
        (0.5, 2.0),    # g_MHz
        (0.5, 2.0),    # drive_units
        (0.0, 50.0),   # delta_MHz
        (500.0, 2000.0), # kappa_eng_kHz
        (0.0, 2*np.pi) # phi_rad
    ]

    results = []

    def objective(x):
        if interrupted:
            sys.exit(0)
        f_plus, purity = compute_fidelity(x, lam, enable_qubit_drive, enable_Lx)
        results.append((f_plus, purity))
        return -f_plus  # maximize F+

    print(f"[OPT] Running differential evolution optimization...")
    opt_result = differential_evolution(objective, bounds, maxiter=maxiter, popsize=popsize, polish=True, disp=False)
    x_opt = opt_result.x
    f_plus_opt, purity_opt = compute_fidelity(x_opt, lam, enable_qubit_drive, enable_Lx)

    if log_csv:
        os.makedirs("qutip_pipeline_results", exist_ok=True)
        with open("qutip_pipeline_results/optimization_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["iteration", "F_plus", "purity"])
            for i, (fp, pur) in enumerate(results):
                writer.writerow([i, fp, pur])
        print("[LOG] Optimization trace saved to qutip_pipeline_results/optimization_log.csv")

    return x_opt, f_plus_opt, purity_opt

# ===== Phi scan =====
def phi_scan_plot(x_opt, lam, enable_qubit_drive, enable_Lx):
    phis = np.linspace(0, 2*np.pi, 100)
    f_vals = []
    for phi in phis:
        params = list(x_opt)
        params[-1] = phi
        f_plus, _ = compute_fidelity(params, lam, enable_qubit_drive, enable_Lx)
        f_vals.append(f_plus)
    os.makedirs("qutip_pipeline_results", exist_ok=True)
    plt.plot(phis, f_vals)
    plt.xlabel("phi (rad)")
    plt.ylabel("F_plus")
    plt.title("F_plus vs phi (optimized)")
    plt.savefig("qutip_pipeline_results/Fplus_vs_phi_optimized.png")
    plt.close()
    print("[PHI SCAN] Saved: qutip_pipeline_results/Fplus_vs_phi_optimized.png")

# ===== Main =====
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--opt", action="store_true", help="Run optimization")
        parser.add_argument("--opt-maxiter", type=int, default=30)
        parser.add_argument("--opt-popsize", type=int, default=14)
        parser.add_argument("--phi-scan", action="store_true")
        parser.add_argument("--lam", type=float, default=0.05)
        parser.add_argument("--fast-test", action="store_true")
        parser.add_argument("--enable-qubit-drive", action="store_true")
        parser.add_argument("--enable-Lx", action="store_true")
        args = parser.parse_args()

        print("[ARGS] Parsed arguments:")
        print(vars(args))

        if args.opt:
            x_opt, f_plus_opt, purity_opt = run_optimization(
                args.opt_maxiter, args.opt_popsize, args.lam,
                args.enable_qubit_drive, args.enable_Lx
            )
            print("[OPT] Completed.")
            print({
                "g_MHz": x_opt[0],
                "drive_units": x_opt[1],
                "delta_MHz": x_opt[2],
                "kappa_eng_kHz": x_opt[3],
                "phi_rad": x_opt[4],
                "F_plus": f_plus_opt,
                "purity": purity_opt,
                "P_g": 0.99999,
                "P_e": 1e-5
            })

            if args.phi_scan:
                phi_scan_plot(x_opt, args.lam, args.enable_qubit_drive, args.enable_Lx)

    except KeyboardInterrupt:
        print("\n[MAIN] Keyboard interrupt — exiting.")
        sys.exit(0)
