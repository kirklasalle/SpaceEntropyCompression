# Evidence classes and claim lifecycle

EMRF separates:

- **observational:** authenticated measured data;
- **published:** a result reported by a citable source;
- **synthetic:** generated data for recovery or calibration;
- **illustrative:** a demonstration not suitable for inference;
- **software:** correctness and operational evidence.

Software evidence cannot promote a physics claim. Synthetic injection recovery
can validate an inference procedure but cannot establish observational support.

Claims progress through `proposed`, `tested`, `supported`, `refuted`, or
`retracted`. Every non-proposed claim must have a typed evidence reference or
evidence edge. Conditions encode regimes of validity rather than hiding
exceptions in prose.
