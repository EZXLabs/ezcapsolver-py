"""Build the synchronous client in full, then solve one task with it.

Same API as ``async_client_task.py`` with the ``await`` taken out. Every
constructor setting is spelled out below. All of them have defaults, so
``EzCapSolverClient()`` on its own is already a working client.

The two examples differ in one place on purpose: that one passes a task object
to ``solve()``, this one calls the per-type shortcut, which takes the fields
directly. Both entry points exist on both clients.
"""

import os

from ezcapsolver import EzCapSolverClient, PollingConfig


def main() -> None:
    client = EzCapSolverClient(
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
        # one reusable object, and http_client=httpx.Client(...) to share a
        # connection pool. A borrowed client is yours to close.
    )

    with client:
        # Google's own reCAPTCHA demo page, so this runs as written.
        # Typed as Solved[ReCaptchaSolution], inferred from the method.
        solved = client.solve_recaptcha_v2_task_proxyless(
            website_url="https://www.google.com/recaptcha/api2/demo",
            website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        )
        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id}")
        print(f"User-Agent: {solved.solution.user_agent}")
        print(f"Token:      {solved.solution.token[:64]}...")
        print(f"Balance:    {client.get_balance()}")


if __name__ == "__main__":
    main()
