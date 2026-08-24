# Installation

## From source

Install the latest version directly from GitHub:

```bash
python -m pip install git+https://github.com/vandalt/mastodown.git
```

Mastodown requires Python 3.11 or later.

## For development

Clone the repository and enter its directory:

```bash
git clone https://github.com/vandalt/mastodown.git
cd mastodown
```

Install the package and all development dependencies with
[uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

You can also install them with pip directly:

```bash
python -m pip install -U -e . --group dev
```

If you install with pip instead of uv, simply remove `uv run` from all commands below.

### Building the documentation

The docs can be built with

```bash
uv run make -C docs html
```

### Running the unit tests

Mastodown uses [pytest](https://pytest.org/) for testing.

```bash
uv run pytest
```
