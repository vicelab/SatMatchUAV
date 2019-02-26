import numpy
import math
import arcpy
import sys
from arcpy import env


# turns a georeferenced image into a stencil image with unique values
# by using a smaller (high-res) image as a guide
nodatavalue = -1000

def makeStencil(inIMG, inSAT, outIMG):
    # Get input Raster properties
    rasUAV = arcpy.Raster(inIMG)
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


    if prjUAV.exportToString() != prjSAT.exportToString():
        print 'Warning, the projections don\'t match!'
        exit(3)


    # Figure out the size and placement of the new bitmap
    lowerLeftSAT = arcpy.Point(rasSAT.extent.XMin, rasSAT.extent.YMin)
    cellSizeSAT = rasSAT.meanCellWidth
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
    imageNew = numpy.zeros((math.trunc(rowsNew), math.trunc(colsNew)), dtype = int)

    # find first pixel location within the bitmap coordinate system (starting top-left, and rows, columns)
    offx = (lowerLeftNew.X -lowerLeft.X) /cellSize
    offy = rows +( lowerLeft.Y  -lowerLeftNew.Y - heightNew ) /cellSize
    initoff = [offx,offy]


    pixpos = [0,0]
    pixfrac=[.0,.0]
    # iterate through the bitmap and put unique values
    counter = 0
    for rowNew in range(rowsNew):
        for colNew in range(colsNew):
            imageNew[rowNew][colNew] = counter
            counter += 1

    # Convert Array to raster (keep the origin and cellsize the same as the input)
    newRaster = arcpy.NumPyArrayToRaster(imageNew,lowerLeftNew,cellSizeSAT, value_to_nodata=nodatavalue)
    arcpy.DefineProjection_management(newRaster, prjSAT)
    newRaster.save(outIMG)


    arcpy.AddMessage('donzo')



if __name__ == '__main__':
    param = sys.argv
    if len(param) == 4:
        inIMG = param[1]
        inSAT = param[2]
        outIMG = param[3]
    else:
        inIMG = arcpy.GetParameterAsText(0)
        inSAT = arcpy.GetParameterAsText(1)
        outIMG = arcpy.GetParameterAsText(2)
        # inIMG = 'C:\\Users\\aanderson29\\Box Sync\\[VICE Lab]\\RESEARCH\\PROJECTS\\Gallo\\Madera Block 760\\METRIC\\WIP\\Andy\\Reprojected\\Madera_2018-06-06_UAV_BLU_Sat-Repj_v01.TIF'
        # inSAT = 'C:\\Users\\aanderson29\\Box\\[VICE Lab]\\RESEARCH\\DATA\\Madera\\Sentinel\\2018-06-06_L2\\S2B_MSIL2A_20180606T183929_N0206_R070_T11SKA_20180606T221737.SAFE\\GRANULE\\L2A_T11SKA_A006531_20180606T185001\\IMG_DATA\\R10m\\T11SKA_20180606T183929_B02_10m.jp2'
        # outIMG ='C:\\Users\\aanderson29\\Box\\[VICE Lab]\\RESEARCH\\PROJECTS\\Gallo\\Madera Block 760\\METRIC\\WIP\\Andy\\Stencils\\Madera_6-06-2018_SAT_BLU_stencild_v01.TIF'
    print 'hi'

    makeStencil(inIMG, inSAT, outIMG)
    print 'bye'
