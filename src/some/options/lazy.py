from __future__ import annotations

from typing import Optional, Callable, Any

from some.types import UnwrapOr, FnType, T, Status


class LazySome(UnwrapOr[T]):
    def __init__(self, fn: FnType[T]):
        self._fn = fn
        self._status = Status.PENDING
        self._value: Optional[T] = None
        self._error: Optional[Exception] = None

    def _evaluate(self) -> Optional[T]:
        if self._status == Status.PENDING:
            try:
                self._value = self._fn()
                self._status = Status.OK
            except Exception as e:
                self._error = e
                self._status = Status.ERROR
        return self._value

    def map(self, fn: Callable[[T], Any]) -> LazySome[Any]:
        def _fn():
            result = self.unwrap()
            return fn(result)

        return LazySome(_fn)

    def unwrap(self) -> T:
        self._evaluate()

        if self._status == Status.OK:
            return self._value
        elif self._status == Status.ERROR:
            raise self._error

    def unwrap_or(self, default: T) -> T:
        self._evaluate()
        if self._status == Status.OK:
            return self._value
        else:
            return default

    def __repr__(self):
        state_str = f"{self._status.value.lower().capitalize()}"
        if self._status == Status.OK:
            value_str = f"{self._value}"
        elif self._status == Status.ERROR:
            value_str = f"{self._error}"
        elif self._status == Status.PENDING:
            value_str = f"<pending>"
        else:
            raise ValueError(f"Unknown status: {self._status}")
        return f"Some{state_str}({value_str})"


LazySomeFnType = Callable[..., LazySome[T]]
