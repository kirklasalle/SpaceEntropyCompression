# Diagnose and report a problem

Run:

```text
emrf doctor --report
```

The command prints the report path and SHA-256. To choose a location:

```text
emrf doctor --report emrf-support.json
```

The report excludes environment variables, credentials, executable and user
paths, run arguments, and dataset URLs. Review it before sharing anyway.
Attach it to the appropriate issue form together with reproduction steps.

Never attach observational data whose licence forbids redistribution, bearer
tokens, cloud credentials, private source archives, or unpublished personal
information.
