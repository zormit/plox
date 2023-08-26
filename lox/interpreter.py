from attrs import define, Factory
from typing import TypeGuard, Callable
from .environment import Environment
from .error import LoxRuntimeError, error_handler
from .expr import *
from .stmt import Stmt, Expression, Print, Var
from .token import Token
from .token_type import *
from .token_type import GREATER


@define
class Interpreter:
    _environment: Environment = Factory(lambda: Environment())

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

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self._environment.define(stmt.name.lexeme, value)

    def visit_assign_expr(self, expr: Assign) -> object:
        value = self.evaluate(expr.value)
        self._environment.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        if expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

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
        if expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise LoxRuntimeError(
                expr.operator, "Operands must be two numbers or two strings."
            )
        if self.ensure_float([left, right], expr.operator):
            return operations[expr.operator.token_type](left, right)
        return None

    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if isinstance(a, bool) and isinstance(b, bool):
            return a == b
        if isinstance(a, float) and isinstance(b, float):
            return a == b
        if isinstance(a, str) and isinstance(b, str):
            return a == b
        return False

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

    def visit_variable_expr(self, expr: Variable) -> object:
        return self._environment.get(expr.name)

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
        expected = "a number" if len(operands) == 1 else "numbers"
        raise LoxRuntimeError(operator, f"{label} must be {expected}.")
