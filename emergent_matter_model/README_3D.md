# 3D Visualisation Usage

## Quick Start

Activate your environment and run:

```
python viz3d.py
```

This generates a 3D scatter (Plotly) of high-value emergent matter voxels.
The model uses 4 total dimensions: 3 spatial (x, y, z) and evaluates at 
varying entropy states S. Entropy is a thermodynamic state field (the arrow), 
not a spatial coordinate.

## Customization

- Adjust spatial grids in `viz3d.py` (x, y, z resolution)
- Adjust the entropy state grid `S` to explore different thermodynamic states
- Modify `c_funcs` — one curvature function per dimension (single argument).
  The first three are spatial; the 4th is entropy coupling \( C_S(S) \).
- Ensure \( C_S(S) \) is monotonically non-decreasing (Second Law)
- Change `thresh` percentile for density of points
- Use `M[..., i]` to visualise different entropy state slices

## Roadmap

- Add entropy state slider (animate across entropy sweep)
- Isosurface extraction (e.g., marching cubes via scikit-image)
- Volume rendering (e.g., vtk or k3d)
- Interactive comparison across entropy states

## Dependencies

Plotly is already listed in `requirements.txt`.
