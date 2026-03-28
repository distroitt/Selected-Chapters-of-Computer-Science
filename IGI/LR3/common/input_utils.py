from __future__ import annotations

from typing import Callable, Optional


def read_int(
        prompt: str,
        validator: Optional[Callable[[int], bool]] = None,
        error_message: str = "Please enter a valid integer.",
) -> int:
    while True:
        try:
            value = int(input(prompt))
            if validator is not None and not validator(value):
                print(error_message)
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer value.")


def read_float(
        prompt: str,
        validator: Optional[Callable[[float], bool]] = None,
        error_message: str = "Please enter a valid real number.",
) -> float:
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
            if validator is not None and not validator(value):
                print(error_message)
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a real number.")


def read_text(prompt: str, allow_empty: bool = False) -> str:
    while True:
        value = input(prompt)
        if value or allow_empty:
            return value
        print("The text must not be empty.")


def read_menu_choice(prompt: str, valid_choices: set[str]) -> str:
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("Unknown menu item. Please choose one of the listed options.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"y", "yes", "д", "да"}:
            return True
        if answer in {"n", "no", "н", "нет"}:
            return False
        print("Please answer yes/y or no/n.")
