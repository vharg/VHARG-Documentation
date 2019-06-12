## Visualise Titan Outputs
The following three GMT scripts (adapted from Christina Widiwijayanti) can be used for visualisation of titan output tecplot files once they have been downloaded from the cluster (can be done using cyberduck). Files need executing in a GMT terminal and the tecplot files should be at the same directory level as the script. 

* Visu-titan2d-single-tecplot.bash
* Convert-tecplot-loop.bash
* Visu-titan2d-impacted-area.bash

### Visu-titan2d-single-tecplot.bash
1. The first script is used to visualise a single tecplot file corresponding to an individual timestep. The script comprises a series of commands needed to create a map from your DEM input. This can be any DEM and doesnt have to be the one you used to run titan, a .tif file is fine. 

2. 	Edit lines 2, 7, 9 to point to the directory containing the DEM to be used as input. 
3. Edit line 11 to specify the dimensions of the map you want to create.
4. Open a GMT terminal, navigate to the script, and run: `bash Visu-titan2d-single-tecplot.bash` After hitting enter there will then be a prompt asking which tecplot file you wish to run the script for, type this without the extension.

### Convert-tecplot-loop.bash
1. Needs to be run in a folder containing all of the tecplot files created by titan. This script creates junk.blm, grd, dat files. These are a compilation of the individual tecplot files and contain information on the total impacted area. This script should be run before the next one. 
2. Edit so that the dimensions match those specified previously (there are 5 places to do so). Run in the same way as before. 

### Visu-titan2d-impacted-area.bash
1. Visu-titan2d-impacted-area.bash uses the output of the Convert-tecplot-loop.bash script. 
2. Lines 2, 7, 9 need editing to point to the location of the DEM used as input.
3. Line 12, change this to the dimensions of your map.
4. Execute this script and there are 2 prompts, the first asks for the (impacted area) junk file with no extension, the second asks for a single tecplot file (again no extension). This should be the last one that was created as part of your run. You will then get an output postscript file which shows the total impacted area. 