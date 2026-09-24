"""Classify an hCaptcha challenge image.

Task type: ``HCaptchaClassification``

Classification runs through the synchronous endpoint, so ``Solved.task_id`` is
``None``.

Every field is optional: different classification modules take different input
combinations, and the service contract does not state which are required. The
solution schema is unconfirmed too, so the raw JSON value comes back undecoded.

Docs: https://docs.ezxlabs.com/docs/captcha/api/hcaptcha
"""

import asyncio
import base64
from pathlib import Path

from ezcapsolver import AsyncEzCapSolverClient, HCaptchaClassificationTask

FIXTURES = Path(__file__).parent.parent / "fixtures"


async def main() -> None:
    image = base64.b64encode((FIXTURES / "crosswalks1x1.jpg").read_bytes()).decode()

    async with AsyncEzCapSolverClient() as client:
        solved = await client.sync_solve(
            HCaptchaClassificationTask(
                # A grid module would send `images` and `anchors` instead.
                image=image,
                question="Please click each image containing a crosswalk",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Solution:   {solved.solution}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
