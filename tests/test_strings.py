from contextlib import nullcontext

import pytest

from betterletter.strings import cf_contains

# Placeholder for parameters that do not matter in that instance of a test, e.g.
# when an exception is raised, so no result is produced.
VOID = None


@pytest.mark.parametrize(
    ["element", "string", "result", "expectation"],
    [
        # Simple strings:
        ("", "", True, nullcontext()),
        ("", "a", True, nullcontext()),
        ("a", "", False, nullcontext()),
        ("a", "a", True, nullcontext()),
        ("aa", "a", False, nullcontext()),
        ("a", "aa", True, nullcontext()),
        #
        # Invalids
        (1, "", VOID, pytest.raises(AttributeError)),
        (1, 1, VOID, pytest.raises(AttributeError)),
        (None, None, VOID, pytest.raises(AttributeError)),
        #
        # Unicode strings
        ("ß", "ß", True, nullcontext()),
        ("ss", "ß", True, nullcontext()),
        ("ß", "ss", True, nullcontext()),
        ("SS", "ß", True, nullcontext()),
        ("ß", "SS", True, nullcontext()),
        ("SS", "SS", True, nullcontext()),
        ("ss", "ss", True, nullcontext()),
        ("ẞ", "ss", True, nullcontext()),  # Uppercase ß
        ("ẞ", "SS", True, nullcontext()),  # Uppercase ß
        ("ẞ", "ß", True, nullcontext()),  # Uppercase ß
        ("ẞ", "ẞ", True, nullcontext()),  # Uppercase ß
        ("ss", "ẞ", True, nullcontext()),  # Uppercase ß
        ("SS", "ẞ", True, nullcontext()),  # Uppercase ß
        ("ß", "ẞ", True, nullcontext()),  # Uppercase ß
        ("ẞ", "ẞ", True, nullcontext()),  # Uppercase ß
        #
        ("Bussgeld", "BUẞGELD IST DOOF!", True, nullcontext()),
        ("Bußgeld", "BUẞGELD IST DOOF!", True, nullcontext()),
        ("BUSSGELD", "BUẞGELD IST DOOF!", True, nullcontext()),
        ("BUẞGELD", "BUẞGELD IST DOOF!", True, nullcontext()),
    ],
)
def test_cf_contains(element, string, result, expectation):
    with expectation:
        assert cf_contains(element, string) == result
