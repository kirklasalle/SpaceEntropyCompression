# `data/synthetic/`: SYNTHETIC FIXTURES, NOT OBSERVATIONS

**Everything in this folder is synthetic.** These tables were generated during development, most likely as placeholders during AI-assisted coding. Earlier versions of the repository labelled them with real instrument names (GRAVITY, NACO, SINFONI, JWST NIRSpec, ALMA) and real paper citations. That labelling was wrong.

The independent audit in [`docs/SHOW_YOUR_WORK.md`](../../docs/SHOW_YOUR_WORK.md) proves that they can't be real measurements. For example:

* `astrometry/s301_synthetic.csv` implies on-sky motion faster than light, and contains radial velocities that the S301 discovery paper (Nature 2026) says haven't been measured yet.
* `astrometry/s2_synthetic.csv` puts two pericentre passages one period apart 59 mas apart on the sky.
* `sparc/*.csv` don't match the SPARC database (and NGC 1560 isn't in SPARC at all).
* `jwst_kinematics_synthetic.csv` paired real object names with wrong redshifts or nonexistent rotation measurements. The names have been replaced with `SYN-Z01` … `SYN-Z10`.
* `cosmology/sn_hubble_diagram_synthetic.csv` has a χ² probability of 2×10⁻⁷ against a smooth fit (no statistical scatter).
* `cosmology/cmb_tt_peaks_synthetic.csv` contains the same peak heights that are hard-coded in the CMB template.

## Rules

1. **Never cite these files, or results computed from them, as scientific evidence.**
2. They are kept only so the existing unit tests and demonstrations still run. Any pipeline that reads them prints a `SYNTHETIC INPUT DATA` banner (see [`emergent_matter_model/data_provenance.py`](../../emergent_matter_model/data_provenance.py)).
3. Every file starts with a `# SYNTHETIC DATA` header. Keep it if you copy a file.

## Where the real data are

| Domain | Real source | How it's used in this repository |
|---|---|---|
| Galaxy rotation curves | SPARC, Lelli, McGaugh & Schombert (2016), AJ 152, 157, <https://astroweb.case.edu/SPARC/> | Downloaded on demand by `emergent_matter_model/fetch_real_data.py`; analysed in `emergent_matter_model/sparc_real_analysis.py` |
| BAO distances | DESI DR1, arXiv:2404.03002 Table 1 | `data/cosmology/desi_2024_bao.csv` (official values, verified) |
| S-star astrometry | Gillessen et al. (2017) ApJ 837, 30; GRAVITY Collaboration releases; S301: GRAVITY Collaboration (2026), Nature / arXiv:2607.12664 (astrometry only) | Not yet ingested |
| Type Ia supernovae | Pantheon+ official data release (Scolnic et al. 2022; Brout et al. 2022) | Not yet ingested |
| CMB TT spectrum | Planck Legacy Archive, `COM_PowerSpect_CMB-TT-binned_R3.01.txt` | Not yet ingested |
| High-z rotation curves | Requires a documented compilation with per-object references | Not yet ingested |
