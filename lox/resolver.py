from attrs import define, Factory
from enum import Enum
from typing import TypeGuard, Callable
from .callable import LoxCallable, LoxFunction
from .environment import Environment
from .error import LoxRuntimeError, error_handler
from .expr import *
from .interpreter import Interpreter
from .stmt import *
from .token import Token
from .token_type import *


FunctionType = Enum("FunctionType", ["NONE", "FUNCTION"])


@define
class Resolver:
    _interpreter: Interpreter
    _scopes: list[dict[str, bool]] = Factory(list)
    # TODO: do we need factory here? :thinking:
    _current_function: FunctionType = FunctionType.NONE

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()

    def resolve(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self._resolve(statement)

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
        if name.lexeme in scope:
            error_handler.token_error(
                name, "Already a variable with this name in this scope."
            )
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
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def _resolve_function(self, function: Function, function_type: FunctionType):
        enclosing_function = self._current_function
        self._current_function = function_type

        self._begin_scope()
        for param in function.parameters:
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._end_scope()

        self._current_function = enclosing_function

    def visit_if_stmt(self, stmt: If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self._resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if self._current_function == FunctionType.NONE:
            error_handler.token_error(stmt.keyword, "Can't return from top-level code.")

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
        for argument in expr.arguments:
            self._resolve(argument)

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
        if len(self._scopes) > 0 and self._scopes[-1].get(expr.name.lexeme) == False:
            error_handler.token_error(
                expr.name, "Can't read local variable in its own initializer."
            )
        self._resolve_local(expr, expr.name)
