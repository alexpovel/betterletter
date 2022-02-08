import json
import logging
from functools import cache, partial
from pathlib import Path

from betterletter import _RESOURCES, ISO6391Code, LanguageMapping, WordLookup
from betterletter.iteration import apply_to_all

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


@cache  # Somewhat heavy io, caching helps a ton for tests etc.
def get_dictionary(language: ISO6391Code) -> WordLookup:
    """Provides the word set from a provided dictionary file.

    Args:
        language: The dictionary of this language will be loaded.

    Returns:
        Set of words from the file.
    """
    path = _RESOURCES / Path("dicts")
    file = Path(language).with_suffix(".txt")

    items = read(path / file)
    logger.debug("Fetched word list.")
    return set(items)


@cache
def get_language_mappings() -> dict[ISO6391Code, LanguageMapping]:
    with open_with_encoding((_RESOURCES / "languages").with_suffix(".json")) as f:
        # Enforce lowercase so we can rely on it later on. Do not use `casefold` on keys,
        # it lowercases too aggressively. E.g., it will turn 'ß' into 'ss', while keys
        # are supposed to be the native letters themselves.
        language_mappings: dict[ISO6391Code, LanguageMapping] = apply_to_all(
            json.load(f), str.lower
        )
    return language_mappings
