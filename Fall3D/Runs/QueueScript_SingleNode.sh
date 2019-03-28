#!/bin/bash

#PBS -N Fall3D
#PBS -j oe
#PBS -V
#PBS -m bea
#PBS -l nodes=1:ppn=24
#PBS -q q24
#PBS 

# Here job name is kelud14 - change!

/home/volcano/FALL3D/fall3d-7.3.1/Scripts/Script-Fall3d_ser kelud14

