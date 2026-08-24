# Mastodown: Tiny Python MAST client

This is a tiny Python client to query MAST on the command line or from Python.
I also had a lot of MAST-related codes scattered across projects and figured this would be a good place to centralize them.

## Command line

List metadata for all available MAST observation columns:

```bash
mastodown get-meta
```

Query JWST products and save the resulting table to CSV:

```bash
mastodown query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits -o products.csv
```

Filter options accept one or more space-separated values. Use `--keep-ta` to retain
target-acquisition observations and `--verbose` to print observation details.
Use `--filters` for MAST instrument filters, `--date-range START_DATE END_DATE` for
inclusive `YYYY-MM-DD` observation dates, and `--max-entries` to limit the returned
observations.

Query products and download them after confirmation:

```bash
mastodown download --programs 01200 02473 --download-dir data --dry-run
```

The download command prompts after showing the query result; press Enter to continue,
enter `n` to cancel, or pass `-y` / `--yes` to skip the prompt. Use
`--query-output products.csv` to save the query result, and
`--no-proposal-subdir` to save files directly in the download directory.
`--target-subdir` to place each product under its target name, after the optional
proposal directory.

### Proprietary data

Both `query` and `download` authenticate automatically when `MAST_API_TOKEN` is set:

```bash
export MAST_API_TOKEN=your-mast-token
mastodown download --programs 01200
```

Alternatively, pass `--auth` to securely enter a token through Astroquery's prompt:

```bash
mastodown query --programs 01200 --auth
```

The environment token takes precedence over `--auth`. Do not pass tokens directly on
the command line.

## References

- [Astroquery's MAST module](https://astroquery.readthedocs.io/en/latest/mast/mast.html)
- [`jwst_mast_query`](https://github.com/spacetelescope/jwst_mast_query)
