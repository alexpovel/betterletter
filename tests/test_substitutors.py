from contextlib import nullcontext

import pytest
from betterletter.io import get_dictionary, get_language_mappings
from betterletter.substituters import _substitute_spans, backward, forward


@pytest.mark.parametrize(
    ["string", "substitutions", "result", "expectation"],
    [
        ("A", {(0, 1): "B"}, "B", nullcontext()),
        ("Apple", {(0, 1): "B"}, "Bpple", nullcontext()),
        ("Apple", {(0, 1): "Ba"}, "Bapple", nullcontext()),
        #
        ("Apple", {(0, 1): "B", (2, 3): "C"}, "BpCle", nullcontext()),
        #
        (0 * " ", {(0, 1): "A"}, "A", nullcontext()),
        (1 * " ", {(0, 1): "A"}, "A", nullcontext()),
        (2 * " ", {(0, 1): "A"}, "A" + " ", nullcontext()),
        #
        ("Apple", {(0, 0): ""}, "Apple", nullcontext()),
        ("Apple", {(0, 3): ""}, "le", nullcontext()),
        ("Apple", {(0, 99): ""}, "", nullcontext()),
        #
        (
            "Know the way",
            {(0, 4): "", (9, 12): ""},
            " the ",
            nullcontext(),
        ),
        (
            "extra",
            {(0, 1): "", (1, 2): "", (2, 3): "", (3, 4): "", (4, 5): ""},
            "",
            nullcontext(),
        ),
        (
            "extra",
            {(0, 1): "H", (1, 2): "e", (2, 3): "l", (3, 4): "l", (4, 5): "o"},
            "Hello",
            nullcontext(),
        ),
        (
            "extra",
            {(0, 1): "Hello", (1, 2): "", (2, 3): "", (3, 4): "", (4, 5): ""},
            "Hello",
            nullcontext(),
        ),
        #
        (
            "Schmuedelduemelbuss",
            {(10, 99): "ü"},
            "Schmuedeldü",
            nullcontext(),
        ),
        (
            "Schmuedelduemelbuss",
            {(10, 12): "ü"},
            "Schmuedeldümelbuss",
            nullcontext(),
        ),
        (
            "Schmuedelduemelbussdaepp",
            {(4, 6): "ü", (10, 12): "ü"},
            "Schmüdeldümelbussdaepp",
            nullcontext(),
        ),
        (
            "Schmuedelduemelbussdaepp",
            {(4, 6): "ü", (10, 12): "ü", (17, 19): "ß"},
            "Schmüdeldümelbußdaepp",
            nullcontext(),
        ),
        (
            "Schmuedelduemelbussdaepp",
            {(4, 6): "ü", (10, 12): "ü", (17, 19): "ß", (20, 22): "ä"},
            "Schmüdeldümelbußdäpp",
            nullcontext(),
        ),
    ],
)
def test_substitute_spans(string, substitutions, result, expectation):
    with expectation:
        assert _substitute_spans(string, substitutions) == result


@pytest.fixture(scope="module")  # https://stackoverflow.com/a/64693486/11477374
def german_words():
    """Provides same known words list as used by the main script."""
    return get_dictionary(language="de")


@pytest.fixture(scope="module")  # https://stackoverflow.com/a/64693486/11477374
def german_language_mapping():
    """Provides same mapping of native characters to alt. spellings as main script."""
    return get_language_mappings()["de"]


_COMMON_ARGS = [
    ("Uebel", False, "Übel", nullcontext()),
    ("uebel", False, "übel", nullcontext()),
    ("Busse", False, "Buße", nullcontext()),
    ("busse", False, "busse", nullcontext()),
    ("Gruss", False, "Gruß", nullcontext()),
    ("gruss", False, "gruss", nullcontext()),
    ("gruesse", False, "grüße", nullcontext()),
    ("Apfel", False, "Apfel", nullcontext()),
    ("apfel", False, "apfel", nullcontext()),
    ("Aepfel", False, "Äpfel", nullcontext()),
    (
        "Ueberhaupt braeuchte es mal einen Teststring.",
        False,
        "Überhaupt bräuchte es mal einen Teststring.",
        nullcontext(),
    ),
    (
        "Saetze ohne Bedeutung, aber mit vielen Umlauten.",
        False,
        "Sätze ohne Bedeutung, aber mit vielen Umlauten.",
        nullcontext(),
    ),
    (
        "DRPFA-Angehoerige gehoeren haeufig nicht dazu.",
        False,
        "DRPFA-Angehörige gehören häufig nicht dazu.",
        nullcontext(),
    ),
    (
        "Bindestrich-Woerter spraechen Baende ueber Fehler.",
        False,
        "Bindestrich-Wörter sprächen Bände über Fehler.",
        nullcontext(),
    ),
    (
        "Doppelgaenger-Doppelgaenger sind doppelt droelfzig.",
        False,
        "Doppelgänger-Doppelgänger sind doppelt droelfzig.",
        nullcontext(),
    ),
    (
        "Oder Uemlaeuten? Auslaeuten? Leute gaebe es, wuerde man meinen.",
        False,
        "Oder Uemlaeuten? Auslaeuten? Leute gäbe es, würde man meinen.",
        nullcontext(),
    ),
    (
        "Ueble Nachrede ist naechtens nicht erlaubt.",
        False,
        "Üble Nachrede ist nächtens nicht erlaubt.",
        nullcontext(),
    ),
    (
        "Erlaube man dieses, waere es schoen uebertrieben.",
        False,
        "Erlaube man dieses, wäre es schön übertrieben.",
        nullcontext(),
    ),
    (
        "Busse muesste geloest werden, bevor Gruesse zum Gruss kommen.",
        False,
        "Buße müsste gelöst werden, bevor Grüße zum Gruß kommen.",
        nullcontext(),
    ),
    (
        "Busse sind Geraete, die womoeglich schnell fuehren.",
        False,
        "Buße sind Geräte, die womöglich schnell führen.",
        nullcontext(),
    ),
    ("Voegel sind aehnlich zu Oel.", False, "Vögel sind ähnlich zu Öl.", nullcontext()),
    (
        "Hierfuer ist fuer den droegen Poebel zu beachten, dass Anmassungen"
        " zu Gehoerverlust fuehren koennen.",
        False,
        "Hierfür ist für den drögen Pöbel zu beachten, dass Anmaßungen"
        " zu Gehörverlust führen können.",
        nullcontext(),
    ),
    ("Stroemelschnoesseldaemel", False, "Stroemelschnoesseldaemel", nullcontext()),
    # `force=True`
    ("Stroemelschnoesseldaemel", True, "Strömelschnößeldämel", nullcontext()),
    ("ae", True, "ä", nullcontext()),
    ("Ae", True, "Ä", nullcontext()),
    ("oe", True, "ö", nullcontext()),
    ("Oe", True, "Ö", nullcontext()),
    ("ue", True, "ü", nullcontext()),
    ("Ue", True, "Ü", nullcontext()),
    ("ss", True, "ß", nullcontext()),
    #
    (
        "Ueberhaupt braeuchte es mal einen Teststring. Saetze ohne Bedeutung, aber mit vielen Umlauten. DRPFA-Angehoerige gehoeren haeufig nicht dazu. Bindestrich-Woerter spraechen Baende ueber Fehler. Doppelgaenger-Doppelgaenger sind doppelt droelfzig. Oder Uemlaeuten? Auslaeuten? Leute gaebe es, wuerde man meinen. Ueble Nachrede ist naechtens nicht erlaubt. Erlaube man dieses, waere es schoen uebertrieben. Busse muesste geloest werden, bevor Gruesse zum Gruss kommen. Busse sind Geraete, die womoeglich schnell fuehren. Voegel sind aehnlich zu Oel. Hierfuer ist fuer den droegen Poebel zu beachten, dass Anmassungen zu Gehoerverlust fuehren koennen. Stroemelschnoesseldaemel!",
        False,
        "Überhaupt bräuchte es mal einen Teststring. Sätze ohne Bedeutung, aber mit vielen Umlauten. DRPFA-Angehörige gehören häufig nicht dazu. Bindestrich-Wörter sprächen Bände über Fehler. Doppelgänger-Doppelgänger sind doppelt droelfzig. Oder Uemlaeuten? Auslaeuten? Leute gäbe es, würde man meinen. Üble Nachrede ist nächtens nicht erlaubt. Erlaube man dieses, wäre es schön übertrieben. Buße müsste gelöst werden, bevor Grüße zum Gruß kommen. Buße sind Geräte, die womöglich schnell führen. Vögel sind ähnlich zu Öl. Hierfür ist für den drögen Pöbel zu beachten, dass Anmaßungen zu Gehörverlust führen können. Stroemelschnoesseldaemel!",
        nullcontext(),
    ),
]


class TestForward:
    @pytest.mark.parametrize(
        [
            "text",
            "force",
            "result",
            "expectation",
        ],
        _COMMON_ARGS
        + [
            ("Grüße", False, "Grüße", nullcontext()),
            ("grüße", False, "grüße", nullcontext()),
            ("AEPFEL", False, "ÄPFEL", nullcontext()),
            ("AE", True, "Ä", nullcontext()),
            ("OE", True, "Ö", nullcontext()),
            ("UE", True, "Ü", nullcontext()),
            ("Ss", True, "SS", nullcontext()),
            ("SS", True, "SS", nullcontext()),
        ],
    )
    def test_german(
        self, text, force, result, expectation, german_language_mapping, german_words
    ):
        with expectation:
            assert (
                "".join(forward(text, german_language_mapping, german_words, force))
                == result
            )


class TestBackward:
    @pytest.mark.parametrize(
        [
            "result",
            "force",
            "text",
            "expectation",
        ],
        _COMMON_ARGS,
    )
    def test_german(self, result, force, text, expectation, german_language_mapping):
        with expectation:
            assert "".join(backward(text, german_language_mapping)) == result
