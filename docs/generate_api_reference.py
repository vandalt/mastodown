"""Generate API reference pages from the Mastodown package."""

from pathlib import Path
import subprocess
import sys

DOCS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DOCS_DIR.parent
API_DIR = DOCS_DIR / "api"
PACKAGE_DIR = PROJECT_DIR / "src" / "mastodown"
INDEX_PATH = API_DIR / "index.rst"


def main() -> None:
    """Generate module pages and an API-reference toctree."""
    API_DIR.mkdir(exist_ok=True)

    for path in API_DIR.glob("mastodown*.rst"):
        path.unlink()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx.ext.apidoc",
            "--separate",
            "--no-toc",
            "--force",
            "-o",
            str(API_DIR),
            str(PACKAGE_DIR),
        ],
        check=True,
    )

    # The package overview duplicates the flat API index's role and introduces
    # duplicate toctree references for each module.
    (API_DIR / "mastodown.rst").unlink()
    modules = sorted(path.stem for path in API_DIR.glob("mastodown.*.rst"))
    for module in modules:
        exclude_imported_members(API_DIR / f"{module}.rst")
    INDEX_PATH.write_text(
        "API Reference\n"
        "=============\n"
        "\n"
        ".. toctree::\n"
        "   :maxdepth: 1\n"
        "\n"
        + "".join(f"   {module}\n" for module in modules),
        encoding="utf-8",
    )


def exclude_imported_members(path: Path) -> None:
    """Keep autodoc focused on Mastodown's public objects."""
    content = path.read_text(encoding="utf-8")
    content = content.replace(
        "   :members:\n",
        (
            "   :members:\n"
            "   :exclude-members: ArgumentParser, DataFrame, InvalidQueryError, "
            "MastMissions, Namespace, Observations, Path, Series, Time, concat, "
            "datetime, environ, read_csv, sub, timedelta\n"
        ),
        1,
    )
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
