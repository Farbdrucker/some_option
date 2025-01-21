from abc import abstractmethod
from enum import StrEnum
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Status(StrEnum):
    OK = "OK"
    ERROR = "ERROR"
    PENDING = "PENDING"


class Error:
    def __init__(self, e: Exception):
        self._error = e

    def __repr__(self):
        return f"Error: {self._error}"


class UnwrapOr(Generic[T]):
    @abstractmethod
    def unwrap(self) -> T: ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...


FnType = Callable[..., T]

UnwrapOrFnType = Callable[..., UnwrapOr[T]]


class Option(StrEnum):
    Some = "Some"
    LazySome = "LazySome"
    LazyDAGSome = "LazyDAGSome"
