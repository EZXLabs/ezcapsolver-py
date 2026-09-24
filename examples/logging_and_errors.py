"""Turn on SDK logging, and handle every error it can raise.

Everything the SDK raises derives from ``EzCaptchaError``, so catching that one
base class is enough to be safe. The specific types below are worth separating
because each calls for a different response.

The SDK attaches only a ``NullHandler``, so nothing is printed until you
configure logging yourself:

- ``INFO``  — task created, task solved, balance queried
- ``DEBUG`` — the request lifecycle and every polling attempt
- ``TRACE`` — full request and response bodies, with ``clientKey`` and ``proxy``
  replaced by ``[REDACTED]``. This sits one step below ``DEBUG`` because a
  DataDome or Akamai payload runs to megabytes.
"""

import asyncio
import logging

from ezcapsolver import (
    ApiError,
    AsyncEzCapSolverClient,
    EzCaptchaError,
    PollingExhaustedError,
    ReCaptchaV2Task,
    SolutionDecodeError,
    TransportError,
    WaitInterruptedError,
    task_id_of,
)

# Scope the level to this SDK. A global DEBUG would also turn on httpx's own
# output and bury these lines. Swap DEBUG for ezcapsolver.TRACE to add bodies.
logging.basicConfig(level=logging.INFO)
logging.getLogger("ezcapsolver").setLevel(logging.DEBUG)


async def main() -> None:
    async with AsyncEzCapSolverClient() as client:
        try:
            solved = await client.solve(
                ReCaptchaV2Task(
                    website_url="https://www.google.com/recaptcha/api2/demo",
                    website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
                )
            )
        except ApiError as exc:
            print(f"API error:  {exc.error_code} {exc.error_description}")
        except PollingExhaustedError as exc:
            # The budget ran out, but the task may still finish. The service
            # holds its result for five minutes after creation.
            print(f"Timed out:  gave up after {exc.attempts} attempts")
            recover(exc)
        except WaitInterruptedError as exc:
            # Same situation, different cause: the task was created and billed,
            # but the wait broke off. Note this catches network failures that
            # happen while polling, which is why it sits above the
            # TransportError clause below.
            print(f"Interrupted: {exc.__cause__}")
            recover(exc)
        except SolutionDecodeError as exc:
            # The worker returned a shape this release does not model. The raw
            # value is attached, so nothing is lost.
            print(f"Bad shape:  {exc.raw}")
        except TransportError as exc:
            # Network-level failure; the underlying httpx error is attached.
            print(f"Network:    {exc.cause}")
        except EzCaptchaError as exc:
            print(f"Other:      {exc}")
        else:
            print(f"Token:      {solved.solution.token[:64]}...")


def recover(exc: EzCaptchaError) -> None:
    """Report a task that was billed and can still be fetched.

    One question -- "is there a billed task to rescue?" -- regardless of which
    exception carries the id. Waiting again is free; creating a second task is
    not.
    """
    if task_id := task_id_of(exc):
        print(f"Recover:    wait_for_result({task_id}) -- do not create a second task")


if __name__ == "__main__":
    asyncio.run(main())
