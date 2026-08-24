"""Configuration for the Mastodown Sphinx documentation."""

from pathlib import Path
import sys

DOCS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS_DIR))
sys.path.insert(0, str(DOCS_DIR.parent / "src"))

project = "Mastodown"
copyright = "2026, Thomas Vandal"
author = "Thomas Vandal"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"


def generate_cli_reference(_: object) -> None:
    """Refresh generated CLI help before Sphinx reads source files."""
    from generate_cli_reference import write_reference

    write_reference()


def setup(app: object) -> None:
    """Register documentation build hooks."""
    app.connect("builder-inited", generate_cli_reference)
