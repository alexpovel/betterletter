"""File to configure pytest, e.g. to implement hooks.

See also: https://stackoverflow.com/q/34466027/11477374
List of hooks: https://pytest.org/en/latest/reference.html#hook-reference
"""

from contextlib import nullcontext


def pytest_make_parametrize_id(config, val, argname):
    """Provide IDs aka names for test cases.

    pytest generates automatic IDs. Using this function, they can be altered to
    whatever more legible representation, see
    https://doc.pytest.org/en/latest/example/parametrize.html#different-options-for-test-ids.

    Implementing this function in a specific file using a specific name will hook it
    into pytest and use it for *all* ID generation automatically, so no need to specify
    `ids=<func>` all the time.
    Demo: https://raphael.codes/blog/ids-for-pytest-fixtures-and-parametrize/
    """
    if isinstance(val, nullcontext):
        return "NoError"
    elif hasattr(val, "expected_exception"):
        # Decided against try/except and for hasattr for a unified approach.
        # Get which exception was passed in pytest.raises(<Exception>):
        return str(val.expected_exception)
    else:
        # See if object has __str__ implemented
        try:
            return str(val)
        except:
            pass
