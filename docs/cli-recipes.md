# Command line recipes

For complete option details, see the {doc}`command reference <cli-reference>`.

## Viewing MAST metadata columns

List metadata for all available MAST observation columns:

```bash
mastodown get-meta
```

## Querying products

Query JWST products and save the resulting table to CSV:

```bash
mastodown query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits -o products.csv
```

Filter options accept one or more space-separated values. Use `--keep-ta` to
retain target-acquisition observations and `--verbose` to print observation
details. Use `--filters` for MAST instrument filters,
`--date-range START_DATE END_DATE` for inclusive `YYYY-MM-DD` observation
dates, and `--max-entries` to limit returned observations.

## Downloading products

Query products and download them after confirmation:

```bash
mastodown download --programs 01200 02473 --download-dir data --dry-run
```

The download command prompts after showing the query result; press Enter to
continue, enter `n` to cancel, or pass `-y` / `--yes` to skip the prompt. Use
`--query-output products.csv` to save the query result, and
`--no-proposal-subdir` to save files directly in the download directory. Use
`--target-subdir` to place each product under its target name, after the
optional proposal directory.

(proprietary-data-without-an-environment-variable)=
## Accessing proprietary data without an environment variable

As described in the {ref}`installation docs <accessing-proprietary-data>`,
the simplest way to access proprietary data is by storing your MAST API token in an environment variable.

Alternatively, you can pass `--auth` to securely enter a token through Astroquery's prompt:

```bash
mastodown query --programs 01200 --auth
```

The environment token takes precedence over `--auth`.
Do not pass tokens directly on the command line.
