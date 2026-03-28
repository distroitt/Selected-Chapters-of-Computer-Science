from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def task_screen(title: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            line = "=" * 72
            print(f"\n{line}\n{title}\n{line}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
