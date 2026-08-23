from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from pandas import DataFrame

import mastho.download as download
from mastho.download import check_manifest, download_products


def products_for(directory: Path) -> DataFrame:
    return DataFrame(
        {
            "obs_id": ["observation-1"],
            "proposal_id": ["1"],
            "productFilename": ["product.fits"],
            "dataURI": ["mast:example/product.fits"],
            "local_path": [directory / "product.fits"],
        }
    )


class CheckManifestTests(TestCase):
    def test_empty_manifest_treats_product_as_missing(self):
        with TemporaryDirectory() as directory:
            products = products_for(Path(directory))

            products_to_download, manifest = check_manifest(products, DataFrame())

        self.assertEqual(products_to_download["obs_id"].tolist(), ["observation-1"])
        self.assertTrue(manifest.empty)


class DownloadProductsTests(TestCase):
    def test_failed_download_is_not_added_to_manifest(self):
        with TemporaryDirectory() as directory:
            product = products_for(Path(directory)).drop(columns=["local_path"])
            with patch(
                "mastho.download.Observations.download_file",
                return_value=("ERROR", "download failed", None),
            ):
                download_products(product, download_dir=directory, proposal_subdir=False)

            manifest_path = Path(directory) / "manifest.csv"
            self.assertTrue(manifest_path.exists())
            self.assertNotIn("observation-1", manifest_path.read_text())

    def test_dry_run_adds_planned_products_without_writing_manifest(self):
        with TemporaryDirectory() as directory:
            product = products_for(Path(directory)).drop(columns=["local_path"])
            with patch(
                "mastho.download.update_manifest",
                wraps=download.update_manifest,
            ) as update_manifest:
                download_products(
                    product, download_dir=directory, proposal_subdir=False, dry_run=True
                )

            self.assertEqual(
                update_manifest.call_args.args[1]["obs_id"].tolist(), ["observation-1"]
            )
            self.assertFalse((Path(directory) / "manifest.csv").exists())
