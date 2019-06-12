## Run Titan2d on Komodo


1. Titan2d-v4.0.0 is installed as a module on Komodo, at usr/local/titan2d-v4.0.0. An example run and the MPI script needed to submit the job to the cluster can be found at: `home/volcano/RunTitan2D/titanTEST`

2. If using the GUI to help create the input files, login to the cluster using -X after the ssh. Alternatively the input files can be created manually, by copying and editing pre-existing ones. If you are doing many similar runs for the same volcano this way might be easier.  

	```
ssh -X user@komodo.ase.ntu.edu.sg
```
3. Navigate to `/home/volcano/titan2d-v4.0.0/bin`. Launch the GUI using: `./titan_gui.sh`. In the Load/Save tab choose where to store the run, I am putting mine in `/home/volcano/RunTitan2D` and calling it Gede1. Fill in the run parameters by clicking through each of the tabs, when this has been done once the 'Load/Save' tab is useful.

4. Under the job submission tab enter the number of CPUs. `checkfreenode` can be used to decide which node to run on, choose 12, 16 or 24 CPU's. Clicking 'Run Job' will create the file structure (but does not yet run the job) neccessary to run in the Gede1 directory (as below). The `MPIscript.sh` needs to be copied from `/home/volcano/RunTitan` into the date folder: 


	```
Gede1
├──2019_06_11_14_30_20.276 
│		├── MPIscript.sh  				
│		├── maxHeightforKML.data
│		├── runtitan.sh 
│		├── zone.txt
│		├── simulation.py
│		├── Stdout.txt
│		├── Stderr.txt
│	
├── Gede1.ascpile   
├── Gede1.ascprm
├── Gede1.ascflux            
└── Gede1.ascplane
```
5. In your copied MPI script edit lines 7, 8, 9. In lines 8, 9 specify the number of CPUs as previously chosen in the job submission tab. In this case we have used 24.


	```
PBS -l nodes=1:ppn=24
PBS -q q24
```

6. The file `simulation.py` stores the main information related to the run, this file can be copied and edited as opposed to using the GUI to setup a new run. Be sure to also edit the file giving information about the source you have selected (Gede1.ascpile etc). **Another note on the simulation.py file, (if this has been created by titan), line 10, delete one of the = signs so that region_limits=()**

7. Submit the job to the cluster:  `qsub MPIscript.sh`, and check the job is running `qstat` the outputs you have specified will be generated in the directory `vizout`. Outputs can be downloaded from the server and visualised using GMT or in Panopoly.

	
