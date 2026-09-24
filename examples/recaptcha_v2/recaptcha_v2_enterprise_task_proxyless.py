"""Solve a reCAPTCHA v2 Enterprise challenge.

Task type: ``ReCaptchaV2EnterpriseTaskProxyless``

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV2EnterpriseTask


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            ReCaptchaV2EnterpriseTask(
                website_url="https://example.com",
                website_key="your_enterprise_key",
                # Enterprise pages often render both; leave them out if absent.
                sa="",
                s="",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
