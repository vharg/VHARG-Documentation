
# TephraProb on a cluster

There is a relatively easy way to parallelise TephraProb on a computer cluster without having to struggle with Matlab's Parallel Computing Toolbox. Matlab is not even needed on the cluster, and it is just a matter of sending single occurrences of Tephra2 on different nodes. Here is how to do so:

1. Generate your input files and eruption scenarios locally
2. Send the required files on the cluster
3. Run the scenario on the cluster
4. Retrieve the output files from the cluster to the local computer
5. Post-process the output files (e.g. probability calculations) locally


TephraProb is installed on Komodo in `/home/volcano/TephraProb/`.

## Before starting

### :warning: Prerequisite

1. This procedure starts only when scenarios have been generated locally. You should be pretty much ready to hit the `Run Tephra2` in TephraProb;
2. Check that your scenarios was setup with the `write_conf` and `write_gs` variables enabled;
3. This procedure requires all TephraProb files and folder to be organised in their original hierarchy and names;
4. TEPHRA2 should be compiled on the cluster.


### Windows users

If TephraProb was run on Windows, you might have to alter your `T2_stor.txt` file. Each line contains a separate command to Tephra2 with the paths to the configuration, wind, grid, grain-size and output files. :warning: All path in this file must be relative to the root folder of TephraProb, so any line that contains an absolute path must be trimmed. This can easily be done with any *Find & Replace* command of any text editor. For instance:

```sh
C:/Documents/TephraProb/RUNS/...	# Wrong
RUNS/...							# Right
```


## Main procedure


1. Transfer your run, grid and wind files on the cluster according to the hierarchy below. Note that **not** all files of the `RUNS/`, `GRID/` and `WIND/` folders need to be transferred;

```
ROOT
├── MODEL/
├── RUNS/
│   └── runName/
│       └── runNumber/
│           ├── CONF/*.*
│           ├── GS*.*
│           └── OUT/*.*
├── WIND/
│   └── windName/
│           └── pathToAscii/*.*
├── GRID/
│   └── gridName/
│           └── *.utm
├── T2_stor.txt
└── runTephraProb.sh
```

2. Connect to the cluster and navigate at the root of TephraProb, i.e. in the same directory as `T2_stor.txt`;
```sh
ssh userName@komodo.ase.ntu.edu.sg 
```

3. Rename `T2_stor.txt` to a relevant run name, e.g. `MakaturingVEI4.txt`:
```sh
mv T2_stor.txt MakaturingVEI4.txt
```

4. **Duplicate** `runTephraProb.sh` to a file name reflecting your run name, e.g. `runMakaturingVEI4.sh`:
```sh
cp runTephraProb.sh runMakaturingVEI4.sh
```

5. Get the number of lines contained in `MakaturingVEI4.txt`, divide this number by 24 and round that to the upper integer. Let's call this number `nline`;

6. Split `MakaturingVEI4.txt` by `nline` with the following command (replace `nline`), which should create 24 files named `MakaturingVEI4.txt00` to `MakaturingVEI4.txt23`:

```sh
split -l nline -a 2 -d MakaturingVEI4.txt MakaturingVEI4.txt
```

7. Edit `runMakaturingVEI4.sh` (e.g. `vi runMakaturingVEI4.sh`) and replace `T2_stor.txt$chunk` by `MakaturingVEI4.txt$chunk`

8. Submit the job using:
```sh
qsub -t 0-23 runMakaturingVEI4.sh
```

9. Check the job status with `qstat`. Upon completion, transfer the content of `RUNS/runName/runNumber/OUT/` back to your local TephraProb folder and processd with the post-processing steps.

10. Clean your mess! Remove the temporary files and archive your run Files:
```sh
rm *.txt*
```

## Tips

### RSYNC Examples

#### To cluster:
```sh
rsync -arvz --exclude *.mat --exclude FIG --exclude KML --exclude LOG --exclude SUM  RUNS/run_name host@server:~/TephraProb/RUNS/
```

#### From cluster
```sh
rsync -arvz --ignore-existing host@server:~/TephraProb/RUNS/runName/ RUNS/runName/
```

### Compile Tephra2 
Tephra2 should be compiled by default on the cluster. If not, follow this command:
```sh
cd MODEL
make clean
cd forward_src
make
cd ..
chmod 755 tephra2-2012
cd ..
```
