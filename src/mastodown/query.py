import logging
from datetime import datetime, timedelta

from astropy.time import Time
from astroquery.exceptions import InvalidQueryError
from astroquery.mast import MastMissions, Observations
from pandas import DataFrame

logger = logging.getLogger(__name__)


def get_meta() -> None:
    """Log metadata for all MAST observation columns."""
    metadata = Observations.get_metadata("observations")
    logger.info("%s", "\n".join(metadata.pformat(max_lines=-1)))


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

    if verbose:
        display_columns = [
            "instrument_name",
            "filters",
            "target_name",
            "obs_id",
            "calib_level",
        ]
        logger.info(
            "Found the following observations:\n%s",
            "\n".join(obs_tbl[display_columns].pformat(max_lines=-1)),
        )

    # Then we get all data products associated with the observations
    products_tbl = Observations.get_unique_product_list(obs_tbl)

    if verbose:
        logger.info("Found the following products before filtering:\n%s", products_tbl)

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

    if len(products_df) > 0:
        metadata_programs = programs or products_df["proposal_id"].dropna().unique()
        metadata = MastMissions(mission="jwst").query_criteria(
            program=", ".join(str(p) for p in metadata_programs),
            select_cols=["exp_type", "fileSetName", "targprop"],
        ).to_pandas()

        if not keep_ta:
            non_ta_files = tuple(  # noqa: F841
                metadata.query(
                    "exp_type not in ['NIS_TACQ', 'NIS_TACONFIRM']"
                ).fileSetName
            )
            products_df = products_df.query(
                "obs_id.str.startswith(@non_ta_files)"
            ).reset_index(drop=True)

        target_names = []
        for obs_id in products_df["obs_id"]:
            matches = metadata.loc[
                metadata["fileSetName"].map(obs_id.startswith), "targprop"
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"Expected exactly one JWST metadata match for product {obs_id!r}; "
                    f"found {len(matches)}."
                )
            target_names.append(matches.item())
        products_df = products_df.drop(columns=["target_name"], errors="ignore")
        products_df.insert(0, "target_name", target_names)
    else:
        products_df.insert(0, "target_name", [])

    products_df = products_df.sort_values("obs_id").reset_index(drop=True)

    # Report the final data summary before download.
    total_size = products_df["size"].sum() / 1e9 if "size" in products_df else 0
    num_files = len(products_df)
    logger.info(
        "Final list contains %d files with total size %.2f Gb", num_files, total_size
    )

    return products_df
