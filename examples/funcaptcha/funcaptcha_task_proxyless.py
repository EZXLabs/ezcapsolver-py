"""Solve a FunCaptcha (Arkose Labs) challenge.

Task type: ``FuncaptchaTaskProxyless``

Docs: https://docs.ezxlabs.com/docs/captcha/api/funcaptcha
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient, FunCaptchaTask


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            FunCaptchaTask(
                website_url="https://example.com",
                website_key="your_public_key",
                # Arkose Labs blob, passed as a JSON string like {"blob":"..."}.
                data=None,
                # Only when the site serves Arkose Labs from a custom subdomain.
                api_js_subdomain=None,
                # FunCaptcha expects protocol://host:port:username:password
                # rather than the usual proxy format, and a rotating proxy has
                # to support sessions.
                proxy=os.environ.get("EZCAPTCHA_PROXY"),
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
