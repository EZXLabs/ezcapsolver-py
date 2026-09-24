"""Solve a reCAPTCHA v2 challenge, requiring a score of 0.9 or above.

Task type: ``ReCaptchaV2TaskProxylessS9``

S9 is the same request as plain v2 — only the task type differs, which is why
``ReCaptchaV2S9Task`` is a subclass that overrides nothing but that.

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV2S9Task


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            ReCaptchaV2S9Task(
                website_url="https://example.com",
                website_key="your_site_key",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
