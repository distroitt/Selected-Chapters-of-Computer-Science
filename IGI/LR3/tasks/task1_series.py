from __future__ import annotations

import math

from common.decorators import task_screen
from common.input_utils import read_float


def compute_series_value(x: float, eps: float, max_iterations: int = 500) -> tuple[float, int]:
    term = 2 / x
    total = 0.0

    for index in range(max_iterations):
        total += term
        if abs(term) < eps:
            return total, index + 1
        term *= (2 * index + 1) / ((2 * index + 3) * x * x)

    raise RuntimeError("The series did not reach the required precision in 500 iterations.")


def compute_math_value(x: float) -> float:
    return math.log((x + 1) / (x - 1))


@task_screen("Task 1. Power Series")
def run_task() -> None:
    print("Function: ln((x + 1) / (x - 1)) = 2 * sum(1 / ((2n + 1) * x^(2n + 1))), |x| > 1")
    x = read_float(
        "Enter x (|x| > 1): ",
        validator=lambda value: abs(value) > 1,
        error_message="The argument must satisfy |x| > 1.",
    )
    eps = read_float(
        "Enter eps (> 0): ",
        validator=lambda value: value > 0,
        error_message="The precision must be greater than zero.",
    )

    try:
        series_value, terms_count = compute_series_value(x, eps)
        math_value = compute_math_value(x)
    except (RuntimeError, ValueError, ZeroDivisionError) as error:
        print(f"Calculation error: {error}")
        return

    print(f"x = {x}")
    print(f"F(x) by series = {series_value:.12f}")
    print(f"n = {terms_count}")
    print(f"Math F(x) = {math_value:.12f}")
    print(f"Absolute error = {abs(math_value - series_value):.12e}")
