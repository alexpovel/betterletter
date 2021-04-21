#!/bin/env python3

"""Tool to replace alternative spellings of special characters
(e.g. German umlauts [ä, ö, ü] etc. [ß]) with the proper special characters.
For example, this problem occurs when no proper keyboard layout was available.

This tool is dictionary-based to check if replacements are valid words.
"""

import argparse
import json
import logging
import re
import sys
from functools import partial
from itertools import combinations
from pathlib import Path
from typing import Any, Generator, Iterable, Union

import pyperclip

# Because Windows is being stupid (defaults to cp1252), be explicit about encoding.
# Provide this globally so no spot is forgotten.
ENCODING = "utf8"
OPEN_WITH_ENCODING = partial(open, encoding=ENCODING)


def distinct_highest_element(iterable: Iterable, key=None) -> Union[Any, None]:
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
        key: The key to compare the iterable elements by. The key must return a sortable
            object (implementing at least `__lt__`). If None, element values are used
            directly.

    Returns:
        The distinctly single-highest element according to the key criterion if it
        exists, else None.
    """
    # If iterable is already sorted, Python's timsort will be very fast and little
    # superfluous work will have to be done.
    iterable = sorted(iterable, key=key)
    highest = iterable[-1]

    try:
        second_highest = iterable[-2]
    except IndexError:
        # Iterable of length one necessarily has one distinct element.
        return highest

    if key is None:
        if highest > second_highest:
            return highest
    else:
        if key(second_highest) < key(highest):
            return highest
    return None  # Fell through, explicit return for mypy


def read_linedelimited_file(file: Path) -> list[str]:
    with OPEN_WITH_ENCODING(file) as f:
        lines = f.read().splitlines()
    logging.debug(f"Fetched list containing {len(lines)} items from {file}")
    return lines


def write_linedelimited_file(file: Path, lines: list[str]):
    with OPEN_WITH_ENCODING(file, "w") as f:
        f.write("\n".join(lines))
    logging.debug(f"Wrote file containing {len(lines)} lines to {file}")


def filter_strs_by_letter_occurrence(
    strings: list[str], letter_filters: list[str]
) -> Generator[str, None, None]:
    """Filters a string list by only retaining elements that contain any filter letters.

    Comparison for filtering is caseless.

    Args:
        strings: List to filter.
        letter_filters: List of substrings that elements in the list-to-be-filtered
            must contain to be returned.

    Yields:
        All strings of the original list which contain any string in the filter list.
    """
    for string in strings:
        if any(cf_contains(ltr, string) for ltr in letter_filters):
            logging.debug(f"Yielding '{string}'.")
            yield string


def prepare_processed_dictionary(
    file: Path,
    fallback_file: Path,
    letter_filters: list[str] = None,
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
        logging.debug("Found pre-processed list.")
    except FileNotFoundError:
        logging.debug("No pre-processed list found, creating from original.")
        items = read_linedelimited_file(fallback_file)
        logging.debug(f"Fetched unprocessed list.")
        items = list(filter_strs_by_letter_occurrence(items, letter_filters))
        write_linedelimited_file(file, items)
    return items


def cf_contains(element: str, string: str) -> bool:
    """Casefold (aka 'strong `lower()`') check if a substring is in a larger string.

    Args:
        element: The shorter string to bed tested if contained in the larger string.
        string: The larger string.

    Returns:
        Caseless test of whether the larger string contains the shorter string.
    """
    return element.casefold() in string.casefold()


def combinations_any_length(iterable: Iterable[Any]) -> Any:
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
            logging.debug(f"Yielding combinatory element {item}.")
            yield item


def substitute_spans(
    string: str,
    spans: list[tuple[int, int]],
    spans_to_substitutions: dict[tuple[int, int], str],
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
    spans = sorted(spans, reverse=True)

    # Cannot use `str.translate`, because the translation of e.g. 'ue' to 'ü' would
    # be done on the entire string at once. There exists words for which this is not
    # suitable, e.g. 'Kuechenfeuer' -> 'Küchenfeuer': two 'ue', only one of which is
    # to be replaced.
    chars = list(string)  # Make mutable
    for span in spans:
        start, end = span
        substitution = spans_to_substitutions[span]
        # RHS has to be an iterable; since we join using the empty string later, no
        # further action is needed (like putting the substitution into a 1-element
        # tuple, which would keep the substitution string intact as one unit).
        chars[start:end] = substitution
    new_string = "".join(chars)
    logging.debug(f"Turned '{string}' into '{new_string}'.")
    return new_string


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


def parse(description: str, lang_choices: Iterable[str]) -> dict[str, Any]:
    """Prepares, runs and returns parsing of CLI arguments for the script."""
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "language",
        help="Text language to work with, in ISO 639-1 format.",
        choices=lang_choices,
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        help="Read from and write back to clipboard instead of STDIN/STDOUT.",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--force-all",
        help="Force substitutions and return the text version with the maximum number"
        " of substitutions, even if they are illegal words (useful for names).",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        help="Reverse mode, where all special characters are simply replaced"
        " by their alternative spellings",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Output detailed logging information.",
        action="store_true",
    )
    return vars(parser.parse_args())


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
            logging.debug(f"Item '{item}' is a word: {is_word}.")

            # Short-circuits, so saves processing if not a word in the first place
            is_special_word = is_word and any(
                cf_contains(special_alt_letter.pattern, item)
                for special_alt_letter in specials_to_regex_alts.values()
            )
            logging.debug(
                f"Item '{item}' contains potential specials: {is_special_word}."
            )

            if is_special_word:
                # Using spans (start, end pairs) as keys is valid, as they are unique.
                spans_to_substitutions = {}
                for special_letter, regex in specials_to_regex_alts.items():
                    for match in re.finditer(regex, item):
                        logging.debug(f"Found a {match=} in {item=}.")
                        if any(letter.isupper() for letter in match.group()):
                            # Treat e.g. 'Ae', 'AE', 'aE' as uppercase 'Ä'
                            special_letter = special_letter.upper()
                            logging.debug(f"Treating match as uppercase.")
                        else:
                            # Reset to lowercase, might still be uppercase from last
                            # iteration.
                            special_letter = special_letter.lower()
                            logging.debug(f"Treating match as lowercase.")
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
                logging.debug(f"All combinations to be tested are: {span_combinations}")
                logging.debug(
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
                logging.debug(f"Word candidates for replacement are: {candidates}")

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

                logging.debug(
                    f"Legal ({legal_source}) word candidates for replacement"
                    f" are: {legal_candidates}"
                )

                if legal_candidates:
                    # ONLY assign to `item` if legal candidates were found at all.
                    # If no legal candidates, all substitutions were wrong: do not
                    # reassign to `item`, so e.g. 'Abenteuer' stays 'Abenteuer'.
                    item = represent_strings(legal_candidates)
            logging.debug(f"Adding item '{item}' to processed line.")
            processed_line.append(item)
        new_line = "".join(processed_line)
        logging.debug(f"Processed line reads: '{new_line}'")
        processed_lines.append(new_line)
    return "\n".join(processed_lines)


def substitute_specials_with_alts(
    text: str,
    specials_to_alt_spellings: dict[str, str],
):
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


def backup_clipboard(text: str, file: Path):
    """Writes text content to file for backup purposes."""
    with OPEN_WITH_ENCODING(file, "w") as f:
        f.write(text)


def main():
    this_dir = Path(__file__).parent

    with OPEN_WITH_ENCODING(
        this_dir / Path("language_specials").with_suffix(".json")
    ) as f:
        language_specials: dict = json.load(f)

    args = parse(description=__doc__, lang_choices=language_specials)

    if args["debug"]:
        # Leave at default if no logging/debugging requested.
        logging.basicConfig(level="DEBUG")

    language: str = args["language"]

    base_dict_path = this_dir / Path("dicts")
    base_dict_file = Path(language).with_suffix(".dic")

    use_clipboard = args["clipboard"]

    if use_clipboard:
        text = pyperclip.paste()
        backup_clipboard(text, file=this_dir / Path(".clip.bak"))
        possible_empty_reason = "clipboard empty or binary (document, image, ...)"
    else:
        text = sys.stdin.read()
        possible_empty_reason = "STDIN was empty"

    if not text:
        logging.debug(f"No text received, exiting ({possible_empty_reason}).")
        return

    if args["reverse"]:
        new_text = substitute_specials_with_alts(text, language_specials[language])
    else:
        try:
            known_words = prepare_processed_dictionary(
                file=base_dict_path / Path("containing_specials_only") / base_dict_file,
                fallback_file=base_dict_path / base_dict_file,
                letter_filters=language_specials[language].keys(),
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Dictionary for {language=} not available (looked for '{e.filename}')"
            ) from e

        new_text = substitute_alts_with_specials(
            text=text,
            specials_to_alt_spellings=language_specials[language],
            known_words=known_words,
            force=args["force_all"],
        )

    if use_clipboard:
        pyperclip.copy(new_text)
    else:
        print(new_text)


if __name__ == "__main__":
    main()
