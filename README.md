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
