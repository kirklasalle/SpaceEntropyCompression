# Record scientific evidence

EMRF's knowledge graph preserves claims, sources, datasets, runs, and results
without converting software success into scientific support.

## Validate and query

```text
emrf kb validate
emrf kb query --kind claim --status proposed
emrf kb query "SPARC" --json
```

## Register a literature source

Save a verified BibTeX entry and a snapshot of the retrieved source. Compute
the snapshot SHA-256, then run:

```text
emrf kb add-source source:example-2026 \
  --title "Example paper" \
  --author "A. Researcher" \
  --year 2026 \
  --doi 10.0000/example \
  --snapshot-sha256 SHA256 \
  --bibtex-file example.bib
```

## Link terminal evidence

Only terminal durable runs may publish graph evidence:

```text
emrf kb link-run RUN_ID \
  --claim claim:target \
  --source source:example-2026 \
  --dataset dataset:target
```

EMRF hashes regular run artifacts and rejects later byte changes. A claim is
not promoted automatically; lifecycle changes require scientific review.
