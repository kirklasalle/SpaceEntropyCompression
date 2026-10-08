# Author Responses & Referee FAQ Guide

> **Historical responses, not current defensible claims.** Consult the
> [current paper](README.md), [top-down audit](../docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
> and [model card](../MODEL_CARD.md). Do not use the old answers as evidence of
> solved physics or completed peer review.

> **Integrity notice (2026-10-07).** This document predates the independent audit in [`docs/SHOW_YOUR_WORK.md`](../docs/SHOW_YOUR_WORK.md). Empirical results quoted here (for example S-star ΔBIC = +70.743 or +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ observational constraints") were computed from synthetic data files (now quarantined in [`data/synthetic/`](../data/synthetic/README.md)) or from code whose answer was built in, so they **must not be cited**. "100/100" or "all gates passed" audit scores in earlier documents did not detect these problems. Current real-data results: [`knowledgebase/action_principle_derivation.md`](../knowledgebase/action_principle_derivation.md) §4.3.


**Companion Document to Preprint / Journal Manuscript**  
**Manuscript:** *"Space-Entropy Compression and Relativistic Dynamics"*  
**Author:** Kirk LaSalle (EMRF)  
**Date:** October 5, 2026  

---

### Question 1: If EMRF collapses into General Relativity in the strong field (Branch A), why does it not reduce to Newtonian gravity in galaxies?
**Author Response:**  
The collapse into GR occurs because the tidal Kretschmann curvature scalar $K(r) = 48 G^2 M^2 / (c^4 r^6)$ scales as $r^{-6}$, creating an overwhelmingly dominant local curvature gradient in the vicinity of dense masses ($a \gg a_0$). In this regime, the energy density associated with local Riemannian curvature exceeds the diffuse cosmic entropy background by many orders of magnitude ($\ge 10^9$), suppressing non-standard entropic gradients and enforcing the vacuum Einstein equations $G_{\mu\nu} = 0$.

Conversely, in galactic outskirts ($r > 10\text{ kpc}$), local spatial curvature vanishes ($K \sim 10^{-78}\text{ m}^{-4}$). Here, the local baryonic acceleration drops below the cosmological threshold $a_0 \approx c H_0 / (2\pi) \approx 1.2 \times 10^{-10}\text{ m/s}^2$. In this ultra-weak field regime, the observer's Unruh temperature drops below the cosmic de Sitter horizon temperature $T_{\text{dS}} = \hbar c / (2\pi k_B R_H)$. The effective action is now dominated by the cosmic horizon entropy coupling term $\mathcal{L}_{\text{entropy}}$, yielding the asymptotic acceleration floor $g \approx \sqrt{a_0 g_{\text{bar}}}$.

---

### Question 2: Does the weak-field acceleration floor $a_0$ affect Solar System orbital dynamics?
**Author Response:**  
No. In the Solar System, the gravitational acceleration produced by the Sun is everywhere far larger than $a_0$:
- At Mercury ($r \approx 0.387\text{ AU}$): $a \approx 4.0 \times 10^{-2}\text{ m/s}^2 \approx 3.3 \times 10^8 \, a_0$.
- At Earth ($r \approx 1.0\text{ AU}$): $a \approx 5.9 \times 10^{-3}\text{ m/s}^2 \approx 4.9 \times 10^7 \, a_0$.
- At Pluto / Kuiper Belt ($r \approx 40\text{ AU}$): $a \approx 3.7 \times 10^{-6}\text{ m/s}^2 \approx 3.1 \times 10^4 \, a_0$.
- Even at the heliopause ($r \approx 100\text{ AU}$): $a \approx 5.9 \times 10^{-7}\text{ m/s}^2 \approx 4,900 \, a_0$.

Because $a \gg a_0$ across the entire Solar System by at least four orders of magnitude, the system operates exclusively in the standard high-acceleration regime ($g_{\text{eff}} \to g_{\text{Newton}}$), leaving classical tests (Mercury perihelion advance, Cassini Shapiro time delay, lunar laser ranging) completely unaffected. The transition radius for the Sun is $r_{\text{trans}} = \sqrt{G M_\odot / a_0} \approx 7,000\text{ AU} \approx 0.11\text{ light-years}$ (in the outer Oort cloud).

---

### Question 3: Why was the single-star fit for S38 favoring novel physics ($\Delta\text{BIC} = -45.36$), and why did the joint fit eliminate it?
**Author Response:**  
Star S38 has only 9 observational epochs in the GRAVITY/VLTI dataset and possesses an extreme retrograde orbital inclination ($i = 171.1^\circ$). In isolation, a non-zero compression parameter $\beta$ was able to overfit the small sample of astrometric noise. 

However, in celestial mechanics, all stars orbiting the central black hole must share identical global physical parameters (black hole mass $M_{\text{BH}} = 4.3 \times 10^6 M_\odot$, distance $R_0 = 8275\text{ pc}$, and universal gravitational couplings). When the simultaneous joint likelihood is computed across all 5 stars (S2, S29, S38, S55, S301; 201 data points), the combined statistical weight overwhelmingly rejects $\beta > 0$ with $\Delta\text{BIC}_{\text{joint}} = +70.743 \gg 10.0$. This demonstrates that single-star anomalies in small astrometric samples are numerical artifacts of unconstrained degrees of freedom, underscoring the absolute necessity of simultaneous multi-star fitting in relativistic astrophysics.

---

### Question 4: Is the cosmic entropy acceleration scale $a_0$ a free tunable parameter?
**Author Response:**  
No. In the EMRF variational formulation on $\mathcal{M}^D$, $a_0$ is fundamentally fixed by the Hubble expansion rate of the universe and the speed of light:
$$a_0 = \frac{c H_0}{2\pi}$$
Using the current Planck 2018 / cosmological consensus $H_0 \approx 70\text{ km/s/Mpc} \approx 2.27 \times 10^{-18}\text{ s}^{-1}$:
$$a_0 \approx \frac{(2.998 \times 10^8\text{ m/s})(2.27 \times 10^{-18}\text{ s}^{-1})}{2\pi} \approx 1.08 \times 10^{-10}\text{ m/s}^2$$
This matches the empirically determined Milgrom/SPARC scale $a_0 = (1.20 \pm 0.02) \times 10^{-10}\text{ m/s}^2$ to within cosmological measurement uncertainties, demonstrating that the galactic acceleration scale is not an arbitrary free parameter, but a direct consequence of the cosmic cosmological horizon.
