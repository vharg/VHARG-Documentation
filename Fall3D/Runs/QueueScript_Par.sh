#!/bin/bash

#PBS -N Fall3D
#PBS -j oe
#PBS -V
#PBS -m bea
#PBS -l nodes=9:ppn=24
#PBS -q q24
#PBS 
module load GMT/4.5.8/gnu


NCPUS=216 
NGROUP=9

# Here job name is kelud14_fine, change!
date
/home/volcano/FALL3D/fall3d-7.3.1/Scripts/Script-Fall3d_par kelud14_fine $NCPUS $NGROUP $PBS_NODEFILE
date