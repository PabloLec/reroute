import time
import aiohttp
import asyncio
from random import randint


async def get(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            print(
                "Successfully got url {} with resp of length {}.".format(url, len(resp))
            )
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])
    print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))


urls = [
    "https://ows.emodnet-bathymetry.eu/wms?bbox=2.00,52.00,5.99,55.01&styles=&format=jpeg&request=GetFeatureInfo&layers=quality_index&query_layers=quality_index&width=1024&height=1024&x=550&y=550"
]

for _ in range(1000):
    urls.append(
        f"https://ows.emodnet-bathymetry.eu/wms?bbox=2.00,52.00,5.99,55.01&styles=&format=jpeg&request=GetFeatureInfo&layers=quality_index&query_layers=quality_index&width=1024&height=1024&x={randint(0,1024)}&y={randint(0,1024)}"
    )
start = time.time()
asyncio.run(main(urls))
end = time.time()

print("Took {} seconds to pull {} websites.".format(end - start, len(urls)))
