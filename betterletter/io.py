import json
import logging
from functools import partial
from pathlib import Path
from typing import Iterable, Optional

from betterletter import _RESOURCES, ISO6391Code, LanguageMapping, WordLookup
from betterletter.iteration import apply_to_all, filter_strings

logger = logging.getLogger(__name__)


# Be explicit about encoding, since Windows might default to something other than UTF8.
# Provide this globally so no spot is forgotten.
_ENCODING = "utf8"
open_with_encoding = partial(open, encoding=_ENCODING)


def read(file: Path) -> list[str]:
    with open_with_encoding(file) as f:
        lines = f.read().splitlines()
    logger.debug(f"Fetched list containing {len(lines)} items from {file}")
    return lines


def write(file: Path, lines: list[str]) -> None:
    with open_with_encoding(file, "w") as f:
        f.write("\n".join(lines))
    logger.debug(f"Wrote file containing {len(lines)} lines to {file}")


def get_dictionary(
    language: ISO6391Code,
    letter_filters: Optional[Iterable[str]] = None,
) -> WordLookup:
    """Provides words from a pre-processed file or additionally creates it if not found.

    Args:
        file: The pre-processed, line-separated file of items.
        fallback_file: File to use and create new file from if main file not found.
        letter_filters: List of substrings items in the fallback file must contain to
            be returned and written to a new, processed file.

    Returns:
        Collection of words from the read pre-preprocessed file.
    """
    base_path = _RESOURCES / Path("dicts")
    base_file = Path(language).with_suffix(".txt")
    file = base_path / Path("filtered") / base_file

    if letter_filters is None:
        letter_filters = []
    try:
        items = read(file)
        logger.debug("Found pre-processed list.")
    except FileNotFoundError:
        logger.warning("No pre-processed dictionary found, creating from original.")
        logger.warning("This only needs to be done once after package installation.")
        fallback = base_path / base_file
        items = read(fallback)
        logger.debug(f"Fetched unprocessed list.")
        items = list(filter_strings(items, letter_filters))
        write(file, items)
    return set(items)


def backup_clipboard(text: str, file: Path) -> None:
    """Writes text content to file for backup purposes."""
    with open_with_encoding(file, "w") as f:
        f.write(text)


def get_language_mappings() -> dict[ISO6391Code, LanguageMapping]:
    with open_with_encoding((_RESOURCES / "languages").with_suffix(".json")) as f:
        # Enforce lowercase so we can rely on it later on. Do not use `casefold` on keys,
        # it lowercases too aggressively. E.g., it will turn 'ß' into 'ss', while keys
        # are supposed to be the native letters themselves.
        language_mappings: dict[ISO6391Code, LanguageMapping] = apply_to_all(
            json.load(f), str.lower
        )
    return language_mappings
