# EMRF Scientific Data and Software Library

This directory is the human-reviewed catalog of upstream scientific data and
software considered or used by EMRF. It is a catalog, not a redistribution
bundle. Large or licence-restricted datasets remain under the git-ignored
`data/external/` directory.

## Files

* `data_catalog.json` records authoritative sources, citations, licensing or
  terms links, acquisition methods, priorities, and local holdings.
* `software_catalog.json` records the intended engineering and scientific
  toolchain, including tools evaluated but not yet adopted.

## Verification meaning

`verified` is scoped to the stated field and date. It never means that a
dataset proves EMRF. A local holding is verified only when its bytes match a
pinned SHA-256 record. A URL or citation check only confirms provenance
metadata.

Statuses are:

* `existing_holding`: bytes are present locally and pinned in an existing
  project manifest or result record;
* `planned`: authoritative source identified, but acquisition still requires
  licence/size approval;
* `evaluated`: software assessed but not necessarily installed;
* `adopted`: software is part of the current or approved target stack.

## Acquisition policy

1. Confirm licence/terms and expected size.
2. Pin a release, commit, DOI, or archive record.
3. Stream into a temporary file, hash it, then atomically promote it.
4. Record the retrieval time, source URL, size, SHA-256, citation and any
   transformations.
5. Never overwrite raw observations. Derived products point back to their
   immutable inputs.

## Managed local storage

The Phase 3 `emrf.data.store.ContentAddressedStore` foundation stores bytes at
`store/sha256/<prefix>/<digest>` beneath the configured data root and records
logical holdings in `library.sqlite`. Ingestion streams through an fsynced
partial file, validates optional expected size and SHA-256 values, and then
atomically promotes the object. Reads verify content by default and reject
symbolic-link objects. Duplicate bytes share one object.

Holding identifiers are trimmed before registration and are immutable once
bound. Repeating an identical registration returns the original provenance;
it does not silently update citation, licence, source or metadata. Register a
new dataset version when provenance changes. Atomic promotion is guaranteed by
the local filesystem; parent-directory fsync is best effort on platforms such
as Windows.

Approved holdings can be imported from existing local files or fetched through
the shared data-library service. Fetches use HTTPS only, preserve partial
progress for retry, validate server range responses, reject HTTPS downgrade
redirects and quarantine completed downloads that fail a pinned size or hash.
The catalog file is packaged with installed wheels; an automated test requires
the packaged copy and this human-reviewed copy to remain byte-for-byte equal.

The CLI supports:

```text
emrf data catalog [--verify] [--json]
emrf data info DATASET [--verify]
emrf data import DATASET [HOLDING] [--source FILE]
emrf data fetch DATASET [HOLDING] [--retries N] [--timeout SECONDS]
emrf data verify
emrf data backup DESTINATION
emrf data backup-verify SOURCE
emrf data restore SOURCE
emrf data gc [--execute]
```

Garbage collection is a dry run unless `--execute` is supplied. A backup
destination must not already exist. Backup creation verifies every source
object and writes a portable manifest plus a consistent SQLite snapshot.
Restore verifies the full backup before importing objects and refuses
immutable holding conflicts. Keep at least one off-site backup and perform the
quarterly restore drill required by the engineering plan.

Matching REST endpoints are documented in `emergent_matter_model/openapi.yaml`.
All data-changing REST operations are disabled unless a trusted server is
started with `EMRF_API_ALLOW_DATA_WRITE=1`.

## Authoritative source families

The catalog links to SPARC, Pantheon+, DESI, DES-SN5YR, Union3, the Planck
Legacy Archive, GWOSC, Gaia wide-binary releases and NIST CODATA. Software
links point to each project's official documentation or repository.

Last research review: 2026-10-09. Metadata marked `needs_confirmation` must be
checked again before it is used in automated acquisition.
