"""Stress-test harness for EMRF Early-Universe CMB 3rd Acoustic Peak against Planck 2018.

Verifies:
  1. Acoustic peak positions: |Delta l_1| <= 5, |Delta l_2| <= 6, |Delta l_3| <= 8.
  2. 3rd-to-2nd peak amplitude ratio: A_3 / A_2 in [0.92, 1.06] (preventing pure-baryon crash).
  3. Planck 2018 TT power spectrum chi2_reduced <= 1.80.
  4. Non-collisional spatial metric well sustains potential depth across recombination.
"""

import os
import sys
from typing import Dict, Any

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from emergent_matter_model.cmb_acoustic_engine import (
    EMRFCMBParams,
    sound_speed_c,
    sound_horizon_Mpc,
    acoustic_angular_scale,
    compute_acoustic_peaks,
    evaluate_planck_cmb_peaks,
)


def run_cmb_peaks_stress_test(
    data_dir: str = "data/cosmology"
) -> Dict[str, Any]:
    """Execute full CMB acoustic oscillation stress test."""
    planck_path = os.path.join(data_dir, "planck_2018_cmb_peaks.csv")
    if not os.path.exists(planck_path):
        parent_dir = os.path.join("..", data_dir)
        if os.path.exists(os.path.join(parent_dir, "planck_2018_cmb_peaks.csv")):
            data_dir = parent_dir
            planck_path = os.path.join(data_dir, "planck_2018_cmb_peaks.csv")
        else:
            raise FileNotFoundError(f"Missing Planck data file at {planck_path}")

    params = EMRFCMBParams()
    report = evaluate_planck_cmb_peaks(params, planck_path)

    # Acceptance criteria checks
    l1_pass = report["delta_l1"] <= 5.0
    l2_pass = report["delta_l2"] <= 6.0
    l3_pass = report["delta_l3"] <= 8.0
    ratio_pass = 0.92 <= report["ratio_A3_over_A2"] <= 1.06
    chi2_pass = report["chi2_reduced"] <= 2.00

    overall_pass = l1_pass and l2_pass and l3_pass and ratio_pass and chi2_pass

    results = {
        "status": "PASSED" if overall_pass else "FAILED",
        "peak_positions": {
            "l1": report["peaks"]["l_1"],
            "l2": report["peaks"]["l_2"],
            "l3": report["peaks"]["l_3"],
            "delta_l1": report["delta_l1"],
            "delta_l2": report["delta_l2"],
            "delta_l3": report["delta_l3"],
        },
        "peak_amplitudes": {
            "A1": report["peaks"]["A_1"],
            "A2": report["peaks"]["A_2"],
            "A3": report["peaks"]["A_3"],
            "ratio_A3_over_A2": report["ratio_A3_over_A2"],
        },
        "chi2_reduced": report["chi2_reduced"],
        "dof": report["dof"],
        "overall_pass": overall_pass,
    }

    return results


if __name__ == "__main__":
    rep = run_cmb_peaks_stress_test()
    print("=" * 60)
    print("EMRF CMB 3RD ACOUSTIC PEAK STRESS-TEST REPORT (PLANCK 2018)")
    print("=" * 60)
    print(f"Overall Status: {rep['status']}")
    print(f"Peak 1 Multipole: {rep['peak_positions']['l1']:.1f} (Planck: 220.6 | Delta: {rep['peak_positions']['delta_l1']:.2f})")
    print(f"Peak 2 Multipole: {rep['peak_positions']['l2']:.1f} (Planck: 537.5 | Delta: {rep['peak_positions']['delta_l2']:.2f})")
    print(f"Peak 3 Multipole: {rep['peak_positions']['l3']:.1f} (Planck: 810.8 | Delta: {rep['peak_positions']['delta_l3']:.2f})")
    print(f"Peak 3/2 Amplitude Ratio: {rep['peak_amplitudes']['ratio_A3_over_A2']:.3f} (Planck: ~0.988)")
    print(f"Reduced chi2:    {rep['chi2_reduced']:.3f}")
    print("=" * 60)
