import pytest

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
