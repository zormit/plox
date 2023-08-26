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

    def define(self, name: str, value: object) -> None:
        self._values[name] = value
