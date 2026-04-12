"""Unit tests for minilog.terms."""

from minilog.terms import Atom, Var, Num, Str, Compound, is_ground


def test_atom_equality_and_hash():
    a1 = Atom("авраам")
    a2 = Atom("авраам")
    a3 = Atom("ісак")
    assert a1 == a2
    assert a1 != a3
    assert hash(a1) == hash(a2)
    assert hash(a1) != hash(a3)


def test_var_equality_and_repr():
    v1 = Var("х")
    v2 = Var("х")
    v3 = Var("_")
    assert v1 == v2
    assert v1 != v3
    assert repr(v1) == "?х"
    assert repr(v3) == "?_"


def test_num_and_str():
    n = Num(42)
    f = Num(3.14)
    s = Str("hello")
    assert repr(n) == "42"
    assert repr(f) == "3.14"
    assert repr(s) == '"hello"'
    assert hash(n) == hash(Num(42))
    assert hash(s) == hash(Str("hello"))


def test_compound_repr_and_arity():
    c = Compound("батько", (Atom("авраам"), Atom("ісак")))
    assert repr(c) == "батько(авраам, ісак)"
    assert c.arity == 2
    assert hash(c) == hash(Compound("батько", (Atom("авраам"), Atom("ісак"))))


def test_is_ground():
    assert is_ground(Atom("x")) is True
    assert is_ground(Num(1)) is True
    assert is_ground(Str("s")) is True
    assert is_ground(Var("y")) is False
    assert is_ground(Compound("f", (Atom("a"), Atom("b")))) is True
    assert is_ground(Compound("f", (Atom("a"), Var("b")))) is False


def test_nested_compound_is_ground():
    nested = Compound("f", (Compound("g", (Atom("a"),)), Atom("b")))
    assert is_ground(nested) is True
    nested_var = Compound("f", (Compound("g", (Var("x"),)), Atom("b")))
    assert is_ground(nested_var) is False


def test_compound_value_equality():
    c1 = Compound("f", (Atom("a"), Num(1)))
    c2 = Compound("f", (Atom("a"), Num(1)))
    c3 = Compound("f", (Atom("a"), Num(2)))
    assert c1 == c2
    assert c1 != c3
