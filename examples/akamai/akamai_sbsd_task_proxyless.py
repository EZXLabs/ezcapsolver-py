"""Generate an Akamai SBSD payload.

Task type: ``AkamaiSBSDTaskProxyless``

SBSD is a single round and runs through the synchronous endpoint, so the
solution comes back inline and ``Solved.task_id`` is ``None``.

Docs: https://docs.ezxlabs.com/docs/captcha/api/akamai-sbsd
"""

import asyncio

from ezcapsolver import AkamaiSBSDTask, AsyncEzCapSolverClient

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        # Every value below is collected from the protected page before
        # solving: `sbsd_url` comes from its <script src="/sbsd/...?v=..."> tag,
        # `script_base64` is that script base64-encoded, and `bm_so` is the
        # bm_so cookie, falling back to sbsd_o.
        solved = await client.sync_solve(
            AkamaiSBSDTask(
                page_url="https://example.com",
                sbsd_url="https://example.com/sbsd/xxxxx?v=xxx",
                bm_so="bm_so_cookie_value",
                ua=UA,
                lang="en-US",
                script_base64="base64_encoded_sbsd_script",
            )
        )

        print(f"Request ID: {solved.request_id or '-'}")
        print(f"Payload:    {solved.solution.payload[:64]}...")
        print(f"bm_lso_time:{solved.solution.bm_lso_time or '-'}")

        # Decode the payload from base64, then POST it as {"body": <decoded>}
        # to the SBSD endpoint — that is `sbsd_url` without its query string.
        # Keep the cookies that response sets for every subsequent request.

        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
