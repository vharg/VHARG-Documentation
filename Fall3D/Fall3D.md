# Run Fall3D on the Komodo cluster @ NTU/ASE :volcano: :tiger2:

  - [Intro](#intro)
  - [Download wind data](#download-wind-data)
  - [Run Fall3D](#run-fall3d)

## Intro
FALL3D should be running fine on the cluster at ```/home/volcano/FALL3D/```. All modules should load automatically. List loaded modules with ```module list```. Required modules are:

```
module add netcdf/4.3.1.1/gnu
module add nco/4.6.3-gnu
module add GMT/4.5.8/gnu
```

Required files are stored on Komodo and on the Github repository. For the latter option, the content of the:
- ```Wind/``` folder should be placed in ```/home/volcano/FALL3D/WindDownload/yourWindName/```
- ```Runs/``` folder should be placed in ```/home/volcano/FALL3D/Runs/yourRunName/```

|:warning: Watch out for modules! |
|---|
| Modules loaded to download the wind data are pretty unstable and are likely to cause problems in the next steps. Therefore you should log out and log back in before running Fall3d.| 


|:boom: Example run |
|---|
| ```Makaturing``` is the example run name used in this manual. Adapt accordingly and make sure to be consistent.| 


## Download wind data
1. Make sure you have the ```.ecmwfapirc``` file in your home directory, e.g. ```/home/susanna.jenkins/```
2. Create a wind folder in ```/home/volcano/FALL3D/WindDownload/```
```
cd /home/volcano/FALL3D/WindDownload/
mkdir Makaturing
cd Makaturing
```

1. Copy template files to your folder:

```
cp ../ecmwf_data.py ./
cp ../FALL3D_eraIn_ecmwf.sh ./
cp ../FALL3D_queue_script.sh ./
```

4. Edit lines 16-22 of *your version of* ```FALL3D_eraIn_ecmwf.sh```. 
    - :warning: **NB1**: The domain must be a multiple of the grid resolution, i.e. if you divide the X or Y range of degrees (e.g. 10 to 30 = 20) by grid resolution (e.g. 0.75) it must be an integer. Ditto for the distance from 0, i.e. -2 won't work with a 0.75 degree grid (can't divide 2 by 0.75), but -3 will. Or won't compile for FALL3D. 
    - :warning: **NB2**: If LATMIN has a decimal (or presumably any of the LAT/LON) then the wind file won't compile properly and so Script-SetDbs won't work, must be integer...
    - :warning: **NB3**: The ```scaling``` variable can be used to upsample the resolution of the atmospheric data in order to increase the resolution of Fall3D outputs, which is necessary for tephra accumulation. Note that i) the scaling parameter should be an integer (i.e. a scaling of 2 doubles the number of points in each dimension) and ii)the two previous points apply to the upsampled output.

|:boom: Just so you know |
|---|
| The scripts to download wind profiles also create a file called ```domain.txt``` that contains the values of ```nx``` and ```ny```, which are required by the Fall3D configuration file.| 


5. Edit *your version of* ```FALL3D_queue_script.sh``` to adapt the path, e.g. ```/home/volcano/FALL3D/WindDownload/Makaturing```

6. Run the script with ```qsub FALL3D_queue_script.sh```
7. Check your submission with ```qstat``` (**Q** = queued; **R** = running; **C** = complete)



## Run Fall3D

1. Create symbolic link to the wind data:

```
ln -s /home/volcano/FALL3D/WindDownload/Makaturing/eraIn.nc /home/volcano/FALL3D/Data/eraIn-nc/Makaturing.eraIn.nc
```

2. Create a run folder and copy template file:
```
mkdir Runs/Makaturing 
cd Runs/Makaturing
cp ../../Input_Template.inp Makaturing.inp
```

3. Edit input file for parameters want where says **EDIT** (and in post-process section if want to run GMT post-processing), can use ```../../Input_Example.inp``` for inspiration 

4. Run the pre-processing scripts, which should all return a 0 value. If you get a 1, check the log files in your ```Runs/Makaturing/``` folder.
```
../../fall3d-7.3.1/Scripts/Script-SetDbs Makaturing eraIn
../../fall3d-7.3.1/Scripts/Script-SetTgsd Makaturing
../../fall3d-7.3.1/Scripts/Script-SetSrc Makaturing
```

### Test run
5. Do a test run on one node. See if the job runs using ```qstat```. If it does, then cancel it using ```qdel jobId``` and go to next step
```
qsub -x -I;  ../../fall3d-7.3.1/Scripts/Script-Fall3d_ser Makaturing
```

### Run on a single CPU
6. To use a single CPU, resubmit using the queue. First copy the queue script ```QueueScript_SingleNode.sh```, edit the header and the run name, then submit it: 
```
cp ../../QueueScript_SingleNode.sh . 
qsub QueueScript_SingleNode.sh
```

### Run in parallel
7. To use FALL3D in parallel, copy the queue script ```QueueScript_Par.sh```, edit the header and the run name. The ```ppn``` variable defines the number of processor used per node, which has to be adapted based on the number of granulometry bins defined in the run configuration file. 

```
cp ../../QueueScript_Par.sh
qsub QueueScript_Par.sh
```

###  Post processing & visualisation

8.  Post-process results using GMT (typed from the correct run folder): 
```
../../fall3d-7.3.1/Scripts/Script-Fall3d2GMT Makaturing
```  
This takes a while but provides lots of images that can be viewed in the cluster starting a server...
```
python -m SimpleHTTPServer 8080
```
... which can then be visualised by opening [172.21.46.50:8080](172.21.46.50:8080) in a web browser. Alternatively, you can use [Panoply](https://www.giss.nasa.gov/tools/panoply/download/) to open the file ```Makaturing.res.nc```.

