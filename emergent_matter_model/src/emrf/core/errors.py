"""Typed EMRF storage and integrity failures."""


class StorageError(OSError):
    """A durable storage operation could not be completed safely."""


class IntegrityError(StorageError):
    """Stored or incoming bytes do not match their integrity metadata."""


class AcquisitionError(StorageError):
    """A remote scientific-data acquisition could not complete safely."""
