import json
from contextlib import nullcontext
from importlib.resources import open_text

import pytest
from specialsinserter import (ENCODING, cf_contains, combinations_any_length,
                              distinct_highest_element,
                              filter_strs_by_letter_occurrence,
                              represent_strings, substitute_alts_with_specials,
                              substitute_spans)

# Placeholder for parameters that do not matter in that instance of a test, e.g.
# when an exception is raised, so no result is produced.
VOID = None


class TestHelpers:
    @pytest.mark.parametrize(
        ["iterable", "key", "element", "expectation"],
        [
            # Empty iterables
            ([], None, VOID, pytest.raises(IndexError)),
            ((), None, VOID, pytest.raises(IndexError)),
            ("", None, VOID, pytest.raises(IndexError)),
            ({}, None, VOID, pytest.raises(IndexError)),
            #
            # Single-element iterables
            ([1], None, 1, nullcontext()),
            ((1,), None, 1, nullcontext()),
            ("1", None, "1", nullcontext()),
            ({"1": None}, None, "1", nullcontext()),
            #
            # Non-iterables
            ((1), None, VOID, pytest.raises(TypeError)),  # Not actually a tuple
            (None, None, VOID, pytest.raises(TypeError)),
            (1, None, VOID, pytest.raises(TypeError)),
            #
            # Multi-element iterables w/ single distinct highest element
            ([1, 2, 3], None, 3, nullcontext()),
            ((1.0, 2.0, 3.0), None, 3, nullcontext()),
            ("abc", None, "c", nullcontext()),
            ([(1, 2), (1, 3)], None, (1, 3), nullcontext()),
            #
            # Multi-element iterables w/o single distinct highest element
            ([1, 2, 3, 3], None, None, nullcontext()),
            ((1.0, 2.0, 3.0, 3.0), None, None, nullcontext()),
            ("abcc", None, None, nullcontext()),
            ([(1, 2), (1, 3), (1, 3)], None, None, nullcontext()),
            #
            # Multi-element iterables w/ key and w/o single distinct highest element
            ([[], []], len, None, nullcontext()),
            ([1, 2, 3], len, VOID, pytest.raises(TypeError)),  # int has no len
            ((1.0, 2.0, 3.0), len, VOID, pytest.raises(TypeError)),
            ("abc", len, None, nullcontext()),  # all chars in str same length
            ([(1, 2), (1, 3)], len, None, nullcontext()),  # all tuples same length
            #
            # Multi-element iterables w/ key and w/o single distinct highest element
            ([1, 2, 3, 3], len, VOID, pytest.raises(TypeError)),
            ((1.0, 2.0, 3.0, 3.0), len, VOID, pytest.raises(TypeError)),
            ("abcc", len, None, nullcontext()),  # all chars in str same length
            ([(1, 2), (1, 3), (1, 3)], len, None, nullcontext()),
            #
            # Multi-element iterables w/ key and w/ single distinct highest element
            ("a", len, "a", nullcontext()),
            (["b", "b", "bb"], len, "bb", nullcontext()),
            (["a", "b", "cc"], len, "cc", nullcontext()),
            ([(), (1,)], len, (1,), nullcontext()),
            ([(1,)], len, (1,), nullcontext()),
            ([(1, 2), (1, 3), (1, 2, 3)], len, (1, 2, 3), nullcontext()),
            #
            ([1, 2, 3], "Not a callable", VOID, pytest.raises(TypeError)),
        ],
    )
    def test_distinct_highest_element(self, iterable, key, element, expectation):
        with expectation:
            assert distinct_highest_element(iterable, key) == element

    @pytest.mark.parametrize(
        ["element", "string", "result", "expectation"],
        [
            # Simple strings:
            ("", "", True, nullcontext()),
            ("", "a", True, nullcontext()),
            ("a", "", False, nullcontext()),
            ("a", "a", True, nullcontext()),
            ("aa", "a", False, nullcontext()),
            ("a", "aa", True, nullcontext()),
            #
            # Invalids
            (1, "", VOID, pytest.raises(AttributeError)),
            (1, 1, VOID, pytest.raises(AttributeError)),
            (None, None, VOID, pytest.raises(AttributeError)),
            #
            # Unicode strings
            ("ß", "ß", True, nullcontext()),
            ("ss", "ß", True, nullcontext()),
            ("ß", "ss", True, nullcontext()),
            ("SS", "ß", True, nullcontext()),
            ("ß", "SS", True, nullcontext()),
            ("SS", "SS", True, nullcontext()),
            ("ss", "ss", True, nullcontext()),
            ("ẞ", "ss", True, nullcontext()),  # Uppercase ß
            ("ẞ", "SS", True, nullcontext()),  # Uppercase ß
            ("ẞ", "ß", True, nullcontext()),  # Uppercase ß
            ("ẞ", "ẞ", True, nullcontext()),  # Uppercase ß
            ("ss", "ẞ", True, nullcontext()),  # Uppercase ß
            ("SS", "ẞ", True, nullcontext()),  # Uppercase ß
            ("ß", "ẞ", True, nullcontext()),  # Uppercase ß
            ("ẞ", "ẞ", True, nullcontext()),  # Uppercase ß
            #
            ("Bussgeld", "BUẞGELD IST DOOF!", True, nullcontext()),
            ("Bußgeld", "BUẞGELD IST DOOF!", True, nullcontext()),
            ("BUSSGELD", "BUẞGELD IST DOOF!", True, nullcontext()),
            ("BUẞGELD", "BUẞGELD IST DOOF!", True, nullcontext()),
        ],
    )
    def test_cf_contains(self, element, string, result, expectation):
        with expectation:
            assert cf_contains(element, string) == result

    @pytest.mark.parametrize(
        ["strings", "letter_filters", "result", "expectation"],
        [
            ([""], [""], [""], nullcontext()),
            (["a"], [""], ["a"], nullcontext()),
            (["a", "b"], [""], ["a", "b"], nullcontext()),
            #
            ([""], ["a"], [], nullcontext()),
            #
            (
                ["Hello World", "Hello", "World"],
                ["Hello"],
                ["Hello World", "Hello"],
                nullcontext(),
            ),
            #
            (
                ["Äpfel", "Banane", "Bußgeld", "Öl", "Schiff"],
                ["ä", "ö", "ü", "ß"],
                ["Äpfel", "Bußgeld", "Öl"],
                nullcontext(),
            ),
            (
                ["Äpfel", "äpfel", "ÄPFEL"],
                ["ä"],
                ["Äpfel", "äpfel", "ÄPFEL"],
                nullcontext(),
            ),
            (
                ["Äpfel", "äpfel", "ÄPFEL"],
                ["Ä"],
                ["Äpfel", "äpfel", "ÄPFEL"],
                nullcontext(),
            ),
        ],
    )
    def test_filter_strs_by_letter_occurrence(
        self, strings, letter_filters, result, expectation
    ):
        with expectation:
            assert (
                list(filter_strs_by_letter_occurrence(strings, letter_filters))
                == result
            )

    @pytest.mark.parametrize(
        ["iterable", "result", "expectation"],
        [
            ("a", [("a",)], nullcontext()),
            ("ab", [("a",), ("b",), ("a", "b")], nullcontext()),
            (
                "abc",
                [
                    ("a",),
                    ("b",),
                    ("c",),
                    ("a", "b"),
                    ("a", "c"),
                    ("b", "c"),
                    ("a", "b", "c"),
                ],
                nullcontext(),
            ),
            (
                [1, 2, 3],
                [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3),],
                nullcontext(),
            ),
            (
                [(1, 2), (3, 4), (5, 6)],
                [
                    ((1, 2),),
                    ((3, 4),),
                    ((5, 6),),
                    ((1, 2), (3, 4)),
                    ((1, 2), (5, 6)),
                    ((3, 4), (5, 6)),
                    ((1, 2), (3, 4), (5, 6)),
                ],
                nullcontext(),
            ),
            (
                [(1,), (2,), (3,), (4, 5)],
                [
                    ((1,),),
                    ((2,),),
                    ((3,),),
                    ((4, 5),),
                    ((1,), (2,)),
                    ((1,), (3,)),
                    ((1,), (4, 5)),
                    ((2,), (3,)),
                    ((2,), (4, 5)),
                    ((3,), (4, 5)),
                    ((1,), (2,), (3,)),
                    ((1,), (2,), (4, 5)),
                    ((1,), (3,), (4, 5)),
                    ((2,), (3,), (4, 5)),
                    ((1,), (2,), (3,), (4, 5)),
                ],
                nullcontext(),
            ),
        ],
    )
    def test_combinations_any_length(self, iterable, result, expectation):
        with expectation:
            assert list(combinations_any_length(iterable)) == result

    @pytest.mark.parametrize(
        ["string", "spans", "spans_to_substitutions", "result", "expectation"],
        [
            ("A", [(0, 1)], {(0, 1): "B"}, "B", nullcontext()),
            ("Apple", [(0, 1)], {(0, 1): "B"}, "Bpple", nullcontext()),
            ("Apple", [(0, 1)], {(0, 1): "Ba"}, "Bapple", nullcontext()),
            #
            ("Apple", [(0, 1)], {(0, 1): "B", (2, 3): "C"}, "Bpple", nullcontext()),
            #
            (0 * " ", [(0, 1)], {(0, 1): "A"}, "A", nullcontext()),
            (1 * " ", [(0, 1)], {(0, 1): "A"}, "A", nullcontext()),
            (2 * " ", [(0, 1)], {(0, 1): "A"}, "A" + " ", nullcontext()),
            #
            ("Apple", [(0, 0)], {(0, 0): ""}, "Apple", nullcontext()),
            ("Apple", [(0, 3)], {(0, 3): ""}, "le", nullcontext()),
            ("Apple", [(0, 99)], {(0, 99): ""}, "", nullcontext()),
            #
            (
                "Know the way",
                [(0, 4), (9, 12)],
                {(0, 4): "", (9, 12): ""},
                " the ",
                nullcontext(),
            ),
            (
                "extra",
                [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                {(0, 1): "", (1, 2): "", (2, 3): "", (3, 4): "", (4, 5): ""},
                "",
                nullcontext(),
            ),
            (
                "extra",
                [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                {(0, 1): "H", (1, 2): "e", (2, 3): "l", (3, 4): "l", (4, 5): "o"},
                "Hello",
                nullcontext(),
            ),
            (
                "extra",
                [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                {(0, 1): "Hello", (1, 2): "", (2, 3): "", (3, 4): "", (4, 5): ""},
                "Hello",
                nullcontext(),
            ),
            #
            (
                "Schmuedelduemelbuss",
                [(4, 6), (10, 12), (17, 19)],
                {(4, 6): "ü", (10, 12): "ü", (17, 19): "ß"},
                "Schmüdeldümelbuß",
                nullcontext(),
            ),
            (
                # Do not replace if not requested, even though replacement is available
                # in mapping
                "Schmuedelduemelbussdaepp",
                [(4, 6), (10, 12), (17, 19)],
                {(4, 6): "ü", (10, 12): "ü", (17, 19): "ß", (20, 22): "ä"},
                "Schmüdeldümelbußdaepp",
                nullcontext(),
            ),
            (
                # Only replace if also requested
                "Schmuedelduemelbussdaepp",
                [(4, 6), (10, 12), (17, 19), (20, 22)],
                {(4, 6): "ü", (10, 12): "ü", (17, 19): "ß", (20, 22): "ä"},
                "Schmüdeldümelbußdäpp",
                nullcontext(),
            ),
        ],
    )
    def test_substitute_spans(
        self, string, spans, spans_to_substitutions, result, expectation
    ):
        with expectation:
            assert substitute_spans(string, spans, spans_to_substitutions) == result

    @pytest.mark.parametrize(
        ["strings", "separator", "delimiters", "result", "expectation"],
        [
            ([""], "|", ("[", "]"), "", nullcontext()),
            (["", ""], "|", ("[", "]"), "[|]", nullcontext()),
            (["Hello"], "|", ("[", "]"), "Hello", nullcontext()),
            (["Hello"], "|", ("(", ")"), "Hello", nullcontext()),
            (["Hello"], "/", ("(", ")"), "Hello", nullcontext()),
            (["Hello", "World"], "|", ("[", "]"), "[Hello|World]", nullcontext()),
            #
            ([""], "/", ("(", ")"), "", nullcontext()),
            (["", ""], "/", ("(", ")"), "(/)", nullcontext()),
            (["Hello"], "/", ("[", "]"), "Hello", nullcontext()),
            (["Hello", "World"], "/", ("(", ")"), "(Hello/World)", nullcontext()),
            #
            (
                ["Hello", "World", "!"],
                "|",
                ("[", "]"),
                "[Hello|World|!]",
                nullcontext(),
            ),
            #
            ([""], "|", ["["], VOID, pytest.raises(ValueError)),
        ],
    )
    def test_represent_strings(
        self, strings, separator, delimiters, result, expectation
    ):
        with expectation:
            assert represent_strings(strings, separator, delimiters) == result


class TestMainDE:
    @pytest.fixture
    def known_words(self):
        """Provides same known words list as used by the main script."""
        # Use `open_text`: if this test suite runs successfully, it means import of
        # specialsinserter worked. That way, `open_text` is also guaranteed to work.
        # Messing around here using relative Paths on the other hand is error-prone.
        with open_text(
            "specialsinserter.dicts.containing_specials_only",
            "de.dic",
            encoding=ENCODING,
        ) as f:
            return f.read().splitlines()

    @pytest.fixture
    def specials_to_alt_spellings(self):
        """Provides same mapping of special characters to alt. spellings as main script.
        """
        with open_text(
            "specialsinserter", "language_specials.json", encoding=ENCODING
        ) as f:
            language_specials = json.load(f)
            return language_specials["de"]

    @pytest.mark.parametrize(
        ["text", "force", "result", "expectation",],
        [
            ("Uebel", False, "Übel", nullcontext()),
            ("uebel", False, "übel", nullcontext()),
            ("Busse", False, "Buße", nullcontext()),
            ("busse", False, "busse", nullcontext()),
            ("Gruss", False, "Gruß", nullcontext()),
            ("Grüße", False, "Grüße", nullcontext()),
            ("gruss", False, "gruss", nullcontext()),
            ("grüße", False, "grüße", nullcontext()),
            ("gruesse", False, "grüße", nullcontext()),
            ("Apfel", False, "Apfel", nullcontext()),
            ("apfel", False, "apfel", nullcontext()),
            ("Aepfel", False, "Äpfel", nullcontext()),
            ("AEPFEL", False, "ÄPFEL", nullcontext()),
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
            (
                "Voegel sind aehnlich zu Oel.",
                False,
                "Vögel sind ähnlich zu Öl.",
                nullcontext(),
            ),
            (
                "Hierfuer ist fuer den droegen Poebel zu beachten, dass Anmassungen"
                " zu Gehoerverlust fuehren koennen.",
                False,
                "Hierfür ist für den drögen Pöbel zu beachten, dass Anmaßungen"
                " zu Gehörverlust führen können.",
                nullcontext(),
            ),
            (
                "Stroemelschnoesseldaemel",
                False,
                "Stroemelschnoesseldaemel",
                nullcontext(),
            ),
            # `force=True`
            ("Stroemelschnoesseldaemel", True, "Strömelschnößeldämel", nullcontext(),),
            ("ae", True, "ä", nullcontext(),),
            ("Ae", True, "Ä", nullcontext(),),
            ("AE", True, "Ä", nullcontext(),),
            ("oe", True, "ö", nullcontext(),),
            ("Oe", True, "Ö", nullcontext(),),
            ("OE", True, "Ö", nullcontext(),),
            ("ue", True, "ü", nullcontext(),),
            ("Ue", True, "Ü", nullcontext(),),
            ("UE", True, "Ü", nullcontext(),),
            ("ss", True, "ß", nullcontext(),),
            ("Ss", True, "SS", nullcontext(),),
            ("SS", True, "SS", nullcontext(),),
        ],
    )
    def test_substitute_alts_with_specials(
        self, text, specials_to_alt_spellings, known_words, force, result, expectation
    ):
        with expectation:
            assert (
                substitute_alts_with_specials(
                    text, specials_to_alt_spellings, known_words, force
                )
                == result
            )
