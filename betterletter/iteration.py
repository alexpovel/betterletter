import logging
from collections.abc import Callable
from itertools import combinations
from typing import Any, Iterable, Iterator, TypeVar

from betterletter import VERBOSE
from betterletter.strings import cf_contains

logger = logging.getLogger(__name__)


K = TypeVar("K")
V = TypeVar("V")


def subset(dictionary: dict[K, V], select: Iterable[K]) -> dict[K, V]:
    """Given a dictionary, returns it with only the selected keys present.

    Args:
        dictionary: The dictionary to be sliced down.
        select: Only these keys will be present in the returned dictionary.

    Returns:
        A new dictionary (a subset of the input one) with only selected keys present.
    """
    keys = set(dictionary.keys()) & set(select)
    return {k: dictionary[k] for k in keys}


def filter_strings(
    strings: Iterable[str], letter_filters: Iterable[str]
) -> Iterator[str]:
    """Filters strings by only retaining those which contain any filter letters.

    Comparison for filtering is caseless.

    Args:
        strings: Items to filter.
        letter_filters: List of substrings that elements in the list-to-be-filtered
            must contain to be returned.

    Yields:
        All strings of the original list which contain any string in the filter list.
    """
    for string in strings:
        if any(cf_contains(ltr, string) for ltr in letter_filters):
            logger.log(level=VERBOSE, msg=f"Yielding {string=}")  # Called very often
            yield string


T = TypeVar("T")


def all_lengths_combinations(iterable: Iterable[T]) -> Iterator[Iterable[T]]:
    """Yields all possible combinations of all possible lengths of an iterable.

    Adapted from https://stackoverflow.com/a/59009314/11477374. For an iterable
    `["A", "B", "C"]`, returns:

    ```
    [
        ['A'],
        ['B'],
        ['C'],
        ['A', 'B'],
        ['A', 'C'],
        ['B', 'C'],
        ['A', 'B', 'C'],
    ]
    ```

    by running `itertools.combinations` with all repeats of essentially
    `range(len(iterable))`.

    Args:
        iterable: The iterable to yield combinations of.

    Yields:
        A viable combination from the iterable.
    """
    for i, _ in enumerate(iterable, start=1):
        subcombinations = combinations(iterable, r=i)
        for item in subcombinations:
            logger.debug(f"Yielding combinatory element {item}.")
            yield item


def splitlines(string: str) -> list[str]:
    """Splits a newline-delimited string into a list of newline-delimited strings.

    Suitable for `difflib.Differ.compare`.
    """
    lines = string.splitlines(keepends=False)
    # `splitlines(keepends=True)` would work, but the last line is problematic. This
    # manual approach is more reliable.
    return [line + "\n" for line in lines]


def apply_to_all(dictionary: dict[Any, Any], func: Callable[[Any], Any]) -> Any:
    """Recursively apply a callable to all elements (keys + values) of a dictionary."""
    if isinstance(dictionary, dict):
        return {func(k): apply_to_all(v, func) for k, v in dictionary.items()}
    return func(dictionary)
