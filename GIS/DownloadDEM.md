##Download DEM

1. SRTM digital elevation models can be downloaded from the [USGS earth explorer site][link1] (for this you need to register and make an account). 

[link1]: https://earthexplorer.usgs.gov/

2. Using the map zoom to your area of interest, under the search criteria tab you can choose the map extent. 

3. Navigate to `Data Sets -> Digital elevation -> SRTM` and choose a dataset. SRTM 1 Arc-Second global provides void-filled worldwide coverage at a resolution of 30 metres. The data acquisition date is February 2000. More information on acquisition and processing can be found [here.][link2]

[link2]: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1-arc?qt-science_center_objects=0#qt-science_center_objects "Title"

4. Download all of the files that cover your region of interest in GeoTIFF format. If your region spans multiple tiles these can be mosaicked in QGIS using: `Raster > Miscellaneous > Merge`

5. Clipping the DEM to a manageable size can also be done in QGIS, choose: `Layer > Create Layer > New Shapefile Layer`. Create a polygon layer. Right click the new layer, toggle editting on, and draw a box around the region you want to clip to. Choose: `Raster > Extraction > Clip Layer by Extent`. Use your merged DEM as the input layer and your new shapefile as the clipping extent. 
