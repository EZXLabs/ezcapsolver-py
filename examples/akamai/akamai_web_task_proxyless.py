"""Run the Akamai Web sensor handshake.

Task type: ``AkamaiWEBTaskProxyless``

Akamai Web is a multi-round protocol, and it runs through the synchronous
endpoint. Each solved payload is posted back to ``v3Url``; the fresh ``_abck``
cookie from that response feeds the next round. Clearing the challenge takes up
to eight rounds.

Watch the two spellings: the worker returns ``encodedata`` and the next request
sends it as ``encode_data``. They genuinely differ on the wire, and the SDK
keeps the service's definitions rather than "fixing" them.

Docs: https://docs.ezxlabs.com/docs/captcha/api/akamai-web
"""

import asyncio

from ezcapsolver import AkamaiWebTask, AsyncEzCapSolverClient

MAX_ROUNDS = 8


async def main() -> None:
    # The first round sends no encoded state.
    encode_data = ""

    async with AsyncEzCapSolverClient() as client:
        for index in range(MAX_ROUNDS):
            solved = await client.sync_solve(
                AkamaiWebTask(
                    page_url="https://example.com",
                    # Most sites change this URL on every request, so read it
                    # from the page rather than hard-coding it.
                    v3_url="https://example.com/v3/...",
                    # Chrome only. `lang` has to match both the
                    # accept-language header sent to the site and the region
                    # the proxy exits from.
                    ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
                    lang="en-GB",
                    index=index,
                    abck="_abck_cookie_value",
                    bmsz="bm_sz_cookie_value",
                    # Read from network traffic, then base64-encoded. Only the
                    # first round sends it; later rounds send an empty string.
                    script_base64="base64_encoded_v3_script" if index == 0 else "",
                    encode_data=encode_data,
                )
            )

            solution = solved.solution
            print(f"Round {index}:    payload {len(solution.payload)} bytes")

            # POST `payload` to v3Url, read the new _abck cookie from that
            # response, and carry the encoded state into the next round.
            encode_data = solution.encodedata
            if not encode_data:
                print("Finished:   the flow returned no further state")
                break

        print(f"Balance:    {await client.get_balance()}")


if __name__ == "__main__":
    asyncio.run(main())
