from attrs import define, Factory
from typing import List, Optional
from .expr import *
from .stmt import *
from .token import Token
from .token_type import *


@define
class Parser:
    tokens: List[Token] = Factory(list)
    _current: int = 0

    class ParseError(RuntimeError):
        pass

    def parse(self) -> list[Optional[Stmt]]:
        statements = []
        while not self._at_end():
            statements.append(self._declaration())
        return statements

    def _declaration(self) -> Optional[Stmt]:
        try:
            if self._match(VAR):
                return self._var_declaration()
            return self._statement()
        except self.ParseError:
            self._synchronize()
            return None

    def _statement(self) -> Stmt:
        if self._match(FOR):
            return self._for_statement()
        if self._match(IF):
            return self._if_statement()
        if self._match(PRINT):
            return self._print_statement()
        if self._match(WHILE):
            return self._while_statement()
        if self._match(LEFT_BRACE):
            return Block(self._block())
        return self._expression_statement()

    def _for_statement(self) -> Stmt:
        self._consume(LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Stmt | None
        if self._match(SEMICOLON):
            initializer = None
        elif self._match(VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition = None
        if not self._check(SEMICOLON):
            condition = self._expression()
        self._consume(SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self._check(RIGHT_PAREN):
            increment = self._expression()
        self._consume(RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self._statement()

        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])

        return body

    def _if_statement(self) -> Stmt:
        self._consume(LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self._statement()
        else_branch = None
        if self._match(ELSE):
            else_branch = self._statement()
        return If(condition, then_branch, else_branch)

    def _block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._check(RIGHT_BRACE) and not self._at_end():
            declaration = self._declaration()
            if declaration is not None:
                statements.append(declaration)
        self._consume(RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _print_statement(self) -> Stmt:
        value = self._expression()
        self._consume(SEMICOLON, "Expect ';' after value")
        return Print(value)

    def _expression_statement(self) -> Stmt:
        expr = self._expression()
        self._consume(SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def _var_declaration(self) -> Stmt:
        name = self._consume(IDENTIFIER, "Expect variable name.")
        initializer = None
        if self._match(EQUAL):
            initializer = self._expression()
        self._consume(SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _while_statement(self) -> Stmt:
        self._consume(LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(RIGHT_PAREN, "Expect ')' after condition")
        body = self._statement()
        return While(condition, body)

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._or()
        if self._match(EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr = self._and()
        while self._match(OR):
            operator = self._previous()
            right = self._and()
            expr = Logical(expr, operator, right)
        return expr

    def _and(self) -> Expr:
        expr = self._equality()
        while self._match(AND):
            operator = self._previous()
            right = self._equality()
            expr = Logical(expr, operator, right)
        return expr

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
        return self._call()

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self._check(RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self._expression())
                if self._match(COMMA):
                    break
        paren = self._consume(RIGHT_PAREN, "Expect ')' after arguments")
        return Call(callee, paren, arguments)

    def _call(self) -> Expr:
        expr = self._primary()
        while True:
            if self._match(LEFT_PAREN):
                expr = self._finish_call(expr)
            else:
                break
        return expr

    def _primary(self) -> Expr:
        if self._match(FALSE):
            return Literal(False)
        if self._match(TRUE):
            return Literal(True)
        if self._match(NIL):
            return Literal(None)

        if self._match(NUMBER, STRING):
            return Literal(self._previous().literal)

        if self._match(IDENTIFIER):
            return Variable(self._previous())

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
