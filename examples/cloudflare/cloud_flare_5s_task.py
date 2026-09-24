"""Clear the Cloudflare five-second challenge.

Task type: ``CloudFlare5STask``

A ``proxy`` is required for this type: the clearance is bound to the exit IP,
so the worker has to solve the challenge from the address you will replay it
from.

The result is not a token. It is the browser state the worker ended up with —
headers, clearance cookies and the TLS fingerprint — and clearing the challenge
means replaying all of it together against the protected site.

Docs: https://docs.ezxlabs.com/docs/captcha/api/cloudflare-5s
"""

import asyncio
import os

import httpx

from ezcapsolver import AsyncEzCapSolverClient, Cloudflare5sTask

TARGET = "https://example.com"


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            Cloudflare5sTask(
                website_url=TARGET,
                proxy=os.environ["EZCAPTCHA_PROXY"],
            )
        )

        solution = solved.solution
        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"TLS:        {solution.tls_version}")
        for name, value in solution.header.items():
            print(f"Header:     {name}: {value}")
        for name, value in solution.cookies.items():
            print(f"Cookie:     {name}={value}")

        # Replaying the state is the step that actually clears the challenge.
        # Send it through the same proxy the worker used, or the clearance will
        # be rejected.
        async with httpx.AsyncClient(
            headers=solution.header,
            cookies=solution.cookies,
            proxy=os.environ["EZCAPTCHA_PROXY"],
        ) as http:
            response = await http.get(TARGET)
            print(f"Replayed:   HTTP {response.status_code}")

        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
