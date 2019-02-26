import numpy
import math
import arcpy
import sys


# Aggregates the pixels in an image to correspond with the pixel locations of a reference image (using MEAN).
# Since the method aggregates fractional pixels, there is no need for the size of the reference pixels to be integer multiples of the source pixels.
# Both the reference and the source image need to be in the same projection!


def SatMatchScatter(inUAV,inSAT,outcsv):
    nodatavalue= -10000 # not sure if this is a good one, but I had to pick something

    arcpy.AddMessage('loading data')

    # Get input Raster properties
    rasUAV = arcpy.Raster(inUAV)
    lowerLeft = arcpy.Point(rasUAV.extent.XMin, rasUAV.extent.YMin)
    cellSize = rasUAV.meanCellWidth
    rows = rasUAV.height
    cols = rasUAV.width
    height = cellSize *rows
    width  = cellSize *cols
    metaUAV = arcpy.Describe(rasUAV)
    prjUAV = metaUAV.SpatialReference.name
    prjUAVdesc = metaUAV.SpatialReference.exportToString()
    imgUAV = arcpy.RasterToNumPyArray(rasUAV, nodata_to_value=nodatavalue)

    # Get the metadata from the Satellite file
    rasSAT = arcpy.Raster(inSAT)
    lowerLeftSAT = arcpy.Point(rasSAT.extent.XMin, rasSAT.extent.YMin)
    rowsSAT = rasSAT.height
    colsSAT = rasSAT.width
    heightSAT = cellSize *rowsSAT
    widthSAT  = cellSize *colsSAT
    metaSAT = arcpy.Describe(rasSAT)
    prjSAT = metaSAT.SpatialReference.name
    prjSATdesc = metaSAT.SpatialReference.exportToString()
    imgSAT = arcpy.RasterToNumPyArray(rasSAT, nodata_to_value=nodatavalue)


    if prjUAVdesc != prjSATdesc or rasSAT.meanCellWidth != cellSize:
         print 'Error, the projections don\'t match!'
         exit(3)


    # Figure out the size and placement of the new bitmap
    sample = numpy.zeros((rows, cols))

    lowerLeftNew = arcpy.Point(int((lowerLeft.X -lowerLeftSAT.X) /cellSize ) *cellSize +lowerLeftSAT.X,
                               int((lowerLeft.Y -lowerLeftSAT.Y) /cellSize ) *cellSize +lowerLeftSAT.Y)


    # create an array to house the output image
    imgNew = numpy.zeros((math.trunc(rows), math.trunc(cols)))

    # find first pixel location within the source bitmap coordinate system (starting top-left, and rows, columns)
    offx = int((lowerLeftNew.X -lowerLeftSAT.X) /cellSize)
    offy = int((lowerLeftSAT.Y -lowerLeftNew.Y) /cellSize)  + rowsSAT - rows


    # iterate through the output bitmap and aggregate pixels
    arcpy.AddMessage('processing')
    imgNew = imgSAT[offy:offy+rows,offx:offx+cols]


    arcpy.AddMessage('saving result')


    # convert images into vectors of strings, leaving out any pixel with no data

    # reshape the image data into vectors
    imgUAV = numpy.reshape(imgUAV,(imgUAV.size))
    imgNew = numpy.reshape(imgNew,(imgUAV.size))

    # turn the image data into text, using the file names as headers
    csvUAV = inUAV.split('\\')[-1].split('\n')[0]
    csvNew = inSAT.split('\\')[-1].split('\n')[0]
    for i in range(imgUAV.size):
        if imgUAV[i] != nodatavalue and imgNew[i] != nodatavalue:
            csvUAV += ',%f' %imgUAV[i]
            csvNew += ',' + (str(imgNew[i]))
    csvUAV += '\n'
    csvNew += '\n'

    f = open(outcsv,'a')
    f.writelines(csvUAV)
    f.writelines(csvNew)
    f.close()

     # arcpy.AddMessage('done')


if __name__ == '__main__':
    param = sys.argv
    if len(param) == 4:
        inUAV = param[1]
        inSAT = param[2]
        outcsv = param[3]
    else:
        inUAV = arcpy.GetParameterAsText(0)
        inSAT = arcpy.GetParameterAsText(1)
        outcsv = arcpy.GetParameterAsText(2)
        # inIMG = 'C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/uav2sat-resample\\Madera_2018-07-05_UAV_GRN_Sat-Rsmp_v01.tif'
        # inSAT = 'C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Sat_files\\LC08_L1TP_042035_20180705_20180717_01_T1_sr_band3.tif'
        # outIMG ='C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Testing\\testingscat.csv'
    SatMatchScatter(inUAV,inSAT,outcsv)
