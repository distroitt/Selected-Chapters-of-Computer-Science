from __future__ import annotations

from common.input_utils import read_menu_choice
from tasks import task1_series, task2_sum_squares, task3_text_scan, task4_fixed_text, task5_list_processing


def print_menu() -> None:
    print("\nMain menu")
    print("1. Task 1 - power series")
    print("2. Task 2 - sum of squares")
    print("3. Task 3 - count uppercase English letters")
    print("4. Task 4 - fixed text analysis")
    print("5. Task 5 - list processing")
    print("0. Exit")


def main() -> None:
    actions = {
        "1": task1_series.run_task,
        "2": task2_sum_squares.run_task,
        "3": task3_text_scan.run_task,
        "4": task4_fixed_text.run_task,
        "5": task5_list_processing.run_task,
    }

    print("Laboratory work 3, variant 1")
    print("Choose a task to run.")

    while True:
        print_menu()
        choice = read_menu_choice("Select an option: ", {"0", "1", "2", "3", "4", "5"})
        if choice == "0":
            print("Program finished.")
            break

        actions[choice]()


if __name__ == "__main__":
    main()
