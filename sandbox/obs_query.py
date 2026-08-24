# %% [markdown]
# The [observation query](https://astroquery.readthedocs.io/en/latest/mast/mast_obsquery.html) replicates the [Web Portal](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html).
# This is the primary interface to query mast and enables queries accross multiple missions.
#
# I have a lot of scripts to query MAST for JWST programs with this interface and will try to move most of them in this file before seeing if I use it in the CLI.

# %%
from pathlib import Path

from mastodown.download import download_products
from mastodown.query import query_obs

programs = ["01200", "02473"]
calib_level = [1]
extension = ["fits"]
product_type = ["SCIENCE"]
keep_TA = False
download_dir = Path("./data")
overwrite = False
dry_run = True


# %%
products = query_obs(
    programs=programs,
    calib_level=calib_level,
    product_type=product_type,
    extension=extension,
    keep_ta=keep_TA,
)

download_products(products, download_dir=download_dir, overwrite=overwrite, dry_run=dry_run)
