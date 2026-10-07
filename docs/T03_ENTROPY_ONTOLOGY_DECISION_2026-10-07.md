# T03 Decision Record: Entropy Ontology

**Date:** 2026-10-07  
**Decision owner:** Kirk LaSalle (Principal Investigator)  
**Roadmap task:** [T03 - Resolving the entropy ontology](./REFEREE_ACTION_ROADMAP_2026-10-07.md)  
**Status:** Decided. Formal dynamics are open and are carried into T04.

## Decision

Entropy $S(X,t)$ is a **thermodynamic state field** over the spatial degrees of freedom. It is **the arrow**: the direction of physical change is the direction in which entropy is generated. Its generation and action have field implications, and it couples into the compression functional.

Entropy is **not**:

- a spatial coordinate axis of the manifold $X = (x, y, z, d_0, d_1, d_2, \dots)$;
- a replacement for time, or "the clock". Time $t$ parameterizes change; entropy gives that change its direction.

In words of the principal investigator (2026-10-07): *"entropy is still the arrow. Its generation and action have field implications."*

## Source record

| Date | Source | Statement |
|---|---|---|
| Original dialogue | [GPT Discussion - the start of it all](./GPT%20Discussion%20-%20the%20start%20of%20it%20all.txt) | "with thermodynamics ... we're talking about change, entropy ... going from one state to another ... time is observed as matter changing, and that is within that compression." Thermodynamics is described as a residual output and expression of compression, and "thermodynamics and entropy is part of the theorem as an expression and an effect." |
| 2026-10-05 | [Master audit, author clarification](./EMRF_MASTER_AUDIT_2026-10-05.md) | Space is dimensional ($x, y, z, d_0, d_1, d_2$); neither entropy nor time is a spatial coordinate. Earlier AI-introduced wording ("entropy IS the clock", entropy as an $(n+1)$-th dimension) was a misinterpretation. |
| 2026-10-07 | This record | Entropy is a thermodynamic state field, and it remains the arrow. Its generation and action carry field implications. |

These statements are consistent: change is observed in time; entropy generation orients that change; entropy is a state of the compressed system, not an axis of space.

## Working definitions

These definitions fix meaning only. They are not a derivation and do not establish that the model describes nature.

| Quantity | Meaning | Units | Status |
|---|---|---|---|
| $X$ | Spatial coordinates $(x, y, z, d_0, \dots)$ | length (extra-dimension units open) | Defined; extra dimensions not yet specified physically |
| $t$ | Parameter of change | s | Defined |
| $S(X,t)$ | Thermodynamic entropy state (field; per-volume density $s$ where needed) | J/K (density: J K$^{-1}$ m$^{-3}$) | Defined; which entropy (thermal, horizon, information) depends on regime |
| $\sigma(X,t)$ | Local entropy generation (production) rate | J K$^{-1}$ m$^{-3}$ s$^{-1}$ | Defined by the balance below |
| $C(X,t)$ | Effective compression functional $\mathcal{F}(E, S, \text{geometry}, t)$ | dimensionless after normalization by $C_0$ | Phenomenological |

**The arrow.** In the standard local balance form,

$$\partial_t s + \nabla \cdot \mathbf{J}_S = \sigma, \qquad \sigma \ge 0,$$

the arrow of change is the orientation of $t$ for which $\sigma \ge 0$ (the Second Law). For an isolated system, total entropy is non-decreasing. This is the established thermodynamic meaning of "entropy is the arrow"; adopting it does not add a new physical claim.

**Transformation behavior.** $S$ is a scalar state quantity. It is not transformed as a coordinate. A fully relativistic treatment would use an entropy current $s^\mu$ with $\nabla_\mu s^\mu \ge 0$; that formulation is not yet implemented or derived in this project (see open items).

**Coupling.** In the current phenomenological model, entropy enters the compression functional through a weighted term $w_S\, C_S(S)$. How $\sigma$ (generation) and $\mathbf{J}_S$ (flux) feed back into compression is a field implication of this decision that has not yet been derived.

## Consequences for the software

The current implementation in [`emergent_matter_model/model.py`](../emergent_matter_model/model.py) evaluates $C = \sum_i w_i C_i(x_i) + w_S C_S(S)$ over a grid. The last grid entry is a **set of entropy state values** to sweep, not a spatial axis. Accordingly:

- The API (`n_total`, `X_grid`, `from_spatial_and_entropy`) is unchanged for backward compatibility. The last element is documented as the entropy state, not a coordinate.
- Each output slice `M[..., j]` is the matter field at entropy state $S_j$. Ordering slices by increasing $S$ follows the arrow only for an isolated system; the simulator does not evolve $S$ in time and does not compute $\sigma$.
- Documentation describing entropy as a dimension, coordinate axis, or clock has been corrected.

## Open items carried into T04

1. Specify which entropy applies in each regime (thermal, horizon/Bekenstein-Hawking, information) and how they combine.
2. Write the entropy balance (or covariant current $s^\mu$) as part of the model's equations, including the source $\sigma$ and its relation to compression.
3. Derive, rather than assume, the form of the coupling $C_S(S)$, and whether compression depends on $S$, on $\sigma$, or on both.
4. State the conditions under which the entropy coupling becomes negligible and the model reduces to GR.
5. Implement time evolution of $S(X,t)$ with a check that $\sigma \ge 0$, if the derivation supports it.

Until these are complete, entropy-dependent results in this project remain phenomenological.
