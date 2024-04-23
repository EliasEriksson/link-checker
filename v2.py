from pathlib import Path
from typing import DefaultDict
import sys
import asyncio
import csv
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.parse import urlparse, ParseResult
import aiohttp


class Job:
    row: int
    location: str
    url: ParseResult

    def __init__(self, row: int, location: str, url: ParseResult) -> None:
        self.row = row
        self.location = location
        self.url = url

    def __repr__(self) -> str:
        url = f"{self.url.scheme}://{self.url.netloc}/{self.url.path}"
        return f"{self.__class__.__name__}(location={self.location}, url={url})"


class Result:
    job: Job
    status: int

    def __init__(self, job: Job, status: int) -> None:
        self.job = job
        self.status = status

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(job={self.job}, status={self.status})"


def create_jobs(input: Path) -> DefaultDict[str, list[Job]]:
    jobs: DefaultDict[str, list[Job]] = defaultdict(list)
    with open(input, "r") as file:
        reader = csv.reader(file, "excel")
        for row, (location, description) in enumerate(reader):
            soup = BeautifulSoup(description, "html.parser")
            for a in soup.find_all("a"):
                url = urlparse(a.get("href"))
                if url:
                    origin = f"{url.scheme}://{url.hostname}"
                    jobs[origin].append(Job(row, location, url))
    return jobs


async def process(jobs: list[Job]) -> list[Result]:
    results: list[Result] = []
    client = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(connect=5))
    async with client as session:
        for job in jobs:
            url = job.url.geturl()
            try:
                async with session.get(url) as response:
                    result = Result(job, response.status)
            except aiohttp.ServerTimeoutError:
                result = Result(job, 600)
            except aiohttp.ServerConnectionError:
                result = Result(job, 500)
            except aiohttp.ClientConnectorError:
                result = Result(job, 600)
            except aiohttp.ClientError:
                result = Result(job, 400)
            finally:
                print(f"Response status {result.status} from link {url}")
                results.append(result)
    return results


def save_results(output: Path, results: list[Result]) -> None:
    with open(output, "w") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Location",
                "In data row number",
                "Requested URL",
                "Response status",
            ]
        )
        for result in results:
            writer.writerow(
                [
                    result.job.location,
                    result.job.row,
                    result.job.url.geturl(),
                    result.status,
                ]
            )


async def main(input: Path, output: Path) -> None:
    jobs = create_jobs(input)
    tasks = [asyncio.create_task(process(jobs[origin])) for origin in jobs]
    results = sorted(
        (result for list in await asyncio.gather(*tasks) for result in list),
        key=lambda result: result.job.row,
    )
    save_results(output, results)


if __name__ == "__main__":
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
