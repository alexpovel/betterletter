from functools import reduce
import re
from typing import Iterable
from subalt import AlternativeSpelling, ISO6391Code
import logging
import operator as op

# from subalt.io import get_language_mappings

logger = logging.getLogger(__name__)


def cf_contains(element: str, string: str) -> bool:
    """Casefold (aka 'strong `lower()`') check if a substring is in a larger string.

    Args:
        element: The shorter string to be tested for containment in `string`.
        string: The larger string.

    Returns:
        Caseless test of whether the larger string contains the shorter string.
    """
    return element.casefold() in string.casefold()


def any_item_pattern(
    items: Iterable[str],
    flags: Iterable[re.RegexFlag],
) -> re.Pattern[str]:
    pattern = "(" + "|".join(set(items)) + ")"
    logger.debug(f"Returning regex pattern '{pattern}'")
    return re.compile(pattern=pattern, flags=reduce(op.__or__, flags))
