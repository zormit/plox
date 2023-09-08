from attrs import define
from .stmt import Function
from .environment import Environment


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

    def arity(self) -> int:
        return len(self._declaration.parameters)

    def call(self, interpreter, arguments: list[object]) -> object:
        environment = Environment(self._closure)
        for i, parameter in enumerate(self._declaration.parameters):
            environment.define(parameter.lexeme, arguments[i])

        try:
            interpreter.execute_block(self._declaration.body, environment)
        except interpreter.RuntimeReturn as return_value:
            return return_value.value
        return None

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"
