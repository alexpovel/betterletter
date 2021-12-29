def represent_strings(
    strings: list[str],
    separator: str = "|",
    delimiters: tuple[str, str] = ("[", "]"),
) -> str:
    """Represents strings as one by joining them, leaving single strings as-is.

    Args:
        strings: The strings to be joined into one unified, larger string.
        separator: The separator to insert between joined substrings.
        delimiters: The two strings to be inserted left and right of the joined string.

    Returns:
        The strings joined into one larger, processed one or the untouched string if
            only one found.
    """
    n_required_delimiters = 2
    n_passed_delimiters = len(delimiters)
    if n_passed_delimiters != n_required_delimiters:
        raise ValueError(
            f"Passed {n_passed_delimiters} delimiters when {n_required_delimiters}"
            " required (left, right)."
        )

    multiple_strings = int(len(strings) > 1)
    processed_delimiters = tuple(
        delimiter * multiple_strings for delimiter in delimiters
    )

    if len(strings) == 1:
        # These assertions resulted from what used to be a comment; it is a very wordy
        # and duplicated effort to assert correctness of the above trickery instead of
        # using a more straightforward approach. This is just for fun.
        assert not any(processed_delimiters)
        assert separator.join(strings) == strings[0]

    return processed_delimiters[0] + separator.join(strings) + processed_delimiters[-1]
