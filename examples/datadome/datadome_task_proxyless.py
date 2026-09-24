"""Clear a DataDome challenge, both steps.

Task type: ``DataDomeTaskProxyless``

The challenge takes two calls that share one solution model: step one returns
the challenge address in ``url``, step two the validation instructions. Both
run through the synchronous endpoint.

Docs: https://docs.ezxlabs.com/docs/captcha/api
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, DataDomeStep, DataDomeTask

# The interstitial or slider page, captured and base64-encoded.
CHALLENGE_HTML_B64 = "base64_encoded_challenge_page"


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        # Step one: find out where the challenge lives.
        first = await client.sync_solve(
            DataDomeTask(
                html_b64=CHALLENGE_HTML_B64,
                step=DataDomeStep.ONE,
                referer="https://example.com",
            )
        )
        print(f"Kind:       {first.solution.kind or '-'}")
        print(f"Challenge:  {first.solution.url or '-'}")

        # Fetch that page, capture the slider image, then ask for the
        # validation instructions.
        second = await client.sync_solve(
            DataDomeTask(
                html_b64=CHALLENGE_HTML_B64,
                step=DataDomeStep.TWO,
                image="base64_encoded_slider_image",
                referer=first.solution.url,
            )
        )
        print(f"Validate:   {second.solution.url or '-'}")
        print(f"Body:       {second.solution.body or '-'}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
