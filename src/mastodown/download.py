import logging
from pathlib import Path
from re import sub

from astroquery.mast import (
    Observations,
)
from pandas import DataFrame, Series, concat, read_csv

PROG_ID_LEN = 5
logger = logging.getLogger(__name__)


def target_directory_name(target_name: str) -> str:
    """Return a readable filesystem-safe directory name for a MAST target."""
    directory_name = sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", target_name).strip(" .")
    return directory_name or "unknown-target"


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


def check_manifest(
    products: DataFrame, manifest: DataFrame, overwrite: bool = False
) -> tuple[DataFrame, DataFrame]:
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
        logger.warning(
            "%d files in the manifest are missing on disk; downloading them.",
            n_missing_disk,
        )

    n_missing_manifest = len(products_not_manifest_on_disk)
    if n_missing_manifest != 0:
        logger.warning(
            "%d files on disk are missing from the manifest; adding them to the manifest.",
            n_missing_manifest,
        )
        manifest = update_manifest(manifest, products_not_manifest_on_disk)

    if overwrite and products_on_disk.any():
        n_on_disk = products_on_disk.sum()
        logger.info(
            "Overwrite is enabled; %d files already on disk will be re-downloaded.",
            n_on_disk,
        )
    products_to_download = products[~products_on_disk | overwrite]

    return products_to_download, manifest


def download_products(
    products: DataFrame,
    download_dir: Path | str | None = None,
    proposal_subdir: bool = True,
    target_subdir: bool = False,
    overwrite: bool = False,
    dry_run: bool = False,
) -> DataFrame:
    """Download data products from mast

    :param products: Dataframe of data products to download
    :param download_dir: Parent download directory
    :param proposal_subdir: Whether each proposal ID should have its
                            subdirectory in ``download_dir``. Deults to True
    :param target_subdir: Whether each target name should have its subdirectory
                          in the proposal or download directory. Defaults to False
    :param overwrite: Whether existing files should be overwritten. Defaults to False
    :param dry_run: Whether this is a dry-run where no I/O happens. Defaults to False
    :return: The products data frame with any modifications (mainly the `local_path` key) applied
    """
    products = products.copy()

    if download_dir is None:
        download_dir = "."
    download_dir = Path(download_dir)
    if proposal_subdir:
        download_dirs = download_dir / products.proposal_id.str.zfill(PROG_ID_LEN)
    else:
        download_dirs = download_dir
    if target_subdir:
        download_dirs = download_dirs / products.target_name.map(target_directory_name)
    products["download_dir"] = download_dirs
    products["local_path"] = products["download_dir"] / products["productFilename"]

    manifest_path = download_dir / "manifest.csv"
    if manifest_path.exists():
        logger.info("Loading existing manifest from %s", manifest_path)
        manifest = read_csv(manifest_path)
        logger.info("Found %d previously downloaded products", len(manifest))
    else:
        manifest = DataFrame()

    products_to_download, manifest = check_manifest(
        products, manifest, overwrite=overwrite
    )

    num_files = len(products_to_download)
    logger.info("Will download %d data products", num_files)

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
        logger.warning(
            "Download failed for %d out of %d products", n_total - n_success, n_total
        )
    logger.info("Downloaded %d data products", n_success)

    if not dry_run:
        manifest.to_csv(manifest_path, index=False)
        logger.info(
            "Saved manifest with %d data products to %s", len(manifest), manifest_path
        )
    return products


def download_product(
    product: Series,
    overwrite: bool = False,
    dry_run: bool = False,
    download_dir: Path | str | None = None,
) -> Path | bool:
    """Download a single data product from MAST

    Called by :func:`download_products`.

    :param product: The info on the data product to download as a pandas series
    :param overwrite: Whether existing files should be overwritten. Defaults to False
    :param dry_run: Whether this is a dry-run where no I/O happens. Defaults to False
    :param download_dir: Directory where the file will be downloaded. If ``local_path``
                         is a key in the product, ``download_dir`` is ignored.
                         Defaults to `None` which will download the file in the current directory.
    :return: The path if the download was successful, False otherwise
    """
    if "local_path" in product:
        local_path = Path(product.local_path)
    else:
        if download_dir is None:
            download_dir = "."
        download_dir = Path(download_dir)
        local_path = download_dir / product["productFilename"]
    if local_path.exists() and not overwrite:
        logger.info("File %s already exists; skipping download", local_path)
        return local_path
    elif local_path.exists() and overwrite:
        logger.info("Overwriting existing file: %s", local_path)
    else:
        logger.info("Downloading file: %s", local_path)

    if dry_run:
        return local_path

    local_path.parent.mkdir(parents=True, exist_ok=True)

    status, msg, _ = Observations.download_file(
        product["dataURI"], local_path=local_path, cache=not overwrite
    )
    if status != "COMPLETE":
        logger.error(
            "Download failed for product %s with status %s: %s",
            local_path,
            status,
            msg,
        )
        return False

    return local_path
