from attrs import define


@define
class LoxCallable:
    def arity(self) -> int:
        raise NotImplemented

    def call(self, interpreter, arguments: list[object]) -> object:
        raise NotImplemented
