from unittest import TestCase
from unittest.mock import Mock, patch

from astropy.time import Time
from astropy.table import Table
from pandas import DataFrame

from mastho.query import query_obs


class QueryObservationTests(TestCase):
    def test_query_uses_date_range_filters_and_max_entries(self):
        products = Mock()
        products.to_pandas.return_value = DataFrame({"parent_obsid": []})
        observations = Table({"obsid": [], "target_name": []})

        with (
            patch(
                "mastho.query.Observations.query_criteria",
                return_value=observations,
            ) as query,
            patch("mastho.query.Observations.get_product_list"),
            patch("mastho.query.Observations.filter_products", return_value=products),
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
            }
        )

        with (
            patch(
                "mastho.query.Observations.query_criteria",
                return_value=observations,
            ),
            patch("mastho.query.Observations.get_product_list"),
            patch("mastho.query.Observations.filter_products", return_value=products),
        ):
            result = query_obs(programs=["01200"], keep_ta=True)

        self.assertEqual(result.columns[0], "target_name")
        self.assertEqual(result["target_name"].tolist(), ["NGC 123"])

    def test_query_rejects_invalid_date_range(self):
        with self.assertRaisesRegex(
            ValueError, "start_date and end_date must be specified together"
        ):
            query_obs(start_date="2024-01-01")
