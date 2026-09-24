"""Classify a reCAPTCHA v2 image grid.

Task type: ``ReCaptchaV2Classification``

Classification runs through the synchronous endpoint: the result comes back
inline, so there is nothing to poll and ``Solved.task_id`` is ``None``.

The result exposes ``type``, ``has_object``, ``objects`` and ``extra`` directly.
Use ``is_multi`` and ``is_single`` to check the result kind. Unknown kinds keep
their original type and additional fields, with the full JSON in ``Solved.raw``.

Docs: https://docs.ezxlabs.com/docs/captcha/api/recaptcha-v2
"""

import asyncio
import base64
from pathlib import Path

from ezcapsolver import (
    AsyncEzCapSolverClient,
    ReCaptchaV2ClassificationTask,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


async def main() -> None:
    # A single image asking about crosswalks, which the worker answers with a
    # yes or no. The 3x3 and 4x4 fixtures sit alongside it; those return the
    # indexes of the cells to click instead, so pass a matching ``size``.
    image = base64.b64encode((FIXTURES / "crosswalks1x1.jpg").read_bytes()).decode()

    async with AsyncEzCapSolverClient() as client:
        solved = await client.sync_solve(
            ReCaptchaV2ClassificationTask(
                image=image,
                # Google object identifier; /m/014xcs is "crosswalk".
                question="/m/014xcs",
                size=1,
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        solution = solved.solution
        if solution.is_multi:
            print(f"Cells:      {solution.objects}")
        elif solution.is_single:
            print(f"Has object: {solution.has_object}")
        else:
            print(f"Type:       {solution.type}")
            print(f"Raw:        {solved.raw}")

        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
