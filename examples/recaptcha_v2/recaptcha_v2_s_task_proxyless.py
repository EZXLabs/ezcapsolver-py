"""Solve a reCAPTCHA v2 challenge that carries the ``s`` parameter.

Task type: ``ReCaptchaV2STaskProxyless``

Some sites bind the challenge to a per-session ``s`` value rendered into the
page. Read it from the page source and pass it through unchanged.

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV2STask


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            ReCaptchaV2STask(
                website_url="https://example.com",
                website_key="your_site_key",
                # Challenge-bound value scraped from the protected page.
                s="challenge_bound_s_parameter",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
