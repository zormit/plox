from . import expr
from .scanner import Token
from .token_type import *


class AstPrinter:
    def visit_binary_expr(self, expr):
        left = expr.left.visit(self)
        right = expr.right.visit(self)
        return f"({expr.operator.lexeme} {left} {right})"

    def visit_grouping_expr(self, expr):
        expression = expr.expression.visit(self)
        return f"(group {expression})"

    def visit_literal_expr(self, expr):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        right = expr.right.visit(self)
        return f"({expr.operator.lexeme} {right})"

    def print(self, expr):
        print(expr.visit(self))


if __name__ == "__main__":
    expression = expr.Binary(
        expr.Unary(Token(MINUS, "-", None, 1), expr.Literal(123)),
        Token(STAR, "*", None, 1),
        expr.Grouping(expr.Literal(45.67)),
    )
    AstPrinter().print(expression)
