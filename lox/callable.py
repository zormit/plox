from __future__ import annotations
from attrs import define, Factory
from .stmt import Function
from .environment import Environment
from .error import LoxRuntimeError
from .token import Token


@define
class LoxCallable:
    def arity(self) -> int:
        raise NotImplemented

    def call(self, interpreter, arguments: list[object]) -> object:
        raise NotImplemented


@define
class LoxFunction(LoxCallable):
    _declaration: Function
    _closure: Environment
    _is_initializer: bool

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment = Environment(self._closure)
        environment.define("this", instance)
        return LoxFunction(self._declaration, environment, self._is_initializer)

    def arity(self) -> int:
        return len(self._declaration.parameters)

    def call(self, interpreter, arguments: list[object]) -> object:
        environment = Environment(self._closure)
        for i, parameter in enumerate(self._declaration.parameters):
            environment.define(parameter.lexeme, arguments[i])

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except interpreter.RuntimeReturn as return_value:
            if self._is_initializer:
                return self._closure.get_at(0, "this")
            return return_value.value
        if self._is_initializer:
            return self._closure.get_at(0, "this")
        return None

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"


@define
class LoxClass(LoxCallable):
    name: str
    methods: dict[str, LoxFunction]

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interpreter, arguments: list[object]) -> object:
        instance = LoxInstance(self)
        if initializer := self.find_method("init"):
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def find_method(self, name: str) -> LoxFunction | None:
        return self.methods.get(name)

    def __str__(self) -> str:
        return self.name


@define
class LoxInstance:
    klass: LoxClass
    _fields: dict[str, object] = Factory(dict)

    def get(self, name: Token) -> object:
        if name.lexeme in self._fields:
            return self._fields[name.lexeme]
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: object) -> None:
        self._fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"{self.klass.name} instance"
