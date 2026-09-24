"""Solve a Cloudflare Turnstile widget.

Task type: ``CloudFlareTurnstileTask``

Unlike the five-second challenge, Turnstile does return a token — plus the
headers to send alongside it.

Docs: https://docs.ezxlabs.com/docs/captcha/api/turnstile
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient, CloudflareTurnstileTask


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            CloudflareTurnstileTask(
                website_url="https://example.com",
                # Turnstile site keys start with 0x.
                website_key="0x4AAAAAAA...",
                proxy=os.environ.get("EZCAPTCHA_PROXY"),
                # Some widgets embed metadata the worker needs; pass it through
                # when the page renders one.
                rq_data=None,
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"Token:      {solved.solution.token[:64]}...")
        for name, value in solved.solution.header.items():
            print(f"Header:     {name}: {value}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
