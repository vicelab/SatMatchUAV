import numpy
import math
import arcpy
from arcpy import env


# Aggregates the pixels in an image such that they match the pixel locations of a reference image.
# The method does this by  aggregating fractional pixels (using MEAN).
# Both the reference and the source image need to be in the same projection
arcpy.AddMessage('hello')
nodatavalue= -10000 # not sure if this is a good one, but I had to pick something

inUAV = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Testing/reprojected.tif'
inSAT = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Mike/Satelite Data_Testing/Landsat/LC08_L1TP_042035_20180619_20180703_01_T1_B11.TIF'
outMap = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Testing/stencil.tif'
# inUAV = arcpy.GetParameterAsText(0)
# inSAT = arcpy.GetParameterAsText(1)
# outImg = arcpy.GetParameterAsText(2)



# Get input Raster properties
rasUAV = arcpy.Raster(inUAV)
#rasUAV = arcpy.Raster('C:/Users/aanderson29/Desktop/TEMP/ndvi_test/madera_2018-07-05_Fabcd_index_ndvi.tif')
#rasUAV = arcpy.Raster('D:/Shared/VL_METRIC-GALLO/Andy/Testing/reduced_again.tif')
lowerLeft = arcpy.Point(rasUAV.extent.XMin, rasUAV.extent.YMin)
cellSize = rasUAV.meanCellWidth
metaUAV = arcpy.Describe(rasUAV)
prjUAV = metaUAV.SpatialReference


image = arcpy.RasterToNumPyArray(rasUAV, nodata_to_value=nodatavalue)
rows = image.shape[0]
cols = image.shape[1]
height = cellSize *rows
width  = cellSize *cols


# Get the metadata from the Satellite file
rasSAT = arcpy.Raster(inSAT)
metaSAT = arcpy.Describe(rasSAT)
prjSAT = metaSAT.SpatialReference

# if prjUAV != prjSAT:
#     print 'Warning, the projections don\'t match!'
#     exit(3)


# Figure out the size and placement of the new bitmap
lowerLeftSAT = arcpy.Point(rasSAT.extent.XMin, rasSAT.extent.YMin)
cellSizeSAT = rasSAT.meanCellWidth
# lowerLeftSAT = arcpy.Point(rasUAV.extent.XMin, rasUAV.extent.YMin)
# cellSizeSAT =  cellSize * 2
cellfactor = cellSizeSAT /cellSize
samplesize = math.trunc(math.ceil(cellfactor)) + 1 # size of the pixel matrix to be aggregated into one resulting pixel
pixelNew = numpy.zeros((samplesize, samplesize))

lowerLeftNew = arcpy.Point(math.floor( (lowerLeft.X -lowerLeftSAT.X) /cellSizeSAT ) *cellSizeSAT +lowerLeftSAT.X,
                           math.floor( (lowerLeft.Y -lowerLeftSAT.Y) /cellSizeSAT ) *cellSizeSAT +lowerLeftSAT.Y)


# find the size of bitmap needed to cover the original one
rowsNew = math.trunc(math.ceil(height /cellSizeSAT))
if lowerLeftNew.Y - lowerLeft.Y  + rowsNew * cellSizeSAT < height:
    rowsNew +=1
colsNew = math.trunc(math.ceil(width  /cellSizeSAT))
if lowerLeftNew.X - lowerLeft.X  + colsNew * cellSizeSAT < width:
    colsNew +=1

heightNew = rowsNew*cellSizeSAT
widthNew  = colsNew*cellSizeSAT
imageNew = numpy.zeros((math.trunc(rowsNew), math.trunc(colsNew)))

# find first pixel location within the bitmap coordinate system (starting top-left, and rows, columns)
offx = (lowerLeftNew.X -lowerLeft.X) /cellSize
offy = rows +( lowerLeft.Y  -lowerLeftNew.Y - heightNew ) /cellSize
initoff = [offx,offy]


pixpos = [0,0]
pixfrac=[.0,.0]
# iterate through the output bitmap and aggregate pixels
counter = 0
for rowNew in range(rowsNew):
    for colNew in range(colsNew):
        imageNew[rowNew][colNew] = counter
        counter += 1

# Convert Array to raster (keep the origin and cellsize the same as the input)
newRaster = arcpy.NumPyArrayToRaster(imageNew,lowerLeftNew,cellSizeSAT, value_to_nodata=nodatavalue)
arcpy.DefineProjection_management(newRaster, prjSAT)
newRaster.save(outMap)


arcpy.AddMessage('donzo')
