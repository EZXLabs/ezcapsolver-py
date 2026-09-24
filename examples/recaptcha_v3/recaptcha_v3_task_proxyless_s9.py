"""Solve a reCAPTCHA v3 challenge, requiring a score of 0.9 or above.

Task type: ``ReCaptchaV3TaskProxylessS9``

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v3
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV3S9Task


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            ReCaptchaV3S9Task(
                website_url="https://example.com",
                website_key="your_site_key",
                page_action="examples/v3scores",
                website_title="",
                is_invisible=True,
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
