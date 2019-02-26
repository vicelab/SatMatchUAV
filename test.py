import numpy
import math
import arcpy
import sys


# Aggregates the pixels in an image to correspond with the pixel locations of a reference image (using MEAN).
# Since the method aggregates fractional pixels, there is no need for the size of the reference pixels to be integer multiples of the source pixels.
# Both the reference and the source image need to be in the same projection!


# inIMG = 'C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/uav2sat-resample\\Madera_2018-07-05_UAV_GRN_Sat-Rsmp_v01.tif'
# inSAT = 'C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Sat_files\\LC08_L1TP_042035_20180705_20180717_01_T1_sr_band3.tif'
# outIMG ='C:/Users/aanderson29/Box Sync/[VICE Lab]/RESEARCH/PROJECTS/Gallo/Madera Block 760/METRIC/WIP/Andy/Testing\\testingscat.csv'
# outTbl = arcpy.GetParameterAsText(2)
# noDataThreshold = 0.1


def hello(a):
    print a


if __name__ == '__main__':
    param = sys.argv
    if len(param) == 2:
        a = param[1]
    else:
        a = 'hithere'
    hello(a)

a = 'hi Mom'
hello(a)
