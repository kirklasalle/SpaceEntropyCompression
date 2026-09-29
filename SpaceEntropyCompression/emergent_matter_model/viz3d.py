import argparse
import numpy as np
import plotly.graph_objects as go
from model import EmergentMatterModel

"""3D visualisation for Emergent Matter Model (space + entropy).

Generates a 3D scatter of high-value voxels at a chosen entropy state.
The model has 4 total dimensions: 3 spatial (x, y, z) + 1 entropy (S).
"""


def demo_3d(resolution: int = 40, n_entropy: int = 5, percentile: float = 92.0,
            entropy_slice: int = 0):
    # Spatial grids
    x = np.linspace(-2, 2, resolution)
    y = np.linspace(-2, 2, resolution)
    z = np.linspace(-2, 2, resolution)

    # Entropy grid — the dimensional expression of what was once called t.
    S = np.linspace(0, 1, n_entropy)

    # Curvature component functions — one per dimension (single argument).
    # The 4th function is the entropy-curvature C_S(S).
    c_funcs = [
        lambda x_: np.sin(x_),              # C_x
        lambda y_: np.cos(y_),              # C_y
        lambda z_: 0.5 * z_ ** 2,           # C_z
        lambda s:  s,                        # C_S  (linear entropy curvature)
    ]

    model = EmergentMatterModel.from_spatial_and_entropy(
        n_spatial=3,
        spatial_weights=[0.3, 0.4, 0.3],
        entropy_weight=0.2,
        k=1.0, alpha=1.0, C0=1.0,
    )

    # M has shape (Nx, Ny, Nz, Ns) — 4-D grid
    M = model.simulate_grid_vectorized_3d([x, y, z, S], c_funcs)

    # Pick the requested entropy slice for visualisation
    si = min(entropy_slice, len(S) - 1)
    M_slice = M[..., si]

    # Threshold for high-value scatter
    thresh = np.percentile(M_slice, percentile)
    xs, ys, zs = np.where(M_slice >= thresh)
    xs = x[xs]
    ys = y[ys]
    zs = z[zs]
    vals = M_slice[M_slice >= thresh]

    fig = go.Figure(data=[go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers',
        marker=dict(size=4, color=vals, colorscale='Viridis', opacity=0.7,
                    colorbar=dict(title='M'))
    )])
    fig.update_layout(
        title=f'Emergent Matter High-Value Voxels (S={S[si]:.2f})',
        scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'),
    )
    fig.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='3D visualisation of emergent matter at an entropy slice')
    parser.add_argument('--resolution', type=int, default=40,
                        help='Grid points per spatial axis (default: 40)')
    parser.add_argument('--n-entropy', type=int, default=5,
                        help='Number of entropy states (default: 5)')
    parser.add_argument('--percentile', type=float, default=92.0,
                        help='Percentile threshold for scatter (default: 92)')
    parser.add_argument('--entropy-slice', type=int, default=0,
                        help='Which entropy slice to display (default: 0)')
    args = parser.parse_args()
    demo_3d(
        resolution=args.resolution,
        n_entropy=args.n_entropy,
        percentile=args.percentile,
        entropy_slice=args.entropy_slice,
    )
