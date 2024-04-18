# FlowDIR 2023
*Eleanor Tennant, Susanna Jenkins, Sébastien Biass*

FlowDIR is a MATLAB tool designed to forecast the travel directions of topographically controlled hazardous flows. The tool consists of two complimentary methods that can be used to estimate flow directionality: 
<ol> 

- The azimuthal elevation difference (AED): this method analyses the topography in a straight line from the starting coordinate. 

- The least cost path (LCP): this method calculates an optimal path through a grid of elevation values. 


This page serves as a succinct introduction to FlowDIR. For a more comprehensive understanding of how FlowDIR works please refer to:

*Tennant, E., Jenkins, S.F., Biass, S., (2023). FlowDIR: a MATLAB tool for rapidly and probabilistically forecasting the travel directions of volcanic flows. Journal of Applied Volcanology* 

## Getting started


FlowDIR was written using MATLAB v9.12. Before starting ensure that you have the following MATLAB toolboxes installed: mapping; image processing, parallel computing.

<ol> 

<li> Download and unpack the zipfile into your MATLAB folder ensuring that the paths are set correctly. The folder contains all of the files needed to run FlowDIR along with several case studies. The content of the folder is as follows: 

```
FlowDIR
   ├── Code
   |	 └── FlowDIR.m
   ├── DEMs
   |	 └── Shinmoedake_2016_5m_clip.tif
   ├── Dependancies
   |	 ├── topotoolbox-master
   |	 ├── polarwitherrorbar.m
   |	 └── polarPcolor.m
   └── Out
         └── Shinmoedake
         		├── 0
         		└── 1
```


<li> FlowDIR can be run from the command line :

`FlowDIR('Shinmoedake', 'Shinmoedake_2016_5m_clip.tif',800, 678187, 3532034, 50, 30, 1, 50, 30000)`

Where the inputs are as follows:

FlowDIR(volcano name, DEM filename, swath length (m), starting coordinate X, starting coordinate Y, buffer (m), elevation threshold (m), uncertainty in start (0/1), start uncertainty (m), least cost path timestep for save), 

Type <code>help FlowDIR</code> into the MATLAB command window to learn more about the inputs required for command line executable mode. 

Alternatively, to run with the dedicated graphical user interface (GUI) simply type  <code>FlowDIR</code> into the command window and the following will pop up:
<br/>


<center><img src="https://github.com/EllyTennant/FlowDir/blob/main/images/GUI.png" width="250"></center>

<li> The input parameters are defined as:

|  FlowDIR input    | Description | Suggested range|
| ----------- | ----------- | ----------- |
| DEM file      | Path to a .tif file projected to UTM coordinates.       |-|
| Starting coordinate	| A single point in UTM coordinates (X,Y).|-|
| Swath length  (m) | The initial swath length prior to clipping. This needs to be long enough to extend from the starting coordinate to outside of the summit region in all directions.  | 500 – 1000 m (default 800 m)|
| Buffer (m)     | Swaths are clipped to the maximum elevation plus the buffer. This is used to extract the summit region.      | 50 – 150 m. Depends on the topography |
|   Elevation threshold (m)  | The elevation change values calculated as part of the AED procedure for each azimuth bin are compared to this value.  If the value is below this threshold the crater wall section is likely to be overtopped and if the value is above this threshold the crater wall section is unlikely to be overtopped. | 20 – 50 m (no default)|
|  Capture uncertainty in start? (0/1)   | Input 1 to run FlowDIR with uncertainty in the starting coordinate. When uncertainty = 0, the initialisation polygon edges are 1 DEM cell width from the starting coordinate, resulting in nine initialisation points. | Default 0|
|  Start uncertainty (m)  | When uncertainty = 1, the user can set the size of the polygon width in meters to increase the number of initialisation points. | No default|



<li>FlowDIR will plot the DEM, and ask you to clip it to an area of interest by drawing a polygon. +/- at the top right hand side of the plot can be used to zoom in or out.
<br/>


<center><img src="https://github.com/EllyTennant/FlowDir/blob/main/images/clip_dem.png" width="400"></center>

The new zoomed in DEM is then plotted and you can click to define the start point.

<li> FlowDIR will now begin, its progress is stated as below:

```Running FlowDir, please wait...
Start point # [1/25] ...
Start point # [2/25] ...
Start point # [3/25] ...
Start point # [4/25] ...
...
Finished
```

<li> When FlowDIR is finished, the AED probabilities and the coordinates of the bin centre points at the buffer limit will be printed to the command window. 

```
    Direction        X             Y         AED Probability
    _________    __________    __________    _______________

     {'NNE'}     7.1219e+05     9.103e+06        0.38045    
     {'NE' }     7.1227e+05    9.1029e+06         2.5246    
     {'ENE'}     7.1231e+05    9.1028e+06          5.498    
     {'E'  }     7.1236e+05    9.1028e+06         9.4317
```
The output figure and the workspace containing all variables will be saved into the <code>out/VolcanoName/X</code> folder.

<br/>
<img src="https://github.com/EllyTennant/FlowDIR/blob/main/images/Shinmoedake.png" width="800"></center>

## Citation
Please cite FlowDIR as:

*Tennant, E., Jenkins, S.F., Biass, S., (2023). FlowDIR: a MATLAB tool for rapidly and probabilistically forecasting the travel directions of volcanic flows. Journal of Applied Volcanology* 
