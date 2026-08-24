from argparse import ArgumentParser, Namespace
from os import environ

from astroquery.mast import Observations
from pandas import DataFrame

from mastodown.download import download_products
from mastodown.query import query_obs

GET_META_DESCRIPTION = (
    "List metadata for all MAST observation columns. "
    "Should match the web portal interface."
)
QUERY_DESCRIPTION = "Query the MAST observations portal."
DOWNLOAD_DESCRIPTION = (
    "Query the MAST observations portal and download the matching products."
)


def get_meta() -> None:
    """Print metadata for all MAST observation columns."""
    Observations.get_metadata("observations").pprint(max_lines=-1)


def add_query_arguments(parser: ArgumentParser, output_flags: tuple[str, ...]) -> None:
    """Add query options to a command parser."""
    parser.add_argument(
        "--programs",
        nargs="+",
        help="Proposal IDs to query.",
    )
    parser.add_argument(
        "--calib-level",
        nargs="+",
        type=int,
        help="Calibration levels of products to include.",
    )
    parser.add_argument(
        "--product-type",
        nargs="+",
        help="Product types to include.",
    )
    parser.add_argument(
        "--extension",
        nargs="+",
        help="File extensions to include.",
    )
    parser.add_argument(
        "--filters",
        nargs="+",
        help="MAST instrument filters to include.",
    )
    parser.add_argument(
        "--date-range",
        nargs=2,
        metavar=("START_DATE", "END_DATE"),
        help="Inclusive observation dates in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--max-entries",
        type=int,
        help="Maximum number of observations to return.",
    )
    parser.add_argument(
        "--keep-ta",
        action="store_true",
        help="Keep target-acquisition observations.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print matching observations and product summary details.",
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Prompt securely for a MAST API token when MAST_API_TOKEN is not set.",
    )
    parser.add_argument(
        *output_flags,
        dest="query_output",
        help="Write the resulting dataframe to this CSV path.",
    )


def run_query(args: Namespace) -> DataFrame:
    """Query products, print the result, and optionally save it as CSV."""
    products = query_obs(
        programs=args.programs,
        calib_level=args.calib_level,
        product_type=args.product_type,
        extension=args.extension,
        filters=args.filters,
        start_date=args.date_range[0] if args.date_range is not None else None,
        end_date=args.date_range[1] if args.date_range is not None else None,
        max_entries=args.max_entries,
        keep_ta=args.keep_ta,
        verbose=args.verbose,
    )
    print(products)
    if args.query_output is not None:
        products.to_csv(args.query_output, index=False)
    return products


def confirm_download(dry_run: bool = False) -> bool:
    """Return whether the user confirms a download."""
    dry_run_str = " (dry run, no modifications will happen on disk)" if dry_run else ""
    return input(f"Continue with download{dry_run_str}? [Y/n] ").strip().lower() != "n"


def authenticate(args: Namespace) -> None:
    """Authenticate with MAST from the environment or an interactive prompt."""
    token = environ.get("MAST_API_TOKEN")
    if token:
        Observations.login(token=token)
    elif args.auth:
        Observations.login()


def main() -> None:
    """Run the mastodown command-line interface."""
    parser = ArgumentParser(
        prog="mastodown",
        description="Tiny Python MAST client.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "get-meta", help=GET_META_DESCRIPTION, description=GET_META_DESCRIPTION
    )
    query_parser = subparsers.add_parser(
        "query", help=QUERY_DESCRIPTION, description=QUERY_DESCRIPTION
    )
    add_query_arguments(query_parser, ("-o", "--output"))
    download_parser = subparsers.add_parser(
        "download", help=DOWNLOAD_DESCRIPTION, description=DOWNLOAD_DESCRIPTION
    )
    add_query_arguments(download_parser, ("--query-output",))
    download_parser.add_argument(
        "--download-dir",
        help="Directory in which to save downloaded products.",
    )
    download_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Download products even when they already exist.",
    )
    download_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List planned downloads without writing files.",
    )
    download_parser.add_argument(
        "--no-proposal-subdir",
        action="store_false",
        dest="proposal_subdir",
        help="Save products directly in the download directory.",
    )
    download_parser.add_argument(
        "--target-subdir",
        action="store_true",
        help="Group downloaded products into target-name subdirectories.",
    )
    download_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Download without prompting for confirmation.",
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    if args.command == "get-meta":
        get_meta()
    elif args.command == "query":
        authenticate(args)
        run_query(args)
    elif args.command == "download":
        authenticate(args)
        products = run_query(args)
        if args.yes or confirm_download(dry_run=args.dry_run):
            download_products(
                products,
                download_dir=args.download_dir,
                proposal_subdir=args.proposal_subdir,
                target_subdir=args.target_subdir,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
            )
        else:
            print("Download cancelled.")
