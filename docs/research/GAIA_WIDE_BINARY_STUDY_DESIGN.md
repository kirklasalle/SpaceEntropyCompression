# Gaia wide-binary independent-study design

## Status

- **Stage:** method-qualified preregistration
- **Outcome computation:** not started
- **Preregistration:** frozen in `research/preregistrations/gaia_wide_binary_v1.json`
- **Evidence class if completed:** prospective independent-survey test with known published outcomes

This document selects and qualifies the observational source for the next
scientific increment. It is not a prediction commitment and must not be cited
as an EMRF result.

## Why this source

The SPARC quality-3 analysis was a lower-quality holdout from the same
catalogue. A stronger next test must use observations independent in instrument,
scale and reduction. Three candidates were reviewed:

1. THINGS/LITTLE THINGS rotation curves map directly onto the existing galaxy
   fitter, but THINGS is a major source for SPARC and several galaxies overlap.
2. DES-SN5YR is already managed, but it tests the existing flat-LCDM distance
   baseline rather than a derived EMRF observable and shares low-redshift
   supernovae with Pantheon+.
3. Gaia wide binaries probe stellar dynamics at kAU scales using astrometry,
   independently of the H I/Hα galaxy observations in SPARC.

The Gaia route is selected. It is observationally independent of SPARC, but it
is not blind: Chae (2023) published an anomaly from these data, and that result
was known before this design was written.

## Authoritative sources

- Chae (2023), *The Astrophysical Journal* 952, 128,
  DOI [`10.3847/1538-4357/ace101`](https://doi.org/10.3847/1538-4357/ace101),
  revised preprint [`arXiv:2305.04613v4`](https://arxiv.org/abs/2305.04613v4).
- Chae analysis materials and 200 pc Gaia DR3 sample,
  DOI [`10.5281/zenodo.8270396`](https://doi.org/10.5281/zenodo.8270396).
- Source catalogue: El-Badry, Rix & Heintz (2021), MNRAS 506, 2269,
  DOI [`10.1093/mnras/stab323`](https://doi.org/10.1093/mnras/stab323),
  archive [`10.5281/zenodo.4435257`](https://doi.org/10.5281/zenodo.4435257).

Zenodo record `8270396` is open access under CC BY 4.0. Twelve exact holdings
are pinned in the curated and packaged data catalogs: the 46,642,671-byte
observational CSV, revised README and three revised analysis files, the
Newtonian-control generator, and six mass–magnitude relation tables. The
managed library contains and verifies every holding. The 1.42 GB base EDR3
catalogue and the provided virtual Newtonian CSV are intentionally excluded;
the bounded study uses the published derivative observations and must generate
its own deterministic controls.

## What is already scientifically known

The revised paper reports Monte Carlo deprojection of sky-projected separation
and proper-motion velocity, calibration of unresolved multiplicity in a
high-acceleration control regime, and comparison of kinematic acceleration
`g = v²/r` with Newtonian acceleration `g_N = GM/r²`. Its revision notes minor
corrections to figures and an equation. Those published claims are prior
knowledge, not outcomes newly discovered by EMRF.

The repository's current `stress_test_wide_binaries.py` is not an observational
analysis of the archived catalogue. It evaluates four hard-coded illustrative
bins with a phenomenological external-field formula. It therefore cannot serve
as the confirmatory implementation or as the source of acceptance thresholds.

## Preregistered design

The outcome-blind method qualification reproduced the 19,716-row frozen
population and its ordered identifier hash from the exact 46,642,671-byte
catalogue. It also qualified deterministic orbital deprojection and explicitly
classified the external-field expression as a phenomenological comparator,
not a first-principles EMRF prediction.

The immutable contract freezes open acceleration bins at `[-11.5, -9.8,
-8.5, -7.5]`, a primary unresolved-multiplicity fraction of 0.5 with 0.3 and
0.7 sensitivity runs, 2,048 paired deterministic bootstrap/Monte Carlo
realizations, locally generated Newtonian controls, a low-acceleration primary
statistic, comparator values, 95 percent interval decisions, and fail-closed
convergence gates. No observational analyzer existed when these choices were
frozen.

## Gates before outcome execution

No observational outcome may be computed until all of these gates pass:

1. **Immutable commitment:** verify the exact preregistration against its named
   metadata-only prediction commitment.
2. **Independent review:** merge the qualification, contract, and commitment
   to protected `main` before adding any observational outcome implementation.
3. **Protected execution:** implement only after the commitment merges, then
   execute from exact protected `main` with retained complete-or-failed
   evidence.

## Evidence limits

A successful study would be an independent-survey test relative to SPARC, not
an independent discovery of the published Gaia anomaly. Selection effects,
chance alignments, unresolved multiples, stellar mass calibration,
deprojection and the Galactic external-field model remain material
systematics. Disagreement may reject the declared EMRF implementation without
establishing Newtonian gravity; agreement may establish consistency only under
the frozen analysis design.

## Operational note

No physical off-site backup destination exists as of 2026-10-12. The Gaia
holdings are content-addressed and locally verified, but this does not satisfy
the 3-2-1 requirement. Local recovery certification must continue until an
operator supplies an independent destination.
