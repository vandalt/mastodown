from contextlib import redirect_stdout
from io import StringIO
from os import environ
from unittest import TestCase
from unittest.mock import Mock, call, patch

from pandas import DataFrame

from mastodown.cli import main


class QueryCommandTests(TestCase):
    def test_query_auth_prompts_through_astroquery(self):
        products = DataFrame({"productFilename": ["product.fits"]})
        calls = Mock()

        with (
            patch("mastodown.cli.Observations.login") as login,
            patch("mastodown.cli.query_obs", return_value=products) as query,
            patch.dict(environ, {}, clear=True),
            patch("sys.argv", ["mastodown", "query", "--auth"]),
            redirect_stdout(StringIO()),
        ):
            calls.attach_mock(login, "login")
            calls.attach_mock(query, "query")
            main()

        login.assert_called_once_with()
        query.assert_called_once()
        self.assertEqual(calls.mock_calls, [call.login(), call.query(
            programs=None,
            calib_level=None,
            product_type=None,
            extension=None,
            filters=None,
            start_date=None,
            end_date=None,
            max_entries=None,
            keep_ta=False,
            verbose=False,
        )])

    def test_query_does_not_authenticate_without_token_or_flag(self):
        products = DataFrame({"productFilename": ["product.fits"]})

        with (
            patch("mastodown.cli.Observations.login") as login,
            patch("mastodown.cli.query_obs", return_value=products),
            patch.dict(environ, {}, clear=True),
            patch("sys.argv", ["mastodown", "query"]),
            redirect_stdout(StringIO()),
        ):
            main()

        login.assert_not_called()

    def test_query_forwards_arguments_and_prints_products(self):
        products = DataFrame({"productFilename": ["product.fits"]})

        with (
            patch("mastodown.cli.query_obs", return_value=products) as query,
            patch(
                "sys.argv",
                [
                    "mastodown",
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
                    "--filters",
                    "F480M",
                    "F150W",
                    "--date-range",
                    "2024-01-01",
                    "2024-01-31",
                    "--max-entries",
                    "100",
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
            filters=["F480M", "F150W"],
            start_date="2024-01-01",
            end_date="2024-01-31",
            max_entries=100,
            keep_ta=True,
            verbose=True,
        )
        self.assertIn("product.fits", output.getvalue())

    def test_query_writes_csv_when_output_is_specified(self):
        products = Mock()

        with (
            patch("mastodown.cli.query_obs", return_value=products),
            patch("sys.argv", ["mastodown", "query", "-o", "products.csv"]),
            redirect_stdout(StringIO()),
        ):
            main()

        products.to_csv.assert_called_once_with("products.csv", index=False)

    def test_query_does_not_write_csv_without_output(self):
        products = Mock()

        with (
            patch("mastodown.cli.query_obs", return_value=products),
            patch("sys.argv", ["mastodown", "query"]),
            redirect_stdout(StringIO()),
        ):
            main()

        products.to_csv.assert_not_called()


class DownloadCommandTests(TestCase):
    def test_download_uses_environment_token_before_querying(self):
        products = Mock()
        calls = Mock()

        with (
            patch("mastodown.cli.Observations.login") as login,
            patch("mastodown.cli.query_obs", return_value=products) as query,
            patch("mastodown.cli.download_products") as download,
            patch.dict(environ, {"MAST_API_TOKEN": "token"}),
            patch("sys.argv", ["mastodown", "download", "--auth", "--yes"]),
            redirect_stdout(StringIO()),
        ):
            calls.attach_mock(login, "login")
            calls.attach_mock(query, "query")
            main()

        login.assert_called_once_with(token="token")
        query.assert_called_once()
        download.assert_called_once()
        self.assertEqual(calls.mock_calls[:2], [call.login(token="token"), call.query(
            programs=None,
            calib_level=None,
            product_type=None,
            extension=None,
            filters=None,
            start_date=None,
            end_date=None,
            max_entries=None,
            keep_ta=False,
            verbose=False,
        )])

    def test_download_forwards_options_and_skips_prompt_with_yes(self):
        products = Mock()

        with (
            patch("mastodown.cli.query_obs", return_value=products) as query,
            patch("mastodown.cli.download_products") as download,
            patch("builtins.input") as prompt,
            patch(
                "sys.argv",
                [
                    "mastodown",
                    "download",
                    "--programs",
                    "01200",
                    "02473",
                    "--calib-level",
                    "1",
                    "--product-type",
                    "SCIENCE",
                    "--extension",
                    "fits",
                    "--keep-ta",
                    "--verbose",
                    "--query-output",
                    "products.csv",
                    "--download-dir",
                    "data",
                    "--overwrite",
                    "--dry-run",
                    "--no-proposal-subdir",
                    "--target-subdir",
                    "--yes",
                ],
            ),
            redirect_stdout(StringIO()),
        ):
            main()

        query.assert_called_once_with(
            programs=["01200", "02473"],
            calib_level=[1],
            product_type=["SCIENCE"],
            extension=["fits"],
            filters=None,
            start_date=None,
            end_date=None,
            max_entries=None,
            keep_ta=True,
            verbose=True,
        )
        products.to_csv.assert_called_once_with("products.csv", index=False)
        download.assert_called_once_with(
            products,
            download_dir="data",
            proposal_subdir=False,
            target_subdir=True,
            overwrite=True,
            dry_run=True,
        )
        prompt.assert_not_called()

    def test_download_proceeds_when_confirmation_is_empty(self):
        products = Mock()

        with (
            patch("mastodown.cli.query_obs", return_value=products),
            patch("mastodown.cli.download_products") as download,
            patch("builtins.input", return_value=""),
            patch("sys.argv", ["mastodown", "download"]),
            redirect_stdout(StringIO()),
        ):
            main()

        download.assert_called_once_with(
            products,
            download_dir=None,
            proposal_subdir=True,
            target_subdir=False,
            overwrite=False,
            dry_run=False,
        )

    def test_download_cancels_when_confirmation_is_no(self):
        products = Mock()

        with (
            patch("mastodown.cli.query_obs", return_value=products),
            patch("mastodown.cli.download_products") as download,
            patch("builtins.input", return_value="n"),
            patch("sys.argv", ["mastodown", "download"]),
            redirect_stdout(StringIO()) as output,
        ):
            main()

        download.assert_not_called()
        self.assertIn("Download cancelled.", output.getvalue())
