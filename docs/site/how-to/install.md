# Install and configure EMRF

## Supported installation

From the repository root:

```text
python -m venv emergent_matter_model/.venv
python -m pip install -e "./emergent_matter_model[dev]" -c constraints-ci.txt
emrf doctor
```

For a runtime-only installation, install the wheel without `[dev]`.

## Writable roots

- `EMRF_HOME`: all mutable EMRF state.
- `EMRF_DATA_DIR`: observational data only.
- `EMRF_PROJECT_ROOT`: explicit source checkout.
- `EMRF_OFFSITE_BACKUP_DIR`: provider-neutral off-site backup destination.

`emrf doctor` reports whether an off-site destination is configured. This is
advisory and does not claim that a physical copy exists or has passed a restore
drill. Until an independent destination is supplied, continue local verified
backups and restore drills but treat the 3-2-1 off-site requirement as unmet.

Never place API bearer tokens in source files. `EMRF_API_V2_TOKEN` is read at
runtime and is deliberately excluded from support reports.

## Verify

```text
emrf doctor
emrf data verify
emrf kb validate
emrf verify physics
```
