from enum import Enum

TokenType = Enum(
    "TokenType",
    [
        "LEFT_PAREN",
        "RIGHT_PAREN",
        "LEFT_BRACE",
        "RIGHT_BRACE",
        "LEFT_TAG",
        "RIGHT_TAG",
        "COMMA",
        "DOT",
        "MINUS",
        "PLUS",
        "SEMICOLON",
        "SLASH",
        "STAR",
        "BANG",
        "BANG_EQUAL",
        "EQUAL",
        "EQUAL_EQUAL",
        "GREATER",
        "GREATER_EQUAL",
        "LESS",
        "LESS_EQUAL",
        "IDENTIFIER",
        "STRING",
        "NUMBER",
        "AND",
        "CLASS",
        "ELSE",
        "FALSE",
        "FUN",
        "FOR",
        "IF",
        "NIL",
        "OR",
        "PRINT",
        "RETURN",
        "SUPER",
        "THIS",
        "TRUE",
        "VAR",
        "WHILE",
        "EOF",
        "WINK",
        "MAYBE",
        "PLEASE",
        "PRETTYPLEASE",
    ],
)

# this is to make mypy detect the globals :D
LEFT_PAREN: TokenType
RIGHT_PAREN: TokenType
LEFT_BRACE: TokenType
RIGHT_BRACE: TokenType
LEFT_TAG: TokenType
RIGHT_TAG: TokenType
COMMA: TokenType
DOT: TokenType
MINUS: TokenType
PLUS: TokenType
SEMICOLON: TokenType
SLASH: TokenType
STAR: TokenType
BANG: TokenType
BANG_EQUAL: TokenType
EQUAL: TokenType
EQUAL_EQUAL: TokenType
GREATER: TokenType
GREATER_EQUAL: TokenType
LESS: TokenType
LESS_EQUAL: TokenType
IDENTIFIER: TokenType
STRING: TokenType
NUMBER: TokenType
AND: TokenType
CLASS: TokenType
ELSE: TokenType
FALSE: TokenType
FUN: TokenType
FOR: TokenType
IF: TokenType
NIL: TokenType
OR: TokenType
PRINT: TokenType
RETURN: TokenType
SUPER: TokenType
THIS: TokenType
TRUE: TokenType
VAR: TokenType
WHILE: TokenType
EOF: TokenType
WINK: TokenType
MAYBE: TokenType
PLEASE: TokenType
PRETTYPLEASE: TokenType
globals().update({token_type.name: token_type for token_type in TokenType})
