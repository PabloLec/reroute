import sys
import time
import rasterio
import simplekml
from math import radians, cos, sin, asin, sqrt
from pathlib import Path

sys.setrecursionlimit(1000000)


def haversine(A, B):
    xy1 = BATHY_DATASET.xy(A[0], A[1])
    xy2 = BATHY_DATASET.xy(B[0], B[1])
    lon1, lat1, lon2, lat2 = xy1[0], xy1[1], xy2[0], xy2[1]
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


STEP = 48

VALUES = {
    0: None,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 0,
    40: 100,
    41: 100,
    42: 100,
    43: 100,
    44: 100,
    45: 100,
    70: 100,
    71: 100,
    72: 100,
}

BATHY_DATASET = rasterio.open("tid.tif")
BOUNDS = BATHY_DATASET.bounds
TID = BATHY_DATASET.read(1)

DATASET2 = rasterio.open("scientific.tif")
SCIENTIFIC = DATASET2.read(1)

DATASET3 = rasterio.open("economy.tif")
ECONOMY = DATASET3.read(1)

DATASET4 = rasterio.open("telecom.tif")
TELECOM = DATASET4.read(1)

DATASET5 = rasterio.open("traffic.tif")
TRAFFIC = DATASET5.read(1)

DATASET6 = rasterio.open("depth.tif")
DEPTH = BATHY_DATASET.read(1)

POINT_A = None
POINT_B = None
MAX_DIST = None
MIN_DEPTH = None
MAX_DEPTH = None
# A_B_DISTANCE = haversine(POINT_A, POINT_B)

minX = None
maxX = None
minY = None
maxY = None

SOLUTIONS = {}


def is_good_enough(point):
    return abs(point[0] - POINT_B[0]) <= STEP and abs(point[1] - POINT_B[1]) <= STEP


def get_value(point):
    if not MIN_DEPTH <= DEPTH[point[0], point[1]] <= MAX_DEPTH:
        return 0

    tid = VALUES[TID[point[0], point[1]]]
    if tid is None:
        return tid
    scientific = SCIENTIFIC[point[0] // 24, point[1] // 24] * 100
    economy = ECONOMY[point[0] // 24, point[1] // 24] * 100
    telecom = TELECOM[point[0] // 24, point[1] // 24] * 50
    traffic = TRAFFIC[point[0] // 24, point[1] // 24]
    traffic = max(traffic, 0) * 50

    return tid + scientific + economy + telecom + traffic


def get_detailed_value(point):
    tid = VALUES[TID[point[0], point[1]]]
    scientific = SCIENTIFIC[point[0] // 24, point[1] // 24] * 100
    economy = ECONOMY[point[0] // 24, point[1] // 24] * 100
    telecom = TELECOM[point[0] // 24, point[1] // 24] * 50
    traffic = TRAFFIC[point[0] // 24, point[1] // 24]
    traffic = max(traffic, 0) * 50

    return f"BATHY: {tid}\nSCIENTIFIC: {scientific}\nECONOMY: {economy}\nTELECOM: {telecom}\nTRAFFIC: {traffic}"


def get_angle(previous, current):
    angle = ""
    if previous[0] < current[0]:
        angle += "S"
    elif previous[0] > current[0]:
        angle += "N"
    if previous[1] < current[1]:
        angle += "W"
    elif previous[1] > current[1]:
        angle += "E"

    return ""


def get_route(route, value, length, current, seen=set()):
    global SOLUTIONS

    if not 0 <= current[0] <= 21600:
        return
    if not 0 <= current[1] <= 21600:
        return
    if not minX <= current[0] <= maxX:
        return
    if not minY <= current[1] <= maxY:
        return

    # angle = get_angle(route[-1], current) if len(route) > 1 else ""
    if len(route) > 0:
        length += haversine(current, route[-1])
    if length >= MAX_DIST:
        return

    route.append(current)
    seen.add(current)
    added_value = get_value(current)
    if added_value is None:
        return
    value = value + added_value

    if is_good_enough(current):
        for x in route:
            if VALUES[TID[x[0], x[1]]] is None:
                return
        if value in SOLUTIONS and SOLUTIONS[value]["length"] < length:
            SOLUTIONS[value] = {"route": list(route), "length": length}
        elif value not in SOLUTIONS:
            SOLUTIONS[value] = {"route": list(route), "length": length}

    if (current[0], current[1] - STEP) not in seen:
        # bottom
        get_route(
            route.copy(),
            value,
            length,
            (current[0], current[1] - STEP),
            seen.copy(),
        )

    if (current[0] - STEP, current[1] - STEP) not in seen:
        # bottom-left
        get_route(
            route.copy(),
            value,
            length,
            (current[0] - STEP, current[1] - STEP),
            seen.copy(),
        )

    if (current[0] + STEP, current[1] - STEP) not in seen:
        # bottom-left
        get_route(
            route.copy(),
            value,
            length,
            (current[0] + STEP, current[1] - STEP),
            seen.copy(),
        )

    if (current[0], current[1] + STEP) not in seen:
        # up
        get_route(
            route.copy(), value, length, (current[0], current[1] + STEP), seen.copy()
        )

    if (current[0] - STEP, current[1] + STEP) not in seen:
        # bottom-left
        get_route(
            route.copy(),
            value,
            length,
            (current[0] - STEP, current[1] + STEP),
            seen.copy(),
        )

    if (current[0] + STEP, current[1] + STEP) not in seen:
        # bottom-left
        get_route(
            route.copy(),
            value,
            length,
            (current[0] + STEP, current[1] + STEP),
            seen.copy(),
        )

    if (current[0] - STEP, current[1]) not in seen:
        get_route(
            route.copy(), value, length, (current[0] - STEP, current[1]), seen.copy()
        )

    if (current[0] + STEP, current[1]) not in seen:
        get_route(
            route.copy(), value, length, (current[0] + STEP, current[1]), seen.copy()
        )

    return route, value, length


def main(A, B, dist, sensor, save_path, exit_code):
    global POINT_A
    global POINT_B
    global MAX_DIST
    global MIN_DEPTH
    global MAX_DEPTH
    global STEP
    global minX, maxX, minY, maxY

    A = {"x": float(A[0]), "y": float(A[1])}
    B = {"x": float(B[0]), "y": float(B[1])}

    colA, rowA = BATHY_DATASET.index(A["x"], A["y"])
    colB, rowB = BATHY_DATASET.index(B["x"], B["y"])

    POINT_A = (colA, rowA)
    POINT_B = (colB, rowB)

    MAX_DIST = float(dist) + haversine(POINT_A, POINT_B)
    STEP = 24 * round((MAX_DIST // 2) / 24)
    print("STEP:", STEP)

    if sensor == 0:
        MIN_DEPTH = 0
        MAX_DEPTH = 100
    elif sensor == 1:
        MIN_DEPTH = 5
        MAX_DEPTH = 500
    elif sensor == 2:
        MIN_DEPTH = 30
        MAX_DEPTH = 3000
    elif sensor == 3:
        MIN_DEPTH = 100
        MAX_DEPTH = 12000

    minX = min(colA, colB) - min(colA, colB)
    maxX = max(colA, colB) + max(colA, colB)
    minY = min(rowA, rowB) - min(rowA, rowB)
    maxY = max(rowA, rowB) + max(rowA, rowB)

    print("POINT_A", POINT_A)
    print("POINT_B", POINT_B)
    print("MAX_DIST", MAX_DIST)

    start = time.time()

    get_route([], 0, 0, POINT_A)
    print(SOLUTIONS.keys())

    end = time.time()

    print(f"TIME: {end-start}")

    if len(SOLUTIONS.keys()) == 0:
        exit_code.value = 1
        print("EXIT_CODE 1")
        return

    best = max(SOLUTIONS.keys())
    route = SOLUTIONS[best]["route"]
    length = SOLUTIONS[best]["length"]
    route.append(POINT_B)
    print("POINT_A", POINT_A)
    print("POINT_B", POINT_B)
    for point in route:
        print(point)
        print(get_detailed_value(point))
        print(" = = = = = = = = = = = = = =")
    print("\n", length, "km")

    kml = simplekml.Kml()

    for i in range(len(route) - 1):
        current = BATHY_DATASET.xy(route[i][0], route[i][1])
        next = BATHY_DATASET.xy(route[i + 1][0], route[i + 1][1])
        linestring = kml.newlinestring(name=str(i))
        linestring.coords = [(current[0], current[1]), (next[0], next[1])]
    kml.save(save_path)
    print(" KML SAVED ")


def test():
    A = (-4.808, 47.585)
    B = (-25.18, 40.45)
    dist = 1250
    main(A, B, dist, 3, "/home/pablo/projets/reroute/test.kml", None)


# test()
