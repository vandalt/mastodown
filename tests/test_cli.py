from contextlib import redirect_stdout
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from pandas import DataFrame

from mastho.cli import main


class QueryCommandTests(TestCase):
    def test_query_forwards_arguments_and_prints_products(self):
        products = DataFrame({"productFilename": ["product.fits"]})

        with (
            patch("mastho.cli.query_obs", return_value=products) as query,
            patch(
                "sys.argv",
                [
                    "mastho",
                    "query",
                    "--programs",
                    "01200",
                    "02473",
                    "--calib-level",
                    "1",
                    "2",
                    "--product-type",
                    "SCIENCE",
                    "--extension",
                    "fits",
                    "jpg",
                    "--keep-ta",
                    "--verbose",
                ],
            ),
            redirect_stdout(StringIO()) as output,
        ):
            main()

        query.assert_called_once_with(
            programs=["01200", "02473"],
            calib_level=[1, 2],
            product_type=["SCIENCE"],
            extension=["fits", "jpg"],
            keep_ta=True,
            verbose=True,
        )
        self.assertIn("product.fits", output.getvalue())

    def test_query_writes_csv_when_output_is_specified(self):
        products = Mock()

        with (
            patch("mastho.cli.query_obs", return_value=products),
            patch("sys.argv", ["mastho", "query", "-o", "products.csv"]),
            redirect_stdout(StringIO()),
        ):
            main()

        products.to_csv.assert_called_once_with("products.csv", index=False)

    def test_query_does_not_write_csv_without_output(self):
        products = Mock()

        with (
            patch("mastho.cli.query_obs", return_value=products),
            patch("sys.argv", ["mastho", "query"]),
            redirect_stdout(StringIO()),
        ):
            main()

        products.to_csv.assert_not_called()
