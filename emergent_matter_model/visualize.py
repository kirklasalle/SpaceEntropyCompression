"""2D Visualisation client for Emergent Matter Model on Multidimensional Space M^D.

Foundational Ontology (Clarified by Kirk LaSalle, 2026-10-05):
Spatial coordinates: X = (x_1, x_2, d_0) in M^D.
Thermodynamic entropy S(X,t) is an organizational state functional that modulates
the spatial compression functional C(X,t) into emergent matter density M(X,t).
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import requests

from model import EmergentMatterModel


def run_simulation(
    server: str = "http://127.0.0.1:5000",
    resolution: int = 60,
    d0_value: float = 0.5,
    entropy_val: float = 0.4,
    offline: bool = True,
    save_fig: str | None = None,
):
    """Simulate 2D spatial slice of M^D with extra spatial coordinate d_0 and entropy S."""
    x1 = np.linspace(-2.5, 2.5, resolution)
    x2 = np.linspace(-2.5, 2.5, resolution)

    if not offline:
        payload = {
            "n": 3,
            "weights": [0.45, 0.45, 0.10],
            "X_grid": [x1.tolist(), x2.tolist(), [d0_value]],
            "k": 1.0,
            "alpha": 1.0,
            "C0": 1.0,
        }
        try:
            r = requests.post(f"{server}/api/v1/simulate", json=payload, timeout=10)
            r.raise_for_status()
            M_data = np.array(r.json()["M"])
            M_slice = M_data[:, :, 0]
        except Exception as exc:
            print(f"Server unavailable ({exc}), falling back to direct offline calculation.", file=sys.stderr)
            offline = True

    if offline:
        # Direct local model calculation
        X1, X2 = np.meshgrid(x1, x2)
        r = np.sqrt(X1**2 + X2**2) + 0.1
        c_spatial = (1.0 / r) + 0.3 * np.cos(2.0 * np.pi * d0_value)
        # Entropy modulation
        m_density = (np.maximum(c_spatial, 0.0) ** 1.2) / (1.0 + 0.5 * entropy_val)
        M_slice = m_density

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(M_slice, extent=[-2.5, 2.5, -2.5, 2.5], origin="lower", cmap="inferno")
    ax.set_title(f"Emergent Matter M(X) on Spatial Slice (d_0={d0_value:.2f}, S={entropy_val:.2f})", fontsize=11, fontweight="bold")
    ax.set_xlabel("Spatial Dimension $x_1$", fontsize=10)
    ax.set_ylabel("Spatial Dimension $x_2$", fontsize=10)
    fig.colorbar(im, ax=ax, label="Emergent Matter Density $M(X)$")

    if save_fig:
        out_p = Path(save_fig)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_p, dpi=200)
        print(f"Figure saved to: {out_p}")
    else:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2D Visualisation of Emergent Matter Spatial Slice")
    parser.add_argument("--server", default="http://127.0.0.1:5000", help="Simulation server URL")
    parser.add_argument("--resolution", type=int, default=60, help="Grid points per spatial axis")
    parser.add_argument("--d0", type=float, default=0.5, help="Extra spatial dimension d0 value")
    parser.add_argument("--entropy", type=float, default=0.4, help="Thermodynamic entropy level S")
    parser.add_argument("--offline", action="store_true", default=True, help="Compute locally without server")
    parser.add_argument("--save-fig", type=str, default=None, help="Save figure to path")
    args = parser.parse_args()

    run_simulation(
        server=args.server,
        resolution=args.resolution,
        d0_value=args.d0,
        entropy_val=args.entropy,
        offline=args.offline,
        save_fig=args.save_fig,
    )
