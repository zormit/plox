from attrs import define
from typing import Optional
from .expr import Expr
from .token import Token


@define(frozen=True)
class Stmt:
    # TODO: make abstract method? How to define this interface?
    def visit(self, visitor):
        pass


@define(frozen=True)
class Block(Stmt):
    statements: list[Stmt]

    def visit(self, visitor):
        visitor.visit_block_stmt(self)


@define(frozen=True)
class Expression(Stmt):
    expression: Expr

    def visit(self, visitor):
        visitor.visit_expression_stmt(self)


@define(frozen=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def visit(self, visitor):
        visitor.visit_if_stmt(self)


@define(frozen=True)
class Function(Stmt):
    name: Token
    parameters: list[Token]
    body: list[Stmt]

    def visit(self, visitor):
        visitor.visit_function_stmt(self)


@define(frozen=True)
class Class(Stmt):
    name: Token
    methods: list[Function]

    def visit(self, visitor):
        visitor.visit_class_stmt(self)


@define(frozen=True)
class Print(Stmt):
    expression: Expr

    def visit(self, visitor):
        visitor.visit_print_stmt(self)


@define(frozen=True)
class Return(Stmt):
    keyword: Token
    value: Expr | None

    def visit(self, visitor):
        visitor.visit_return_stmt(self)


@define(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Optional[Expr]

    def visit(self, visitor):
        visitor.visit_var_stmt(self)


@define(frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt

    def visit(self, visitor):
        visitor.visit_while_stmt(self)


@define(frozen=True)
class Nop(Stmt):
    def visit(self, visitor):
        visitor.visit_nop_stmt(self)
