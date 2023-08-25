from attrs import define
from .expr import Expr


@define
class Stmt:
    # TODO: make abstract method? How to define this interface?
    def visit(self, visitor):
        pass


@define
class Expression(Stmt):
    expression: Expr

    def visit(self, visitor):
        visitor.visit_expression_stmt(self)


@define
class Print(Stmt):
    expression: Expr

    def visit(self, visitor):
        visitor.visit_print_stmt(self)
