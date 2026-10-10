"""Public access to EMRF project and writable data-path resolution."""

from emrf_paths import (
    app_root,
    data_root,
    default_app_root,
    project_root,
    resolve_data_path,
)

__all__ = [
    "app_root",
    "data_root",
    "default_app_root",
    "project_root",
    "resolve_data_path",
]
