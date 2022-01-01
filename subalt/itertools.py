import logging
from collections.abc import Callable
from itertools import combinations
from typing import Any, Iterable, Iterator, Optional, TypeVar

# from subalt import C
from subalt.strtools import cf_contains

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


def filter_strs(strings: Iterable[str], letter_filters: Iterable[str]) -> Iterator[str]:
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
            logger.debug(f"Yielding '{string}'.")
            yield string


def distinct_greatest_element(
    iterable: Iterable[Any], key: Optional[Callable[[Any], Any]] = None
) -> Optional[Any]:
    """Gets one element if it compares greater than all others according to some key.

    For example, using `key=len`, the list `[(1, 2), (3, 4)]` has two tuples of the
    same length: no value (2 and 2) compares greater than any other. The iterable
    `[(1, 2), (3, 4), (5, 6, 7)]` has an element of length 3, which is greater than
    the second-highest (here: longest, due to the `key`), returning that element.

    If `key` is `None`, the values of elements are compared directly, instead of some
    property (`key`) of those elements. As such, `[1, 1]` fails, but `[1, 1, 2]` etc.
    returns the found element, `2`.

    Args:
        iterable: The iterable to be examined.
        key: The key to compare the iterable elements by. If None, element values are
            used directly.

    Returns:
        The distinctly single-highest element according to the key criterion if it
        exists, else None.
    """
    # If iterable is already sorted, Python's timsort will be very fast and little
    # superfluous work will have to be done.
    sorted_iterable = sorted(iterable, key=key)
    highest = sorted_iterable[-1]

    try:
        second_highest = sorted_iterable[-2]
    except IndexError:
        # Iterable of length one necessarily has one distinct element.
        return highest

    if key is None:
        identity = lambda _: _
        key = identity

    if key(highest) > key(second_highest):
        return highest

    return None  # Fell through, explicit return for mypy


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
    if type(dictionary) != dict:
        return func(dictionary)
    return {func(k): apply_to_all(v, func) for k, v in dictionary.items()}
