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
class ProductionRuleDef:
    """A production rule definition from .ml source."""
    name: str
    condition: list[Goal]
    add: list[Compound]
    remove: list[Compound]
    guard: Goal | None = None


@dataclass
class Program:
    facts: list[Fact]
    rules: list[Rule]
    queries: list[Query]
    production_rules: list[ProductionRuleDef] | None = None


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

        production_rules: list[ProductionRuleDef] = []

        self._skip_newlines()
        while not self._at(TokenType.EOF):
            if self._at(TokenType.KW_RULE):
                rules.append(self._parse_rule())
            elif self._at(TokenType.KW_PRODUCTION):
                production_rules.append(self._parse_production_rule())
            elif self._at(TokenType.QUERY_START):
                queries.append(self._parse_query())
            elif self._at(TokenType.IDENT):
                facts.append(self._parse_fact())
            else:
                raise self._error(
                    f"expected fact, rule, query, or production rule; got {self._peek().name}"
                )
            self._skip_newlines()

        return Program(facts=facts, rules=rules, queries=queries,
                       production_rules=production_rules or None)

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

    def _parse_production_rule(self) -> ProductionRuleDef:
        """Parse: продукція <name> якщо <body> [додати <terms>] [видалити <terms>] [коли <guard>]."""
        self._advance()  # consume KW_PRODUCTION
        name_tok = self._expect(TokenType.IDENT)
        name = name_tok.value

        self._skip_newlines()
        self._expect(TokenType.KW_IF)
        condition = self._parse_body()

        add_terms: list[Compound] = []
        remove_terms: list[Compound] = []
        guard: Goal | None = None

        self._skip_newlines()

        # Parse optional додати clause
        if self._at(TokenType.KW_ADD):
            self._advance()
            self._skip_newlines()
            add_terms.append(self._parse_compound())
            while self._at(TokenType.COMMA):
                self._advance()
                self._skip_newlines()
                add_terms.append(self._parse_compound())
            self._skip_newlines()

        # Parse optional видалити clause
        if self._at(TokenType.KW_REMOVE):
            self._advance()
            self._skip_newlines()
            remove_terms.append(self._parse_compound())
            while self._at(TokenType.COMMA):
                self._advance()
                self._skip_newlines()
                remove_terms.append(self._parse_compound())
            self._skip_newlines()

        # Validate: at least one of add/remove must be non-empty
        if not add_terms and not remove_terms:
            raise self._error("production rule must have at least one 'додати' or 'видалити' clause")

        # Parse optional коли guard
        if self._at(TokenType.KW_WHEN):
            self._advance()
            self._skip_newlines()
            guard = self._parse_goal()
            self._skip_newlines()

        self._expect(TokenType.DOT)
        return ProductionRuleDef(
            name=name, condition=condition,
            add=add_terms, remove=remove_terms, guard=guard,
        )

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
        """Parse: compound | negation | comparison (with arithmetic expressions)."""
        self._skip_newlines()

        # Negation: не compound
        if self._at(TokenType.KW_NOT):
            self._advance()
            inner = self._parse_compound()
            if not isinstance(inner, Compound):
                raise self._error("negation requires a compound term")
            return Negation(inner=inner)

        # Try to parse an expression (which may be a simple term or arithmetic)
        left = self._parse_expression()

        # Check for comparison operator
        if self._at(*COMPARISON_OPS.keys()):
            op_tok = self._advance()
            op = COMPARISON_OPS[op_tok.type]
            right = self._parse_expression()
            return Comparison(left=left, op=op, right=right)

        # Must be a compound goal (no arithmetic in non-comparison context)
        if not isinstance(left, Compound):
            raise self._error("goal must be a compound term, comparison, or negation")
        return left

    # -- arithmetic expression parsing (for comparison goals) --

    def _parse_expression(self) -> Term:
        """Parse: term_add { ('+' | '-') term_add }. Left-associative."""
        left = self._parse_term_mul()
        while self._at(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_tok = self._advance()
            right = self._parse_term_mul()
            left = Compound(functor=op_tok.value, args=(left, right))
        return left

    def _parse_term_mul(self) -> Term:
        """Parse: factor { ('*' | '/') factor }. Left-associative."""
        left = self._parse_factor()
        while self._at(TokenType.OP_STAR, TokenType.OP_SLASH):
            op_tok = self._advance()
            right = self._parse_factor()
            left = Compound(functor=op_tok.value, args=(left, right))
        return left

    def _parse_factor(self) -> Term:
        """Parse: '-' factor | primary."""
        if self._at(TokenType.OP_MINUS):
            self._advance()
            inner = self._parse_factor()
            return Compound(functor="-", args=(inner,))
        return self._parse_primary()

    def _parse_primary(self) -> Term:
        """Parse: number | var | compound_call | '(' expression ')' | atom."""
        if self._at(TokenType.LPAREN):
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        # Function call in expression: IDENT '(' expression {',' expression} ')'
        if self._at(TokenType.IDENT):
            tok = self._current()
            if (self.pos + 1 < len(self.tokens)
                    and self.tokens[self.pos + 1].type == TokenType.LPAREN):
                self._advance()  # consume IDENT
                self._advance()  # consume (
                args: list[Term] = []
                if not self._at(TokenType.RPAREN):
                    args.append(self._parse_expression())
                    while self._at(TokenType.COMMA):
                        self._advance()
                        args.append(self._parse_expression())
                self._expect(TokenType.RPAREN)
                return Compound(functor=tok.value, args=tuple(args))

        return self._parse_term()

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
