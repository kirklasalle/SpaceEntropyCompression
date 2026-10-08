# Multi-Messenger Gravitational Wave Speed & GW170817 Invariance in EMRF

> **Integrity notice (2026-10-07).** This document predates the independent audit in [`docs/SHOW_YOUR_WORK.md`](../docs/SHOW_YOUR_WORK.md). Empirical results quoted here (for example S-star ΔBIC = +70.743 or +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ observational constraints") were computed from synthetic data files (now quarantined in [`data/synthetic/`](../data/synthetic/README.md)) or from code whose answer was built in, so they **must not be cited**. "100/100" or "all gates passed" audit scores in earlier documents did not detect these problems. Current real-data results: [`knowledgebase/action_principle_derivation.md`](action_principle_derivation.md) §4.3.


**Author:** Kirk LaSalle & EMRF Collaboration  
**Date:** 2026-10-05  
**Version:** 1.0.0  
**Target Module:** `emergent_matter_model/stress_test_gw_speed.py`

---

## 1. The Multi-Messenger Gravitational Wave Speed Constraint

On August 17, 2017, the Advanced LIGO and Virgo detectors observed the inspiral and merger of two neutron stars (GW170817). Just 1.74 seconds later, the Fermi Gamma-ray Burst Monitor (Fermi-GBM) detected short gamma-ray burst GRB 170817A originating from the same source galaxy (NGC 4993, at a distance of $D \approx 40\text{ Mpc}$).

Propagating over 130 million light-years, this multi-messenger detection bounded the fractional speed difference between gravitational waves ($c_{\text{gw}}$) and electromagnetic radiation ($c$) to:
$$-3.0 \times 10^{-15} \le \frac{c_{\text{gw}} - c}{c} \le +7.0 \times 10^{-16}$$

### Why This Destroyed Other Modified Gravity Theories:
In many modified gravity formulations (such as quartic/quintic Horndeski, covariant Galileons, and TeVeS with disformal vector fields), the scalar or vector fields induce an effective metric for tensor perturbations:
$$\tilde{g}^{\mu\nu} = g^{\mu\nu} + D(\phi) \partial^\mu \phi \partial^\nu \phi$$
This disformal metric changes the gravitational wave speed ($c_{\text{gw}} \neq c$), typically by parts in $10^{-3}$ to $10^{-2}$. GW170817 instantly eliminated these models because they predicted arrival time differences of months to thousands of years.

---

## 2. EMRF Conformal Light Cone Invariance on $\mathcal{M}^D$

In Kirk LaSalle's foundational ontology:
1. Space is strictly multidimensional: $X = (x, y, z, d_0) \in \mathcal{M}^D$.
2. The spatial compression functional $C(X,t)$ affects the geometry conformally rather than disformally:
$$g_{\mu\nu}(X,t) = \Omega^2(X,t) \, \eta_{\mu\nu}$$
where $\Omega(X,t) = 1 + \Phi(X,t)/c^2$.

### Mathematical Proof of $c_{\text{gw}} \equiv c$:
Under a conformal transformation $g_{\mu\nu} = \Omega^2 \eta_{\mu\nu}$, the null cone condition is invariant:
$$ds^2 = g_{\mu\nu} dx^\mu dx^\nu = \Omega^2 \eta_{\mu\nu} dx^\mu dx^\nu = 0 \iff \eta_{\mu\nu} dx^\mu dx^\nu = 0$$
The wave equation for transverse-traceless tensor perturbations $h_{ij}$ in the EMRF metric satisfies:
$$\square_g h_{ij} = \frac{1}{\sqrt{-g}} \partial_\mu \left( \sqrt{-g} g^{\mu\nu} \partial_\nu h_{ij} \right) = 0$$
Expanding the d'Alembertian:
$$\left( \frac{1}{c^2} \frac{\partial^2}{\partial t^2} - \nabla^2_{(D)} \right) h_{ij} + \mathcal{O}(\partial \ln \Omega) \partial h_{ij} = 0$$
In the high-frequency eikonal approximation ($k \gg |\nabla \ln \Omega|$), the dispersion relation is:
$$\omega^2 - c^2 k^2 = 0 \implies v_{\text{phase}} = \frac{\omega}{k} = c, \quad v_{\text{group}} = \frac{d\omega}{dk} = c$$
Therefore:
$$\frac{c_{\text{gw}} - c}{c} \equiv 0.0000000000000000$$

**Conclusion:** EMRF naturally and fundamentally preserves the speed of light for gravitational waves, surviving the GW170817 multi-messenger test with zero empirical violation.
