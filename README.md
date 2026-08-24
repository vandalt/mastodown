# Mastodown

Mastodown is a small Python client for querying and downloading data from the
[MAST](https://mast.stsci.edu/) archive on the command line or from Python.

Read the [documentation](https://mastodown.readthedocs.io/) for installation,
command-line usage, authentication, and the Python API reference.

## Quick start

```bash
python -m pip install git+https://github.com/vandalt/mastodown.git
mastodown query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits -o products.csv
```

See the [CLI guide](https://mastodown.readthedocs.io/en/latest/cli.html) for all
commands and options.
