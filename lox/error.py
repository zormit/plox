import sys
from attrs import define
from .token import Token
from .token_type import EOF


@define
class LoxRuntimeError(RuntimeError):
    token: Token
    message: str


@define
class ErrorHandler:
    had_error: bool = False
    had_runtime_error: bool = False

    def error(self, line: int, message: str, where: str = ""):
        self.eprint(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def token_error(self, token: Token, message: str):
        if token.token_type == EOF:
            self.error(token.line, message, where=" at end")
        else:
            self.error(token.line, message, where=f" at '{token.lexeme}'")

    def runtime_error(self, error: LoxRuntimeError) -> None:
        self.eprint(error.message)
        self.eprint(f"[line {error.token.line}]")
        self.had_runtime_error = True

    def eprint(self, msg: str):
        print(msg, file=sys.stderr)

    def reset(self):
        self.had_error = False
        self.had_runtime_error = False


# singleton for globally tracking whether error occurred
error_handler = ErrorHandler()
