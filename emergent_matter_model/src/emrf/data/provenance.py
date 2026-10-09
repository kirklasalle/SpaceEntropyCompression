"""Public package bridge to the preserved data-provenance implementation."""

from data_provenance import (
    SYNTHETIC_MARKER,
    is_synthetic,
    provenance_banner,
    skip_comment_lines,
    verify_observation_file,
)

__all__ = [
    "SYNTHETIC_MARKER",
    "is_synthetic",
    "provenance_banner",
    "skip_comment_lines",
    "verify_observation_file",
]
