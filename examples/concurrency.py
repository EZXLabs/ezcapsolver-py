"""Solve many challenges at once through a single client.

The client is read-only after construction and httpx owns the connection pool,
so one instance serves any number of coroutines. Building a client per task
only wastes connections.
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV2Task

SITES = [
    ("https://a.example.com", "6Lc-key-a"),
    ("https://b.example.com", "6Lc-key-b"),
    ("https://c.example.com", "6Lc-key-c"),
]


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        pending = [
            client.solve(ReCaptchaV2Task(website_url=url, website_key=key)) for url, key in SITES
        ]
        # return_exceptions keeps one failure from taking down the rest.
        results = await asyncio.gather(*pending, return_exceptions=True)

        for (url, _), result in zip(SITES, results, strict=True):
            if isinstance(result, BaseException):
                print(f"{url}: failed -> {result}")
            else:
                print(f"{url}: {result.solution.token[:40]}...")


if __name__ == "__main__":
    asyncio.run(main())
