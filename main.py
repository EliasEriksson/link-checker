import asyncio
from pathlib import Path
import csv
import sys
import aiohttp


async def request(link: str) -> tuple[str, int]:
    print(f"Requesting: {link}")
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(connect=10)) as client:
            async with client.get(link) as response:
                print(f"Response status {response.status} from link {link}")
                return link, 200 <= response.status < 300
    except aiohttp.ServerTimeoutError:
        print(f"Failed to request: {link}")
        return link, 502


async def main(input: Path, output: Path) -> None:
    with open(input) as input:
        reader = csv.reader(input)
        links = [row[0] for row in reader]
    requests = [asyncio.create_task(request(link)) for link in links]
    result = await asyncio.gather(*requests)
    with open(output, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["Link", "Status"])
        writer.writerows(result)


if __name__ == '__main__':
    try:
        input = Path(sys.argv[1])
    except IndexError:
        print("Input file required as first sysarg.")
        sys.exit(1)
    try:
        output = Path(sys.argv[2])
    except IndexError:
        print("Output file required as second sysarg.")
        sys.exit(1)
    asyncio.run(main(input, output))
