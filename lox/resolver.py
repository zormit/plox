from attrs import define, Factory
from typing import TypeGuard, Callable
from .callable import LoxCallable, LoxFunction
from .environment import Environment
from .error import LoxRuntimeError, error_handler
from .expr import *
from .interpreter import Interpreter
from .stmt import *
from .token import Token
from .token_type import *


@define
class Resolver:
    _interpreter: Interpreter
    _scopes: list[dict[str, bool]]

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()

    def resolve(self, statements: list[Stmt]) -> None:
        map(self._resolve, statements)

    def _resolve(self, node: Stmt | Expr) -> None:
        node.visit(self)

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return
        scope = self._scopes[-1]
        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return
        self._scopes[-1][name.lexeme] = True

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        for depth, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope:
                self._interpreter.resolve(expr, depth)
                return

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._resolve(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        self._begin_scope()
        for param in stmt.parameters:
            self._declare(param)
            self._define(param)
        self.resolve(stmt.body)
        self._end_scope()

    def visit_if_stmt(self, stmt: If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.then_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self._resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if stmt.value is not None:
            self._resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_while_stmt(self, stmt: While) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_assign_expr(self, expr: Assign) -> None:
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Binary) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        self._resolve(expr.callee)
        map(self._resolve, expr.arguments)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self._resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> None:
        return

    def visit_logical_expr(self, expr: Logical) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_unary_expr(self, expr: Unary) -> None:
        self._resolve(expr.right)

    def visit_variable_expr(self, expr: Variable) -> None:
        if (len(self._scopes) > 0) and (not self._scopes[-1][expr.name.lexeme]):
            error_handler.token_error(
                expr.name, "Can't read local variable in its own initializer."
            )
        self._resolve_local(expr, expr.name)