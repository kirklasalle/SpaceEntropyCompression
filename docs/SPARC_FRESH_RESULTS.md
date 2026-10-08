## Fresh computed results

All acceleration scales below are in 10^-10 m/s².
Grid minima are not continuous maximum-likelihood estimates. Intervals are conditional
ΔQ = 1 grid crossings, not calibrated significance intervals.

| Sample | Galaxies / points | Grid minimum | ΔQ=1 interval | Descriptive reduced χ² |
|---|---:|---:|---|---:|
| all | 153 / 3168 | 1.250 | 1.222 to 1.256 | 4.842 |
| gas dominated | 66 / 966 | 1.000 | 0.979 to 1.062 | 2.617 |
| star bulgeless | 56 / 1070 | 0.900 | 0.884 to 0.909 | 4.375 |
| star bulge | 31 / 1132 | 1.900 | 1.849 to 1.967 | 6.574 |
| star bulge deep | 25 / 305 | 1.600 | 1.543 to 1.692 | 3.903 |
| star bulgeless deep | 50 / 614 | 0.850 | 0.801 to 0.871 | 1.815 |

### Fixed stellar reference (distances/inclinations fixed)

- emrf_sqrt: a₀ = 1.5888; data χ² = 137768.92.
- rar_exponential: a₀ = 1.2216; data χ² = 126216.65.
- simple: a₀ = 1.1827; data χ² = 125461.34.
- standard: a₀ = 1.7715; data χ² = 155383.15.

### Fixed-horizon objective differences

These ΔQ values include nuisance penalties; they are not ΔBIC or discovery significances.
- Planck base LCDM: a₀,H = 1.04220 ± 0.00773 from quoted external H₀ uncertainty ([source](https://arxiv.org/abs/1807.06209)).
- SH0ES Cepheid-SN: a₀,H = 1.12941 ± 0.01608 from quoted external H₀ uncertainty ([source](https://arxiv.org/abs/2112.04510)).
The grid comparisons use the historical rounded SH0ES reference 73.0, not 73.04. These external errors are propagated separately, not integrated into a joint SPARC likelihood or used to claim a detection significance.
- all: {'67.4': 107.32388133661334, '73.0': 27.06239494086367} (H₀ in km/s/Mpc).
- gas_dominated: {'67.4': 0.14368183870374196, '73.0': 5.384920975979185} (H₀ in km/s/Mpc).
- star_bulgeless: {'67.4': 32.92269627795122, '73.0': 74.56722516021819} (H₀ in km/s/Mpc).
- star_bulge: {'67.4': 438.74475723321575, '73.0': 311.5975028179264} (H₀ in km/s/Mpc).

### Robustness checks

- upsilon_0.4: grid minimum 1.200; descriptive reduced χ² 4.864; grid-edge minimum: False (edge minima are not resolved estimates).
- upsilon_0.6: grid minimum 1.250; descriptive reduced χ² 4.835; grid-edge minimum: False (edge minima are not resolved estimates).
- bulge_ratio_0.75: grid minimum 1.000; descriptive reduced χ² 6.994; grid-edge minimum: False (edge minima are not resolved estimates).
- bulge_ratio_2.0: grid minimum 2.950; descriptive reduced χ² 7.530; grid-edge minimum: False (edge minima are not resolved estimates).
- free_bulge_post_hoc: grid minimum 1.300; descriptive reduced χ² 5.317; grid-edge minimum: False (edge minima are not resolved estimates).
- quality_1: grid minimum 1.250; descriptive reduced χ² 4.594; grid-edge minimum: False (edge minima are not resolved estimates).
- inclination_40_to_80: grid minimum 1.150; descriptive reduced χ² 4.527; grid-edge minimum: False (edge minima are not resolved estimates).

### Independently checked single-galaxy influence

Removing **UGC06787** changes the deep-bulge sample's grid optimum from **1.60 to 0.90**. An independent full-grid refit of the remaining 24 galaxies / 287 observed points reproduces the subtraction result.
This is an exploratory influence diagnostic, not a reason to discard that galaxy. It prevents describing the deep-bulge excess as a robust population discovery.

### Other-law nuisance profiles

Same observed sample and nuisance constraints; these are not unpenalized BIC fits.
- emrf_sqrt: a₀ grid minimum 1.600; Q = 16065.100; descriptive reduced χ² 5.338; grid edge False.
- simple: a₀ grid minimum 1.300; Q = 14754.321; descriptive reduced χ² 4.884; grid edge False.
- standard: a₀ grid minimum 1.600; Q = 17674.596; descriptive reduced χ² 5.901; grid edge False.
- all leave-one-galaxy-out grid range: [1.2000000000000006, 1.3000000000000007].
- gas_dominated leave-one-galaxy-out grid range: [0.9500000000000004, 1.0500000000000005].
- star_bulgeless leave-one-galaxy-out grid range: [0.8500000000000003, 0.9500000000000004].
- star_bulge leave-one-galaxy-out grid range: [1.8000000000000012, 2.0500000000000016].
- star_bulge_deep leave-one-galaxy-out grid range: [0.9000000000000004, 1.750000000000001].
- star_bulgeless_deep leave-one-galaxy-out grid range: [0.8000000000000003, 0.8500000000000003].
- Maximum forward/reverse total-objective difference: 4.74029e-09.
- Scan-order differences below 0.1 objective units: True. If false, intervals need additional numerical refinement.

A scan-direction check tests numerical consistency, not statistical coverage.
No full Bayesian marginalization, raw tracking-data fit or
calibrated discovery significance is supplied. External H₀ uncertainty is not integrated
into these profiles; the horizon comparisons are conditional on reference H₀ values.

Source SHA-256: `0b01abdbd8a7e2cc9ec68a2713fad12016d4be951b796460cadd48cd76b81bcc`.
