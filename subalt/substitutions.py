import logging
import re
from typing import Iterable

from subalt import Span
from subalt.itertools import combinations_any_length, distinct_highest_element
from subalt.reprs import represent_strings
from subalt.strtools import cf_contains

logger = logging.getLogger(__name__)


def substitute_spans(
    string: str,
    spans: Iterable[Span],
    spans_to_substitutions: dict[Span, str],
) -> str:
    """Substitutes elements at given positions in a string.

    Works from a list of spans (start, end index pairs) and a mapping of those pairs to
    elements to put in that span instead.

    Args:
        string: The original string to substitute elements in.
        spans: All spans in the string to substitute elements at.
        spans_to_substitutions: A mapping of spans to which element (e.g. a letter) to
            insert at that position, replacing the original.

    Returns:
        The original string with all characters at the given spans replaced according to
        the passed mapping.
    """
    # Reverse to work back-to-front, since during processing, indices
    # change as the string changes length. If starting from the back,
    # this issue is avoided; if starting from the front (non-reverse sorting),
    # later positions would get shifted.
    reverse_spans = sorted(spans, reverse=True)

    # Cannot use `str.translate`, because the translation of e.g. 'ue' to 'ü' would
    # be done on the entire string at once. There exists words for which this is not
    # suitable, e.g. 'Kuechenfeuer' -> 'Küchenfeuer': two 'ue', only one of which is
    # to be replaced.
    chars = list(string)  # Make mutable
    for span in reverse_spans:
        start, end = span
        substitution = spans_to_substitutions[span]
        # RHS has to be an iterable; since we join using the empty string later, no
        # further action is needed (like putting the substitution into a 1-element
        # tuple, which would keep the substitution string intact as one unit).
        chars[start:end] = substitution
    new_string = "".join(chars)
    logger.debug(f"Turned '{string}' into '{new_string}'.")
    return new_string


def substitute_alts_with_specials(
    text: str,
    specials_to_alt_spellings: dict[str, str],
    known_words: Iterable[str],
    force: bool,
) -> str:
    """Substitutes all alternative spellings with their proper version in a text.

    Args:
        text: The text in which alternative spellings are to be replaced.
        specials_to_alt_spellings: A mapping of special characters to their alternative
            spellings.
        known_words: A collection of known words against which potential candidates for
            replacement are compared (since by far not all replacements possible as
            per the mapping are also legal words).
        force: Whether to force substitutions. If yes, will return the version of the
            text with the most substitutions, regardless if these are legal words as per
            the list of known words. This is useful for names.

    Returns:
        The text with all alternative spellings of special characters in words replaced
        with (legal) versions with proper (UTF-8) characters.
    """
    word_regex = re.compile(r"(\w+)")
    assert (
        word_regex.groups == 1
    ), "A (single) capture group is required for re.split to work as intended here."

    # Enforce lowercase so we can rely on it later on. Do not use `casefold` on keys,
    # it lowercases too aggressively. E.g., it will turn 'ß' into 'ss', while keys
    # are supposed to be the special letters themselves.
    specials_to_regex_alts = {
        special_character.lower(): re.compile(alt_spelling.casefold(), re.IGNORECASE)
        for special_character, alt_spelling in specials_to_alt_spellings.items()
    }

    # A final, single newline won't survive the `splitlines` and `"\n".join` procedure
    # otherwise:
    newline = "\n"
    ending = newline if text[-1] == newline else ""

    lines = text.splitlines()
    processed_lines = []
    for line in lines:
        processed_line = []
        items = re.split(word_regex, line)  # Can be words and non-words ("!", "-", ...)
        for item in items:
            # After having split using regex, checking each item *again* here is
            # duplicated effort; however, this is very easy to do. The alternatives are
            # way harder to code, therefore easier to get wrong and harder to maintain.
            is_word = bool(re.match(word_regex, item))
            logger.debug(f"Item '{item}' is a word: {is_word}.")

            # Short-circuits, so saves processing if not a word in the first place
            is_special_word = is_word and any(
                cf_contains(special_alt_letter.pattern, item)
                for special_alt_letter in specials_to_regex_alts.values()
            )
            logger.debug(
                f"Item '{item}' contains potential specials: {is_special_word}."
            )

            if is_special_word:
                # Using spans (start, end pairs) as keys is valid, as they are unique.
                spans_to_substitutions = {}
                for special_letter, regex in specials_to_regex_alts.items():
                    for match in re.finditer(regex, item):
                        logger.debug(f"Found a {match=} in {item=}.")
                        if any(letter.isupper() for letter in match.group()):
                            # Treat e.g. 'Ae', 'AE', 'aE' as uppercase 'Ä'
                            special_letter = special_letter.upper()
                            logger.debug(f"Treating match as uppercase.")
                        else:
                            # Reset to lowercase, might still be uppercase from last
                            # iteration.
                            special_letter = special_letter.lower()
                            logger.debug(f"Treating match as lowercase.")
                        spans_to_substitutions[match.span()] = special_letter

                # For example, 'Abenteuerbuecher' contains two 'ue' elements, spanning
                # (6, 8) and (10, 12), respectively (as returned by `re.Match.span`).
                # We cannot (easily) determine algorithmically which spans would be the correct
                # ones to substitute at. Therefore, get all possible combinations; in
                # this example: the first, the second, and both (i.e., all combinations
                # of all possible lengths).
                span_combinations = list(
                    combinations_any_length(spans_to_substitutions)
                )
                logger.debug(f"All combinations to be tested are: {span_combinations}")
                logger.debug(
                    f"The underlying mapping for the tests is: {spans_to_substitutions}"
                )

                # Special words can be problematic, e.g. 'Abenteuer'. The algorithm
                # finds 'ue', but the resulting word 'Abenteür' is illegal. Therefore,
                # words with replacements are only *candidates* at first and have
                # to get checked against a dictionary.
                candidates = [
                    substitute_spans(item, spans, spans_to_substitutions)
                    for spans in span_combinations
                ]
                logger.debug(f"Word candidates for replacement are: {candidates}")

                if force:
                    # There exists only one word with "the most substitions"; all others
                    # have fewer. There is no ambiguity as long as the mapping of
                    # alternative spellings to originals is bijective, e.g. 'ue' only
                    # maps to 'ü' and vice versa. This is assumed to always be the case.
                    #
                    # Instead of this convoluted approach, we could also take the
                    # *shortest* candidate, since substitutions generally shorten the
                    # string (e.g. 'ue' -> 'ü'). The shortest string should also have
                    # the most substitutions. However, with Unicode, you never know
                    # how e.g. `len` will evaluate string lengths.
                    # Therefore, get the word that *actually*, provably, has the most
                    # substitutions (highest number of spans).
                    most_spans = distinct_highest_element(span_combinations, key=len)
                    assert most_spans

                    word_with_most_subs = substitute_spans(
                        item, most_spans, spans_to_substitutions
                    )

                    assert word_with_most_subs
                    legal_candidates = [word_with_most_subs]
                    legal_source = "forced"
                else:
                    # Check whether different, specific cases are legal words.
                    if item.islower():
                        # Lowercase stays lowercase:
                        # 'uebel' -> 'übel',
                        # but legally capitalized words are assumed to never occur
                        # lowercased ('aepfel' is never replaced, to e.g. 'Äpfel')
                        case_checks = [str.lower]
                    else:
                        # Includes all-caps, capitalized, title or mixed case.
                        #
                        # All-caps words ('AEPFEL') is to be replaced correctly
                        # ('ÄPFEL'); however, 'ÄPFEL' is not a legal word. So check
                        # the capitalized version ('Äpfel' -> legal) instead.
                        #
                        # Similarly for legally lowercased words, e.g. 'UEBEL':
                        # 'Übel' -> illegal, but 'übel' -> legal, so also check `lower`.
                        case_checks = [str.lower, str.capitalize]

                    candidates_to_cases = {
                        candidate: [case_check(candidate) for case_check in case_checks]
                        for candidate in candidates
                    }

                    legal_candidates = [
                        candidate
                        for candidate, cases in candidates_to_cases.items()
                        if any(case in known_words for case in cases)
                    ]
                    legal_source = "found in dictionary"

                logger.debug(
                    f"Legal ({legal_source}) word candidates for replacement"
                    f" are: {legal_candidates}"
                )

                if legal_candidates:
                    # ONLY assign to `item` if legal candidates were found at all.
                    # If no legal candidates, all substitutions were wrong: do not
                    # reassign to `item`, so e.g. 'Abenteuer' stays 'Abenteuer'.
                    item = represent_strings(legal_candidates)
            logger.debug(f"Adding item '{item}' to processed line.")
            processed_line.append(item)
        new_line = "".join(processed_line)
        logger.debug(f"Processed line reads: '{new_line}'")
        processed_lines.append(new_line)
    return "\n".join(processed_lines) + ending


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
