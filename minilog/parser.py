"""Recursive-descent parser for minilog .ml files."""

from dataclasses import dataclass
from typing import Union

from minilog.errors import ParseError
from minilog.lexer import Token, TokenType, tokenize
from minilog.terms import Atom, Compound, Num, Str, Term, Var


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------

@dataclass
class Fact:
    head: Compound


@dataclass
class Rule:
    head: Compound
    body: list["Goal"]


@dataclass
class Query:
    goal: Compound
    trace: bool = False


@dataclass(frozen=True)
class Comparison:
    """A numeric comparison goal: ?x ≥ 5."""
    left: Term
    op: str
    right: Term


@dataclass(frozen=True)
class Negation:
    """A negation-as-failure goal: не compound(...)."""
    inner: Compound


Goal = Union[Compound, Comparison, Negation]


@dataclass
class Program:
    facts: list[Fact]
    rules: list[Rule]
    queries: list[Query]


# ---------------------------------------------------------------------------
# Comparison operator tokens
# ---------------------------------------------------------------------------

COMPARISON_OPS: dict[TokenType, str] = {
    TokenType.OP_GE: "≥",
    TokenType.OP_LE: "≤",
    TokenType.OP_GT: ">",
    TokenType.OP_LT: "<",
    TokenType.OP_EQ: "=",
    TokenType.OP_NE: "≠",
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """Recursive-descent parser for minilog token streams."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # -- helpers --

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self) -> TokenType:
        return self.tokens[self.pos].type

    def _at(self, *types: TokenType) -> bool:
        return self._peek() in types

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, tt: TokenType) -> Token:
        tok = self._current()
        if tok.type != tt:
            raise ParseError(
                tok.line, tok.col,
                f"expected {tt.name}, got {tok.type.name} ({tok.value!r})",
            )
        return self._advance()

    def _skip_newlines(self) -> None:
        while self._at(TokenType.NEWLINE):
            self._advance()

    def _error(self, msg: str) -> ParseError:
        tok = self._current()
        return ParseError(tok.line, tok.col, msg)

    # -- grammar --

    def parse(self) -> Program:
        """Parse the full token stream into a Program AST."""
        facts: list[Fact] = []
        rules: list[Rule] = []
        queries: list[Query] = []

        self._skip_newlines()
        while not self._at(TokenType.EOF):
            if self._at(TokenType.KW_RULE):
                rules.append(self._parse_rule())
            elif self._at(TokenType.QUERY_START):
                queries.append(self._parse_query())
            elif self._at(TokenType.IDENT):
                facts.append(self._parse_fact())
            else:
                raise self._error(
                    f"expected fact, rule, or query; got {self._peek().name}"
                )
            self._skip_newlines()

        return Program(facts=facts, rules=rules, queries=queries)

    def _parse_fact(self) -> Fact:
        """Parse: compound '.'"""
        head = self._parse_compound()
        if not isinstance(head, Compound):
            raise self._error("fact head must be a compound term or atom")
        self._expect(TokenType.DOT)
        return Fact(head=head)

    def _parse_rule(self) -> Rule:
        """Parse both inline and block rule forms."""
        self._advance()  # consume KW_RULE
        head = self._parse_compound()
        if not isinstance(head, Compound):
            raise self._error("rule head must be a compound term or atom")

        if self._at(TokenType.KW_IF):
            # Inline form: правило head якщо body .
            self._advance()  # consume якщо
            body = self._parse_body()
            self._expect(TokenType.DOT)
            return Rule(head=head, body=body)

        if self._at(TokenType.COLON):
            # Block form: правило head : NEWLINE INDENT якщо body . DEDENT
            self._advance()  # consume :
            self._skip_newlines()
            self._expect(TokenType.INDENT)
            self._skip_newlines()
            self._expect(TokenType.KW_IF)
            body = self._parse_body()
            self._skip_newlines()
            self._expect(TokenType.DOT)
            self._skip_newlines()
            self._expect(TokenType.DEDENT)
            return Rule(head=head, body=body)

        raise self._error("expected 'якщо' or ':' after rule head")

    def _parse_query(self) -> Query:
        """Parse: '?-' ['слід'] compound '.'"""
        self._advance()  # consume QUERY_START
        trace = False
        if self._at(TokenType.KW_TRACE):
            trace = True
            self._advance()
        goal = self._parse_compound()
        if not isinstance(goal, Compound):
            raise self._error("query goal must be a compound term or atom")
        self._expect(TokenType.DOT)
        return Query(goal=goal, trace=trace)

    def _parse_body(self) -> list[Goal]:
        """Parse: goal { 'і' goal }"""
        goals: list[Goal] = []
        self._skip_newlines()
        goals.append(self._parse_goal())
        self._skip_newlines()
        while self._at(TokenType.KW_AND):
            self._advance()  # consume і
            self._skip_newlines()
            goals.append(self._parse_goal())
            self._skip_newlines()
        return goals

    def _parse_goal(self) -> Goal:
        """Parse: compound | negation | comparison."""
        self._skip_newlines()

        # Negation: не compound
        if self._at(TokenType.KW_NOT):
            self._advance()
            inner = self._parse_compound()
            if not isinstance(inner, Compound):
                raise self._error("negation requires a compound term")
            return Negation(inner=inner)

        # Could be comparison or compound — parse the first term
        left = self._parse_term()

        # Check for comparison operator
        if self._at(*COMPARISON_OPS.keys()):
            op_tok = self._advance()
            op = COMPARISON_OPS[op_tok.type]
            right = self._parse_term()
            return Comparison(left=left, op=op, right=right)

        # Must be a compound goal
        if not isinstance(left, Compound):
            raise self._error("goal must be a compound term, comparison, or negation")
        return left

    def _parse_compound(self) -> Compound:
        """Parse: IDENT '(' [term {',' term}] ')' | IDENT (nullary atom)."""
        tok = self._expect(TokenType.IDENT)
        functor = tok.value

        if not self._at(TokenType.LPAREN):
            # Nullary atom treated as 0-arity Compound for uniformity
            return Compound(functor=functor, args=())

        self._advance()  # consume (
        args: list[Term] = []
        if not self._at(TokenType.RPAREN):
            args.append(self._parse_term())
            while self._at(TokenType.COMMA):
                self._advance()
                args.append(self._parse_term())
        self._expect(TokenType.RPAREN)
        return Compound(functor=functor, args=tuple(args))

    def _parse_term(self) -> Term:
        """Parse: atom | variable | number | string | compound."""
        if self._at(TokenType.VAR):
            tok = self._advance()
            return Var(name=tok.value)

        if self._at(TokenType.INT):
            tok = self._advance()
            return Num(value=int(tok.value))

        if self._at(TokenType.FLOAT):
            tok = self._advance()
            return Num(value=float(tok.value))

        if self._at(TokenType.STRING):
            tok = self._advance()
            return Str(value=tok.value)

        if self._at(TokenType.IDENT):
            tok = self._current()
            # Look ahead: if followed by '(' it's a compound, otherwise an atom
            if (self.pos + 1 < len(self.tokens)
                    and self.tokens[self.pos + 1].type == TokenType.LPAREN):
                return self._parse_compound()
            self._advance()
            return Atom(name=tok.value)

        raise self._error(
            f"expected term, got {self._peek().name} ({self._current().value!r})"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(source: str) -> Program:
    """Parse a minilog source string into a Program AST."""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()
