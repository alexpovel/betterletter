from abc import abstractmethod
from pathlib import Path
from typing import Protocol, TypeAlias, TypeVar

_PACKAGE_ROOT = Path(__file__).parent

Span: TypeAlias = tuple[int, int]
C = TypeVar("C", bound="Comparable")


class Comparable(Protocol):
    """Protocol for annotation of comparable types.

    See also https://github.com/python/typing/issues/59#issuecomment-353878355 .
    """
    @abstractmethod
    def __lt__(self: C, other: C) -> bool:
        pass
