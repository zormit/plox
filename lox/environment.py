from __future__ import annotations
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

    def ancestor(self, distance: int) -> Environment:
        environment = self
        for _ in range(distance):
            # TODO: is this somehow guaranteed? what if not?
            if environment.enclosing is not None:
                environment = environment.enclosing
        return environment

    def get_at(self, distance: int, name: str) -> object:
        return self.ancestor(distance)._values[name]

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self.ancestor(distance)._values[name.lexeme] = value
