# Installation

## Installing from PyPI

Mastodown requires Python 3.11 or later.
It can be installed directly from PyPI with

```console
python -m pip install mastodown
```

(accessing-proprietary-data)=
## Accessing proprietary data

The simplest way to access proprietary data is to create a [MAST API token](https://auth.mast.stsci.edu/token)
and store it as an environment variable in your `~/.consolerc` or `~/.zshrc` file:

```console
export MAST_API_TOKEN=<your-mast-token>
```

Mastodown will then authenticate you automatically on every run.
If you do not wish to set the environment variable, you can enter the token on-demand.
See the {ref}`Accessing proprietary data without an environment variable recipe
<proprietary-data-without-an-environment-variable>`.

## Installing for development

Clone the repository and enter its directory:

```console
git clone https://github.com/vandalt/mastodown.git
cd mastodown
```

Install the package and all development dependencies with
[uv](https://docs.astral.sh/uv/):

```console
uv sync
```

You can also install them with pip directly:

```console
python -m pip install -U -e . --group dev
```

If you install with pip instead of uv, simply remove `uv run` from all commands below.

### Building the documentation

The docs can be built with

```console
uv run make -C docs html
```

### Running the unit tests

Mastodown uses [pytest](https://pytest.org/) for testing.

```console
uv run pytest
```

Tests that query the live public MAST API are excluded by default. Run them with:

```console
uv run pytest --run-integration
```
