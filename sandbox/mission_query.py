# %% [markdown]
# The [mission queries](https://astroquery.readthedocs.io/en/latest/mast/mast_missions.html) interface is intended to search a specific mission at a time.
# Since I only query JWST data, this is probably the easiest path forward so I'm trying to set up a script with that in addition to the observation query (see obs_query.py).

# %%
from pathlib import Path

from astroquery.mast import MastMissions

m = MastMissions(mission="jwst")

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

# %%
# This will print onlyh the name because the description has a weird format
m.get_column_list().pprint(max_lines=-1)

# %%
# If we want the descriptions too
m.get_column_list()[["name", "description"]].pprint_all()

# %%
datasets = m.query_criteria(program=programs).to_pandas()

# %%
if not keep_TA:
    datasets = datasets.query("exp_type not in ['NIS_TACQ', 'NIS_TACONFIRM']").reset_index(drop=True)

# %%
from astropy.table import Table
# products_tbl = m.get_unique_product_list(Table.from_pandas(datasets))
dataset_list = datasets[m.get_dataset_kwd()].tolist()
products_tbl = m.get_unique_product_list(dataset_list)

# %%
products_tbl = m.filter_products(
    products_tbl, extension="fits", type="science", file_suffix=["_uncal"]
)
