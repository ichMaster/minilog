"""Unit tests for minilog.lexer."""

import pytest

from minilog.lexer import Token, TokenType, tokenize
from minilog.errors import LexError


def test_simple_fact():
    """Tokenize a plain fact like батько(авраам, ісак)."""
    tokens = tokenize("батько(авраам, ісак).")
    types = [t.type for t in tokens]
    assert types == [
        TokenType.IDENT, TokenType.LPAREN,
        TokenType.IDENT, TokenType.COMMA,
        TokenType.IDENT, TokenType.RPAREN,
        TokenType.DOT, TokenType.EOF,
    ]
    assert tokens[0].value == "батько"
    assert tokens[2].value == "авраам"
    assert tokens[4].value == "ісак"


def test_inline_rule():
    """Tokenize an inline rule with keyword recognition."""
    tokens = tokenize("правило предок(?х, ?y) якщо батько(?х, ?y).")
    types = [t.type for t in tokens]
    assert types == [
        TokenType.KW_RULE, TokenType.IDENT, TokenType.LPAREN,
        TokenType.VAR, TokenType.COMMA, TokenType.VAR,
        TokenType.RPAREN, TokenType.KW_IF,
        TokenType.IDENT, TokenType.LPAREN,
        TokenType.VAR, TokenType.COMMA, TokenType.VAR,
        TokenType.RPAREN, TokenType.DOT, TokenType.EOF,
    ]
    assert tokens[0].value == "правило"
    assert tokens[3].value == "х"
    assert tokens[5].value == "y"


def test_block_rule_indent_dedent():
    """Block-form rule produces INDENT/DEDENT tokens."""
    src = "правило предок(?х, ?y):\n    якщо батько(?х, ?y).\n"
    tokens = tokenize(src)
    types = [t.type for t in tokens]
    assert TokenType.COLON in types
    assert TokenType.INDENT in types
    assert TokenType.DEDENT in types


def test_query():
    """Tokenize a query with ?- prefix."""
    tokens = tokenize("?- предок(авраам, ?хто).")
    types = [t.type for t in tokens]
    assert types == [
        TokenType.QUERY_START, TokenType.IDENT, TokenType.LPAREN,
        TokenType.IDENT, TokenType.COMMA, TokenType.VAR,
        TokenType.RPAREN, TokenType.DOT, TokenType.EOF,
    ]
    assert tokens[0].value == "?-"
    assert tokens[5].value == "хто"


def test_comments_discarded():
    """Line comments starting with % are discarded."""
    src = "% це коментар\nбатько(авраам, ісак)."
    tokens = tokenize(src)
    values = [t.value for t in tokens if t.type == TokenType.IDENT]
    assert values == ["батько", "авраам", "ісак"]
    # No comment content in tokens
    for t in tokens:
        assert "коментар" not in t.value


def test_variables_and_anonymous():
    """Variables ?ident and anonymous ?_ are recognized."""
    tokens = tokenize("предок(?х, ?_).")
    var_tokens = [t for t in tokens if t.type == TokenType.VAR]
    assert len(var_tokens) == 2
    assert var_tokens[0].value == "х"
    assert var_tokens[1].value == "_"


def test_numbers_int_and_float():
    """Integer and float literals are tokenized correctly."""
    tokens = tokenize("вік(петро, 42). вага(3.14).")
    int_tokens = [t for t in tokens if t.type == TokenType.INT]
    float_tokens = [t for t in tokens if t.type == TokenType.FLOAT]
    assert len(int_tokens) == 1
    assert int_tokens[0].value == "42"
    assert len(float_tokens) == 1
    assert float_tokens[0].value == "3.14"


def test_string_literal():
    """String literals with escape sequences."""
    tokens = tokenize('"hello\\nworld"')
    str_tokens = [t for t in tokens if t.type == TokenType.STRING]
    assert len(str_tokens) == 1
    assert str_tokens[0].value == "hello\nworld"


def test_comparison_operators():
    """All comparison operators are recognized."""
    src = "?n ≥ 18. ?n ≤ 5. ?a > 3. ?b < 10. ?c = 1. ?d ≠ 0."
    tokens = tokenize(src)
    op_types = [t.type for t in tokens if t.type.name.startswith("OP_")]
    assert op_types == [
        TokenType.OP_GE, TokenType.OP_LE,
        TokenType.OP_GT, TokenType.OP_LT,
        TokenType.OP_EQ, TokenType.OP_NE,
    ]


def test_malformed_input_raises_lex_error():
    """Unexpected characters raise LexError with position."""
    with pytest.raises(LexError) as exc_info:
        tokenize("батько@авраам")
    assert "unexpected character" in str(exc_info.value)
    assert exc_info.value.line == 1


def test_line_col_tracking():
    """Tokens carry correct line and column information."""
    src = "батько(авраам, ісак).\nмати(сара, ісак)."
    tokens = tokenize(src)
    # First token on line 1
    assert tokens[0].line == 1
    assert tokens[0].col == 1
    # After NEWLINE, "мати" should be on line 2
    мати_token = [t for t in tokens if t.value == "мати"][0]
    assert мати_token.line == 2
    assert мати_token.col == 1


def test_traced_query():
    """Tokenize a traced query with слід keyword."""
    tokens = tokenize("?- слід предок(авраам, йосип).")
    types = [t.type for t in tokens]
    assert TokenType.QUERY_START in types
    assert TokenType.KW_TRACE in types


def test_nullary_atom_fact():
    """A bare atom followed by a dot is a valid fact."""
    tokens = tokenize("сонячно.")
    types = [t.type for t in tokens]
    assert types == [TokenType.IDENT, TokenType.DOT, TokenType.EOF]


def test_keyword_and():
    """The single-letter keyword і is recognized."""
    tokens = tokenize("правило x(?a) якщо y(?a) і z(?a).")
    and_tokens = [t for t in tokens if t.type == TokenType.KW_AND]
    assert len(and_tokens) == 1
    assert and_tokens[0].value == "і"
