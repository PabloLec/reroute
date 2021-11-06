import time
import aiohttp
import asyncio
import pickle
from random import randint
from re import X, findall

xmax = -8.0
xmin = -32.0
ymin = 34.0
ymax = 59.0


def bathy_request_url(x, y):
    return f"https://ows.emodnet-bathymetry.eu/wms?bbox={xmin},{ymin},{xmax},{ymax}&styles=&format=jpeg&request=GetFeatureInfo&layers=quality_index&query_layers=quality_index&width=240&height=250&x={x}&y={y}"


class Grid:
    def __init__(self, height, width):
        self.master = []
        self.create_empty_grid(height, width)

    def save_grid(self, file="grid.pkl"):
        with open(file, "wb") as f:
            pickle.dump(grid, f)

    def create_empty_grid(self, height, width):
        for y in range(height):
            self.master.append([])
            for x in range(width):
                self.master[-1].append(Cell(x, y))

    def get_bathy(self):
        asyncio.run(self.send_bathy_requests())

    async def send_bathy_requests(self):
        async with aiohttp.ClientSession() as session:
            queries = []
            for row in self.master:
                for cell in row:
                    queries.append(cell.fetch_bathy(session))
            await asyncio.gather(*queries)


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bathy = 0

    def __repr__(self):
        return str(f"X:{self.x} Y:{self.y} B:{self.bathy}")

    async def fetch_bathy(self, session):
        async def request(url):
            async with session.get(url=url) as response:
                resp = await response.read()
                if not response.ok:
                    return False
                resp = str(resp)
                combined = findall("combined \= ([0-9]+)", resp)
                self.bathy = 0 if len(combined) == 0 else combined[0]

                return True

        url = bathy_request_url(self.x, self.y)
        try:
            while True:
                resp = await request(url)
                if resp:
                    break
                time.sleep(randint(1, 9) / 10)
        except Exception as e:
            print("Unable to get url {} due to {}.".format(url, e))


grid = Grid(240, 250)
start = time.time()
grid.get_bathy()
end = time.time()

print(grid.master)
grid.save_grid()

print("Took {} seconds to pull.".format(end - start))
