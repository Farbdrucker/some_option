SomeOption
===

Fun afternoon project inspired by `rust`s `Some` type.

```python
from some import some, Option

@some(Option.Some)
def add(a, b):
    return a + b

result = add(1, 2)
print(result.unwrap())  # 3

result = add(None, 2)

try:
    result.unwrap()  # TypeError
except TypeError:
    print(result)
    
result.unwrap_or(0)  # 0

result = add(add(1, 2), 2)
print(result.unwrap())  # 5
```

# Install
- [install](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) `uv`

# Build
```bash
uv run python -m build
```