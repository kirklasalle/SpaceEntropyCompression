"""Compatibility bridge for the canonical packaged EMRF version."""

try:
    from emrf._version import API_VERSION, __version__
except ModuleNotFoundError:
    try:
        from src.emrf._version import API_VERSION, __version__
    except ModuleNotFoundError:
        from emergent_matter_model.src.emrf._version import API_VERSION, __version__

__all__ = ["API_VERSION", "__version__"]
