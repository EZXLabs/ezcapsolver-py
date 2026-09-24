"""Generate an Incapsula Reese84 sensor payload.

Task type: ``IncapsulaTaskProxyless``

Incapsula runs through the synchronous endpoint, so the solution comes back
inline and ``Solved.task_id`` is ``None``.

``solution.data`` is stringified JSON and has to be POSTed to the Reese84
endpoint verbatim. The SDK deliberately does not unwrap it — that would change
what you have to send.

Docs: https://docs.ezxlabs.com/docs/captcha/api/incapsula
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient, IncapsulaTask

# Full source of the Reese84 sensor script, fetched from `script_url`.
SCRIPT = ""

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.sync_solve(
            IncapsulaTask(
                script=SCRIPT,
                script_url="https://example.com/xxxxx?d=example.com",
                page_url="https://example.com",
                # Must match the Accept-Language header of the browser flow.
                accept_language="en-US,en;q=0.9",
                ua=UA,
                proxy=os.environ.get("EZCAPTCHA_PROXY"),
                # Only the sites with PoW challenges enabled need this one.
                pow=os.environ.get("EZCAPTCHA_INCAPSULA_POW"),
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Status:     {solved.solution.status if solved.solution.status else '-'}")
        print(f"Data:       {solved.solution.data[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
