from attrs import define
from .token_type import TokenType


@define(frozen=True, eq=False)
class Token:
    token_type: TokenType
    lexeme: str
    literal: object
    line: int
