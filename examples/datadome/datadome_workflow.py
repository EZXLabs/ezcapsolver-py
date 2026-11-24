"""Clear a DataDome challenge in one call and get the cookie it issues.

Task type: ``DataDomeTaskProxyless`` (steps one to three, run inside the call)

Needs the ``datadome`` extra: ``pip install 'ezcapsolver-py[datadome]'``.

The call fetches the page, locates and loads the challenge, reads its script,
asks the service for the answer, and submits it. Browser-side requests go
through the proxy with the Chrome TLS fingerprint the user agent names, so keep
using both for the requests that carry the cookie.

Docs: https://docs.ezxlabs.com/docs/captcha/api
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient
from ezcapsolver.ext import DataDomeChallenge

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
)


async def main() -> None:
    async with AsyncEzCapSolverClient("YOUR_API_KEY") as client:
        cookie = await client.solve_data_dome_workflow(
            DataDomeChallenge(
                target_url="https://example.com/signup",
                user_agent=USER_AGENT,
                proxy=os.environ.get("EZCAPTCHA_PROXY"),
            )
        )
        if cookie is None:
            print("DataDome did not intercept the page")
        else:
            print(f"Cookie:   {cookie.name}={cookie.value}")
            print(f"Domain:   {cookie.domain}")
        print(f"Balance:  {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
