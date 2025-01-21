from __future__ import annotations

from typing import Optional, Callable

from some.types import UnwrapOr, T, Status, FnType


class Some(UnwrapOr[T]):
    def __init__(self, value: T, state: Status, _error: Optional[Exception] = None):
        self._value = value
        self._status = state
        self._error = _error

    def unwrap(self) -> T:
        if self._status == Status.OK:
            return self._value
        elif self._status == Status.ERROR:
            raise self._error

    def unwrap_or(self, default: T) -> T:
        if self._status == Status.OK:
            return self._value
        else:
            return default

    @classmethod
    def error(cls, error: Exception) -> Some[T]:
        return Some(None, Status.ERROR, error)

    @classmethod
    def ok(cls, value: T) -> Some[T]:
        return Some(value, Status.OK)

    def __repr__(self):
        value_str = f"{self._value}" if self._status == Status.OK else f"{self._error}"
        state_str = f"{self._status.value.lower().capitalize()}"
        return f"Some{state_str}({value_str})"

    def __bool__(self):
        return self._status == Status.OK


SomeFnType = Callable[..., Some[T]]
