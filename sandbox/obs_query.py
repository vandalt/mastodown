# %% [markdown]
# The [observation query](https://astroquery.readthedocs.io/en/latest/mast/mast_obsquery.html) replicates the [Web Portal](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html).
# This is the primary interface to query mast and enables queries accross multiple missions.
#
# I have a lot of scripts to query MAST for JWST programs with this interface and will try to move most of them in this file before seeing if I use it in the CLI.

# %%
from pathlib import Path

from astroquery.mast import Observations

from mastho.download import download_product

programs = ["01200", "02473"]
calib_level = [1]
extension = ["fits"]
product_type = ["SCIENCE"]
keep_TA = False
download_dir = Path("./data")
overwrite = False
dry_run = True
proposal_subdir = True
PROG_ID_LEN = 5

manifest_path = download_dir / "manifest.csv"

# %%
# Get observation table that will contain only level 3 (i2d) data
# Use this to see all possible fields: Observations.get_metadata("observations").pprint(max_lines=-1)
obs_tbl = Observations.query_criteria(
    proposal_id=programs,
    project="JWST",
    # instrument_name=["NIRISS/IMAGE", "NIRCAM/IMAGE"],
    # filters=["F480M", "F150W"],
)
display_columns = ["instrument_name", "filters", "target_name", "obs_id", "calib_level"]
print("Found the following observations:")
obs_tbl[display_columns].pprint(max_lines=-1)

# %%
# Then we get all data products associated with the observations
products_tbl = Observations.get_product_list(obs_tbl)

# %%
# Then filter to keep science and/or auxiliary, pick the calib level and extension
products_df = Observations.filter_products(
    products_tbl, productType=product_type, calib_level=calib_level, extension=extension
).to_pandas()


# %%
# Then we still need the mission interface to drop TA target from what I could tell
if not keep_TA:
    from astroquery.mast import MastMissions

    missions = MastMissions(mission="jwst")
    metadata = missions.query_criteria(
        instrume="NIRISS, NIRCAM",
        program=", ".join(str(p) for p in programs),
        select_cols=["exp_type", "fileSetName"],
    )
    metadata = metadata.to_pandas()
    metadata_img = metadata.query("exp_type not in ['NIS_TACQ', 'NIS_TACONFIRM']")

    non_ta_files = tuple(metadata_img.fileSetName)
    products_df = products_df.query("obs_id.str.startswith(@non_ta_files)").reset_index(
        drop=True
    )

# %%
# Print final data before download
total_size = sum(products_df["size"]) / 1e9
num_files = len(products_df)
print(f"Final list contains {num_files} files with total size {total_size:.2f} GB")

# %%
download_dirs = download_dir
if proposal_subdir:
    download_dirs = download_dirs / products_df.proposal_id.str.zfill(PROG_ID_LEN)

products_df["download_dir"] = download_dirs

# %%
# Handle manifest load or creation
# TODO: This should be extracted independently of download method
# TODO: Handle existing or missing files too?
# Load existing manifest if it exists
import pandas as pd

if manifest_path.exists():
    print(f"Loading existing manifest from {manifest_path}")
    existing_manifest = pd.read_csv(manifest_path)
    print(f"Found {len(existing_manifest)} previously downloaded products")
else:
    existing_manifest = pd.DataFrame()

# %%
# Filter out products already in manifest (unless overwrite is enabled)
if not existing_manifest.empty and not overwrite:
    products_to_download = products_df[
        ~products_df["obs_id"].isin(existing_manifest["obs_id"])
    ].reset_index(drop=True)
    print(
        f"Skipping {len(products_df) - len(products_to_download)} products already in manifest"
    )
else:
    products_to_download = products_df
    if overwrite and not existing_manifest.empty:
        print("Overwrite enabled: will re-download all products")


num_files = len(products_to_download)
print(f"Will download {num_files} new products")

# %%
# TODO: The looping should probs also be independent on how we get the files
# Download the files
for i, product in products_to_download.iterrows():
    download_dir = product["download_dir"]
    local_path = download_dir / product["productFilename"]
    if local_path.exists() and not overwrite:
        print(
            f"File {local_path} already exists, skipping download and adding to manifest"
        )
        continue
    elif local_path.exists() and overwrite:
        print(f"Overwriting existing file: {local_path}")
    print(f"Downloading file {i + 1}/{num_files}: {product.productFilename}")

    if not dry_run:
        download_dir.mkdir(parents=True, exist_ok=True)

        status, msg, _ = Observations.download_file(
            product["dataURI"], local_path=local_path, cache=not overwrite
        )
        if status != "COMPLETE":
            print(
                f"Download failed for product {local_path} with status {status}: {msg}"
            )

# Merge and save manifest
if not dry_run:
    updated_manifest = pd.concat(
        [existing_manifest, products_to_download], ignore_index=True
    ).drop_duplicates(subset=["obs_id"], keep="last")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    updated_manifest.to_csv(manifest_path, index=False)
    print(f"Saved manifest with {len(updated_manifest)} total products to {manifest_path}")
