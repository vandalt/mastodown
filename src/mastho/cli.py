from argparse import ArgumentParser

from astroquery.mast import Observations

from mastho.query import query_obs


def get_meta() -> None:
    """Print metadata for all MAST observation columns."""
    Observations.get_metadata("observations").pprint(max_lines=-1)


def main() -> None:
    """Run the mastho command-line interface."""
    parser = ArgumentParser(
        prog="mastho",
        description="Tiny Python MAST client.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "get-meta",
        help="List metadata for all MAST observation columns. Should match the web portal interface.",
    )
    query_parser = subparsers.add_parser(
        "query",
        help="Query the MAST observations portal.",
    )
    query_parser.add_argument(
        "--programs",
        nargs="+",
        help="Proposal IDs to query.",
    )
    query_parser.add_argument(
        "--calib-level",
        nargs="+",
        type=int,
        help="Calibration levels of products to include.",
    )
    query_parser.add_argument(
        "--product-type",
        nargs="+",
        help="Product types to include.",
    )
    query_parser.add_argument(
        "--extension",
        nargs="+",
        help="File extensions to include.",
    )
    query_parser.add_argument(
        "--keep-ta",
        action="store_true",
        help="Keep target-acquisition observations.",
    )
    query_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print matching observations and product summary details.",
    )
    query_parser.add_argument(
        "-o",
        "--output",
        help="Write the resulting dataframe to this CSV path.",
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    if args.command == "get-meta":
        get_meta()
    elif args.command == "query":
        products = query_obs(
            programs=args.programs,
            calib_level=args.calib_level,
            product_type=args.product_type,
            extension=args.extension,
            keep_ta=args.keep_ta,
            verbose=args.verbose,
        )
        print(products)
        if args.output is not None:
            products.to_csv(args.output, index=False)
