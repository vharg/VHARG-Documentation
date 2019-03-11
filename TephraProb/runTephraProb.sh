#!/bin/bash

#PBS -N TephraProb
#PBS -j oe
#PBS -V
#PBS -l nodes=1:ppn=24
#PBS -q q24

module load openmpi/1.4.5-gnu

cd $PBS_O_WORKDIR

chunk=`printf "%02d" $PBS_ARRAYID`

mpirun -np 24 -machinefile $PBS_NODEFILE parallel -j 24 -a T2_stor.txt$chunk