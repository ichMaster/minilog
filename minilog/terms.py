"""Term hierarchy for minilog: Atom, Var, Num, Str, Compound."""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Atom:
    """An atomic symbol: авраам, ісак, red."""
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Var:
    """A variable: ?х, ?хто, ?_. Anonymous variable has name='_'."""
    name: str

    def __repr__(self) -> str:
        return f"?{self.name}"


@dataclass(frozen=True)
class Num:
    """A numeric literal: 42, 3.14."""
    value: int | float

    def __repr__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Str:
    """A string literal."""
    value: str

    def __repr__(self) -> str:
        return f'"{self.value}"'


@dataclass(frozen=True)
class Compound:
    """A compound term: батько(авраам, ісак)."""
    functor: str
    args: tuple["Term", ...]

    def __repr__(self) -> str:
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"

    @property
    def arity(self) -> int:
        return len(self.args)


Term = Union[Atom, Var, Num, Str, Compound]


def is_ground(term: Term) -> bool:
    """True if the term contains no variables."""
    if isinstance(term, Var):
        return False
    if isinstance(term, Compound):
        return all(is_ground(a) for a in term.args)
    return True
