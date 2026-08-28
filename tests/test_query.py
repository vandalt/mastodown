from unittest import TestCase
from unittest.mock import Mock, patch

from astropy.table import Table
from astropy.time import Time
from pandas import DataFrame

from mastodown.query import query_obs


class QueryObservationTests(TestCase):
    def test_query_uses_date_range_filters_and_max_entries(self):
        products = Mock()
        products.to_pandas.return_value = DataFrame(
            {"obs_id": [], "parent_obsid": []}
        )
        observations = Table({"obsid": [], "target_name": []})

        with (
            patch(
                "mastodown.query.Observations.query_criteria",
                return_value=observations,
            ) as query,
            patch("mastodown.query.Observations.get_unique_product_list"),
            patch("mastodown.query.Observations.filter_products", return_value=products),
        ):
            query_obs(
                programs=["01200"],
                filters=["F480M"],
                start_date="2024-01-01",
                end_date="2024-01-31",
                max_entries=100,
                keep_ta=True,
            )

        query.assert_called_once_with(
            proposal_id=["01200"],
            filters=["F480M"],
            t_min=[Time("2024-01-01").mjd, Time("2024-02-01").mjd],
            pagesize=100,
            page=1,
            project="JWST",
        )

    def test_query_includes_target_name_as_first_column(self):
        observations = Table(
            {"obsid": [123], "target_name": ["NGC 123"]}
        )
        products = Mock()
        products.to_pandas.return_value = DataFrame(
            {
                "obs_id": ["observation-1"],
                "parent_obsid": [123],
                "productFilename": ["product.fits"],
                "proposal_id": ["1200"],
            }
        )
        metadata = Mock()
        metadata.to_pandas.return_value = DataFrame(
            {
                "exp_type": ["NRC_IMAGE"],
                "fileSetName": ["observation-1"],
                "targprop": ["HD-218396"],
            }
        )

        with (
            patch(
                "mastodown.query.Observations.query_criteria",
                return_value=observations,
            ),
            patch("mastodown.query.Observations.get_unique_product_list"),
            patch("mastodown.query.Observations.filter_products", return_value=products),
            patch("mastodown.query.MastMissions") as missions,
        ):
            missions.return_value.query_criteria.return_value = metadata
            result = query_obs(programs=["01200"], keep_ta=True)

        self.assertEqual(result.columns[0], "target_name")
        self.assertEqual(result["target_name"].tolist(), ["HD-218396"])

    def test_query_removes_target_acquisition_products(self):
        observations = Table({"obsid": [], "target_name": []})
        products = Mock()
        products.to_pandas.return_value = DataFrame(
            {
                "obs_id": [
                    "science-1_rate",
                    "target-acquisition-1_rate",
                    "another-science-1_rate",
                ],
                "proposal_id": ["1200", "1200", "1200"],
            }
        )
        metadata = Mock()
        metadata.to_pandas.return_value = DataFrame(
            {
                "exp_type": ["NRC_IMAGE", "NIS_TACQ", "NRC_IMAGE"],
                "fileSetName": [
                    "science-1",
                    "target-acquisition-1",
                    "another-science-1",
                ],
                "targprop": ["Science target", "TA target", "Another science target"],
            }
        )

        with (
            patch(
                "mastodown.query.Observations.query_criteria",
                return_value=observations,
            ),
            patch("mastodown.query.Observations.get_unique_product_list"),
            patch("mastodown.query.Observations.filter_products", return_value=products),
            patch("mastodown.query.MastMissions") as missions,
        ):
            missions.return_value.query_criteria.return_value = metadata
            result = query_obs(target_name="Science target")

        self.assertEqual(
            result["obs_id"].tolist(), ["another-science-1_rate", "science-1_rate"]
        )
        self.assertEqual(
            result["target_name"].tolist(), ["Another science target", "Science target"]
        )
        missions.return_value.query_criteria.assert_called_once_with(
            program="1200",
            select_cols=["exp_type", "fileSetName", "targprop"],
        )

    def test_query_rejects_invalid_date_range(self):
        with self.assertRaisesRegex(
            ValueError, "start_date and end_date must be specified together"
        ):
            query_obs(start_date="2024-01-01")
