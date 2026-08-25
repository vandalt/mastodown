# Getting started

<!-- TODO: Add outputs -->

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

Final list contains 8774 files with total size 649.74 Gb
       target_name      obsID obs_collection dataproduct_type                           obs_id                                        description type  ... proposal_id                                    productFilename      size parent_obsid dataRights calib_level    filters
0     WISE-1738+27   87621090           JWST            image  jw02473074001_02101_00005_nrcb1  exposure (L2a): charge trap product for persis...    S  ...        2473   jw02473074001_02101_00005_nrcb1_trapsfilled.fits  50365440     87622652     PUBLIC           2      F150W
1     WISE-1738+27   87621090           JWST            image  jw02473074001_02101_00005_nrcb1         source/target (L3) : association generator    S  ...        2473  jw02473-o074_20260725t120007_image2_00005_asn....      1803     87622652     PUBLIC           2      F150W
2     WISE-1738+27   87621090           JWST            image  jw02473074001_02101_00005_nrcb1              source/target (L3) : association pool    S  ...        2473                   jw02473_20260725t120007_pool.csv    222244     87622652     PUBLIC           2      F150W
3     WISE-1738+27   87621090           JWST            image  jw02473074001_02101_00005_nrcb1                                       Preview-Full    S  ...        2473          jw02473074001_02101_00005_nrcb1_uncal.jpg    794363     87622652     PUBLIC           1      F150W
4     WISE-1738+27   87621090           JWST            image  jw02473074001_02101_00005_nrcb1                                       Preview-Full    S  ...        2473            jw02473074001_02101_00005_nrcb1_cal.jpg   1062300     87622652     PUBLIC           2      F150W
...            ...        ...            ...              ...                              ...                                                ...  ...  ...         ...                                                ...       ...          ...        ...         ...        ...
8769      HD-93649  233595389           JWST            image    jw01200003001_03103_00001_nis                                       Preview-Full    S  ...        1200      jw01200003001_03103_00001_nis_trapsfilled.jpg     50557    233595389     PUBLIC           2  F430M;NRM
8770      HD-93649  233595389           JWST            image    jw01200003001_03103_00001_nis             exposure (L2b): 3D calibrated exposure    S  ...        1200         jw01200003001_03103_00001_nis_calints.fits  28543680    233595389     PUBLIC           2  F430M;NRM
8771      HD-93649  233595389           JWST            image    jw01200003001_03103_00001_nis  exposure (L2a): 2D count rate averaged over in...    S  ...        1200            jw01200003001_03103_00001_nis_rate.fits    201600    233595389     PUBLIC           2  F430M;NRM
8772      HD-93649  233595389           JWST            image    jw01200003001_03103_00001_nis       exposure (L2a): 3D countrate per integration    S  ...        1200        jw01200003001_03103_00001_nis_rateints.fits  23774400    233595389     PUBLIC           2  F430M;NRM
8773      HD-93649  233595389           JWST            image    jw01200003001_03103_00001_nis      exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200           jw01200003001_03103_00001_nis_uncal.fits  21372480    233595389     PUBLIC           1  F430M;NRM

[8774 rows x 21 columns]
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

Final list contains 533 files with total size 150.68 Gb
      target_name      obsID obs_collection dataproduct_type                              obs_id                                    description type  ... proposal_id                                productFilename       size parent_obsid dataRights calib_level    filters
0    WISE-1738+27   87621090           JWST            image     jw02473074001_02101_00005_nrcb1  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473     jw02473074001_02101_00005_nrcb1_uncal.fits  293659200     87622652     PUBLIC           1      F150W
1    WISE-1738+27   87621093           JWST            image     jw02473074001_02101_00003_nrcb2  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473     jw02473074001_02101_00003_nrcb2_uncal.fits  293659200     87622652     PUBLIC           1      F150W
2    WISE-1738+27   87621095           JWST            image     jw02473074001_02101_00004_nrcb1  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473     jw02473074001_02101_00004_nrcb1_uncal.fits  293659200     87622652     PUBLIC           1      F150W
3    WISE-1738+27   87621099           JWST            image     jw02473074001_02101_00005_nrcb3  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473     jw02473074001_02101_00005_nrcb3_uncal.fits  293659200     87622652     PUBLIC           1      F150W
4    WISE-1738+27   87621103           JWST            image  jw02473074001_02101_00001_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00001_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
..            ...        ...            ...              ...                                 ...                                            ...  ...  ...         ...                                            ...        ...          ...        ...         ...        ...
528      HD-95086  233545572           JWST            image       jw01200003001_03104_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03104_00001_nis_uncal.fits  472345920    232954396     PUBLIC           1  F380M;NRM
529     HD-218396  233545572           JWST            image       jw01200003001_03104_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03104_00001_nis_uncal.fits  472345920    232954397     PUBLIC           1  F380M;NRM
530     HD-218396  233595304           JWST            image       jw01200001001_03102_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200001001_03102_00001_nis_uncal.fits  263986560    232954397     PUBLIC           1  F380M;NRM
531      HD-93649  233595388           JWST            image       jw01200003001_03102_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03102_00001_nis_uncal.fits   26017920    233595388     PUBLIC           1  F480M;NRM
532      HD-93649  233595389           JWST            image       jw01200003001_03103_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03103_00001_nis_uncal.fits   21372480    233595389     PUBLIC           1  F430M;NRM

[533 rows x 21 columns]
```

### Query by filter

With a few filters, we narrowed down the search to "only" 150 Gb.
NIRCam data from the blue channel is particularly voluminous because it includes four detectors.
We can include only the mid-IR filters to reduce the data volume significantly:

```console
$ mastodown query --programs 01200 02473 --calib-level 1 --product-type SCIENCE --extension fits --filters F480M F430M F380M

Final list contains 113 files with total size 32.38 Gb
      target_name      obsID obs_collection dataproduct_type                              obs_id                                    description type  ... proposal_id                                productFilename       size parent_obsid dataRights calib_level    filters
0    WISE-1738+27   87621103           JWST            image  jw02473074001_02101_00001_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00001_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
1    WISE-1738+27   87621129           JWST            image  jw02473074001_02101_00004_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00004_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
2    WISE-1738+27   87621135           JWST            image  jw02473074001_02101_00005_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00005_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
3    WISE-1738+27   87621145           JWST            image  jw02473074001_02101_00002_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00002_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
4    WISE-1738+27   87621150           JWST            image  jw02473074001_02101_00003_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00003_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
..            ...        ...            ...              ...                                 ...                                            ...  ...  ...         ...                                            ...        ...          ...        ...         ...        ...
108      HD-95086  233545572           JWST            image       jw01200003001_03104_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03104_00001_nis_uncal.fits  472345920    232954396     PUBLIC           1  F380M;NRM
109     HD-218396  233545572           JWST            image       jw01200003001_03104_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03104_00001_nis_uncal.fits  472345920    232954397     PUBLIC           1  F380M;NRM
110     HD-218396  233595304           JWST            image       jw01200001001_03102_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200001001_03102_00001_nis_uncal.fits  263986560    232954397     PUBLIC           1  F380M;NRM
111      HD-93649  233595388           JWST            image       jw01200003001_03102_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03102_00001_nis_uncal.fits   26017920    233595388     PUBLIC           1  F480M;NRM
112      HD-93649  233595389           JWST            image       jw01200003001_03103_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03103_00001_nis_uncal.fits   21372480    233595389     PUBLIC           1  F430M;NRM

[113 rows x 21 columns]
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

Final list contains 113 files with total size 32.38 Gb
      target_name      obsID obs_collection dataproduct_type                              obs_id                                    description type  ... proposal_id                                productFilename       size parent_obsid dataRights calib_level    filters
0    WISE-1738+27   87621103           JWST            image  jw02473074001_02101_00001_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00001_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
1    WISE-1738+27   87621129           JWST            image  jw02473074001_02101_00004_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00004_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
2    WISE-1738+27   87621135           JWST            image  jw02473074001_02101_00005_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00005_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
3    WISE-1738+27   87621145           JWST            image  jw02473074001_02101_00002_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00002_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
4    WISE-1738+27   87621150           JWST            image  jw02473074001_02101_00003_nrcblong  exposure (L1b): Uncalibrated 4D exposure data    S  ...        2473  jw02473074001_02101_00003_nrcblong_uncal.fits  293659200     87622666     PUBLIC           1      F480M
..            ...        ...            ...              ...                                 ...                                            ...  ...  ...         ...                                            ...        ...          ...        ...         ...        ...
108      HD-95086  233545572           JWST            image       jw01200003001_03104_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03104_00001_nis_uncal.fits  472345920    232954396     PUBLIC           1  F380M;NRM
109     HD-218396  233545572           JWST            image       jw01200003001_03104_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03104_00001_nis_uncal.fits  472345920    232954397     PUBLIC           1  F380M;NRM
110     HD-218396  233595304           JWST            image       jw01200001001_03102_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200001001_03102_00001_nis_uncal.fits  263986560    232954397     PUBLIC           1  F380M;NRM
111      HD-93649  233595388           JWST            image       jw01200003001_03102_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03102_00001_nis_uncal.fits   26017920    233595388     PUBLIC           1  F480M;NRM
112      HD-93649  233595389           JWST            image       jw01200003001_03103_00001_nis  exposure (L1b): Uncalibrated 4D exposure data    S  ...        1200       jw01200003001_03103_00001_nis_uncal.fits   21372480    233595389     PUBLIC           1  F430M;NRM

[113 rows x 21 columns]
Continue with download (dry run, no modifications will happen on disk)? [Y/n] Will download 113 data products
Downloading file: data/02473/jw02473074001_02101_00001_nrcblong_uncal.fits
[...]
Downloaded 113 data products
```

To view quick recipes for other use cases, see the {doc}`command line recipes <cli-recipes>`.
To view all command line commands and options, see the {doc}`command reference <cli-reference>`.
