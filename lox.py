# TODO: add command line arguments to also run a file.
from enum import Enum
from attrs import asdict, define, make_class, Factory
from typing import List

TokenType = Enum('TokenType',
'LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMICOLON SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF')

print(TokenType)
print(TokenType.LEFT_PAREN)

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

    def scan_tokens(self) -> List[Token]:
        while(not self.at_end()):
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF,"",None, self.line))
        return self.tokens

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    # TODO: use generator! how does it work again?
    def advance(self) -> str:
        c = self.source[self.current]
        self.current+=1
        return c

    def add_token(self, token_type: TokenType, literal: object = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case '(':
                # TODO: can we make LEFT_PAREN global?
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)

def run(source: str) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    print(tokens)



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
