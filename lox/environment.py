from attrs import define, Factory
from typing import Optional, Self
from .error import LoxRuntimeError
from .token import Token


@define
class Environment:
    # TODO: understand what is going on here on typesystem level https://stackoverflow.com/a/74586625
    enclosing: Optional[Self] = None
    _values: dict[str, object] = Factory(dict)

    def get(self, name: Token) -> object:
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: str, value: object) -> None:
        self._values[name] = value
