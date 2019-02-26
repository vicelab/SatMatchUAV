import numpy
import math
import arcpy
from arcpy import env


# Aggregates the pixels in an image such that they match the pixel locations of a reference image.
# The method does this by  aggregating fractional pixels (using MEAN).
# Both the reference and the source image need to be in the same projection
arcpy.AddMessage('hello')
nodatavalue= -10000 # not sure if this is a good one, but I had to pick something

inUAV = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/ndvi/madera_2018-07-05_Fabcd_index_ndvi.tif'
inSAT = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Mike/Satelite Data_Testing/Landsat/LC08_L1TP_042035_20180619_20180703_01_T1_B11.TIF'
outMap = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Testing/nomoire2.tif'
# inIMG = arcpy.GetParameterAsText(0)
# inSAT = arcpy.GetParameterAsText(1)
# outIMG = arcpy.GetParameterAsText(2)



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
lowerLeftSAT = lowerLeft
cellSizeSAT = 2.75
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
for rowNew in range(rowsNew):
    arcpy.AddMessage(rowNew)
    offy = initoff[1] + rowNew * cellfactor
    pixpos[1] = math.trunc(math.floor(offy))
    pixfrac[1] = offy - pixpos[1]
    for colNew in range(colsNew):
        offx = initoff[0] + colNew * cellfactor
        pixpos[0] = math.trunc(math.floor(offx))
        pixfrac[0] = offx - pixpos[0]

        # initialize weights
        weights  = numpy.zeros((samplesize, samplesize))
        weights += 1
        # process the edges of the weight matrix
        for row in range(samplesize):
            weights[row][0] *= 1 - pixfrac[0] # left edge
            weights[row][samplesize-1] *= pixfrac[0] # right edge
        for col in range(samplesize):
            weights[0][col] *= 1 - pixfrac[1] # top edge
            weights[samplesize-1][col] *= pixfrac[1] # bottom edge

        # aggregate the image pixels within the new, larger pixel
        for row in range(samplesize):
            for col in range(samplesize):
                # if the subpixel falls within the image:
                if (0 <= pixpos[0] + col < cols) and (0 <= pixpos[1] + row < rows):
                    pixVal = image[pixpos[1]+row][pixpos[0]+col]
                    pixelNew[row][col] = pixVal
                    if pixVal == nodatavalue:
                        weights[row][col] = 0
                else:
                    weights[row][col] = 0

        # find out if the new pixel has a valid value:
        weightSum = weights.sum()
        if weightSum != 0:
            weighted = weights * pixelNew
            imageNew[rowNew][colNew] = weighted.sum() / weightSum
        else:
            imageNew[rowNew][colNew] = nodatavalue



# Convert Array to raster (keep the origin and cellsize the same as the input)
newRaster = arcpy.NumPyArrayToRaster(imageNew,lowerLeftNew,cellSizeSAT, value_to_nodata=nodatavalue)
arcpy.DefineProjection_management(newRaster, prjSAT)
newRaster.save(outMap)


print 'done'
arcpy.AddMessage('donzo')
