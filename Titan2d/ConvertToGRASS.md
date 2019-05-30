## Convert DEM into GRASS format 

GRASS is the preferred DEM format for use in Titan2D. GeoTIFF or other format DEM's can be converted to GRASS using a combination of GRASS GIS, GMT, and GDAL commands. 

* Open a terminal and navigate to the DEM you want to convert, in this case the DEM is in GeoTIFF format. 
	
### Convert the DEM to UTM coordinate system:

``` bash
gdalwarp -t_srs EPSG:32748 Gede.tif Gede_UTM.tif
``` 
* EPSG:32748 refers to coordinate reference system WGS 84 / UTM zone 48 S. EPSG codes can be found online if you know the UTM zone.

``` shell
gdalinfo followed by the name of the file can be used to check this has worked. 
eos-ellytennant:GRASS elly$ gdalinfo Gede_UTM.tif 
Driver: GTiff/GeoTIFF
Files: Gede_UTM.tif
Size is 4997, 4640
Coordinate System is:
PROJCS["WGS 84 / UTM zone 48S" 
```
* Also check that the corner coordinates are in UTM format (meters):
	
```	
Corner Coordinates:
Upper Left  (  699408.009, 9268377.222) (106d48'13.21"E,  6d36'56.35"S)
Lower Left  (  699408.009, 9229905.838) (106d48'17.88"E,  6d57'48.58"S)
Upper Right (  740839.369, 9268377.222) (107d10'41.71"E,  6d36'50.95"S)
Lower Right (  740839.369, 9229905.838) (107d10'47.34"E,  6d57'42.89"S)
Center      (  720123.689, 9249141.530) (106d59'30.04"E,  6d47'19.83"S)
```
* Information on any of the GDAL commands can be gained through 'commandname --help' i.e `gdalwarp --help` 
	
### Convert from GeoTIFF to grd DEM format using GMT 

```gdal_translate -of GMT Gede_UTM.tif Gede_UTM.grd``` 
	
### Resample the DEM
Click on the GMT application and a new GMT terminal will open. Resample the DEM so that the corner coordinates are whole numbers and a multiple of the grid resolution (pixel size). We can also change the grid resolution here, at the moment mine is: `Pixel Size = (8.291246648232578,-8.291246648232757)` but I will change it to 10/10 to make it easier to work with.

```grdsample Gede_UTM.grd -GGede_10m -I10/10 -R700000/740000/9230000/9268000 -r -V```
	
* (West/East/South/North)
	
* Use `grdinfo Gede_10m` to check that this has worked correctly, -r converts to pixel node registration, check this along with the grid bounds and the increment. 
	
### Convert NetCDF grid to binary
* Still in the GMT environment, use:

```grdconvert Gede_10m Gede_10m.bin=bf ``` 
	

### Set up the GRASS location
* Now we need to set up the Location in which to store the GRASS DEM. Open GRASS, either by typing into the terminal, or by clicking on the icon in Applications. Then follow through the steps on the GUI  to set up the location.
	* Navigate to the database directory you want to store the data in.
	* Select GRASS location, make a new location
	* Select GRASS Mapset, make a new mapset.  
	
### Convert NetCDF binary to GRASS
* Within the GRASS terminal navigate to the the location of the Gede_10m.bin file. Next change from NetCDF raster binary to GRASS raster binary using:

```r.in.bin -hf input=Gede_10m.bin output=Gede_10m.grass``` 

You should now have a GRASS format DEM!	
		
