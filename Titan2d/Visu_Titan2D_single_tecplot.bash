#!/bin/bash

#VISUALIZE TITAN2D OUTPUT FLOW DISTRIBUTION IN A 2D TOPO-MAP
############################################################

# DEM file with directory path
# TOPO MAP : /Users/elly/Documents/HazardModelling/Titan_2D/TestVisualisation/Gede_UTM.tif

#1 This command is needed for the popup asking which file you want to visualise, you dont need to specify the file in the script
echo -n "input single tecplot file (tecpl0000000758):"
read NAME

#2 create DEM gray-shade/gradient file
grdgradient /Users/elly/Documents/HazardModelling/Titan_2D/TestVisualisation/Gede_UTM.tif -GIll.grd -E90/20/40/40 -V



#3 create color shade
makecpt -Cgray -T-5000/15000/100 -Z > topo.cpt


#4 create color shade for characterizing deposit thickness
makecpt -Crainbow -T0/30/3 -V > deposit_thicknes.cpt
makecpt -Crainbow -T10/200/10 -V > lava.cpt


#5 setup text formatting 
gmtset HEADER_FONT_SIZE 15 OBLIQUE_ANOTATION 0 DEGREE_FORMAT 0


#6 call "time-stamp" from selected tecplot output file
head -1 $NAME.tec | awk '{print "730000 9235000 18 0 1 10",$5}' > junk


#7 plot in overlay map: DEM gray-shade image
grdimage /Users/elly/Documents/HazardModelling/Titan_2D/TestVisualisation/Gede_UTM.tif -JX17/17 -Ctopo.cpt -IIll.grd -R700000/740000/9230000/9268000  -Ba10000g10000:"":/a10000g10000:.:SWne -X4 -Y2 -K > $NAME.ps



#8 plot in overlay map: DEM contour line, interval contour 500m. 
#grdcontour /Users/elly/Documents/HazardModelling/Titan_2D/TestVisualisation/Gede_UTM.tif -JX -R -O -C500 -Wfat -Ba5000g1000:"":/a5000g1000:.:SWne -K  >> $NAME.ps


#9 plot in overlay map: DEM contour line, interval contour 100m. 
grdcontour /Users/elly/Documents/HazardModelling/Titan_2D/TestVisualisation/Gede_UTM.tif -JX -R -O -C100 -Ba5000g1000:"":/a5000g1000:.:SWne -K  >> $NAME.ps


#10 plot in overlay map: "time-stamp" of selected tecplot file
pstext junk -G255/255/0 -V -R -W0 -JX -O -K >> $NAME.ps


#11 plot in overlay map: deposit thickness from selected tecplot file, in defined color scale, EDIT THIS to have the boundaries of the grid area.
awk '($1>=710000)&&($1<=740000)&&($2>=9240000)&&($2<=9260000)&&($4>=0.5) {printf ("%11.5f %11.5f %11.5f\n",$1,$2,$4)}' $NAME.tec | psxy -Sc0.03 -Cdeposit_thicknes.cpt -R -V -JX -K -O >> $NAME.ps


#12 Plot initial source ellipsoid. EDIT THIS to have the location of the start point.
psxy -JX -R -Se -W2/255/0/0 -O -V -K <<END>> $NAME.ps
720012.26 9250168.74 120 .09 .045
END


#13 plot color scale as legend
psscale -Clava.cpt -D18/8/16/0.4 -L -B::/:m: -U"$NAME" -O >> $NAME.ps showpage


#14 convert postcript file to .jpg
convert -rotate 90 $NAME.ps $NAME.jpg 



