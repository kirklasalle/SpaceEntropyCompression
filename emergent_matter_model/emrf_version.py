"""Compatibility bridge for the canonical packaged EMRF version."""

import importlib

try:
    from emrf._version import API_VERSION, __version__
except ModuleNotFoundError:
    try:
        _mod = importlib.import_module("src.emrf._version")
    except ModuleNotFoundError:
        _mod = importlib.import_module("emergent_matter_model.src.emrf._version")
    API_VERSION = _mod.API_VERSION
    __version__ = _mod.__version__

__all__ = ["API_VERSION", "__version__"]
