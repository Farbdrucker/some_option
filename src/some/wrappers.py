from functools import wraps
from typing import Any, Type, Callable

from some.options import (
    Some,
    SomeFnType,
    LazySome,
    LazySomeFnType,
    LazyDAGSome,
    LazyDAGSomeFnType,
)
from some.types import UnwrapOr, FnType, Option, UnwrapOrFnType


def evaluate_arg(value: Any, type_: Type[UnwrapOr]) -> Any:
    if isinstance(value, type_):
        return value.unwrap()
    return value


def safe(fn: FnType) -> SomeFnType:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        evaluated_args = [evaluate_arg(arg, Some) for arg in args]
        evaluated_kwargs = {k: evaluate_arg(v, Some) for k, v in kwargs.items()}

        try:
            return Some.ok(fn(*evaluated_args, **evaluated_kwargs))
        except Exception as e:
            return Some.error(e)

    return wrapper


def lazy(fn: FnType) -> LazySomeFnType:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        def compute():
            evaluated_args = [evaluate_arg(arg, LazySome) for arg in args]
            evaluated_kwargs = {k: evaluate_arg(v, LazySome) for k, v in kwargs.items()}
            return fn(*evaluated_args, **evaluated_kwargs)

        return LazySome(compute)

    return wrapper


def lazy_dag(fn: FnType) -> LazyDAGSomeFnType:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        dependencies = set()
        for arg in args:
            if isinstance(arg, LazyDAGSome):
                dependencies.add(arg)
        for arg in kwargs.values():
            if isinstance(arg, LazyDAGSome):
                dependencies.add(arg)

        def compute():
            evaluated_args = [evaluate_arg(arg, LazyDAGSome) for arg in args]
            evaluated_kwargs = {
                k: evaluate_arg(v, LazyDAGSome) for k, v in kwargs.items()
            }
            return fn(*evaluated_args, **evaluated_kwargs)

        return LazyDAGSome(compute, dependencies=dependencies, name=fn.__name__)

    return wrapper


def some_type(type_: Type[UnwrapOr]) -> Callable[[FnType], UnwrapOrFnType]:
    if type_ is Some:
        return safe
    elif type_ is LazySome:
        return lazy
    elif type_ is LazyDAGSome:
        return lazy_dag
    else:
        raise ValueError(f"Unknown type: {type_}")


def some_enum(type_: Option) -> Callable[[FnType], UnwrapOrFnType]:
    if type_ is Option.Some:
        return some_type(Some)
    elif type_ is Option.LazySome:
        return some_type(LazySome)
    elif type_ is Option.LazyDAGSome:
        return some_type(LazyDAGSome)
    else:
        raise ValueError(f"Unknown type: {type_}")


def some(t: Type[UnwrapOr] | Option) -> Callable[[FnType], UnwrapOrFnType]:
    if isinstance(t, Option):
        return some_enum(t)
    elif issubclass(t, UnwrapOr):
        return some_type(t)
    else:
        raise ValueError(f"Unknown type: {t}")
