# Add Google Basemaps in QGIS 3

Unlike in QGIS2, the `Open Layers` plugin, which was commonly used to add a variety of basemaps, does not exist in QGIS3. There is a workaround to add Google Maps into QGIS3. This procedure is inspired from [this page](https://geogeek.xyz/how-to-add-google-maps-layers-in-qgis-3.html).

1. Make sure that the `Browser` panel is visible on the main interface. If not, go to `View` > `Panels` > `Browser`
2. Locate the `XYZ Tiles` entry, right-click and select `New connection`
3. There, add one of the following:

| Name | URL |
| ---- | --- |
| Google Maps:             | https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z} |
| Google Satellite:        | http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z} |
| Google Satellite Hybrid: | https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z} |
| Google Terrain:          | https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z} |
| Google Roads:            | https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z} |

You can now drag any entry in the `XYZ Tiles` panel to your map.