from __future__ import annotations

from common.decorators import task_screen
from common.input_utils import read_int, read_menu_choice
from common.sequence_initializers import fill_by_random_generator, fill_by_user_input


def format_list(numbers: list[float]) -> str:
    return "[" + ", ".join(f"{value:.3f}" for value in numbers) + "]"


def sum_negative_elements(numbers: list[float]) -> float:
    total = 0.0
    for value in numbers:
        if value < 0:
            total += value
    return total


def product_between_min_and_max(numbers: list[float]) -> tuple[float, list[float], int, int]:
    max_index = max(range(len(numbers)), key=lambda index: numbers[index])
    min_index = min(range(len(numbers)), key=lambda index: numbers[index])
    left, right = sorted((max_index, min_index))
    middle_part = numbers[left + 1: right]

    product = 1.0
    for value in middle_part:
        product *= value

    return product, middle_part, max_index, min_index


def create_list(size: int) -> list[float]:
    numbers = [0.0] * size
    print("Choose the initialization method:")
    print("1. Manual input")
    print("2. Random generator")
    choice = read_menu_choice("Your choice: ", {"1", "2"})

    if choice == "1":
        fill_by_user_input(numbers)
    else:
        fill_by_random_generator(numbers)

    return numbers


@task_screen("Task 5. List Processing")
def run_task() -> None:
    size = read_int(
        "Enter the list size (> 0): ",
        validator=lambda value: value > 0,
        error_message="The list size must be a positive integer.",
    )

    numbers = create_list(size)
    negative_sum = sum_negative_elements(numbers)
    product, middle_part, max_index, min_index = product_between_min_and_max(numbers)

    print(f"List: {format_list(numbers)}")
    print(f"Sum of negative elements: {negative_sum:.3f}")
    print(f"Maximum element index: {max_index}")
    print(f"Minimum element index: {min_index}")

    if middle_part:
        print(f"Elements between min and max: {format_list(middle_part)}")
        print(f"Product of elements between min and max: {product:.3f}")
    else:
        print("There are no elements between the minimum and maximum elements.")
        print("Product of elements between min and max: 1.000")
