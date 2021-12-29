def cf_contains(element: str, string: str) -> bool:
    """Casefold (aka 'strong `lower()`') check if a substring is in a larger string.

    Args:
        element: The shorter string to bed tested if contained in the larger string.
        string: The larger string.

    Returns:
        Caseless test of whether the larger string contains the shorter string.
    """
    return element.casefold() in string.casefold()
