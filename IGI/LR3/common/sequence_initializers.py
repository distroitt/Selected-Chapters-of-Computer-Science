from __future__ import annotations

import random

from common.input_utils import read_float


def fill_by_user_input(target: list[float]) -> None:
    for index in range(len(target)):
        target[index] = read_float(f"Enter item #{index + 1}: ")


def random_value_generator(size: int, lower: float, upper: float):
    for _ in range(size):
        yield round(random.uniform(lower, upper), 3)


def fill_by_random_generator(target: list[float]) -> None:
    lower = read_float("Enter the lower bound for random values: ")
    upper = read_float(
        "Enter the upper bound for random values: ",
        validator=lambda value: value > lower,
        error_message="The upper bound must be greater than the lower bound.",
    )
    for index, value in enumerate(random_value_generator(len(target), lower, upper)):
        target[index] = value
