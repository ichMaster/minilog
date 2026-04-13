"""Lexer for minilog .ml source files."""

import unicodedata
from dataclasses import dataclass
from enum import Enum, auto

from minilog.errors import LexError


class TokenType(Enum):
    # Literals & identifiers
    IDENT = auto()
    VAR = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()

    # Ukrainian keywords
    KW_FACT = auto()      # факт
    KW_RULE = auto()      # правило
    KW_IF = auto()        # якщо
    KW_AND = auto()       # і
    KW_NOT = auto()       # не
    KW_TRACE = auto()     # слід

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()

    # Query
    QUERY_START = auto()  # ?-

    # Comparison operators
    OP_GE = auto()        # ≥
    OP_LE = auto()        # ≤
    OP_GT = auto()        # >
    OP_LT = auto()        # <
    OP_EQ = auto()        # =
    OP_NE = auto()        # ≠

    # Arithmetic operators
    OP_PLUS = auto()      # +
    OP_MINUS = auto()     # -
    OP_STAR = auto()      # *
    OP_SLASH = auto()     # /

    # Indentation
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()

    # End of file
    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "факт": TokenType.KW_FACT,
    "правило": TokenType.KW_RULE,
    "якщо": TokenType.KW_IF,
    "і": TokenType.KW_AND,
    "не": TokenType.KW_NOT,
    "слід": TokenType.KW_TRACE,
}


@dataclass
class Token:
    """A single token produced by the lexer."""
    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


def _is_ident_start(ch: str) -> bool:
    """Check if character can start an identifier."""
    return ch == "_" or unicodedata.category(ch).startswith("L")


def _is_ident_cont(ch: str) -> bool:
    """Check if character can continue an identifier."""
    return (ch == "_" or ch == "'"
            or unicodedata.category(ch).startswith("L")
            or unicodedata.category(ch) == "Nd")


def tokenize(source: str) -> list[Token]:
    """Tokenize a minilog source string into a list of tokens."""
    tokens: list[Token] = []
    pos = 0
    line = 1
    col = 1
    indent_stack: list[int] = [0]
    at_line_start = True

    def peek() -> str:
        return source[pos] if pos < len(source) else ""

    def advance() -> str:
        nonlocal pos, col
        ch = source[pos]
        pos += 1
        col += 1
        return ch

    while pos < len(source):
        ch = peek()

        # Handle line comments
        if ch == "%":
            while pos < len(source) and source[pos] != "\n":
                pos += 1
            continue

        # Handle newlines
        if ch == "\n":
            advance()
            line += 1
            col = 1
            at_line_start = True
            continue

        # Handle indentation at start of line
        if at_line_start:
            # Count leading spaces
            indent = 0
            while pos < len(source) and source[pos] == " ":
                indent += 1
                pos += 1
                col += 1

            # Skip blank lines and comment-only lines
            if pos >= len(source) or source[pos] == "\n" or source[pos] == "%":
                continue

            at_line_start = False

            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                tokens.append(Token(TokenType.INDENT, "", line, 1))
            elif indent < indent_stack[-1]:
                while indent_stack[-1] > indent:
                    indent_stack.pop()
                    tokens.append(Token(TokenType.DEDENT, "", line, 1))
                if indent_stack[-1] != indent:
                    raise LexError(line, col, "inconsistent indentation")
            else:
                # Same level — emit NEWLINE to separate statements
                if tokens and tokens[-1].type not in (
                    TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT
                ):
                    tokens.append(Token(TokenType.NEWLINE, "", line, 1))

            continue

        # Skip spaces (not at line start)
        if ch == " " or ch == "\t":
            advance()
            continue

        start_col = col

        # Query start: ?-
        if ch == "?" and pos + 1 < len(source) and source[pos + 1] == "-":
            advance()
            advance()
            tokens.append(Token(TokenType.QUERY_START, "?-", line, start_col))
            continue

        # Variables: ?ident or ?_
        if ch == "?":
            advance()
            if pos < len(source) and source[pos] == "_" and (
                pos + 1 >= len(source) or not _is_ident_cont(source[pos + 1])
            ):
                advance()
                tokens.append(Token(TokenType.VAR, "_", line, start_col))
                continue
            if pos < len(source) and _is_ident_start(source[pos]):
                name_start = pos
                while pos < len(source) and _is_ident_cont(source[pos]):
                    pos += 1
                    col += 1
                name = source[name_start:pos]
                tokens.append(Token(TokenType.VAR, name, line, start_col))
                continue
            raise LexError(line, start_col, "expected variable name after '?'")

        # Identifiers and keywords
        if _is_ident_start(ch):
            name_start = pos
            while pos < len(source) and _is_ident_cont(source[pos]):
                pos += 1
                col += 1
            name = source[name_start:pos]
            tt = KEYWORDS.get(name, TokenType.IDENT)
            tokens.append(Token(tt, name, line, start_col))
            continue

        # Numbers
        if ch.isdigit():
            num_start = pos
            while pos < len(source) and source[pos].isdigit():
                pos += 1
                col += 1
            if pos < len(source) and source[pos] == "." and (
                pos + 1 < len(source) and source[pos + 1].isdigit()
            ):
                pos += 1
                col += 1
                while pos < len(source) and source[pos].isdigit():
                    pos += 1
                    col += 1
                tokens.append(Token(TokenType.FLOAT, source[num_start:pos], line, start_col))
            else:
                tokens.append(Token(TokenType.INT, source[num_start:pos], line, start_col))
            continue

        # String literals
        if ch == '"':
            advance()  # skip opening quote
            string_val: list[str] = []
            while pos < len(source) and source[pos] != '"':
                if source[pos] == "\\":
                    pos += 1
                    col += 1
                    if pos >= len(source):
                        raise LexError(line, col, "unterminated string escape")
                    esc = source[pos]
                    if esc == "n":
                        string_val.append("\n")
                    elif esc == '"':
                        string_val.append('"')
                    elif esc == "\\":
                        string_val.append("\\")
                    else:
                        raise LexError(line, col, f"unknown escape '\\{esc}'")
                    pos += 1
                    col += 1
                elif source[pos] == "\n":
                    raise LexError(line, col, "unterminated string literal")
                else:
                    string_val.append(source[pos])
                    pos += 1
                    col += 1
            if pos >= len(source):
                raise LexError(line, col, "unterminated string literal")
            pos += 1  # skip closing quote
            col += 1
            tokens.append(Token(TokenType.STRING, "".join(string_val), line, start_col))
            continue

        # Punctuation
        if ch == "(":
            advance()
            tokens.append(Token(TokenType.LPAREN, "(", line, start_col))
            continue
        if ch == ")":
            advance()
            tokens.append(Token(TokenType.RPAREN, ")", line, start_col))
            continue
        if ch == ",":
            advance()
            tokens.append(Token(TokenType.COMMA, ",", line, start_col))
            continue
        if ch == ".":
            advance()
            tokens.append(Token(TokenType.DOT, ".", line, start_col))
            continue
        if ch == ":":
            advance()
            tokens.append(Token(TokenType.COLON, ":", line, start_col))
            continue

        # Comparison operators
        if ch == "≥":
            advance()
            tokens.append(Token(TokenType.OP_GE, "≥", line, start_col))
            continue
        if ch == "≤":
            advance()
            tokens.append(Token(TokenType.OP_LE, "≤", line, start_col))
            continue
        if ch == ">":
            advance()
            tokens.append(Token(TokenType.OP_GT, ">", line, start_col))
            continue
        if ch == "<":
            advance()
            tokens.append(Token(TokenType.OP_LT, "<", line, start_col))
            continue
        if ch == "=":
            advance()
            tokens.append(Token(TokenType.OP_EQ, "=", line, start_col))
            continue
        if ch == "≠":
            advance()
            tokens.append(Token(TokenType.OP_NE, "≠", line, start_col))
            continue
        if ch == "!" and pos + 1 < len(source) and source[pos + 1] == "=":
            advance()  # consume !
            advance()  # consume =
            tokens.append(Token(TokenType.OP_NE, "!=", line, start_col))
            continue

        # Arithmetic operators
        if ch == "+":
            advance()
            tokens.append(Token(TokenType.OP_PLUS, "+", line, start_col))
            continue
        if ch == "*":
            advance()
            tokens.append(Token(TokenType.OP_STAR, "*", line, start_col))
            continue
        if ch == "/":
            advance()
            tokens.append(Token(TokenType.OP_SLASH, "/", line, start_col))
            continue
        if ch == "-":
            # Unary minus on numeric literal: if followed by digit and previous
            # token is an expression-starting token, emit negative number
            _unary_ctx = {
                TokenType.LPAREN, TokenType.COMMA, TokenType.OP_GE,
                TokenType.OP_LE, TokenType.OP_GT, TokenType.OP_LT,
                TokenType.OP_EQ, TokenType.OP_NE, TokenType.OP_PLUS,
                TokenType.OP_MINUS, TokenType.OP_STAR, TokenType.OP_SLASH,
                TokenType.KW_IF, TokenType.KW_AND, TokenType.NEWLINE,
                TokenType.INDENT,
            }
            next_pos = pos + 1
            next_is_digit = next_pos < len(source) and source[next_pos].isdigit()
            prev_is_unary = not tokens or tokens[-1].type in _unary_ctx
            if next_is_digit and prev_is_unary:
                advance()  # consume -
                num_start = pos
                while pos < len(source) and source[pos].isdigit():
                    pos += 1
                    col += 1
                if pos < len(source) and source[pos] == "." and (
                    pos + 1 < len(source) and source[pos + 1].isdigit()
                ):
                    pos += 1
                    col += 1
                    while pos < len(source) and source[pos].isdigit():
                        pos += 1
                        col += 1
                    tokens.append(Token(TokenType.FLOAT, "-" + source[num_start:pos], line, start_col))
                else:
                    tokens.append(Token(TokenType.INT, "-" + source[num_start:pos], line, start_col))
                continue
            advance()
            tokens.append(Token(TokenType.OP_MINUS, "-", line, start_col))
            continue

        raise LexError(line, start_col, f"unexpected character {ch!r}")

    # Emit remaining DEDENTs
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token(TokenType.DEDENT, "", line, col))

    tokens.append(Token(TokenType.EOF, "", line, col))
    return tokens
