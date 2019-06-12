#!/bin/bash

#select Titan2d output data
###########################

#echo -n "output-filename:"
#read NAME

awk '($1>=700000)&&($1<=740000)&&($2>=9230000)&&($2<=9268000)&&($4>=0.1) {printf ("%11.5f %11.5f %11.5f\n",$1,$2,$4)}' tecpl0000000000.tec > junk.dat

for i in tec*.tec
do

awk '($1>=700000)&&($1<=740000)&&($2>=9230000)&&($2<=9268000)&&($4>=0.5) {printf ("%11.5f %11.5f %11.5f\n",$1,$2,$4)}' $i >> junk.dat

#  echo "Looping ... i is set to $i"
done


blockmean junk.dat -R700000/740000/9230000/9268000 -V -I5/5 > junk.blm

xyz2grd junk.blm -R700000/740000/9230000/9268000 -I5/5 -N0 -V -Gjunk.grd

grd2xyz junk.grd -R700000/740000/9230000/9268000 -V > junk.dat


