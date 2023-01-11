#!/bin/env python3

"""Tool to replace alternative spellings of native characters
(e.g. German umlauts [ä, ö, ü] etc. [ß]) with the proper native characters.
For example, this problem occurs when no proper keyboard layout was available.

This program is dictionary-based to check if replacements are valid words.

By default, reads from STDIN and writes to STDOUT.
"""

import argparse
import logging
import re
import sys
from typing import TYPE_CHECKING, Any, Iterable, Optional, Union

try:
    import tkinter as tk

    _TKINTER_AVAILABLE = True
except ImportError:
    _TKINTER_AVAILABLE = False

try:
    import pyperclip

    _PYPERCLIP_AVAILABLE = True
except ImportError:
    _PYPERCLIP_AVAILABLE = False

from betterletter import substituters
from betterletter.io import get_dictionary, get_language_mappings
from betterletter.iteration import splitlines

logger = logging.getLogger(__name__)


def parse(
    args: Optional[list[str]], description: str, lang_choices: Iterable[str]
) -> dict[str, Union[bool, str]]:
    """Prepares, runs and returns parsing of CLI arguments for the script."""
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "language",
        help="Text language to work with, in ISO 639-1 format.",
        choices=lang_choices,
    )

    kwargs: dict[str, Union[str, bool]]  # Satisfy mypy
    if _PYPERCLIP_AVAILABLE:
        kwargs = {
            "help": "Read from and write back to clipboard instead of STDIN/STDOUT.",
            "action": "store_true",
        }
    else:
        kwargs = {
            "help": "OPTION IGNORED (not available): package 'pyperclip' couldn't be imported.",
            # False in all cases:
            "action": "store_false",
            "default": False,
        }

    parser.add_argument("-c", "--clipboard", **kwargs)  # type: ignore

    parser.add_argument(
        "-f",
        "--force",
        help="Force substitutions and return the text version with the maximum number"
        " of substitutions, even if they are illegal words (useful for names).",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        help="Reverse mode, where all native characters are simply replaced"
        " by their alternative spellings.",
        action="store_true",
    )

    if _TKINTER_AVAILABLE:
        kwargs = {
            "help": "Stop and open a GUI prompt for confirmation before finishing.",
            "action": "store_true",
        }
    else:
        kwargs = {
            "help": "OPTION IGNORED (not available): package 'tkinter' couldn't be imported.",
            # False in all cases:
            "action": "store_false",
            "default": False,
        }

    parser.add_argument("-g", "--gui", **kwargs)  # type: ignore

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
    return vars(parser.parse_args(args=args))


def main(raw_args: Optional[list[str]] = None) -> None:
    language_mappings = get_language_mappings()

    args = parse(
        args=raw_args, description=__doc__, lang_choices=language_mappings.keys()
    )

    if args["debug"]:
        # Leave at default if no logging/debugging requested.
        logging.basicConfig(level="DEBUG")

    language = str(args["language"])
    language_mapping = language_mappings[language]

    use_clipboard = args["clipboard"]

    if use_clipboard:
        in_text = pyperclip.paste()
        possible_empty_reason = "clipboard empty or binary (document, image, ...)"
    else:
        in_text = sys.stdin.read()
        possible_empty_reason = "STDIN was empty"

    if not in_text.strip():
        logger.warning(f"Empty input received ({possible_empty_reason}).")

    if args["reverse"]:
        out_text = substituters.backward(in_text, language_mapping)
    else:
        try:
            known_words = get_dictionary(language=language)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Dictionary for {language=} not available (looked for '{e.filename}')"
            ) from e

        out_text = "".join(
            substituters.forward(
                text=in_text,
                language_mapping=language_mapping,
                known_words=known_words,
                force=bool(args["force"]),
            )
        )

    if args["diff"] or args["gui"]:
        from difflib import Differ

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
