from typing import Iterable


def represent_strings(
    strings: Iterable[str],
    separator: str = "|",
    delimiters: tuple[str, str] = ("[[[", "]]]"),
) -> str:
    """Represents strings as one by joining them.

    Args:
        strings: The strings to be joined into one unified, larger string.
        separator: The separator to insert between joined substrings.
        delimiters: The two strings to be inserted left and right of the joined string.

    Returns:
        The strings joined into a larger, processed one.
    """
    return delimiters[0] + separator.join(strings) + delimiters[-1]
