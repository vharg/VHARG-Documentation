MOLASSES is a model for simulating lava flow

# Simulating deterministic and probabilistic lava flow inundation using MOLASSES

## Introduction

The MOLASSES code (https://github.com/geoscience-community-codes/MOLASSES) is operational on Komodo, but not parallelised. There are a number of files needed to run the code:

- A DEM, the higher resolution the DEM the longer the runtime. 
- A Vent location if running deterministically, or a kernel density map if running probabilistically with variability in the vent location.
- The config file, which shows the location of the files and the range of inputs (probabilistic) such as thickness (residual) and the number of flows to simulate.

The code runs in perl and requires the following modules on Komodo: 
openmpi/1.4.5-gnu
GMT/5.4.1/gnu

## Preparation of inputs

Copy config.laos to your own configuration file, e.g. config.gede, and edit the copied file for:
- DEM_FILE location
- SPATIAL_DENSITY_FILE location (or vent co-ordinates if fixed vent)
- SPD_GRID_SPACING of spatial density file
- RESIDUAL VALUES - where residual is the simulated lava flow thickness
- VOLUMES:
  - MIN/MAX_TOTAL_VOLUME - ??
  - LOG_MEAN/STD_DEV_TOTAL_VOLUME = ??
- PULSE VOLUME (min and max) - where pulse volume is ??
- FLOWS - number of flows per simulation
- RUNS - number of simulations to run

cp run_laos.pl to your own run file, e.g. rul_gede.pl and edit the name of the config file 
(the plot files should work but you need the right modules, so we have been plotting results in GIS instead)

edit Queuescript.sh to have the correct run file at the end, e.g. perl run_gede.pl

## Running MOLASSES

The model currently doesn't run in parallel, but could be made to.

1. Navigate to the /run_code_here folder and if running in debug mode, i.e. are ssh'd into a node: perl run_xxx.pl, or:
2. qsub Queuescript.sh making sure that the run_xxx.pl bit of the Queuescript.sh file has been edited.

A 30 m DEM takes about 5 hours to run with 100 flows and varying vent location (for the volumes used in the Laos example). 
A 90 m DEM takes about 3 hours, with the same parameters.

## Outputs
- Outputs are produced in the run_code_here folder with generic names, so please tidy them up into run folders once they're run (and ideally change the code to create uniquely named outputs)
- Sometimes it might fail after a few hundred simulations (memory issue?), if so you can run it in batches and cumulate the output files in matlab.
- The conditional probability can be obtained from the gitsxx file, which is the number of times a cell is impacted (divide by the number of simulations to get conditional probability)
