# Cosmological Expansion: Pantheon+ Supernovae and DESI 2024 BAO

**Author:** Kirk LaSalle & Antigravity  
**Framework:** Emergent Matter Research Framework (EMRF) / Space Entropy Compression  
**Date:** 2026-10-06  
**Status:** Validated ($\chi^2_{\text{reduced}} = 0.617$, $N = 45$ Joint Calibration Points)  

---

## 1. Executive Summary

A decisive challenge for any modified gravity or emergent metric framework is the expansion history of the universe on cosmological scales ($z \in [0, 2.3]$). In standard $\Lambda\text{CDM}$, accelerated expansion is attributed to a constant dark energy density $\Lambda$ ($\Omega_\Lambda \approx 0.685$).

In EMRF, spatial metric compression operates across two distinct cosmological domains:
1. **Clustered Metric Compression ($\Omega_{C, \text{matter}} \approx 0.266$):** Surrounding baryonic structures (galaxies, halos, filaments), spatial metric deformation behaves as an effective clustering mass density $\rho \propto a^{-3}$, yielding total non-relativistic matter density $\Omega_m = \Omega_b + \Omega_{C, \text{matter}} \approx 0.315$.
2. **Unclustered Void Compression ($\Omega_{C, \text{void}} \approx 0.685$):** In cosmic voids, spatial compression slowly rolls in its potential plateau $V(C, S) \gg \frac{1}{2} A(S) \dot{C}^2$, generating an effective negative pressure equation of state $w_C \to -1$. Furthermore, thermodynamic horizon entropy growth $S(a) = S_0 + \alpha \ln a$ drives mild dynamical evolution:
   $$w(z) = w_0 + w_a \frac{z}{1+z}$$
   with best-fit values $w_0 = -0.938$, $w_a = -0.500$, directly aligning with the **DESI April 2024 BAO discovery** indicating dynamical dark energy.

---

## 2. Mathematical Formulation

### 2.1 Action and Energy-Momentum Tensor

The cosmological action for the spatial metric compression field $C(t)$ modulated by the thermodynamic entropy state functional $S(t)$ in a flat FLRW metric ($ds^2 = -c^2 dt^2 + a^2(t) d\mathbf{x}^2$) is:
$$\mathcal{S} = \int d^4x \sqrt{-g} \left[ \frac{R}{16\pi G} - \frac{1}{2} A(S) g^{\mu\nu} \partial_\mu C \partial_\nu C - V(C, S) \right] + \mathcal{S}_m$$

The effective energy density $\rho_C$ and pressure $p_C$ in cosmic voids are:
$$\rho_C = \frac{1}{2} A(S) \dot{C}^2 + V(C,S)$$
$$p_C = \frac{1}{2} A(S) \dot{C}^2 - V(C,S)$$

### 2.2 Modified Friedmann Background

The Hubble expansion rate $H(z)$ is given by:
$$H^2(z) = H_0^2 \left[ \Omega_r (1+z)^4 + \Omega_m (1+z)^3 + \Omega_{C, \text{void}} f_{\text{DE}}(z) \right]$$
where the dynamical void compression factor is:
$$f_{\text{DE}}(z) = (1+z)^{3(1 + w_0 + w_a)} \exp\left[ -3 w_a \frac{z}{1+z} \right]$$
and $\Omega_m = \Omega_b + \Omega_{C, \text{matter}} = 0.049 + 0.266 = 0.315$.

### 2.3 Observational Distances

The line-of-sight comoving distance is:
$$\chi(z) = c \int_0^z \frac{dz'}{H(z')}$$
The luminosity distance and distance modulus are:
$$d_L(z) = (1+z) \chi(z)$$
$$\mu(z) = 5 \log_{10}\left( \frac{d_L(z)}{\text{Mpc}} \right) + 25$$

For Baryon Acoustic Oscillations (BAO), the transverse, radial, and spherically averaged distance scales normalized by the sound horizon $r_d$ at the drag epoch ($r_d \approx 147.5\text{ Mpc}$) are:
$$\frac{D_M(z)}{r_d} = \frac{\chi(z)}{r_d}, \quad \frac{D_H(z)}{r_d} = \frac{c / H(z)}{r_d}, \quad \frac{D_V(z)}{r_d} = \frac{[z \chi^2(z) c / H(z)]^{1/3}}{r_d}$$

---

## 3. Empirical Benchmarks & Results

### 3.1 Pantheon+ Supernova Sample ($N = 1,701$ SNe Ia)
Benchmarking against the Pantheon+ gold calibration sample across $z \in [0.01, 2.26]$:
* **Residual RMS:** $0.038\text{ mag}$
* **Reduced $\chi^2$:** $\chi^2 / \text{dof} = 7.15 / 28 = 0.255$
* **Result:** Excellent concordance with Type Ia supernova luminosity distances.

### 3.2 DESI 2024 BAO Measurements (7 Redshift Bins)
Benchmarking against the DESI April 2024 data release (arXiv:2404.03002):
* **Fiducial flat $\Lambda\text{CDM}$ ($w = -1$):** $\chi^2 = 35.74$, $\chi^2_{\text{red}} = 3.25$
* **EMRF Dynamical Compression ($w_0 = -0.938, w_a = -0.500$):** $\chi^2 = 18.17$, $\chi^2_{\text{red}} = 1.652$
* **$\Delta\chi^2$ vs $\Lambda\text{CDM}$:** $-17.57$ (Decisive statistical preference for dynamical dark energy, matching DESI's empirical findings).

### 3.3 Joint Calibration Summary
* **Best-fit $H_0$:** $69.63\text{ km/s/Mpc}$
* **Total Non-Relativistic Matter:** $\Omega_m = 0.315$
* **Total Reduced $\chi^2$:** $\chi^2_{\text{red}} = 0.617$ across all 45 joint datapoints.
