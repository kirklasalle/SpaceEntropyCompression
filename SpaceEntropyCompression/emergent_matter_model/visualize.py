"""2D visualisation client for the Emergent Matter Model server.

Sends a simulation request (2 spatial + 1 entropy = 3 total dimensions)
and displays a heatmap at a chosen entropy slice.
"""

import argparse
import sys
import requests
import numpy as np
import matplotlib.pyplot as plt


def run_simulation(server: str = 'http://127.0.0.1:5000',
                   resolution: int = 50, n_entropy: int = 10,
                   entropy_slice: int = 0):
    n = 3  # 2 spatial dims + 1 entropy dim
    weights = [0.4, 0.4, 0.2]  # last weight is entropy

    x1 = np.linspace(-2, 2, resolution)
    x2 = np.linspace(-2, 2, resolution)
    S = np.linspace(0, 1, n_entropy)   # entropy states

    payload = {
        'n': n,
        'weights': weights,
        'X_grid': [x1.tolist(), x2.tolist(), S.tolist()],
        'k': 1.0,
        'alpha': 1.0,
        'C0': 1.0,
    }

    try:
        r = requests.post(f'{server}/api/v1/simulate', json=payload, timeout=30)
        r.raise_for_status()
    except requests.RequestException as exc:
        print(f"Error contacting server: {exc}", file=sys.stderr)
        sys.exit(1)

    M = np.array(r.json()['M'])

    si = min(entropy_slice, len(S) - 1)
    plt.imshow(M[:, :, si], extent=[-2, 2, -2, 2], origin='lower')
    plt.title(f'Emergent Matter  M(X, S={S[si]:.2f})')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.colorbar(label='M')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='2D heatmap of emergent matter at an entropy slice')
    parser.add_argument('--server', default='http://127.0.0.1:5000',
                        help='Base URL of the simulation server')
    parser.add_argument('--resolution', type=int, default=50,
                        help='Grid points per spatial axis (default: 50)')
    parser.add_argument('--n-entropy', type=int, default=10,
                        help='Number of entropy states (default: 10)')
    parser.add_argument('--entropy-slice', type=int, default=0,
                        help='Which entropy slice to display (default: 0)')
    args = parser.parse_args()
    run_simulation(
        server=args.server,
        resolution=args.resolution,
        n_entropy=args.n_entropy,
        entropy_slice=args.entropy_slice,
    )
