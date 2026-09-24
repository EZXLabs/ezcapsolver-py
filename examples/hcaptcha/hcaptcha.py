"""Solve an hCaptcha challenge.

Task type: ``HCaptcha``

The site below is hCaptcha's own demo page, so this example runs as written
once ``EZCAPTCHA_API_KEY`` is set.

``invisible`` and ``rqdata`` have no typed field on the service side, so they
travel through ``extra`` — the pass-through map every task model carries.

Docs: https://docs.ezxlabs.com/docs/captcha/api/hcaptcha
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient, HCaptchaTask


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            HCaptchaTask(
                website_url="https://accounts.hcaptcha.com/demo",
                website_key="a5f74b19-9e45-40e0-b45d-47ff91b7a6c2",
                lang="en-US",
                proxy=os.environ.get("EZCAPTCHA_PROXY"),
                # False because the demo page shows a checkbox. Sites that hide
                # it need True here.
                invisible=False,
                # Only the sites that publish an rqdata value need this one.
                rq_data=os.environ.get("EZCAPTCHA_HCAPTCHA_RQDATA"),
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"Pass UUID:  {solved.solution.generated_pass_uuid}")
        # Every request carrying the token must send this exact User-Agent.
        print(f"User-Agent: {solved.solution.ua or '-'}")
        # Fields this release does not model stay reachable through extra.
        print(f"Context ID: {solved.solution.extra.get('contextId', '-')}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
