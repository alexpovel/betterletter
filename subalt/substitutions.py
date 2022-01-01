import logging
import re
from typing import Iterator

from subalt import LanguageMapping, NativeSpelling, Span, WordLookup
from subalt.itertools import all_lengths_combinations, subset
from subalt.reprs import represent_strings

logger = logging.getLogger(__name__)


def substitute_spans(
    string: str,
    substitutions: dict[Span, NativeSpelling],
) -> str:
    """Substitutes elements at given positions in a string.

    We cannot simply use `str.translate`, because the translation of e.g. 'ue' to 'ü'
    would be done on the entire string at once. There exists words for which this is not
    suitable, e.g. 'Kuechenfeuer' -> 'Küchenfeuer': two 'ue', only one of which is to be
    replaced.

    Args:
        string: The original string to substitute elements in.
        substitutions: A mapping of spans to which element (e.g. a letter) to insert at
            that position, replacing the original.

    Returns:
        The original string with all characters at the given spans replaced according to
        the passed mapping.
    """
    # Reverse to work back-to-front, since during processing, indices change as the
    # string changes length. If starting from the back, this issue is avoided; if
    # starting from the front (non-reverse sorting), later positions would get shifted.
    reverse_spans = sorted(substitutions.keys(), reverse=True)

    chars = list(string)  # Make mutable
    for span in reverse_spans:
        chars[slice(*span)] = substitutions[span]
    new_string = "".join(chars)
    logger.debug(f"Turned '{string}' into '{new_string}'.")
    return new_string


def forward(
    text: str,
    language_mapping: LanguageMapping,
    known_words: WordLookup,
    force: bool,
) -> Iterator[str]:
    """Substitutes all alternative spellings with their native versions in a text.

    Special words can be problematic, e.g. 'Abenteuer'. The algorithm finds 'ue', but a
    possible substitution of 'Abenteür' is illegal. Therefore, words with replacements
    are only *candidates* at first and have to get checked against a dictionary.

    Further, for example, 'Abenteuerbuecher' contains two 'ue' elements, spanning (6, 8)
    and (10, 12), respectively (as returned by `re.Match.span`). We cannot (easily)
    determine algorithmically which spans would be the correct ones to substitute at.
    Therefore, get all possible combinations; in this example: the first, the second,
    and both (i.e., all combinations of all possible lengths).

    Args:
        text: The text in which alternative spellings are to be replaced.
        language_mapping: A mapping of special characters to their alternative
            spellings.
        known_words: A collection of known words against which potential candidates for
            replacement are compared (since by far not all replacements possible as
            per the mapping are also legal words).
        force: Whether to force substitutions. If yes, will return the version of the
            text with the most substitutions, regardless if these are legal words as per
            the list of known words. This is useful for names.
            It is assumed that the *shortest* possible word is the one with the most
            substitutions, since substitutions generally shorten words (like ue -> ü).

    Returns:
        The text with all alternative spellings of special characters in words replaced
        with (legal) versions with proper (UTF-8) characters.
    """
    native_to_alternative_regexes = {
        native: re.compile(alternative, re.IGNORECASE)
        for native, alternative in language_mapping.items()
    }

    items = re.split(r"(\w+)", text)  # Can be words and non-words ("!", "-", ...)

    for item in items:
        logger.debug(f"Processing {item=}")

        # Using spans as keys is valid, as they are unique and immutable.
        substitutions: dict[Span, NativeSpelling] = {}

        for native, alt_regex in native_to_alternative_regexes.items():
            for match in re.finditer(alt_regex, item):
                logger.debug(f"Found a {match=} in {item=}.")
                if any(letter.isupper() for letter in match.group()):
                    # Treat e.g. 'Ae', 'AE', 'aE' as uppercase 'Ä'
                    native = native.upper()
                    logger.debug(f"Treating {match=} as uppercase.")
                else:
                    # Reset to lowercase: might still be uppercase from last iteration.
                    native = native.lower()
                    logger.debug(f"Treating {match=} as lowercase.")
                substitutions[match.span()] = native

        if not substitutions:
            logger.debug(f"No substitutions to be made for {item=}, skipping.")
            yield item
            continue

        all_spans = list(all_lengths_combinations(substitutions))
        all_substitutions = [subset(substitutions, span) for span in all_spans]
        logger.debug(f"Will test the following substitution sets: {all_substitutions}")

        candidates = [
            substitute_spans(item, substitution) for substitution in all_substitutions
        ]
        logger.debug(f"Word candidates for replacement are: {candidates}")

        if force:
            # There exists only one word with "the most substitutions"; all others have
            # fewer. There is no ambiguity as long as the mapping of alternative
            # spellings to originals is bijective, e.g. 'ue' only maps to 'ü' and vice
            # versa. This is assumed to always be the case.
            legal_candidates = [sorted(candidates, key=len)[0]]
            legal_source = "forced"
        else:
            # Check whether different, specific cases are legal words.
            if item.islower():
                # Lowercase stays lowercase: 'uebel' -> 'übel', but legally capitalized
                # words are assumed to never occur lowercased ('aepfel' is never
                # replaced, to e.g. 'Äpfel')
                case_checks = [str.lower]
            else:
                # Includes all-caps, capitalized, title or mixed case. All-caps words
                # ('AEPFEL') is to be replaced correctly ('ÄPFEL'); however, 'ÄPFEL'
                # won't be part of a lookup dictionary. So check the capitalized version
                # ('Äpfel' -> legal) instead. Similarly for legally lowercased words,
                # e.g. 'UEBEL': 'Übel' -> illegal, but 'übel' -> legal, so also check
                # `lower`.
                case_checks = [str.lower, str.capitalize]

            candidate_cases = {
                candidate: [case_check(candidate) for case_check in case_checks]
                for candidate in candidates
            }

            legal_candidates = [
                candidate
                for candidate, cases in candidate_cases.items()
                if any(case in known_words for case in cases)
            ]
            legal_source = "found in dictionary"

        logger.debug(
            f"Legal ({legal_source}) word candidates for replacement"
            f" are: {legal_candidates}"
        )

        n_candidates = len(legal_candidates)
        if n_candidates == 1:
            item = legal_candidates[0]
        elif n_candidates > 1:
            item = represent_strings(legal_candidates)
        else:
            logger.warning(
                f"Substitutions took place but {item=} has no legal candidates."
            )

        logger.debug(f"Yielding fully processed {item=}")
        yield item


def substitute_specials_with_alts(
    text: str,
    specials_to_alt_spellings: dict[str, str],
) -> str:
    """Replaces all special characters in a text with their alternative spellings.

    No dictionary check is performed, since this operation is much simpler than its
    reverse.

    Args:
        text: The string in which to do the substitutions.
        specials_to_alt_spellings: A mapping of special characters to their alternative
            spellings (like 'ä' -> 'ae'). Can be lower- or uppercase.

    Returns:
        The text with replacements made, in the correct case.
    """
    table = {}
    for special_char, alt_spelling in specials_to_alt_spellings.items():
        # Create a table mapping *both* lower- and uppercase of the special character
        # to an appropriate replacement.
        lower, upper = special_char.lower(), special_char.upper()
        if len(lower) == 1:
            # Translation table keys have to be of length one. However, special chars
            # like can run into: 'ß'.lower() -> 'ss', which is not a valid key.
            table[lower] = alt_spelling.lower()
        if len(upper) == 1:
            # I am unaware of any special chars where the upper() method returns a
            # string longer 1, but just in case, it is included here.
            #
            # `str.capitalize()` turns e.g. 'ae' into 'Ae', the appropriate
            # representation for an uppercase 'Ä' letter (as opposed to 'AE' from
            # `str.upper()`).
            table[upper] = alt_spelling.capitalize()
    # str.translate requires 'ordinals: string' mappings, not just 'string: string'
    trans = str.maketrans(table)
    return text.translate(trans)
