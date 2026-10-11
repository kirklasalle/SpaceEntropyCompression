# Contributing

Read the repository `CONTRIBUTING.md`, then:

1. Create a focused branch.
2. State the evidence class and scientific limitations.
3. Add or update tests that measure the exact requirement.
4. Run the smallest relevant suite, then the non-golden baseline.
5. Update generated reference with:

```text
python tools/generate_docs_reference.py
mkdocs build --strict
```

Changes to reviewed numerical results require the golden harness. Dependency
changes require manifest, constraint, and installed-wheel review.
