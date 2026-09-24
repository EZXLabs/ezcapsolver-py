"""Generate a DataDome tags payload.

Task type: ``DataDomeTagsTaskProxyless``

Tags is the telemetry stream DataDome collects before it decides to challenge
at all, so this runs on every page rather than only on the challenge page. It
uses the synchronous endpoint.

Docs: https://docs.ezxlabs.com/docs/captcha/api
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, DataDomeJsType, DataDomeTagsTask

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.sync_solve(
            DataDomeTagsTask(
                # DataDome JavaScript key, read from the tags script tag.
                ddk="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                jstype=DataDomeJsType.CH,
                # Session identifier. An empty string is valid on first contact.
                cid="",
                # One-based packet counter; increment it on every send.
                bpc=1,
                referer="https://example.com",
                ua=UA,
                # External business fields forwarded to the worker verbatim.
                fields={},
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Endpoint:   {solved.solution.url or '-'}")
        print(f"Body:       {solved.solution.body or '-'}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
