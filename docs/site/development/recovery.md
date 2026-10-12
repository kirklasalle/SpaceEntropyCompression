# Recovery objectives and drills

EMRF treats recovery as a measured scientific-software property. A backup is
not considered usable merely because files were copied: restoration must occur
in an isolated destination, every recovered object and relationship must be
verified, and the drill must leave a durable receipt.

## Recovery objectives

The recovery point objective (RPO) limits how much recent state may be lost.
The recovery time objective (RTO) limits how long verified restoration may
take. These are initial service targets; retained drill evidence must be used
to tighten or revise them rather than silently weakening a failed gate.

| State class | RPO | RTO | Current recovery status |
|---|---:|---:|---|
| Managed observational objects and holdings | 24 hours | 24 hours | Implemented: verified off-site content-addressed backup and isolated restore |
| Curated data catalog | 0 for a release; 24 hours during development | 4 hours | Implemented: protected Git history and catalog verification in the data drill |
| Durable runs, jobs and artifacts | 1 hour | 4 hours | Implemented: consistent registry snapshot, complete artifact hashes and isolated restore |
| Prediction commitments | 1 hour | 4 hours | Implemented: immutable commitment validation and isolated restore |
| Prediction verification outcomes | 1 hour | 4 hours | Target defined; outcomes are currently transient and are not represented as durable records |
| Scientific knowledge graph and source library | 24 hours | 4 hours | Implemented: graph and schema validation, protected Git, and isolated restore |
| Release metadata and application configuration | 0 for a release | 1 hour | Implemented for releases through protected Git and immutable release artifacts |

An RPO of zero for a released artifact means the exact protected and published
state must be reconstructable; it does not imply synchronous replication of
all development work.

## Automated data recovery drill

`emrf data drill` and the equivalent SDK and REST v2 operations:

1. create a fresh backup from the managed content-addressed store;
2. verify its manifest, object hashes, holding relationships and SQLite
   snapshot;
3. restore into an isolated temporary store without modifying the source;
4. verify every restored object and holding;
5. copy and re-parse the curated catalog, recording its SHA-256 digest, schema
   version and dataset count;
6. measure backup, backup verification, restore and final-verification time;
7. enforce five-minute local RPO and RTO thresholds and fail the RPO if the
   managed source changes after its backup snapshot; and
8. atomically retain a JSON receipt, including failed receipts.

The five-minute drill threshold certifies the controlled local recovery
exercise. It does not replace the broader operational RTO for a complete
off-site observational archive.

Example:

```text
emrf data drill --receipt recovery-receipt.json
```

## Application-state recovery drill

`emrf recovery drill` and the equivalent SDK and REST operations protect:

- the consistent SQLite run/job registry;
- every durable run file, including checkpoints, logs and result artifacts;
- every immutable prediction-commitment record; and
- the scientific knowledge graph together with the schema that validates it.

The backup manifest hashes every file and a canonical logical inventory.
Creation fails if the source changes while it is copied. Restore is
non-destructive and accepts only a destination that does not already exist.
The isolated drill restores all components, revalidates SQLite integrity and
relationships, reparses every prediction commitment, validates the knowledge
schema and semantics, and compares the restored logical fingerprint.

```text
emrf recovery backup state-backup
emrf recovery backup-verify state-backup
emrf recovery restore state-backup isolated-state
emrf recovery drill --receipt state-recovery-receipt.json
```

The application-state drill enforces the strictest combined operational target:
a one-hour RPO and four-hour RTO. A source change after the snapshot fails the
RPO rather than producing success-shaped evidence.

Never run destructive recovery experiments against the only copy of research
data. Production-scale rehearsals must restore into an explicitly isolated
destination and preserve the source backup unchanged.

## Periodic operational certification

The read-only `Operational certification` workflow runs monthly and may also
be dispatched manually from protected `main`. It creates controlled non-empty
state containing one observational holding, one durable run and artifact, one
queued job, and one prediction commitment. It then:

1. runs the isolated observational-data recovery drill;
2. runs the isolated application-state recovery drill;
3. enforces the standard performance and resource baseline; and
4. retains the individual recovery receipts and combined machine-readable
   summary for 90 days, including evidence from failed drills.

The workflow refuses to certify any commit other than the current protected
`main` commit, has read-only repository permissions, never publishes a release,
and does not replace production-scale off-site recovery exercises. Immutable
release and DOI health remain independently rehearsed by the monthly
`Release health` workflow.

For a local controlled rehearsal:

```text
python tools/run_operational_certification.py \
  --workspace operational-certification \
  --receipt operational-certification/evidence/summary.json \
  --profile standard --repeats 2
```

## Incident handling

- Treat an exceeded objective, invalid hash, incomplete relationship or
  unreadable catalog as a failed recovery.
- Preserve the failed receipt and workflow logs.
- Do not overwrite a prior receipt or alter a published release to make a
  rehearsal pass.
- Correct the root cause through protected `main`, repeat the drill and retain
  both failure and success evidence.
- Escalate any prospective loss of prediction commitments or scientific
  evidence before resuming write operations.
