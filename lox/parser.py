from attrs import define, Factory
from typing import List, Optional
from .expr import *
from .token import Token
from .token_type import *


@define
class Parser:
    tokens: List[Token] = Factory(list)
    _current: int = 0

    class ParseError(RuntimeError):
        pass

    def parse(self) -> Optional[Expr]:
        try:
            return self._expression()
        except self.ParseError:
            return None

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(BANG_EQUAL, EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(GREATER, GREATER_EQUAL, LESS, LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(MINUS, PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(SLASH, STAR):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)
        return expr

    def _unary(self) -> Expr:
        if self._match(BANG, MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match(FALSE):
            return Literal(False)
        if self._match(TRUE):
            return Literal(True)
        if self._match(NIL):
            return Literal(None)

        if self._match(NUMBER, STRING):
            return Literal(self._previous().literal)

        if self._match(LEFT_PAREN):
            expr = self._expression()
            self._consume(RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _error(self, token: Token, message: str) -> ParseError:
        from .error import error_handler

        error_handler.token_error(token, message)
        return self.ParseError()

    def _synchronize(self) -> None:
        self._advance()
        while not self._at_end():
            if self._previous().token_type == SEMICOLON:
                return
            sychronization_points = {CLASS, FUN, VAR, FOR, IF, WHILE, PRINT, RETURN}
            if self._peek().token_type in sychronization_points:
                return
            self._advance()

    # TODO: typing of flexible number of args?
    # (should all be of type TokenType)
    def _match(self, *token_types) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._at_end():
            return False
        return self._peek().token_type == token_type

    def _advance(self) -> Token:
        if not self._at_end():
            self._current += 1
        return self._previous()

    def _at_end(self) -> bool:
        return self._peek().token_type == EOF

    def _peek(self) -> Token:
        return self.tokens[self._current]

    def _previous(self) -> Token:
        assert (
            self._current > 0
        ), "[parser] can't access previous token without advancing"
        return self.tokens[self._current - 1]
