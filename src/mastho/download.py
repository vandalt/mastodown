from pathlib import Path

from astroquery.mast import (
    Observations,
)
from pandas import DataFrame, Series, concat, read_csv

PROG_ID_LEN = 5


def update_manifest(manifest: DataFrame, new_products: DataFrame) -> DataFrame:
    """Update the manifest dataframe with new data products

    New data products have priority if there are duplicates

    :param manifest: The manifest dataframe
    :param new_products: The new data products to add
    :return: The updated manifest
    """
    manifest = concat([manifest, new_products], ignore_index=True).drop_duplicates(
        subset=["obs_id"], keep="last"
    )
    return manifest


def check_manifest(products: DataFrame, manifest: DataFrame, overwrite: bool = False) -> tuple[DataFrame, DataFrame]:
    """Check the products to download against the manifest

    Some things to note:

    - If ``overwrite`` is True, all products will be downloaded.
    - If a file is in the manifest but missing on disk, it will be downloaded
    - If a file is on disk but not in the manifest, it will be added to the manifest

    :param products: Data products to download
    :param manifest: Manifest dataframe
    :param overwrite: Whether existing files should be overwritten
    :return: The subset of ``products`` which should be downloaded
    """
    products_on_disk = products["local_path"].apply(lambda x: x.exists())
    if not manifest.empty:
        products_in_manifest = products["obs_id"].isin(manifest["obs_id"])
    else:
        products_in_manifest = Series(False, index=products.index)

    products_in_manifest_not_disk = products[products_in_manifest & ~products_on_disk]
    products_not_manifest_on_disk = products[~products_in_manifest & products_on_disk]

    n_missing_disk = len(products_in_manifest_not_disk)
    if n_missing_disk != 0:
        # TODO: Use logging for all these warnings
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
        n_on_disk = products_on_disk.sum()
        print(
            f"Overwrite is enabled. {n_on_disk} files already on disk will be re-downloaded."
        )
    products_to_download = products[~products_on_disk | overwrite]

    return products_to_download, manifest


def download_products(
    products: DataFrame,
    download_dir: Path | str | None = None,
    proposal_subdir: bool = True,
    overwrite: bool = False,
    dry_run: bool = False,
):
    """Download data products from mast

    :param products: Dataframe of data products to download
    :param download_dir: Parent download directory
    :param proposal_subdir: Whether each proposal ID should have its
                            subdirectory in ``download_dir``. Deults to True
    :param overwrite: Whether existing files should be overwritten. Defaults to False
    :param dry_run: Whether this is a dry-run where no I/O happens. Defaults to False
    """
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

    successful_indices = []
    for index, product in products_to_download.iterrows():
        if download_product(product, overwrite=overwrite, dry_run=dry_run):
            successful_indices.append(index)
    if successful_indices:
        manifest = update_manifest(
            manifest, products_to_download.loc[successful_indices]
        )
    n_success = len(successful_indices)
    n_total = len(products_to_download)
    if n_success < n_total:
        print(
            f"WARNING: Download failed for {n_total - n_success} out of {n_total} products"
        )
    print(f"Downloaded {n_success} data products")

    if not dry_run:
        manifest.to_csv(manifest_path, index=False)
        print(f"Saved manifest with {len(manifest)} data products to {manifest_path}")


# TODO: Check the link to download_products
def download_product(
    product: Series, overwrite: bool = False, dry_run: bool = False
) -> bool:
    """Download a single data product from MAST

    Called by :func:`download_products`.

    :param product: The info on the data product to download as a pandas series
    :param overwrite: Whether existing files should be overwritten. Defaults to False
    :param dry_run: Whether this is a dry-run where no I/O happens. Defaults to False
    :return: True if the download was successful, False otherwise
    """
    local_path = Path(product.local_path)
    # TODO: Uniform/flexible keys for mission
    if local_path.exists() and not overwrite:
        print(f"File {local_path} already exists, skipping download")
        return True
    elif local_path.exists() and overwrite:
        print(f"Overwriting existing file: {local_path}")
    else:
        print(f"Downloading file: {local_path}")

    if dry_run:
        return True

    local_path.parent.mkdir(parents=True, exist_ok=True)

    # TODO: Decide on type/what to call for the download
    status, msg, _ = Observations.download_file(
        product["dataURI"], local_path=local_path, cache=not overwrite
    )
    if status != "COMPLETE":
        print(f"Download failed for product {local_path} with status {status}: {msg}")
        return False

    return True
