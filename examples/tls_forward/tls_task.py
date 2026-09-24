"""Forward one HTTP request through the worker's TLS fingerprint.

Task type: ``TlsTask``

Nothing about this type is a CAPTCHA: the worker replays your request with a
real browser's TLS fingerprint and hands the upstream response back. It runs
through the synchronous endpoint.

This example also shows ``ClientConfig``. Note that ``sync_timeout`` is a
separate budget from ``timeout`` — synchronous calls block until the worker
finishes, and the service allows some types up to three minutes.

Docs: https://docs.ezxlabs.com/docs/captcha/api/tls-forward
"""

import asyncio
import os

from ezcapsolver import AsyncEzCapSolverClient, ClientConfig, TlsForwardTask, TlsHttpMethod

CONFIG = ClientConfig(
    # Left unset, the key is read from EZCAPTCHA_API_KEY.
    timeout=30.0,
    sync_timeout=240.0,
)


async def main() -> None:
    async with AsyncEzCapSolverClient(config=CONFIG) as client:
        solved = await client.sync_solve(
            TlsForwardTask(
                # Browser fingerprint the worker should present.
                tls_type="chrome153",
                proxy=os.environ["EZCAPTCHA_PROXY"],
                method=TlsHttpMethod.GET,
                url="https://postman-echo.com/get",
            )
        )
        solution = solved.solution
        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Upstream:   HTTP {solution.code}")
        for name, value in solution.headers.items():
            print(f"Header:     {name}: {value}")
        print(f"Body:       {solution.body[:200]}")
        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
