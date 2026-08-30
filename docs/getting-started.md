# Getting started

Mastodown is primarily intended as a command line tool.
For complex Python scripts, use the [MAST module from Astroquery](https://astroquery.readthedocs.io/en/latest/mast/mast.html) directly.

The typical workflow to download data has two steps:

1. Querying MAST to preview a table of data products
2. Downloading the data products on disk

We will illustrate this through an example where we download data from two cycle 1 JWST programs: [GO 2473](https://www.stsci.edu/jwst/science-execution/program-information?id=2473) and [GTO 1200](https://www.stsci.edu/jwst/science-execution/program-information?id=1200).

## Query MAST to preview data products

### Query by program

First, we will query MAST to get a preview of all data products in the two programs:

```console
$ mastodown query --programs 01200 02473

Final list contains 8172 files with total size 646.28 Gb
       target_name      obsID obs_collection dataproduct_type                                        obs_id  ...      size parent_obsid dataRights calib_level    filters
0        HD-218396  232954397           JWST     measurements     jw01200-c1001_t001_niriss_f380m-nrm-sub80  ...  41808960    232954397     PUBLIC           3  F380M;NRM
1        HD-218396  232954397           JWST     measurements     jw01200-c1001_t001_niriss_f380m-nrm-sub80  ...      4371    232954397     PUBLIC           3  F380M;NRM
2         HD-95086  232307010           JWST            image  jw01200-c1001_t002_niriss_clearp-f380m-sub80  ...       996    232307010     PUBLIC           3      F380M
3         HD-95086  232307010           JWST            image  jw01200-c1001_t002_niriss_clearp-f380m-sub80  ...     17530    232307010     PUBLIC           3      F380M
4         HD-95086  232307010           JWST            image  jw01200-c1001_t002_niriss_clearp-f380m-sub80  ...    103680    232307010     PUBLIC           3      F380M
...            ...        ...            ...              ...                                           ...  ...       ...          ...        ...         ...        ...
8167  WISE-1738+27   87621135           JWST            image            jw02473074001_02101_00005_nrcblong  ...   1130005     87622666     PUBLIC           2      F480M
8168  WISE-1738+27   87621135           JWST            image            jw02473074001_02101_00005_nrcblong  ...   1163380     87622666     PUBLIC           2      F480M
8169  WISE-1738+27   87621135           JWST            image            jw02473074001_02101_00005_nrcblong  ...    875335     87622666     PUBLIC           2      F480M
8170  WISE-1738+27   87621135           JWST            image            jw02473074001_02101_00005_nrcblong  ...    978355     87622666     PUBLIC           1      F480M
8171  WISE-1738+27   87621135           JWST            image            jw02473074001_02101_00005_nrcblong  ...   1231484     87622666     PUBLIC           2      F480M

[8172 rows x 21 columns]
```

This yields _a lot_ of data (almost 700 Gb).
We can try to filter this a bit more. See `mastodown query -h` to view all the filters available.

### Query by calibration level and file type

We will add the following constraints:

1. Only download uncalibrated (`uncal`) files with `calib_level=1`
2. Only download FITS files
3. Only download science files and ignore auxiliary products

```console
$ mastodown query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits

INFO: 757 of 9062 products were duplicates. Only returning 8305 unique product(s). [astroquery.mast.utils]
INFO: To return all products, use `Observations.get_product_list` [astroquery.mast.observations]
Final list contains 531 files with total size 150.19 Gb
      target_name      obsID obs_collection dataproduct_type                              obs_id  ...        size parent_obsid dataRights calib_level    filters
0       HD-218396  233595304           JWST            image       jw01200001001_03102_00001_nis  ...   263986560    232954397     PUBLIC           1  F380M;NRM
1        HD-95086  233545519           JWST            image       jw01200002001_03102_00001_nis  ...  1504627200    232954396     PUBLIC           1  F380M;NRM
2        HD-95086  159534944           JWST            image       jw01200002001_03103_00001_nis  ...    19290240    159513319     PUBLIC           1      F380M
3        HD-93649  233595388           JWST            image       jw01200003001_03102_00001_nis  ...    26017920    233595388     PUBLIC           1  F480M;NRM
4        HD-93649  233595389           JWST            image       jw01200003001_03103_00001_nis  ...    21372480    233595389     PUBLIC           1  F430M;NRM
..            ...        ...            ...              ...                                 ...  ...         ...          ...        ...         ...        ...
526  WISE-1738+27   87621090           JWST            image     jw02473074001_02101_00005_nrcb1  ...   293659200     87622652     PUBLIC           1      F150W
527  WISE-1738+27   87621139           JWST            image     jw02473074001_02101_00005_nrcb2  ...   293659200     87622652     PUBLIC           1      F150W
528  WISE-1738+27   87621099           JWST            image     jw02473074001_02101_00005_nrcb3  ...   293659200     87622652     PUBLIC           1      F150W
529  WISE-1738+27   87621125           JWST            image     jw02473074001_02101_00005_nrcb4  ...   293659200     87622652     PUBLIC           1      F150W
530  WISE-1738+27   87621135           JWST            image  jw02473074001_02101_00005_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M

[531 rows x 21 columns]
```

### Query by filter

With a few filters, we narrowed down the search to "only" 150 Gb.
NIRCam data from the blue channel is particularly voluminous because it includes four detectors.
We can include only the mid-IR filters to reduce the data volume significantly:

```console
$ mastodown query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits --filters F480M F430M F380M

Final list contains 111 files with total size 31.88 Gb
      target_name      obsID obs_collection dataproduct_type                              obs_id  ...        size parent_obsid dataRights calib_level    filters
0       HD-218396  233595304           JWST            image       jw01200001001_03102_00001_nis  ...   263986560    232954397     PUBLIC           1  F380M;NRM
1        HD-95086  233545519           JWST            image       jw01200002001_03102_00001_nis  ...  1504627200    232954396     PUBLIC           1  F380M;NRM
2        HD-95086  159534944           JWST            image       jw01200002001_03103_00001_nis  ...    19290240    159513319     PUBLIC           1      F380M
3        HD-93649  233595388           JWST            image       jw01200003001_03102_00001_nis  ...    26017920    233595388     PUBLIC           1  F480M;NRM
4        HD-93649  233595389           JWST            image       jw01200003001_03103_00001_nis  ...    21372480    233595389     PUBLIC           1  F430M;NRM
..            ...        ...            ...              ...                                 ...  ...         ...          ...        ...         ...        ...
106  WISE-1738+27   87621103           JWST            image  jw02473074001_02101_00001_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
107  WISE-1738+27   87621145           JWST            image  jw02473074001_02101_00002_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
108  WISE-1738+27   87621150           JWST            image  jw02473074001_02101_00003_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
109  WISE-1738+27   87621129           JWST            image  jw02473074001_02101_00004_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
110  WISE-1738+27   87621135           JWST            image  jw02473074001_02101_00005_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M

[111 rows x 21 columns]
```

Note that we could also save the results of the query by adding the `-o <filename.csv>` flag.
This is useful to further inspect or manipulate the query (in a text editor or with Pandas, for example).

## Downloading data

Now that we have our final query, we can download the data.
All CLI arguments from `mastodown query` are re-usable in `mastodown download`.
In addition, we will specify the download directory with `--download-dir` and
we will make this run a "dry run" that only scans the archive but does not download any files with the `--dry-run` flag.

This command performs a query and then prompts the user to confirm that data should be downloaded.
To skip the prompt, simply add the `--yes` or `-y` flag to the command.

To actually download the data, remove the `--dry-run` flag.

```console
$ mastodown download --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits --filters F480M F430M F380M --download-dir data --dry-run

Final list contains 111 files with total size 31.88 Gb
      target_name      obsID obs_collection dataproduct_type                              obs_id  ...        size parent_obsid dataRights calib_level    filters
0       HD-218396  233595304           JWST            image       jw01200001001_03102_00001_nis  ...   263986560    232954397     PUBLIC           1  F380M;NRM
1        HD-95086  233545519           JWST            image       jw01200002001_03102_00001_nis  ...  1504627200    232954396     PUBLIC           1  F380M;NRM
2        HD-95086  159534944           JWST            image       jw01200002001_03103_00001_nis  ...    19290240    159513319     PUBLIC           1      F380M
3        HD-93649  233595388           JWST            image       jw01200003001_03102_00001_nis  ...    26017920    233595388     PUBLIC           1  F480M;NRM
4        HD-93649  233595389           JWST            image       jw01200003001_03103_00001_nis  ...    21372480    233595389     PUBLIC           1  F430M;NRM
..            ...        ...            ...              ...                                 ...  ...         ...          ...        ...         ...        ...
106  WISE-1738+27   87621103           JWST            image  jw02473074001_02101_00001_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
107  WISE-1738+27   87621145           JWST            image  jw02473074001_02101_00002_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
108  WISE-1738+27   87621150           JWST            image  jw02473074001_02101_00003_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
109  WISE-1738+27   87621129           JWST            image  jw02473074001_02101_00004_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M
110  WISE-1738+27   87621135           JWST            image  jw02473074001_02101_00005_nrcblong  ...   293659200     87622666     PUBLIC           1      F480M

[111 rows x 21 columns]
Continue with download (dry run, no modifications will happen on disk)? [Y/n]   
Will download 111 data products
Downloading file: data/01200/jw01200001001_03102_00001_nis_uncal.fits
[...]
Downloaded 111 data products
```

To view quick recipes for other use cases, see the {doc}`command line recipes <cli-recipes>`.
To view all command line commands and options, see the {doc}`command reference <cli-reference>`.
