# Security policy

## Supported version

Security fixes target the current `main` branch until formal versioned release
support is defined in Phase 9.

## Report privately

Use a [private GitHub security advisory](https://github.com/kirklasalle/SpaceEntropyCompression/security/advisories/new).
Do not open a public issue containing exploit details, credentials, private
data, or a proof that risks data loss.

Include the affected commit, deployment context, reproduction, impact, and
whether observational data, backups, artifacts, or knowledge records may be
compromised. You may attach a reviewed `emrf doctor --report` output.

## Operational boundaries

- REST v1 mutations are disabled by default.
- REST v2 mutations require a bearer token.
- Do not expose development servers directly to the internet.
- Keep raw observations immutable and verify content hashes.
- Test restore procedures before relying on a backup.
