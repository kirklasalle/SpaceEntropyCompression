"""Public package bridge to the shared CLI/API command registry."""

from emrf_registry import (
    CATEGORIES,
    COMMANDS,
    Command,
    dataset_status,
    environment_report,
    get_command,
    list_commands,
    run_command,
)

__all__ = [
    "CATEGORIES",
    "COMMANDS",
    "Command",
    "dataset_status",
    "environment_report",
    "get_command",
    "list_commands",
    "run_command",
]
