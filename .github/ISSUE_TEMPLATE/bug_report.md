---
name: Bug Report
about: Report a bug to help us improve
title: "[Bug] "
labels: bug
---

## Problem Description

<!-- Clearly and concisely describe the bug -->

## Steps to Reproduce

1.
2.
3.

## Expected Behavior

<!-- Describe what you expected to happen -->

## Environment Information

- OS:
- Python version:
- `ezcapsolver-py` version:
- Task type involved:

## Additional Information

<!--
Logs, tracebacks or other information helpful for locating the issue.

Enable debug logging to capture the request and response; the SDK redacts
clientKey and proxy automatically:

    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("ezcapsolver").setLevel(logging.DEBUG)

If a solution failed to decode, SolutionDecodeError.raw holds the exact shape
the worker returned — that is the single most useful thing to attach.
-->
