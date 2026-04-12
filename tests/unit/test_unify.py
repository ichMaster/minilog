"""Unit tests for minilog.unify."""

from minilog.terms import Atom, Compound, Num, Str, Var
from minilog.unify import Substitution, unify, walk


def test_atom_atom_success():
    """Two identical atoms unify without extending the substitution."""
    s = unify(Atom("a"), Atom("a"), Substitution.empty())
    assert s is not None
    assert s.bindings == ()


def test_atom_atom_failure():
    """Two different atoms fail to unify."""
    s = unify(Atom("a"), Atom("b"), Substitution.empty())
    assert s is None


def test_var_binding():
    """A variable unifies with a term by extending the substitution."""
    s = unify(Var("x"), Atom("a"), Substitution.empty())
    assert s is not None
    assert s.apply(Var("x")) == Atom("a")


def test_var_var_binding():
    """Two different variables unify by binding one to the other."""
    s = unify(Var("x"), Var("y"), Substitution.empty())
    assert s is not None
    # One of them should resolve to the other
    result = s.apply(Var("x"))
    assert result == Var("y") or s.apply(Var("y")) == Var("x")


def test_compound_compound_success():
    """Compound terms with matching functor/arity unify recursively."""
    t1 = Compound("f", (Var("x"), Atom("b")))
    t2 = Compound("f", (Atom("a"), Var("y")))
    s = unify(t1, t2, Substitution.empty())
    assert s is not None
    assert s.apply(Var("x")) == Atom("a")
    assert s.apply(Var("y")) == Atom("b")


def test_compound_compound_arity_mismatch():
    """Compounds with different arities fail to unify."""
    t1 = Compound("f", (Atom("a"),))
    t2 = Compound("f", (Atom("a"), Atom("b")))
    s = unify(t1, t2, Substitution.empty())
    assert s is None


def test_compound_functor_mismatch():
    """Compounds with different functors fail to unify."""
    t1 = Compound("f", (Atom("a"),))
    t2 = Compound("g", (Atom("a"),))
    s = unify(t1, t2, Substitution.empty())
    assert s is None


def test_nested_unification():
    """Nested compound terms unify correctly."""
    t1 = Compound("f", (Compound("g", (Var("x"),)),))
    t2 = Compound("f", (Compound("g", (Atom("a"),)),))
    s = unify(t1, t2, Substitution.empty())
    assert s is not None
    assert s.apply(Var("x")) == Atom("a")


def test_walk_chain():
    """walk follows a chain of variable bindings."""
    s = Substitution.empty()
    s = s.extend(Var("x"), Var("y"))
    s = s.extend(Var("y"), Atom("a"))
    result = walk(Var("x"), s)
    assert result == Atom("a")


def test_walk_unbound():
    """walk returns the variable itself when unbound."""
    result = walk(Var("x"), Substitution.empty())
    assert result == Var("x")


def test_apply_roundtrip():
    """apply resolves all variables in a compound term."""
    s = Substitution.empty()
    s = s.extend(Var("x"), Atom("авраам"))
    s = s.extend(Var("y"), Atom("ісак"))
    term = Compound("батько", (Var("x"), Var("y")))
    result = s.apply(term)
    assert result == Compound("батько", (Atom("авраам"), Atom("ісак")))


def test_num_unification():
    """Numbers unify with equal numbers, fail with different ones."""
    assert unify(Num(42), Num(42), Substitution.empty()) is not None
    assert unify(Num(42), Num(43), Substitution.empty()) is None


def test_str_unification():
    """Strings unify with equal strings, fail with different ones."""
    assert unify(Str("a"), Str("a"), Substitution.empty()) is not None
    assert unify(Str("a"), Str("b"), Substitution.empty()) is None


def test_atom_num_mismatch():
    """An atom and a number do not unify."""
    assert unify(Atom("42"), Num(42), Substitution.empty()) is None


def test_substitution_empty():
    """Empty substitution has no bindings."""
    s = Substitution.empty()
    assert s.bindings == ()
    assert s.lookup(Var("x")) is None
