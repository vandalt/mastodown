from pathlib import Path

from astropy.table import Row
from astroquery.mast import (
    Observations,
)
from pandas import DataFrame, Series, concat, read_csv

PROG_ID_LEN = 5


def update_manifest(manifest: DataFrame, new_products: DataFrame) -> DataFrame:
    manifest = concat([manifest, new_products], ignore_index=True).drop_duplicates(
        subset=["obs_id"], keep="last"
    )
    return manifest


# 1. File in manifest:
#     1. On disk -> good, do nothing unless ovewrite
#     2. Not on disk -> report and download
# 2. File not in manifest:
#     1. On disk -> report and add to manifest
#     2. Not on disk -> download normally
def check_manifest(products: DataFrame, manifest: DataFrame, overwrite: bool = False):

    # if existing_manifest.empty:
    products_on_disk = products["local_path"].apply(lambda x: x.exists())
    products_in_manifest = products["obs_id"].isin(manifest["obs_id"])

    products_in_manifest_not_disk = products[products_in_manifest & ~products_on_disk]
    products_not_manifest_on_disk = products[~products_in_manifest & products_on_disk]

    n_missing_disk = len(products_in_manifest_not_disk)
    if n_missing_disk != 0:
        print(
            f"WARNING: There are {n_missing_disk} files in the manifest missing on disk. Downloading them."
        )

    n_missing_manifest = len(products_not_manifest_on_disk)
    if n_missing_manifest != 0:
        print(
            f"WARNING: There are {n_missing_manifest} files on disk missing in the manifest. Adding them to the manifest."
        )
        manifest = update_manifest(manifest, products_not_manifest_on_disk)

    if overwrite and products_on_disk.any():
        n_on_disk = len(products_on_disk)
        print(
            f"Overwrite is enabled. {n_on_disk} files already on disk will be re-downloaded."
        )
    products_to_download = products[~products_on_disk | overwrite]
    manifest = update_manifest(manifest, products_to_download)

    return products_to_download, manifest


# TODO: Support table as well
# TODO: Decide how to handle downlaod_dir/path
def download_products(
    products: DataFrame,
    download_dir: Path | str | None = None,
    proposal_subdir: bool = True,
    overwrite: bool = False,
    dry_run: bool = False,
):
    products = products.copy()

    if download_dir is None:
        download_dir = "."
    download_dir = Path(download_dir)
    if proposal_subdir:
        download_dirs = download_dir / products.proposal_id.str.zfill(PROG_ID_LEN)
    else:
        download_dirs = download_dir
    products["download_dir"] = download_dirs
    products["local_path"] = products["download_dir"] / products["productFilename"]

    manifest_path = download_dir / "manifest.csv"
    if manifest_path.exists():
        print(f"Loading existing manifest from {manifest_path}")
        manifest = read_csv(manifest_path)
        print(f"Found {len(manifest)} previously downloaded products")
    else:
        manifest = DataFrame()

    products_to_download, manifest = check_manifest(
        products, manifest, overwrite=overwrite
    )

    num_files = len(products_to_download)
    print(f"Will download {num_files} data products")

    for i, product in products.iterrows():
        download_product(product, overwrite=overwrite, dry_run=dry_run)

    if not dry_run:
        manifest.to_csv(manifest_path, index=False)
        print(f"Saved manifest with {len(manifest)} data products to {manifest_path}")


def download_product(
    product: Series | Row, overwrite: bool = False, dry_run: bool = False
):
    local_path = Path(product.local_path)
    # TODO: Uniform/flexible keys for mission
    if local_path.exists() and not overwrite:
        print(
            f"File {local_path} already exists, skipping download and not adding to manifest"
        )
        return
    elif local_path.exists() and overwrite:
        print(f"Overwriting existing file: {local_path}")
    else:
        print(f"Downloading file: {local_path}")

    if dry_run:
        return

    local_path.parent.mkdir(parents=True, exist_ok=True)

    # TODO: Decide on type/what to call for the download
    status, msg, _ = Observations.download_file(
        product["dataURI"], local_path=local_path, cache=not overwrite
    )
    if status != "COMPLETE":
        print(f"Download failed for product {local_path} with status {status}: {msg}")
