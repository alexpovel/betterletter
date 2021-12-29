import logging
from functools import partial
from pathlib import Path
from typing import Iterable, Optional

from subalt.itertools import filter_strs_by_letter_occurrence

logger = logging.getLogger(__name__)


# Be explicit about encoding, since Windows might default to something other than UTF8.
# Provide this globally so no spot is forgotten.
_ENCODING = "utf8"
open_with_encoding = partial(open, encoding=_ENCODING)


def read_linedelimited_file(file: Path) -> list[str]:
    with open_with_encoding(file) as f:
        lines = f.read().splitlines()
    logger.debug(f"Fetched list containing {len(lines)} items from {file}")
    return lines


def write_linedelimited_file(file: Path, lines: list[str]) -> None:
    with open_with_encoding(file, "w") as f:
        f.write("\n".join(lines))
    logger.debug(f"Wrote file containing {len(lines)} lines to {file}")


def prepare_processed_dictionary(
    file: Path,
    fallback_file: Path,
    letter_filters: Optional[Iterable[str]] = None,
) -> list[str]:
    """Provides words from a pre-processed file or additionally creates it if not found.

    Args:
        file: The pre-processed, line-separated file of items.
        fallback_file: File to use and create new file from if main file not found.
        letter_filters: List of substrings items in the fallback file must contain to
            be returned and written to a new, processed file.
    Returns:
        List of words from the read pre-preprocessed file.
    """
    if letter_filters is None:
        letter_filters = []
    try:
        items = read_linedelimited_file(file)
        logger.debug("Found pre-processed list.")
    except FileNotFoundError:
        logger.debug("No pre-processed list found, creating from original.")
        items = read_linedelimited_file(fallback_file)
        logger.debug(f"Fetched unprocessed list.")
        items = list(filter_strs_by_letter_occurrence(items, letter_filters))
        write_linedelimited_file(file, items)
    return items


def backup_clipboard(text: str, file: Path) -> None:
    """Writes text content to file for backup purposes."""
    with open_with_encoding(file, "w") as f:
        f.write(text)
