# 3D Visualisation Usage

## Quick Start

Activate your environment and run:

```
python viz3d.py
```

This generates a 3D scatter (Plotly) of high-value emergent matter voxels at a
chosen entropy state S.  The model uses 4 total dimensions: 3 spatial (x, y, z)
plus 1 entropy (S) — entropy is the dimensional expression of what was
conventionally called time.

## Customization

- Adjust spatial grids in `viz3d.py` (x, y, z resolution)
- Adjust the entropy grid `S` to explore different entropy states
- Modify `c_funcs` — one curvature function per dimension (single argument).
  The 4th function is the entropy curvature \( C_S(S) \).
- Change `thresh` percentile for density of points
- Use `M[..., i]` to pick different entropy slices for visualisation

## Roadmap

- Add entropy slider (multi-entropy-state animation)
- Isosurface extraction (e.g., marching cubes via scikit-image)
- Volume rendering (e.g., vtk or k3d)
- Interactive comparison across entropy slices

## Dependencies

Plotly is already listed in `requirements.txt`.
