"""Solve a PerimeterX (Press & Hold) challenge.

Task type: ``PerimeterX``

What the protected site checks are the cookies the solution carries — ``_px3``
above all. The wire names lead with an underscore; the Python fields drop it,
because a leading underscore means "private" in Python, which is the opposite
of what these fields are for.

Docs: https://docs.ezxlabs.com/docs/captcha/api/perimeterx
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, PerimeterXTask


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        solved = await client.solve(
            PerimeterXTask(
                # PerimeterX application identifier; it starts with PX.
                website_key="PXxxxxxxxx",
                invisible=False,
            )
        )

        solution = solved.solution
        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Task ID:    {solved.task_id or '-'}")
        print(f"_px3:       {solution.px3[:64]}...")
        print(f"_pxvid:     {solution.pxvid or '-'}")
        print(f"_pxde:      {solution.pxde or '-'}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
