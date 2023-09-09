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
class LoxClass(LoxCallable):
    name: str

    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: list[object]) -> object:
        return LoxInstance(self)

    def __str__(self) -> str:
        return self.name


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


@define
class LoxInstance:
    klass: LoxClass
    _fields: dict[str, object] = Factory(dict)

    def get(self, name: Token) -> object:
        try:
            return self._fields[name.lexeme]
        except KeyError:
            raise LoxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def set(self, name: Token, value: object) -> None:
        self._fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"{self.klass.name} instance"
