# TODO: add command line arguments to also run a file.
from enum import Enum
from attrs import asdict, define, make_class, Factory
from typing import List

TokenType = Enum(
    "TokenType",
    "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMICOLON SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF",
)
hadError = False


@define
class Token:
    token_type: TokenType
    lexeme: str
    literal: object
    line: int


@define
class Scanner:
    source: str
    tokens: List[Token] = Factory(list)
    start: int = 0
    current: int = 0
    line: int = 1

    _keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def scan_tokens(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    # TODO: use generator! how does it work again?
    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def match(self, expected):
        if self.at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def add_token(self, token_type: TokenType, literal: object = None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def discard_line(self):
        while self.peek() != "\n" and not self.at_end():
            self.advance()

    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                if self.match("="):
                    self.add_token(TokenType.BANG_EQUAL)
                else:
                    self.add_token(TokenType.BANG)
            case "=":
                if self.match("="):
                    self.add_token(TokenType.EQUAL_EQUAL)
                else:
                    self.add_token(TokenType.EQUAL)
            case "<":
                if self.match("="):
                    self.add_token(TokenType.LESS_EQUAL)
                else:
                    self.add_token(TokenType.LESS)
            case ">":
                if self.match("="):
                    self.add_token(TokenType.GREATER_EQUAL)
                else:
                    self.add_token(TokenType.GREATER)
            case "/":
                if self.match("/"):
                    self.discard_line()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                # Ignore whitespace
                pass
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    error(self.line, "Unexpected character.")

    def is_digit(self, c):
        return c in set("0123456789")

    def is_alpha(self, c):
        return c in set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")

    def identifier(self) -> None:
        while self.is_alpha(self.peek()):
            self.advance()
        text = self.source[self.start : self.current]
        token_type = self._keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def string(self) -> None:
        while self.peek() != '"' and not self.at_end():
            if self.peek() == "\n":
                line += 1
            self.advance()

        if self.at_end():
            error(self.line, "Unterminated string.")
            return

        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
        while self.is_digit(self.peek()):
            self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))


def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    print(tokens)
    if hadError:
        sys.exit(65)


def error(line: int, message: str, where: str = ""):
    print(f"[line {line}] Error{where}: {message}")
    hadError = True


def runPrompt():
    while True:
        print("> ", end="")
        try:
            line = input()
        except EOFError:
            break
        run(line)


def main():
    runPrompt()


if __name__ == "__main__":
    main()
