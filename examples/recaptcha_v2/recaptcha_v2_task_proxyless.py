"""Solve a reCAPTCHA v2 challenge.

Task type: ``ReCaptchaV2TaskProxyless``

The site below is Google's own reCAPTCHA demo page, so this example runs as
written once ``EZCAPTCHA_API_KEY`` is set.

``sync_solve_recaptcha_v2_task_proxyless`` runs the same task on the service's
synchronous endpoint. It is a coroutine too — ``sync`` names the endpoint, not
the calling convention.

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient


async def main() -> None:
    # With no key passed, the client reads EZCAPTCHA_API_KEY from the environment.
    async with AsyncEzCapSolverClient() as client:
        # Creates the task, then polls until the worker finishes it.
        solved = await client.solve_recaptcha_v2_task_proxyless(
            website_url="https://www.google.com/recaptcha/api2/demo",
            website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
