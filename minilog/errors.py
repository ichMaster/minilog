"""Error hierarchy for minilog."""


class MinilogError(Exception):
    """Root error for all minilog exceptions."""

    def __init__(self, *args: object, line: int | None = None,
                 col: int | None = None, message: str | None = None) -> None:
        if args and isinstance(args[0], int):
            # Positional form: (line, col, message)
            self.line: int | None = args[0]
            self.col: int | None = args[1] if len(args) > 1 else None
            self.message: str = str(args[2]) if len(args) > 2 else ""
        elif args and isinstance(args[0], str):
            # Positional form: (message,)
            self.line = line
            self.col = col
            self.message = args[0]
        else:
            self.line = line
            self.col = col
            self.message = message or ""
        super().__init__(self.message)

    def __str__(self) -> str:
        name = type(self).__name__
        if self.line is not None and self.col is not None:
            return f"{name} at line {self.line}, col {self.col}: {self.message}"
        return f"{name}: {self.message}"


class LexError(MinilogError):
    """Raised when the lexer encounters invalid input."""


class ParseError(MinilogError):
    """Raised when the parser encounters a syntax error."""


class UnifyError(MinilogError):
    """Raised on unification failures."""


class SolveError(MinilogError):
    """Raised during query solving."""


class EvaluatorError(MinilogError):
    """Raised during arithmetic evaluation."""
