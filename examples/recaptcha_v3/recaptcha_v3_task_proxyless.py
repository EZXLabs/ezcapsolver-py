"""Solve a reCAPTCHA v3 challenge.

Task type: ``ReCaptchaV3TaskProxyless``

v3 is scored rather than interactive, so the action name matters: the site
grades the token against the action it expected. ``is_invisible`` defaults to
``True`` here, unlike v2 — that difference is the service's, not the SDK's.

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v3
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV3Task


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            ReCaptchaV3Task(
                website_url="https://example.com",
                website_key="your_site_key",
                # Must match the action the protected page grades against.
                page_action="examples/v3scores",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
