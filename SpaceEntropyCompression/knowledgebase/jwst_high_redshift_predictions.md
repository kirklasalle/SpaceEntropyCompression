# EMRF Cosmological Redshift Evolution & JWST High-Redshift Kinematic Predictions

**Emergent Matter Research Framework (EMRF) Theoretical Whitepaper**  
**Author:** Kirk LaSalle  
**Date:** 2026-10-05  
**Domain:** Cosmology & Extragalactic Kinematics  

---

## 1. Cosmological Derivation of Redshift-Dependent Acceleration Floor

In the EMRF variational formulation on $\mathcal{M}^{D,1}$ (see [action_principle_derivation.md](action_principle_derivation.md)), the critical weak-field acceleration scale $a_0$ is fundamentally dictated by the Gibbons-Hawking thermodynamic temperature of the cosmic de Sitter horizon:

$$T_{\text{dS}}(t) = \frac{\hbar c}{2\pi k_B R_H(t)} = \frac{\hbar H(t)}{2\pi k_B}$$

$$a_0(t) = \frac{2\pi c k_B T_{\text{dS}}(t)}{\hbar} = \frac{c H(t)}{2\pi}$$

In an expanding Friedmann-Lemaître-Robertson-Walker (FLRW) universe with matter density parameter $\Omega_m$ and dark energy density parameter $\Omega_\Lambda$, the Hubble parameter evolves with redshift $z$ according to the Friedmann equation:

$$H(z) = H_0 \sqrt{\Omega_m (1+z)^3 + \Omega_r (1+z)^4 + \Omega_k (1+z)^2 + \Omega_\Lambda}$$

Assuming standard spatial flatness ($\Omega_k = 0$) and negligible radiation at $z < 10$ ($\Omega_r \ll \Omega_m$):

$$H(z) = H_0 \sqrt{\Omega_m (1+z)^3 + \Omega_\Lambda}$$

Consequently, the EMRF cosmic horizon acceleration floor is **not a static universal constant across cosmic time**, but evolves deterministically with cosmological epoch:

$$a_0(z) = a_0(0) \cdot E(z) = a_0(0) \sqrt{\Omega_m (1+z)^3 + \Omega_\Lambda}$$

where $a_0(0) \approx 1.20 \times 10^{-10}\text{ m/s}^2$ and $E(z) \equiv H(z)/H_0$.

---

## 2. Quantitative Evolution Across Cosmic Epochs

Adopting the Planck 2018 cosmological parameters ($H_0 = 67.4\text{ km/s/Mpc}$, $\Omega_m = 0.315$, $\Omega_\Lambda = 0.685$):

| Redshift $z$ | Lookback Time (Gyr) | Expansion Factor $E(z) = H(z)/H_0$ | $a_0(z)$ ($\text{m/s}^2$) | Acceleration Ratio $a_0(z)/a_0(0)$ |
|:---:|:---:|:---:|:---:|:---:|
| **$0.0$ (Present)** | 0.00 | 1.000 | $1.20 \times 10^{-10}$ | $1.000$ |
| **$0.5$** | 5.12 | 1.323 | $1.59 \times 10^{-10}$ | $1.323$ |
| **$1.0$** | 7.93 | 1.790 | $2.15 \times 10^{-10}$ | $1.790$ |
| **$2.0$** | 10.51 | 3.031 | $3.64 \times 10^{-10}$ | $3.031$ |
| **$3.0$** | 11.66 | 4.568 | $5.48 \times 10^{-10}$ | $4.568$ |
| **$4.0$** | 12.24 | 6.338 | $7.61 \times 10^{-10}$ | $6.338$ |
| **$5.0$** | 12.60 | 8.307 | $9.97 \times 10^{-10}$ | $8.307$ |
| **$6.0$** | 12.83 | 10.450 | $1.25 \times 10^{-9}$  | $10.450$ |

At the epoch observed by the James Webb Space Telescope (JWST) for early disk galaxies ($z \sim 2 - 6$), the effective entropic acceleration floor is **3 to 10 times higher** than in the local universe.

---

## 3. Explicit Falsifiable Predictions for JWST Galaxy Kinematics

### 3.1 Baryonic Tully-Fisher Relation (BTFR) Evolution
In the deep entropic regime ($g \ll a_0$), circular velocity is asymptotically flat:
$$V_{\text{flat}}(z) = \big[ G M_{\text{bar}} a_0(z) \big]^{1/4} = V_{\text{flat}}(0) \cdot \big[ E(z) \big]^{1/4}$$

1. **Velocity Offset at Fixed Baryonic Mass:**  
   A disk galaxy of baryonic mass $M_{\text{bar}} = 10^{10} M_\odot$ at $z = 2$ will exhibit a flat rotation speed:
   $$V_{\text{flat}}(z=2) = (3.031)^{1/4} \cdot V_{\text{flat}}(z=0) \approx 1.320 \cdot V_{\text{flat}}(0)$$
   **Prediction:** High-redshift disk galaxies rotate approximately **$32\%$ faster at $z=2$** and **$59\%$ faster at $z=4$** than local galaxies of identical baryonic mass.

2. **Zero-Point BTFR Shift:**  
   Expressed in logarithmic luminosity/mass coordinates:
   $$\log M_{\text{bar}} = 4 \log V_{\text{flat}} - \log G - \log a_0(z)$$
   $$\Delta \log M_{\text{bar}}(z) = -\log_{10} \big( E(z) \big)$$
   **Prediction:** The zero-point of the BTFR shifts downward by $-0.48\text{ dex}$ at $z=2$ and by $-0.80\text{ dex}$ at $z=4$.

### 3.2 Transition Radius Contraction
The transition radius $r_{\text{trans}}$ separating the inner Newtonian regime from the outer entropic flat-curve regime contracts:
$$r_{\text{trans}}(z) = \sqrt{\frac{G M}{a_0(z)}} = \frac{r_{\text{trans}}(0)}{\sqrt{E(z)}}$$

**Prediction:** At $z=2$, the transition radius is reduced by a factor of $1/\sqrt{3.03} \approx 0.57$. Early galaxies transition into flat rotation curves much closer to their baryonic cores ($r \sim 1 - 3\text{ kpc}$ instead of $5 - 10\text{ kpc}$), matching recent JWST NIRSpec observations of surprisingly dynamically mature, flat rotation curves at early cosmic times.

---

## 4. Testability Against Ongoing JWST Surveys

This prediction is directly testable using:
- **JWST NIRSpec Integral Field Spectroscopy (IFS):** Resolving [O III] $\lambda 5007$ and H$\alpha$ velocity fields in $z = 1 - 7$ disk candidates (e.g. JADES, CEERS, and TEMPLATES surveys).
- **ALMA [C II] $158\,\mu\text{m}$ Kinematics:** Sub-millimeter dynamical observations of cold gas disks at $z > 4$.

If high-redshift disk galaxies exhibit flat rotation velocities strictly consistent with a static $a_0(0)$ without the $[E(z)]^{1/4}$ scaling, the de Sitter horizon entropy coupling hypothesis would be definitively falsified. Conversely, confirming this $(1+z)$-dependent velocity boost provides profound evidence that the galactic acceleration scale is governed by cosmic horizon thermodynamics.
