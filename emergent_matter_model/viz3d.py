"""3D Visualization for Emergent Matter Model on Multidimensional Space M^D.

Foundational Ontology (Clarified by Kirk LaSalle, 2026-10-05):
Space is multidimensional: X = (x, y, z, d_0) in M^D.
Neither entropy (S) nor coordinate time (t) is a spatial coordinate axis.
Entropy S(X,t) is an organizational thermodynamic scalar field coupling into
the compression functional C(X,t) = F(E, S, geom, t).

Generates interactive 3D spatial compression manifolds and isosurfaces.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import plotly.graph_objects as go


def generate_multidimensional_compression_figure(
    resolution: int = 35,
    d0_slice: float = 0.5,
    entropy_amplitude: float = 1.0,
    percentile: float = 88.0,
) -> go.Figure:
    """Generate interactive 3D spatial visualization of compressed space M^D under entropy field."""
    x = np.linspace(-2.5, 2.5, resolution)
    y = np.linspace(-2.5, 2.5, resolution)
    z = np.linspace(-2.5, 2.5, resolution)

    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    r = np.sqrt(X**2 + Y**2 + Z**2) + 1e-6

    # 4D spatial compression: 3D macro-space (x,y,z) + compactified spatial dimension d_0
    # C(X) = (1/r) + 0.3 * cos(2 * pi * d0_slice)
    c_spatial = (1.0 / (r + 0.4)) + 0.35 * np.cos(2.0 * np.pi * d0_slice)

    # Thermodynamic entropy organizational field S(X): increases with disorder/turbulence
    s_field = entropy_amplitude * (0.2 + 0.8 * (r / np.max(r)) ** 2)

    # Emergent matter density: M(X) = [C(X)]^alpha / (1 + beta * S(X))
    m_density = (np.maximum(c_spatial, 0.0) ** 1.5) / (1.0 + 0.5 * s_field)

    # Filter high-density voxels for 3D scatter
    thresh = np.percentile(m_density, percentile)
    mask = m_density >= thresh

    xs = X[mask]
    ys = Y[mask]
    zs = Z[mask]
    vals = m_density[mask]

    fig = go.Figure()

    # 3D Point Cloud of Compressed Spatial Fabric
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers",
        marker=dict(
            size=4.5,
            color=vals,
            colorscale="Plasma",
            opacity=0.75,
            colorbar=dict(title="Emergent Density $M(X)$"),
        ),
        name="Compressed Space Voxels",
    ))

    # Add central mass concentration marker
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers",
        marker=dict(size=12, color="white", symbol="diamond"),
        name="Compression Core (r=0)",
    ))

    fig.update_layout(
        title=f"Multidimensional Spatial Compression M^D [d_0 = {d0_slice:.2f}, S_amp = {entropy_amplitude:.2f}]",
        scene=dict(
            xaxis_title="Spatial Dimension x",
            yaxis_title="Spatial Dimension y",
            zaxis_title="Spatial Dimension z",
            bgcolor="#111116",
        ),
        paper_bgcolor="#111116",
        font=dict(color="#E0E0E0"),
    )
    return fig


def demo_3d(
    resolution: int = 35,
    d0_slice: float = 0.5,
    entropy_amplitude: float = 1.0,
    percentile: float = 88.0,
    html_out: str | Path | None = None,
):
    """Run 3D visualization and optionally export to standalone HTML."""
    fig = generate_multidimensional_compression_figure(
        resolution=resolution,
        d0_slice=d0_slice,
        entropy_amplitude=entropy_amplitude,
        percentile=percentile,
    )

    if html_out:
        out_path = Path(html_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(out_path))
        print(f"Interactive 3D visualization saved to: {out_path}")
    else:
        fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D Visualization of Multidimensional Space M^D")
    parser.add_argument("--resolution", type=int, default=35, help="Grid points per spatial axis")
    parser.add_argument("--d0", type=float, default=0.5, help="Extra spatial coordinate d0 value (0 to 1)")
    parser.add_argument("--entropy", type=float, default=1.0, help="Thermodynamic entropy field amplitude")
    parser.add_argument("--percentile", type=float, default=88.0, help="Density percentile threshold")
    parser.add_argument("--html-out", type=str, default=None, help="Path to write standalone HTML file")
    args = parser.parse_args()

    demo_3d(
        resolution=args.resolution,
        d0_slice=args.d0,
        entropy_amplitude=args.entropy,
        percentile=args.percentile,
        html_out=args.html_out,
    )
