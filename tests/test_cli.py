import sys
from io import StringIO

import pyperclip
import pytest
from _pytest.capture import CaptureFixture

from betterletter.__main__ import main


@pytest.mark.parametrize(
    ["option"],
    [("-h",), ("--help",)],
)
def test_help_option(capsys: CaptureFixture, option: str):
    try:
        main([option])
    except SystemExit:
        pass

    output = capsys.readouterr().out

    assert "Tool to replace alternative spellings of native characters" in output


@pytest.mark.parametrize(
    ["language", "flags", "input", "expected"],
    [
        (
            "de",
            [""],
            "natuerlich",
            "natürlich",
        ),
        (
            "de",
            [""],
            "Hammer",
            "Hammer",
        ),
        (
            "de",
            ["--force"],
            "Kuechenfeuer",
            "Küchenfeür",
        ),
        (
            "de",
            ["--force"],
            "aeueoe",
            "äüö",
        ),
        (
            "de",
            ["--reverse"],
            "äüö",
            "aeueoe",
        ),
    ],
)
def test_common_cli(
    language: str, flags: list[str], input: str, expected: str, capsys: CaptureFixture
):
    sys.stdin = StringIO(input)
    try:
        # Crashes if flags is the empty string
        main(filter(None, [*flags, language]))
    except SystemExit:
        pass

    output = capsys.readouterr().out

    assert output == expected


@pytest.mark.parametrize(
    ["language", "flags", "input", "expected_stdout", "expected_stderr"],
    [
        (
            "de",
            ["--diff"],
            "natuerlich",
            "natürlich",
            "- natuerlich\n?    ^^\n+ natürlich\n?    ^\n",
        ),
        (
            "de",
            ["--diff"],
            "Hammer",
            "Hammer",
            "",
        ),
    ],
)
def test_diff_cli(
    language: str,
    flags: list[str],
    input: str,
    expected_stdout: str,
    expected_stderr: str,
    capsys: CaptureFixture,
):
    sys.stdin = StringIO(input)
    try:
        # Crashes if flags is the empty string
        main(filter(None, [*flags, language]))
    except SystemExit:
        pass

    output = capsys.readouterr()  # Only read once, else the output is empty

    assert output.out == expected_stdout
    assert output.err == expected_stderr


@pytest.mark.parametrize(
    ["language", "flags", "input", "expected"],
    [
        (
            "de",
            ["--clipboard"],
            "natuerlich",
            "natürlich",
        ),
        (
            "de",
            ["--clipboard"],
            "Hammer",
            "Hammer",
        ),
    ],
)
def test_clipboard_cli(
    language: str, flags: list[str], input: str, expected: str, capsys: CaptureFixture
):
    sys.stdin = StringIO(input)
    pyperclip.copy(input)
    try:
        # Crashes if flags is the empty string
        main(filter(None, [*flags, language]))
    except SystemExit:
        pass

    output = capsys.readouterr().out

    assert output == ""
    assert pyperclip.paste() == expected


@pytest.mark.skip(
    reason="Works but GUI opens and blocks; can't be bothered to mock this."
)
@pytest.mark.parametrize(
    ["language", "flags", "input", "expected"],
    [
        (
            "de",
            ["--gui"],
            "natuerlich",
            "natürlich",
        ),
    ],
)
def test_gui_cli(
    language: str, flags: list[str], input: str, expected: str, capsys: CaptureFixture
):
    sys.stdin = StringIO(input)
    try:
        # Crashes if flags is the empty string
        main(filter(None, [*flags, language]))
    except SystemExit:
        pass

    output = capsys.readouterr().out

    assert output == expected
