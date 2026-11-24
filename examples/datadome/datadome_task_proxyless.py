"""Clear a DataDome challenge step by step.

Task type: ``DataDomeTaskProxyless``

The three steps share one request and one solution model, and all run through
the synchronous endpoint. Between them you fetch the pages yourself:

1. Step one turns the intercepted page into the challenge address in ``url``.
2. Fetch that page and its challenge script, then ask step two whether the
   service already caches the script, by its hash.
3. Step three returns the submission in ``url`` and ``body``, and how long to
   wait before sending it in ``submit_after_ms``. Submitting it from the
   challenge page brings back the cookie.

Docs: https://docs.ezxlabs.com/docs/captcha/api
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, DataDomeStep, DataDomeTask

# The browser the pages were fetched with.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
)
# The page DataDome intercepted, captured and base64-encoded.
INTERCEPTED_HTML_B64 = "base64_encoded_intercepted_page"
# The challenge page step one points at, captured and base64-encoded.
CHALLENGE_HTML_B64 = "base64_encoded_challenge_page"
# MD5 of the challenge script without its first-line version banner.
SCRIPT_HASH = "md5_of_the_challenge_script"
# The challenge script itself, base64-encoded.
SCRIPT_B64 = "base64_encoded_challenge_script"


async def main() -> None:
    async with AsyncEzCapSolverClient("YOUR_API_KEY") as client:
        # Step one: find out where the challenge lives.
        first = await client.sync_solve(
            DataDomeTask(
                step=DataDomeStep.ONE,
                html_b64=INTERCEPTED_HTML_B64,
                referer="https://example.com",
                user_agent=USER_AGENT,
            )
        )
        challenge_url = first.solution.url or ""
        print(f"Challenge:  {challenge_url or '-'}")

        # Fetch that page and its script, then ask whether the service caches it.
        second = await client.sync_solve(DataDomeTask(step=DataDomeStep.TWO, hash=SCRIPT_HASH))
        cached = bool(second.solution.status)
        print(f"Cached:     {cached}")

        # Step three: the submission. A cached script only needs its hash.
        third = await client.sync_solve(
            DataDomeTask(
                step=DataDomeStep.THREE,
                html_b64=CHALLENGE_HTML_B64,
                referer=challenge_url,
                user_agent=USER_AGENT,
                external_js_hash=SCRIPT_HASH if cached else None,
                external_js_base64=None if cached else SCRIPT_B64,
            )
        )
        print(f"Kind:       {third.solution.kind or '-'}")
        print(f"Submit to:  {third.solution.url or '-'}")
        print(f"Body:       {third.solution.body or '-'}")
        print(f"Wait (ms):  {third.solution.submit_after_ms or 0}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
