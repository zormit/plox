from attrs import define
from .token import Token
from .token_type import EOF


@define
class ErrorHandler:
    had_error: bool = False

    def error(self, line: int, message: str, where: str = ""):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True

    def token_error(self, token: Token, message: str):
        if token.token_type == EOF:
            self.error(token.line, message, where=" at end")
        else:
            self.error(token.line, message, where=f" at '{token.lexeme}'")


# singleton for globally tracking whether error occurred
error_handler = ErrorHandler()
