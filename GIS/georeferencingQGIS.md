# Georeference a raster in QGIS

This procedure illustrates how to georeference a raster in QGIS.

## Required software
The required software are:
- [QGIS](https://www.qgis.org/fr/site/forusers/download.html)
- [Georeferencer plugin](https://docs.qgis.org/3.4/en/docs/user_manual/plugins/plugins_georeferencer.html)

The **Georeferencer plugin** can be installed directly within QGIS from the `Plugins > Manage and Install Plugins` menu on the top bar of QGIS. There, search for `Georeferencer GDAL`. The user manual, including a detailed procedure, can be found [here](https://docs.qgis.org/3.4/en/docs/user_manual/plugins/plugins_georeferencer.html).

## Imporant concepts
A critical aspect of georeferencing is understanding the **relationship between the coordinate system of the source dataset and the target project**. Here, all coordinate systems use the [ESPG reference system](https://epsg.io/). The idea behind georeferencing is to identify **Ground Control Points** (GCP) on the raster to be georeferenced and tie them to a known coordinate. There are usually two cases when georeferencing a dataset.

### Case 1: The raster contains coordinates
If the raster to be georeferenced contains coordinates **and the source coordinate system is known**, we can simply enter these. This is often the case when digitizing paper topographic maps.

### Case 2: The raster does not contain coordinates
Alternatively, if the raster does not contain coordinates or the coordinate system is not specified, then it is necessary to find features that are identifiable on both the raster and the basemap against which the georeferencing will be performed. The coordinates of the feature on the basemap will then be used as the coordinates of the GCP on the raster. Fortunately, the Georeferencer plugin in QGIS makes that easy, and it is simply a matter of clicking on the feature on the raster and then clicking on the equivalent point on the basemap. 

## Obtaining a basemap
A basemap is necessary to extract the coordinates of a GCP. Several options are possible, but check [this page](https://github.com/vharg/VHARG-Documentation/blob/master/GIS/googleMap_QGIS.md) to use a Google basemap.

