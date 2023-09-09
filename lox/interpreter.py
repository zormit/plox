from __future__ import annotations
from attrs import define, Factory
from typing import TypeGuard, Callable
from .callable import LoxCallable, LoxFunction, LoxClass, LoxInstance
from .environment import Environment
from .error import LoxRuntimeError, error_handler
from .expr import *
from .stmt import *
from .token import Token
from .token_type import *
from .token_type import GREATER


@define
class Interpreter:
    global_env: Environment = Factory(lambda: Environment())
    _environment: Environment | None = None
    _locals: dict[Expr, int] = Factory(dict)

    @define
    class RuntimeReturn(RuntimeError):
        value: object

    def __attrs_post_init__(self):
        self._environment = self.global_env

    @classmethod
    def with_time(cls) -> Interpreter:
        import time

        interpreter = Interpreter()

        @define
        class Clock(LoxCallable):
            def arity(self):
                return 0

            def call(self, interpreter, arguments):
                # TODO: make this compatible with the base impl of Lox
                return time.time()

            def __str__(self):
                return "<native fn>"

        interpreter.global_env.define("clock", Clock())
        return interpreter

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            error_handler.runtime_error(e)

    def execute(self, stmt: Stmt):
        return stmt.visit(self)

    def resolve(self, expr: Expr, depth: int):
        self._locals[expr] = depth

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

    def visit_block_stmt(self, stmt: Block) -> None:
        # TODO: gnah, mypy makes me go mad!
        self.execute_block(stmt.statements, Environment(self._environment))

    def visit_class_stmt(self, stmt: Class) -> None:
        self._environment.define(stmt.name.lexeme, None)
        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self._environment, is_initializer)
            methods[method.name.lexeme] = function
        klass = LoxClass(stmt.name.lexeme, methods)
        self._environment.assign(stmt.name, klass)

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self._environment = previous

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        function = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: If) -> None:
        condition = self.evaluate(stmt.condition)
        if self.truthy(condition):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt: Return) -> None:
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise self.RuntimeReturn(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self._environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self.truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Assign) -> object:
        value = self.evaluate(expr.value)
        distance = self._locals.get(expr)
        if distance is not None:
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.global_env.assign(expr.name, value)
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

    def visit_call_expr(self, expr: Call):
        callee = self.evaluate(expr.callee)

        arguments: list[object] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if isinstance(callee, LoxCallable):
            function = callee
            if len(arguments) != function.arity():
                raise LoxRuntimeError(
                    expr.paren,
                    f"Expected {function.arity()} arguments but got {len(arguments)}.",
                )
            return function.call(self, arguments)
        else:
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

    def visit_get_expr(self, expr: Get):
        obj = self.evaluate(expr.expr_object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

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

    def visit_logical_expr(self, expr: Logical) -> object:
        left = self.evaluate(expr.left)
        if expr.operator.token_type == OR:
            if self.truthy(left):
                return left
        else:
            if not self.truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_set_expr(self, expr: Set) -> object:
        obj = self.evaluate(expr.expr_object)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_this_expr(self, expr: This) -> object:
        return self._lookup_variable(expr.keyword, expr)

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
        return self._lookup_variable(expr.name, expr)

    def _lookup_variable(self, name: Token, expr: Expr) -> object:
        distance = self._locals.get(expr)
        if distance is not None and self._environment is not None:
            return self._environment.get_at(distance, name.lexeme)
        return self.global_env.get(name)

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
