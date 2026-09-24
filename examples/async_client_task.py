"""Build the asynchronous client in full, then solve one task with it.

Every constructor setting is spelled out below. All of them have defaults, so
``AsyncEzCapSolverClient()`` on its own is already a working client.
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient, PollingConfig, ReCaptchaV2Task


async def main() -> None:
    client = AsyncEzCapSolverClient(
        # Omit this entirely to read EZCAPTCHA_API_KEY from the environment.
        os.environ["EZCAPTCHA_API_KEY"],
        # Timeout for the asynchronous endpoints and balance queries.
        timeout=30.0,
        # Separate budget for synchronous-endpoint tasks, which block until the
        # worker is done — the service allows some types up to three minutes.
        sync_timeout=240.0,
        # How the asynchronous endpoint is polled: 50 tries, 3s apart.
        polling=PollingConfig(interval=3.0, max_attempts=50),
        # Optional developer application identifier.
        app_id=None,
        # Proxy the SDK uses to reach the EzCaptchaSolver API — not the one a worker
        # uses to reach the protected site. That is a task field.
        proxy=None,
        user_agent="my-app/1.0",
        # Also available: config=ClientConfig(...) to pass all of the above as
        # one reusable object, and http_client=httpx.AsyncClient(...) to share
        # a connection pool. A borrowed client is yours to close.
    )

    async with client:
        # Google's own reCAPTCHA demo page, so this runs as written.
        # Typed as Solved[ReCaptchaSolution], inferred from the task.
        solved = await client.solve(
            ReCaptchaV2Task(
                website_url="https://www.google.com/recaptcha/api2/demo",
                website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
