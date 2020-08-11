# Kernel Density Estimation

## General description
With a Kernel Density Estimation (KDE) it is possible to calculate the density (e.g. number of events/km2) of features (points or lines) within a given area. A KDE is strongly dependant on the choice of the search radius (or bandwidth), which is the search extent around the mean centre of the dataset within the area in exam. If the search radius is too small we may have an overestimation of density near the mean centre, on the contrary, if the search radius is too large we may have an overestimation of density away from the mean centre, resulting in a more smoothed Kernel map. However, the default search radius available in ArcMap (calculated from a variant of Silverman’s rule of thumb) provides rather robust results, particularly for spatial outliers. A practical example of this method is the creation of a spatial density distribution of vents within a volcanic field (e.g. Connor et al., 2012), however, it can be applied to a large number of subjects.

## Procedure
-	In ArcMap, open the ArcToolbox > Spatial Analyst Tools > Density > Kernel Density
-	Select the Input of interest (layer with point or polyline features) 
-	Select the Population field, if any (this should be selected if we want to assign different weights to points/lines within the input layer)
-	Define the Output raster (name of the Kernel Density raster and where it should be saved)
-	Define the Output cell size (if not specified, a default minimum cell size will be assigned)
-	Define a Search radius (if not specified, a default search radius will be assigned)
-	Define the Area units (e.g. km2, m2 etc.)
-	Define the Output values (either “densities”, which is the number of events per distance unit, or “expected counts” which is the number of events for each cell)
-	Define the Method (either “planar”, for planar distances, or “geodesic” if you want to consider the curvature of the earth, so basically the choice of the method depends on the coordinate system used and the extent of the area in exam)


For more details on how the Kernel Density works and about the individual fields of selection mentioned above, refer to these links: 
-	https://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/kernel-density.htm
-	https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/how-kernel-density-works.htm

## Outcome
The outcome of a KDE is a density map that can be visualized in different ways, a common way is through a classified coloured ramp where different density classes can be assigned and each colour represents a density class. The number and the type of classes can be decided (right click on the Kernel raster > properties > symbology > classified). 

click on this link for more information about the class types:
- https://pro.arcgis.com/en/pro-app/help/mapping/layer-properties/data-classification-methods.htm).
