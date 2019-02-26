import numpy
import math
import arcpy

# import time
# import sys
# import string

# arcpy.AddMessage (sys.version)

# time.sleep(30)
# arcpy.env.workspace = 'in_memory'
# arcpy.env.overwriteOutput = True


# Aggregates the pixels in an image to correspond with the pixel locations of a reference image (using MEAN).
# Since the method aggregates fractional pixels, there is no need for the size of the reference pixels to be integer multiples of the source pixels.
# Both the reference and the source image need to be in the same projection!


# inIMG =  'C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Reflectance_Files/RED/madera_2018-07-05_Fabcd_transparent_reflectance_red.tif'
# inSAT =  'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Mike/Satelite Data_Testing/Landsat/LC08_L1TP_042035_20180619_20180703_01_T1_B11.TIF'
# outIMG = 'C:/Users/aanderson29/Box/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Testing/testingfast4.tif'
# noDataThreshold = 0.1

inUAV = arcpy.GetParameterAsText(0)
inSAT = arcpy.GetParameterAsText(1)
outImg = arcpy.GetParameterAsText(2)
noDataThreshold = float(arcpy.GetParameterAsText(3))

nodatavalue= -10000 # not sure if this is a good one, but I had to pick something (don't use Zero, it'll confuse the code!)


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
prjUAV = metaUAV.SpatialReference
prjUAVname = metaUAV.SpatialReference.name
prjUAVdesc = metaUAV.SpatialReference.exportToString()


# Get the metadata from the Satellite file
rasSAT = arcpy.Raster(inSAT)
metaSAT = arcpy.Describe(rasSAT)
prjSAT = metaSAT.SpatialReference
prjSATname = metaSAT.SpatialReference.name
prjSATdesc = metaSAT.SpatialReference.exportToString()



if prjUAVdesc != prjSATdesc:
     arcpy.AddMessage('ERROR, the projections don\'t match!')
     arcpy.AddMessage('Terminating script...')
     exit(3)


# Figure out the size and placement of the new bitmap
lowerLeftSAT = arcpy.Point(rasSAT.extent.XMin, rasSAT.extent.YMin)
cellSizeSAT = rasSAT.meanCellWidth
cellfactor = cellSizeSAT /cellSize
samplesize = math.trunc(math.ceil(cellfactor)) + 1 # size of the pixel matrix to be aggregated into one resulting pixel
pixelNew = numpy.zeros((samplesize, samplesize))
weights  = numpy.zeros((samplesize, samplesize))

lowerLeftNew = arcpy.Point(math.floor( (lowerLeft.X -lowerLeftSAT.X) /cellSizeSAT ) *cellSizeSAT +lowerLeftSAT.X,
                           math.floor( (lowerLeft.Y -lowerLeftSAT.Y) /cellSizeSAT ) *cellSizeSAT +lowerLeftSAT.Y)


# find the size of bitmap needed to cover the original one
rowsNew = math.trunc(math.ceil(height /cellSizeSAT))
if lowerLeftNew.Y - lowerLeft.Y  + rowsNew * cellSizeSAT < height:
    rowsNew +=1
colsNew = math.trunc(math.ceil(width  /cellSizeSAT))
if lowerLeftNew.X - lowerLeft.X  + colsNew * cellSizeSAT < width:
    colsNew +=1

# Load the source image into a raster with a buffer around it
buffersize = int(math.ceil(cellfactor))
imageBuf = numpy.zeros((rows + 2*buffersize, cols + 2*buffersize)) + nodatavalue
imageBuf[buffersize: rows + buffersize, buffersize: cols + buffersize] = arcpy.RasterToNumPyArray(rasUAV, nodata_to_value=nodatavalue)

# create an array to house the output image
heightNew = rowsNew*cellSizeSAT
widthNew  = colsNew*cellSizeSAT
imageNew = numpy.zeros((math.trunc(rowsNew), math.trunc(colsNew))) + nodatavalue

# find first pixel location within the source bitmap coordinate system (starting top-left, and rows, columns)
offx = (lowerLeftNew.X -lowerLeft.X) /cellSize + buffersize
offy = rows +( lowerLeft.Y  -lowerLeftNew.Y - heightNew ) /cellSize + buffersize
initoff = [offx,offy]


pixpos = [0,0]
pixfrac=[.0,.0]
# iterate through the output bitmap and aggregate pixels
arcpy.AddMessage('processing')
for rowNew in range(rowsNew):
    # arcpy.AddMessage(rowNew)
    offy = initoff[1] + rowNew * cellfactor
    pixpos[1] = int(math.floor(offy))
    pixfrac[1] = offy - pixpos[1]
    for colNew in range(colsNew):
        offx = initoff[0] + colNew * cellfactor
        pixpos[0] = int(math.floor(offx))
        pixfrac[0] = offx - pixpos[0]

        # aggregate the image pixels within the new, larger pixel
        pixelNew = imageBuf[ pixpos[1] : pixpos[1]+samplesize,
                             pixpos[0] : pixpos[0]+samplesize ]

        # initialize weights
        weights *= 0
        # only calculate a value if there are enough valid pixels
        badpixels = 100.0 * (pixelNew == nodatavalue).sum() /samplesize /samplesize
        if badpixels <= noDataThreshold:
            weights += 1
            # process the edges of the weight matrix
            weights[:,0] *= 1 - pixfrac[0] # left edge
            weights[0,:] *= 1 - pixfrac[1] # top edge
            weights[:,-1] *= (pixfrac[0] + cellfactor) % 1 # right edge
            weights[-1,:] *= (pixfrac[0] + cellfactor) % 1 # bottom edge
            #set weights of blank pixels to zero
            weights *= pixelNew != nodatavalue

        # find out if the new pixel has a valid value:
        weightSum = weights.sum()
        if weightSum != 0:
            weighted = weights * pixelNew
            imageNew[rowNew][colNew] = weighted.sum() / weightSum
        else:
            imageNew[rowNew][colNew] = nodatavalue

# trim extraneous cells from edges
# top row
while True:
    if (imageNew[0,:] != nodatavalue).sum() ==0:
        imageNew = imageNew[1:,:]
    else:
        break
# bottom row
while True:
    if (imageNew[-1,:] != nodatavalue).sum() ==0:
        imageNew = imageNew[0:-1,:]
        lowerLeftNew.Y += cellSizeSAT
    else:
        break
# left column
while True:
    if (imageNew[:,0] != nodatavalue).sum() ==0:
        imageNew = imageNew[:,1:]
        lowerLeftNew.X += cellSizeSAT
    else:
        break
# right column
while True:
    if (imageNew[:,-1] != nodatavalue).sum() ==0:
        imageNew = imageNew[:,0:-1]
    else:
        break


arcpy.AddMessage('saving result')

# Convert Array to raster (keep the origin and cellsize the same as the input)
newRaster = arcpy.NumPyArrayToRaster(imageNew,lowerLeftNew,cellSizeSAT, value_to_nodata=nodatavalue)
arcpy.DefineProjection_management(newRaster, prjSAT)
newRaster.save(outImg)


# arcpy.AddMessage('done')
