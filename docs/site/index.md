# Emergent Matter Research Framework

EMRF is scientific research software for reproducible gravitational and
astrophysical analyses, durable observational-data management, typed Python,
CLI and REST interfaces, and evidence-qualified scientific memory.

!!! warning "Research status"
    Passing software tests does not establish physical truth. EMRF contains
    standard baselines, observational re-analyses, synthetic validation, and
    hypotheses. Every result must retain its evidence class and limitations.

## Choose your path

- **New researcher:** complete [the first SPARC result](tutorials/first-sparc-result.md).
- **Operator:** follow [installation](how-to/install.md), [API](how-to/api.md),
  and [support](how-to/support.md) procedures.
- **Developer:** read [architecture](explanation/architecture.md), then
  [contributing](development/contributing.md) and the
  [extension tutorial](development/extensions.md).
- **Reviewer:** start with [evidence classes](explanation/evidence.md) and
  [physics scope](explanation/physics.md).

## Supported surfaces

The typed `EMRFClient` application layer is authoritative. The `emrf` CLI,
Flask REST v1 compatibility API, and FastAPI REST v2 call that layer.
REST v1 remains stable for existing clients; new functionality targets v2.

Current supported Python versions are 3.10 and 3.12. JavaFX compatibility is
certified on Java 17.
