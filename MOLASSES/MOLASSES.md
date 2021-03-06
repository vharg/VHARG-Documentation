MOLASSES is a model for simulating lava flow

# Simulating deterministic and probabilistic lava flow inundation using MOLASSES

## Introduction

The MOLASSES code (https://github.com/geoscience-community-codes/MOLASSES) is operational on Komodo, but not parallelised. There are a number of files needed to run the code:

- A DEM, the higher resolution the DEM the longer the runtime. 
- A Vent location if running deterministically, or a kernel density map if running probabilistically with variability in the vent location.
- The config file, which shows the location of the files and the range of inputs (probabilistic) such as thickness (residual) and the number of flows to simulate.

The code runs in perl and requires the following modules: ??

##TO FINISH
## Preparation of inputs

Each run of the ECMapProb code needs its own `input_data.py` file with the parameters for that particular simulation. The following parameters must be edited:

run_name = [desired name of your output file folder]

source_dem = [1 or 2]
- 1 should be used if you would like the program to automatically import the SRTM30 DEM. If this is the case, under "Map limits", you must input "lat1 = [latitude in decimal degrees]",lat2,long1,long2 to tell the program where to clip the DEM
- 2 should be used if you would like to import a DEM (in .txt/.asc format which must be in UTM). If this is the case, you should remove the lines for lat1,lat2,long1,long2 and add the line "topography_file = [filename]"

cone_levels = [30]
- leave as default

dist_source = [1]
- leave as default

lon_cen/lat_cen OR east_cen/north_cen = [collapse location in decimal degree or UTM coordinates]
- set to most likely location of vent for a new eruption

var_cen = [uncertainty radius of collapse location in meters]
- based on measurement of crater or summit area

height = [height of the collapse in meters]
- 10% of the total eruption column height is a good value, based on Wilson et al. (1978)

hl = [H/L ratio]
- flowdat database is a good place to source analogues or generalised values and uncertainties

var_height = [uncertainty of the collapse height in meters]

var_hl = [uncertainty of the H/L ratio]

dist_input = [1]
- set at 1 for uniform distribution of H/L and height values

N = [number of simulations, 300 seems sufficient]

save_data = [1]
- leave as default

redist_energy = [4]
- leave as default

## Running ECMapProb.py

1. Navigate to the folder containing the `ECMapProb.py` file
2. Make sure this folder also contains `input_data.py`, `Cities.txt`, and the appropriate DEM file if using.
3. Run `ECMapProb.py`
4. The program will run in a terminal window. A 300 simulation run can take from ~1-4 hours, largely dependent upon the complexity of topography surrounding the volcano.
5. When the simulations are finished, a series of files will be saved in folder within the current folder including the `output_map.asc` file which is the energy cone probability map.
