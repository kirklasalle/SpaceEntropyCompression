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
| Durable runs, jobs and artifacts | 1 hour | 4 hours | Target defined; store-specific backup and restore drill remain pending |
| Prediction commitments and verification records | 1 hour | 4 hours | Target defined; store-specific backup and restore drill remain pending |
| Scientific knowledge graph and source library | 24 hours | 4 hours | Target defined; protected Git provides source recovery, but a state drill remains pending |
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
7. enforce a zero-age drill snapshot and a five-minute local drill RTO; and
8. atomically retain a JSON receipt, including failed receipts.

The five-minute drill threshold certifies the controlled local recovery
exercise. It does not replace the broader operational RTO for a complete
off-site observational archive.

Example:

```text
emrf data drill --receipt recovery-receipt.json
```

Never run destructive recovery experiments against the only copy of research
data. Production-scale rehearsals must restore into an explicitly isolated
destination and preserve the source backup unchanged.

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
