#!/bin/env python3

"""Tool to replace alternative spellings of special characters
(e.g. German umlauts [ä, ö, ü] etc. [ß]) with the proper special characters.
For example, this problem occurs when no proper keyboard layout was available.

This program is dictionary-based to check if replacements are valid words.
"""

import argparse
import json
import logging
import re
import sys
import tkinter as tk
from difflib import Differ
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

import pyperclip

from subalt import _PACKAGE_ROOT
from subalt.io import (backup_clipboard, open_with_encoding,
                       prepare_processed_dictionary)
from subalt.itertools import splitlines
from subalt.substitutions import (substitute_alts_with_specials,
                                  substitute_specials_with_alts)

logger = logging.getLogger(__name__)


def parse(description: str, lang_choices: Iterable[str]) -> dict[str, bool | str]:
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
        " by their alternative spellings.",
        action="store_true",
    )
    parser.add_argument(
        "-g",
        "--gui",
        help="Stop and open a GUI prompt for confirmation before finishing.",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--diff",
        help="Print a diff view of the substitutions to stderr.",
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="Output detailed logging information.",
        action="store_true",
    )
    return vars(parser.parse_args())


def main() -> None:
    resources_dir = _PACKAGE_ROOT / "resources"

    with open_with_encoding(
        (resources_dir / "languages").with_suffix(".json")
    ) as f:
        language_specials: dict[str, dict[str, str]] = json.load(f)

    args = parse(description=__doc__, lang_choices=language_specials)

    if args["debug"]:
        # Leave at default if no logging/debugging requested.
        logging.basicConfig(level="DEBUG")

    language = str(args["language"])

    base_dict_path = resources_dir / Path("dicts")
    base_dict_file = Path(language).with_suffix(".txt")

    use_clipboard = args["clipboard"]

    if use_clipboard:
        in_text = pyperclip.paste()
        backup_clipboard(in_text, file=_PACKAGE_ROOT / Path(".clip.bak"))
        possible_empty_reason = "clipboard empty or binary (document, image, ...)"
    else:
        in_text = sys.stdin.read()
        possible_empty_reason = "STDIN was empty"

    if not in_text.strip():
        logger.warning(f"Empty input received ({possible_empty_reason}).")

    if args["reverse"]:
        out_text = substitute_specials_with_alts(
            in_text, language_specials[language]
        )
    else:
        try:
            known_words = prepare_processed_dictionary(
                file=base_dict_path / Path("filtered") / base_dict_file,
                fallback_file=base_dict_path / base_dict_file,
                letter_filters=language_specials[language].keys(),
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Dictionary for {language=} not available (looked for '{e.filename}')"
            ) from e

        out_text = substitute_alts_with_specials(
            text=in_text,
            specials_to_alt_spellings=language_specials[language],
            known_words=known_words,
            force=bool(args["force_all"]),
        )

    if args["diff"] or args["gui"]:
        raw_diff = Differ().compare(splitlines(in_text), splitlines(out_text))
        # See https://docs.python.org/3/library/difflib.html#difflib.Differ :
        # a 'line common to both sequences' starts with two spaces -> we don't care
        diff = "".join(line for line in raw_diff if not re.match("^  ", line))

    if args["gui"]:
        root = tk.Tk()

        usage = tk.Label(
            text="ENTER to confirm, ESC to abort.",
            font="TkFixedFont",
            fg="white",
            bg="SlateGray",
        )
        usage.pack()

        difflabel = tk.Label(text=diff, font="TkFixedFont", justify="left")
        difflabel.pack()

        root.title("Diff view")

        # https://mypy.readthedocs.io/en/latest/runtime_troubles.html#using-classes-that-are-generic-in-stubs-but-not-at-runtime
        if TYPE_CHECKING:
            Event = tk.Event[Any]
        else:
            Event = tk.Event

        def destroy(event: Event) -> None:
            """Destroys a window and ends mainloop."""
            root.destroy()

        def terminate(event: Event) -> None:
            destroy(event)
            sys.exit(1)

        root.bind("<Return>", destroy)  # Enter key
        root.bind("<Escape>", terminate)

        root.mainloop()

    if args["diff"]:
        sys.stderr.write(diff)

    if use_clipboard:
        pyperclip.copy(out_text)
    else:
        sys.stdout.write(out_text)


if __name__ == "__main__":
    main()