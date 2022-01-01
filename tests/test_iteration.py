from contextlib import nullcontext

import pytest
from subalt.iteration import all_lengths_combinations, filter_strings


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
def test_filter_strings(strings, letter_filters, result, expectation):
    with expectation:
        assert list(filter_strings(strings, letter_filters)) == result


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
            [
                (1,),
                (2,),
                (3,),
                (1, 2),
                (1, 3),
                (2, 3),
                (1, 2, 3),
            ],
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
def test_all_lengths_combinations(iterable, result, expectation):
    with expectation:
        assert list(all_lengths_combinations(iterable)) == result
