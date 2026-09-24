"""Drive the task workflow by hand, and reach task types the SDK does not know.

``solve()`` creates a task and waits for it. When you need the payload or the
polling policy under your own control, ``create_task()`` and ``get_result()``
are the two halves it is built from.

``solve_raw()`` goes one step further: it takes a bare task type string and a
dictionary keyed by **wire** names, so a type the service ships today is usable
without waiting for an SDK release.
"""

import asyncio

from ezcapsolver import AsyncEzCapSolverClient, ReCaptchaV2Task, TaskType

POLL_INTERVAL = 3.0
MAX_ATTEMPTS = 24


async def manual_polling(client: AsyncEzCapSolverClient) -> None:
    """Create a task, then poll it on your own schedule."""
    task_id = await client.create_task(
        ReCaptchaV2Task(
            website_url="https://www.google.com/recaptcha/api2/demo",
            website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        )
    )
    print(f"Created:    {task_id}")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # A task that was just enqueued is almost always still processing, so
        # wait before the first query rather than after it.
        await asyncio.sleep(POLL_INTERVAL)
        result = await client.get_result(task_id)

        if result.is_ready:
            print(f"Solution:   {result.solution}")
            return
        print(f"Status:     {result.status} ({attempt}/{MAX_ATTEMPTS})")

    print(f"Gave up after {MAX_ATTEMPTS} attempts; the task was still billed.")


async def unknown_task_type(client: AsyncEzCapSolverClient) -> None:
    """Solve a task type this release has no model for."""
    # Keys are wire names and are sent verbatim; the result is undecoded.
    solved = await client.solve_raw(
        "BrandNewTaskType",
        {"websiteURL": "https://example.com", "someNewField": 42},
    )
    print(f"Task ID:    {solved.task_id or '-'}")
    print(f"Raw:        {solved.solution}")

    # The same type can go to the synchronous endpoint instead, which answers on the
    # creating request and therefore returns no task ID.
    solved = await client.sync_solve_raw("BrandNewSyncType", {"input": "..."})
    print(f"Raw:        {solved.solution}")

    # Task types the SDK does know are available as an enum, so a known type
    # never has to be spelled out as a string.
    print(f"Known:      {TaskType.RECAPTCHA_V2_TASK_PROXYLESS}")


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        await manual_polling(client)
        await unknown_task_type(client)


if __name__ == "__main__":
    asyncio.run(main())
