from __future__ import annotations

from common.decorators import task_screen
from common.input_utils import read_int


def sum_squares_until_zero() -> tuple[int, int]:
    total = 0
    count = 0

    while True:
        value = read_int("Enter an integer (0 to stop): ")
        if value == 0:
            return total, count
        total += value * value
        count += 1


@task_screen("Task 2. Sum Of Squares")
def run_task() -> None:
    total, count = sum_squares_until_zero()
    print(f"Numbers processed: {count}")
    print(f"Sum of squares: {total}")
