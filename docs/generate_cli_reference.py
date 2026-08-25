"""Generate the command-line reference from Mastodown's argument parser."""

import re
import sys
from argparse import ArgumentParser
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DOCS_DIR.parent
REFERENCE_PATH = DOCS_DIR / "cli-reference.md"
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

sys.path.insert(0, str(PROJECT_DIR / "src"))

from mastodown.cli import COMMAND_NAMES, create_parser


def format_command_help(parser: ArgumentParser, command: str | None = None) -> str:
    """Return formatted help for the root parser or one subcommand."""
    if command is None:
        return ANSI_ESCAPE_PATTERN.sub("", parser.format_help()).rstrip()

    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if choices is not None and command in choices:
            return ANSI_ESCAPE_PATTERN.sub("", choices[command].format_help()).rstrip()

    msg = f"Command {command!r} is not registered with the argument parser."
    raise ValueError(msg)


def render_reference() -> str:
    """Render the complete command reference as MyST Markdown."""
    parser = create_parser()
    sections = [
        "# Command reference",
        "",
        "<!-- This reference is generated from the CLI's `--help` output. Do not edit it manually. -->",
    ]
    for command in (None, *COMMAND_NAMES):
        invocation = "mastodown" if command is None else f"mastodown {command}"
        sections.extend(
            [
                "",
                f"## `{invocation}`",
                "",
                "```console",
                f"$ {invocation} --help",
                format_command_help(parser, command),
                "```",
            ]
        )
    return "\n".join(sections) + "\n"


def write_reference(*, check: bool = False) -> None:
    """Write the reference, or fail when the committed version is stale."""
    content = render_reference()
    if check:
        if (
            not REFERENCE_PATH.is_file()
            or REFERENCE_PATH.read_text(encoding="utf-8") != content
        ):
            msg = f"{REFERENCE_PATH.relative_to(PROJECT_DIR)} is out of date."
            raise SystemExit(msg)
        return

    REFERENCE_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    """Generate the reference, accepting a freshness-check mode."""
    write_reference(check="--check" in sys.argv[1:])


if __name__ == "__main__":
    main()
