"""Generate deterministic CLI and REST v2 Markdown reference pages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "emergent_matter_model"
sys.path[:0] = [str(PACKAGE), str(PACKAGE / "src")]

from emrf.interfaces.api_v2 import app
from emrf_cli import build_parser

OUTPUTS = {
    ROOT / "docs" / "site" / "reference" / "cli.md": lambda: _cli_reference(
        build_parser()
    ),
    ROOT / "docs" / "site" / "reference" / "api-v2.md": lambda: _api_reference(
        app.openapi()
    ),
}


def _cli_reference(parser: argparse.ArgumentParser) -> str:
    lines = [
        "# CLI reference",
        "",
        "Generated from the supported `argparse` command tree. Do not edit manually.",
        "",
        "Run `emrf COMMAND --help` for complete option semantics.",
        "",
    ]
    _document_parser(parser, ("emrf",), lines, level=2)
    return "\n".join(lines).rstrip() + "\n"


def _document_parser(
    parser: argparse.ArgumentParser,
    command: tuple[str, ...],
    lines: list[str],
    *,
    level: int,
) -> None:
    title = " ".join(command)
    lines.extend(
        [
            f"{'#' * level} `{title}`",
            "",
            parser.description or "Supported EMRF command.",
            "",
            "```text",
            parser.format_usage().strip(),
            "```",
            "",
        ]
    )
    options = [
        action
        for action in parser._actions
        if not isinstance(action, argparse._SubParsersAction)
        and action.dest != "help"
    ]
    if options:
        lines.extend(["| Argument | Required | Description |", "|---|---:|---|"])
        for action in options:
            names = ", ".join(action.option_strings) or action.dest
            required = "Yes" if _action_is_required(action) else "No"
            description = (action.help or "").replace("|", "\\|")
            lines.append(f"| `{names}` | {required} | {description} |")
        lines.append("")
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, child in action.choices.items():
                _document_parser(child, (*command, name), lines, level=min(level + 1, 6))


def _action_is_required(action: argparse.Action) -> bool:
    if action.option_strings:
        return action.required
    return action.nargs not in {
        argparse.OPTIONAL,
        argparse.ZERO_OR_MORE,
        argparse.REMAINDER,
    }


def _api_reference(schema: dict[str, Any]) -> str:
    lines = [
        "# REST API v2 reference",
        "",
        "Generated from the FastAPI OpenAPI document. Do not edit manually.",
        "",
        f"API version: `{schema['info']['version']}`",
        "",
        "Interactive documentation is served at `/api/v2/docs` and the machine",
        "contract at `/api/v2/openapi.json`.",
        "",
        "## Operations",
        "",
        "| Method | Path | Authentication | Tags |",
        "|---|---|---|---|",
    ]
    for path, path_item in sorted(schema["paths"].items()):
        for method, operation in sorted(path_item.items()):
            if method.upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            security = operation.get("security", schema.get("security", []))
            authenticated = "Required" if security else "No"
            tags = ", ".join(operation.get("tags", []))
            lines.append(
                f"| `{method.upper()}` | `{path}` | {authenticated} | {tags} |"
            )
    lines.extend(
        [
            "",
            "## Error model",
            "",
            "Transport errors use `ErrorResponse` with `code`, `message`, and",
            "`details`. Validation failures return HTTP 422. Mutating operations",
            "require `EMRF_API_V2_TOKEN` and a matching bearer token.",
            "",
            "## Schema inventory",
            "",
        ]
    )
    for name in sorted(schema["components"]["schemas"]):
        lines.append(f"- `{name}`")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    if sys.version_info[:2] not in {(3, 10), (3, 12)}:
        print(
            "Documentation reference generation requires certified Python "
            "3.10 or 3.12.",
            file=sys.stderr,
        )
        return 2
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when committed references differ from generated output",
    )
    args = parser.parse_args(argv)
    stale: list[str] = []
    for path, producer in OUTPUTS.items():
        expected = producer()
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8", newline="\n")
    if stale:
        print(
            "Generated documentation is stale: " + ", ".join(stale),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
