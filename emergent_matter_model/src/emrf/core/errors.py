"""Typed failures shared by EMRF scientific and operational layers."""


class ProvenanceError(ValueError):
    """Required scientific provenance is missing or inconsistent."""


class UnitError(ValueError):
    """A physical value has missing or incompatible units."""


class NumericalError(ArithmeticError):
    """A numerical operation produced an invalid or non-finite result."""


class ConvergenceError(NumericalError):
    """A numerical algorithm did not satisfy its convergence criterion."""


class ConfigError(ValueError):
    """Scientific or operational configuration is invalid."""


class NetworkError(OSError):
    """A required network operation failed."""


class StorageError(OSError):
    """A durable storage operation could not be completed safely."""


class IntegrityError(StorageError):
    """Stored or incoming bytes do not match their integrity metadata."""


class AcquisitionError(StorageError):
    """A remote scientific-data acquisition could not complete safely."""
