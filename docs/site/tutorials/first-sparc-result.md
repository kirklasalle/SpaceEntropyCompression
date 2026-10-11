# Produce your first SPARC result

This tutorial starts from a clean checkout and produces a durable SPARC run.
Allow approximately 15 minutes after dependencies and observations are cached.
Network and compute time vary.

## 1. Create the environment

### Windows PowerShell

```powershell
python -m venv emergent_matter_model\.venv
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt -c constraints-ci.txt
```

### Linux/macOS

```bash
python -m venv emergent_matter_model/.venv
emergent_matter_model/.venv/bin/python -m pip install \
  -r requirements-dev.txt -c constraints-ci.txt
```

## 2. Diagnose the installation

```text
emrf doctor
emrf kb validate
```

If you did not install the console script, replace `emrf` with
`python emergent_matter_model/emrf_cli.py`.

## 3. Acquire and verify SPARC

Review licensing and provenance first:

```text
emrf data info sparc-rotation-curves
emrf data fetch sparc-rotation-curves
emrf data verify
```

Raw observations remain immutable and content-addressed. Do not continue if
verification reports missing or corrupt holdings.

## 4. Run the analysis

```text
emrf run sparc-real-analysis
emrf runs list --limit 5
```

The command writes a durable run record even when the analysis fails. Inspect
it with:

```text
emrf runs info RUN_ID
emrf runs artifacts RUN_ID
```

## 5. Interpret responsibly

This SPARC analysis tests a specified acceleration-scale relationship against
observations. It does not by itself validate the whole EMRF framework, derive
matter, or replace independent lensing and cosmological tests. Record the run,
dataset holdings, assumptions, nuisance treatment, and evidence class.
