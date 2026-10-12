# Python SDK reference

The stable entry point is:

```python
from emrf.sdk import EMRFClient

client = EMRFClient()
print(client.environment_report().to_dict())
```

Operation families include command execution, runs, jobs, artifacts,
verification, datasets, backup/restore, predictions, simulation, scientific
knowledge, deterministic performance baselines, and support reports. Request
and response values are immutable dataclasses exported from `emrf.sdk`.

## Error contract

- `InvalidRequestError`: invalid caller input.
- `ResourceNotFoundError`: a named resource does not exist.
- `OperationUnavailableError`: storage, integrity, acquisition, or operational
  failure prevented completion.

Do not catch broad `Exception` around SDK calls. Handle the stable error class,
log its `code` and `details`, and do not transform a failure into success.
