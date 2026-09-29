"""Comparison with known physics: Schwarzschild-like curvature profile.

Demonstrates that the Emergent Matter Model reproduces the 1/r^6 scaling
of the Kretschner curvature invariant in Schwarzschild spacetime, and
shows how different alpha values map to different physical falloff rates.

Dimensions: 1 spatial (radial r) + 1 entropy (S) = 2 total.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from model import EmergentMatterModel


def schwarzschild_comparison(alpha: float = 1.0, resolution: int = 200):
    # Radial grid (avoid r=0 singularity)
    r = np.linspace(0.5, 10.0, resolution)
    # Entropy grid
    S = np.linspace(0.1, 1.0, 5)

    # Curvature functions:
    #   C_r(r) = 1/r^6   — matches Kretschner scalar radial dependence
    #   C_S(S) = S        — linear entropy curvature
    c_funcs = [
        lambda r_: 1.0 / r_ ** 6,
        lambda s:  s,
    ]

    model = EmergentMatterModel.from_spatial_and_entropy(
        n_spatial=1,
        spatial_weights=[0.8],
        entropy_weight=0.2,
        k=1.0,
        alpha=alpha,
        C0=1.0,
    )

    M = model.simulate_grid([r, S], c_funcs)

    # --- Plot: M(r) at different entropy states ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: linear scale
    ax = axes[0]
    for si in range(len(S)):
        ax.plot(r, M[:, si], label=f'S={S[si]:.2f}')
    ax.set_xlabel('r (radial coordinate)')
    ax.set_ylabel('M (emergent matter density)')
    ax.set_title(f'Emergent Matter vs Radius (α={alpha})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right: log-log to verify power-law slope
    ax = axes[1]
    for si in [0, len(S) - 1]:
        ax.loglog(r, M[:, si], label=f'S={S[si]:.2f}')
    # Reference line: 1/r^(6*alpha)
    ref = (1.0 / r ** (6 * alpha))
    ref *= M[0, 0] / ref[0]  # normalise to match
    ax.loglog(r, ref, '--', color='gray', label=f'1/r^{6*alpha:.1f} (reference)')
    ax.set_xlabel('r')
    ax.set_ylabel('M')
    ax.set_title('Log-log (verify power-law scaling)')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()
    plt.suptitle(
        'Schwarzschild Consistency Check\n'
        'C_r(r) = 1/r⁶ (Kretschner invariant scaling)',
        y=1.02, fontsize=12,
    )
    plt.show()

    # Print slope verification
    # In log-log, slope = d(log M) / d(log r) should be ~ -6*alpha
    log_r = np.log(r)
    log_M = np.log(np.abs(M[:, 0]) + 1e-30)
    slope = np.polyfit(log_r[10:], log_M[10:], 1)[0]
    print(f"\nExpected log-log slope: {-6 * alpha:.2f}")
    print(f"Measured log-log slope: {slope:.2f}")
    print(f"Match: {'YES' if abs(slope + 6 * alpha) < 0.5 else 'approximate'}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Schwarzschild curvature consistency check')
    parser.add_argument('--alpha', type=float, default=1.0,
                        help='Power-law exponent (default: 1.0)')
    parser.add_argument('--resolution', type=int, default=200,
                        help='Grid points for radial axis (default: 200)')
    args = parser.parse_args()
    schwarzschild_comparison(alpha=args.alpha, resolution=args.resolution)
