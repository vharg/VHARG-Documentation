# Download ERA5 data to the Komodo cluster @ NTU/ASE :volcano: :tiger2:

  - [Intro](#intro)
  - [Download wind data](#download-wind-data)

## Intro
Try to download wind data (appropriately named) to ```/home/volcano/Wind/``` so that others have access if needed. 
List loaded modules with ```module list```. Required modules are:

```
module add python/3.5.3
```

You will also need to make an account and then download your API key from CDS:
https://cds.climate.copernicus.eu/api-how-to

The API key should be placed in your account here: ```~/.cdsapirc```

## Download wind data
Go to: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form and choose what wind data you want.
Typically, you need 'geopotential', 'U-component of wind', and 'V-component of wind' to get wind speed and direction with height for a volcano.
You can choose the area to cover, years and hourly or less temporal resolution.

Click 'NetCDF' as the format and then 'Show API request'

Copy and paste this request into a new file on the cluster that describes what you're downloading, e.g.:
```vi ERA5_Hrly_2010-2019_FujiDownload.py```
Press ```Esc```, then ```:wq``` to save the file

To run it, ssh to a node (do not run on the main master node!): ```qsub -I```
navigate to where you were: ```cd /home/volcano/WindDownload``` and to run, type (for the example above): ```python3 ERA5_Hrly_2010-2019_FujiDownload.py```
