from datetime import datetime, timedelta

from astropy.time import Time
from astroquery.exceptions import InvalidQueryError
from astroquery.mast import MastMissions, Observations
from pandas import DataFrame


def get_meta() -> None:
    """Print metadata for all MAST observation columns."""
    Observations.get_metadata("observations").pprint(max_lines=-1)


def parse_date(date_string: str) -> datetime:
    """Parse a YYYY-MM-DD date string."""
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")  # noqa: DTZ007
    except ValueError as error:
        raise ValueError(f"Date must use YYYY-MM-DD format: {date_string}") from error
    if date.strftime("%Y-%m-%d") != date_string:
        raise ValueError(f"Date must use YYYY-MM-DD format: {date_string}")
    return date


def query_obs(
    programs: list[str] | str | None = None,
    calib_level: list[int] | int | None = None,
    product_type: list[str] | str | None = None,
    product_subgroup: list[str] | str | None = None,
    extension: list[str] | str | None = None,
    filters: list[str] | str | None = None,
    target_name: list[str] | str | None = None,
    instrument_name: list[str] | str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    max_entries: int | None = None,
    keep_ta: bool = False,
    verbose: bool = False,
) -> DataFrame:
    # Get observation table that will contain only level 3 (i2d) data
    if (start_date is None) != (end_date is None):
        raise ValueError("start_date and end_date must be specified together.")
    if max_entries is not None and max_entries <= 0:
        raise ValueError("max_entries must be greater than zero.")

    # TODO: There has to be a cleaner way to pre-process arguments
    if isinstance(programs, (str, int)):
        programs = [programs]
    if isinstance(product_type, str):
        product_type = [product_type]
    if isinstance(product_subgroup, str):
        product_subgroup = [product_subgroup]

    criteria = {
        "proposal_id": programs,
        "filters": filters,
        "target_name": target_name,
        "instrument_name": instrument_name,
    }
    if start_date is not None and end_date is not None:
        start = parse_date(start_date)
        end = parse_date(end_date)
        if end < start:
            raise ValueError("end_date must not be earlier than start_date.")
        criteria["t_min"] = [Time(start).mjd, Time(end + timedelta(days=1)).mjd]
    criteria = {k: v for k, v in criteria.items() if v is not None}
    if len(criteria) == 0:
        raise InvalidQueryError(
            "At least one non-positional criterion must be supplied."
        )
    if max_entries is not None:
        criteria.update(pagesize=max_entries, page=1)
    obs_tbl = Observations.query_criteria(**criteria, project="JWST")
    target_names = (
        obs_tbl["obsid", "target_name"].to_pandas().drop_duplicates(subset=["obsid"])
    )

    if verbose:
        display_columns = [
            "instrument_name",
            "filters",
            "target_name",
            "obs_id",
            "calib_level",
        ]
        print("Found the following observations:")
        obs_tbl[display_columns].pprint(max_lines=-1)

    # Then we get all data products associated with the observations
    products_tbl = Observations.get_unique_product_list(obs_tbl)

    if verbose:
        print("Found the following products before filtering:")
        print(products_tbl)

    # Then filter to keep science and/or auxiliary, pick the calib level and extension
    product_filters = {
        "productType": [x.upper() for x in product_type] if product_type else None,
        "productSubGroupDescription": [x.upper() for x in product_subgroup] if product_subgroup else None,
        "calib_level": calib_level,
        "extension": extension,
    }
    product_filters = {k: v for k, v in product_filters.items() if v is not None}
    products_df = Observations.filter_products(
        products_tbl,
        **product_filters,
    ).to_pandas()
    products_df = (
        products_df.drop(columns=["target_name"], errors="ignore")
        .merge(
            target_names,
            left_on="parent_obsid",
            right_on="obsid",
            how="left",
        )
        .drop(columns=["obsid"])
    )
    products_df = products_df[["target_name", *products_df.columns.drop("target_name")]]

    if not keep_ta:
        # We use the mission interface to drop TA observations
        missions = MastMissions(mission="jwst")
        metadata = missions.query_criteria(
            program=", ".join(str(p) for p in programs),
            select_cols=["exp_type", "fileSetName"],
        )
        metadata = metadata.to_pandas()
        metadata_img = metadata.query("exp_type not in ['NIS_TACQ', 'NIS_TACONFIRM']")

        non_ta_files = tuple(metadata_img.fileSetName)  # noqa: F841
        products_df = products_df.query(
            "obs_id.str.startswith(@non_ta_files)"
        ).reset_index(drop=True)

    # Print final data before download
    total_size = products_df["size"].sum() / 1e9 if "size" in products_df else 0
    num_files = len(products_df)
    print(f"Final list contains {num_files} files with total size {total_size:.2f} Gb")

    return products_df
