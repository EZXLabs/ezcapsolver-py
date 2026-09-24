"""Classify a FunCaptcha challenge image.

Task type: ``FunCaptchaClassification``

Classification runs through the synchronous endpoint, so ``Solved.task_id`` is
``None``.

This type has no confirmed solution schema yet. Guessing at fields would be
worse than none — it would promise a contract that does not exist — so
``FunCaptchaClassificationSolution`` declares none, and everything the worker
returns lands in its ``extra`` mapping. Read results from there for now; fields
get promoted out of ``extra`` as samples confirm them.

Docs: https://docs.ezxlabs.com/docs/captcha/api/funcaptcha
"""

import asyncio
import base64
from pathlib import Path

from ezcapsolver import AsyncEzCapSolverClient, FunCaptchaClassificationTask

# Point this at the challenge image captured from the Arkose Labs iframe.
IMAGE = Path(__file__).parent.parent / "fixtures" / "crosswalks1x1.jpg"


async def main() -> None:
    image = base64.b64encode(IMAGE.read_bytes()).decode()

    async with AsyncEzCapSolverClient() as client:
        solved = await client.sync_solve(
            FunCaptchaClassificationTask(
                image=image,
                # The instruction text shown above the challenge.
                question="Pick the image that is the correct way up",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        # The model declares no fields yet, so read the worker's output here.
        for name, value in solved.solution.extra.items():
            print(f"  {name}: {value}")
        print(f"Raw:        {solved.raw}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
