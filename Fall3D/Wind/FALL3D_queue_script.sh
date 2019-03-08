#!/bin/sh

#  FALL3D_queue_script.sh
#
#
#  Created by Susanna Jenkins to operate on Komodo @ EOS/ASE on 25/07/2018.
#  Modules updated by Seb Biass on 26/02/2019
#
#!/bin/bash
# request resources:

#PBS -N FALL3D-meteo
#PBS -j oe
#PBS -V
#PBS -m bea
#PBS -l nodes=1:ppn=12
#PBS -q q12
#PBS


module load fall3d/7.3
module load miniconda/4.3.21

# on computer node, change directory to 'submission directory':
# cd /home/volcano/FALL3D/WindDownload/yourName/
cd /home/volcano/FALL3D/WindDownload/kelud14/


sh ./FALL3D_eraIn_ecmwf.sh


