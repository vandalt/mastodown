# Command reference

<!-- This reference is generated from the CLI's `--help` output. Do not edit it manually. -->

## `mastodown`

```console
$ mastodown --help
usage: mastodown [-h] [--version] {get-meta,query,download} ...

Tiny Python MAST client.

positional arguments:
  {get-meta,query,download}
    get-meta            List metadata for all MAST observation columns. Should
                        match the web portal interface.
    query               Query the MAST observations portal.
    download            Query the MAST observations portal and download the
                        matching products.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## `mastodown get-meta`

```console
$ mastodown get-meta --help
usage: mastodown get-meta [-h]

List metadata for all MAST observation columns. Should match the web portal
interface.

options:
  -h, --help  show this help message and exit
```

## `mastodown query`

```console
$ mastodown query --help
usage: mastodown query [-h] [--programs PROGRAMS [PROGRAMS ...]]
                       [--calib-level CALIB_LEVEL [CALIB_LEVEL ...]]
                       [--product-type PRODUCT_TYPE [PRODUCT_TYPE ...]]
                       [--extension EXTENSION [EXTENSION ...]]
                       [--filters FILTERS [FILTERS ...]]
                       [--date-range START_DATE END_DATE]
                       [--max-entries MAX_ENTRIES] [--keep-ta] [--verbose]
                       [--auth] [-o QUERY_OUTPUT]

Query the MAST observations portal.

options:
  -h, --help            show this help message and exit
  --programs PROGRAMS [PROGRAMS ...]
                        Proposal IDs to query.
  --calib-level CALIB_LEVEL [CALIB_LEVEL ...]
                        Calibration levels of products to include.
  --product-type PRODUCT_TYPE [PRODUCT_TYPE ...]
                        Product types to include.
  --extension EXTENSION [EXTENSION ...]
                        File extensions to include.
  --filters FILTERS [FILTERS ...]
                        MAST instrument filters to include.
  --date-range START_DATE END_DATE
                        Inclusive observation dates in YYYY-MM-DD format.
  --max-entries MAX_ENTRIES
                        Maximum number of observations to return.
  --keep-ta             Keep target-acquisition observations.
  --verbose             Print matching observations and product summary
                        details.
  --auth                Prompt securely for a MAST API token when
                        MAST_API_TOKEN is not set.
  -o, --output QUERY_OUTPUT
                        Write the resulting dataframe to this CSV path.
```

## `mastodown download`

```console
$ mastodown download --help
usage: mastodown download [-h] [--programs PROGRAMS [PROGRAMS ...]]
                          [--calib-level CALIB_LEVEL [CALIB_LEVEL ...]]
                          [--product-type PRODUCT_TYPE [PRODUCT_TYPE ...]]
                          [--extension EXTENSION [EXTENSION ...]]
                          [--filters FILTERS [FILTERS ...]]
                          [--date-range START_DATE END_DATE]
                          [--max-entries MAX_ENTRIES] [--keep-ta] [--verbose]
                          [--auth] [--query-output QUERY_OUTPUT]
                          [--download-dir DOWNLOAD_DIR] [--overwrite]
                          [--dry-run] [--no-proposal-subdir] [--target-subdir]
                          [-y]

Query the MAST observations portal and download the matching products.

options:
  -h, --help            show this help message and exit
  --programs PROGRAMS [PROGRAMS ...]
                        Proposal IDs to query.
  --calib-level CALIB_LEVEL [CALIB_LEVEL ...]
                        Calibration levels of products to include.
  --product-type PRODUCT_TYPE [PRODUCT_TYPE ...]
                        Product types to include.
  --extension EXTENSION [EXTENSION ...]
                        File extensions to include.
  --filters FILTERS [FILTERS ...]
                        MAST instrument filters to include.
  --date-range START_DATE END_DATE
                        Inclusive observation dates in YYYY-MM-DD format.
  --max-entries MAX_ENTRIES
                        Maximum number of observations to return.
  --keep-ta             Keep target-acquisition observations.
  --verbose             Print matching observations and product summary
                        details.
  --auth                Prompt securely for a MAST API token when
                        MAST_API_TOKEN is not set.
  --query-output QUERY_OUTPUT
                        Write the resulting dataframe to this CSV path.
  --download-dir DOWNLOAD_DIR
                        Directory in which to save downloaded products.
  --overwrite           Download products even when they already exist.
  --dry-run             List planned downloads without writing files.
  --no-proposal-subdir  Save products directly in the download directory.
  --target-subdir       Group downloaded products into target-name
                        subdirectories.
  -y, --yes             Download without prompting for confirmation.
```
