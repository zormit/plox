from attrs import define
from .token_type import TokenType


@define
class Token:
    token_type: TokenType
    lexeme: str
    literal: object
    line: int
