"""Extensions built on top of the task types.

The clients map one call to one task. An extension runs a whole workflow around
one or more task types instead — fetching pages, calling several steps, and
submitting the answer — so the caller only supplies the inputs a person would.
Workflow methods end in ``_workflow`` and are added to the clients; their inputs,
results, and errors live here.

Each extension needs an extra of its own, since a workflow usually needs
dependencies the task API does not:

=============  ===================================================================
Extra          Workflow
=============  ===================================================================
``datadome``   :meth:`AsyncEzCapSolverClient.solve_data_dome_workflow
               <ezcapsolver.AsyncEzCapSolverClient.solve_data_dome_workflow>`
=============  ===================================================================

Importing this module never needs an extra; calling a workflow does.
Extensions are new, and their API may still change.
"""

from ._datadome import DataDomeChallenge, DataDomeCookie
from ._errors import BrowserRequestError, DataDomeBlockedError, DataDomeError

__all__ = [
    "BrowserRequestError",
    "DataDomeBlockedError",
    "DataDomeChallenge",
    "DataDomeCookie",
    "DataDomeError",
]
