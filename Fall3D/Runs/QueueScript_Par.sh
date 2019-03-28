#!/bin/bash

#PBS -N Fall3D
#PBS -j oe
#PBS -V
#PBS -m bea
#PBS -l nodes=1:ppn=10
#PBS -q q12
#PBS 

module load GMT/4.5.8/gnu	

# Here job name is kelud14 - change!
# Specify the number of CPUs to use with ppn in the header

if [ "$PBS_O_WORKDIR" != "" ]; then
        cd $PBS_O_WORKDIR
        NCPUS=`cat $PBS_NODEFILE | wc -l`
        
        /home/volcano/FALL3D/fall3d-7.3.1/Scripts/Script-Fall3d_par kelud14_fine $NCPUS $NCPUS $PBS_NODEFILE
fi


