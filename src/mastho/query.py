from astroquery.exceptions import InvalidQueryError
from astroquery.mast import MastMissions, Observations
from pandas import DataFrame


def query_obs(
    programs: list[str] | str | None = None,
    calib_level: list[int] | int | None = None,
    product_type: list[str] | str | None = None,
    extension: list[str] | str | None = None,
    keep_ta: bool = False,
    verbose: bool = False,
) -> DataFrame:
    # Get observation table that will contain only level 3 (i2d) data
    criteria = {"proposal_id": programs}
    criteria = {k: v for k, v in criteria.items() if v is not None}
    if len(criteria) == 0:
        raise InvalidQueryError(
            "At least one non-positional criterion must be supplied."
        )
    obs_tbl = Observations.query_criteria(
        **criteria,
        project="JWST",
        # TODO: Decide if keep or remove
        # instrument_name=["NIRISS/IMAGE", "NIRCAM/IMAGE"],
        # filters=["F480M", "F150W"],
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
    products_tbl = Observations.get_product_list(obs_tbl)

    # Then filter to keep science and/or auxiliary, pick the calib level and extension
    filters = {
        "productType": product_type,
        "calib_level": calib_level,
        "extension": extension,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    products_df = Observations.filter_products(
        products_tbl,
        **filters,
    ).to_pandas()

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

    if verbose:
        # Print final data before download
        total_size = sum(products_df["size"]) / 1e9
        num_files = len(products_df)
        print(
            f"Final list contains {num_files} files with total size {total_size:.2f} GB"
        )

    return products_df
