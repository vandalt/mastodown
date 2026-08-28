import pytest
from astroquery.mast import MastMissions

from mastodown.query import query_obs

pytestmark = pytest.mark.integration


def test_query_returns_unique_observation_ids() -> None:
    result = query_obs(
        programs=["01200"],
        calib_level=1,
        product_type="science",
        extension="fits",
    )

    assert result["obs_id"].is_unique


def test_query_target_names_match_mission_metadata() -> None:
    result = query_obs(
        programs=["01200"],
        calib_level=1,
        product_type="science",
        extension="fits",
    )
    metadata = (
        MastMissions(mission="jwst")
        .query_criteria(
            program="1200",
            select_cols=["fileSetName", "targprop"],
        )
        .to_pandas()
    )

    for product in result.itertuples(index=False):
        matches = metadata.loc[metadata["fileSetName"].map(product.obs_id.startswith)]

        assert len(matches) == 1, product.obs_id
        assert product.target_name == matches["targprop"].item()
