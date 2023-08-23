from attrs import define, Factory
from typing import List
from .token_type import *
from .token import Token


@define
class Scanner:
    source: str
    tokens: List[Token] = Factory(list)
    start: int = 0
    current: int = 0
    line: int = 1

    _keywords = {
        "and": AND,
        "class": CLASS,
        "else": ELSE,
        "false": FALSE,
        "for": FOR,
        "fun": FUN,
        "if": IF,
        "nil": NIL,
        "or": OR,
        "print": PRINT,
        "return": RETURN,
        "super": SUPER,
        "this": THIS,
        "true": TRUE,
        "var": VAR,
        "while": WHILE,
    }

    def scan_tokens(self) -> List[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(EOF, "", None, self.line))
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
                self.add_token(LEFT_PAREN)
            case ")":
                self.add_token(RIGHT_PAREN)
            case "{":
                self.add_token(LEFT_BRACE)
            case "}":
                self.add_token(RIGHT_BRACE)
            case ",":
                self.add_token(COMMA)
            case ".":
                self.add_token(DOT)
            case "-":
                self.add_token(MINUS)
            case "+":
                self.add_token(PLUS)
            case ";":
                self.add_token(SEMICOLON)
            case "*":
                self.add_token(STAR)
            case "!":
                if self.match("="):
                    self.add_token(BANG_EQUAL)
                else:
                    self.add_token(BANG)
            case "=":
                if self.match("="):
                    self.add_token(EQUAL_EQUAL)
                else:
                    self.add_token(EQUAL)
            case "<":
                if self.match("="):
                    self.add_token(LESS_EQUAL)
                else:
                    self.add_token(LESS)
            case ">":
                if self.match("="):
                    self.add_token(GREATER_EQUAL)
                else:
                    self.add_token(GREATER)
            case "/":
                if self.match("/"):
                    self.discard_line()
                else:
                    self.add_token(SLASH)
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
        token_type = self._keywords.get(text, IDENTIFIER)
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
        self.add_token(STRING, value)

    def number(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
        while self.is_digit(self.peek()):
            self.advance()
        self.add_token(NUMBER, float(self.source[self.start : self.current]))
