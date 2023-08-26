from typing import TypeGuard, Callable
from .error import LoxRuntimeError, error_handler
from .expr import *
from .stmt import Stmt, Expression, Print
from .token import Token
from .token_type import *
from .token_type import GREATER


class Interpreter:
    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            error_handler.runtime_error(e)

    def execute(self, stmt: Stmt):
        return stmt.visit(self)

    def evaluate(self, expr: Expr) -> str | float | bool | None:
        return expr.visit(self)

    def stringify(self, value) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float):
            s = str(value)
            if s.endswith(".0"):
                return s[:-2]
            return s
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.BANG_EQUAL:
            return left != right
        if expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return left == right

        operations: dict[TokenType, Callable[[float, float], float]] = {
            TokenType.GREATER: (lambda a, b: a > b),
            TokenType.GREATER_EQUAL: (lambda a, b: a >= b),
            TokenType.LESS: (lambda a, b: a < b),
            TokenType.LESS_EQUAL: (lambda a, b: a <= b),
            TokenType.MINUS: (lambda a, b: a - b),
            TokenType.PLUS: (lambda a, b: a + b),
            TokenType.SLASH: (lambda a, b: a / b),
            TokenType.STAR: (lambda a, b: a * b),
        }
        if self.ensure_float([left, right], expr.operator):
            return operations[expr.operator.token_type](left, right)
        return None

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_unary_expr(self, expr: Unary) -> object:
        right = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.BANG:
                return not self.truthy(right)
            case TokenType.MINUS:
                if self.ensure_float([right], expr.operator):
                    return -right
        return None

    def truthy(self, o: object) -> bool:
        if o is None:
            return False
        if isinstance(o, bool):
            return o
        # slightly different to python:
        # 0 and "" are truthy!
        return True

    def ensure_float(
        self, operands: list[object], operator: Token
    ) -> TypeGuard[list[float]]:
        if all(isinstance(op, float) for op in operands):
            return True
        label = "Operand" if len(operands) == 1 else "Operands"
        raise LoxRuntimeError(operator, f"{label} must be a number")
