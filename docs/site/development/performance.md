# Performance and resource baselines

EMRF treats performance as a versioned engineering contract, not as a reason
to change scientific methods or tolerances. The baseline gate measures four
deterministic workloads and rejects either resource regressions or changed
results.

## Certified standard profile

| Workload | Standard size | Preserved result |
|---|---:|---|
| Covariance | 512 x 512 symmetric positive-definite solve | solution size, residual and solution error |
| Catalog | 2,500 validated dataset records | record count and boundary IDs |
| Run artifacts | 2,000 files, 4 KiB each | file count, total bytes and deterministic ordering |
| Knowledge | 1,200 schema-valid nodes | validity, node count, edge count and zero errors |

Each workload reports:

- median, minimum and maximum elapsed seconds;
- peak Python allocation measured by `tracemalloc`;
- deterministic fixture or native-array bytes;
- the active thresholds and every invariant check;
- platform, Python version, baseline version and baseline SHA-256.

Native NumPy storage is represented by `fixture_bytes`; `tracemalloc` does not
claim to measure memory allocated inside BLAS or NumPy. These metrics are
deliberately reported separately rather than presenting an incomplete number
as process resident memory.

## Run and enforce the baseline

Measure without changing the command exit status:

```text
emrf performance run --profile standard
```

Enforce all thresholds:

```text
emrf performance check --profile standard --repeats 2
```

Use `--workload` repeatedly to select a subset. The `test` profile exists for
interface and failure-path tests; it is not release evidence. CI runs the
standard profile with two repetitions on Ubuntu 24.04 and CPython 3.12.

The typed SDK operation is:

```python
report = client.run_performance_baseline(
    profile="standard",
    repeats=2,
).to_dict()
```

REST v1 exposes `POST /api/v1/performance/baselines` only when
`EMRF_API_ALLOW_RUN=1`. REST v2 exposes
`POST /api/v2/performance/baselines` and always requires the bearer token.
Remote operators should additionally impose request-rate and concurrency
limits because the operation is intentionally resource intensive.

## Threshold evidence

The versioned
`emergent_matter_model/src/emrf/performance_baselines.json` file retains the
reference observation, dimensions and budgets. The initial standard reference
was measured on Windows AMD64 with CPython 3.12.10 using two repetitions.
Runtime limits include cross-runner headroom while remaining close enough to
detect material regressions:

| Workload | Reference median | Maximum median | Reference Python peak | Maximum Python peak |
|---|---:|---:|---:|---:|
| Covariance | 0.0081 s | 2 s | 17,368 B | 8 MiB |
| Catalog | 0.192 s | 3 s | 3,189,516 B | 32 MiB |
| Run artifacts | 2.938 s | 12 s | 3,136,316 B | 32 MiB |
| Knowledge | 1.646 s | 8 s | 2,430,904 B | 32 MiB |

The first protected CI run is a portability certification of these budgets,
not permission to silently widen them.

## Change governance

A baseline update must:

1. preserve or intentionally version every scientific/software invariant;
2. include before-and-after measurements on a supported environment;
3. explain algorithm, dependency, fixture or runner changes;
4. use a new `baseline_version`;
5. pass the full scientific golden matrix and the performance job;
6. receive normal protected review.

Never increase a threshold merely to make a failing build green. Diagnose
algorithmic complexity, I/O amplification, dependency changes, runner health,
and fixture growth first. A new scientific algorithm belongs in the evidence
lifecycle and cannot be smuggled through as a performance optimization.
