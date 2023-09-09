from attrs import define
from .token import Token


@define(frozen=True)
class Expr:
    # TODO: make abstract method? How to define this interface?
    def visit(self, visitor):
        raise NotImplemented


@define(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr

    def visit(self, visitor):
        return visitor.visit_assign_expr(self)


@define(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def visit(self, visitor):
        return visitor.visit_binary_expr(self)


@define(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def visit(self, visitor):
        return visitor.visit_call_expr(self)


@define(frozen=True)
class Get(Expr):
    expr_object: Expr
    name: Token

    def visit(self, visitor):
        return visitor.visit_get_expr(self)


@define(frozen=True)
class Grouping(Expr):
    expression: Expr

    def visit(self, visitor):
        return visitor.visit_grouping_expr(self)


@define(frozen=True)
class Literal(Expr):
    # TODO: refine this to what we'd expect (float, bool, str, None)
    value: object

    def visit(self, visitor):
        return visitor.visit_literal_expr(self)


@define(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def visit(self, visitor):
        return visitor.visit_logical_expr(self)


@define(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def visit(self, visitor):
        return visitor.visit_unary_expr(self)


@define(frozen=True)
class Variable(Expr):
    name: Token

    def visit(self, visitor):
        return visitor.visit_variable_expr(self)
