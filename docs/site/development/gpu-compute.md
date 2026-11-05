# GPU computation and Candidate A validation

## Resource and environment record (2026-11-04)

The local accelerator is an **NVIDIA GeForce GTX 1050 Ti**, compute capability
6.1 (Pascal), with **4096 MiB dedicated VRAM** and driver **582.78**.
The operator reports **32 GB system RAM** and Windows shared GPU memory of up
to **16 GB**. Shared memory is host RAM, not additional dedicated VRAM: do not
budget this as a 20 GB CUDA device or assume device-speed spillover.

The verified command-line environment is:

| Component | Observed version |
|---|---|
| Interpreter | `emergent_matter_model\.venv\Scripts\python.exe`, Python 3.10.0 |
| NumPy / SciPy | 2.2.6 / 1.15.3 |
| CuPy distribution | `cupy-cuda12x` 14.2.0 |
| CUDA toolkit Python distribution | 12.9.2.0 |
| CUDA runtime / NVRTC distributions | 12.9.79 / 12.9.86 |
| CUDA runtime API version | 12090 |

This is not a claim about the editor-selected interpreter or other machines.
On recheck, a float64 device reduction of `arange(10)**2` returned 285.0.
Available memory varies with display and other processes; it is not a fixed
4096 MiB allocation budget. Use one device process, bounded batches and no
automatic CPU fallback. Do not change clocks, power limits or other workloads.

## Optional installation

GPU support is optional; the ordinary CPU installation and CPU tests must not
import CuPy. From the repository root in PowerShell:

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip install -e ".\emergent_matter_model[gpu]"
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip check
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,compute_cap --format=csv
& .\emergent_matter_model\.venv\Scripts\python.exe -c "import cupy as c; x=c.arange(10,dtype=c.float64); print(float((x*x).sum())); print(c.cuda.runtime.runtimeGetVersion())"
```

The `gpu` extra pins the tested CuPy CUDA-12 distribution, including its toolkit
extra. Do not substitute CUDA 13 or another CuPy distribution without checking
Pascal compatibility and repeating validation. Do not install competing `cupy`
and `cupy-cuda*` distributions in the same environment. Record the resolved
versions with each run; the extra is not a lockfile for the entire environment.

CuPy currently warns that `CUDA_PATH` was not detected. Device execution still
works with the pip-provided runtime. Do not suppress errors or point
`CUDA_PATH` at a guessed directory. If device execution fails, stop and diagnose
the installed runtime/driver. The earlier installer shell reported exit 1 with
insufficient retained output to establish its cause; subsequent import and
kernel execution establish that installation succeeded, not why that shell
returned 1. Preserve stderr and the native exit status in future checks.

## Scientific and numerical safeguards

The authoritative protocol is
[`candidate_a_option3_reconstruction_protocol.json`](https://github.com/kirklasalle/SpaceEntropyCompression/blob/8437889/knowledgebase/candidate_a_option3_reconstruction_protocol.json),
SHA-256 `CD9687DDAC497025E709FCCC0C6BAF3D40AE5BCE92166B8C23FEFEEC16270518`.
Do not edit it to accommodate implementation or accuracy failures.

- Use float64 throughout. No float32, mixed-precision or fast-math shortcut.
- Map the **sum** of component volume densities, not each component separately.
- Apply the frozen underflow-to-zero rule; reject negative/non-finite densities
  and overflow explicitly.
- V3 requires order-64/128 convergence below 0.005 on reconstructed sources.
- V3b separately requires GPU/CPU agreement below `1e-10` at the same order.
  Backend agreement cannot establish quadrature accuracy.
- V1 includes every required reconstruction sensitivity, not only the primary
  disc. V2 prohibits double helium correction of the measured gas profiles;
  the frozen synthetic global-mass upper envelopes explicitly include 1.36.
- Hash-check data, protocol and parent protocol before evaluating sources.
  Persist code hashes, runtime versions, gate failures and uncompleted checks.
- Do not ingest observed velocities or compute a fit statistic during these
  checks. The eventual observational analysis remains non-blind/post-data.

The certified SPARC loader filters on positive observed velocity. Model-only
checks must not call that loader. Checking all positive-radius rows inside
the density coverage is a conservative **superset** for numerical validation,
not a claim to have reproduced the velocity-dependent fit selection.

## Timing limitations and correction of earlier estimates

The earlier scratch experiment used synthetic discs, not reconstructed galaxies
or a complete optimizer. It reported approximately 51 ms per CPU solve, 1 ms
per warm device density/reduction, and 5 ms for device geometry construction.
Its first timings included compilation/warm-up. Its elliptic-integral code and
underflow handling were experimental, not a released validation path.

The quoted **15--25 hours** for the full fit was an extrapolation, not a measured
completion time, and is **not a scheduling commitment**. The earlier claim that
order 64 was adequate also did not establish V3 for reconstructed sources.
Both claims must be replaced by measurements of the actual implementation.
No fit may start merely because a synthetic benchmark was fast or agreed with
another backend.

Future timing must synchronize the device, exclude reported warm-up separately,
include host/device transfers and geometry rebuilds, state batch size and memory
use, and time the full residual/Jacobian/optimizer path before predicting a fit
duration. The CPU reference remains the comparison implementation.

## Implemented backend and reproducible checks

The implementation is `tools\candidate_a_option3_reconstruction.py`,
`tools\candidate_a_option3_gpu.py` and `tools\validate_candidate_a_option3.py`.
It implements the primary reconstruction and the frozen model-only source
sensitivity family; it is not an observational optimizer. The measured gas profiles receive no second
helium factor. Synthetic global-mass H2 envelopes receive the explicitly frozen
1.36 factor and one CO factor, with normalization including the constant inner
and outer caps of the prescribed radial representation.

The backend is intentionally **hybrid**: NumPy/SciPy construct the quadrature
nodes and elliptic kernel on CPU; CuPy evaluates stellar/gas volume densities,
the nonlinear map of their sum, and the weighted integral on GPU. It does not
reuse the scratch benchmark's custom elliptic approximation. Geometry is
transferred for each field radius; no production batching/cache acceleration
is claimed. Negative radial forces remain signed during validation.

One radius is processed at a time. The validation process caps its CuPy pool at
**1 GiB**, leaving room for the Windows display and other users. This is not a
device-wide reservation or a guarantee against out-of-memory conditions.
Allocation/runtime failure is an error, never a CPU fallback or a passed gate.

From the repository root:

```powershell
$env:EMRF_TEST_GPU = "1"
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest -q emergent_matter_model\test_candidate_a_option3_reconstruction.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\validate_candidate_a_option3.py --backend gpu --output results\candidate_a_option3_validation_new_run.json
```

Omit `EMRF_TEST_GPU=1` for the CPU-only unit suite; the GPU test is explicitly
skipped, not passed. The validator requires the already-downloaded pinned
Leroy and SPARC inputs and never downloads or substitutes data. `--backend cpu`
records V3b as not run. Existing output files are refused; choose a fresh name
to preserve evidence. Exit **1** means an explicit input/runtime failure; exit
**2** means a persisted incomplete validation, including a failed numerical
gate. There is deliberately no fitting entry point.

## Measured validation checkpoint (2026-11-04)

The corrected run is `results\candidate_a_option3_validation_2026-11-04_r2.json`.
Its source hashes identify the implementation separately from the base Git
commit. The earlier `results\candidate_a_option3_validation_2026-11-04.json`
is preserved as an implementation failure: SciPy's default 50-subinterval
limit was too small for NGC2403's 57 rings. The normalization now allocates
enough subintervals; a regression test constructs all ten primary sources.
This fix changes neither the frozen mass envelope nor the protocol.

| Check | Measured result | Status |
|---|---|---|
| Corrected input audit | 11 overlaps; 13 censored HI rows; 265 missing H2 rows; stellar values present | Reproduced without parsing velocity fields |
| V1 primary projection | Maximum relative integration discrepancy/error estimate `2.75e-9` versus `1e-3` | Primary checks pass; **full V1 incomplete**, since required sensitivity variants are not validated |
| V2 gas conversion | Measured HI and H2 checked against input geometry and one CO factor; synthetic mass normalization tested | Pass within implemented primary scope |
| Frozen-v1 V3 order-64/128 | Maximum `0.0226783304` versus `< 0.005`; 120 of 180 cases exceed threshold | **Frozen-v1 check fails; gate not cleared** |
| V3b CPU/GPU | Maximum `1.2742e-15` versus `< 1e-10`, both orders on all 180 cases | Pass for primary sources |
| V4 / V5 | Not run after the prerequisite failure | Incomplete, not passed |

The worst discrepancy occurs for IC2574, low envelope, alpha = 2.
This check uses the positive-radius superset described above; the exact
velocity-dependent fit subset has not been evaluated. No galaxies or radii were
dropped to obtain a pass. Numerical failure is neither rejection nor support
of Candidate A.

The run measured approximately **36.18 s CPU** and **115.04 s GPU-path** for
the corresponding V3/V3b sweeps, including GPU first use, CPU kernel construction
and transfers. The current correctness-first GPU path is about **3.2 times
slower** in this validation workload. It is not the earlier batched scratch
implementation, and these are not optimizer timings. The CuPy pool retained
3,295,744 bytes at the end; peak device memory was **not measured**. Full-fit
duration is deliberately unset.

Software verification for this checkpoint: **52 targeted tests passed**, with
one velocity-consuming legacy coverage test deliberately deselected. The
explicit GPU test ran rather than skipped. Focused Ruff and mypy checks pass,
the strict MkDocs build passes, installed dependencies pass `pip check`, and
local Markdown link paths were checked separately for the repository documents
outside MkDocs' `docs/site` scope. These checks do not clear V3 or complete V1.

### Segmented quadrature amendment

Kirk has approved a separately versioned amendment for further model-only
validation. The method applies order-\(n\) Gauss-Legendre quadrature on each
finite radial panel split at zero, profile-ring centres, field radii within
support and the frozen cutoff; the vertical integration keeps the frozen
rational half-line map. The original v1 protocol remains unchanged.

The pre-approval exploratory artifact at
`results/candidate_a_option3_segmented_experiment_2026-11-04_r2.json` records a
maximum experimental V3 discrepancy of `2.7904e-4` versus `< 0.005`
and V3b CPU/GPU disagreement of `1.9316e-15` versus `< 1e-10`. Its V3 status is
`candidate_passed_not_authorized`, not a pass of frozen v1 or the new amendment.
The amended rerun is recorded at
`results/candidate_a_option3_segmented_amendment_1_validation_2026-11-04.json`;
it passes V3 (`2.7904e-4`) and V3b (`1.9316e-15`) under amendment 1. That
primary-only artifact reported primary V1 projection error `2.75e-9`; at the
time, full V1 remained incomplete and V4/V5 were not run. The later full
sensitivity run and its incomplete outcomes are documented below. Fitting
remains blocked. No observed velocities were parsed.

The amended CPU V3 and GPU V3b runs took 881.21 s and 869.24 s respectively,
with GPU first use and transfers included; total elapsed time was 1844.35 s.
These are validation timings, not fit estimates. The 1 GiB CuPy pool limit was
not a peak-memory measurement. See
`docs/EMRF_CANDIDATE_A_OPTION3_SEGMENTED_EXPERIMENT_2026-11-04.md` for method
details, full provenance, the amendment hash, and the superseded initial
artifact.

At the time of this checkpoint, the next step was full sensitivity validation
and V4/V5. The later outcome is recorded in the section below. Preserve frozen
v1 and its failed V3 result; do not treat GPU agreement or the pre-approval
experiment as substitutes for any gate.

Candidate B's restricted STXS direction is closed as redundant with the
already-used global-mu likelihood. A GPU does not supply a missing likelihood
or turn conditional bounds into confirmation. The volunteer-compute "EMRF farm"
remains future work, not an installed service.

## Sensitivity validation checkpoint (2026-11-05)

The full amendment-1 model-only run is
`results/candidate_a_option3_sensitivity_validation_2026-11-04.json`, SHA-256
`b3d502f5b9be54260979e990b82a6dc398a4bc2b1800370eb4a99b4cf3be4654`.
The hash-pinned amended protocol and all source files matched the provenance
record. The command was:

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\validate_candidate_a_option3.py --backend gpu --method segmented --amendment --output results\candidate_a_option3_sensitivity_validation_2026-11-04.json
```

V3 passed at `2.790382718485572e-4` versus `< 0.005`; V3b passed at
`2.076880311640573e-15` versus `< 1e-10`, over 180 primary-source cases. V2
passed, and V4 reported the descriptive model-only comparison for 20
galaxy/envelope cases. These checks do not use observed velocities or compute
a fit statistic.

V1 is incomplete: 11 of 20 outer-exponential-tail source cases have a
non-decaying component, which would imply non-finite mass when extrapolated to
infinity. The largest reported projection error among constructed sources is
`6.1755e-4` versus `< 1e-3`, but SciPy emitted roundoff and subdivision-limit
`IntegrationWarning`s in the spherical-profile projection calculation. A
subsequent closed-form line-of-sight integration of the piecewise-linear
spherical-density interpolant rechecked all 20 spherical-bulge
galaxy/envelope cases: maximum relative error `6.175843e-4` versus `< 1e-3`,
with zero integration warnings. Its hash-verified artifact is
`results/candidate_a_option3_projection_recheck_2026-11-05_r2.json`, SHA-256
`951448be4cb1dd819f0c4f072f87f997433e30cbb577fe4364ad59c3ee6f2d41`.
This resolves the projection-integration concern for the spherical variant,
but does not resolve the 11 non-decaying outer tails; full V1 remains
incomplete.

V5 is incomplete: 10/12 variants report all 180 fixed-grid cases. The
outer-tail variant lacks 11 source pairs. The spherical-inner-bulge
deprojection produces negative total baryonic density for eight galaxies,
which is rejected rather than clipped; only 36/180 cases complete for that
variant. Among complete variants, the largest reported changes are for
hydrostatic flaring (`44930.03 km/s`, relative `2.491136`) and Leroy geometry
(`4101.67 km/s`, relative `1.389690`). These are fixed-grid model-only
sensitivities, not fits or physical estimates; the complete per-variant table
is in section 12 of
`docs/EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md`.
The two invalid variants were not silently repaired or omitted. V4's largest
absolute `delta Vbar^2` was `100977.8781 km^2/s^2` (relative `0.941354`).

Total wall time was `5893.1996` seconds; the report separately records CPU V3
at `1066.14` seconds and GPU V3b at `881.96` seconds, including first use and
transfers. These are validation timings, not fit estimates. The GPU process
retained its 1 GiB CuPy pool limit; peak device memory was not measured.
**Outcome: incomplete; fit blocked.** No observed velocities were parsed, no
observational fit was performed, and `fit_permitted` is false. Do not edit the
frozen protocol or change invalid source behavior without a separately
approved and versioned protocol.
