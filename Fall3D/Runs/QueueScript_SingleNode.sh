#!/bin/bash

#PBS -N kelud14_fine
#PBS -j oe
#PBS -V
#PBS -m bea
#PBS -l nodes=1:ppn=24
#PBS -q q24
#PBS 
	
/home/volcano/FALL3D/fall3d-7.3.1/Scripts/Script-Fall3d_ser kelud14_fine

