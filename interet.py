import sys
import time
import rasterio
import simplekml
from math import radians, cos, sin, asin, sqrt
from pathlib import Path


DATASET1 = rasterio.open("tid.tif")
BOUNDS1 = DATASET1.bounds
TID = DATASET1.read(1)

DATASET2 = rasterio.open("scientific.tif")
BOUNDS2 = DATASET2.bounds
INTERET = DATASET2.read(1)

row, col = DATASET1.index(-36.3, 54.0)

print(row // 24, col // 24)

row, col = DATASET2.index(-36.3, 54.0)

print(row, col)

exit()

print(DATASET1.width, DATASET1.height)
print(DATASET2.width, DATASET2.height)

point = (500, 500)

p1 = TID[point[0], point[1]]
p2 = INTERET[point[0], point[1]]


print(DATASET1.xy(point[0], point[1]))
print(DATASET2.xy(point[0], point[1]))
