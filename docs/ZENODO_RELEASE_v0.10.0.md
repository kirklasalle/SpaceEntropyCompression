# Publishing the v0.10.0 correction release on Zenodo

> **Superseded instructions: do not execute this historical release checklist
> as a current publication procedure.** The current repository work is not a new
> tagged release. Citation/Zenodo metadata now separates `main` from the historical
> DOI. Consult [current status](../STATUS.md) and the
> [model card](../MODEL_CARD.md); any new release or deposit needs an explicit
> version/scope decision. Historical suggested descriptions below are not current
> validated claims.

> **Historical release instructions:** subsequent statistical review distinguishes penalized profiling from marginalization and does not certify the historical significance/BIC claims. Review the [new research draft](SPARC_HORIZON_TEST_PAPER.md) and [reproducibility/release-staging guide](REAL_DATA_REPRODUCIBILITY.md) before publishing anything. No release upload or external submission has been performed by the current task.

The earlier Zenodo record (DOI [10.5281/zenodo.23197308](https://doi.org/10.5281/zenodo.23197308)) contains results that have since been withdrawn. Publishing v0.10.0 as a **new version of the same record** keeps the history intact and points readers to the correction. Zenodo doesn't delete earlier versions; new versions are linked under the same "concept" DOI and the newest one is shown first.

## Steps (about 10 minutes)

1. **Push the commits** (the local `main` is ahead of GitHub):
   ```powershell
   git push origin main
   ```
2. **Create a GitHub release** at <https://github.com/kirklasalle/SpaceEntropyCompression/releases/new>:
   * Tag: `v0.10.0` (target `main`)
   * Title: `v0.10.0: Integrity correction and real-data test of a0 = cH0/2pi`
   * Description: paste the text in the next section.
3. **Check Zenodo.** If the GitHub–Zenodo integration is enabled for this repository (the `.zenodo.json` file suggests it is), Zenodo archives the release automatically within a few minutes as a new version. Open the record and confirm the description and version number.
4. **If nothing appears on Zenodo:** open the existing record, click **"New version"**, upload the release archive, paste the same description, and publish.
5. **Optional but recommended:** in the *old* version's description on Zenodo, add one line at the top: "Superseded by v0.10.0; its empirical results are withdrawn — see the correction statement in the newer version." (Zenodo allows editing metadata of published versions.)

## Release description (paste as-is)

> **v0.10.0: Integrity correction and real-data test of a₀ = cH₀/2π**
>
> **Correction.** An independent audit (`docs/SHOW_YOUR_WORK.md`, reproducible with `tools/show_your_work_audit.py`) found that earlier versions reported results computed from synthetic data files labelled as real observations. Several "stress tests" also returned answers written into the code. All of those results are **withdrawn**: S-star ΔBIC = +70.743 / +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ constraints", earlier audit scores, and the claim that the framework derives the Schwarzschild metric. The synthetic files are kept, clearly labelled, in `data/synthetic/`.
>
> **New real-data results** (SPARC rotation curves, 153 galaxies, checksummed public data):
> * The law g = √(g_N² + a₀g_N) used in earlier versions is disfavoured by galaxies and by Solar System bounds.
> * With distances and inclinations marginalized, the hypothesis a₀ = cH₀/2π is **neither confirmed nor excluded**. Gas-dominated galaxies agree with it; the full sample sits 2–4σ above it.
> * The excess comes from galaxies with bulges (5.4σ), and no plausible stellar mass-to-light ratio removes it. This points to galaxy-specific systematics or a non-universal a₀.
> * Bulgeless galaxies prefer a₀ ≈ 0.93 ± 0.04 ×10⁻¹⁰ m/s², below cH₀/2π. Overall, a₀ is systematics-limited at ±15–20%.
>
> Every number can be reproduced with the scripts listed in `README.md`. The revised paper is `paper/main.tex`.
