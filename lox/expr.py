from attrs import define
from .token import Token

_grammar = {
    # fmt: off
    # "Assign"   : "Token name, Expr value",
    "Binary"   : "Expr left, Token operator, Expr right",
    # "Call"     : "Expr callee, Token paren, List<Expr> arguments",
    # "Get"      : "Expr object, Token name",
    "Grouping" : "Expr expression",
    "Literal"  : "Object value",
    # "Logical"  : "Expr left, Token operator, Expr right",
    # "Set"      : "Expr object, Token name, Expr value",
    # "Super"    : "Token keyword, Token method",
    # "This"     : "Token keyword",
    "Unary"    : "Token operator, Expr right",
    # "Variable" : "Token name"
    # fmt: on
}


@define
class Expr:
    # TODO: make abstract method? How to define this interface?
    def visit(self, visitor):
        pass


@define
class Assign(Expr):
    name: Token
    value: Expr

    def visit(self, visitor):
        return visitor.visit_assign_expr(self)


@define
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def visit(self, visitor):
        return visitor.visit_binary_expr(self)


@define
class Grouping(Expr):
    expression: Expr

    def visit(self, visitor):
        return visitor.visit_grouping_expr(self)


@define
class Literal(Expr):
    # TODO: refine this to what we'd expect (float, bool, str, None)
    value: object

    def visit(self, visitor):
        return visitor.visit_literal_expr(self)


@define
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def visit(self, visitor):
        return visitor.visit_logical_expr(self)


@define
class Unary(Expr):
    operator: Token
    right: Expr

    def visit(self, visitor):
        return visitor.visit_unary_expr(self)


@define
class Variable(Expr):
    name: Token

    def visit(self, visitor):
        return visitor.visit_variable_expr(self)
