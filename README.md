# MASTho: Tiny Python MAST client

This is a tiny Python client to query MAST on the command line.
I also had a lot of MAST-related codes scattered across projects and figured this would be a good place to centralize them.

## Command line

List metadata for all available MAST observation columns:

```console
mastho get-meta
```

Query JWST products and save the resulting table to CSV:

```console
mastho query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits -o products.csv
```

Filter options accept one or more space-separated values. Use `--keep-ta` to retain
target-acquisition observations and `--verbose` to print observation details.

Query products and download them after confirmation:

```console
mastho download --programs 01200 02473 --download-dir data --dry-run
```

The download command prompts after showing the query result; press Enter to continue,
enter `n` to cancel, or pass `-y` / `--yes` to skip the prompt. Use
`--query-output products.csv` to save the query result, and
`--no-proposal-subdir` to save files directly in the download directory.
