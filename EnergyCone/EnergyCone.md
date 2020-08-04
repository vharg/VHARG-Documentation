# Running Energy Cone models via the ECMapProb Code

## Introduction

The ECMapProb code (Aravena et al. 2020) is run in a terminal window in python, and has two versions: `Friendly_ECMapProb.py` and `ECMapProb.py`. When the friendly file is run in python, it opens an intuitive GUI with self-explanatory fields for inputs and steps for running the program. However, it is much more efficient to run many energy cone models consecutively or concurrently by running the `ECMapProb.py` in the terminal.

All files necessary to run the code can be downloaded from the GitHub of Alvaro Aravena here: https://github.com/AlvaroAravena/ECMapProb

The code runs in python3 and requires the following modules: matplotlib, numpy, elevation, Pillow, utm, and tifffile. Some of the modules are difficult to install in the current version of python3, all work well in the Anaconda environment.

## Preparation of inputs

Each run of the ECMapProb code needs its own `input_data.py` file with the parameters for that particular simulation. The following paramters must be edited:

run_name = [desired name of your output file folder]

source_dem = [1 or 2]
- 1 should be used if you would like the program to automatically import the SRTM30 DEM. If this is the case, under "Map limits", you must input "lat1 = [latitude in decimal degrees]",lat2,long1,long2 to tell the program where to clip the DEM
- 2 should be used if you would like to import a DEM (in .txt/.asc format which must be in UTM). If this is the case, you should remove the lines for lat1,lat2,long1,long2 and add the line "topography_file = [filename]"

cone_levels = [30]

dist_source = [1]

lon_cen/lat_cen OR east_cen/north_cen = [collapse location in decimal degree or UTM coordinates]

var_cen = [uncertainty of collapse location in meters]

height = [height of the collapse in meters]

hl = [H/L ratio]

var_height = [uncertainty of the collapse height in meters]

var_hl = [uncertainty of the H/L ratio]

dist_input = [1]

N = [number of simulations, 300 seems sufficient]

save_data = [1]

redist_energy = [4]

## Running ECMapProb.py

1. Navigate to the folder containing the `ECMapProb.py` file
2. Make sure this folder also contains `input_data.py`, `Cities.txt`, and the appropriate DEM file if using.
3. Run `ECMapProb.py`
4. The program will run in a terminal window. A 300 simulation run can take from ~1-4 hours, largely dependent upon the complexity of topography surrounding the volcano.
5. When the simulations are finished, a series of files will be saved in folder within the current folder including the `output_map.asc` file which is the energy cone probability map.
