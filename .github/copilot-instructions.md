# Mastodown Copilot Instructions

## Commands

- Set up the development environment with `uv sync`.
- Run all tests with `uv run pytest`.
- Run one test with `uv run pytest tests/test_query.py::QueryObservationTests::test_query_uses_date_range_filters_and_max_entries`.
- Build documentation, including generated API and CLI reference pages, with `uv run make -C docs html`. The build treats warnings as errors.
- Check that the committed CLI reference matches `mastodown --help` with `uv run python docs/generate_cli_reference.py --check`.

Python 3.11 or later is required. When using a pip-installed environment rather than uv, omit `uv run`.

## Architecture

- The package uses a `src/` layout. The `mastodown` console command is registered in `pyproject.toml` and calls `mastodown.cli:main`.
- `cli.py` owns argparse setup and orchestration. Both `query` and `download` use the same query arguments; `run_query()` delegates to `query_obs()`, prints its dataframe, and optionally writes CSV. `download` then asks for confirmation unless `--yes` is supplied.
- `query.py` translates CLI/library filters into `astroquery.mast.Observations` calls for JWST. It fetches observations, gets and filters their products, joins `target_name` back from the observation table, and returns a pandas dataframe with `target_name` as its first column. Target-acquisition filtering uses the JWST mission metadata interface unless `keep_ta=True`.
- `download.py` consumes that dataframe and requires its product, proposal, target, and data URI columns. It derives `local_path`, compares it with `<download-dir>/manifest.csv`, downloads only required products, and updates the manifest only with successful downloads. Proposal directories are enabled by default; target directories use `target_directory_name()` to produce filesystem-safe names.
- Sphinx documentation is in `docs/`. `docs/Makefile` runs `generate_api_reference.py` before HTML builds, while `docs/conf.py` regenerates `cli-reference.md` from `cli.py` at Sphinx startup. `docs/cli-reference.md` is generated output; change the parser or generator rather than editing its content manually.

## Repository Conventions

- Keep the CLI parser, `COMMAND_NAMES`, generated CLI reference, and CLI reference tests aligned whenever commands or options change. Run the freshness check after parser changes.
- Preserve the shared argument forwarding contract between `query` and `download`: `add_query_arguments()` defines it once, and `run_query()` is the only CLI-to-`query_obs()` bridge.
- Authentication is intentionally centralized in `authenticate()`: use `MAST_API_TOKEN` when present; only trigger Astroquery's interactive login when `--auth` is set and no environment token exists.
- Query validation is library-level: date bounds must be supplied together in exact `YYYY-MM-DD` form, end dates are inclusive, and `max_entries` must be positive. Tests mock Astroquery network methods, so new query behavior should remain testable without live MAST access.
- Treat `manifest.csv` as the download state source of truth. Reconcile missing files already recorded in it, add already-present unrecorded files, and do not record failed downloads. `dry_run=True` must avoid filesystem writes, including the manifest.
- Tests use `unittest.TestCase` with `unittest.mock` and `pytest` as the runner. Patch dependencies at their use site (for example, `mastodown.query.Observations` or `mastodown.cli.query_obs`) and use temporary directories for download filesystem behavior.
