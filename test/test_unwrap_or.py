import pytest

from conftest import add, sub

from some import some, Option

some_wrapper = some(Option.Some)

some_add = some_wrapper(add)
some_sub = some_wrapper(sub)


def test_some_unwrap():
    add_1_2 = some_add(1, 2)
    assert add_1_2.unwrap() == 3

    add_some_2 = some_add(add_1_2, 2)
    assert add_some_2.unwrap() == 5

    assert some_add(some_add(2, 2), some_add(3, 3)).unwrap() == 10


def test_some_unwrap_or():
    add_1_2 = some_add(1, 2)
    assert add_1_2.unwrap_or(0) == 3

    assert some_add(some_add(2, 2), None).unwrap_or(0) == 0

    with pytest.raises(TypeError):
        some_add(None, 0).unwrap()

