#!/bin/sh

#  FALL3D_interim.sh
#
#  Downloads ECMWF interim data for FAll 3D and reformats it into a correct format
#
#  Created by Tom Sheldrake on 16/06/2015.
#  Parameters extracted out of the bash file by Seb Biass 26/02/2019

#   Requirements:
#   1.  See https://software.ecmwf.int/wiki/display/WEBAPI/Access+ECMWF+Public+Datasets for detail on python database installation required for ecmwf batch download
#   2.  Make sure 'ecmwf_data.py' is in your working directory
#   2.  Download NetCDF operators (NCO's) for netcdf file manipulation - http://nco.sourceforge.net/

# 	Edit this block of code
north=-7			# Maximum latitude
south=-9			# Minimum latitude
east=113			# Maximum longitude
west=110			# Minimum longitude
resolution=0.25		# Grid resolution (0.25, 0.5, 0.75)
scaling=4 			# Scaling of the grid size for Fall3D output (i.e. scaling=4 means each dimension is upsampled with 4 times more points)
sDate='2014-02-01'	# Start date
eDate='2014-02-28'	# End date
# 	End edit block


python ecmwf_data.py $west $east $south $north $resolution $sDate $eDate $scaling

#*****Load nco module****

# module load libraries/gnu_builds/nco-4.5.1

#*****concatenate boundary layer ****

ncrcat -h bl1.nc bl2.nc bl3.nc bl4.nc bl_complete.nc

#*****Remove offset and scale by changing to 'double' variable ****

ncap2 -O -s 'blh=float(blh)' bl_complete.nc bl_complete.nc

ncap2 -O -s 'z=float(z)' invariant.nc invariant.nc
ncap2 -O -s 'lsm=float(lsm)' invariant.nc invariant.nc

ncap2 -O -s 'u10=float(u10)' sfc.nc sfc.nc
ncap2 -O -s 'v10=float(v10)' sfc.nc sfc.nc
ncap2 -O -s 't2m=float(t2m)' sfc.nc sfc.nc

ncap2 -O -s 'z=float(z)' prs.nc prs.nc
ncap2 -O -s 't=float(t)' prs.nc prs.nc
ncap2 -O -s 'w=float(w)' prs.nc prs.nc
ncap2 -O -s 'r=float(r)' prs.nc prs.nc
ncap2 -O -s 'u=float(u)' prs.nc prs.nc
ncap2 -O -s 'v=float(v)' prs.nc prs.nc

#*****rename surface geopotential****

ncrename -v z,Z:sfc invariant.nc

#*****Make temporary copies of original files****

cp -r sfc.nc sfc2.nc
cp -r invariant.nc invariant2.nc
cp -r bl_complete.nc bl.nc

#*****append files together & remove temporary files****

ncks -A prs.nc sfc2.nc
ncks -A sfc2.nc invariant2.nc

rm -r sfc2.nc

ncks -A invariant2.nc bl.nc

rm -r invariant2.nc

#*****rename****

mv bl.nc eraIn.nc


#*****rename variables & dimensions****

ncrename -v t,T eraIn.nc
ncrename -v r,R eraIn.nc
ncrename -v u,U eraIn.nc
ncrename -v v,V eraIn.nc
ncrename -v w,W eraIn.nc
ncrename -v level,pres eraIn.nc
ncrename -v u10,U10:sfc eraIn.nc
ncrename -v v10,V10:sfc eraIn.nc
ncrename -v t2m,T2:sfc eraIn.nc
ncrename -v lsm,LSM:sfc eraIn.nc
ncrename -v blh,BLH:sfc eraIn.nc
ncrename -v latitude,lat eraIn.nc
ncrename -v longitude,lon eraIn.nc
ncrename -v z,Z eraIn.nc


ncrename -d latitude,lat eraIn.nc
ncrename -d level,pres  eraIn.nc
ncrename -d longitude,lon eraIn.nc


ncap2 -O -s 'pres=float(pres)' eraIn.nc eraIn.nc


#*****add global attributes****

ncatted -O -h -a YEAR,global,o,l,1900 eraIn.nc
ncatted -O -h -a MONTH,global,o,l,1 eraIn.nc
ncatted -O -h -a DAY,global,o,l,1 eraIn.nc
ncatted -O -h -a HOUR,global,o,l,0 eraIn.nc
ncatted -O -h -a TIME_INCR,global,o,l,21600 eraIn.nc

# Calculate grid intervals
#nx=$(echo "($east - $west) / $resolution + 1" | bc)
#ny=$(echo "($north - $south) / $resolution + 1" | bc)
nx=$(echo "(($east - $west) / $resolution) * $scaling + 1" | bc)
ny=$(echo "(($north - $south) / $resolution) * $scaling + 1" | bc)

ncatted -O -h -a LONMIN,global,o,l,$west eraIn.nc
ncatted -O -h -a LONMAX,global,o,l,$east eraIn.nc
ncatted -O -h -a LATMIN,global,o,l,$south eraIn.nc
ncatted -O -h -a LATMAX,global,o,l,$north eraIn.nc
ncatted -O -h -a NX,global,o,l,$nx eraIn.nc
ncatted -O -h -a NY,global,o,l,$ny eraIn.nc
ncatted -O -h -a NP,global,o,l,37 eraIn.nc
#ncatted -O -h -a NT,global,o,l,40 eraIn.nc

#*****Time overwrite****

ncks -O --mk_rec_dmn time eraIn.nc eraIn.nc

#*****Time overwrite2****

ncap2 -O  -s "time=time*1000" eraIn.nc eraIn.nc
ncap2 -O  -s "time=time*3.6" eraIn.nc eraIn.nc


#*****Change time dimension****

ncatted -O -a units,time,o,c,"seconds since 1900-01-01 00:00:0.0" eraIn.nc eraIn.nc

#*****flip latitude dimension****

ncpdq -O -h -a -lat eraIn.nc eraIn.nc

#*****Reorder dimensions****

ncpdq -O -a time,pres,lat,lon eraIn.nc eraIn.nc

#*****Reverse pressure levels

ncpdq -O -h -a -pres eraIn.nc eraIn.nc

#*****Delete all non-necessary files

rm -rf bl*
rm -rf invariant.nc
rm -rf sfc.nc
rm -rf prs.nc

echo Finished!
















