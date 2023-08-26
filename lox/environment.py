from attrs import define, Factory
from .error import LoxRuntimeError
from .token import Token


@define
class Environment:
    _values: dict[str, object] = Factory(dict)

    def get(self, name: Token) -> object:
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: str, value: object) -> None:
        self._values[name] = value
