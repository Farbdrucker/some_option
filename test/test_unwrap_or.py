import pytest

from conftest import add

from some import some, Option


@pytest.mark.parametrize("t", (Option.Some, Option.LazySome, Option.LazyDAGSome))
def test_some_unwrap_or(t):
    wrapper = some(t)

    add_ = wrapper(add)

    add_1_2 = add_(1, 2)
    assert add_1_2.unwrap() == 3

    add_some_2 = add_(add_1_2, 2)
    assert add_some_2.unwrap() == 5

    assert add_(add_(2, 2), add_(3, 3)).unwrap() == 10

    add_1_2 = add_(1, 2)
    assert add_1_2.unwrap_or(0) == 3

    assert add_(add_(2, 2), None).unwrap_or(0) == 0

    with pytest.raises(TypeError):
        add_(None, 0).unwrap()
